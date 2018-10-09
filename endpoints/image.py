import uuid

import datetime
import boto3
import os
import json
import falcon
from sciencecache_model import *
from playhouse.shortcuts import dict_to_model, model_to_dict
from utilities import *



S3_ROOT_DIR = 'uploads/' + configuration['environment']
UUID_LENGTH = 36

AWS_ACCESS_KEY_ID = configuration['aws']['aws_access_key_id']
AWS_SECRET_ACCESS_KEY = configuration['aws']['aws_secret_access_key']
AWS_S3_BUCKET_NAME = configuration['aws']['aws_s3_bucket_name']

import re
S3_SAFE_REGEX= r"""[^0-9A-Za-z!-_.*'()]"""
S3_REPLACE_CHARACTER = '_'
S3_REGEX_FLAGS = re.IGNORECASE




class image_end_point():

    def sanitize_key_for_s3(self, key):
        try:
            key = re.sub(
                pattern=S3_SAFE_REGEX,
                repl=S3_REPLACE_CHARACTER,
                string=key,
                flags=S3_REGEX_FLAGS,
            )
        except re.error as e:
            print(e)
            raise falcon.HTTPBadRequest(description='Invalid FileName. Error parsing pattern.')
        except SyntaxError as e:
            print(e)
            raise falcon.HTTPBadRequest(description='Invalid FileName. Your Filename may contain non-ascii characters')
        except Exception as e:
            print(e)
            raise falcon.HTTPBadRequest(description='An unknown error occured. Try a different file name')
        return key

    def on_get(self, request, response, object_id=None):

        s3_client = boto3.client(
            's3',
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            use_ssl=True
        )


        if(not request.get_param('type')):
            raise falcon.HTTPMissingParam(param_name='type')

        if(not request.get_param('id')):
            raise falcon.HTTPMissingParam(param_name='id')


        obj_type = request.get_param('type')
        obj_id = request.get_param('id')
        results = []
        #object_key =""
        try:
            images = []

            if(obj_type == 'route'):
                for image in Images.select().join(RouteImages).where(RouteImages.route == obj_id, Images.id ==  RouteImages.image):
                    images.append(image)

            elif(obj_type == 'observation-point' ):
                for image in Images.select().join(ObspntImages).where(ObspntImages.observation_point == obj_id, Images.id ==  ObspntImages.image):
                    images.append(image)

            else:
                raise falcon.HTTPBadRequest(description='type does not exist, avaiable types:  route, observation-point')


            for image in images:
                s3_presigned_url = s3_client.generate_presigned_url(
                ClientMethod='get_object',
                Params={
                    'Bucket': AWS_S3_BUCKET_NAME,
                    'Key': image.image
                })
                image_dict = model_to_dict(image,recurse=False)
                image_dict['image'] = s3_presigned_url

                results.append(image_dict)



        except Images.DoesNotExist:
            raise falcon.HTTPNotFound(
                description='image not found'
            )

        except RouteImages.DoesNotExist:
            raise falcon.HTTPNotFound(
                description='Route with object_id not found'
            )
        except ObspntImages.DoesNotExist:
            raise falcon.HTTPNotFound(
                description='Observation Point with object_id not found'
            )

       

        response.body = json.dumps(results)
    


    @falcon.before(check_logged_in)
    def on_post(self, request, response, object_id=None):

        s3_client = boto3.client(
            's3',
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            use_ssl=True
        )

        if(object_id is None):
            raise falcon.HTTPMissingParam(param_name='object_id')
        
        if(not request.get_param('filename')):
            raise falcon.HTTPMissingParam(param_name='filename')

        if(not request.get_param('filetype')):
            raise falcon.HTTPMissingParam(param_name='filetype')

       
        if(not request.get_param('type')):
            raise falcon.HTTPMissingParam(param_name='type')


        obj_type = request.get_param('type')
        imaage_id =""

        try:

            # load the request body
            new_image_dict = json.loads(request.stream.read() or 0)
            new_image = dict_to_model(Images, new_image_dict, ignore_unknown=True)
            new_image.save()
            image_id = new_image.id

        except Exception as e:
            raise falcon.HTTPBadRequest(description='Could not create image')

        # Example: 's3://nabat-s3/uploads/project-uuid/uuid_filename.ext'
        filename = self.sanitize_key_for_s3(request.get_param('filename'))
        unique_file_string = str(datetime.datetime.utcnow().strftime("%Y_%m_%d_%H_%M_%S")+"Z")

        s3_directory = S3_ROOT_DIR + '/' + str(image_id)
        object_key = self.sanitize_key_for_s3(s3_directory + '/' + unique_file_string + '/' + filename)

        s3_presigned_url = s3_client.generate_presigned_post(
            Bucket=AWS_S3_BUCKET_NAME,
            Key=object_key,
 
        )
        try:
            image = Images.get_by_id(image_id)
            image.image = str(s3_presigned_url['fields']['key'])
            image.save()

            if(obj_type == 'route'):
                new_route_image_dict = {'route': object_id, "image": image_id}
                new_route_image = dict_to_model(RouteImages, new_route_image_dict, ignore_unknown=True)
                new_route_image.save()

            elif(obj_type == 'observation-point' ):
                new_obs_image_dict = {'observation_point': object_id, "image": image_id}
                new_obs_image = dict_to_model(ObspntImages, new_obs_image_dict, ignore_unknown=True)
                new_obs_image.save()
            
            else:
                raise falcon.HTTPBadRequest(description='type does not exist, avaiable types:  route, observation-point')

        except Images.DoesNotExist:
            raise falcon.HTTPNotFound(
                description='image not found'
            )

        except RouteImages.DoesNotExist:
            raise falcon.HTTPNotFound(
                description='Route with object_id not found'
            )
        except ObspntImages.DoesNotExist:
            raise falcon.HTTPNotFound(
                description='Observation Point with object_id not found'
            )

        response.body = json.dumps(s3_presigned_url)


    @falcon.before(check_logged_in)
    def on_delete(self, request, response, object_id=None):

        if(object_id is None):
            raise falcon.HTTPMissingParam(param_name='object_id')

        try:

            image = Images.get_by_id(object_id)

            s3_client = boto3.client(
                's3',
                aws_access_key_id=AWS_ACCESS_KEY_ID,
                aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                use_ssl=True
            )
            s3_client.delete_object(Bucket=AWS_S3_BUCKET_NAME,Key=image.image)
            image.delete_instance()
            
        except Images.DoesNotExist as e:
            raise falcon.HTTPNotFound(
                description='Image with id: ' + str(object_id)  + ' not found'
            )
            
        except Exception as e:
            print (e)
            raise falcon.HTTPInternalServerError(description=str(e))
        
        response.status = falcon.HTTP_NO_CONTENT




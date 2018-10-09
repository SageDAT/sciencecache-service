import json
import uuid
import boto3
import os

import falcon
from sciencecache_model import *
from playhouse.shortcuts import dict_to_model, model_to_dict
from utilities import *
import datetime



class route_end_point():




    S3_ROOT_DIR = 'uploads/' + configuration['environment']
    UUID_LENGTH = 36

    AWS_ACCESS_KEY_ID = configuration['aws']['aws_access_key_id']
    AWS_SECRET_ACCESS_KEY = configuration['aws']['aws_secret_access_key']
    AWS_S3_BUCKET_NAME = configuration['aws']['aws_s3_bucket_name']

    s3_client = boto3.client(
        's3',
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        use_ssl=True
    )

    

    def edit_premissions(self,user_id,route_id):
        user = get_user(user_id)
        if(user):
            if(user.is_admin):
                return True
            else:
                try:
                    UserRoleRoute.select().where(UserRoleRoute.user == user_id,
                        (UserRoleRoute.role == Role.select().where(Role.description =='Owner').get()) | (UserRoleRoute.role == Role.select().where(Role.description =='Edit').get()),
                        UserRoleRoute.route == route_id).get()
                    return True

                except UserRoleRoute.DoesNotExist as e:
                    return False

        return False

    def get_signed_url(self,route_id):

        with sciencecache_database.transaction():  

            try:
                image = Images.select().join(RouteImages).where(RouteImages.route == route_id, Images.id ==  RouteImages.image).get()
                s3_presigned_url = self.s3_client.generate_presigned_url(
                    ClientMethod='get_object',
                    Params={
                        'Bucket': self.AWS_S3_BUCKET_NAME,
                        'Key': image.image
                    }
                )
                return s3_presigned_url
            except Exception as e:
                pass
        return None
      


    def get_public_routes(self,route_id):

        try:
            if(route_id is None):
                results = []
                for r in  Routes.select().where(Routes.published == True, Routes.private == False):
                    route_dict = model_to_dict(r, recurse=False)
                    route_dict['image'] = self.get_signed_url(route_dict['route'])
                    results.append(route_dict)
                return results


                
            else:
                route = Routes.get_by_id(route_id)
                if(route.published and not route.private):
                    return model_to_dict(route,recurse=False)
                else:
                    raise falcon.HTTPUnauthorized(description='This route is not public')
            
        except Routes.DoesNotExist as e:
            raise falcon.HTTPNotFound(description='Route with route_id: ' + str(route_id)  + ' not found')

        # except Exception as e:
        #     raise falcon.HTTPBadRequest(description=str(e))


    def get_private_routes(self,route_id,user_id):

        user = None
        try:
            if user_id or user_id is not "":
                user = User.get_by_id(int(user_id))
            else:
                raise falcon.HTTPBadRequest("user-ID header is none")

        except User.DoesNotExist as e:
            raise falcon.HTTPNotFound(description='User with id: ' + str(user_id)  + ' not found')

        except Exception as e:
            raise falcon.HTTPBadRequest(description=str(e))

        try:
             # user is an admin
            if(user.is_admin):
                
                # getting all the routes
                results = []
                if (route_id is None):
                    for r in  Routes.select():
                        route_dict = model_to_dict(r, recurse=False)
                        route_dict['image'] = self.get_signed_url(route_dict['route'])
                        results.append(route_dict)
                    return results
                
                # getting just 1 route with route id
                else:
                    route = Routes.get_by_id(route_id)
                    return model_to_dict(route,recurse=False)
                

            # user is not admin
            else:
                    # getting all the routes
                results=[]
                if (route_id is None):
                    for r in Routes.select().join(UserRoleRoute).where(UserRoleRoute.user == user.id).order_by(Routes.last_updated.desc()):
                        route_dict = model_to_dict(r, recurse=False)
                        route_dict['image'] = self.get_signed_url(route_dict['route'])
                        results.append(route_dict)
                    return results
                
                # getting just 1 route with route id
                else:
                    route = Routes.get_by_id(route_id)
                    if(route.published and not route.private):
                        return model_to_dict(route,recurse=False)
                    else:
                        route = Routes.select().join(UserRoleRoute).where(UserRoleRoute.user == user.id, UserRoleRoute.route == Routes.route, Routes.route == route_id).get()
                        return model_to_dict(route,recurse=False)
                    
            
        except Routes.DoesNotExist as e:
            raise falcon.HTTPNotFound(description='Route with route_id: ' + str(route_id)  + ' not found')

        except Exception as e:
            raise falcon.HTTPBadRequest(description=str(e))





    def on_get(self, request, response, route_id = None):

        results = []
        user_ID = request.get_header('user-ID')

        if(user_ID is None or user_ID is ""):
            results = self.get_public_routes(route_id)

        else:
            results = self.get_private_routes(route_id,user_ID)

        response.body = json.dumps(results, default=json_serial)

        

    @falcon.before(check_logged_in)    
    def on_post(self, request, response, route_id = None):
        
        # Do not allow POST (create) when route_id is given
        if route_id is not None:
            raise falcon.falcon.HTTPMethodNotAllowed(
                allowed_methods=['GET', 'POST', 'PUT','OPTIONS'],
                description='New routes must be created without an route_id'
            )

        try:
            

            # load the request body
            route_dict = json.loads(request.stream.read() or 0)

            #sanitize input
            bad_keys = ['route','access_key','last_updated']
            for key in bad_keys:
                if(key in route_dict):
                    del route_dict[key]

           
            #create new route
            new_route = None
            route_dict['access_key'] = str(uuid.uuid4())
            route_dict['last_updated'] = str(datetime.datetime.now())

    
       
            new_route = dict_to_model(Routes, route_dict, ignore_unknown=True)
            new_route.save()

        
        except Exception as e:
                raise falcon.HTTPBadRequest(description=str(e))

        response.status = falcon.HTTP_CREATED
        response.body = json.dumps(model_to_dict(new_route),default=json_serial)

        
    @falcon.before(check_logged_in)
    def on_put(self, request, response, route_id=None):

        
           # Do not allow POST (create) when route_id is given
        if route_id is None:
            raise falcon.HTTPBadRequest(description="route_id can not be empty: routes/123")
            
        user_ID = request.get_header('user-ID')
        if(not self.edit_premissions(user_ID,route_id)):
            raise falcon.HTTPUnauthorized(
                description='You do not have premission to edit this route'
                )
        try:

            # load the request body
            changes = json.loads(request.stream.read() or 0)

            #sanitize input
            bad_keys = ['route','access_key','last_updated']
            for key in bad_keys:
                if(key in changes):
                    del changes[key]

           
            changes['last_updated'] = str(datetime.datetime.now())

            #find route
            route = Routes.get_by_id(route_id)
            route_dict = model_to_dict(route, recurse=False)
             

            
            # apply the changes
            for field in changes:
                route_dict[field] = changes[field]

            # save changes
            updated_route = dict_to_model(Routes, route_dict, ignore_unknown=True)
            updated_route.save()

           
        except Routes.DoesNotExist as e:
            raise falcon.HTTPNotFound(
                description='Route with route_id: ' + str(route_id)  + ' not found'
            )

        except Exception as e:
            raise falcon.HTTPInternalServerError(description=str(e))


        response.body = json.dumps(model_to_dict(updated_route),default=json_serial)

        

    @falcon.before(check_logged_in)
    def on_delete(self, request, response, route_id=None):
        
        if route_id is None:
            raise falcon.HTTPBadRequest(description="route_id can not be empty: routes/123")

        user_ID = request.get_header('user-ID')
        if(not self.edit_premissions(user_ID,route_id)):
            raise falcon.HTTPUnauthorized(
                description='You do not have premission to delete this route'
                )

        try:
            #find route
            route = Routes.get_by_id(route_id)
            route.delete_instance()
            
        except Routes.DoesNotExist as e:
            raise falcon.HTTPNotFound(
                description='Route with route_id: ' + str(route_id)  + ' not found'
            )
            
        except Exception as e:
            print (e)
            raise falcon.HTTPInternalServerError(description=str(e))
        
        response.status = falcon.HTTP_NO_CONTENT
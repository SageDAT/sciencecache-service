import json
import uuid
import falcon
from sciencecache_model import *
from playhouse.shortcuts import dict_to_model, model_to_dict
from utilities import *

class obs_form_data_request_end_point():



    def on_get(self, request, response, obs_form_data_request_id = None):


        results =[]
        try:
            with sciencecache_database.transaction():  
                
                if (obs_form_data_request_id is not None):
                    obs_form_data_request = ObspointFormDatarequests.get_by_id(obs_form_data_request_id)
                    results = model_to_dict(obs_form_data_request,recurse=True)

                  
                elif(request.get_param('form')):
                    form_id = request.get_param('form')
                    for r in  ObspointFormDatarequests.select().where(ObspointFormDatarequests.obs_point_form == form_id):
                        results.append(model_to_dict(r, recurse=True))


                else:
                    for r in ObspointFormDatarequests.select():
                        results.append(model_to_dict(r, recurse=False))
            

        except ObspointFormDatarequests.DoesNotExist as e:
            raise falcon.HTTPNotFound(
                description='Observation point form data requests with obs_form_data_request_id: ' + str(obs_form_data_request_id)  + ' not found'
            )
        except Exception as e:
            print(e)
            raise falcon.HTTPBadRequest(description="Failed to get Observation point form data request")

        response.body = json.dumps(results, default=json_serial)


    @falcon.before(check_logged_in)    
    def on_post(self, request, response, obs_form_data_request_id = None):
        
        
        # Do not allow POST (create) when obs_form_data_request_id is given
        if obs_form_data_request_id is not None:
            raise falcon.falcon.HTTPMethodNotAllowed(
                allowed_methods=['GET', 'POST', 'PUT','OPTIONS'],
                description='New Observation point form data requests must be created without an obs_form_data_request_id'
            )

        try:
            

            # load the request body
            obs_form_data_request_dict = json.loads(request.stream.read() or 0)

            #sanitize input
            bad_keys = ['id']
            for key in bad_keys:
                if(key in obs_form_data_request_dict):
                    del obs_form_data_request_dict[key]


            #create new  Observation point form data request
            new_obs_form_data_request = None
    

            new_obs_form_data_request = dict_to_model(ObspointFormDatarequests, obs_form_data_request_dict, ignore_unknown=True)
            new_obs_form_data_request.save()


        except Exception as e:
                raise falcon.HTTPBadRequest(description=str(e))

        response.status = falcon.HTTP_CREATED
        response.body = json.dumps(model_to_dict(new_obs_form_data_request),default=json_serial)

        
    @falcon.before(check_logged_in)
    def on_put(self, request, response, obs_form_data_request_id=None):
           # Do not allow POST (create) when obs_form_data_request_id is given
        if obs_form_data_request_id is None:
            raise falcon.HTTPBadRequest(description="obs_form_data_request_id can not be empty: obs-from-data-request/123")

        try:

            # load the request body
            changes = json.loads(request.stream.read() or 0)

            #sanitize input
            bad_keys = ['id']
            for key in bad_keys:
                if(key in changes):
                    del changes[key]

           
            #find Observation point form Observation point form data request
            obs_form_data_request = ObspointFormDatarequests.get_by_id(obs_form_data_request_id)
            obs_form_data_request_dict = model_to_dict(obs_form_data_request, recurse=False)
            
            # apply the changes
            for field in changes:
                obs_form_data_request_dict[field] = changes[field]

            # save changes
            updated_obs_form_data_request = dict_to_model(ObspointFormDatarequests, obs_form_data_request_dict, ignore_unknown=True)
            updated_obs_form_data_request.save()

        except ObspointFormDatarequests.DoesNotExist as e:
            raise falcon.HTTPNotFound(
                description='Observation point form data request with obs_form_data_requests_id: ' + str(obs_form_data_request_id)   + ' not found'
            )

        except Exception as e:
            raise falcon.HTTPInternalServerError(description=str(e))


        response.body = json.dumps(model_to_dict(updated_obs_form_data_request),default=json_serial)

        

    @falcon.before(check_logged_in)
    def on_delete(self, request, response, obs_form_data_request_id=None):
        
        if obs_form_data_request_id is None:
            raise falcon.HTTPBadRequest(description="obs_form_data_request_id can not be empty: obs-from-data-request/123")
        

        try:

            #find Observation point form data request 
            obs_form_data_request = ObspointFormDatarequests.get_by_id(obs_form_data_request_id)
            obs_form_data_request.delete_instance()
            
        except ObspointFormDatarequests.DoesNotExist as e:
            raise falcon.HTTPNotFound(
                description=' Observation point form data request with obs_form_data_request_id: ' + str(obs_form_data_request_id)  + ' not found'
            )
            
        except Exception as e:
            print (e)
            raise falcon.HTTPInternalServerError(description=str(e))
        
        response.status = falcon.HTTP_NO_CONTENT
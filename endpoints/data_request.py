import json
import uuid
import falcon
from sciencecache_model import *
from playhouse.shortcuts import dict_to_model, model_to_dict
from utilities import *

class data_request_end_point():



    def on_get(self, request, response, data_request_id = None):


        results =[]
        try:
            with sciencecache_database.transaction():  
                
                if (data_request_id is not None):
                    data_request = Datarequests.get_by_id(data_request_id)
                    results = model_to_dict(data_request,recurse=False)

                else:
                    for r in Datarequests.select():
                        results.append(model_to_dict(r, recurse=False))
            

        except Datarequests.DoesNotExist as e:
            raise falcon.HTTPNotFound(
                description='Data requests with data_request_id: ' + str(data_request_id)  + ' not found'
            )
        except Exception as e:
            print(e)
            raise falcon.HTTPBadRequest(description="Failed to get data request point")

        response.body = json.dumps(results, default=json_serial)


    @falcon.before(check_logged_in)    
    def on_post(self, request, response, data_request_id = None):
        
        
        # Do not allow POST (create) when data_request_id is given
        if data_request_id is not None:
            raise falcon.falcon.HTTPMethodNotAllowed(
                allowed_methods=['GET', 'POST', 'PUT','OPTIONS'],
                description='New data request must be created without an data_request_id'
            )

        try:
            

            # load the request body
            data_request_dict = json.loads(request.stream.read() or 0)

            #sanitize input
            bad_keys = ['id']
            for key in bad_keys:
                if(key in data_request_dict):
                    del data_request_dict[key]


            #create new data request
            new_data_request = None
    

            new_data_request = dict_to_model(Datarequests, data_request_dict, ignore_unknown=True)
            new_data_request.save()


        except Exception as e:
                raise falcon.HTTPBadRequest(description=str(e))

        response.status = falcon.HTTP_CREATED
        response.body = json.dumps(model_to_dict(new_data_request),default=json_serial)

        
    @falcon.before(check_logged_in)
    def on_put(self, request, response, data_request_id=None):
           # Do not allow POST (create) when data_request_id is given
        if data_request_id is None:
            raise falcon.HTTPBadRequest(description="data_request_id can not be empty: data-request/123")

        try:

            # load the request body
            changes = json.loads(request.stream.read() or 0)

            #sanitize input
            bad_keys = ['id']
            for key in bad_keys:
                if(key in changes):
                    del changes[key]

           
            #find data request
            data_request = Datarequests.get_by_id(data_request_id)
            data_request_dict = model_to_dict(data_request, recurse=False)
            
            # apply the changes
            for field in changes:
                data_request_dict[field] = changes[field]

            # save changes
            updated_data_request = dict_to_model(Datarequests, data_request_dict, ignore_unknown=True)
            updated_data_request.save()

        except Datarequests.DoesNotExist as e:
            raise falcon.HTTPNotFound(
                description='Data request with data_requests_id: ' + str(data_request_id)   + ' not found'
            )

        except Exception as e:
            raise falcon.HTTPInternalServerError(description=str(e))


        response.body = json.dumps(model_to_dict(updated_data_request),default=json_serial)

        

    @falcon.before(check_logged_in)
    def on_delete(self, request, response, data_request_id=None):
        
        if data_request_id is None:
            raise falcon.HTTPBadRequest(description="data_request_id can not be empty: data-request/123")
        

        try:

            #find data request 
            data_request = Datarequests.get_by_id(data_request_id)
            data_request.delete_instance()
            
        except Datarequests.DoesNotExist as e:
            raise falcon.HTTPNotFound(
                description='Data request with data_request_id: ' + str(data_request_id)  + ' not found'
            )
            
        except Exception as e:
            print (e)
            raise falcon.HTTPInternalServerError(description=str(e))
        
        response.status = falcon.HTTP_NO_CONTENT
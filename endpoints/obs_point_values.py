import json
import uuid
import falcon
from sciencecache_model import *
from playhouse.shortcuts import dict_to_model, model_to_dict
from utilities import *
import datetime


class obs_point_values_end_point():



    def on_get(self, request, response, obs_point_values_id = None):


        results =[]
        try:
            with sciencecache_database.transaction():  
                
                if (obs_point_values_id is not None):
                    obs_point_values = ObsPntValues.get_by_id(obs_point_values_id)
                    results = model_to_dict(obs_point_values,recurse=False)
          
                elif(request.get_param('observation-point')):
                    observation_point_id = request.get_param('observation-point')
                    for r in  ObsPntValues.select().where(ObsPntValues.observation_point == observation_point_id):
                        results.append(model_to_dict(r, recurse=False))

                else:
                    for r in ObsPntValues.select():
                        results.append(model_to_dict(r, recurse=False))
            

        except ObsPntValues.DoesNotExist as e:
            raise falcon.HTTPNotFound(
                description='obs_point_values with obs_point_values_id: ' + str(obs_point_values_id)  + ' not found'
            )
        except Exception as e:
            print(e)
            raise falcon.HTTPBadRequest(description="Failed to get obs_point_values ")

        response.body = json.dumps(results, default=json_serial)


    @falcon.before(check_logged_in)    
    def on_post(self, request, response, obs_point_values_id = None):
        
        
        # Do not allow POST (create) when obs_point_values_id is given
        if obs_point_values_id is not None:
            raise falcon.falcon.HTTPMethodNotAllowed(
                allowed_methods=['GET', 'POST', 'PUT','OPTIONS'],
                description='New obs_point_values must be created without an obs_point_values_id'
            )

        try:
            
            # load the request body
            obs_point_values_dict = json.loads(request.stream.read() or 0)

            #sanitize input
            bad_keys = ['id','date_captured']
            for key in bad_keys:
                if(key in obs_point_values_dict):
                    del obs_point_values_dict[key]

            obs_point_values_dict['date_captured'] = str(datetime.datetime.now())

            #create new obs_point_values
            new_obs_point_values = None
    

            new_obs_point_values = dict_to_model(ObsPntValues, obs_point_values_dict, ignore_unknown=True)
            new_obs_point_values.save()


        except Exception as e:
                raise falcon.HTTPBadRequest(description=str(e))

        response.status = falcon.HTTP_CREATED
        response.body = json.dumps(model_to_dict(new_obs_point_values,recurse=False),default=json_serial)

        
    @falcon.before(check_logged_in)
    def on_put(self, request, response, obs_point_values_id=None):
           # Do not allow POST (create) when obs_point_values_id is given
        if obs_point_values_id is None:
            raise falcon.HTTPBadRequest(description="obs_point_values_id can not be empty: obs-point-values/123")

        try:

            # load the request body
            changes = json.loads(request.stream.read() or 0)

            #sanitize input
            bad_keys = ['id']
            for key in bad_keys:
                if(key in changes):
                    del changes[key]

           
            #find obs_point_values 
            obs_point_values = ObsPntValues.get_by_id(obs_point_values_id)
            obs_point_values_dict = model_to_dict(obs_point_values, recurse=False)
            
            # apply the changes
            for field in changes:
                obs_point_values_dict[field] = changes[field]

            # save changes
            updated_obs_point_values = dict_to_model(ObsPntValues, obs_point_values_dict, ignore_unknown=True)
            updated_obs_point_values.save()

        except ObsPntValues.DoesNotExist as e:
            raise falcon.HTTPNotFound(
                description='obs_point_values with obs_point_valuess_id: ' + str(obs_point_values_id)   + ' not found'
            )

        except Exception as e:
            raise falcon.HTTPInternalServerError(description=str(e))


        response.body = json.dumps(model_to_dict(updated_obs_point_values),default=json_serial)

        

    @falcon.before(check_logged_in)
    def on_delete(self, request, response, obs_point_values_id=None):
        
        if obs_point_values_id is None:
            raise falcon.HTTPBadRequest(description="obs_point_values_id can not be empty: obs-point-values/123")
        

        try:

            #find obs_point_values  
            obs_point_values = ObsPntValues.get_by_id(obs_point_values_id)
            obs_point_values.delete_instance()
            
        except ObsPntValues.DoesNotExist as e:
            raise falcon.HTTPNotFound(
                description='obs_point_values with obs_point_values_id: ' + str(obs_point_values_id)  + ' not found'
            )
            
        except Exception as e:
            print (e)
            raise falcon.HTTPInternalServerError(description=str(e))
        
        response.status = falcon.HTTP_NO_CONTENT
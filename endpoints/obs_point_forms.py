import json
import uuid
import falcon
from sciencecache_model import *
from playhouse.shortcuts import dict_to_model, model_to_dict
from utilities import *
import datetime


class obs_point_forms_end_point():



    def on_get(self, request, response, obs_point_id = None):


        results =[]
        try:
            with sciencecache_database.transaction():  
                
                form = []
                if (obs_point_id is not None):
                    for obs_pnt_values in  ObsPntValues.select().where(ObsPntValues.observation_point == obs_point_id):

                     Routes.select().join(UserRoleRoute).where(UserRoleRoute.user == user.id).order_by(Routes.last_updated.desc()):

            

        except ObsPntValues.DoesNotExist as e:
            raise falcon.HTTPNotFound(
                description='obs_point_id: ' + str(obs_point_id)  + ' not found'
            )
        except Exception as e:
            print(e)
            raise falcon.HTTPBadRequest(description="Failed to get obs point forms ")

        response.body = json.dumps(results, default=json_serial)
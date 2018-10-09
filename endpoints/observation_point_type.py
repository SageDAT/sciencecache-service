import json
import falcon
from sciencecache_model import *
from playhouse.shortcuts import dict_to_model, model_to_dict
from utilities import *

class observation_point_type_end_point:



   def on_get(self, request, response, observation_point_type_id = None):

    results =[]
    try:
        if (observation_point_type_id == None):
            for r in  ObservationpointType.select():
                results.append(model_to_dict(r, recurse=False))
        else:
            observation_point_type = ObservationpointType.select().where(ObservationpointType.id == observation_point_type_id).get()
            results = model_to_dict(observation_point_type)
        

    except ObservationpointType.DoesNotExist:
      raise falcon.HTTPNotFound(
        description='ObservationpointType with id: ' + str(observation_point_type_id)  + ' not found'
      )
    except Exception as e:
        print(e)
        raise falcon.HTTPBadRequest(description="Failed to get ObservationpointType")

    response.body = json.dumps(results)


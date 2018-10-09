import json
import falcon
from sciencecache_model import *
from playhouse.shortcuts import dict_to_model, model_to_dict
from utilities import *

class route_difficulty_end_point:



   def on_get(self, request, response, route_difficulty_id = None):

    results =[]
    try:
        if (route_difficulty_id == None):
            for r in  Routedifficulty.select():
                results.append(model_to_dict(r, recurse=False))
        else:
            route_difficulty = Routedifficulty.select().where(Routedifficulty.id == route_difficulty_id).get()
            results = model_to_dict(route_difficulty)
        

    except Routes.DoesNotExist:
      raise falcon.HTTPNotFound(
        description='Routedifficulty with id: ' + str(route_difficulty_id)  + ' not found'
      )
    except Exception as e:
        print(e)
        raise falcon.HTTPBadRequest(description="Failed to get Routedifficulty")

    response.body = json.dumps(results)


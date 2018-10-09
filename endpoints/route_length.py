import json
import falcon
from sciencecache_model import *
from playhouse.shortcuts import dict_to_model, model_to_dict
from utilities import *

class route_length_end_point:



   def on_get(self, request, response, route_length_id = None):

    results =[]
    try:
        if (route_length_id == None):
            for r in  Routelength.select():
                results.append(model_to_dict(r, recurse=False))
        else:
            route_length = Routelength.select().where(Routelength.id == route_length_id).get()
            results = model_to_dict(route_length, recurse=False)
        

    except Routes.DoesNotExist:
      raise falcon.HTTPNotFound(
        description='Routelength with id: ' + str(route_length_id)  + ' not found'
      )
    except Exception as e:
        print(e)
        raise falcon.HTTPBadRequest(description="Failed to get Routelength")

    response.body = json.dumps(results)


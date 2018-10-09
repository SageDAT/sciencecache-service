import json
import falcon
from sciencecache_model import *
from playhouse.shortcuts import dict_to_model, model_to_dict
from utilities import *

class roles_end_point:


    #@falcon.before(check_logged_in)
    def on_get(self, request, response):

        results =[]
        try:
        
            for role in  Role.select():
                results.append(model_to_dict(role, recurse=False))
            
        except Exception as e:
            print(e)
            raise falcon.HTTPBadRequest(description="Failed to get roles")

        response.body = json.dumps(results)


import json
import falcon
from sciencecache_model import *
from playhouse.shortcuts import dict_to_model, model_to_dict
from utilities import *

class user_end_point:


    @falcon.before(check_logged_in)
    def on_get(self, request, response):

        email = request.get_header('email-address')

        user = {}
        try:
            if (email == None):
                raise falcon.HTTPMissingHeader(header_name='email-address')
            
            else:
                user = User.select().where(User.user_email == email).get()
                user = model_to_dict(user,recurse=True)

        except User.DoesNotExist:
            raise falcon.HTTPNotFound(
                description='User with email: ' + str(email)  + ' not found'
            )
            
        except Exception as e:
            print(e)
            raise falcon.HTTPBadRequest(description="Failed to get user")

        response.body = json.dumps(user)


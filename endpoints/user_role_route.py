import json
import falcon
from sciencecache_model import *
from playhouse.shortcuts import dict_to_model, model_to_dict
from utilities import *

class user_role_route_end_point:

    @falcon.before(check_logged_in)
    def on_get(self, request, response, user_role_route_id=None):

        results =[]
        try:
            # get a role by ID
            if user_role_route_id is not None:
                role = UserRoleRoute.get_by_id(user_role_route_id)
                results.append(model_to_dict(role, recurse=False))

            # no role ID provided
            else:

                # Get user-role-routes with route id 
                if(request.get_param('route')):
                    route_id = request.get_param('route')
                    for r in  UserRoleRoute.select().where(UserRoleRoute.route == route_id):
                        results.append(model_to_dict(r, recurse=False))

                # get user-role-routes with user id
                elif(request.get_param('user')):
                    user_id = request.get_param('user')
                    for r in  UserRoleRoute.select().where(UserRoleRoute.user == user_id):
                        results.append(model_to_dict(r, recurse=False))

                else:
                    raise falcon.HTTPBadRequest(description="No route or user parameter was specified. Ex) user-role-route?route=321 user-role-route?user=123")

        except UserRoleRoute.DoesNotExist as e:
            raise falcon.HTTPNotFound(
                description='UserRoleRoute not found'
            )
        except Exception as e:
            print(e)
            raise falcon.HTTPBadRequest(description="Failed to get UserRoleRoute")

        response.body = json.dumps(results, default=json_serial)


    @falcon.before(check_logged_in)
    def on_post(self, request, response, user_role_route_id=None):

        if user_role_route_id is not None:
            raise falcon.HTTPBadRequest(description="do not provide role ID on post")

        try:
            # load the request body
            new_user_role_route_dict = json.loads(request.stream.read() or 0)
            #sanitize input
            bad_keys = ['id']
            for key in bad_keys:
                if(key in new_user_role_route_dict):
                    del new_user_role_route_dict[key]

            #create new route
            new_user_role_route = None

            new_user_role_route = dict_to_model(UserRoleRoute, new_user_role_route_dict, ignore_unknown=True)
            new_user_role_route.save()

        
        except Exception as e:
            raise falcon.HTTPBadRequest(description=str(e))

        response.status = falcon.HTTP_CREATED
        response.body = json.dumps(model_to_dict(new_user_role_route),default=json_serial)




    @falcon.before(check_logged_in)
    def on_put(self, request, response, user_role_route_id=None):

        if user_role_route_id is None:
            raise falcon.HTTPBadRequest(description="user_role_route_id can not be empty: user-role-route/123")

        try:

            # load the request body
            changes = json.loads(request.stream.read() or 0)

            # nothing to sanitize
           
            #find role
            role = UserRoleRoute.get_by_id(user_role_route_id)
            role_dict = model_to_dict(role, recurse=False)
             

            
            # apply the changes
            for field in changes:
                role_dict[field] = changes[field]

            # save changes
            updated_role = dict_to_model(UserRoleRoute, role_dict, ignore_unknown=True)
            updated_role.save()

           
        except UserRoleRoute.DoesNotExist as e:
            raise falcon.HTTPNotFound(
                description='UserRoleRoute with user_role_route_id: ' + str(user_role_route_id)  + ' not found'
            )

        except Exception as e:
            raise falcon.HTTPInternalServerError(description=str(e))


        response.body = json.dumps(model_to_dict(updated_role),default=json_serial)

    
    @falcon.before(check_logged_in)
    def on_delete(self, request, response, user_role_route_id=None):
        
        if user_role_route_id is None:
            raise falcon.HTTPBadRequest(description="user_role_route_id can not be empty: routes/123")
        

        try:
            #find role
            role = UserRoleRoute.get_by_id(user_role_route_id)
            role.delete_instance()
            
        except UserRoleRoute.DoesNotExist as e:
            raise falcon.HTTPNotFound(
                description='UserRoleRoute with user_role_route_id: ' + str(user_role_route_id)  + ' not found'
            )
            
        except Exception as e:
            print (e)
            raise falcon.HTTPInternalServerError(description=str(e))
        
        response.status = falcon.HTTP_NO_CONTENT




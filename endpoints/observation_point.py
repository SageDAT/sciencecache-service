import json
import uuid
import falcon
from sciencecache_model import *
from playhouse.shortcuts import dict_to_model, model_to_dict
from utilities import *

class observation_point_end_point():



    def edit_premissions(self,user_id,observation_point_id):
        user = get_user(user_id)
        if(user):
            if(user.is_admin):
                return True
            else:
                try:
                    UserRoleRoute.select().where(UserRoleRoute.user == user_id,
                        (UserRoleRoute.role == Role.select().where(Role.description =='Owner').get()) | (UserRoleRoute.role == Role.select().where(Role.description =='Edit').get()),
                        UserRoleRoute.route == ObservationPoints.get_by_id(observation_point_id).route).get()
                    return True

                except UserRoleRoute.DoesNotExist as e:
                    return False
                except ObservationPoints.DoesNotExist as e:
                    return False

        return False



    def on_get(self, request, response, observation_point_id = None):


        results =[]
        try:
            with sciencecache_database.transaction():
               
                # Get user-role-routes with route id 
                if(request.get_param('route')):
                    route_id = request.get_param('route')
                    for r in  ObservationPoints.select().where(ObservationPoints.route == route_id):
                        results.append(model_to_dict(r, recurse=False))

                
                elif (observation_point_id is not None):
                    observation_point = ObservationPoints.get_by_id(observation_point_id)
                    results = model_to_dict(observation_point,recurse=False)

                else:
                    for r in ObservationPoints.select():
                        results.append(model_to_dict(r, recurse=False))
            

        except ObservationPoints.DoesNotExist as e:
            raise falcon.HTTPNotFound(
                description='Observation point with observation_point_id: ' + str(observation_point_id)  + ' not found'
            )
        except Exception as e:
            print(e)
            raise falcon.HTTPBadRequest(description="Failed to get observation point")

        response.body = json.dumps(results, default=json_serial)


    @falcon.before(check_logged_in)    
    def on_post(self, request, response, observation_point_id = None):
        
        
        # Do not allow POST (create) when route_id is given
        if observation_point_id is not None:
            raise falcon.falcon.HTTPMethodNotAllowed(
                allowed_methods=['GET', 'POST', 'PUT','OPTIONS'],
                description='New observation points must be created without an observation_point_id'
            )

        try:
            

            # load the request body
            observation_point_dict = json.loads(request.stream.read() or 0)

            #sanitize input
            bad_keys = ['id']
            for key in bad_keys:
                if(key in observation_point_dict):
                    del observation_point_dict[key]

           
            #test route exisits
            if ('route' in observation_point_dict):
                route = Routes.get_by_id(observation_point_dict['route'])

            #create new route
            new_observation_point = None
    

            new_observation_point = dict_to_model(ObservationPoints, observation_point_dict, ignore_unknown=True)
            new_observation_point.save()

        
        except Routes.DoesNotExist as e:
            raise falcon.HTTPNotFound(
                description='Route with id: ' + str(observation_point_dict['route'])  + ' not found'
            )

        except Exception as e:
                raise falcon.HTTPBadRequest(description=str(e))

        response.status = falcon.HTTP_CREATED
        response.body = json.dumps(model_to_dict(new_observation_point),default=json_serial)

        
    @falcon.before(check_logged_in)
    def on_put(self, request, response, observation_point_id=None):
           # Do not allow POST (create) when route_id is given
        if observation_point_id is None:
            raise falcon.HTTPBadRequest(description="observation_point_id can not be empty: observation-point/123")

        user_ID = request.get_header('user-ID')
        if(not self.edit_premissions(user_ID,observation_point_id)):
            raise falcon.HTTPUnauthorized(
                description='You do not have premission to edit this Observation Point'
                )

        try:

            # load the request body
            changes = json.loads(request.stream.read() or 0)

            #sanitize input
            bad_keys = ['id']
            for key in bad_keys:
                if(key in changes):
                    del changes[key]

            #test route exisits
            if ('route' in changes):
                route = Routes.get_by_id(changes['route'])

           
            #find observation point
            observation_point = ObservationPoints.get_by_id(observation_point_id)
            observation_point_dict = model_to_dict(observation_point, recurse=False)
            
            # apply the changes
            for field in changes:
                observation_point_dict[field] = changes[field]

            # save changes
            updated_observation_point = dict_to_model(ObservationPoints, observation_point_dict, ignore_unknown=True)
            updated_observation_point.save()

        except Routes.DoesNotExist as e:
            raise falcon.HTTPNotFound(
                description='Route with route_id: ' + str(changes['route'])  + ' not found'
            )

        except ObservationPoints.DoesNotExist as e:
            raise falcon.HTTPNotFound(
                description='Observation point with observation_point_id: ' + str(observation_point_id)  + ' not found'
            )

        except Exception as e:
            raise falcon.HTTPInternalServerError(description=str(e))


        response.body = json.dumps(model_to_dict(updated_observation_point),default=json_serial)

        

    @falcon.before(check_logged_in)
    def on_delete(self, request, response, observation_point_id=None):
        
        if observation_point_id is None:
            raise falcon.HTTPBadRequest(description="observation_point_id can not be empty: observation-point/123")

        user_ID = request.get_header('user-ID')
        if(not self.edit_premissions(user_ID,observation_point_id)):
            raise falcon.HTTPUnauthorized(
                description='You do not have premission to delete this Observation Point'
                )
        

        try:

            #find observation point
            observation_point = ObservationPoints.get_by_id(observation_point_id)
            observation_point.delete_instance()
            
        except ObservationPoints.DoesNotExist as e:
            raise falcon.HTTPNotFound(
                description='Observation point with observation_point_id: ' + str(observation_point_id)  + ' not found'
            )
            
        except Exception as e:
            print (e)
            raise falcon.HTTPInternalServerError(description=str(e))
        
        response.status = falcon.HTTP_NO_CONTENT
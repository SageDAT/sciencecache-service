import json
import uuid
import falcon
from sciencecache_model import *
from playhouse.shortcuts import dict_to_model, model_to_dict
from utilities import *
import datetime


class visit_values_end_point():


    def on_get(self, request, response, visit_values_id = None):


        results =[]
        try:
            with sciencecache_database.transaction():

                if (visit_values_id is not None):
                    visit_values = VisitValues.get_by_id(visit_values_id)
                    results = model_to_dict(visit_values,recurse=False)

                elif(request.get_param('obspnt_visit_form')):
                    obspnt_visit_form_id = request.get_param('obspnt_visit_form')
                    for r in  VisitValues.select().where(VisitValues.obspnt_visit_form == obspnt_visit_form_id):
                        results.append(model_to_dict(r, recurse=False))

                else:
                    for r in VisitValues.select():
                        results.append(model_to_dict(r, recurse=False))


        except VisitValues.DoesNotExist as e:
            raise falcon.HTTPNotFound(
                description='visit_values with visit_values_id: ' + str(visit_values_id) + ' not found'
            )
        except Exception as e:
            print(e)
            raise falcon.HTTPBadRequest(description="Failed to get visit_values")

        response.body = json.dumps(results, default=json_serial)


    @falcon.before(check_logged_in)
    def on_post(self, request, response, visit_values_id = None):


        # Do not allow POST (create) when visit_values_id is given
        if visit_values_id is not None:
            raise falcon.falcon.HTTPMethodNotAllowed(
                allowed_methods=['GET', 'POST', 'PUT','OPTIONS'],
                description='New visit_values must be created without an visit_values_id'
            )

        try:

            # load the request body
            visit_values_dict = json.loads(request.stream.read() or 0)

            #sanitize input
            bad_keys = ['id','date_captured']
            for key in bad_keys:
                if(key in visit_values_dict):
                    del visit_values_dict[key]

            visit_values_dict['date_captured'] = str(datetime.datetime.now())

            #create new visit_values
            new_visit_values = None


            new_visit_values = dict_to_model(VisitValues, visit_values_dict, ignore_unknown=True)
            new_visit_values.save()


        except Exception as e:
            raise falcon.HTTPBadRequest(description=str(e))

        response.status = falcon.HTTP_CREATED
        response.body = json.dumps(model_to_dict(new_visit_values,recurse=False),default=json_serial)


    @falcon.before(check_logged_in)
    def on_put(self, request, response, visit_values_id=None):
        # Do not allow POST (create) when visit_values_id is given
        if visit_values_id is None:
            raise falcon.HTTPBadRequest(description="visit_values_id can not be empty: visit-values/123")

        try:

            # load the request body
            changes = json.loads(request.stream.read() or 0)

            #sanitize input
            bad_keys = ['id']
            for key in bad_keys:
                if(key in changes):
                    del changes[key]


            #find visit_values
            visit_values = VisitValues.get_by_id(visit_values_id)
            visit_values_dict = model_to_dict(visit_values, recurse=False)

            # apply the changes
            for field in changes:
                visit_values_dict[field] = changes[field]

            # save changes
            updated_visit_values = dict_to_model(VisitValues, visit_values_dict, ignore_unknown=True)
            updated_visit_values.save()

        except VisitValues.DoesNotExist as e:
            raise falcon.HTTPNotFound(
                description='visit_values with visit_values_id: ' + str(visit_values_id) + ' not found'
            )

        except Exception as e:
            raise falcon.HTTPInternalServerError(description=str(e))


        response.body = json.dumps(model_to_dict(updated_visit_values),default=json_serial)



    @falcon.before(check_logged_in)
    def on_delete(self, request, response, visit_values_id=None):

        if visit_values_id is None:
            raise falcon.HTTPBadRequest(description="visit_values_id can not be empty: visit-values/123")


        try:
            #find visit_values
            visit_values = VisitValues.get_by_id(visit_values_id)
            visit_values.delete_instance()

        except VisitValues.DoesNotExist as e:
            raise falcon.HTTPNotFound(
                description='visit_values with visit_values_id: ' + str(visit_values_id) + ' not found'
            )

        except Exception as e:
            print (e)
            raise falcon.HTTPInternalServerError(description=str(e))

        response.status = falcon.HTTP_NO_CONTENT
import json
import uuid
import falcon
from sciencecache_model import *
from playhouse.shortcuts import dict_to_model, model_to_dict
from utilities import *

class visit_form_data_request_end_point():


    def on_get(self, request, response, visit_form_data_request_id = None):


        results =[]
        try:
            with sciencecache_database.transaction():

                if (visit_form_data_request_id is not None):
                    visit_form_data_request = VisitFormDatarequests.get_by_id(visit_form_data_request_id)
                    results = model_to_dict(visit_form_data_request, recurse=True)

                elif(request.get_param('visitform')):
                    visit_form_id = request.get_param('visitform')
                    for r in VisitFormDatarequests.select().where(VisitFormDatarequests.visit_form == visit_form_id):
                        results.append(model_to_dict(r, recurse=True))

                else:
                    for r in VisitFormDatarequests.select():
                        results.append(model_to_dict(r, recurse=False))


        except VisitFormDatarequests.DoesNotExist as e:
            raise falcon.HTTPNotFound(
                description='Visit form data requests with visit_form_data_request_id: ' + str(visit_form_data_request_id)  + ' not found'
            )
        except Exception as e:
            print(e)
            raise falcon.HTTPBadRequest(description="Failed to get Visit form data request")

        response.body = json.dumps(results, default=json_serial)


    @falcon.before(check_logged_in)
    def on_post(self, request, response, visit_form_data_request_id = None):

        # Do not allow POST (create) when visit_form_data_request_id is given
        if visit_form_data_request_id is not None:
            raise falcon.falcon.HTTPMethodNotAllowed(
                allowed_methods=['GET', 'POST', 'PUT','OPTIONS'],
                description='Visit form data requests must be created without an visit_form_data_request_id'
            )

        try:

            # load the request body
            visit_form_data_request_dict = json.loads(request.stream.read() or 0)

            #sanitize input
            bad_keys = ['id']
            for key in bad_keys:
                if(key in visit_form_data_request_dict):
                    del visit_form_data_request_dict[key]


            #create new Visit form data request
            new_visit_form_data_request = None


            new_visit_form_data_request = dict_to_model(VisitFormDatarequests, visit_form_data_request_dict, ignore_unknown=True)
            new_visit_form_data_request.save()


        except Exception as e:
            raise falcon.HTTPBadRequest(description=str(e))

        response.status = falcon.HTTP_CREATED
        response.body = json.dumps(model_to_dict(new_visit_form_data_request),default=json_serial)


    @falcon.before(check_logged_in)
    def on_put(self, request, response, visit_form_data_request_id=None):
        # Do not allow POST (create) when visit_form_data_request_id is given
        if visit_form_data_request_id is None:
            raise falcon.HTTPBadRequest(description="visit_form_data_request_id can not be empty: visit-from-data-request/123")

        try:
            # load the request body
            changes = json.loads(request.stream.read() or 0)

            #sanitize input
            bad_keys = ['id']
            for key in bad_keys:
                if(key in changes):
                    del changes[key]

            #find View form data request
            visit_form_data_request = VisitFormDatarequests.get_by_id(visit_form_data_request_id)
            visit_form_data_request_dict = model_to_dict(visit_form_data_request, recurse=False)

            # apply the changes
            for field in changes:
                visit_form_data_request_dict[field] = changes[field]

            # save changes
            updated_visit_form_data_request = dict_to_model(VisitFormDatarequests, visit_form_data_request_dict, ignore_unknown=True)
            updated_visit_form_data_request.save()

        except VisitFormDatarequests.DoesNotExist as e:
            raise falcon.HTTPNotFound(
                description='Visit form data request with visit_form_data_requests_id: ' + str(visit_form_data_request_id) + ' not found'
            )

        except Exception as e:
            raise falcon.HTTPInternalServerError(description=str(e))

        response.body = json.dumps(model_to_dict(updated_visit_form_data_request),default=json_serial)



    @falcon.before(check_logged_in)
    def on_delete(self, request, response, visit_form_data_request_id=None):

        if visit_form_data_request_id is None:
            raise falcon.HTTPBadRequest(description="visit_form_data_request_id can not be empty: visit-from-data-request/123")

        try:
            #find Visit form data request
            visit_form_data_request = VisitFormDatarequests.get_by_id(visit_form_data_request_id)
            visit_form_data_request.delete_instance()

        except VisitFormDatarequests.DoesNotExist as e:
            raise falcon.HTTPNotFound(
                description='Visit form data request with visit_form_data_request_id: ' + str(visit_form_data_request_id) + ' not found'
            )

        except Exception as e:
            print (e)
            raise falcon.HTTPInternalServerError(description=str(e))

        response.status = falcon.HTTP_NO_CONTENT
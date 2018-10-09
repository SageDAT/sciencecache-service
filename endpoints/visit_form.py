import json
import uuid
import falcon
from sciencecache_model import *
from playhouse.shortcuts import dict_to_model, model_to_dict
from utilities import *

class visit_form_end_point():


    def on_get(self, request, response, visit_form_id = None):
        "This will return a list of visit forms"

        results =[]
        try:
            with sciencecache_database.transaction():

                if (visit_form_id is not None):
                    visitform = VisitForm.get_by_id(visit_form_id)
                    results = model_to_dict(visitform,recurse=False)

                elif(request.get_param('observationpoint')):
                    obspnt_id = request.get_param('observationpoint')
                    forms = VisitForm.select().join(VisitFormDatarequests).join(ObspntVisitForm).where(ObspntVisitForm.observation_point == obspnt_id)
                    for r in forms:
                        results.append(model_to_dict(r, recurse=True))

                else:
                    for r in VisitForm.select():
                        results.append(model_to_dict(r, recurse=False))


        except VisitForm.DoesNotExist as e:
            raise falcon.HTTPNotFound(
                description='visit form  with visit_form_id: ' + str(visit_form_id)  + ' not found'
            )
        except Exception as e:
            print(e)
            raise falcon.HTTPBadRequest(description="Failed to get visit form ")

        response.body = json.dumps(results, default=json_serial)


    @falcon.before(check_logged_in)
    def on_post(self, request, response, visit_form_id = None):
        "This will post a new visit form"

        # Do not allow POST (create) when visit_form_id is given
        if visit_form_id is not None:
            raise falcon.falcon.HTTPMethodNotAllowed(
                allowed_methods=['GET', 'POST', 'PUT','OPTIONS'],
                description='New form must be created without an visit_form_id'
            )

        try:

            # load the request body
            visit_form_dict = json.loads(request.stream.read() or 0)

            #sanitize input
            bad_keys = ['id','owner']
            for key in bad_keys:
                if(key in visit_form_dict):
                    del visit_form_dict[key]


            #create new form
            new_visit_form = None


            new_visit_form = dict_to_model(VisitForm, visit_form_dict, ignore_unknown=True)
            new_visit_form.save()


        except Exception as e:
            raise falcon.HTTPBadRequest(description=str(e))

        response.status = falcon.HTTP_CREATED
        response.body = json.dumps(model_to_dict(new_visit_form),default=json_serial)


    @falcon.before(check_logged_in)
    def on_put(self, request, response, visit_form_id=None):
        "Update a view form"
        # Do not allow POST (create) when visit_form_id is given
        if visit_form_id is None:
            raise falcon.HTTPBadRequest(description="visit_form_id can not be empty: visitform/123")

        try:
            # load the request body
            changes = json.loads(request.stream.read() or 0)

            #sanitize input
            bad_keys = ['id']
            for key in bad_keys:
                if(key in changes):
                    del changes[key]

            #find viewform
            visit_form = VisitForm.get_by_id(visit_form_id)
            visit_form_dict = model_to_dict(visit_form, recurse=False)

            # apply the changes
            for field in changes:
                visit_form_dict[field] = changes[field]

            # save changes
            updated_visit_form = dict_to_model(VisitForm, visit_form_dict, ignore_unknown=True)
            updated_visit_form.save()

        except VisitForm.DoesNotExist as e:
            raise falcon.HTTPNotFound(
                description='visit form with visit_form_id: ' + str(visit_form_id) + ' not found'
            )

        except Exception as e:
            raise falcon.HTTPInternalServerError(description=str(e))


        response.body = json.dumps(model_to_dict(updated_visit_form),default=json_serial)



    @falcon.before(check_logged_in)
    def on_delete(self, request, response, visit_form_id=None):

        if visit_form_id is None:
            raise falcon.HTTPBadRequest(description="visit_form_id can not be empty: visitform/123")

        try:
            #find visit form
            visit_form = VisitForm.get_by_id(visit_form_id)
            visit_form.delete_instance()

        except VisitForm.DoesNotExist as e:
            raise falcon.HTTPNotFound(
                description='visit form with visit_form_id: ' + str(visit_form_id) + ' not found'
            )

        except Exception as e:
            print (e)
            raise falcon.HTTPInternalServerError(description=str(e))

        response.status = falcon.HTTP_NO_CONTENT
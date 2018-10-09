import json
import uuid
import falcon
from sciencecache_model import *
from playhouse.shortcuts import dict_to_model, model_to_dict
from utilities import *

class obspnt_visit_form_end_point():

    def on_get(self, request, response, obspnt_visit_form_id = None):

        results =[]
        try:
            with sciencecache_database.transaction():

                if (obspnt_visit_form_id is not None):
                    obspnt_visit_form = ObspntVisitForm.get_by_id(obspnt_visit_form_id)
                    results = model_to_dict(obspnt_visit_form, recurse=True)

                elif(request.get_param('observationpoint')):
                    obspnt_id = request.get_param('observationpoint')
                    for r in  ObspntVisitForm.select().where(ObspntVisitForm.observation_point == obspnt_id):
                        results.append(model_to_dict(r, recurse=True))

                else:
                    for r in ObspntVisitForm.select():
                        results.append(model_to_dict(r, recurse=False))


        except ObspntVisitForm.DoesNotExist as e:
            raise falcon.HTTPNotFound(
                description='ObsPnt Visit form with id: ' + str(obspnt_visit_form_id) + ' not found'
            )
        except Exception as e:
            print(e)
            raise falcon.HTTPBadRequest(description="Failed to get Obs Pnt Visit Form")

        response.body = json.dumps(results, default=json_serial)

    @falcon.before(check_logged_in)
    def on_post(self, request, response, obspnt_visit_form_id = None):

        # Do not allow POST (create) when obspnt_visit_form_id is given
        if obspnt_visit_form_id is not None:
            raise falcon.falcon.HTTPMethodNotAllowed(
                allowed_methods=['GET', 'POST', 'PUT','OPTIONS'],
                description='Obs Pnt Visit form must be created without an obspnt_visit_form_id'
            )

        try:

            # load the request body
            obspnt_visit_form_dict = json.loads(request.stream.read() or 0)

            #sanitize input
            bad_keys = ['id']
            for key in bad_keys:
                if(key in obspnt_visit_form_dict):
                    del obspnt_visit_form_dict[key]


            #create new Obs Visit form
            new_obspnt_visit_form = None


            new_obspnt_visit_form = dict_to_model(ObspntVisitForm, obspnt_visit_form_dict, ignore_unknown=True)
            new_obspnt_visit_form.save()


        except Exception as e:
            raise falcon.HTTPBadRequest(description=str(e))

        response.status = falcon.HTTP_CREATED
        response.body = json.dumps(model_to_dict(new_obspnt_visit_form),default=json_serial)


    @falcon.before(check_logged_in)
    def on_put(self, request, response, obspnt_visit_form_id=None):
        # Do not allow POST (create) when obspnt_visit_form_id is given
        if obspnt_visit_form_id is None:
            raise falcon.HTTPBadRequest(description="obspnt_visit_form_id can not be empty: obspnt-visit-form/123")

        try:
            # load the request body
            changes = json.loads(request.stream.read() or 0)

            #sanitize input
            bad_keys = ['id']
            for key in bad_keys:
                if(key in changes):
                    del changes[key]

            #find Obspnt visit form
            obspnt_visit_form = ObspntVisitForm.get_by_id(obspnt_visit_form_id)
            obspnt_visit_form_dict = model_to_dict(obspnt_visit_form, recurse=False)

            # apply the changes
            for field in changes:
                obspnt_visit_form_dict[field] = changes[field]

            # save changes
            updated_obspnt_visit_form = dict_to_model(ObspntVisitForm, obspnt_visit_form_dict, ignore_unknown=True)
            updated_obspnt_visit_form.save()

        except ObspntVisitForm.DoesNotExist as e:
            raise falcon.HTTPNotFound(
                description='Obs Pnt Visit Form with obspnt_visit_form_id: ' + str(obspnt_visit_form_id) + ' not found'
            )

        except Exception as e:
            raise falcon.HTTPInternalServerError(description=str(e))

        response.body = json.dumps(model_to_dict(updated_obspnt_visit_form),default=json_serial)



    @falcon.before(check_logged_in)
    def on_delete(self, request, response, obspnt_visit_form_id=None):

        if obspnt_visit_form_id is None:
            raise falcon.HTTPBadRequest(description="obspnt_visit_form_id can not be empty: obspnt-visit-form/123")

        try:
            #find Obs Visit form
            obspnt_visit_form = ObspntVisitForm.get_by_id(obspnt_visit_form_id)
            obspnt_visit_form.delete_instance()

        except ObspntVisitForm.DoesNotExist as e:
            raise falcon.HTTPNotFound(
                description='Obs Pnt Visit form with obspnt_visit_form_id: ' + str(obspnt_visit_form_id) + ' not found'
            )

        except Exception as e:
            print (e)
            raise falcon.HTTPInternalServerError(description=str(e))

        response.status = falcon.HTTP_NO_CONTENT
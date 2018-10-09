import json
import uuid
import falcon
from sciencecache_model import *
from playhouse.shortcuts import dict_to_model, model_to_dict
from utilities import *

class form_end_point():


    def on_get(self, request, response, form_id = None):


        results =[]
        try:
            with sciencecache_database.transaction():  
                
                if (form_id is not None):
                    form = ObsPointForm.get_by_id(form_id)
                    results = model_to_dict(form,recurse=False)

                else:
                    for r in ObsPointForm.select():
                        results.append(model_to_dict(r, recurse=False))
            

        except ObsPointForm.DoesNotExist as e:
            raise falcon.HTTPNotFound(
                description='form  with form_id: ' + str(form_id)  + ' not found'
            )
        except Exception as e:
            print(e)
            raise falcon.HTTPBadRequest(description="Failed to get form ")

        response.body = json.dumps(results, default=json_serial)


    @falcon.before(check_logged_in)    
    def on_post(self, request, response, form_id = None):
        
        
        # Do not allow POST (create) when form_id is given
        if form_id is not None:
            raise falcon.falcon.HTTPMethodNotAllowed(
                allowed_methods=['GET', 'POST', 'PUT','OPTIONS'],
                description='New form must be created without an form_id'
            )

        try:
            
            # load the request body
            form_dict = json.loads(request.stream.read() or 0)

            #sanitize input
            bad_keys = ['id','owner']
            for key in bad_keys:
                if(key in form_dict):
                    del form_dict[key]


            #create new form
            new_form = None
    

            new_form = dict_to_model(ObsPointForm, form_dict, ignore_unknown=True)
            new_form.save()


        except Exception as e:
                raise falcon.HTTPBadRequest(description=str(e))

        response.status = falcon.HTTP_CREATED
        response.body = json.dumps(model_to_dict(new_form),default=json_serial)

        
    @falcon.before(check_logged_in)
    def on_put(self, request, response, form_id=None):
           # Do not allow POST (create) when form_id is given
        if form_id is None:
            raise falcon.HTTPBadRequest(description="form_id can not be empty: form/123")

        try:

            # load the request body
            changes = json.loads(request.stream.read() or 0)

            #sanitize input
            bad_keys = ['id']
            for key in bad_keys:
                if(key in changes):
                    del changes[key]

           
            #find form 
            form = ObsPointForm.get_by_id(form_id)
            form_dict = model_to_dict(form, recurse=False)
            
            # apply the changes
            for field in changes:
                form_dict[field] = changes[field]

            # save changes
            updated_form = dict_to_model(ObsPointForm, form_dict, ignore_unknown=True)
            updated_form.save()

        except ObsPointForm.DoesNotExist as e:
            raise falcon.HTTPNotFound(
                description='form with forms_id: ' + str(form_id)   + ' not found'
            )

        except Exception as e:
            raise falcon.HTTPInternalServerError(description=str(e))


        response.body = json.dumps(model_to_dict(updated_form),default=json_serial)

        

    @falcon.before(check_logged_in)
    def on_delete(self, request, response, form_id=None):
        
        if form_id is None:
            raise falcon.HTTPBadRequest(description="form_id can not be empty: form/123")
        

        try:

            #find form  
            form = ObsPointForm.get_by_id(form_id)
            form.delete_instance()
            
        except ObsPointForm.DoesNotExist as e:
            raise falcon.HTTPNotFound(
                description='form  with form_id: ' + str(form_id)  + ' not found'
            )
            
        except Exception as e:
            print (e)
            raise falcon.HTTPInternalServerError(description=str(e))
        
        response.status = falcon.HTTP_NO_CONTENT
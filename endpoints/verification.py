import json
import falcon
from sciencecache_model import *
from playhouse.shortcuts import dict_to_model, model_to_dict
from utilities import *


class verification_end_point():

    def on_put(self, request, response):

        try:

            # load the request body
            verification_data = json.loads(request.stream.read() or 0)

            #sanitize input
            bad_keys = ['id']
            for key in bad_keys:
                if(key in verification_data):
                    del verification_data[key]

            # #find user
            # user = User.select().where(User.user_email == verification_data['user_email']).get()
            # user_dict = model_to_dict(user, recurse=False)

            deviceUser_dict = None
            try:
                deviceUser = Deviceinfo.select().where((Deviceinfo.user_email == verification_data['user_email']) & (Deviceinfo.uuid == verification_data['user_uuid']) ).get()
                deviceUser_dict = model_to_dict(deviceUser, recurse=False)
            except:
                pass

            if deviceUser_dict:
                deviceUser_dict['is_validated'] = True
                updated_user = dict_to_model(Deviceinfo, deviceUser_dict, ignore_unknown=True)
                updated_user.save()
                info = {
                    'isSuccessful': True
                }

            else:
                info = {
                    'isSuccessful': False
                }
                response.status = falcon.HTTP_500

        except User.DoesNotExist as e:
            raise falcon.HTTPError(
                description='Unable to verify'
            )

        except Exception as e:
            raise falcon.HTTPInternalServerError(description=str(e))

        # response.body = json.dumps(model_to_dict(updated_user),default=json_serial)
        response.body = json.dumps(info, ensure_ascii=False)

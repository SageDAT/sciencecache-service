import json
import uuid
import falcon
from sciencecache_model import *
from playhouse.shortcuts import dict_to_model, model_to_dict
from utilities import *
import smtplib
from email.mime.text import MIMEText

class deviceinfo_end_point():


    @falcon.before(check_logged_in)
    def on_get(self, request, response, deviceinfo_id = None):


        results =[]
        try:
            with sciencecache_database.transaction():

                if (deviceinfo_id is not None):
                    deviceinfo = Deviceinfo.get_by_id(deviceinfo_id)
                    results = model_to_dict(deviceinfo,recurse=True)


                elif(request.get_param('form')):
                    form_id = request.get_param('form')
                    for r in  Deviceinfo.select().where(Deviceinfo.obs_point_form == form_id):
                        results.append(model_to_dict(r, recurse=True))


                else:
                    for r in Deviceinfo.select():
                        results.append(model_to_dict(r, recurse=False))


        except Deviceinfo.DoesNotExist as e:
            raise falcon.HTTPNotFound(
                description='Deviceinfo with deviceinfo_id: ' + str(deviceinfo_id)  + ' not found'
            )
        except Exception as e:
            print(e)
            raise falcon.HTTPBadRequest(description="Failed to get Deviceinfo")

        response.body = json.dumps(results, default=json_serial)



    def on_post(self, request, response, deviceinfo_id = None):


        # Do not allow POST (create) when deviceinfo_id is given
        if deviceinfo_id is not None:
            raise falcon.falcon.HTTPMethodNotAllowed(
                allowed_methods=['GET', 'POST', 'PUT','OPTIONS'],
                description='Deviceinfo must be created without an deviceinfo_id'
            )

        try:
            # load the request body
            deviceinfo_dict = json.loads(request.stream.read() or 0)

            email_token = str(uuid.uuid4())

            #sanitize input
            bad_keys = ['id', 'is_validated']
            for key in bad_keys:
                if(key in deviceinfo_dict):
                    del deviceinfo_dict[key]

            incomingUUID = deviceinfo_dict['uuid']
            incomingEmail = deviceinfo_dict['user_email']

            #if uuid already exists
            deviceUser_dict = None
            try:
                if incomingEmail:
                    deviceUser = Deviceinfo.select().where((Deviceinfo.user_email == incomingEmail) & (Deviceinfo.uuid == incomingUUID) ).get()
                    deviceUser_dict = model_to_dict(deviceUser, recurse=False)
                else:
                    deviceUser = Deviceinfo.select().where(Deviceinfo.uuid == incomingUUID).get()
                    deviceUser_dict = model_to_dict(deviceUser, recurse=False)
            except:
                pass

            if deviceUser_dict:
                print('found preexisting')

                # apply the changes -- put
                for field in deviceinfo_dict:
                    deviceUser_dict[field] = deviceinfo_dict[field]

                deviceUser_dict['email_token'] = email_token

                # save changes
                updated_deviceinfo = dict_to_model(Deviceinfo, deviceUser_dict, ignore_unknown=True)
                updated_deviceinfo.save()

                #check if verified
                if deviceUser_dict['user_email'] and not deviceUser_dict['is_validated']:
                    print('we have email and is not validated!')
                    sendRegisterEmail(updated_deviceinfo)
                    print('resending email')


                # response.body = json.dumps(model_to_dict(updated_deviceinfo), default=json_serial)
                info = {
                    'isSuccessful': True,
                    'isUpdate': True,
                    'isNew': False
                }
                response.body = json.dumps(info, ensure_ascii=False)

            else:
                print('no preexisting user')
                #check for preexising device uuid

                #create new Deviceinfo -- post
                new_deviceinfo = None
                deviceinfo_dict['is_validated'] = False
                deviceinfo_dict['email_token'] = email_token
                new_deviceinfo = dict_to_model(Deviceinfo, deviceinfo_dict, ignore_unknown=True)

                #remove new verfication_uuid before save
                new_deviceinfo.save()

                #also check for is_validated
                if(new_deviceinfo.user_email):
                    # make temp uuid
                    sendRegisterEmail(new_deviceinfo)

                response.status = falcon.HTTP_CREATED
                # response.body = json.dumps(model_to_dict(new_deviceinfo), default=json_serial)
                info = {
                    'isSuccessful': True,
                    'isUpdate': False,
                    'isNew': True
                }
                response.body = json.dumps(info, ensure_ascii=False)



        except Exception as e:
            raise falcon.HTTPBadRequest(description=str(e))



    @falcon.before(check_logged_in)
    def on_put(self, request, response, deviceinfo_id=None):
        # Do not allow POST (create) when deviceinfo_id is given
        if deviceinfo_id is None:
            raise falcon.HTTPBadRequest(description="deviceinfo_id can not be empty: deviceinfo/123")

        try:

            # load the request body
            changes = json.loads(request.stream.read() or 0)

            #sanitize input
            bad_keys = ['id']
            for key in bad_keys:
                if(key in changes):
                    del changes[key]


            #find Deviceinfo to update
            deviceinfo = Deviceinfo.get_by_id(deviceinfo_id)
            deviceinfo_dict = model_to_dict(deviceinfo, recurse=False)

            # apply the changes
            for field in changes:
                deviceinfo_dict[field] = changes[field]

            # save changes
            updated_deviceinfo = dict_to_model(Deviceinfo, deviceinfo_dict, ignore_unknown=True)
            updated_deviceinfo.save()

        except Deviceinfo.DoesNotExist as e:
            raise falcon.HTTPNotFound(
                description='Deviceinfo with deviceinfo_id: ' + str(deviceinfo_id)   + ' not found'
            )

        except Exception as e:
            raise falcon.HTTPInternalServerError(description=str(e))

        response.body = json.dumps(model_to_dict(updated_deviceinfo),default=json_serial)



    @falcon.before(check_logged_in)
    def on_delete(self, request, response, deviceinfo_id=None):

        if deviceinfo_id is None:
            raise falcon.HTTPBadRequest(description="deviceinfo_id can not be empty: deviceinfo/123")


        try:
            #find Deviceinfo
            deviceinfo = Deviceinfo.get_by_id(deviceinfo_id)
            deviceinfo.delete_instance()

        except Deviceinfo.DoesNotExist as e:
            raise falcon.HTTPNotFound(
                description='Deviceinfo with deviceinfo_id: ' + str(deviceinfo_id)  + ' not found'
            )

        except Exception as e:
            print (e)
            raise falcon.HTTPInternalServerError(description=str(e))

        response.status = falcon.HTTP_NO_CONTENT


def sendRegisterEmail(deviceinfo):
    """Device info email sending method"""

    url = configuration['email']['siteurl'] + 'verifyuser?email=' + deviceinfo.user_email + '&uuid=' + deviceinfo.uuid + '&token=' + deviceinfo.email_token

    # try:
    message = "You have started registration for the ScienceCache citizen science phone application. Please click the\n" \
              "registration link below to complete registration.<p></p> <a href=\"" + url + "\">Register Here</a>"
    email = MIMEText(message, 'html')
    email['Subject'] = 'Sciencecache email registration'
    email['From'] = configuration['email']['from_email']
    email['Content'] = 'Content-type: text/html'

    email_recipients = []
    email_recipients.append(str(deviceinfo.user_email))
    email['To'] = ", ".join(email_recipients)

    send_registration = smtplib.SMTP(configuration['email']['smtp'])
    send_registration.sendmail(email['From'], email_recipients, email.as_string())
    send_registration.quit()
    # except Exception as e:
    #     print(e)
    # raise falcon.HTTPInternalServerError(
    #     title='Error sending registration email.',
    #     description='Failed to send'
    # )
import falcon
import json
import datetime
from google.oauth2 import id_token
from google.auth.transport import requests
from environment import *
from sciencecache_model import *
from playhouse.shortcuts import dict_to_model, model_to_dict






def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, (datetime.datetime, datetime.date)):
        return obj.isoformat()
    else:
        return str(obj)
    raise TypeError("Type %s not serializable" % type(obj))


def insert_user(info,user_id):
    try:
        user = User.select().where(User.user_email == info['email']).get()
        if(user_id is not None):
            if(int(user_id) != int(user.id)):
                raise falcon.HTTPUnauthorized(
                    description='user-ID header: ' + str(user_id) +  ' does not match logged-in user: ' + str(user.id)
                    )


    except User.DoesNotExist as e:
        if '@usgs.gov' in info['email'] or '@contractor.usgs.gov' in info['email']:
            print('Valid email')
            user_dict = {}
            user_dict['user_email'] = info['email']
            user_dict['first_name'] = info['given_name']
            user_dict['last_name'] = info['family_name']
            user_dict['is_admin'] = False
            new_user = dict_to_model(User, user_dict, ignore_unknown=True)
            new_user.save()
        else:
            print('Invalid email')

            

def validate_token(token, email,user_id):

    if token == None or email == None:
        # Either the token or the email were not provided, we need both to verify
        return False
    
    try:

        # multiple clients access the backend server:
        idinfo = id_token.verify_oauth2_token(token, requests.Request())
        if idinfo['aud'] not in configuration["front_end_IDS"]:
            raise ValueError('Could not verify audience.' + idinfo['aud'] )

        if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            raise ValueError('Wrong issuer.')

        # ID token is valid. Get the user's Google Account ID from the decoded token.
        userEmail = idinfo['email']
        if userEmail == email:
            insert_user(idinfo,user_id)
            return True

    except ValueError:
        # Invalid token
        pass

    return False


def validate_device(uuid, email):

    if uuid == None or email == None:
        return False

    try:
        validateThisDeviceInfo = Deviceinfo.select().where((Deviceinfo.user_email == email) & (Deviceinfo.uuid == uuid)).get()

        if validateThisDeviceInfo and validateThisDeviceInfo.is_validated == True:
            return True
        else:
            return False

    except Deviceinfo.DoesNotExist as e:
        raise falcon.HTTPNotFound(description='Device info: ' + str(uuid) + ' ' + str(email) + ' not found')



def check_logged_in(request, response, resource, params):
    token = request.get_header('IDToken')
    email = request.get_header('email-address')
    user_ID = request.get_header('user-ID')

    if token is None:
        raise falcon.HTTPMissingHeader(header_name='IDToken')
    if email is None:
        raise falcon.HTTPMissingHeader(header_name='email-address')

    authorized = validate_token(token,email,user_ID)
    if not authorized:
        raise falcon.HTTPUnauthorized(
            description='You must be logged in to use this service.'
        )

def check_valid_device(request, response, resource, params):
    email = request.get_header('email-address')
    uuid = request.get_header('uuid')

    if uuid is None:
        raise falcon.HTTPMissingHeader(header_name='uuid')
    if email is None:
        raise falcon.HTTPMissingHeader(header_name='email-address')

    authorized = validate_device(uuid, email)
    if not authorized:
        raise falcon.HTTPUnauthorized(
            description='You are not authorized.'
        )
    
def get_user(id):
    try:
        return User.get_by_id(id)
    except User.DoesNotExist as e:
        return None

def get_user_via_email(email):
    try:
        return User.get(User.user_email == email)
    except User.DoesNotExist as e:
        return None

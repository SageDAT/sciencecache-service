#!/usr/bin/env python

import json
import os
import sys
from os.path import join, dirname
from falcon_cors import CORS
from peewee import *
import falcon




# Ensure that Python knows where to find our custom modules
sys.path.append(os.path.dirname(__file__))
from environment import *

class PeeweeConnectionMiddleware(object):
    def process_request(self, req, resp):
        sciencecache_database.connect()

    def process_response(self, req, resp, resource):
        if not sciencecache_database.is_closed():
            sciencecache_database.close()

class Default:
  def on_get(self, request, response):
    response.status = falcon.HTTP_200
    response.body=json.dumps({'message' : 'ScienceCache Service RESTful queries.'})


cors = CORS(allow_all_origins = True, allow_methods_list=['POST', 'PUT', 'GET', 'DELETE', 'PATCH'], allow_all_headers=True)
sciencecache = Default()
app = application = falcon.API(
  middleware=[
    PeeweeConnectionMiddleware(),
    cors.middleware
  ]
)

from endpoints.route import route_end_point
from endpoints.route_difficulty import route_difficulty_end_point
from endpoints.route_length import route_length_end_point
from endpoints.observation_point import observation_point_end_point
from endpoints.observation_point_type import observation_point_type_end_point
from endpoints.user import user_end_point
from endpoints.user_role_route import user_role_route_end_point
from endpoints.users import users_end_point
from endpoints.roles import roles_end_point
from endpoints.data_request import data_request_end_point
from endpoints.form import form_end_point
from endpoints.visit_form import visit_form_end_point
from endpoints.obs_form_datarequests import obs_form_data_request_end_point
from endpoints.visit_form_datarequests import visit_form_data_request_end_point
from endpoints.obs_point_values import obs_point_values_end_point
from endpoints.visit_values import visit_values_end_point
from endpoints.obspnt_visit_form import obspnt_visit_form_end_point
from endpoints.image import image_end_point
from endpoints.deviceinfo import deviceinfo_end_point
from endpoints.verification import verification_end_point

from mobile_endpoints.route import mobile_route_end_point
from mobile_endpoints.observation_point import mobile_observation_point_end_point

# Defined Routes
app.add_route('/', Default())
app.add_route('/user', user_end_point())
app.add_route('/routes', route_end_point())
app.add_route('/routes/{route_id}', route_end_point())
app.add_route('/observation-point', observation_point_end_point())
app.add_route('/observation-point/{observation_point_id}', observation_point_end_point())
app.add_route('/observation-point-type', observation_point_type_end_point())
app.add_route('/observation-point-type/{observation_point_type_id}', observation_point_type_end_point())
app.add_route('/route-difficulty', route_difficulty_end_point())
app.add_route('/route-difficulty/{route_difficulty_id}', route_difficulty_end_point())
app.add_route('/route-length', route_length_end_point())
app.add_route('/route-length/{route_length_id}', route_length_end_point())
app.add_route('/user-role-route', user_role_route_end_point())
app.add_route('/user-role-route/{user_role_route_id}', user_role_route_end_point())
app.add_route('/users', users_end_point())
app.add_route('/roles', roles_end_point())
app.add_route('/data-request', data_request_end_point())
app.add_route('/data-request/{data_request_id}', data_request_end_point())
app.add_route('/form',form_end_point())
app.add_route('/form/{form_id}',form_end_point())
app.add_route('/visitform', visit_form_end_point())
app.add_route('/visitform/{visit_form_id}', visit_form_end_point())
app.add_route('/obs-form-data-request',obs_form_data_request_end_point())
app.add_route('/obs-form-data-request/{obs_form_data_request_id}',obs_form_data_request_end_point())
app.add_route('/visit-form-data-request', visit_form_data_request_end_point())
app.add_route('/visit-form-data-request/{visit_form_data_request_id}', visit_form_data_request_end_point())
app.add_route('/obs-point-values',obs_point_values_end_point())
app.add_route('/obs-point-values/{obs_point_values_id}',obs_point_values_end_point())
app.add_route('/visit-values', visit_values_end_point())
app.add_route('/visit-values/{visit_values_id}', visit_values_end_point())
app.add_route('/obspnt-visit-form', obspnt_visit_form_end_point())
app.add_route('/obspnt-visit-form/{obspnt_visit_form_id}', obspnt_visit_form_end_point())
app.add_route('/image',image_end_point())
app.add_route('/image/{object_id}',image_end_point())
app.add_route('/deviceinfo', deviceinfo_end_point())
app.add_route('/deviceinfo/{deviceinfo_id}', deviceinfo_end_point())
app.add_route('/verification', verification_end_point())


app.add_route('/mobile-routes', mobile_route_end_point())
app.add_route('/mobile-routes/{route_id}', mobile_route_end_point())
app.add_route('/mobile-observation-point', mobile_observation_point_end_point())
app.add_route('/mobile-observation-point/{observation_point_id}', mobile_observation_point_end_point())




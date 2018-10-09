import os
import json
from peewee import *
from playhouse.postgres_ext import *
from environment import sciencecache_database
from collections import namedtuple
from psycopg2.extensions import *

'''
    custom field for columns of type geometry
    code modified from here: https://github.com/coleifer/peewee/issues/758
'''
class GeometryField(Field):
    db_field = 'geometry'
    def __init__(self, geom_type=None, geom_srid=None, **kwargs):
        self.geom_srid = geom_srid
        self.geom_type = geom_type

        super(GeometryField, self).__init__(**kwargs)
        if geom_type:
            if geom_srid:
                self.db_field = 'geometry(%s, %s)' % (geom_type, geom_srid)
            else:
                self.db_field = 'geometry(%s)' % (geom_type, )

class PointField(GeometryField):
    def __init__(self, geom_srid=4326, **kwargs):
        super(PointField, self).__init__(
            geom_type='Point',
            geom_srid=geom_srid,
            **kwargs)

    def db_value(self, value):
        print(value)
        if isinstance(value, list):
            return Point(value[0], value[1], self.geom_srid)
        else:
            return value
    
    def python_value(self, value):
        res = sciencecache_database.execute_sql('select st_x(%s), st_y(%s)', (value, value))
        return res.fetchone()

Point = namedtuple('Point', ['x', 'y', 'srid'])

def adapt_point(point):
    x = point.x
    y = point.y
    srid = point.srid
    return AsIs("st_setsrid(st_makepoint(%s, %s), %s)" % (x,y,srid))

register_adapter(Point, adapt_point)

class UnknownField(object):
    def __init__(self, *_, **__): pass

class BaseModel(Model):
    class Meta:
        database = sciencecache_database

class Datarequests(BaseModel):
    question = CharField(null=True)
    description = TextField(null=True)
    request_type = TextField(null=True)
    options = JSONField(null=True)
    request_help = TextField(null=True)
    placeholder = CharField(null=True)

    class Meta:
        table_name = 'datarequests'
        indexes = (
            (('id', 'id'), True),
        )
        schema = 'sc2'

class Deviceinfo(BaseModel):
    user_email = CharField(null=True)
    platform = CharField(null=True)
    uuid = CharField(null=True, unique=True)
    model = CharField(null=True)
    manufacturer = CharField(null=True)
    isvirtual = BooleanField(null=True)
    email_token = CharField(null=True)
    is_validated = BooleanField()

    class Meta:
        table_name = 'deviceinfo'
        indexes = (
            (('id', 'id'), True),
        )
        schema = 'sc2'

class Routedifficulty(BaseModel):
    difficulty = CharField()
    description = CharField()
    sort_order = IntegerField()

    class Meta:
        table_name = 'routedifficulty'
        indexes = (
            (('id', 'id'), True),
        )
        schema = 'sc2'

class Routelength(BaseModel):
    length = CharField(null=True)
    description = CharField()
    weight = IntegerField()

    class Meta:
        table_name = 'routelength'
        indexes = (
            (('id', 'id'), True),
        )
        schema = 'sc2'

class GatewayUrl(BaseModel):
    url = CharField(null=True)
    federal_approved = BooleanField(null=True)

    class Meta:
        table_name = 'gateway_url'
        schema = 'sc2'

class Routes(BaseModel):
    route = AutoField(column_name='route_id')
    route_version = FloatField()
    name = CharField()
    description = TextField(null=True)
    warning = TextField(null=True)
    gateway = ForeignKeyField(column_name='gateway_id', field='id', model=GatewayUrl, null=True)
    federal_staff_only = BooleanField(null=True)
    published = BooleanField()
    private = BooleanField()
    visible_yn = BooleanField()
    allow_unplanned_obs = BooleanField(null=True)
    waypoint_count = IntegerField(null=True)
    access_key = CharField(null=True)
    last_updated = DateTimeField()
    route_difficulty = ForeignKeyField(column_name='route_difficulty_id', field='id', model=Routedifficulty)
    route_length = ForeignKeyField(column_name='route_length_id', field='id', model=Routelength)

    class Meta:
        table_name = 'routes'
        indexes = (
            (('route', 'route'), True),
        )
        schema = 'sc2'

class Visits(BaseModel):
    route = ForeignKeyField(column_name='route_id', field='route', model=Routes)
    route_version = CharField(null=True)
    datetime_started = DateTimeField()
    date_uploaded = DateTimeField(null=True)

    class Meta:
        table_name = 'visits'
        indexes = (
            (('id'), True),
        )
        schema = 'sc2'

class Devicevisit(BaseModel):
    visit = ForeignKeyField(column_name='visit_id', field='id', model=Visits)
    device = ForeignKeyField(column_name='device_id', field='id', model=Deviceinfo)
    version = CharField(null=True)
    cordova = CharField(null=True)

    class Meta:
        table_name = 'devicevisit'
        schema = 'sc2'

class Images(BaseModel):
    image_description = CharField()
    image = CharField(column_name='image_id', null=True)

    class Meta:
        table_name = 'images'
        indexes = (
            (('id', 'id'), True),
        )
        schema = 'sc2'

class ObservationpointType(BaseModel):
    description = CharField(null=True)

    class Meta:
        table_name = 'observationpoint_type'
        schema = 'sc2'

class ObsPointForm(BaseModel):
    name = CharField()
    observation_point_type = ForeignKeyField(column_name='observation_point_type_id', field='id', model=ObservationpointType)
    owner = CharField(null=True)

    class Meta:
        table_name = 'obs_point_form'
        schema = 'sc2'

class ObservationPoints(BaseModel):
    route = ForeignKeyField(column_name='route_id', field='route', model=Routes)
    sort_order = IntegerField()
    name = CharField()
    observation_point_type = ForeignKeyField(column_name='observation_point_type_id', field='id', model=ObservationpointType)
    description = TextField(null=True)
    warning = TextField(null=True)
    obspoint_geom = PointField(null=True)  # USER-DEFINED
    field_created = BooleanField(null=True)
    include_in_route = BooleanField(null=True)
    parent = ForeignKeyField(column_name='parent_id', field='id', model='self', null=True)
    obspnt_form = ForeignKeyField(column_name='obspnt_form_id', field='id', model=ObsPointForm, null=True)
    image_request = BooleanField(null=True)
    photo_instructions = TextField(null=True)

    class Meta:
        table_name = 'observation_points'
        schema = 'sc2'

class ObspointFormDatarequests(BaseModel):
    obs_point_form = ForeignKeyField(column_name='obs_point_form_id', field='id', model=ObsPointForm)
    datarequest = ForeignKeyField(column_name='datarequest_id', field='id', model=Datarequests)

    class Meta:
        table_name = 'obspoint_form_datarequests'
        schema = 'sc2'

class ObsPntValues(BaseModel):
    observation_point = ForeignKeyField(column_name='observation_point_id', field='id', model=ObservationPoints)
    form_datarequests = ForeignKeyField(column_name='form_datarequests_id', field='id', model=ObspointFormDatarequests)
    value = TextField()
    date_captured = DateTimeField(null=True)

    class Meta:
        table_name = 'obs_pnt_values'
        schema = 'sc2'

class ObspntImages(BaseModel):
    image = ForeignKeyField(column_name='image_id', field='id', model=Images)
    observation_point = ForeignKeyField(column_name='observation_point_id', field='id', model=ObservationPoints)

    class Meta:
        table_name = 'obspnt_images'
        schema = 'sc2'

class VisitForm(BaseModel):
    name = CharField()
    observation_point_type = ForeignKeyField(column_name='observation_point_type_id', field='id', model=ObservationpointType)
    owner = CharField(null=True)

    class Meta:
        table_name = 'visit_form'
        schema = 'sc2'

class VisitFormDatarequests(BaseModel):
    visit_form = ForeignKeyField(column_name='visit_form_id', field='id', model=VisitForm)
    datarequest = ForeignKeyField(column_name='datarequest_id', field='id', model=Datarequests)

    class Meta:
        table_name = 'visit_form_datarequests'
        schema = 'sc2'

class ObspntVisitForm(BaseModel):
    observation_point = ForeignKeyField(column_name='observation_point_id', field='id', model=ObservationPoints)
    visit_form_datarequests = ForeignKeyField(column_name='visit_form_datarequests_id', field='id', model=VisitFormDatarequests)

    class Meta:
        table_name = 'obspnt_visit_form'
        schema = 'sc2'

class VisitValues(BaseModel):
    obspnt_visit_form = ForeignKeyField(column_name='obspnt_visit_form_id', field='id', model=ObspntVisitForm)
    visit = ForeignKeyField(column_name='visit_id', field='id', model=Visits)
    value = TextField()
    date_captured = DateTimeField(null=True)

    class Meta:
        table_name = 'visit_values'
        schema = 'sc2'

class ObspntvisitImages(BaseModel):
    image = ForeignKeyField(column_name='image_id', field='id', model=Images)
    visitvalue = ForeignKeyField(column_name='visitvalue_id', field='id', model=VisitValues)

    class Meta:
        table_name = 'obspntvisit_images'
        schema = 'sc2'

class Omb(BaseModel):
    omb_route = ForeignKeyField(column_name='omb_route_id', field='route', model=Routes)
    omb_number = CharField(null=True)
    policy = TextField()
    information = TextField()

    class Meta:
        table_name = 'omb'
        indexes = (
            (('id', 'id'), True),
        )
        schema = 'sc2'

class Role(BaseModel):
    description = CharField()

    class Meta:
        table_name = 'role'
        schema = 'sc2'

class RouteBoundingBox(BaseModel):
    route = ForeignKeyField(column_name='route_id', field='route', model=Routes)
    description = CharField(null=True)
    bb_min = UnknownField(null=True)  # USER-DEFINED
    bb_max = UnknownField(null=True)  # USER-DEFINED

    class Meta:
        table_name = 'route_bounding_box'
        schema = 'sc2'

class RouteImages(BaseModel):
    image = ForeignKeyField(column_name='image_id', field='id', model=Images)
    route = ForeignKeyField(column_name='route_id', field='route', model=Routes)

    class Meta:
        table_name = 'route_images'
        schema = 'sc2'

class Routeconfig(BaseModel):
    rc_route = ForeignKeyField(column_name='rc_route_id', field='route', model=Routes)
    camera_min_quality = IntegerField()
    camera_max_width = IntegerField()
    camera_max_height = IntegerField()

    class Meta:
        table_name = 'routeconfig'
        indexes = (
            (('id', 'id'), True),
        )
        schema = 'sc2'

class User(BaseModel):
    user_email = CharField(unique=True)
    first_name = CharField(null=True)
    last_name = CharField(null=True)
    is_admin = BooleanField(null=True)

    class Meta:
        table_name = 'user'
        schema = 'sc2'

class UserRoleRoute(BaseModel):
    user = ForeignKeyField(column_name='user_id', field='id', model=User)
    role = ForeignKeyField(column_name='role_id', field='id', model=Role)
    route = ForeignKeyField(column_name='route_id', field='route', model=Routes)

    class Meta:
        table_name = 'user_role_route'
        schema = 'sc2'

class Whitelist(BaseModel):
    tld = CharField(null=True)
    federal = BooleanField(null=True)

    class Meta:
        table_name = 'whitelist'
        schema = 'sc2'


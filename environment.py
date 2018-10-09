import json
from peewee import *
import sys
import os
from os.path import dirname,join

configuration = {}


# Ensure that Python knows where to find our custom modules
app_path = dirname(__file__)
config_path = join(app_path, 'config.json')

with open(config_path) as json_data:
    configuration = json.load(json_data)


sciencecache_database = PostgresqlDatabase(
    configuration['database']['name'],  # Required by Peewee.
    user=configuration['database']['user'],  # Will be passed directly to psycopg2.
    password=configuration['database']['cred'],  # Ditto.
    host=configuration['database']['host'],  # Ditto.
    port=configuration['database']['port']
)

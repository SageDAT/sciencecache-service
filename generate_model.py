from os.path import join, dirname
########
##  REQUIRES PYTHON 2.7 ####
#######

from peewee import PostgresqlDatabase,ProgrammingError
import os
import sys
import pexpect



DB_NAME ='sciencecache' # Required by Peewee.
DB_USER='sciencecache'  # Will be passed directly to psycopg2.
DB_PASS="J8kSGXmhJIpAKquv"
DB_HOST="igsisdbpgfdev1.cjkzjn3eobi3.us-west-2.rds.amazonaws.com"
DB_PORT="5432"
DB_SCHEMA='sc2'



sciencecache_database = PostgresqlDatabase(
    DB_NAME,  # Required by Peewee.
    user=DB_USER,  # Will be passed directly to psycopg2.
    password=DB_PASS,  # Ditto.
    host=DB_HOST,  # Ditto.
    port=DB_PORT,
    field_types={'geometry': 'geometry'}
)




try:
    model_name ='gen_model.py'
    command_string = 'python -m pwiz -e postgresql' +' --host='+ DB_HOST +' --port='+ DB_PORT +' --user='+ DB_USER +' --schema='+ DB_SCHEMA +' --preserve-order --password sciencecache > '+ model_name

    child = pexpect.spawn('/bin/bash', ['-c',command_string])
    child.logfile = sys.stdout
    child.expect('Password:')
    child.sendline(DB_PASS)
    child.interact()

    command_string = "sed -i '' s/PostgresqlDatabase.*/sciencecache_database/g " + model_name +" "+ model_name
    child = pexpect.spawn(command_string)
    child.interact()

    command_string = "sed -i '' s/rel_model/model/g " + model_name +" "+ model_name
    child = pexpect.spawn(command_string)
    child.interact()


except Exception as e:
    print(e)
    print "destroying " + model_name + "for security"
    command_string = 'rm ' + model_name
    child = pexpect.spawn(command_string)
    child.interact()
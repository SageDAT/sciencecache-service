import os
from os.path import join, dirname
import datetime
# from dotenv import load_dotenv
# from error_handler import DotEnvError
from playhouse.migrate import *
from peewee import PostgresqlDatabase,ProgrammingError
import migrations
from environment import sciencecache_database
import sys


class UTCMinus0600(datetime.tzinfo):
    """tzinfo derived concrete class named "+0530" with offset of 19800"""
    # can be configured here
    _offset = datetime.timedelta(seconds = -21600)
    _dst = datetime.timedelta(0)
    _name = "+0000"
    def utcoffset(self, dt):
        return self.__class__._offset
    def dst(self, dt):
        return self.__class__._dst
    def tzname(self, dt):
        return self.__class__._name

# Load dotenv for this machine (from ./service/.env)
# `cp .env.dist .env` to initialize and change settings in .env file
# app_path = dirname(__file__)
# dotenv_path = join(app_path, '.env')
# load_dotenv(dotenv_path)


# ENVIRONMENT = os.environ.get("ENVIRONMENT")
# if ENVIRONMENT is None: raise DotEnvError('ENVIRONMENT')
# DB_HOST = os.environ.get("DB_HOST")
# if DB_HOST is None: raise DotEnvError('DB_HOST')
# DB_NAME = os.environ.get("DB_NAME")
# if DB_NAME is None: raise DotEnvError('DB_NAME')
# DB_PORT = os.environ.get("DB_PORT")
# if DB_PORT is None: raise DotEnvError('DB_PORT')
# DB_USER = os.environ.get("DB_USER")
# if DB_USER is None: raise DotEnvError('DB_USER')
# DB_PASS = os.environ.get("DB_PASS")
# if DB_PASS is None: raise DotEnvError('DB_PASS')
# DB_SCHEMA = os.environ.get("DB_SCHEMA")
# if DB_SCHEMA is None: raise DotEnvError('DB_SCHEMA')


database = sciencecache_database
#setting the schema in PostgresqlDatabase() does not work and must be done here
database.execute_sql("set search_path to 'sc2';")
migrator = PostgresqlMigrator(database)



#Simple rollback argument "python migrate.py rollback" to rollback changes. "python migrate.py" to migrate steps
rollback = False
try:
    if(sys.argv[1]):
        rollback = True
except IndexError:
    pass

# tz = UTCMinus0600()
# db_version=999
# for line in database.execute_sql("SELECT version_number FROM nabat.db_version LIMIT 1;"):
#     db_version = float(line[0])
# db_version += 0.01
# database.execute_sql("UPDATE nabat.db_version SET version_number = " + str(db_version) + ", change_date = '" + str(datetime.datetime.now(tz)) + "';")


def rollback_step(rollback_object,name):
    print ("\n rolling back " + name)
    with database.transaction():
        try:
            rollback_object.rollback(migrator,database)
        except ProgrammingError as e:
            print ("nothing to rollback")
            print(e)
        except Exception as e:
            print("an error occurred... this change could not be rolled back")
            print(e)



def migrate_step(migration_object,name):
    print ("\n migrating " + name)
    with database.transaction():
        try:
            migration_object.migrate(migrator,database)

        except ProgrammingError as e:
            print ("This change was already migrated")
            print(e)
        except Exception as e:
            print(e)
            print("an error has occurred...")


### Import migration file
from migrations.m001_main_database import m001_main_database
from migrations.m002_study_table import m002_study_table




try:
    print ("starting migrations... ")

    if rollback:
        print("rolling back!")


        # m001 creates the database (copy and paste from a ddl file)
        # rollback_step(m001_main_database(), "m001_main_database")
        rollback_step(m002_study_table(), "m002_study_table")



        print("rollback ended.")



    else:
        print("migrating!")
        # migrate_step(m001_main_database(), "m001_main_database")
        migrate_step(m002_study_table(), "m002_study_table")



        print("migration ended.")




except Exception as e:
    print ("migration failed")
    print(e)
    exit(1)
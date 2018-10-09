# sciencecache-service 2.0 - python based RESTful microservice

## Description

The sciencecache-service is a RESTful web api that provides CRUD interaction with the sciencecache database.  It is used by the sciencecache mobile application to GET published routes (and their associated data) out of the database, and to POST visit information and unplanned observation points (and their associated data) into the database.  It is used by the scEdit web application to provide a secured method to GET, POST, PUT, and DELETE route, feature, and observation point information.

## Technical Information

Python version: 3.6+

### pip installed packages:

requirments.txt
### Other requirements:

 
## Installation

It's recommended that you create a virtual environment for the software to execute against:

1. Clone the repo
2. Install VirtualEnv: `pip install virtualenv`
3. Switch to the root directory of the cloned repo and create a new virtual environment: `virtualenv service`
4. Activate the new virtual environment: `source service/bin/activate`
5. Install the requirements `pip install -r requirements.txt`  
6. Edit the config.json file and change the database host and port to reflect where you would like to connect


###Building Dev database with Docker
* Install docker https://www.docker.com/get-docker
* docker-compose build (build the db locally)
* docker-compose up (run the db locally)
* docker-compose down

###Starting the service
1. Switch to the repo directory
2. Activate the virtual environment (assuming you named it 'service' as we did in step 6 of the installation instructions): `source service/bin/activate`
3. ~~start the gunicorn server: `gunicorn sciencecache-service:app --reload`~~ mod_wsgi-express start-server sciencecache-service.py

###Rebuilding the ORM
1. Use a virtualenv for python 2.7 (Is this still required?)
`virtualenv --python=/usr/bin/python service27` where --python is python 2.7 path
2. Use the virtualenv named service27 `source service27/bin/activate`
3. Install the requirements `pip install -r requirements.txt`
4. Install `pip install pexpect`
5. Run generate_model.py and copy gen_model.py contents into sciencecache_model.py (but dont copy over the import statements)
`python generate_model.py`
6. Preserve geometry on the ObservationPoint ORM, overwrite `obspoint_geom = UnknownField(null=True)` 
with `obspoint_geom = PointField(null=True)  # USER-DEFINED` in sciencecache_model.py

###Testing
Tests run from the Makefile using:
`make tests`

###Migration
migrate.py is used to build or rollback the database. Use `python migrate.py` on dev, beta, or 
prod (run from build script in Jenkins). Run the relevant migrate script 001-00X depending on environment.# sciencecache-service

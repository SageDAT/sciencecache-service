-- sciencecache_ddl.sql
--
--	PURPOSE:  Create database for ScienceCache - based on original migration from Counch
--
--	NOTES:
--		1) inital database was in couche -moved to postgres.  Start with slight refactor of db
--		2) Needed: whitelisted emails per route, is_validated on device; user table, roles on routes, owners on routes
--			
--		 
--
--	AUTHOR(S):
--		Sanjay Advani, USGS (SA)
--
--	HISTORY:
--==========================================================================
--	2017-10-29.  Created from already created postgres tables.  SA
--				 removed some of the lines that set to the default, and added explicit relationships
--				 "answers" table removed, images set to many-many with routes, wypnts and datarequests
--	2018-01-29:  Removed ref's to feature - moved all feature concepts to observation point (closer to v1.0 structure)
--==========================================================================
-- Schema: sc2 - set to "sc2" as v1.0 now resides on production under the "sc2" sc2 schema

DROP SCHEMA IF EXISTS sc2 cascade;

CREATE SCHEMA if not exists sc2;

set search_path = public, sc2;


  -- =========================================
-- Table: routedifficulty
-- DROP TABLE routedifficulty;

CREATE TABLE sc2.routedifficulty
(
  id serial NOT NULL,
  difficulty character varying(255) NOT NULL,
  description character varying(255) NOT NULL,
  sort_order integer NOT NULL,
  CONSTRAINT routedifficulty_pkey PRIMARY KEY (id)
)
;
ALTER TABLE sc2.routedifficulty
  OWNER TO sciencecache;
  
-- =========================================
-- Table: routelength
-- DROP TABLE routelength;

CREATE TABLE sc2.routelength
(
  id serial NOT NULL,
  length character varying(255),
  description character varying(255) NOT NULL,
  weight integer NOT NULL,
  CONSTRAINT routelength_pkey PRIMARY KEY (id)
)
;
ALTER TABLE sc2.routelength
  OWNER TO sciencecache;
  
  
-- =========================================
-- Table: gateway_url
-- DROP TABLE gateway_url;

CREATE TABLE sc2.gateway_url
(
  id serial NOT NULL primary key,
  url character varying(255),
  federal_approved boolean
)
;
ALTER TABLE sc2.gateway_url
  OWNER TO sciencecache;

-- =========================================
-- Table: whitelist
-- DROP TABLE whitelist;

CREATE TABLE sc2.whitelist
(
  id serial NOT NULL primary key,
  tld character varying(255),
  federal boolean
)
;
ALTER TABLE sc2.whitelist
  OWNER TO sciencecache;
-- =========================================
-- Table: routes
-- DROP TABLE routes;

CREATE TABLE sc2.routes
(
  route_id serial NOT NULL,
  route_version real NOT NULL,
  name character varying(255) NOT NULL,
  --contact character varying(255),
  description text,
  warning text,
  gateway_id integer,
  federal_staff_only boolean,
  --image text,
  published boolean NOT NULL,
  private boolean NOT NULL,
  visible_yn boolean NOT null default TRUE, --allow for soft delete or "hide" of route on SCEdit
  allow_unplanned_obs boolean default TRUE,
  waypoint_count integer,
  access_key character varying(255),
  last_updated timestamp without time zone NOT NULL,
  route_difficulty_id integer NOT NULL,
  route_length_id integer NOT NULL,
  --image_id character varying,
  CONSTRAINT routes_pkey PRIMARY KEY (route_id),
  CONSTRAINT routes_route_difficulty_id_fkey FOREIGN KEY (route_difficulty_id)
      REFERENCES sc2.routedifficulty (id),
  CONSTRAINT routes_route_length_id_fkey FOREIGN KEY (route_length_id)
      REFERENCES sc2.routelength (id),
  constraint routes_gateway_fkey foreign key (gateway_id) references sc2.gateway_url(id)
)
;
ALTER TABLE sc2.routes
  OWNER TO sciencecache;

-- Index: idx_routes_route_difficulty_id
-- DROP INDEX idx_routes_route_difficulty_id;
CREATE INDEX idx_routes_route_difficulty_id
  ON sc2.routes
  USING btree
  (route_difficulty_id);

-- Index: idx_routes_route_length_id
-- DROP INDEX idx_routes_route_length_id;
CREATE INDEX idx_routes_route_length_id
  ON sc2.routes
  USING btree
  (route_length_id);
  
  -- Index: idx_routes_route_length_id
-- DROP INDEX idx_routes_route_length_id;
CREATE INDEX idx_routes_gateway_id
  ON sc2.routes
  USING btree
  (gateway_id);

-- =========================================
-- Table: user (2018-02-05 added)
-- DROP TABLE sc2.user;

create table sc2.user
(
	id serial not null primary key,
	user_email character varying (255) not null unique,
	first_name character varying (50),
	last_name character varying (100),
	is_admin boolean default false
)
;

-- =========================================
-- Table: role (2018-02-05 added)
-- DROP TABLE sc2.role;

create table sc2.role
(
	id serial not null primary key,
	description character varying (255)  not null
)
;

-- =========================================
-- Table: user_role_route (2018-02-05 added)
-- DROP TABLE sc2.user_role_route;

create table sc2.user_role_route
(
	id serial not null primary key,
	user_id integer not null,
	role_id integer not null,
	route_id integer not null,
	constraint urr_user_fkey foreign key (user_id) references sc2.user(id),
	constraint urr_role_fkey foreign key (role_id) references sc2.role(id),
	constraint urr_route_fkey foreign key (route_id) references sc2.routes(route_id)
)
;

  -- Index: idx_urr_user
-- DROP INDEX idx_urr_user;
CREATE INDEX idx_urr_user
  ON sc2.user_role_route
  USING btree
  (user_id);
  -- Index: idx_urr_role
-- DROP INDEX idx_urr_role;
CREATE INDEX idx_urr_role
  ON sc2.user_role_route
  USING btree
  (role_id);
  -- Index: idx_urr_route
-- DROP INDEX idx_urr_route;
CREATE INDEX idx_urr_route
  ON sc2.user_role_route
  USING btree
  (route_id);


-- =========================================
-- Table: observationpoint_type (was feature type - removed ref's to feature)
-- DROP TABLE sc2.observationpoint_type;

create table sc2.observationpoint_type
(
	id serial not null primary key,
	description character varying(255)
)
;

ALTER TABLE sc2.observationpoint_type
  OWNER TO sciencecache;
  
-- =========================================
-- Table: obs_point_form
-- DROP TABLE obs_point_form;

create table sc2.obs_point_form
(
	id serial not null primary key,
	name character varying(255) not null,
	observation_point_type_id integer not null,
	owner character varying(255),
	constraint fk_ffrm_ft foreign key (observation_point_type_id) references sc2.observationpoint_type(id)
)
;

ALTER TABLE sc2.obs_point_form
  OWNER TO sciencecache;

-- Index: idx_obs_point_form_obs_type
-- DROP INDEX idx_obs_point_form_obs_type;
CREATE INDEX idx_obs_point_form_obs_type
  ON sc2.obs_point_form
  USING btree
  (observation_point_type_id);

  -- =========================================
-- Table: observation_points
-- DROP TABLE observation_points;

CREATE TABLE sc2.observation_points
(
  id serial NOT NULL,
  route_id integer NOT NULL,
  sort_order integer NOT NULL,
  name character varying(255) NOT NULL,
  observation_point_type_id integer NOT NULL,
  description text,
  warning text,
  obspoint_geom geometry (POINT, 4326),
  field_created boolean default false,
  include_in_route boolean,
  parent_id integer,
  obspnt_form_id integer,
  --latitude double precision,
  --longitude double precision,
  --image text,
  image_request boolean,
  photo_instructions text,
  --image_id character varying(255),
  CONSTRAINT obspnt_pkey PRIMARY KEY (id),
  CONSTRAINT obspnt_route_id_fkey FOREIGN KEY (route_id)
      REFERENCES sc2.routes (route_id),
  constraint fk_obp_obptyp foreign key(observation_point_type_id) references sc2.observationpoint_type(id),
  constraint fk_obp_parent foreign key(parent_id) references sc2.observation_points(id),
  constraint fk_obp_form foreign key(obspnt_form_id) references sc2.obs_point_form(id)
)
;
ALTER TABLE sc2.observation_points
  OWNER TO sciencecache;

-- Index: idx_obs_rte
-- DROP INDEX idx_obs_rte;
CREATE INDEX idx_obs_rte
  ON sc2.observation_points
  USING btree
  (route_id);
  
-- Index: idx_o_obptype
-- DROP INDEX idx_o_obptype;
CREATE INDEX idx_o_obptype
  ON sc2.observation_points
  USING btree
  (observation_point_type_id);
  
-- Index: idx_o_parent
-- DROP INDEX idx_o_parent;
CREATE INDEX idx_o_parent
  ON sc2.observation_points
  USING btree
  (parent_id);
  
-- Index: idx_o_obpform
-- DROP INDEX idx_o_obpform;
CREATE INDEX idx_o_obpform
  ON sc2.observation_points
  USING btree
  (obspnt_form_id);
-- =========================================  
-- Table: route_bounding_box
-- DROP TABLE route_bounding_box;

CREATE TABLE sc2.route_bounding_box
(
  id serial NOT NULL,
  route_id integer NOT NULL,
  description character varying(255),
  bb_min geometry (point, 4326),
  bb_max geometry (point, 4326),
  -- bb_minx double precision,
  -- bb_miny double precision,
  -- bb_maxx double precision,
  -- bb_maxy double precision,
  CONSTRAINT rte_bb_pkey PRIMARY KEY (id),
  CONSTRAINT rte_bb_route_id_fkey FOREIGN KEY (route_id)
      REFERENCES sc2.routes (route_id)
)
;
ALTER TABLE sc2.route_bounding_box
  OWNER TO sciencecache;

-- Index: idx_location_loc_route_id
-- DROP INDEX idx_location_loc_route_id;
CREATE INDEX idx_rbb_route_id
  ON sc2.route_bounding_box
  USING btree
  (route_id);
  
-- =========================================
-- Table: omb
-- DROP TABLE omb;

CREATE TABLE sc2.omb
(
  id serial NOT NULL,
  omb_route_id integer NOT NULL,
  omb_number character varying(255),
  policy text NOT NULL,
  information text NOT NULL,
  CONSTRAINT omb_pkey PRIMARY KEY (id),
  CONSTRAINT omb_omb_route_id_fkey FOREIGN KEY (omb_route_id)
      REFERENCES sc2.routes (route_id)
)
;
ALTER TABLE sc2.omb
  OWNER TO sciencecache;

-- Index: idx_omb_omb_route_id
-- DROP INDEX idx_omb_omb_route_id;
CREATE INDEX idx_omb_omb_route_id
  ON sc2.omb
  USING btree
  (omb_route_id);
  
-- =========================================
-- Table: routeconfig
-- DROP TABLE routeconfig;

CREATE TABLE sc2.routeconfig
(
  id serial NOT NULL,
  rc_route_id integer NOT NULL,
  camera_min_quality integer NOT NULL,
  camera_max_width integer NOT NULL,
  camera_max_height integer NOT NULL,
  CONSTRAINT routeconfig_pkey PRIMARY KEY (id),
  CONSTRAINT routeconfig_rc_route_id_fkey FOREIGN KEY (rc_route_id)
      REFERENCES sc2.routes (route_id)
)
;
ALTER TABLE sc2.routeconfig
  OWNER TO sciencecache;

-- Index: idx_routeconfig_rc_route_id
-- DROP INDEX idx_routeconfig_rc_route_id;
CREATE INDEX idx_routeconfig_rc_route_id
  ON sc2.routeconfig
  USING btree
  (rc_route_id);

-- =========================================
-- Table: datarequests
-- DROP TABLE datarequests;

  
CREATE TABLE sc2.datarequests
(
  id serial NOT NULL,
  question character varying(255),
  description text,
  request_type text,
  options json,
  request_help text,
  placeholder character varying(255),
  --image_id character varying(255),
  CONSTRAINT datarequests_pkey PRIMARY KEY (id)
)
;
ALTER TABLE sc2.datarequests
  OWNER TO sciencecache;

-- =========================================
-- Table: visit_form - should feature_form be parent to visit form?
-- DROP TABLE visit_form;

create table sc2.visit_form
(
	id serial not null primary key,
	name character varying(255) not null,
	observation_point_type_id integer not null,
	owner character varying(255),
	constraint fk_vfrm_ff foreign key (observation_point_type_id) references sc2.observationpoint_type(id)
)
;

ALTER TABLE sc2.visit_form
  OWNER TO sciencecache;
-- Index: visit_form_obs_type
-- DROP INDEX visit_form_obs_type;
CREATE INDEX visit_form_obs_type
  ON sc2.visit_form
  USING btree
  (observation_point_type_id);
  
-- =========================================
-- Table: obspoint_form_datarequests 
--		hint and clue from sciencecache 1.0 should be "feature data requests"
-- DROP TABLE obspoint_form_datarequests;

create table sc2.obspoint_form_datarequests
(
	id serial not null primary key,
	obs_point_form_id integer not null,
	datarequest_id integer not null,
	constraint fk_ffd_ff foreign key (obs_point_form_id) references sc2.obs_point_form(id),
	constraint fk_ffd_dr foreign key (datarequest_id) references sc2.datarequests(id)
)
;

ALTER TABLE sc2.obspoint_form_datarequests
  OWNER TO sciencecache;
  
-- Index: idx_ffd_ff
-- DROP INDEX idx_ffd_ff;
CREATE INDEX idx_ffd_ff
  ON sc2.obspoint_form_datarequests
  USING btree
  (obs_point_form_id);
  
-- Index: idx_ffd_dr
-- DROP INDEX idx_ffd_dr;
CREATE INDEX idx_ffd_dr
  ON sc2.obspoint_form_datarequests
  USING btree
  (datarequest_id);
  
-- =========================================
-- Table: feature
-- DROP TABLE feature;
/* -- REMOVED FEATURE LEVEL - MOVED ALL INFO TO OBSERVATION POINT
create table sc2.feature
(
	id serial not null primary key,
	name character varying(255) not null,
	feature_type_id integer not null,
    location_description text, --from waypoints - moved to here as location_description is a specific description
	observation_point_id integer not null,
	field_created boolean default false,
	include_in_route boolean,
	constraint fk_feat_obspnt foreign key(observation_point_id) references sc2.observation_points(id),
	constraint fk_feat_featyp foreign key(feature_type_id) references sc2.feature_type(id)
)
 ;
 
ALTER TABLE sc2.feature
  OWNER TO sciencecache;
  
-- Index: idx_f_obspnt
-- DROP INDEX idx_f_obspnt;
CREATE INDEX idx_f_obspnt
  ON sc2.feature
  USING btree
  (observation_point_id);  

-- Index: idx_f_feattype
-- DROP INDEX idx_f_feattype;
CREATE INDEX idx_f_feattype
  ON sc2.feature
  USING btree
  (feature_type_id);  
   */
-- =========================================
-- Table: obs_pnt_values
-- DROP TABLE obs_pnt_values;

create table sc2.obs_pnt_values
(
	id serial not null primary key,
	observation_point_id integer not null,
	form_datarequests_id integer not null,
	value text not null,
	date_captured timestamp with time zone,
	constraint fk_opv_obspnt foreign key(observation_point_id) references sc2.observation_points,
	constraint fk_opv_dr foreign key(form_datarequests_id) references sc2.obspoint_form_datarequests
)
;

ALTER TABLE sc2.obs_pnt_values
  OWNER TO sciencecache;
  
-- Index: idx_f_obspnt
-- DROP INDEX idx_f_obspnt;
CREATE INDEX idx_opv_feat
  ON sc2.obs_pnt_values
  USING btree
  (observation_point_id);  
  
-- Index: idx_f_obspnt
-- DROP INDEX idx_f_obspnt;
CREATE INDEX idx_opv_fdv
  ON sc2.obs_pnt_values
  USING btree
  (form_datarequests_id);  
-- =========================================  
-- Table: visits
-- DROP TABLE visits;

CREATE TABLE sc2.visits
(
  id serial NOT NULL,
  route_id integer NOT NULL,
  route_version character varying(255),
  datetime_started timestamp with time zone not null,
  date_uploaded timestamp with time zone,
  --obs_points_found character varying(255),
  CONSTRAINT visits_pkey PRIMARY KEY (id),
  constraint visit_route_fkey foreign key (route_id) references sc2.routes (route_id)
)
;
ALTER TABLE sc2.visits
  OWNER TO sciencecache;

--Index: idx_visits_rte
--DROP INDEX idx_visits_rte;
CREATE INDEX idx_visits_rte
  ON sc2.visits
  USING btree
  (route_id);
-- =========================================  
create table sc2.visit_form_datarequests
(
	id serial not null primary key,
	visit_form_id integer not null,
	datarequest_id integer not null,
	constraint fk_vfd_vf foreign key (visit_form_id) references sc2.visit_form(id),
	constraint fk_vfd_dr foreign key (datarequest_id) references sc2.datarequests(id)
)
;

ALTER TABLE sc2.visit_form_datarequests
  OWNER TO sciencecache;

-- Index: idx_vf_dr_vf
-- DROP INDEX idx_vf_dr_vf;
CREATE INDEX idx_vf_dr_vf
  ON sc2.visit_form_datarequests
  USING btree
  (visit_form_id);  
  
-- Index: idx_vf_dr_dr
-- DROP INDEX idx_vf_dr_dr;
CREATE INDEX idx_vf_dr_dr
  ON sc2.visit_form_datarequests
  USING btree
  (datarequest_id);

-- =========================================  
-- Table: deviceinfo
-- DROP TABLE deviceinfo;

CREATE TABLE sc2.deviceinfo
(
  id serial NOT NULL,
  user_email character varying(255),
  platform character varying(255),
  uuid character varying(255),
  model character varying(255),
  manufacturer character varying(255),
  isVirtual boolean,
  email_token character varying(255),
	is_validated boolean default false,
  CONSTRAINT deviceinfo_pkey PRIMARY KEY (id)
)
;
CREATE UNIQUE INDEX deviceinfo_uuid_key ON sc2.deviceinfo (uuid) ;
ALTER TABLE sc2.deviceinfo
  OWNER TO sciencecache;


-- Index: idx_deviceinfo_visit_id
-- DROP INDEX idx_deviceinfo_visit_id;
-- CREATE INDEX idx_deviceinfo_visit_id
  -- ON sc2.deviceinfo
  -- USING btree
  -- (visit_id);
  
-- =========================================  
-- Table: devicevisit
-- DROP TABLE devicevisit;

CREATE TABLE sc2.devicevisit
(
	id serial NOT NULL,
	visit_id integer not null,
	device_id integer not null,
	version character varying(255),
	cordova character varying(255),
	constraint devicevisit_pk PRIMARY KEY (id),
	constraint fk_dv_dev foreign key (device_id) references sc2.deviceinfo (id),
	constraint fk_dv_vis foreign key (visit_id) references sc2.visits(id)
)
;
ALTER TABLE sc2.deviceinfo
  OWNER TO sciencecache;
  
CREATE INDEX dv_visit_id
  ON sc2.devicevisit
  USING btree
  (visit_id);
  
CREATE INDEX dv_dev_id
  ON sc2.devicevisit
  USING btree
  (device_id);
-- =========================================  
-- Table: images
-- DROP TABLE images;

CREATE TABLE sc2.images
(
  id serial NOT NULL,
  -- visit_id integer NOT NULL,
  -- waypoint_id integer NOT NULL,
  image_description character varying(255) NOT NULL,
  image_id character varying(255),
  CONSTRAINT images_pkey PRIMARY KEY (id)
  -- CONSTRAINT images_visit_id_fkey FOREIGN KEY (visit_id)
      -- REFERENCES sc2.visits (visit_id)
)
;
ALTER TABLE sc2.images
  OWNER TO sciencecache;


-- =========================================
-- Table: obspnt_visit_form
-- DROP TABLE obspnt_visit_form;
create table sc2.obspnt_visit_form
(
	id serial not null primary key,
	observation_point_id integer not null,
	visit_form_datarequests_id integer not null,
	constraint fk_ovf_obspnt foreign key(observation_point_id) references sc2.observation_points (id),
	constraint fk_ovf_vfd foreign key(visit_form_datarequests_id) references sc2.visit_form_datarequests (id)
)
;

ALTER TABLE sc2.obspnt_visit_form
  OWNER TO sciencecache;
  
-- Index: idx_ovf_op
-- DROP INDEX idx_ovf_op;
CREATE INDEX idx_ovf_op
  ON sc2.obspnt_visit_form
  USING btree
  (observation_point_id);
  
-- Index: idx_ovf_vfdr
-- DROP INDEX idx_ovf_vfdr;
CREATE INDEX idx_ovf_vfdr
  ON sc2.obspnt_visit_form
  USING btree
  (visit_form_datarequests_id);  
 
-- =========================================
-- Table: visit_values
-- DROP TABLE visit_values;
create table sc2.visit_values
(
	id serial not null primary key,
	obspnt_visit_form_id integer not null,
	visit_id integer not null,
	value text not null,
	date_captured timestamp with time zone,
	constraint fk_vv_vist foreign key(visit_id) references sc2.visits (id),
	constraint fk_vv_frm foreign key(obspnt_visit_form_id) references sc2.obspnt_visit_form (id)
)
;

ALTER TABLE sc2.visit_values
  OWNER TO sciencecache;
  
-- Index: idx_vv_visit
-- DROP INDEX idx_vv_visit;
CREATE INDEX idx_vv_visit
  ON sc2.visit_values
  USING btree
  (visit_id);  
  
-- Index: idx_vv_ovfdr
-- DROP INDEX idx_vv_ovfdr;
CREATE INDEX idx_vv_ovfdr
  ON sc2.visit_values
  USING btree
  (obspnt_visit_form_id); 
 

-- =========================================
-- Table: visitdr_images
-- DROP TABLE visitdr_images

create table sc2.obspntvisit_images
(
	id serial primary key not null,
	image_id integer not null,
	visitvalue_id integer not null,
	constraint fk_vi_image foreign key (image_id) references sc2.images(id) on delete cascade,
	constraint fk_vi_visval foreign key (visitvalue_id) references sc2.visit_values (id) on delete cascade
)
;

create table sc2.route_images
(
	id serial primary key not null,
	image_id integer not null,
	route_id integer not null,
	constraint fk_ri_image foreign key (image_id) references sc2.images(id) on delete cascade,
	constraint fk_ri_rte	foreign key (route_id) references sc2.routes (route_id) on delete cascade
)
;

create table sc2.obspnt_images
(
	id serial primary key not null,
	image_id integer not null,
	observation_point_id integer not null,
	constraint fk_opi_image foreign key (image_id) references sc2.images(id) on delete cascade,
	constraint fk_opi_op	foreign key (observation_point_id) references sc2.observation_points(id) on delete cascade
)
;

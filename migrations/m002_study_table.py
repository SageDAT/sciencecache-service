from playhouse.migrate import *

class m002_study_table():

    def migrate(self, migrator,db):
        """Write your migrations here."""

        new_sql = """
            -- Table: study
            CREATE TABLE sc2.study
                (
                 id serial primary key not null,
                 name character varying(50) not null,
                 description character varying(255),
                 owner character varying (255)
                )
            ;
            ALTER TABLE sc2.study OWNER TO sciencecache;
            
            ALTER TABLE sc2.routes ADD study_id integer;
            ALTER TABLE sc2.routes ADD CONSTRAINT routes_study_fkey foreign key (study_id) references sc2.study(id);
        """

        db.execute_sql(new_sql)


    def rollback(self, migrator,db):
        """Write your rollback migrations here."""

        old_sql = """
        
            ALTER TABLE sc2.routes DROP IF EXISTS study_id;
            DROP TABLE IF EXISTS sc2.study;
        """

        db.execute_sql(old_sql)

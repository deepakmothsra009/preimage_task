import os
import psycopg2
from configurations import POSTGRES_HOST


def create_databse():
    connection = psycopg2.connect(
        user="postgres",
        password="postgres",
        host=POSTGRES_HOST,
        port="5432",
    )
    connection.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = connection.cursor()
    cursor.execute("SELECT datname FROM pg_database WHERE datname='preimage';")
    if not cursor.fetchone():
        query_command = """CREATE DATABASE preimage"""
        cursor.execute(query_command)
    cursor.close()
    connection.close()


def create_user_info_table(cursor):
    query_command = """CREATE TABLE IF NOT EXISTS user_info_table 
                    ( user_id SERIAL PRIMARY KEY, user_name TEXT )"""
    cursor.execute(query_command)


def create_project_info_table(cursor):
    query_command = """CREATE TABLE IF NOT EXISTS project_info_table 
                    ( project_id SERIAL PRIMARY KEY, user_id INTEGER REFERENCES user_info_table,
                     project_name TEXT )"""
    cursor.execute(query_command)


def create_project_version_table(cursor):
    query_command = """CREATE TABLE IF NOT EXISTS project_version_table 
                    ( project_version_id SERIAL PRIMARY KEY, project_id INTEGER REFERENCES project_info_table,
                     project_version_name TEXT,  project_version_number INTEGER, row_insert_time TIMESTAMP DEFAULT NOW(),
                     UNIQUE (project_id,project_version_id, project_version_name ))"""
    cursor.execute(query_command)


def create_project_version_result_table(cursor):
    query_command = """CREATE TABLE IF NOT EXISTS project_version_result_table 
                    ( version_result_id SERIAL PRIMARY KEY , project_version_id INTEGER REFERENCES
                     project_version_table , project_version_result_path TEXT )"""
    cursor.execute(query_command)


def get_latest_project_version(user, project_name):
    connection = psycopg2.connect(
        user="postgres",
        password="postgres",
        host=POSTGRES_HOST,
        port="5432",
        database="preimage",
    )
    connection.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = connection.cursor()
    query_command = """INSERT INTO user_info_table (user_name) SELECT '{}' WHERE NOT EXISTS 
                    (SELECT user_name FROM user_info_table WHERE user_name = '{}')""".format(
        user, user
    )
    cursor.execute(query_command)
    query_command = """SELECT EXISTS(SELECT project_name FROM project_info_table where 
                    project_name = '{}' )""".format(
        project_name
    )
    cursor.execute(query_command)
    query_return = cursor.fetchone()
    if query_return[0] == False:
        query_command = """INSERT INTO project_info_table ( project_name , user_id ) VALUES('{}' , 
                        (SELECT user_id FROM user_info_table WHERE user_name = '{}'))""".format(
            project_name, user
        )
        cursor.execute(query_command)
        project_version_number = 1
        project_version_name = "{}_version_{}".format(
            project_name, project_version_number
        )
        query_command = """INSERT INTO project_version_table(project_version_name , project_version_number , project_id )
                         VALUES('{}' , '{}' ,(SELECT project_id FROM project_info_table WHERE project_name = '{}')) 
                         RETURNING project_version_name""".format(
            project_version_name, project_version_number, project_name, user
        )
        cursor.execute(query_command)
        query_return = cursor.fetchone()
        project_version_name = query_return[0]
        cursor.close()
        connection.close()
        return project_version_name
    else:
        query_command = """SELECT project_version_name , project_version_number , project_id FROM project_version_table 
                        WHERE project_id = (SELECT project_id FROM project_info_table WHERE project_name = '{}') 
                        order by row_insert_time desc limit 1""".format(
            project_name
        )
        cursor.execute(query_command)
        query_return = cursor.fetchone()
        project_version_name, project_version_number, project_id = query_return
        latest_project_version_number = project_version_number + 1
        latest_project_version_name = "{}_version_{}".format(
            project_name, latest_project_version_number
        )
        query_command = """INSERT INTO project_version_table (project_id , project_version_name , project_version_number)
                         VALUES('{}' , '{}' , '{}')""".format(
            project_id, latest_project_version_name, latest_project_version_number
        )
        cursor.execute(query_command)
        cursor.close()
        connection.close()
        return latest_project_version_name


if __name__ == "__main__":

    create_databse()
    connection = psycopg2.connect(
        user="postgres",
        password="postgres",
        host=POSTGRES_HOST,
        port="5432",
        database="preimage",
    )
    connection.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = connection.cursor()

    create_user_info_table(cursor)
    create_project_info_table(cursor)
    create_project_version_table(cursor)
    create_project_version_result_table(cursor)
    cursor.close()
    connection.close()
    # user_name = sys.argv[1]
    # project_name = sys.argv[2]
    # project_version_name = get_latest_project_version(user_name , project_name, cursor)
    # print("project_version_name : ", project_version_name)

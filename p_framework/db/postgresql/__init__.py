import psycopg2
from p_framework.db import DatabaseWrapper
from p_framework.db.exceptions import ConnectionError, CreateError, DropError


class DB(DatabaseWrapper):

    def __init__(self, **conn_params):

        try:
            self.conn = psycopg2.connect(**conn_params)
        except Exception, e:
            raise ConnectionError(e)

    def cursor(self):
        return self.conn.cursor()

    def select(self, query):
        with self.cursor() as cur:
            cur.execute(query)
            return cur.fetchall()

    def create_database(self, database_name):
        try:
            self.conn.set_isolation_level(0)
            self.cursor().execute("""CREATE DATABASE %s""" % (database_name,))
        except Exception, e:
            raise CreateError(e)

    def drop_database(self, database_name):
        try:
            self.conn.set_isolation_level(0)
            self.cursor().execute("""DROP DATABASE %s""" % (database_name,))
        except Exception, e:
            raise DropError(e)

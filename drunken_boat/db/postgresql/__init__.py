import psycopg2
import os
from drunken_boat.db import DatabaseWrapper
from drunken_boat.db.exceptions import (ConnectionError, CreateError,
                                        DropError)


def field_is_nullable(field):
    """
    Parse a field dictionnary and check if a nullable value is
    acceptable by the database
    """
    return field["is_nullable"] != "NO" or field["column_default"] is not None


class DB(DatabaseWrapper):

    def __init__(self, **conn_params):

        try:
            self.conn = psycopg2.connect(**conn_params)
        except Exception as e:
            raise ConnectionError(e)

    def cursor(self):
        return self.conn.cursor()

    def select(self, query, params=None):
        with self.cursor() as cur:
            cur.execute(query, params)
            return cur.fetchall()

    def create_database(self, database_name):
        try:
            self.conn.set_isolation_level(0)
            self.cursor().execute("""CREATE DATABASE %s""" % (database_name,))
        except Exception as e:
            raise CreateError(e)

    def drop_database(self, database_name):
        try:
            self.conn.set_isolation_level(0)
            self.cursor().execute("""DROP DATABASE %s""" % (database_name,))
        except Exception as e:
            raise DropError(e)

    def create_table(self, table, **kwargs):

        if not kwargs:
            raise CreateError("you must specify columns")

        columns = ",".join(
            ["{} {}".format(k, v) for k, v in kwargs.items()])

        try:
            self.cursor().execute("CREATE TABLE %s (%s)" % (table, columns))
        except Exception as e:
            raise CreateError(e)

    def drop_table(self, table):
        try:
            self.cursor().execute("DROP TABLE %s" % (table,))
        except Exception as e:
            raise DropError(e)

    def get_primary_key(self, table):
        sql = os.path.join(os.path.dirname(__file__),
                           "sql",
                           "get_primary_key.sql")
        with open(sql) as sql:
            with self.cursor() as cursor:
                cursor.execute(sql.read(), (table, ))
                result = cursor.fetchone()
        return result[0]

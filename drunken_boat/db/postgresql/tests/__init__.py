from drunken_boat.db.postgresql import DB
from test_config import DATABASE


def drop_db():
    db = DB(database="template1")
    db.drop_database("dummy_db")


def create_db():
    db = DB(database="template1")
    db.create_database("dummy_db")


def get_test_db():
    return DB(**DATABASE)

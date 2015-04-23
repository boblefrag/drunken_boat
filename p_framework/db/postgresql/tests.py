import pytest
from p_framework.db.postgresql import DB
from p_framework.db.exceptions import ConnectionError, CreateError, DropError

from psycopg2._psycopg import cursor


def test_exeption():
    pytest.raises(ConnectionError, DB, database="test")


def drop_db():
    db = DB(database="template1")
    db.drop_database("dummy_db")


def create_db():
    db = DB(database="template1")
    db.create_database("dummy_db")


def test_select(request):
    drop_db()
    create_db()
    db = DB(database="dummy_db")
    rows = db.select("SELECT datname from pg_database")
    assert isinstance(rows, list)
    assert isinstance(rows[0], tuple)
    assert len(rows[0]) == 1


def test_cursor_exist():
    drop_db()
    create_db()
    db = DB(database="dummy_db")
    assert hasattr(db, "cursor")
    c = db.cursor()
    assert isinstance(c, cursor)


def test_drop_error():
    db = DB(database="dummy_db")
    pytest.raises(DropError,
                  db.drop_database,
                  "dummy_db")


def test_create_error():
    db = DB(database="dummy_db")
    pytest.raises(CreateError,
                  db.create_database,
                  "dummy_db")

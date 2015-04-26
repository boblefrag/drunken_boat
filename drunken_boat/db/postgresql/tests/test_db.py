import pytest
from drunken_boat.db.postgresql import DB
from drunken_boat.db.postgresql.tests import drop_db, create_db
from drunken_boat.db.exceptions import ConnectionError, CreateError, DropError

from psycopg2._psycopg import cursor


def test_exeption():
    pytest.raises(ConnectionError, DB, database="test")


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


def test_drop_database_error():
    db = DB(database="dummy_db")
    pytest.raises(DropError,
                  db.drop_database,
                  "dummy_db")


def test_create_database_error():
    db = DB(database="dummy_db")
    pytest.raises(CreateError,
                  db.create_database,
                  "dummy_db")


def test_create_table():
    drop_db()
    create_db()
    db = DB(database="dummy_db")
    assert db.create_table("dummy", id="serial PRIMARY KEY") is None


def test_drop_table():
    drop_db()
    create_db()
    db = DB(database="dummy_db")
    db.create_table("dummy", id="serial PRIMARY KEY")
    assert db.drop_table("dummy") is None


def test_create_table_raise_columns():
    """
    raise in creating the database because columns informations does not
    exists
    """
    drop_db()
    create_db()
    db = DB(database="dummy_db")
    pytest.raises(CreateError, db.create_table, "dummy")


def test_create_table_raise_already_exists():
    drop_db()
    create_db()
    db = DB(database="dummy_db")
    db.create_table("dummy", id="serial PRIMARY KEY")
    pytest.raises(CreateError,
                  db.create_table,
                  "dummy",
                  id="serial PRIMARY KEY")


def test_drop_table_raise():
    drop_db()
    create_db()
    db = DB(database="dummy_db")
    pytest.raises(DropError, db.drop_table, "dummy")

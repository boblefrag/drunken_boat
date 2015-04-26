import pytest
from drunken_boat.db.postgresql import DB
from drunken_boat.db.postgresql.tests import drop_db, create_db, get_test_db
from drunken_boat.db.exceptions import ConnectionError, CreateError, DropError

from psycopg2._psycopg import cursor


@pytest.fixture(scope="module")
def prepare_db():
    drop_db()
    create_db()


def test_exeption():
    pytest.raises(ConnectionError, DB, database="test")


def test_select(prepare_db):
    db = get_test_db()
    rows = db.select("SELECT datname from pg_database")
    assert isinstance(rows, list)
    assert isinstance(rows[0], tuple)
    assert len(rows[0]) == 1


def test_cursor_exist(prepare_db):
    db = get_test_db()
    assert hasattr(db, "cursor")
    c = db.cursor()
    assert isinstance(c, cursor)


def test_drop_database_error(prepare_db):
    db = get_test_db()
    pytest.raises(DropError,
                  db.drop_database,
                  "dummy_db")


def test_create_database_error(prepare_db):
    db = get_test_db()
    pytest.raises(CreateError,
                  db.create_database,
                  "dummy_db")


def test_create_table(prepare_db):
    db = get_test_db()
    assert db.create_table("dummy", id="serial PRIMARY KEY") is None


def test_drop_table(prepare_db):
    db = get_test_db()
    db.create_table("dummy", id="serial PRIMARY KEY")
    assert db.drop_table("dummy") is None


def test_create_table_raise_columns(prepare_db):
    """
    raise in creating the database because columns informations does not
    exists
    """
    db = get_test_db()
    pytest.raises(CreateError, db.create_table, "dummy")


def test_create_table_raise_already_exists(prepare_db):
    drop_db()
    create_db()
    db = get_test_db()
    db.create_table("dummy", id="serial PRIMARY KEY")
    pytest.raises(CreateError,
                  db.create_table,
                  "dummy",
                  id="serial PRIMARY KEY")


def test_drop_table_raise(prepare_db):
    drop_db()
    create_db()
    db = get_test_db()
    pytest.raises(DropError, db.drop_table, "dummy")

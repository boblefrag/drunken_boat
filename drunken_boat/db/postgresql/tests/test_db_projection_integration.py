import pytest
from drunken_boat.db.postgresql.tests import drop_db, create_db
from drunken_boat.db.postgresql.projections import Projection, DataBaseObject
from drunken_boat.db.postgresql.fields import CharField
from drunken_boat.db.postgresql import DB


class TestProjection(Projection):
    title = CharField(10)

    class Meta:
        table = "dummy"


class TestRaiseProjection(Projection):
    title = CharField(10)


class TestRaiseProjectionWithNoGetTable(Projection):
    title = CharField(10, table="dummy")


@pytest.fixture(scope="module")
def prepare_test():
    drop_db()
    create_db()
    db = DB(database="dummy_db")
    db.create_table("dummy",
                    id="serial PRIMARY KEY",
                    title="character varying (10)",
                    introduction="text")
    db.conn.commit()
    with db.cursor() as cur:
        cur.execute("INSERT INTO dummy (title, introduction) VALUES (%s, %s)",
                    ("hello", "This is an introduction"))
        cur.execute("INSERT INTO dummy (title, introduction) VALUES (%s, %s)",
                    ("goodbye", "This is an a leaving"))
        db.conn.commit()

    return db


def test_db(prepare_test):
    db = prepare_test
    assert db.select("SELECT id, title, introduction FROM dummy LIMIT 1") == [
        (1, 'hello', "This is an introduction")]


def test_projection_select(prepare_test):
    projection = TestProjection(DB(database="dummy_db"))
    results = projection.select()
    assert isinstance(results[0], DataBaseObject)
    assert results[0].title.value == "hello"
    assert results[0].title.__repr__() == "hello"
    assert results[1].title.__repr__() == "goodbye"
    assert isinstance(results[0].title, CharField)
    assert isinstance(results[1].title, CharField)


def test_projection_get_by_py(prepare_test):
    projection = TestProjection(DB(database="dummy_db"))
    assert isinstance(projection.get_by_pk(1), DataBaseObject)
    assert isinstance(projection.get_by_pk(2), DataBaseObject)


def test_raising_projection(prepare_test):
    pytest.raises(ValueError, TestRaiseProjection, DB(database="dummy_db"))
    projection = TestRaiseProjectionWithNoGetTable(DB(database="dummy_db"))
    pytest.raises(ValueError, projection.select)


def test_projection_query(prepare_test):
    projection = TestProjection(DB(database="dummy_db"))
    query = "select title from dummy"
    assert isinstance(projection.select(query=query)[0], DataBaseObject)


def test_projection_results_empty(prepare_test):
    projection = TestProjection(DB(database="dummy_db"))
    query = "select title from dummy where introduction = %s"
    params = ["nothing"]
    assert len(projection.select(query=query, params=params)) == 0

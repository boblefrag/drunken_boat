from psycopg2 import DataError
import pytest
import datetime
from drunken_boat.db.exceptions import NotFoundError
from drunken_boat.db.postgresql.tests import drop_db, create_db, get_test_db
from drunken_boat.db.postgresql.projections import Projection, DataBaseObject
from drunken_boat.db.postgresql.fields import CharField, Timestamp
from drunken_boat.db.postgresql import DB


class DataBaseObjectWithMeth(DataBaseObject):

    def age_seconds(self):
        return self.age.total_seconds()


class TestProjection(Projection):
    title = CharField()

    class Meta:
        table = "dummy"


class TestRaiseProjection(Projection):
    title = CharField()


class TestProjectionWithVirtual(Projection):
    title = CharField()
    age = Timestamp(db_name="age(birthdate)", virtual=True)

    class Meta:
        table = "dummy"
        database_object = DataBaseObjectWithMeth


class TestRaiseProjectionWithNoGetTable(Projection):
    title = CharField(table="dummy")


@pytest.fixture(scope="module")
def prepare_test():
    drop_db()
    create_db()
    db = get_test_db()
    db.create_table("dummy",
                    id="serial PRIMARY KEY",
                    title="character varying (10) NOT NULL",
                    introduction="text NOT NULL",
                    birthdate="timestamp")
    db.conn.commit()
    with db.cursor() as cur:
        cur.execute("""INSERT INTO dummy (title,
                                          introduction,
                                          birthdate) VALUES (%s, %s, %s)""",
                    ("hello",
                     "This is an introduction",
                     datetime.datetime(2000, 3, 14)))
        cur.execute("""INSERT INTO dummy (title,
                                        introduction,
                                        birthdate) VALUES (%s, %s, %s)""",
                    ("goodbye",
                     "This is an a leaving",
                     datetime.datetime(2010, 5, 25)))
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
    assert results[0].title == "hello"
    assert results[1].title == "goodbye"


def test_projection_get_by_py(prepare_test):
    projection = TestProjection(DB(database="dummy_db"))
    assert isinstance(projection.get_by_pk(1), DataBaseObject)
    assert isinstance(projection.get_by_pk(2), DataBaseObject)


def test_raising_projection(prepare_test):
    pytest.raises(ValueError, TestRaiseProjection, get_test_db())
    projection = TestRaiseProjectionWithNoGetTable(get_test_db())
    pytest.raises(ValueError, projection.select)


def test_projection_query(prepare_test):
    projection = TestProjection(get_test_db())
    query = "select title from dummy"
    assert isinstance(projection.select(query=query)[0], DataBaseObject)


def test_projection_results_empty(prepare_test):
    projection = TestProjection(get_test_db())
    query = "select title from dummy where introduction = %s"
    params = ["nothing"]
    assert len(projection.select(query=query, params=params)) == 0


def test_projection_get_by_py_raise(prepare_test):
    projection = TestProjection(get_test_db())
    pytest.raises(NotFoundError, projection.get_by_pk, 3)


def test_projection_with_vitual(prepare_test):
    projection = TestProjectionWithVirtual(get_test_db())
    results = projection.select()
    assert isinstance(results[0].age, datetime.timedelta)


def test_projection_method(prepare_test):
    projection = TestProjectionWithVirtual(get_test_db())
    results = projection.select()
    assert isinstance(results[0].age_seconds(), float)


def test_projection_inserting(prepare_test):
    projection = TestProjectionWithVirtual(get_test_db())
    pytest.raises(ValueError, projection.insert, {})
    pytest.raises(ValueError, projection.insert, {"title": "hello"})

    pytest.raises(DataError, projection.insert,
                  {"title": "hello",
                   "introduction": "a meaningfull introduction",
                   "birthdate": "a string"})

    assert projection.insert(
        {"title": "hello",
         "introduction": "a meaningfull introduction"}
    ) is None
    assert isinstance(projection.insert(
        {"title": "hello",
         "introduction": "a meaningfull introduction"},
        returning="id"
    ), tuple)
    doc = projection.insert(
        {"title": "hello",
         "introduction": "a meaningfull introduction"},
        returning="id"
    )
    assert isinstance(doc[0], int)
    doc = projection.insert(
        {"title": "hello",
         "introduction": "a meaningfull introduction"},
        returning="self"
    )
    assert isinstance(doc, DataBaseObjectWithMeth)

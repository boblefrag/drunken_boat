from psycopg2 import DataError
import pytest
import datetime
from drunken_boat.db.exceptions import NotFoundError
from drunken_boat.db.postgresql.tests import drop_db, create_db, get_test_db
from drunken_boat.db.postgresql.tests import projections_fixtures
from drunken_boat.db.postgresql.projections import DataBaseObject
from drunken_boat.db.postgresql.query import Query
from drunken_boat.db.postgresql import DB


@pytest.fixture(scope="module")
def prepare_test():
    drop_db()
    create_db()
    db = get_test_db()
    db.create_table("author",
                    id="serial PRIMARY KEY",
                    name="varchar(10) NOT NULL")
    db.conn.commit()
    db.create_table("book",
                    id="serial PRIMARY KEY",
                    name="varchar(10) NOT NULL",
                    author_id="integer NOT NULL")
    db.conn.commit()
    with db.cursor() as cur:
        cur.execute(
            "alter table book add foreign key(author_id) references author"
        )
    db.conn.commit()
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
    projection = projections_fixtures.TestProjection(DB(database="dummy_db"))
    results = projection.select()
    assert isinstance(results[0], DataBaseObject)
    assert results[0].title == "hello"
    assert results[1].title == "goodbye"
    results = projection.select(lazy=True)
    assert isinstance(results, Query)


def test_projection_get_by_py(prepare_test):
    projection = projections_fixtures.TestProjection(DB(database="dummy_db"))
    assert isinstance(projection.get_by_pk(1), DataBaseObject)
    assert isinstance(projection.get_by_pk(2), DataBaseObject)


def test_raising_projection(prepare_test):
    pytest.raises(ValueError,
                  projections_fixtures.TestRaiseProjection, get_test_db())
    projection = projections_fixtures.TestRaiseProjectionWithNoGetTable(
        get_test_db())
    pytest.raises(ValueError, projection.select)


def test_projection_query(prepare_test):
    projection = projections_fixtures.TestProjection(get_test_db())
    query = "select title from dummy"
    assert isinstance(projection.select(query=query)[0], DataBaseObject)


def test_projection_results_empty(prepare_test):
    projection = projections_fixtures.TestProjection(get_test_db())
    query = "select title from dummy where introduction = %s"
    params = ["nothing"]
    assert len(projection.select(query=query, params=params)) == 0


def test_projection_get_by_py_raise(prepare_test):
    projection = projections_fixtures.TestProjection(get_test_db())
    pytest.raises(NotFoundError, projection.get_by_pk, 3)


def test_projection_with_vitual(prepare_test):
    projection = projections_fixtures.TestProjectionWithVirtual(get_test_db())
    results = projection.select()
    assert isinstance(results[0].age, datetime.timedelta)


def test_projection_method(prepare_test):
    projection = projections_fixtures.TestProjectionWithVirtual(get_test_db())
    results = projection.select()
    assert isinstance(results[0].age_seconds(), float)


def test_projection_inserting(prepare_test):
    projection = projections_fixtures.TestProjectionWithVirtual(get_test_db())
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
    assert isinstance(doc, projections_fixtures.DataBaseObjectWithMeth)


def test_pojection_foreign(prepare_test):
    projection_author = projections_fixtures.AuthorProjection(get_test_db())
    projection_author.insert(
        {"name": "author"})
    projection = projections_fixtures.BookProjection(get_test_db())
    projection.insert({"name": "book", "author_id": 1})
    assert isinstance(projection.select(), list)
    assert isinstance(projection.select()[0], DataBaseObject)
    assert isinstance(projection.select()[0].author, DataBaseObject)


def test_projection_reverse(prepare_test):
    projection_author = projections_fixtures.AuthorProjectionReverse(
        get_test_db())
    assert isinstance(projection_author.select()[0].books, list)
    author = projection_author.select()[0]
    book = projection_author.select()[0].books[0]
    assert author.id == book.author_id


def test_projection_reverse_with_params(prepare_test):
    projection_author = projections_fixtures.AuthorProjectionReverse(
        get_test_db())
    projection_book = projections_fixtures.BookProjection(get_test_db())
    projection_book.insert({"name": "a name", "author_id": 1})
    projection_book.insert({"name": "a title", "author_id": 1})
    books = projection_author.select()[0].books
    assert len(books) == 3
    books = projection_author.select(
        related={"books": {"where": "name=%s",
                           "params": ("a name",)}})[0].books
    assert len(books) == 1
    books = projection_author.select(
        related={"books": {"where": "name=%s OR name=%s",
                           "params": ("a name", "a title")}})[0].books
    assert len(books) == 2

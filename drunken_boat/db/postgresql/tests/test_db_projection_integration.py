from psycopg2 import DataError, ProgrammingError
import pytest
import datetime
from drunken_boat.db.exceptions import NotFoundError
from drunken_boat.db.postgresql.tests import drop_db, create_db, get_test_db
from drunken_boat.db.postgresql.tests import projections_fixtures
from drunken_boat.db.postgresql.projections import DataBaseObject
from drunken_boat.db.postgresql.query import Query, Where
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
    where = Where("title", "=", "%s")
    results = projection.select(where=where, params=("hello",))
    assert results[0].title == "hello"


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


def test_projection_query_where(prepare_test):
    projection = projections_fixtures.TestProjection(get_test_db())
    where = Where("title", "=", "%s")
    projection = projection.select(where=where, params=("hello",))
    assert projection[0].title == "hello"


def test_projection_query_where_or(prepare_test):
    projection = projections_fixtures.TestProjection(get_test_db())
    where = Where("title", "=", "%s") | Where("id", "=", "%s")
    results = projection.select(where=where, params=("hello", 2))
    assert results[0].title == "hello"
    assert results[1].title == "goodbye"
    results = projection.select(where=where, params=("hello", 1))
    assert len(results) == 1


def test_projection_query_where_and(prepare_test):
    projection = projections_fixtures.TestProjection(get_test_db())
    where = Where("title", "=", "%s") & Where("id", "=", "%s")
    results = projection.select(where=where, params=("hello", 2))
    assert len(results) == 0
    results = projection.select(where=where, params=("hello", 1))
    assert len(results) == 1


def test_projection_query_where_nor(prepare_test):
    projection = projections_fixtures.TestProjection(get_test_db())
    where = Where("title", "=", "%s") & ~(
        Where("id", "=", "%s") | Where("title", "=", "%s"))
    results = projection.select(where=where, params=("hello", 1, "goodbye"))
    assert len(results) == 0
    results = projection.select(where=where, params=("goodbye", 1, "hello"))
    assert len(results) == 1


def test_projection_query_where_nand(prepare_test):
    projection = projections_fixtures.TestProjection(get_test_db())
    where = Where("title", "=", "%s") & ~(
        Where("id", "=", "%s") & Where("title", "=", "%s"))
    results = projection.select(where=where, params=("goodbye", 2, "goodbye"))
    assert len(results) == 0
    results = projection.select(where=where, params=("hello", 2, "goodbye"))
    assert len(results) == 1


def test_projection_query_where_raise(prepare_test):
    where = Where("title", "=", "%s")
    pytest.raises(TypeError, where.__and__, "a string")
    pytest.raises(TypeError, where.__or__, "a string")


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


def test_projection_update(prepare_test):
    projection = projections_fixtures.TestProjectionWithVirtual(get_test_db())
    pytest.raises(ProgrammingError, projection.update,
                  Where("id", "=", "%s"),
                  {"godawa": "Kaboom"},
                  (4,))
    p = projection.update(Where("id", "=", "%s"), {"title": "Kaboom"}, (4,))
    assert p == []
    p = projection.update(Where("id", "=", "%s"),
                          {"title": "hello"}, (4,), returning="id")
    assert p == [(4,)]


def test_projection_delete(prepare_test):
    projection = projections_fixtures.TestProjectionWithVirtual(get_test_db())
    projection.insert(
        {"title": "dummy",
         "introduction": "a meaningfull introduction"})
    assert projection.delete("title=%s", ("dummy",)) == []
    projection.insert(
        {"title": "dummy",
         "introduction": "a meaningfull introduction"})
    assert projection.delete(Where("title", "=", "%s"), ("dummy",)) == []
    pytest.raises(ProgrammingError,
                  projection.delete,
                  Where("name", "=", "%s"), ("Pouet",))
    projection.insert(
        {"title": "dummy",
         "introduction": "a meaningfull introduction"})
    p = projection.delete(Where("title", "=", "%s"),
                          ("dummy",),
                          returning="self")
    assert isinstance(p[0], DataBaseObject)


def test_projection_foreign(prepare_test):
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


def test_projection_reverse_insert(prepare_test):
    projection_author = projections_fixtures.AuthorProjectionReverse(
        get_test_db())
    p = projection_author.insert({"name": "hello"}, returning="self")
    assert p.name == "hello"
    assert hasattr(p, "books")

    projection_author_empty = projections_fixtures.AuthorProjectionReverseEm(
        get_test_db())
    p = projection_author_empty.insert({"name": "hello"}, returning="self")
    assert isinstance(p, DataBaseObject)


def test_projection_reverse_update(prepare_test):
    projection_author = projections_fixtures.AuthorProjectionReverse(
        get_test_db())
    p = projection_author.update("name=%s", {"name": "champomy"}, ("hello",),
                                 returning="self")[0]
    assert p.name == "champomy"

    projection_author_empty = projections_fixtures.AuthorProjectionReverseEm(
        get_test_db())

    p = projection_author_empty.update(
        "name=%s", {"name": "hello"}, ("champomy",),
        returning="self")
    assert p[0].id


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


def test_projection_reverse_with_where_object(prepare_test):

    projection_author = projections_fixtures.AuthorProjectionReverse(
        get_test_db())
    books = projection_author.select(
        related={"books": {"where": Where("name", "=", "%s"),
                           "params": ("a name",)}})[0].books
    assert len(books) == 1

    authors = projection_author.select(
        where=Where("id", "=", "%s"),
        params=(24,),
        related={"books": {"where": Where("name", "=", "%s"),
                           "params": ("nothin",)}})
    assert len(authors) == 0

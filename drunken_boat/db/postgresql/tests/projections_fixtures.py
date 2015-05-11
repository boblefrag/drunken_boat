import datetime
from drunken_boat.db.postgresql.projections import Projection, DataBaseObject
from drunken_boat.db.postgresql.fields import (CharField, Timestamp,
                                               ForeignKey, ReverseForeign)
from drunken_boat.db.postgresql.tests import drop_db, create_db, get_test_db


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


class AuthorProjection(Projection):
    name = CharField()

    class Meta:
        table = "author"


class BookProjection(Projection):
    name = CharField()
    author = ForeignKey(
        join=["author_id", "id"],
        projection=AuthorProjection
    )

    class Meta:
        table = "book"


class BookProjectionReverse(Projection):

    class Meta:
        table = "book"


class AuthorProjectionReverse(Projection):
    name = CharField()
    books = ReverseForeign(
        join=["id", "author_id"],
        projection=BookProjectionReverse
    )

    class Meta:
        table = "author"


class AuthorProjectionReverseEm(Projection):

    books = ReverseForeign(
        join=["id", "author_id"],
        projection=BookProjection
    )

    class Meta:
        table = "author"


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

from drunken_boat.db.postgresql.projections import Projection, DataBaseObject
from drunken_boat.db.postgresql.fields import (CharField, Timestamp,
                                               ForeignKey, ReverseForeign)


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
    books = ReverseForeign(
        join=["id", "author_id"],
        projection=BookProjectionReverse
    )

    class Meta:
        table = "author"

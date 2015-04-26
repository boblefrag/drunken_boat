import pytest
from drunken_boat.db.postgresql.projections import Projection
from drunken_boat.db.postgresql.fields import CharField


class MockDB(object):
    pass


class MissingTableProjection(Projection):
    title = CharField(10)


class TestProjection(Projection):
    title = CharField(10)

    class Meta:
        table = "dummy_table"


def test_projection():
    proj = TestProjection(MockDB())
    assert isinstance(proj, TestProjection)
    assert proj.title.table == "dummy_table"
    assert proj.title.name == "title"


def test_table_missing():
    pytest.raises(ValueError, MissingTableProjection, MockDB())

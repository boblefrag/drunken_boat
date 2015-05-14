import pytest
from psycopg2 import ProgrammingError
from drunken_boat.db.postgresql.tests import get_test_db
from drunken_boat.db.postgresql.tests import projections_fixtures
from drunken_boat.db.postgresql.models import Model, ModelObject
from drunken_boat.db.postgresql.projections import DataBaseObject


@pytest.fixture(scope="module")
def prepare_test():
    projections_fixtures.prepare_test()


def test_model_init(prepare_test):
    db = get_test_db()
    model = Model(db,
                  projections={"default": projections_fixtures.TestProjection})
    assert isinstance(model, Model)
    assert isinstance(model.object(), ModelObject)
    obj = model.object()
    obj.title = "hello"
    obj.introduction = "i this me you're looking for ?"
    obj.save()
    assert hasattr(obj, "id")
    o = obj.save(returning="title")
    assert len(o) == 2
    assert o[0] == "hello"
    obj.title = "something"
    assert obj.update(returning="title")[0] == "something"
    assert isinstance(obj.save(returning="self"), DataBaseObject)


def test_raise_wrong_returning(prepare_test):
    db = get_test_db()
    model = Model(db,
                  projections={"default": projections_fixtures.TestProjection})
    obj = model.object()
    obj.title = "hello"
    obj.introduction = "i this me you're looking for ?"
    pytest.raises(ProgrammingError, obj.save, returning="something")
    obj = model.object()
    obj.title = "hello"
    obj.introduction = "i this me you're looking for ?"
    obj.save()
    obj.title = "something"
    pytest.raises(ProgrammingError, obj.update, returning="something")


def test_delete(prepare_test):
    db = get_test_db()
    model = Model(db,
                  projections={"default": projections_fixtures.TestProjection})
    obj = model.object()
    obj.title = "hello"
    obj.introduction = "i this me you're looking for ?"
    obj.save()
    assert obj.delete() == []
    obj = model.object()
    obj.title = "hello"
    obj.introduction = "i this me you're looking for ?"
    obj.save()
    assert obj.delete(returning="title") == [("hello",)]


def test_projection_default(prepare_test):
    db = get_test_db()
    model = Model(db,
                  projections={"primary": projections_fixtures.TestProjection})
    assert hasattr(model.projections, "default")
    assert hasattr(model.projections, "primary")

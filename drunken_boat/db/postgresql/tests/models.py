import pytest
from drunken_boat.db.postgresql.tests import get_test_db
from drunken_boat.db.postgresql.tests import projections_fixtures
from drunken_boat.db.postgresql.models import Model, ModelObject


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

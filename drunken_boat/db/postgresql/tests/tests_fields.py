from drunken_boat.db.postgresql.fields import CharField


def test_charfield():
    title = CharField(10, "title", "dummy_table")
    assert isinstance(title, CharField)
    assert hasattr(title, "limit")
    assert hasattr(title, "name")
    assert hasattr(title, "table")

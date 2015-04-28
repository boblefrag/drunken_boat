from drunken_boat.db.postgresql.fields import CharField


def test_charfield():
    title = CharField("title", "dummy_table")
    assert isinstance(title, CharField)
    assert hasattr(title, "db_name")
    assert hasattr(title, "table")

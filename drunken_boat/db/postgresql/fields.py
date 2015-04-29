class Field(object):
    virtual = False

    def __init__(self, db_name=None, table=None, *args, **kwargs):
        self.db_name = db_name
        self.table = table
        if kwargs.get("virtual"):
            self.virtual = kwargs["virtual"]

    def __call__(self, value, *args, **kwargs):
        return value


class CharField(Field):
    db_type = "varchar"


class Text(Field):
    db_type = "text"


class Integer(Field):
    db_type = "integer"


class Timestamp(Field):
    db_type = "timestamp"

class Field(object):
    virtual = False

    def __init__(self, db_name=None, table=None, *args, **kwargs):
        self.db_name = db_name
        self.table = table
        if kwargs.get("virtual"):
            self.virtual = kwargs["virtual"]

    def hydrate(self, result):
        hydrated = {self.name: result[0]}
        result = result[1:]
        return hydrated, result


class Related(Field):
    virtual = True

    def __init__(self, join, projection, *args, **kwargs):
        from drunken_boat.db.postgresql.projections import Projection
        if not issubclass(projection, Projection):
            raise ValueError(
                "{} Must be a drunken_boat.db.postgresql.projections.\
Projection instance".format(projection))
        self.join = join
        self.projection = projection
        super(Related, self).__init__(*args, **kwargs)

    def hydrate(self, result):
        hydrated, result = self.projection(None).hydrate(result)
        return {self.name: hydrated}, result


class ForeignKey(Related):
    pass


class CharField(Field):
    db_type = "varchar"


class Text(Field):
    db_type = "text"


class Integer(Field):
    db_type = "integer"


class Timestamp(Field):
    db_type = "timestamp"


class Boolean(Field):
    db_type = "boolean"

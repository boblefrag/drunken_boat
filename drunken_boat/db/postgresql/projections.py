from drunken_boat.db.postgresql.fields import Field
from drunken_boat.db.exceptions import NotFoundError


class DataBaseObject(object):

    def __init__(self, fields, *args, **kwargs):
        for field in fields:
            setattr(self, field.name, field(kwargs[field.name]))


class Projection(object):

    def __new__(cls, *args, **kwargs):
        cls.fields = []
        for name, attr in cls.__dict__.iteritems():
            if isinstance(attr, Field):
                if not getattr(attr, "name"):
                    attr.name = name
                cls.fields.append(attr)

        for field in cls.fields:
            if hasattr(cls, "Meta"):
                if not getattr(field, "table") and hasattr(cls.Meta, "table"):
                    field.table = cls.Meta.table

        return super(Projection, cls).__new__(cls)

    def __init__(self, DB):
        self.db = DB
        for field in self.fields:
            if not getattr(field, "table"):
                raise ValueError("{} is missing a table".format(field))

    def get_where(self, *args, **kwargs):
            pass

    def get_table(self, *args, **kwargs):
        if hasattr(self, "Meta"):
            if hasattr(self.Meta, "table"):
                return self.Meta.table
        raise ValueError("""You does not define {} Meta.table .Projections on
multitable must define a get_table method""".format(self))

    def get_joins(self, *args, **kwargs):
        pass

    def get_by_pk(self, pk, *args, **kwargs):
        pk_column = self.db.get_primary_key(self.Meta.table)
        where = "WHERE {} = %s".format(pk_column)
        kwargs["params"] = kwargs.get("params", [])
        kwargs["params"].append(pk)
        results = self.select(where=where, params=kwargs["params"])
        if len(results) == 0:
            raise NotFoundError("{} with value {} does not exists".format(
                pk_column, pk
            ))
        return results[0]

    def select(self, *args, **kwargs):
        results = []
        if kwargs.get("query"):
            # if a query is already given, just use this one
            query = kwargs["query"]
        else:
            where = kwargs.get("where")
            if not where:
                where = self.get_where(*args, **kwargs)
            table = self.get_table(*args, **kwargs)
            joins = self.get_joins(*args, **kwargs)
            fields = []
            for field in self.fields:
                fields.append((field.table, field.name))
            select_query = " ".join([
                '"{}"."{}"'.format(field[0], field[1]) for field in fields])
            query = "SELECT {} FROM {} {} {}".format(
                select_query,
                table,
                joins if joins else '',
                where if where else ''
            )
        db_results = self.db.select(query, kwargs.get("params"))
        for result in db_results:
            results.append(
                DataBaseObject(
                    self.fields,
                    **dict(zip(
                        [field.name for field in self.fields],
                        result)))
            )
        return results

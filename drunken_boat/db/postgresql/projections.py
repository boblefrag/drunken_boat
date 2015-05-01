import os
from drunken_boat.db.postgresql.fields import Field
from drunken_boat.db.exceptions import NotFoundError


class DataBaseObject(object):

    def __init__(self, dict, *args, **kwargs):
        for k, v in dict.items():
            setattr(self, k, v)


class Query(object):
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

    def get_joins(self, *args, **kwargs):
        joins = []
        join_id = 0
        for field in self.fields:

            if hasattr(field, "join"):
                join_id += 1
                join_alias = "t{}".format(join_id)
                joins.append(
                    """INNER JOIN {table} {join_alias} ON
                    {from_field}={join_alias}.{to_field}""".format(
                        table=field.projection.Meta.table,
                        from_field=field.join[0],
                        to_field=field.join[1],
                        join_alias=join_alias
                    ))
                field.alias = ", ".join(
                    ['"{}"."{}"'.format(join_alias, f.db_name)
                     for f in field.projection(self.db).fields])
        return " ".join(joins)

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
                if not field.virtual:
                    fields.append('{}.{}'.format(field.table,
                                                 field.db_name))
                else:
                    if hasattr(field, "alias"):
                        fields.append(field.alias)
                    else:
                        fields.append(field.db_name)
            select_query = ", ".join(fields)
            query = "SELECT {} FROM {} {} {}".format(
                select_query,
                table,
                joins if joins else '',
                where if where else ''
            )

        db_results = self.db.select(query, kwargs.get("params"))
        for result in db_results:
            results.append(
                self.hydrate(result)[0]
            )
        return results

    @property
    def database_object(self):
        if not hasattr(self, "Meta") or not hasattr(
                    self.Meta, "database_object"):
            database_object = DataBaseObject
        else:
            database_object = self.Meta.database_object
        return database_object

    def hydrate(self, result):
        r = result
        obj = {}
        for field in self.fields:
            hydrated, r = field.hydrate(r)
            obj.update(hydrated)
        return self.database_object(obj), r

        # return self.database_object(
        #     self.fields,
        #     **dict(zip(
        #         [field.name for field in self.fields],
        #         result)))


class Projection(Query):

    def __new__(cls, *args, **kwargs):
        cls.fields = []
        for name, attr in cls.__dict__.items():
            if isinstance(attr, Field):
                if not getattr(attr, "db_name"):
                    attr.db_name = name
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

    @property
    def get_fields(self):
        result = []
        if not hasattr(self, "schema"):
            schema = "public"
        sql = os.path.join(os.path.dirname(__file__),
                           "sql",
                           "get_fields_from_table.sql")
        with open(sql) as sql:
            with self.db.cursor() as cur:
                cur.execute(sql.read(), (schema, self.Meta.table))
                db_result = cur.fetchall()
        fields = ["column_name", "data_type",
                  "is_nullable", "column_default"]
        for elem in db_result:
            result.append(dict(zip(fields, elem)))
        return result

    def insert(self, values, returning=None):
        if not values:
            raise ValueError("values parameter cannot be an empty dict")
        db_fields = self.get_fields
        errors = []
        for fields in db_fields:
            if not values.get(fields["column_name"]) and \
               fields["is_nullable"] == "NO" and \
               fields["column_default"] is None:
                errors.append("{} of type {} is required".format(
                    fields["column_name"],
                    fields["data_type"]
                ))
        if len(errors) != 0:
            raise ValueError("\n".join(errors))
        keys = []
        vals = []

        for k, v in values.items():
            keys.append(k)
            vals.append(v)

        sql_template = "insert into {} ({}) VALUES ({})"
        if returning:
            if returning == "self":
                sql_template += "returning {}".format(
                    ", ".join([f.db_name for f in self.fields]))
            else:
                sql_template += "returning {}".format(returning)
        sql = sql_template.format(
            self.Meta.table,
            ", ".join(tuple(keys)),
            ", ".join(["%s" for k in keys])
        )
        params = vals
        res = None
        with self.db.cursor() as cur:
            try:
                cur.execute(sql, params)
            except Exception as e:
                self.db.conn.rollback()
                raise e
            if returning:
                res = cur.fetchone()
        self.db.conn.commit()
        if returning == "self":
            return self.hydrate(res)[0]
        return res

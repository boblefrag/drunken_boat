import os
from drunken_boat.db.postgresql.fields import Field
from drunken_boat.db.postgresql.query import Query, Where
from drunken_boat.db.postgresql import field_is_nullable
from drunken_boat.db.exceptions import NotFoundError


class DataBaseObject(object):

    def __init__(self, dict, *args, **kwargs):
        for k, v in dict.items():
            setattr(self, k, v)


class ProjectionQuery(object):

    def get_by_pk(self, pk, *args, **kwargs):
        pk_column = self.db.get_primary_key(self.Meta.table)
        where = "{} = %s".format(pk_column)
        kwargs["params"] = kwargs.get("params", [])
        kwargs["params"].append(pk)
        results = self.select(where=where, params=kwargs["params"])
        if len(results) == 0:
            raise NotFoundError("{} with value {} does not exists".format(
                pk_column, pk
            ))
        return results[0]

    def get_joins(self, table, *args, **kwargs):
        joins = []
        join_id = 0
        self_table = table
        for field in self.fields:

            if hasattr(field, "join") and field.make_join:
                join_id += 1
                join_alias = "t{}".format(join_id)
                joins.append(
                    """INNER JOIN {table} {join_alias} ON
                    {self_table}.{from_field}={join_alias}.{to_field}
                    """.format(
                        self_table=self_table,
                        table=field.projection.Meta.table,
                        from_field=field.join[0],
                        to_field=field.join[1],
                        join_alias=join_alias
                    ))
                field.alias = ", ".join(
                    ['"{}"."{}"'.format(join_alias, f.db_name)
                     for f in field.projection(self.db).fields])
        return " ".join(joins)

    def get_query_from(self, *args, **kwargs):
        where = kwargs.get("where")
        if isinstance(where, Where):
                where = where()
        if not where:
            where = self.get_where(*args, **kwargs)
        table = self.get_table(*args, **kwargs)
        joins = self.get_joins(table, *args, **kwargs)
        return "{} {} {}".format(
            table,
            joins if joins else '',
            "WHERE {}".format(where) if where else ''
        )

    def select(self, lazy=False, *args, **kwargs):
        if kwargs.get("query"):
            # if a query is already given, just use this one
            query = kwargs["query"]
        else:
            query_from = self.get_query_from(self, *args, **kwargs)
            fields = []
            for field in self.fields:
                select = field.get_select()
                if select:
                    fields.append(select)
            select_query = ", ".join(fields)
            query = "SELECT {} FROM {}".format(
                select_query,
                query_from
            )

        Q = Query(self, query,
                  params=kwargs.pop("params", None),
                  **kwargs.get("related", {}))
        if lazy:
            return Q
        else:
            return Q.execute()

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


class Projection(ProjectionQuery):

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

    def check_constrains(self, values):
        """
        For each field on the table check if a value is provided. If no
        value is provided, ensure the field is nullable or a default
        value is provided.
        """
        errors = []
        for field in self.get_table_fields:
            if not values.get(
                    field["column_name"]) and not field_is_nullable(field):
                errors.append("{} of type {} is required".format(
                    field["column_name"],
                    field["data_type"]
                ))
        if len(errors) != 0:
            raise ValueError("\n".join(errors))

    def get_table(self, *args, **kwargs):
        if hasattr(self, "Meta"):
            if hasattr(self.Meta, "table"):
                return self.Meta.table
        raise ValueError("""You does not define {} Meta.table .Projections on
multitable must define a get_table method""".format(self))

    @property
    def get_table_fields(self):
        """
        Introspect the table to get all the fields of the table and
        retreive column_name, data_type, is_nullable and
        column_default.
        """
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

    def make_returning(self, sql_template, returning=None):
        if returning:
            returning_fields = []
            if returning == "self":
                returning_fields = [f.get_select() for f in self.fields]
            else:
                returning_fields = [returning]

            if not len(returning_fields) == 0:
                sql_template += "returning {}".format(
                    ",".join(returning_fields))
        return sql_template

    def insert(self, values, returning=None):
        """
        Insert a new row into the table checking for constraints.  If
        returning is set, return the corresponding column(s).  If the
        special "self" is given to returning, return the
        DatabaseObject used by this Projection
        """
        if not values:
            raise ValueError("values parameter cannot be an empty dict")

        self.check_constrains(values)
        keys = []
        vals = []
        for k, v in values.items():
            keys.append(k)
            vals.append(v)

        sql_template = "insert into {} ({}) VALUES ({})"
        sql_template = self.make_returning(sql_template, returning)

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
        results = self.return_results([res], returning)
        if len(results) > 0:
            return results[0]

    def update(self, where, values, where_params, returning=None):
        args = []
        params = []
        for k, v in values.items():
            args.append(k)
            params.append(v)
        [params.append(p) for p in where_params]
        if isinstance(where, Where):
            where = where()
        joins = self.get_joins(self.Meta.table)
        sql_template = """
        UPDATE {table} SET {args} {joins} WHERE {where}""".format(
            table=self.Meta.table,
            joins=joins if joins else '',
            args=", ".join(["{}=%s".format(arg) for arg in args]),
            where=where
        )
        sql_template = self.make_returning(sql_template, returning)
        res = None
        with self.db.cursor() as cur:
            try:
                cur.execute(sql_template, params)
            except Exception as e:
                self.db.conn.rollback()
                raise e
            if returning:
                res = cur.fetchall()
        self.db.conn.commit()
        return self.return_results(res, returning)

    def delete(self, where, params, returning=None):
        if isinstance(where, Where):
            where = where()
        sql_template = """DELETE FROM {table} WHERE {where}""".format(
            table=self.Meta.table,
            where=where
        )
        sql_template = self.make_returning(sql_template, returning)
        res = None
        with self.db.cursor() as cur:
            try:
                cur.execute(sql_template, params)
            except Exception as e:
                self.db.conn.rollback()
                raise e
            if returning:
                res = cur.fetchall()
        self.db.conn.commit()
        return self.return_results(res, returning)

    def return_results(self, res, returning):
        results = []
        if res:
            if returning == "self":
                for result in res:
                    results.append(
                        self.hydrate(result)[0]
                    )
                for field in self.fields:
                    if hasattr(field, "extra"):
                        results = field.extra(self, results)
            else:
                results = res

        return results

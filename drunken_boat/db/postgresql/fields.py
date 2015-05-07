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

    def get_select(self):
        """Return the select representation of the field"""
        if not self.virtual:
            return '{}.{}'.format(self.table, self.db_name)

        else:
            if hasattr(self, "alias"):
                return self.alias
        return self.db_name


class Related(Field):

    virtual = True
    make_join = True

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


class ReverseForeign(Related):
    make_join = False

    def get_select(self):
        return self.join[0]

    def extra(self, projection, results, where=None, params=None):
        """The extra method will make a request to get all the related
        object pointed by the ReverseForeign storing them in
        self.related_object.

        then, when self.hydrate will be called, those objects will be
        added to the object representation of the main Projection.
        """
        lookup = [getattr(result, self.join[0]) for result in results]
        reverse_projection = self.projection(projection.db)
        reverse_field = Field(db_name=self.join[1],
                              table=reverse_projection.Meta.table)
        reverse_field.name = reverse_field.db_name
        reverse_projection.fields.append(
            reverse_field
        )
        where_clause = "{}=ANY(%s)".format(self.join[1])
        if where:
            where_clause = "{} AND ({})".format(where_clause, where)
        params_clause = [[lookup]]
        if params:
            [params_clause.append(param) for param in params]

        reverses = reverse_projection.select(
            where=where_clause,
            params=params_clause)
        for result in results:
            setattr(
                result,
                self.name,
                [reverse for reverse in reverses
                 if getattr(
                         reverse,
                         self.join[1]) == getattr(result, self.join[0])])

        return results

    def hydrate(self, result):
        hydrated = {self.join[0]: result[0]}
        result = result[1:]
        return hydrated, result


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

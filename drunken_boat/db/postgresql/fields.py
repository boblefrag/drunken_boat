"""This module manage database Fields and behavior of special fields
like foreignkey, reverse foreignkey etc...
"""

from drunken_boat.db.postgresql.query import Where


class Field(object):
    """
    Base class for managing fields. Anything from varchar to array
    """
    virtual = False

    def __init__(self, db_name=None, table=None, **kwargs):
        self.db_name = db_name
        self.table = table
        if kwargs.get("virtual"):
            self.virtual = kwargs["virtual"]

    def hydrate(self, result):
        """
        fill the python field with the result from database with
        conversion if needed
        """
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
    """
    A related field is a field pointing on another field or
    table. Exeample is foreignkey or reverse foreignkey
    """

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
    """
    A field pointing to a another field on another table
    """
    pass


class ReverseForeign(Related):
    """
    A virtual field (not actualy on the database) showing database
    lines with a relation to a field. FOr exemple all the Post of an
    Author (table post having a foreingkey on author)
    """
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
        # do not try to get reverse if there is no results
        if len(results) == 0:
            return []
        # get the lookup, the reverse projection and the reverse field
        # lookup is the list of results used for the reverse relation
        lookup = [getattr(result, self.join[0]) for result in results]
        reverse_projection = self.projection(projection.db)
        reverse_field = Field(db_name=self.join[1],
                              table=reverse_projection.Meta.table)
        # reverse field name is the real database field
        reverse_field.name = reverse_field.db_name
        reverse_projection.fields.append(
            reverse_field
        )
        # the default where clause is the lookup on the reverse
        # relation. Something like where related_field = ANY(1, 2,3,
        # ...)
        where_clause = "{}=ANY(%s)".format(self.join[1])
        # One can also add more condition on the reverse relation
        if where:
            if isinstance(where, Where):
                where = where()
            where_clause = "{} AND ({})".format(where_clause, where)
        params_clause = [[lookup]]
        # if another condition is added to the reverse, we need to get
        # the parameters of this condition
        if params:
            for param in params:
                params_clause.append(param)
        # Now it's time to make the request on the database
        reverses = reverse_projection.select(
            where=where_clause,
            params=params_clause)
        # then we dispatch the result of the reverse query into the
        # results we got earlier
        for result in results:
            setattr(
                result,
                self.name,
                [reverse for reverse in reverses
                    if getattr(
                        reverse,
                        self.join[1]
                    ) == getattr(result, self.join[0])])

        return results

    def hydrate(self, result):
        hydrated = {self.join[0]: result[0]}
        result = result[1:]
        return hydrated, result


class CharField(Field):
    """
    varchar db type
    """
    db_type = "varchar"


class Text(Field):
    """
    text db type
    """
    db_type = "text"


class Integer(Field):
    """
    integer db type
    """
    db_type = "integer"


class Timestamp(Field):
    """
    timestamp db type
    """
    db_type = "timestamp"


class Boolean(Field):
    """
    boolean type
    """
    db_type = "boolean"

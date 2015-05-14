from drunken_boat.db.postgresql.projections import DataBaseObject
from drunken_boat.db.postgresql.fields import Field
from drunken_boat.db.postgresql.query import Where


class ModelObject(DataBaseObject):

    def __init__(self, projection, **kwargs):
        self.projection = projection
        self.pk_column = projection.db.get_primary_key(projection.Meta.table)
        if self.pk_column not in [
                field.db_name for field in self.projection.fields]:
            pk = Field(db_name=self.pk_column,
                       table=projection.Meta.table)
            pk.name = pk.db_name
            self.projection.fields.append(pk)
        if not kwargs:
            kwargs = {}
        super(ModelObject, self).__init__(kwargs)

    def get_attrs(self):
        attrs = {}
        for key, value in self.__dict__.items():
            if key not in ["projection", "pk_column"]:
                attrs[key] = value
        return attrs

    def save(self, returning=None):
        attrs = self.get_attrs()
        attrs.pop(self.pk_column, None)
        if not returning:
            returning = self.pk_column
            returning_index = 0
        else:
            if returning != "self":
                if self.pk_column not in returning:
                    returning += ",{}".format(self.pk_column)
                returning_index = returning.split(",").index(self.pk_column)
            else:
                returning_index = None
        try:
            result = self.projection.insert(attrs,
                                            returning=returning)
        except Exception as e:
            raise e
        if returning_index is not None:
            setattr(self, self.pk_column, result[returning_index])
        else:
            setattr(self, self.pk_column, getattr(result, self.pk_column))
        return result

    def update(self, returning=None):
        where = Where(self.pk_column, "=", "%s")
        try:
            result = self.projection.update(
                where(),
                self.get_attrs(),
                (getattr(self, self.pk_column),),
                returning=returning)
        except Exception as e:
            raise e
        if result:
            return result[0]

    def delete(self, returning=None):
        where = Where(self.pk_column, "=", "%s")
        return self.projection.delete(where(),
                                      (getattr(self, self.pk_column),),
                                      returning=returning)


class Projections(object):

    def __init__(self, database, projections):
        for projection_name, projection in projections.items():
            setattr(self, projection_name, projection(database))
        if not hasattr(self, "default"):
            self.default = projections[list(projections.keys())[0]](database)


class Model(object):
    """
    A model is a place to hold all you projections and define database
    It offer clean api to create new objects.
    """

    def __init__(self, database, projections):
        self.projections = Projections(database, projections)
        self.database = database
        self.database_object = ModelObject

    def object(self, projection=None):
        if not projection:
            projection = self.projections.default
        return self.database_object(projection)

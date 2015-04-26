class Field(object):

    def __init__(self, name=None, table=None, *args, **kwargs):
        self.name = name
        self.table = table

    def __call__(self, value, *args, **kwargs):
        obj = self.__class__(*args, **kwargs)
        obj.value = value
        return obj

    def __repr__(self):
        if hasattr(self, "value"):
            return self.value
        else:
            return super(Field, self).__repr__()


class CharField(Field):
    db_type = "character varying"

    def __init__(self, limit, name=None, table=None):
        super(CharField, self).__init__(name, table)
        self.limit = limit

    def __call__(self, value, *args, **kwargs):
        obj = super(CharField, self).__call__(value, limit=self.limit)
        return obj


class Text(Field):
    db_type = "text"

class Query(object):

    def __init__(self, projection, query, params=None, **kwargs):
        self.query = query
        self.params = params
        self.projection = projection
        self.kwargs = kwargs

    def execute(self):
        results = []
        db_results = self.projection.db.select(self.query, self.params)
        for result in db_results:
            results.append(
                self.projection.hydrate(result)[0]
            )
        for field in self.projection.fields:
            if hasattr(field, "extra"):
                where, params = None, None
                if self.kwargs.get(field.name):
                    where = self.kwargs[field.name].get("where")
                    params = self.kwargs[field.name].get("params")
                results = field.extra(self.projection, results,
                                      where=where, params=params)
        return results


class Where(object):

    def __init__(self, clause, operator, value):
        """
        Where object let you write in an easy, clear and maintanable
        manner WHERE clause to add to your queries.
        Where objects will be roughly executed as:
        WHERE {clause}{operator}{value}
        for example Where('id', '=', %s) will be executed as :

        WHERE id = %s

        you can also express things more fun like:
        Where('id', '=', ANY(%s)) that will be rendered as:

        WHERE id = ANY(%s)
        """
        self.clause = clause
        self.operator = operator
        self.value = value
        self.clause_list = [self.render()]

    def render(self):
        return "{clause} {operator} {value}".format(
            clause=self.clause,
            operator=self.operator,
            value=self.value)

    def __call__(self):
        return "({})".format(" ".join(self.clause_list))

    def __and__(self, obj):
        if not isinstance(obj, Where):
            raise TypeError("cannot concatenate {} and {}".format(
                obj.__class__,
                self.__class__
            ))
        else:
            self.clause_list += ["AND", obj()]
        return self

    def __or__(self, obj):
        if not isinstance(obj, Where):
            raise TypeError(
                "unsupported operand type(s) for |: {} and {}".format(
                    obj.__class__,
                    self.__class__
                ))
        else:
            self.clause_list += ["OR", obj()]
        return self

    def __invert__(self):
        self.clause_list = ["NOT", self()]
        return self

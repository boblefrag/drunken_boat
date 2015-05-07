class Query(object):

    def __init__(self, projection, query, params=None, **kwargs):
        self.query = query
        self.params = params
        self.projection = projection
        self.kwargs = kwargs

    def execute(self):
        results = []
        print self.query, self.params
        db_results = self.projection.db.select(self.query, self.params)
        for result in db_results:
            results.append(
                self.projection.hydrate(result)[0]
            )
        for field in self.projection.fields:
            if hasattr(field, "extra"):
                where, params = None, None
                if self.kwargs.get(field.name):
                    print self.kwargs.get(field.name)
                    where = self.kwargs[field.name].get("where")
                    params = self.kwargs[field.name].get("params")
                results = field.extra(self.projection, results,
                                      where=where, params=params)
        return results

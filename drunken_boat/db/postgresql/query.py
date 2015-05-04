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
                results = field.extra(self.projection, results, **self.kwargs)
        return results

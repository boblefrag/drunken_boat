"""Router is respnsible to parse a URL and return the right View or a
404 if this view does not exists
"""
from werkzeug.routing import Rule, Map, Submount


class Router(object):
    view = None
    rules = None
    patterns = None

    def __init__(self, url, view=None):
        self.url = url
        if view:
            self.view = view

    def build_rules(self, prefix=None):
        rules = []
        if not self.rules:
            if self.view:
                rules.append(Rule(self.url, endpoint=self.view))
            if self.patterns:
                for pattern in self.patterns:
                    sub_rules = pattern.build_rules(prefix=self.url)
                    rules.append(sub_rules)
            if prefix:
                self.rules = Submount(prefix, rules)
            else:
                self.rules = Map(rules)
        return self.rules

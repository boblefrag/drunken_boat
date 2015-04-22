"""Router is respnsible to parse a URL and return the right View or a
404 if this view does not exists
"""
from werkzeug.routing import Rule, Map, Submount

class Router(object):
    view = None
    rules = None
    patterns = None

    @classmethod
    def build_rules(klass, prefix=None):
        rules = []
        if not klass.rules:
            if klass.view:
                rules.append(Rule(klass.url, endpoint=klass.view))
            if klass.patterns:
                for pattern in klass.patterns:
                    sub_rules = pattern.build_rules(prefix=klass.url)
                    rules.append(sub_rules)
            if prefix:
                klass.rules = Submount(prefix, rules)
            else:
                klass.rules = Map(rules)
        return klass.rules

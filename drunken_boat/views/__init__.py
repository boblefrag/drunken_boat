from werkzeug.exceptions import MethodNotAllowed


class View(object):
    def render(self, request, **kwargs):
        try:
            return getattr(self, request.method.lower())(request, **kwargs)
        except AttributeError:
            raise MethodNotAllowed

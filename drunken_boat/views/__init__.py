"""
A View is responsible for computing a Request object into a Response object.
This module define the base handling of request handling
"""
from werkzeug.exceptions import MethodNotAllowed


class View(object):
    """A view module is binded to a Router. It's a simple placeholder to
    let you implement GET/POST/PUT/DELETE/PATCH/HEAD or OPTION method
    """

    def render(self, request, **kwargs):
        """return either a self.method correspondig to the request.method or
        a 405 error (method not allowed)
        """
        try:
            return getattr(self, request.method.lower())(request, **kwargs)
        except AttributeError:
            raise MethodNotAllowed

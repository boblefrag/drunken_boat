from werkzeug.wrappers import Request
from werkzeug.exceptions import HTTPException


class Application(object):

    def __init__(self, root_url, config=None):
        self.url = root_url

    def wsgi_app(self, environ, start_response):
        request = Request(environ)
        response = self.dispatch_request(request)
        return response(environ, start_response)

    def dispatch_request(self, request):
        url_map = self.url.build_rules()
        urls = url_map.bind_to_environ(request.environ)
        try:
            endpoint, kwargs = urls.match()

            return endpoint().render(request, **kwargs)
        except HTTPException, e:
            return e

    def __call__(self, environ, start_response):
        return self.wsgi_app(environ, start_response)

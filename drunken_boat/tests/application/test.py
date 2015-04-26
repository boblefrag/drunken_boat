from drunken_boat.router import Router
from drunken_boat.views import View
from werkzeug.wrappers import Response
from werkzeug.test import Client
from drunken_boat import Application


class ArticleView(View):

    def get(self, request, **kwargs):
        response = Response('Hello World!', mimetype='text/plain')
        return response


class ArticleRouter(Router):
    view = ArticleView


class CustomApplication(Application):
    def config(self, config={}):
        for k, v in config.items():
            setattr(self, k, v)


def config_application():
    articles_url = ArticleRouter("/home/")
    test_app = Application(articles_url)
    c = Client(test_app, Response)
    return c


def test_application_get():
    c = config_application()
    resp = c.get('/home/')
    assert resp.status_code == 200


def test_application_get_not_found():
    c = config_application()
    resp = c.get('/article/')
    assert resp.status_code == 404


def test_application_method_not_allowed():
    c = config_application()
    resp = c.post('/home/')
    assert resp.status_code == 405


def test_conf_app():
    articles_url = ArticleRouter("/home/")
    test_app = CustomApplication(articles_url)
    conf = {"foo": "bar"}
    test_app.config(conf)
    assert hasattr(test_app, "foo")
    assert test_app.foo == "bar"

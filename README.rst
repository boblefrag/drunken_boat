P-Framework
-----------

Performance based web framework written in python

A simple Hello World
--------------------

from p_framework import Application
from p_framework.router import Router
from p_framework.views import View
from werkzeug.wrappers import Response


class ArticleView(View):

    def get(self, request, **kwargs):
        response = Response('Hello World!', mimetype='text/plain')
        return response


class ArticleRouter(Router):
    view = ArticleView


if __name__ == '__main__':
    from werkzeug.serving import run_simple
    articles_url = ArticleRouter("/home/")
    app = Application(articles_url)
    run_simple('127.0.0.1', 5000, app, use_debugger=True, use_reloader=True)

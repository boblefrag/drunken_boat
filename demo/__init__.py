from drunken_boat import Application
from drunken_boat.router import Router
from drunken_boat.views import View
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

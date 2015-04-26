Drunken Boat
------------

.. image::
   https://coveralls.io/repos/boblefrag/drunken_boat/badge.svg?branch=master
   :target: https://coveralls.io/r/boblefrag/drunken_boat?branch=master

.. image:: https://travis-ci.org/boblefrag/drunken_boat.svg?branch=master
    :target: https://travis-ci.org/boblefrag/drunken_boat


Drunken boat is a performance based webframework under heavy active
developpment.

It offer Routing, View management and a projection based ORM, schema
less and eventualy agnostic


A simple Hello World
--------------------

.. code-block:: python

    from drunken_boat import Application
    from drunken_boat.router import Router
    from drunken_boat.views import View
    from werkzeug.wrappers import Response


    class ArticleView(View):

        def get(self, request, **kwargs):
            response = Response('Hello World!', mimetype='text/plain')
            return response


    if __name__ == '__main__':
        from werkzeug.serving import run_simple
        app = Application(
            Router("/home/", view=ArticleView)
        )
        run_simple('127.0.0.1', 5000, app, use_debugger=True, use_reloader=True)

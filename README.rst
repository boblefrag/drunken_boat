Drunken Boat
============

.. image::
   https://coveralls.io/repos/boblefrag/drunken_boat/badge.svg?branch=master
   :target: https://coveralls.io/r/boblefrag/drunken_boat?branch=master

.. image:: https://travis-ci.org/boblefrag/drunken_boat.svg?branch=master
    :target: https://travis-ci.org/boblefrag/drunken_boat

.. image:: https://readthedocs.org/projects/drunken-boat/badge/?version=stable
    :target: https://readthedocs.org/projects/drunken-boat/?badge=stable


Drunken boat is a performance based webframework under heavy active
developpment.

It offer Routing, View management and a projection based ORM, schema
less and eventualy agnostic


A simple Hello World
____________________

first, install `drunken-boat` see http://drunken-boat.readthedocs.org/en/stable/install.html. Once drunken_boat
installed you can boostrap your first application with::

     drunken_run.py bootstrap example_blog

This will create for you all you need to start::

    cd /home/yohann/Dev/drunken_boat/example_blog
    python application.py

then visit http://localhost:5000/

Project Layout
--------------

drunken_run.py bootstrap example_blog create a new `example_blog`
directory with base file structure to start working::

    example_blog/
      -- __init__.py
      -- application.py
      -- router.py
      -- views.py
      -- projection.py
      -- config.py

content of `application.py`::

    from drunken_boat import Application
    from example_blog.router import MainRouter

    app = Application(
            MainRouter("/")
        )

    if __name__ == '__main__':
        from werkzeug.serving import run_simple
        run_simple('127.0.0.1', 5000, app, use_debugger=True, use_reloader=True)


application only need an Application instance with a `Router`
responsible for routing the incomming requests.

content of `router.py`::

    from drunken_boat.router import Router
    from example_blog.views import MainView


    class MainRouter(Router):
        view = MainView

a router can be as simple as this one but obviously you can add more
endpoints using `Router.patterns`. `Router` can take a `View`
attribute to compute the `Response` to return

content of `view.py`::

    from drunken_boat.views import View
    from werkzeug.wrappers import Response


    class MainView(View):
        def get(self, request, **kwargs):
            response = Response('Hello World!', mimetype='text/plain')
            return response

Every request on "/" will return a "Hello World!" a lot more can be
done in `View` check the documentation on how to manage much more with
`MiddleWare`,  `Projection` for database access and else.

See http://drunken-boat.readthedocs.org/ for full documentation

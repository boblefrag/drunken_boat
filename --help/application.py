from drunken_boat import Application
from --help.router import MainRouter

app = Application(
        MainRouter("/"))

if __name__ == '__main__':
    from werkzeug.serving import run_simple
    run_simple('127.0.0.1', 5000, app, use_debugger=True, use_reloader=True)
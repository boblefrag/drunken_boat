from p_framework.router import Router
from werkzeug.routing import Map


class HomeView(object):
    pass


class ArticleView(object):
    pass


class ArticleRouter(Router):
    url = "/articles"
    view = ArticleView

class DetailRouter(Router):
    url = "/article/<int:id>"
    view = ArticleView


class BaseRouter(Router):
    url = "/index"
    patterns = [ArticleRouter]


class EmptyRouter(Router):
    url = "/index"
    patterns = []

class Home(Router):
    url = "/home"
    view = HomeView

def test_rules_is_map():
    assert isinstance(Home.build_rules(), Map)

def test_map_contain_homeview_endpoint():
    assert Home.build_rules()._rules[0].endpoint == HomeView

def test_map_contain_one_rule():
    assert len(Home.build_rules()._rules) == 1

def test_rules_persists():
    Home.build_rules()
    assert isinstance(Home.rules, Map)

def test_sub_discovery():
    assert isinstance(BaseRouter.build_rules(), Map)

def test_sub_contain_sub_url():
    t = BaseRouter.build_rules()
    assert t._rules[0].map._rules[0].rule == "/index/articles"

def test_empty_router_no_raise():
    assert isinstance(EmptyRouter.build_rules(), Map)

def test_empty_router_no_routes():
    assert len(EmptyRouter.build_rules()._rules) == 0

def test_detail_router_with_params():
    assert isinstance(DetailRouter.build_rules(), Map)

def test_detail_router_with_params_regexp():
    t = DetailRouter.build_rules()
    assert t._rules[0]._regex.pattern == "^\|\/article\/(?P<id>\d+)$"
    assert list(t._rules[0].arguments)[0] == "id"

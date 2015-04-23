from p_framework.router import Router
from werkzeug.routing import Map


class HomeView(object):
    pass


class ArticleView(object):
    pass


class ArticleRouter(Router):
    view = ArticleView


class DetailRouter(Router):
    view = ArticleView


class BaseRouter(Router):
    patterns = [ArticleRouter("/articles")]


class EmptyRouter(Router):
    patterns = []


class Home(Router):
    view = HomeView


def test_rules_is_map():
    home = Home("/home")
    assert isinstance(home.build_rules(), Map)


def test_map_contain_homeview_endpoint():
    home = Home("/home")
    assert home.build_rules()._rules[0].endpoint == HomeView


def test_map_contain_one_rule():
    home = Home("/home")
    assert len(home.build_rules()._rules) == 1


def test_rules_persists():
    home = Home("/home")
    home.build_rules()
    assert isinstance(home.rules, Map)


def test_sub_discovery():
    base_router = BaseRouter("/index")
    assert isinstance(base_router.build_rules(), Map)


def test_sub_contain_sub_url():
    base_router = BaseRouter("/index")
    t = base_router.build_rules()
    assert t._rules[0].map._rules[0].rule == "/index/articles"


def test_empty_router_no_raise():
    empty_router = EmptyRouter("/index/")
    assert isinstance(empty_router.build_rules(), Map)


def test_empty_router_no_routes():
    empty_router = EmptyRouter("/index/")
    assert len(empty_router.build_rules()._rules) == 0


def test_detail_router_with_params():
    detail_router = DetailRouter("/article/<int:id>")
    assert isinstance(detail_router.build_rules(), Map)


def test_detail_router_with_params_regexp():
    detail_router = DetailRouter("/article/<int:id>")
    t = detail_router.build_rules()
    assert t._rules[0]._regex.pattern == "^\|\/article\/(?P<id>\d+)$"
    assert list(t._rules[0].arguments)[0] == "id"

P-Framework
-----------

Performance based web framework written in python

#### home/router.py ####
from p_framework.router import Router
from home.views import HomeView

class Home(Router):
    view = HomeView

home_url = Home("/home/")

#### articles/router.py ####
from p_framework.router import Router
from articles.views import (DetailView, ListView)

class Detail(Router):
    url = "(?P<pk>\d+)"
    view = DetailView

class Articles(Router):
    view = ListView
    patterns = [
    Detail("/<int:id>/")
    ]

articles_url = Articles("/articles/")

#### articles/views ####
from p_framework import View
from articles.db import ArticleList, ArticleDetail
from articles.templates import List

class ListView(View):

    def get(request):
        template = Detail
        return List(ArticleList.get(limit=10))

    def post(request):
        pass

    def put(request):
        pass

    def delete(request):
        pass
##### articles/db #########
from p_framework.db.backend.postgresql import DB
from articles.router import Detail

class AuthorForeign(DB):
    _table = "author"
    firstname = DB.VarChar()
    lastname = DB.VarChar()


class ArticleList(DB):
    _table = "article"
    id = DB.PositiveInteger()
    title = DB.VarChar()
    author = DB.ForeignKey(AuthorForeign)
    introduction = DB.Text()

    def url(self):
        return Detail.get_url(self.id)
#### articles/templates ####
from p_framework.templates import HTML

class Detail(HTML):
    def get_path(self):
        return "articles/templates/html/article_list.html"

#### articles/templates/html/article_list.html ####
{% for article in articles %}
<h3>{{article.title}} by {{article.author.firstname}} {{article.author.lastname}}</h3>
<p>{{article.introduction}}</p>
<a href="{{article.url}}">read more</a>
{% endfor %}

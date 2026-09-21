from django.urls import path

from .views import article_detail, article_list

app_name = "blog"

urlpatterns = [
    path("", article_list, name="article_list"),
    path("search/", article_list, name="article_search"),
    path("<slug:slug>/", article_detail, name="article_detail"),
]

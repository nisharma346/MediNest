from django.urls import path
from .views import home, services

app_name = "core"

urlpatterns = [
    path("", home, name="home"),
    path("services/", services, name="services"),
]
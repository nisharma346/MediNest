from django.urls import path
from .views import home, services, admin_dashboard

app_name = "core"

urlpatterns = [
    path("", home, name="home"),
    path("services/", services, name="services"),
    path("admin-dashboard/", admin_dashboard, name="admin_dashboard"),
]
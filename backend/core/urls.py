from django.urls import path
from .views import (
    home, services, contact, admin_dashboard,
    health_update_list, health_update_detail,
    gallery_list
)

app_name = "core"

urlpatterns = [
    path("", home, name="home"),
    path("services/", services, name="services"),
    path("contact/", contact, name="contact"),
    path("gallery/", gallery_list, name="gallery_list"),
    path("health-updates/", health_update_list, name="health_update_list"),
    path("health-updates/<slug:slug>/", health_update_detail, name="health_update_detail"),
    path("admin-dashboard/", admin_dashboard, name="admin_dashboard"),
]
from django.urls import path
from .views import register, user_login, user_logout, dashboard, edit_profile

app_name = "accounts"

urlpatterns = [
    path("register/", register, name="register"),
    path("login/", user_login, name="login"),
    path("dashboard/", dashboard, name="dashboard"),
    path("profile/edit/", edit_profile, name="edit_profile"),
    path("logout/", user_logout, name="logout"),
]
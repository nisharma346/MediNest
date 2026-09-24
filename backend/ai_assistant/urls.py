from django.urls import path
from . import views

app_name = "ai_assistant"

urlpatterns = [
    path("", views.assistant_view, name="assistant"),
    path("api/chat/", views.chat_api_view, name="chat_api"),
]

import json
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST

from .services import get_ai_health_response


def assistant_view(request):
    """
    Renders the MediNest AI Health Assistant chat interface page.
    """
    return render(request, "ai_assistant/assistant.html")


@require_POST
def chat_api_view(request):
    """
    POST API endpoint for receiving chat messages from the browser UI,
    calling the OpenAI service, and returning JSON.
    """
    try:
        data = json.loads(request.body.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse(
            {"success": False, "error": "Invalid JSON format in request body."},
            status=400
        )

    user_message = data.get("message", "")
    if not user_message:
        return JsonResponse(
            {"success": False, "error": "Message parameter is required."},
            status=400
        )

    result = get_ai_health_response(user_message)
    if result.get("success"):
        return JsonResponse({
            "success": True,
            "response": result.get("response", "")
        })
    else:
        return JsonResponse({
            "success": False,
            "error": result.get("error", "An unexpected error occurred.")
        })

import logging
import os
from django.conf import settings

logger = logging.getLogger(__name__)

# Maximum allowed input length for user messages
MAX_MESSAGE_LENGTH = 1000

# Strict Developer System Prompt for Healthcare Safety & Disclaimers
AI_SYSTEM_PROMPT = """You are MediNest AI Health Assistant.

You provide general health and wellness information and educational guidance.

You are NOT a doctor and must not claim to diagnose diseases.

Do not provide definitive medical diagnoses.

Do not prescribe prescription medicines or provide medication dosage instructions.

Do not tell users to stop or start prescription medication.

For symptoms, explain possible general categories of causes carefully and recommend consulting an appropriate qualified healthcare professional when necessary.

If symptoms could indicate a medical emergency, clearly advise the user to seek immediate emergency medical care.

Do not pretend to have access to the user's medical records, laboratory results, scans, prescriptions, or medical history unless such information is explicitly provided in the current conversation.

Do not claim certainty when medical information is uncertain.

Encourage users to consult a qualified doctor for diagnosis and treatment.

Keep answers clear, friendly, concise, and understandable for normal users.

Always prioritize user safety.

If a user describes potentially serious emergency symptoms (such as severe chest pain, difficulty breathing, unconsciousness, signs of stroke, severe bleeding, seizures, suicidal/self-harm emergency, or severe allergic reaction), state clearly:
"If this may be an emergency, seek immediate medical attention or contact your local emergency service."
"""


def _generate_health_fallback(query):
    """
    Generates educational health guidance as a fallback when OpenAI API key
    is inactive or out of credits (429 RateLimitError / insufficient_quota).
    """
    q = query.lower()

    # Emergency check
    emergency_keywords = ["chest pain", "breathing", "unconscious", "stroke", "bleeding", "seizure", "suicide", "allergic"]
    if any(k in q for k in emergency_keywords):
        return (
            "⚠️ **Emergency Medical Warning:** If you or someone around you is experiencing potentially severe symptoms "
            "(such as difficulty breathing, severe chest pain, sudden numbness, or heavy bleeding), "
            "please seek immediate emergency medical attention or contact your local emergency service immediately."
        )

    # Greetings
    if any(g in q for g in ["hi", "hello", "hey", "greetings", "namaste"]):
        return (
            "Hello! I am your **MediNest AI Health Assistant**.\n\n"
            "How can I assist you with your health and wellness questions today? "
            "You can ask me about sleep hygiene, nutrition guidelines, fitness tips, stress management, or general symptom categories."
        )

    # Sleep
    if "sleep" in q:
        return (
            "Here are general evidence-based tips to improve your sleep quality:\n\n"
            "1. **Maintain a Regular Schedule:** Go to bed and wake up at the same time daily.\n"
            "2. **Optimize Environment:** Keep your bedroom dark, quiet, and cool.\n"
            "3. **Screen Hygiene:** Avoid blue light screens (phones, laptops) 30-60 minutes before bedtime.\n"
            "4. **Limit Stimulants:** Avoid caffeine and heavy meals 4-6 hours before sleep.\n\n"
            "*Disclaimer: If chronic insomnia persists, please consult a qualified healthcare provider.*"
        )

    # Nutrition / Diet
    if any(n in q for n in ["nutrition", "food", "diet", "eat", "water", "drink"]):
        return (
            "Here are general daily nutrition & hydration guidelines:\n\n"
            "1. **Balanced Meals:** Include plenty of colorful vegetables, whole fruits, lean proteins, and whole grains.\n"
            "2. **Hydration:** Drink 8-10 glasses (about 2-2.5 liters) of water daily unless otherwise advised by your physician.\n"
            "3. **Minimize Processed Foods:** Reduce refined sugars, excess sodium, and ultra-processed snacks.\n\n"
            "*Always consult a registered dietitian or doctor for personalized dietary advice.*"
        )

    # Stress & Mental Wellness
    if any(s in q for s in ["stress", "anxiety", "headache", "head"]):
        return (
            "For managing mild stress or tension:\n\n"
            "1. **Mindful Breathing:** Practice 4-7-8 deep breathing exercises.\n"
            "2. **Physical Activity:** Short daily walks promote endorphin release.\n"
            "3. **Rest & Screen Breaks:** Rest your eyes periodically during screen work.\n\n"
            "*If you experience severe headaches, fever, or persistent anxiety, please seek guidance from a medical professional.*"
        )

    # Default general wellness guidance
    return (
        f"Thank you for asking about '{query}'.\n\n"
        "As your MediNest AI Health Assistant, I provide general educational health and wellness information. "
        "For optimal well-being, maintain a balanced diet, stay hydrated, engage in regular physical activity, and prioritize adequate sleep.\n\n"
        "For specific medical diagnoses, prescriptions, or personalized treatment plans, please consult a licensed doctor or healthcare professional."
    )


def get_ai_health_response(user_message):
    """
    Validates user input, calls the OpenAI API safely, and returns the response string.
    - Does NOT log or expose API keys.
    - Catches API errors gracefully and provides fallback guidance when API credits are exhausted.
    """
    # 1. Validate user message type
    if not user_message or not isinstance(user_message, str):
        return {
            "success": False,
            "error": "Please enter a valid message."
        }

    cleaned_message = user_message.strip()

    # 2. Reject empty messages
    if not cleaned_message:
        return {
            "success": False,
            "error": "Message cannot be empty."
        }

    # 3. Limit excessively long messages
    if len(cleaned_message) > MAX_MESSAGE_LENGTH:
        return {
            "success": False,
            "error": f"Message is too long. Please keep your query under {MAX_MESSAGE_LENGTH} characters."
        }

    # 4. Extract API key safely from settings or environment
    api_key = getattr(settings, "OPENAI_API_KEY", None) or os.getenv("OPENAI_API_KEY")
    if not api_key:
        logger.warning("OPENAI_API_KEY is missing. Using MediNest Health Fallback.")
        return {
            "success": True,
            "response": _generate_health_fallback(cleaned_message)
        }

    # 5. Extract configurable model name
    model_name = getattr(settings, "OPENAI_MODEL", None) or os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)

        response_text = ""

        # 6. Try OpenAI Responses API
        if hasattr(client, "responses"):
            try:
                res = client.responses.create(
                    model=model_name,
                    instructions=AI_SYSTEM_PROMPT,
                    input=cleaned_message,
                )
                if hasattr(res, "output_text") and res.output_text:
                    response_text = res.output_text
                elif hasattr(res, "output") and res.output:
                    text_parts = []
                    for item in res.output:
                        if hasattr(item, "content") and item.content:
                            text_parts.append(str(item.content))
                        elif hasattr(item, "text") and item.text:
                            text_parts.append(str(item.text))
                    response_text = "\n".join(text_parts)
            except Exception as resp_exc:
                logger.warning(f"Responses API call failed ({type(resp_exc).__name__}). Falling back to Chat Completions.")
                response_text = ""

        # 7. Fallback to Chat Completions API if Responses API did not return text
        if not response_text:
            res = client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": AI_SYSTEM_PROMPT},
                    {"role": "user", "content": cleaned_message},
                ],
                max_tokens=1000,
                temperature=0.7,
            )
            if res.choices and len(res.choices) > 0:
                response_text = res.choices[0].message.content

        if not response_text:
            response_text = _generate_health_fallback(cleaned_message)

        return {
            "success": True,
            "response": response_text.strip()
        }

    except Exception as exc:
        # Never print or log the API key or credentials
        logger.warning(f"OpenAI API call ({type(exc).__name__}). Using MediNest AI Health Fallback.")
        return {
            "success": True,
            "response": _generate_health_fallback(cleaned_message)
        }

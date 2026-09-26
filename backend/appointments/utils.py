import logging
from django.conf import settings

try:
    import razorpay
except ImportError:
    razorpay = None

logger = logging.getLogger(__name__)


def get_razorpay_diagnostic():
    """
    Safe Razorpay configuration diagnostic.
    NEVER logs or exposes secret keys.
    """
    key_id = (getattr(settings, "RAZORPAY_KEY_ID", "") or "").strip()
    key_secret = (getattr(settings, "RAZORPAY_KEY_SECRET", "") or "").strip()

    key_id_exists = bool(key_id)
    key_secret_exists = bool(key_secret)
    is_non_empty = key_id_exists and key_secret_exists

    is_test_mode = key_id.startswith("rzp_test_")
    is_live_mode = key_id.startswith("rzp_live_")

    if is_test_mode:
        mode_str = "TEST Mode (rzp_test_)"
    elif is_live_mode:
        mode_str = "LIVE Mode (rzp_live_)"
    elif key_id_exists:
        mode_str = "Unknown Prefix"
    else:
        mode_str = "Missing Key ID"

    return {
        "key_id_exists": key_id_exists,
        "key_secret_exists": key_secret_exists,
        "is_non_empty": is_non_empty,
        "is_test_mode": is_test_mode,
        "is_live_mode": is_live_mode,
        "mode_str": mode_str,
        "sdk_installed": razorpay is not None,
    }


def verify_razorpay_auth():
    """
    Verifies Razorpay credentials by initializing the SDK client and making a test call.
    Returns tuple: (success: bool, message: str)
    NEVER exposes secret keys or credentials in logs or output.
    """
    diagnostic = get_razorpay_diagnostic()

    if not diagnostic["sdk_installed"]:
        return False, "Razorpay authentication failed: Razorpay SDK package is not installed."

    if not diagnostic["is_non_empty"]:
        return False, "Razorpay authentication failed: Credentials are missing or incomplete."

    key_id = settings.RAZORPAY_KEY_ID.strip()
    key_secret = settings.RAZORPAY_KEY_SECRET.strip()

    try:
        client = razorpay.Client(auth=(key_id, key_secret))
        # Create a lightweight test order (1 INR = 100 paise) to verify authentication
        client.order.create(
            data={
                "amount": 100,
                "currency": "INR",
                "receipt": "auth_verify_check",
                "notes": {"type": "auth_verification"},
            }
        )
        return True, "Razorpay credentials authenticated successfully"
    except razorpay.errors.BadRequestError as exc:
        logger.error("Razorpay authentication check failed: BadRequestError")
        return False, "Razorpay authentication failed: Bad Request"
    except razorpay.errors.ServerError as exc:
        logger.error("Razorpay authentication check failed: ServerError")
        return False, "Razorpay authentication failed: Server Error"
    except razorpay.errors.RazorpayError as exc:
        logger.error("Razorpay authentication check failed: RazorpayError")
        return False, "Razorpay authentication failed"
    except Exception as exc:
        logger.error("Razorpay authentication check failed: unexpected error")
        return False, "Razorpay authentication failed"

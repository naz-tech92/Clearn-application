import os
import firebase_admin
from firebase_admin import auth, credentials


def _initialize_firebase():
    if firebase_admin._apps:
        return

    service_account_path = os.environ.get("FIREBASE_SERVICE_ACCOUNT") or "serviceAccountKey.json"
    cred = credentials.Certificate(service_account_path)
    firebase_admin.initialize_app(cred)


_initialize_firebase()


def verify_firebase_token(id_token):
    try:
        return auth.verify_id_token(id_token)
    except Exception:
        return None


def create_firebase_user(email, password, full_name, phone_number):
    """Create a Firebase Authentication user."""
    try:
        existing = auth.get_user_by_email(email)
        return {
            "ok": False,
            "error": "A Firebase account already exists for this email.",
            "uid": existing.uid,
        }
    except auth.UserNotFoundError:
        pass
    except Exception as exc:
        return {
            "ok": False,
            "error": f"Unable to check Firebase account status: {exc}",
            "uid": None,
        }

    create_args = {
        "email": email,
        "password": password,
        "display_name": full_name,
    }

    clean_phone = (phone_number or "").strip()
    if clean_phone:
        create_args["phone_number"] = clean_phone if clean_phone.startswith("+") else f"+{clean_phone}"

    try:
        user = auth.create_user(**create_args)
        return {"ok": True, "uid": user.uid}
    except Exception as exc:
        return {"ok": False, "error": f"Firebase signup failed: {exc}", "uid": None}

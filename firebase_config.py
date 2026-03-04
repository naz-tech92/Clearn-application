import json
import os
from typing import Optional

try:
    import firebase_admin
    from firebase_admin import auth, credentials
except Exception:
    firebase_admin = None
    auth = None
    credentials = None


_FIREBASE_INIT_ERROR = None


def _service_account_payload() -> Optional[dict]:
    """Load service-account JSON from env first, then local file."""
    inline_json = (os.environ.get("FIREBASE_SERVICE_ACCOUNT_JSON") or "").strip()
    if inline_json:
        try:
            return json.loads(inline_json)
        except json.JSONDecodeError:
            return None

    path = (os.environ.get("FIREBASE_SERVICE_ACCOUNT_PATH") or "").strip()
    if path and os.path.exists(path):
        with open(path, "r", encoding="utf-8") as fh:
            return json.load(fh)

    local_path = os.path.join(os.path.dirname(__file__), "serviceAccountKey.json")
    if os.path.exists(local_path):
        with open(local_path, "r", encoding="utf-8") as fh:
            return json.load(fh)
    return None


def _init_firebase():
    global _FIREBASE_INIT_ERROR
    if firebase_admin is None or auth is None or credentials is None:
        _FIREBASE_INIT_ERROR = "firebase-admin is not installed."
        return False

    try:
        firebase_admin.get_app()
        _FIREBASE_INIT_ERROR = None
        return True
    except ValueError:
        pass

    payload = _service_account_payload()
    if not payload:
        _FIREBASE_INIT_ERROR = (
            "Firebase service account not found. Set FIREBASE_SERVICE_ACCOUNT_JSON "
            "or FIREBASE_SERVICE_ACCOUNT_PATH, or provide serviceAccountKey.json."
        )
        return False

    try:
        cred = credentials.Certificate(payload)
        firebase_admin.initialize_app(cred)
        _FIREBASE_INIT_ERROR = None
        return True
    except Exception as exc:
        _FIREBASE_INIT_ERROR = f"Firebase init failed: {exc}"
        return False


def verify_firebase_token(id_token):
    """
    Validate Firebase ID token via Firebase Admin SDK.
    Returns a dict compatible with app.py expectations, or None.
    """
    if not id_token:
        return None
    if not _init_firebase():
        return None

    token = str(id_token).strip()
    if token.lower().startswith("bearer "):
        token = token[7:].strip()
    if not token:
        return None

    try:
        decoded = auth.verify_id_token(token)
        return {
            "uid": decoded.get("uid"),
            "email": decoded.get("email"),
            "name": decoded.get("name") or "",
            "email_verified": bool(decoded.get("email_verified", False)),
        }
    except Exception:
        return None


def create_firebase_user(email, password, full_name, phone_number):
    """
    Create user using Firebase Admin SDK.
    """
    if not _init_firebase():
        return {"ok": False, "error": _FIREBASE_INIT_ERROR or "Firebase not initialized.", "uid": None}

    clean_phone = (phone_number or "").strip()
    if clean_phone and not clean_phone.startswith("+"):
        clean_phone = ""

    try:
        kwargs = {
            "email": email,
            "password": password,
            "display_name": full_name or None,
        }
        if clean_phone:
            kwargs["phone_number"] = clean_phone

        user = auth.create_user(**kwargs)
        return {"ok": True, "uid": user.uid}
    except Exception as exc:
        msg = str(exc)
        lowered = msg.lower()
        if "email_exists" in lowered or "already exists" in lowered:
            return {
                "ok": False,
                "error": "A Firebase account already exists for this email.",
                "uid": None,
            }
        if "password should be at least" in lowered or "weak password" in lowered:
            return {
                "ok": False,
                "error": "Firebase password must be at least 6 characters.",
                "uid": None,
            }
        if "invalid phone number" in lowered:
            return {"ok": False, "error": "Invalid phone number format for Firebase.", "uid": None}
        return {"ok": False, "error": f"Firebase signup failed: {msg}", "uid": None}

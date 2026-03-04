import json
import os
from typing import Optional
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

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

    token = str(id_token).strip()
    if token.lower().startswith("bearer "):
        token = token[7:].strip()
    if not token:
        return None

    if _init_firebase():
        try:
            decoded = auth.verify_id_token(token)
            provider = (
                decoded.get("firebase", {}).get("sign_in_provider")
                if isinstance(decoded.get("firebase"), dict)
                else ""
            )
            return {
                "uid": decoded.get("uid"),
                "email": decoded.get("email"),
                "name": decoded.get("name") or "",
                "email_verified": bool(decoded.get("email_verified", False)),
                "provider": provider or "",
            }
        except Exception:
            pass

    return _verify_token_via_rest(token)


def _verify_token_via_rest(token):
    api_key = (
        (os.environ.get("FIREBASE_WEB_API_KEY") or "").strip()
        or "AIzaSyDMw-DDATn4Iq2J1s7Ya9k-NPW7qMCHtw8"
    )
    if not api_key:
        return None
    endpoint = f"https://identitytoolkit.googleapis.com/v1/accounts:lookup?key={api_key}"
    payload = json.dumps({"idToken": token}).encode("utf-8")
    req = Request(
        endpoint,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urlopen(req, timeout=12) as response:
            raw = response.read().decode("utf-8")
        parsed = json.loads(raw)
        users = parsed.get("users") or []
        if not users:
            return None
        user = users[0]
        provider = ""
        provider_info = user.get("providerUserInfo") or []
        if provider_info and isinstance(provider_info[0], dict):
            provider = provider_info[0].get("providerId") or ""
        return {
            "uid": user.get("localId"),
            "email": user.get("email"),
            "name": user.get("displayName") or "",
            "email_verified": bool(user.get("emailVerified", False)),
            "provider": provider or "password",
        }
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError, KeyError, IndexError):
        return None


def create_firebase_user(email, password, full_name, phone_number, disabled=False):
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
            "disabled": bool(disabled),
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


def update_firebase_user(uid, **kwargs):
    if not uid:
        return {"ok": False, "error": "Missing Firebase uid."}
    if not _init_firebase():
        return {"ok": False, "error": _FIREBASE_INIT_ERROR or "Firebase not initialized."}
    try:
        auth.update_user(uid, **kwargs)
        return {"ok": True}
    except Exception as exc:
        return {"ok": False, "error": f"Firebase update failed: {exc}"}


def delete_firebase_user(uid):
    if not uid:
        return {"ok": True}
    if not _init_firebase():
        return {"ok": False, "error": _FIREBASE_INIT_ERROR or "Firebase not initialized."}
    try:
        auth.delete_user(uid)
        return {"ok": True}
    except Exception as exc:
        return {"ok": False, "error": f"Firebase delete failed: {exc}"}

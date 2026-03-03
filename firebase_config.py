import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


FIREBASE_WEB_API_KEY = "AIzaSyClwTmYQaeHZv79EklocgR7xuBd1aixfU8"


def _post_json(url, payload, timeout=20):
    body = json.dumps(payload).encode("utf-8")
    req = Request(
        url,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urlopen(req, timeout=timeout) as response:
        raw = response.read().decode("utf-8")
    return json.loads(raw)


def _parse_firebase_error(exc):
    """Extract Firebase REST error message when available."""
    try:
        raw = exc.read().decode("utf-8")
        payload = json.loads(raw)
        return payload.get("error", {}).get("message") or str(exc)
    except Exception:
        return str(exc)


def verify_firebase_token(id_token):
    """
    Validate Firebase ID token via Identity Toolkit lookup endpoint.
    Returns a dict compatible with app.py expectations, or None.
    """
    if not id_token:
        return None

    url = f"https://identitytoolkit.googleapis.com/v1/accounts:lookup?key={FIREBASE_WEB_API_KEY}"
    try:
        payload = _post_json(url, {"idToken": id_token}, timeout=20)
        users = payload.get("users") or []
        if not users:
            return None
        user = users[0]
        return {
            "uid": user.get("localId"),
            "email": user.get("email"),
            "name": user.get("displayName") or "",
            "email_verified": bool(user.get("emailVerified", False)),
        }
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError):
        return None


def create_firebase_user(email, password, full_name, phone_number):
    """
    Create user using Firebase Auth REST API.
    Works even when firebase_admin SDK is unavailable/outdated.
    """
    signup_url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={FIREBASE_WEB_API_KEY}"
    try:
        signup_payload = {
            "email": email,
            "password": password,
            "returnSecureToken": True,
        }
        created = _post_json(signup_url, signup_payload, timeout=20)
        uid = created.get("localId")
        id_token = created.get("idToken")

        # Best-effort profile update with display name.
        if id_token and full_name:
            update_url = f"https://identitytoolkit.googleapis.com/v1/accounts:update?key={FIREBASE_WEB_API_KEY}"
            update_payload = {
                "idToken": id_token,
                "displayName": full_name,
                "returnSecureToken": False,
            }
            try:
                _post_json(update_url, update_payload, timeout=20)
            except Exception:
                pass

        return {"ok": True, "uid": uid}
    except HTTPError as exc:
        code = _parse_firebase_error(exc)
        if code == "EMAIL_EXISTS":
            return {
                "ok": False,
                "error": "A Firebase account already exists for this email.",
                "uid": None,
            }
        if code == "OPERATION_NOT_ALLOWED":
            return {
                "ok": False,
                "error": "Email/password sign-in is disabled in Firebase Authentication.",
                "uid": None,
            }
        if code == "WEAK_PASSWORD : Password should be at least 6 characters":
            return {
                "ok": False,
                "error": "Firebase password must be at least 6 characters.",
                "uid": None,
            }
        return {"ok": False, "error": f"Firebase signup failed: {code}", "uid": None}
    except (URLError, TimeoutError, json.JSONDecodeError) as exc:
        return {"ok": False, "error": f"Firebase signup failed: {exc}", "uid": None}

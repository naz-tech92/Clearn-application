from flask import Flask, render_template, jsonify, request, session, g, send_from_directory
import json
import os
import re
import html
import base64
import secrets
import smtplib
import sqlite3
import threading
from datetime import datetime, timezone, timedelta
from email.mime.text import MIMEText
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from werkzeug.security import generate_password_hash, check_password_hash
from firebase_config import (
    create_firebase_user,
    delete_firebase_user,
    update_firebase_user,
    verify_firebase_token,
)

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.jinja_env.auto_reload = True
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key-change-me")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
DATABASE_PATH = os.path.join(DATA_DIR, "cyberlearn.db")


def _utc_now_iso():
    return datetime.now(timezone.utc).isoformat()


def init_database():
    os.makedirs(DATA_DIR, exist_ok=True)
    with sqlite3.connect(DATABASE_PATH) as conn:
        conn.executescript(
            """
            PRAGMA foreign_keys = ON;

            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fullname TEXT NOT NULL,
                fullname_normalized TEXT NOT NULL UNIQUE,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                present_skill_career TEXT NOT NULL,
                school TEXT NOT NULL,
                country TEXT NOT NULL,
                phone_number TEXT NOT NULL UNIQUE,
                firebase_uid TEXT,
                auth_provider TEXT NOT NULL DEFAULT 'password',
                email_verified INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS login_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                email TEXT NOT NULL,
                ip_address TEXT,
                user_agent TEXT,
                provider TEXT NOT NULL DEFAULT 'password',
                status TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
            );

            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                email TEXT,
                channel TEXT NOT NULL,
                user_message TEXT NOT NULL,
                assistant_reply TEXT,
                source TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
            );

            CREATE TABLE IF NOT EXISTS pending_verifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL UNIQUE,
                fullname TEXT NOT NULL,
                present_skill_career TEXT NOT NULL,
                school TEXT NOT NULL,
                country TEXT NOT NULL,
                phone_number TEXT NOT NULL,
                password_hash TEXT NOT NULL,
                firebase_uid TEXT NOT NULL,
                code_hash TEXT NOT NULL,
                attempts INTEGER NOT NULL DEFAULT 0,
                expires_at TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
            """
        )
        _ensure_column(conn, "users", "auth_provider", "TEXT NOT NULL DEFAULT 'password'")
        _ensure_column(conn, "users", "email_verified", "INTEGER NOT NULL DEFAULT 0")
        _ensure_column(conn, "login_events", "provider", "TEXT NOT NULL DEFAULT 'password'")
        conn.commit()


def _ensure_column(conn, table_name, column_name, definition):
    existing = conn.execute(f"PRAGMA table_info({table_name})").fetchall()
    if any(row[1] == column_name for row in existing):
        return
    conn.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {definition}")


def get_db():
    db = getattr(g, "_db_conn", None)
    if db is None:
        db = sqlite3.connect(DATABASE_PATH)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA foreign_keys = ON")
        g._db_conn = db
    return db


@app.teardown_appcontext
def close_db_connection(error):
    db = getattr(g, "_db_conn", None)
    if db is not None:
        db.close()


def get_user_by_email(email):
    return get_db().execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()


def log_login_event(email, status, user_id=None, provider="password"):
    db = get_db()
    db.execute(
        """
        INSERT INTO login_events (user_id, email, ip_address, user_agent, provider, status, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            user_id,
            email,
            request.headers.get("X-Forwarded-For", request.remote_addr),
            (request.headers.get("User-Agent") or "")[:350],
            (provider or "password")[:60],
            status,
            _utc_now_iso(),
        ),
    )
    db.commit()


def log_message(email, user_message, assistant_reply, source):
    db = get_db()
    user = get_user_by_email(email) if email else None
    db.execute(
        """
        INSERT INTO messages (user_id, email, channel, user_message, assistant_reply, source, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            user["id"] if user else None,
            email or None,
            "ai_assist",
            user_message,
            assistant_reply,
            source,
            _utc_now_iso(),
        ),
    )
    db.commit()


def _generate_verification_code():
    return f"{secrets.randbelow(1000000):06d}"


def _verification_expiry_iso(minutes=15):
    return (datetime.now(timezone.utc) + timedelta(minutes=minutes)).isoformat()


def _store_pending_verification(
    email,
    fullname,
    present_skill,
    school,
    country,
    phone_number,
    password,
    firebase_uid,
    code,
):
    db = get_db()
    db.execute(
        """
        INSERT INTO pending_verifications (
            email, fullname, present_skill_career, school, country,
            phone_number, password_hash, firebase_uid, code_hash, attempts, expires_at, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 0, ?, ?)
        ON CONFLICT(email) DO UPDATE SET
            fullname=excluded.fullname,
            present_skill_career=excluded.present_skill_career,
            school=excluded.school,
            country=excluded.country,
            phone_number=excluded.phone_number,
            password_hash=excluded.password_hash,
            firebase_uid=excluded.firebase_uid,
            code_hash=excluded.code_hash,
            attempts=0,
            expires_at=excluded.expires_at,
            created_at=excluded.created_at
        """,
        (
            email,
            fullname,
            present_skill,
            school,
            country,
            phone_number,
            generate_password_hash(password),
            firebase_uid,
            generate_password_hash(code),
            _verification_expiry_iso(),
            _utc_now_iso(),
        ),
    )
    db.commit()


def _get_pending_verification(email):
    return get_db().execute(
        "SELECT * FROM pending_verifications WHERE email = ?",
        ((email or "").strip().lower(),),
    ).fetchone()


def _delete_pending_verification(email):
    get_db().execute("DELETE FROM pending_verifications WHERE email = ?", ((email or "").strip().lower(),))
    get_db().commit()


def _refresh_pending_verification_code(email, code):
    db = get_db()
    db.execute(
        """
        UPDATE pending_verifications
        SET code_hash = ?, attempts = 0, expires_at = ?, created_at = ?
        WHERE email = ?
        """,
        (generate_password_hash(code), _verification_expiry_iso(), _utc_now_iso(), (email or "").strip().lower()),
    )
    db.commit()

def _local_firebase_project_id():
    env_project_id = (os.environ.get("FIREBASE_WEB_PROJECT_ID") or os.environ.get("FIREBASE_PROJECT_ID") or "").strip()
    if env_project_id:
        return env_project_id

    local_key_path = os.path.join(os.path.dirname(__file__), "serviceAccountKey.json")
    if not os.path.exists(local_key_path):
        return ""
    try:
        with open(local_key_path, "r", encoding="utf-8") as fh:
            payload = json.load(fh)
        return (payload.get("project_id") or "clearn-96c81").strip()
    except Exception:
        return ""


def build_firebase_web_config():
    def _compact(value):
        return "".join(str(value or "").split())

    def _clean(value):
        return str(value or "").strip()

    project_id = _local_firebase_project_id()
    if not project_id:
        project_id = "clearn-96c81"
    project_id = _compact(project_id)

    default_config = {
        "apiKey": "AIzaSyDMw-DDATn4Iq2J1s7Ya9k-NPW7qMCHtw8",
        "authDomain": "clearn-96c81.firebaseapp.com",
        "projectId": "clearn-96c81",
        "storageBucket": "clearn-96c81.firebasestorage.app",
        "messagingSenderId": "623690790532",
        "appId": "1:623690790532:web:bfb5431f7edf98ed9334d1",
        "measurementId": "G-HWPD3DRHDZ",
    }

    auth_domain = _clean(os.environ.get("FIREBASE_WEB_AUTH_DOMAIN"))
    if not auth_domain and project_id:
        auth_domain = f"{project_id}.firebaseapp.com"
    auth_domain = _compact(auth_domain)

    storage_bucket = _clean(os.environ.get("FIREBASE_WEB_STORAGE_BUCKET"))
    if not storage_bucket and project_id:
        storage_bucket = f"{project_id}.firebasestorage.app"
    storage_bucket = _compact(storage_bucket)

    return {
        "apiKey": _compact(os.environ.get("FIREBASE_WEB_API_KEY") or default_config["apiKey"]),
        "authDomain": auth_domain or default_config["authDomain"],
        "projectId": project_id,
        "storageBucket": storage_bucket or default_config["storageBucket"],
        "messagingSenderId": _compact(
            os.environ.get("FIREBASE_WEB_MESSAGING_SENDER_ID")
            or default_config["messagingSenderId"]
        ),
        "appId": _compact(os.environ.get("FIREBASE_WEB_APP_ID") or default_config["appId"]),
        "measurementId": _compact(
            os.environ.get("FIREBASE_WEB_MEASUREMENT_ID")
            or default_config["measurementId"]
        ),
    }

@app.route("/protected", methods=["POST"])
def protected():
    id_token = request.headers.get("Authorization")

    if not id_token:
        return jsonify({"error": "Missing token"}), 401

    decoded_token = verify_firebase_token(id_token)

    if not decoded_token:
        return jsonify({"error": "Invalid token"}), 401

    if not decoded_token.get("email_verified"):
        return jsonify({"error": "Email not verified"}), 403

    return jsonify({
        "message": "Access granted",
        "email": decoded_token["email"]
    })


@app.route("/api/firebase/web-config")
def firebase_web_config():
    """Expose Firebase Web SDK config from environment/service-account project."""
    config = build_firebase_web_config()
    missing = [k for k in ("apiKey", "authDomain", "projectId", "appId") if not config.get(k)]
    if missing:
        return jsonify(
            {
                "ok": False,
                "message": (
                    "Missing Firebase web config values: "
                    f"{', '.join(missing)}. Set FIREBASE_WEB_API_KEY, FIREBASE_WEB_APP_ID, "
                    "FIREBASE_WEB_MESSAGING_SENDER_ID, and optional web config vars in environment."
                ),
            }
        ), 500
    return jsonify({"ok": True, "config": config})


@app.route("/api/auth/firebase-session", methods=["POST"])
def firebase_session_login():
    """Create server session from Firebase ID token."""
    auth_header = (request.headers.get("Authorization") or "").strip()
    token = ""
    if auth_header.lower().startswith("bearer "):
        token = auth_header[7:].strip()
    if not token:
        data = request.get_json(silent=True) or {}
        token = (data.get("idToken") or "").strip()

    if not token:
        return jsonify({"ok": False, "message": "Missing Firebase ID token."}), 401

    decoded = verify_firebase_token(token)
    if not decoded:
        return jsonify({"ok": False, "message": "Invalid Firebase ID token."}), 401

    email = (decoded.get("email") or "").strip().lower()
    if not email:
        return jsonify({"ok": False, "message": "Firebase account has no email."}), 400

    provider = (decoded.get("provider") or "password").strip() or "password"
    if provider == "password" and not decoded.get("email_verified"):
        log_login_event(email, "failed_unverified_email", provider=provider)
        return jsonify({"ok": False, "message": "Email not verified. Complete email verification first."}), 403
    profile = get_user_by_email(email)
    session["user_email"] = email
    session["user_fullname"] = (
        (profile["fullname"] if profile else None) or decoded.get("name") or email.split("@")[0]
    )
    if profile:
        log_login_event(email, "success", profile["id"], provider=provider)
    else:
        log_login_event(email, "success_unlinked_profile", None, provider=provider)
    return jsonify({"ok": True, "message": f"Welcome back, {session['user_fullname']}.", "redirectTo": "/"})





    

FULL_NAME_REGEX = re.compile(r"^[A-Z][A-Za-z'-]*(\s+[A-Z][A-Za-z'-]*)+$")
EMAIL_REGEX = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
PHONE_REGEX = re.compile(r"^\+?[0-9]{7,15}$")

WINDOWS_USER_ENV = None
DATA_REFRESH_HOURS = 72
DATA_REFRESH_INTERVAL = timedelta(hours=DATA_REFRESH_HOURS)
DATA_CACHE_LOCK = threading.Lock()
DATA_CACHE = {}


def _load_windows_user_env():
    """Load persistent user environment variables from Windows registry (HKCU\\Environment)."""
    global WINDOWS_USER_ENV
    if WINDOWS_USER_ENV is not None:
        return WINDOWS_USER_ENV

    WINDOWS_USER_ENV = {}
    if os.name != "nt":
        return WINDOWS_USER_ENV

    try:
        import winreg

        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as key:
            idx = 0
            while True:
                try:
                    name, value, _ = winreg.EnumValue(key, idx)
                    WINDOWS_USER_ENV[name] = str(value)
                    idx += 1
                except OSError:
                    break
    except Exception:
        # Keep empty cache on any failure; normal os.environ lookup still works.
        pass
    return WINDOWS_USER_ENV


def get_config_var(*names):
    """
    Read config var from process env first, then persistent Windows user env.
    Accepts multiple candidate names and returns first non-empty value.
    """
    for name in names:
        value = os.environ.get(name)
        if value and str(value).strip():
            return str(value).strip()

    win_env = _load_windows_user_env()
    for name in names:
        value = win_env.get(name)
        if value and str(value).strip():
            return str(value).strip()
    return None


init_database()


def normalize_phone_number(value):
    """Normalize phone number for consistent uniqueness checks."""
    raw = (value or "").strip()
    if raw.startswith("+"):
        return "+" + re.sub(r"\D", "", raw[1:])
    return re.sub(r"\D", "", raw)


def load_topics():
    """Load topics from JSON file with 72-hour cache refresh."""
    return _load_json_with_refresh("topics", "data/topics.json", [])


def load_countries():
    """Load countries from JSON file with 72-hour cache refresh."""
    return _load_json_with_refresh("countries", "data/countries.json", {"countries": {}})


def _read_json_file(path, fallback):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return fallback


def _load_json_with_refresh(cache_key, path, fallback):
    now = datetime.now(timezone.utc)
    with DATA_CACHE_LOCK:
        entry = DATA_CACHE.get(cache_key)
        if entry:
            refreshed_at = entry.get("refreshed_at")
            if isinstance(refreshed_at, datetime) and (now - refreshed_at) < DATA_REFRESH_INTERVAL:
                return entry.get("data", fallback)

        data = _read_json_file(path, fallback)
        DATA_CACHE[cache_key] = {"data": data, "refreshed_at": now}
        return data


def _get_refresh_state():
    now = datetime.now(timezone.utc)
    with DATA_CACHE_LOCK:
        refreshed_times = [
            entry.get("refreshed_at")
            for entry in DATA_CACHE.values()
            if isinstance(entry.get("refreshed_at"), datetime)
        ]

    last_updated = max(refreshed_times) if refreshed_times else now
    next_refresh = last_updated + DATA_REFRESH_INTERVAL
    return last_updated, next_refresh


TECH_SKILLS = {
    "cybersecurity",
    "data_science",
    "cloud_computing",
    "ai_machine_learning",
    "software_engineering",
    "networking",
    "devops",
}
HEALTH_SKILLS = {"nursing", "public_health", "medical_laboratory_science"}
BUSINESS_SKILLS = {"accounting", "digital_marketing", "international_business"}

RECOMMENDED_SCHOOL_CATALOG = {
    "default": {
        "technology": [
            {
                "name": "Massachusetts Institute of Technology (MIT)",
                "brief_details": "Leading engineering and computing institution with strong AI, systems, and security labs.",
                "year_founded": "1861",
                "founded_by": "William Barton Rogers and the Commonwealth of Massachusetts",
                "goals_focus": "Research-led technology education, innovation, and entrepreneurship.",
                "location": "Cambridge, Massachusetts, USA",
                "website": "https://web.mit.edu/",
            },
            {
                "name": "Stanford University",
                "brief_details": "Top university with deep strengths in software, data, startups, and applied research.",
                "year_founded": "1885",
                "founded_by": "Leland and Jane Stanford",
                "goals_focus": "Advanced research, product innovation, and leadership in technology.",
                "location": "Stanford, California, USA",
                "website": "https://www.stanford.edu/",
            },
        ],
        "health": [
            {
                "name": "Johns Hopkins University",
                "brief_details": "Globally recognized for medicine, nursing, and public health training.",
                "year_founded": "1876",
                "founded_by": "Johns Hopkins (philanthropist)",
                "goals_focus": "Evidence-based healthcare education, research, and patient outcomes.",
                "location": "Baltimore, Maryland, USA",
                "website": "https://www.jhu.edu/",
            },
            {
                "name": "Karolinska Institute",
                "brief_details": "Major medical university known for biomedical research and clinical science.",
                "year_founded": "1810",
                "founded_by": "King Karl XIII of Sweden",
                "goals_focus": "Medical discovery, professional training, and public health advancement.",
                "location": "Stockholm, Sweden",
                "website": "https://ki.se/en",
            },
        ],
        "business": [
            {
                "name": "The Wharton School, University of Pennsylvania",
                "brief_details": "Premier business school for finance, strategy, and leadership development.",
                "year_founded": "1881",
                "founded_by": "Joseph Wharton",
                "goals_focus": "Business analytics, executive leadership, and global management.",
                "location": "Philadelphia, Pennsylvania, USA",
                "website": "https://www.wharton.upenn.edu/",
            },
            {
                "name": "London Business School",
                "brief_details": "Top global business school with strong international management orientation.",
                "year_founded": "1964",
                "founded_by": "University of London",
                "goals_focus": "Global leadership, entrepreneurship, and data-driven business practice.",
                "location": "London, United Kingdom",
                "website": "https://www.london.edu/",
            },
        ],
    },
    "cameroon": {
        "technology": [
            {
                "name": "University of Buea",
                "brief_details": "Strong ICT and computer science programs with industry-oriented training.",
                "year_founded": "1993",
                "founded_by": "Government of Cameroon (state university reform)",
                "goals_focus": "Applied technology education and professional skills for national development.",
                "location": "Buea, South West Region, Cameroon",
                "website": "https://www.ubuea.cm/",
            },
            {
                "name": "University of Yaounde I",
                "brief_details": "Major science and engineering institution with broad computing pathways.",
                "year_founded": "1993",
                "founded_by": "Government of Cameroon (from the former University of Yaounde)",
                "goals_focus": "Research, digital skills capacity, and innovation in science and technology.",
                "location": "Yaounde, Centre Region, Cameroon",
                "website": "https://www.uy1.uninet.cm/",
            },
            {
                "name": "National Advanced School of Engineering Yaounde (ENSPY)",
                "brief_details": "Top engineering school with strong computing, networks, and systems programs.",
                "year_founded": "1961",
                "founded_by": "Government of Cameroon",
                "goals_focus": "Engineering excellence, digital infrastructure skills, and applied innovation.",
                "location": "Yaounde, Centre Region, Cameroon",
                "website": "https://polytechnique.cm/",
            },
            {
                "name": "St Louise University Institute of Cameroon",
                "brief_details": "Private institute offering practical, career-focused ICT and professional programs.",
                "year_founded": "2000s",
                "founded_by": "Private educational promoters in Cameroon",
                "goals_focus": "Applied digital skills, employability, and industry-ready training.",
                "location": "Douala, Littoral Region, Cameroon",
                "website": "https://stlouiseuniversityinstitute.com/",
            },
        ],
        "health": [
            {
                "name": "University of Yaounde I - Faculty of Medicine and Biomedical Sciences",
                "brief_details": "Core center for medical and biomedical training in Cameroon.",
                "year_founded": "1969 (faculty roots), modern university structure from 1993",
                "founded_by": "Government of Cameroon",
                "goals_focus": "Medical training, diagnostics, biomedical research, and public health impact.",
                "location": "Yaounde, Centre Region, Cameroon",
                "website": "https://www.uy1.uninet.cm/",
            },
            {
                "name": "University of Buea - Faculty of Health Sciences",
                "brief_details": "Offers programs in nursing, public health, and allied health fields.",
                "year_founded": "1993",
                "founded_by": "Government of Cameroon",
                "goals_focus": "Healthcare workforce development and community health improvement.",
                "location": "Buea, South West Region, Cameroon",
                "website": "https://www.ubuea.cm/",
            },
            {
                "name": "St Louise University Institute of Cameroon",
                "brief_details": "Private health-focused institute in Cameroon supporting nursing and biomedical training.",
                "year_founded": "2000s",
                "founded_by": "Private educational promoters in Cameroon",
                "goals_focus": "Professional healthcare training, practical clinical skills, and community service.",
                "location": "Douala, Littoral Region, Cameroon",
                "website": "https://stlouiseuniversityinstitute.com/",
            },
            {
                "name": "Universite des Montagnes",
                "brief_details": "Recognized medical and health sciences institution with strong practical training.",
                "year_founded": "2000",
                "founded_by": "Academic and medical founders in Cameroon",
                "goals_focus": "Medical education, nursing pathways, and health service impact.",
                "location": "Bangangte, West Region, Cameroon",
                "website": "https://udm.aed-cm.org/",
            },
        ],
        "business": [
            {
                "name": "University of Douala",
                "brief_details": "Key institution for management, accounting, and business practice training.",
                "year_founded": "1993",
                "founded_by": "Government of Cameroon",
                "goals_focus": "Professional business education, entrepreneurship, and economic development.",
                "location": "Douala, Littoral Region, Cameroon",
                "website": "https://www.univ-douala.com/",
            },
            {
                "name": "Catholic University of Central Africa (UCAC)",
                "brief_details": "Private higher institution with recognized business and management programs.",
                "year_founded": "1989",
                "founded_by": "Episcopal Conference of Cameroon",
                "goals_focus": "Ethical leadership, managerial excellence, and responsible enterprise.",
                "location": "Yaounde, Centre Region, Cameroon",
                "website": "https://www.ucac-icy.net/",
            },
            {
                "name": "Pan African Institute for Development - West Africa (PAID-WA)",
                "brief_details": "Professional institute with business, management, and development-focused programs.",
                "year_founded": "1965",
                "founded_by": "Pan-African educational development initiative",
                "goals_focus": "Management capacity, entrepreneurship, and practical business leadership.",
                "location": "Buea, South West Region, Cameroon",
                "website": "https://www.paidafrica.org/",
            },
            {
                "name": "St Louise University Institute of Cameroon",
                "brief_details": "Private institute with business-oriented programs and professional training pathways.",
                "year_founded": "2000s",
                "founded_by": "Private educational promoters in Cameroon",
                "goals_focus": "Business fundamentals, entrepreneurship, and practical workplace readiness.",
                "location": "Douala, Littoral Region, Cameroon",
                "website": "https://stlouiseuniversityinstitute.com/",
            },
        ],
    },
}


def infer_skill_family(skill_name):
    if skill_name in TECH_SKILLS:
        return "technology"
    if skill_name in HEALTH_SKILLS:
        return "health"
    if skill_name in BUSINESS_SKILLS:
        return "business"
    return "technology"


def get_recommended_schools(skill_name, country_key):
    """Return curated schools by country and skill family for country skill detail pages."""
    family = infer_skill_family(skill_name)
    country_catalog = RECOMMENDED_SCHOOL_CATALOG.get(country_key, {})
    schools = country_catalog.get(family)
    if schools:
        return schools
    return RECOMMENDED_SCHOOL_CATALOG["default"].get(family, [])


def format_skill_name(skill_key):
    """Convert a skill key like 'ai_machine_learning' into a display label."""
    words = (skill_key or "").split("_")
    replacements = {"ai": "AI", "ml": "ML"}
    return " ".join(replacements.get(word.lower(), word.capitalize()) for word in words if word)


def estimate_salary_range(demand_level, country_name):
    """MVP salary estimate buckets based on demand and market context."""
    demand = (demand_level or "").lower()
    country = (country_name or "").lower()

    if "very high" in demand:
        return "$90k-$180k"
    if "high" in demand:
        return "$65k-$130k"
    if "growing" in demand:
        return "$40k-$95k"
    if "emerging" in demand:
        return "$30k-$75k"

    if any(k in country for k in ["united states", "singapore", "uk", "canada"]):
        return "$60k-$120k"
    return "$35k-$85k"


def infer_degree_bucket(required_education):
    """Classify education text into a normalized degree filter value."""
    edu = (required_education or "").lower()
    if "phd" in edu or "doctor" in edu:
        return "PhD"
    if "master" in edu or "mph" in edu or "mba" in edu:
        return "Masters"
    if "bachelor" in edu:
        return "Bachelors"
    if "associate" in edu or "diploma" in edu or "certificate" in edu:
        return "Certificate/Diploma"
    return "Any"


def extract_universities(references):
    """Extract candidate university/institute names from references for search/filtering."""
    universities = []
    for ref in references or []:
        ref_text = str(ref).strip()
        lowered = ref_text.lower()
        if any(token in lowered for token in ["university", "institute", "college", "mit", "stanford", "berkeley"]):
            universities.append(ref_text)
    return universities[:5]


def build_search_index():
    """Build universal search index from countries and skills data."""
    countries_data = load_countries().get("countries", {})
    records = []
    seen = set()

    for country_key, country_data in countries_data.items():
        country_name = country_data.get("name", country_key.replace("_", " ").title())
        for skill_key, skill_data in country_data.get("skills", {}).items():
            uid = f"{country_key}:{skill_key}"
            if uid in seen:
                continue
            seen.add(uid)

            required_education = skill_data.get("required_education", "")
            demand_level = skill_data.get("skill_demand_level", "")
            references = skill_data.get("references", [])
            universities = extract_universities(references)
            records.append(
                {
                    "id": uid,
                    "skillKey": skill_key,
                    "skillName": format_skill_name(skill_key),
                    "countryKey": country_key,
                    "countryName": country_name,
                    "demandLevel": demand_level,
                    "degree": infer_degree_bucket(required_education),
                    "requiredEducation": required_education,
                    "salaryRange": estimate_salary_range(demand_level, country_name),
                    "universities": universities,
                    "url": f"/skill/{skill_key}",
                }
            )
    return records


def get_site_grounded_ai_reply(message):
    """Fallback assistant response constrained to CLearn site capabilities/content."""
    lower_message = (message or "").strip().lower()

    if re.search(r"(draw|generate image|make image|create image|illustration|poster|logo)", lower_message):
        return (
            "I can generate a basic preview image for your idea in this chat. "
            "Tell me the style and topic, for example: 'generate image for cybersecurity roadmap'."
        )

    if re.search(r"(category|categories|skill|skills|career path|choose)", lower_message):
        return (
            "Start with /category to compare Technology, Healthcare, and Business tracks. "
            "Open a skill page to view overview, education pathways, careers, global opportunities, and references."
        )

    if re.search(r"(country|cameroon|usa|canada|germany|uk|singapore|australia|uae|abroad)", lower_message):
        return (
            "Use each skill page's Global Opportunities section and country detail pages "
            "to compare demand, required education, and pathway differences by country."
        )

    if re.search(r"(resource|book|course|certification|training)", lower_message):
        return (
            "Check /resources for tools, books, and references, then open the selected skill page's "
            "References & Learning Path section for curated next steps."
        )

    if re.search(r"(school|university|college|where to study)", lower_message):
        return (
            "Open a skill > country page to review recommended schools and institution details. "
            "You can compare countries first from /category before choosing where to study."
        )

    if re.search(r"(new|beginner|where do i start|how to start|how do i use)", lower_message):
        return (
            "Quick path: 1) /category 2) pick a skill 3) read overview and education section "
            "4) compare countries 5) use /resources for tools and references."
        )

    if re.search(r"(visa|immigration|work permit|relocate|abroad)", lower_message):
        return (
            "Use country pages to compare pathways and demand by location, then validate official immigration sites. "
            "I can help you structure a country-by-country checklist."
        )

    if re.search(r"(cv|resume|interview|job application|cover letter)", lower_message):
        return (
            "I can help you draft a beginner CV and interview prep plan based on your selected skill. "
            "Share your target role and country."
        )

    return (
        "I can help using CLearn content. Ask about skills, countries, education levels, resources, "
        "or how to navigate pages like /category, /resources, /topics, and skill pages."
    )


def _should_generate_basic_image(message):
    text = (message or "").strip().lower()
    return bool(re.search(r"(draw|generate image|make image|create image|illustration|poster|logo)", text))


def _build_basic_image_data_url(prompt):
    clean = re.sub(r"\s+", " ", (prompt or "").strip())[:120] or "CLearn Visual"
    safe = html.escape(clean)
    subtitle = html.escape("AI basic preview")
    svg = f"""<svg xmlns='http://www.w3.org/2000/svg' width='960' height='540' viewBox='0 0 960 540'>
<defs>
<linearGradient id='bg' x1='0' y1='0' x2='1' y2='1'>
<stop offset='0%' stop-color='#0ea5e9'/>
<stop offset='55%' stop-color='#22d3ee'/>
<stop offset='100%' stop-color='#38bdf8'/>
</linearGradient>
</defs>
<rect width='960' height='540' fill='url(#bg)'/>
<circle cx='790' cy='120' r='84' fill='rgba(255,255,255,0.22)'/>
<circle cx='180' cy='430' r='110' fill='rgba(2,132,199,0.28)'/>
<rect x='72' y='88' rx='22' ry='22' width='816' height='364' fill='rgba(2,23,44,0.28)'/>
<text x='100' y='180' fill='#f8fafc' font-size='28' font-family='Segoe UI, Arial, sans-serif' font-weight='700'>CLearn Concept</text>
<text x='100' y='228' fill='#e2e8f0' font-size='22' font-family='Segoe UI, Arial, sans-serif'>{safe}</text>
<text x='100' y='272' fill='#dbeafe' font-size='18' font-family='Segoe UI, Arial, sans-serif'>{subtitle}</text>
</svg>"""
    encoded = base64.b64encode(svg.encode("utf-8")).decode("ascii")
    return f"data:image/svg+xml;base64,{encoded}"


def call_external_ai_assistant(message):
    """
    Call configurable chat-completions API.
    Expected response shape: {'choices': [{'message': {'content': '...'}}]}.
    """
    api_key = get_config_var("REAL_API_KEY", "AI_ASSIST_API_KEY", "OPENAI_API_KEY")
    if not api_key:
        return None

    endpoint = get_config_var("AI_ASSIST_API_URL") or "https://api.openai.com/v1/chat/completions"
    model = get_config_var("AI_ASSIST_MODEL") or "gpt-4o-mini"
    timeout_seconds = int(get_config_var("AI_ASSIST_TIMEOUT_SECONDS") or "20")

    system_prompt = (
        "You are CLearn AI assistant. Answer using CLearn site scope first: categories, skills, country comparison, "
        "education pathways, resources, and navigation. "
        "Keep responses concise, factual, and user-oriented. "
        "If unsure, suggest where in CLearn to check."
    )
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": message},
        ],
        "temperature": 0.3,
        "max_tokens": 350,
    }
    body = json.dumps(payload).encode("utf-8")

    req = Request(
        endpoint,
        data=body,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )

    try:
        with urlopen(req, timeout=timeout_seconds) as response:
            raw = response.read().decode("utf-8")
        parsed = json.loads(raw)
        return (
            parsed.get("choices", [{}])[0]
            .get("message", {})
            .get("content", "")
            .strip()
        )
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError, KeyError, IndexError):
        return None


def send_email(to_email, subject, body):
    """Send email using SMTP credentials from environment variables."""
    smtp_host = get_config_var("SMTP_HOST") or "smtp.gmail.com"
    smtp_port = int(get_config_var("SMTP_PORT") or "587")
    smtp_user = get_config_var("SMTP_USER", "GMAIL_USER")
    smtp_password = get_config_var("SMTP_PASS", "GMAIL_APP_PASSWORD")
    smtp_from = get_config_var("SMTP_FROM") or smtp_user or "no-reply@cyberlearn.local"
    smtp_use_tls = (get_config_var("SMTP_USE_TLS") or "true").lower() == "true"

    if not smtp_user or not smtp_password:
        return (
            False,
            "Email service is not configured. For Google SMTP, set GMAIL_USER and "
            "GMAIL_APP_PASSWORD (or SMTP_USER/SMTP_PASS), then retry signup.",
        )

    message = MIMEText(body, "plain", "utf-8")
    message["Subject"] = subject
    message["From"] = smtp_from
    message["To"] = to_email

    try:
        with smtplib.SMTP(smtp_host, smtp_port, timeout=10) as server:
            if smtp_use_tls:
                server.starttls()
            server.login(smtp_user, smtp_password)
            server.sendmail(smtp_from, [to_email], message.as_string())
        return True, None
    except Exception as exc:
        return False, f"Failed to send email: {exc}"


def validate_signup_payload(
    fullname,
    email,
    password,
    confirm_password,
    present_skill,
    school,
    country,
    phone_number,
):
    """Validate signup payload against required rules."""
    if not FULL_NAME_REGEX.match(fullname.strip()):
        return False, "Enter at least two names, each starting with a capital letter."
    if not EMAIL_REGEX.match(email.strip()):
        return False, "Enter a valid email address."
    if len(password) < 8:
        return False, "Password must be at least 8 characters."
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter."
    if not re.search(r"\d", password):
        return False, "Password must contain at least one number."
    if not re.search(r"[!@#$%]", password):
        return False, "Password must contain at least one special character (!@#$%)."
    if password != confirm_password:
        return False, "Confirm password must match password."
    if len(present_skill.strip()) < 2:
        return False, "Present skill/career is required."
    if len(school.strip()) < 2:
        return False, "School is required."
    if len(country.strip()) < 2:
        return False, "Country is required."
    if not PHONE_REGEX.match(phone_number.strip()):
        return False, "Enter a valid phone number (7-15 digits, optional leading +)."
    return True, None


def find_duplicate_signup_field(fullname, email, phone_number, password):
    """
    Enforce uniqueness for email, phone, full name, and password.
    """
    name_key = fullname.strip().lower()
    email_key = email.strip().lower()
    phone_key = normalize_phone_number(phone_number)

    db = get_db()
    if db.execute("SELECT 1 FROM users WHERE email = ? LIMIT 1", (email_key,)).fetchone():
        return "This email is already in use."
    if db.execute("SELECT 1 FROM users WHERE phone_number = ? LIMIT 1", (phone_key,)).fetchone():
        return "This phone number is already in use."
    if db.execute("SELECT 1 FROM users WHERE fullname_normalized = ? LIMIT 1", (name_key,)).fetchone():
        return "This full name is already in use."

    hashes = db.execute("SELECT password_hash FROM users").fetchall()
    for row in hashes:
        if check_password_hash(row["password_hash"], password):
            return "This password is already in use. Please choose a different password."

    return None


@app.route("/")
def home():
    """Home page"""
    return render_template("index.html")


@app.route("/images/<path:filename>")
def project_images(filename):
    """Serve project image assets from the local images folder."""
    return send_from_directory(os.path.join(BASE_DIR, "images"), filename)


@app.route("/topics")
def topics():
    """Topics listing page"""
    return render_template("topics.html")


@app.route("/topic/<int:topic_id>")
def topic_detail(topic_id):
    """Individual topic learning page"""
    topics_data = load_topics()
    topic = next((t for t in topics_data if t["id"] == topic_id), None)
    if not topic:
        return render_template("index.html"), 404
    return render_template("topic.html", topic=topic)


@app.route("/about")
def about():
    """About page"""
    return render_template("about.html")


@app.route("/resources")
def resources():
    """Resources page"""
    return render_template("resources.html")


@app.route("/contact")
def contact():
    """Contact page"""
    return render_template("contact.html")


@app.route("/privacy_policy")
def privacy_policy():
    """Privacy Policy page"""
    return render_template("privacy_policy.html")


@app.route("/terms_of_service")
def terms_of_service():
    """Terms of Service page"""
    return render_template("terms_of_service.html")


@app.route("/category")
def category():
    """Category page"""
    return render_template("category.html")


@app.route("/skill/<skill_name>")
def skill_detail(skill_name):
    """Individual skill page"""
    return render_template(f"skill_{skill_name}.html")


@app.route("/skill/<skill_name>/country/<country_name>")
def country_skill_detail(skill_name, country_name):
    """Country-specific skill details page"""
    countries_data = load_countries()
    country = countries_data.get("countries", {}).get(country_name)
    if not country or skill_name not in country.get("skills", {}):
        return render_template("index.html"), 404

    skill_data = country["skills"][skill_name]
    recommended_schools = get_recommended_schools(skill_name, country_name)
    return render_template(
        "country_skill_detail.html",
        country=country,
        skill_name=skill_name,
        skill_data=skill_data,
        recommended_schools=recommended_schools,
    )


@app.route("/country/<country_name>")
def country_detail(country_name):
    """Country page showing all available skills"""
    countries_data = load_countries()
    country = countries_data.get("countries", {}).get(country_name)
    if not country:
        return render_template("index.html"), 404

    return render_template("country_detail.html", country=country)


@app.route("/education/<level>")
def education_level(level):
    """Educational level page showing skills requiring that level"""
    countries_data = load_countries()
    skills_by_level = {}

    # Map educational levels to skills
    for country_name, country_data in countries_data.get("countries", {}).items():
        for skill_name, skill_data in country_data.get("skills", {}).items():
            education = skill_data.get("required_education", "").lower()
            compact_level = level.lower().replace(" ", "")
            if level.lower() in education or compact_level in education.replace(" ", ""):
                if level not in skills_by_level:
                    skills_by_level[level] = []
                skills_by_level[level].append(
                    {
                        "skill_name": skill_name,
                        "country": country_data,
                        "skill_data": skill_data,
                    }
                )

    if not skills_by_level.get(level):
        return render_template("index.html"), 404

    return render_template("education_level.html", level=level, skills=skills_by_level[level])


@app.route("/login")
def login():
    """Login page"""
    return render_template("login.html")


@app.route("/signup")
def signup():
    """Signup page"""
    return render_template("signup.html")


@app.route("/api/signup", methods=["POST"])
def create_signup():
    """Start signup: create disabled Firebase account and send email verification code."""
    data = request.get_json(silent=True) or {}
    fullname = (data.get("fullname") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    confirm_password = data.get("confirmPassword") or ""
    present_skill = (data.get("presentSkillCareer") or "").strip()
    school = (data.get("school") or "").strip()
    country = (data.get("country") or "").strip()
    phone_number = normalize_phone_number((data.get("phoneNumber") or "").strip())

    is_valid, validation_error = validate_signup_payload(
        fullname,
        email,
        password,
        confirm_password,
        present_skill,
        school,
        country,
        phone_number,
    )
    if not is_valid:
        return jsonify({"ok": False, "message": validation_error}), 400

    existing_pending = _get_pending_verification(email)
    if existing_pending:
        expires_at = datetime.fromisoformat(existing_pending["expires_at"])
        if datetime.now(timezone.utc) > expires_at:
            delete_firebase_user(existing_pending["firebase_uid"])
            _delete_pending_verification(email)
        else:
            code = _generate_verification_code()
            _refresh_pending_verification_code(email, code)
            email_sent, email_error = send_email(
                email,
                "CLearn Verification Code (Resent)",
                (
                    f"Hello {existing_pending['fullname']},\n\n"
                    f"Your new CLearn verification code is: {code}\n"
                    "This code expires in 15 minutes."
                ),
            )
            if not email_sent:
                return jsonify({"ok": False, "message": email_error or "Could not resend verification email."}), 500
            return jsonify(
                {
                    "ok": True,
                    "requiresVerification": True,
                    "email": email,
                    "message": "A new verification code was sent to your email.",
                }
            )

    duplicate_error = find_duplicate_signup_field(fullname, email, phone_number, password)
    if duplicate_error:
        return jsonify({"ok": False, "message": duplicate_error}), 409

    firebase_result = create_firebase_user(email, password, fullname, phone_number, disabled=True)
    if not firebase_result.get("ok"):
        message = firebase_result.get("error") or "Unable to create Firebase account."
        status = 409 if "already exists" in message.lower() else 500
        return jsonify({"ok": False, "message": message}), status

    verification_code = _generate_verification_code()
    _store_pending_verification(
        email=email,
        fullname=fullname,
        present_skill=present_skill,
        school=school,
        country=country,
        phone_number=phone_number,
        password=password,
        firebase_uid=firebase_result.get("uid"),
        code=verification_code,
    )

    email_sent, email_error = send_email(
        email,
        "CLearn Email Verification Code",
        (
            f"Hello {fullname},\n\n"
            f"Your CLearn verification code is: {verification_code}\n"
            "This code expires in 15 minutes.\n\n"
            "If you did not request this signup, you can ignore this email."
        ),
    )
    if not email_sent:
        delete_firebase_user(firebase_result.get("uid"))
        _delete_pending_verification(email)
        return jsonify({"ok": False, "message": email_error or "Could not send verification email."}), 500

    return jsonify(
        {
            "ok": True,
            "requiresVerification": True,
            "email": email,
            "message": "Verification code sent. Please check your email and complete verification.",
        }
    )


@app.route("/api/signup/verify", methods=["POST"])
def verify_signup_code():
    """Finalize signup by verifying one-time code."""
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    code = (data.get("code") or "").strip()

    if not EMAIL_REGEX.match(email):
        return jsonify({"ok": False, "message": "Enter a valid email address."}), 400
    if not re.fullmatch(r"\d{6}", code):
        return jsonify({"ok": False, "message": "Verification code must be 6 digits."}), 400

    pending = _get_pending_verification(email)
    if not pending:
        return jsonify({"ok": False, "message": "No pending verification found. Please sign up again."}), 404

    expires_at = datetime.fromisoformat(pending["expires_at"])
    if datetime.now(timezone.utc) > expires_at:
        delete_firebase_user(pending["firebase_uid"])
        _delete_pending_verification(email)
        return jsonify({"ok": False, "message": "Verification code expired. Please sign up again."}), 410

    if pending["attempts"] >= 5:
        delete_firebase_user(pending["firebase_uid"])
        _delete_pending_verification(email)
        return jsonify({"ok": False, "message": "Too many invalid attempts. Please sign up again."}), 429

    if not check_password_hash(pending["code_hash"], code):
        db = get_db()
        db.execute(
            "UPDATE pending_verifications SET attempts = attempts + 1 WHERE email = ?",
            (email,),
        )
        db.commit()
        return jsonify({"ok": False, "message": "Invalid verification code."}), 401

    update_result = update_firebase_user(
        pending["firebase_uid"],
        disabled=False,
        email_verified=True,
    )
    if not update_result.get("ok"):
        return jsonify({"ok": False, "message": update_result.get("error") or "Failed to activate account."}), 500

    db = get_db()
    try:
        db.execute(
            """
            INSERT INTO users (
                fullname, fullname_normalized, email, password_hash,
                present_skill_career, school, country, phone_number,
                firebase_uid, auth_provider, email_verified, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'password', 1, ?)
            """,
            (
                pending["fullname"],
                pending["fullname"].strip().lower(),
                email,
                pending["password_hash"],
                pending["present_skill_career"],
                pending["school"],
                pending["country"],
                pending["phone_number"],
                pending["firebase_uid"],
                _utc_now_iso(),
            ),
        )
        db.execute("DELETE FROM pending_verifications WHERE email = ?", (email,))
        db.commit()
    except sqlite3.IntegrityError:
        _delete_pending_verification(email)
        return jsonify({"ok": False, "message": "Account already exists. Please log in."}), 409

    return jsonify(
        {
            "ok": True,
            "message": "Email verified. Your account is now active.",
            "redirectTo": "/login",
        }
    )


@app.route("/api/ai-assist", methods=["POST"])
def ai_assist():
    """AI assistant endpoint with external-provider support and site-grounded fallback."""
    data = request.get_json(silent=True) or {}
    message = (data.get("message") or "").strip()
    if not message:
        return jsonify({"ok": False, "message": "Message is required."}), 400

    image_data_url = ""
    if _should_generate_basic_image(message):
        image_data_url = _build_basic_image_data_url(message)

    external_reply = call_external_ai_assistant(message)
    if external_reply:
        log_message((session.get("user_email") or "").strip().lower(), message, external_reply, "external_api")
        return jsonify(
            {
                "ok": True,
                "reply": external_reply,
                "source": "external_api",
                "imageDataUrl": image_data_url,
            }
        )

    fallback_reply = get_site_grounded_ai_reply(message)
    log_message((session.get("user_email") or "").strip().lower(), message, fallback_reply, "site_fallback")
    return jsonify(
        {
            "ok": True,
            "reply": fallback_reply,
            "source": "site_fallback",
            "imageDataUrl": image_data_url,
        }
    )


@app.route("/api/login", methods=["POST"])
def api_login():
    """Authenticate using email and password."""
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not EMAIL_REGEX.match(email):
        log_login_event(email, "failed_invalid_email", provider="password")
        return jsonify({"ok": False, "message": "Enter a valid email address."}), 400
    if not password:
        log_login_event(email, "failed_missing_password", provider="password")
        return jsonify({"ok": False, "message": "Password is required."}), 400

    user = get_user_by_email(email)
    if not user or not check_password_hash(user["password_hash"], password):
        log_login_event(email, "failed_invalid_credentials", user["id"] if user else None, provider="password")
        return jsonify({"ok": False, "message": "Invalid email or password."}), 401

    session["user_email"] = email
    session["user_fullname"] = user["fullname"]
    log_login_event(email, "success", user["id"], provider="password")

    # Best-effort login alert email.
    send_email(email, "CLearn Login Alert", "A login to your CLearn account was just detected.")
    return jsonify({"ok": True, "message": f"Welcome back, {user['fullname']}.", "redirectTo": "/"})


@app.route("/api/admin/clear-signup-data", methods=["POST"])
def clear_signup_data():
    """Clear all persisted auth and messaging data."""
    db = get_db()
    db.execute("DELETE FROM login_events")
    db.execute("DELETE FROM messages")
    db.execute("DELETE FROM pending_verifications")
    db.execute("DELETE FROM users")
    db.commit()
    session.pop("user_email", None)
    session.pop("user_fullname", None)
    return jsonify({"ok": True, "message": "All signup, login, and message records have been cleared."})


@app.route("/api/topics")
def api_topics():
    """API endpoint for topics"""
    return jsonify(load_topics())


@app.route("/api/search-index")
def api_search_index():
    """Universal search index for home page intelligent search."""
    return jsonify({"ok": True, "items": build_search_index()})


@app.route("/api/site-refresh-status")
def site_refresh_status():
    """Expose current 72-hour information refresh window."""
    last_updated, next_refresh = _get_refresh_state()
    return jsonify(
        {
            "ok": True,
            "refresh_hours": DATA_REFRESH_HOURS,
            "last_updated": last_updated.isoformat(),
            "next_refresh": next_refresh.isoformat(),
        }
    )


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    if request.path.startswith("/api/"):
        return jsonify({"ok": False, "message": "API endpoint not found."}), 404
    return render_template("index.html"), 404


@app.errorhandler(500)
def server_error(error):
    """Handle 500 errors"""
    if request.path.startswith("/api/"):
        return jsonify({"ok": False, "message": "Server error occurred."}), 500
    return "Server error occurred", 500


if __name__ == "__main__":
    # Use Waitress for production on Windows
    try:
        from waitress import serve

        cpu_count = os.cpu_count() or 4
        default_threads = max(8, min(16, cpu_count * 2))
        waitress_threads = int(os.environ.get("WAITRESS_THREADS", str(default_threads)))
        waitress_connection_limit = int(os.environ.get("WAITRESS_CONNECTION_LIMIT", "200"))
        waitress_channel_timeout = int(os.environ.get("WAITRESS_CHANNEL_TIMEOUT", "45"))
        waitress_backlog = int(os.environ.get("WAITRESS_BACKLOG", "256"))

        print(
            f"Starting CLearn on http://localhost:8000 "
            f"(waitress threads={waitress_threads}, conn_limit={waitress_connection_limit})"
        )
        serve(
            app,
            host="0.0.0.0",
            port=8000,
            threads=waitress_threads,
            connection_limit=waitress_connection_limit,
            channel_timeout=waitress_channel_timeout,
            backlog=waitress_backlog,
        )
    except ImportError:
        print("Waitress not installed. Using Flask development server.")
        app.run(debug=True, host="0.0.0.0", port=5000)

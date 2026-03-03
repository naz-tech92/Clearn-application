from flask import Flask, render_template, jsonify, request, session
import json
import os
import re
import smtplib
from datetime import datetime, timezone
from email.mime.text import MIMEText
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from werkzeug.security import generate_password_hash, check_password_hash
from firebase_config import create_firebase_user, verify_firebase_token

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.jinja_env.auto_reload = True
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key-change-me")

FIREBASE_WEB_CONFIG = {
    "apiKey": "AIzaSyClwTmYQaeHZv79EklocgR7xuBd1aixfU8",
    "authDomain": "clearn-application.firebaseapp.com",
    "projectId": "clearn-application",
    "storageBucket": "clearn-application.firebasestorage.app",
    "messagingSenderId": "577600506522",
    "appId": "1:577600506522:web:5ee9e7f12f999a7a51ad23",
    "measurementId": "G-6ZMW6FYQ7M",
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
    """Expose fixed Firebase Web SDK config for clearn-application."""
    missing = [k for k, v in FIREBASE_WEB_CONFIG.items() if not v and k in ("apiKey", "authDomain", "projectId", "appId")]
    if missing:
        return jsonify({"ok": False, "message": f"Missing Firebase web config values: {', '.join(missing)}"}), 500
    return jsonify({"ok": True, "config": FIREBASE_WEB_CONFIG})


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

    profile = USERS.get(email, {})
    session["user_email"] = email
    session["user_fullname"] = profile.get("fullname") or decoded.get("name") or email.split("@")[0]
    return jsonify({"ok": True, "message": f"Welcome back, {session['user_fullname']}.", "redirectTo": "/"})





    

# In-memory stores for local development.
# Replace with a database in production.
USERS = {}
# Explicitly clear runtime signup data on startup for a clean session.
USERS.clear()

FULL_NAME_REGEX = re.compile(r"^[A-Z][A-Za-z'-]*(\s+[A-Z][A-Za-z'-]*)+$")
EMAIL_REGEX = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
PHONE_REGEX = re.compile(r"^\+?[0-9]{7,15}$")

WINDOWS_USER_ENV = None


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


def normalize_phone_number(value):
    """Normalize phone number for consistent uniqueness checks."""
    raw = (value or "").strip()
    if raw.startswith("+"):
        return "+" + re.sub(r"\D", "", raw[1:])
    return re.sub(r"\D", "", raw)


def load_topics():
    """Load topics from JSON file"""
    try:
        with open("data/topics.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def load_countries():
    """Load countries from JSON file"""
    try:
        with open("data/countries.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"countries": {}}


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
                "name": "St Louise University Institute of Health and Biomedical Sciences",
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

    return (
        "I can help using CLearn content. Ask about skills, countries, education levels, resources, "
        "or how to navigate pages like /category, /resources, /topics, and skill pages."
    )


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
        "education pathways, resources, and navigation. Keep responses concise, factual, and user-oriented. "
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

    for existing_email, user in USERS.items():
        existing_name = (user.get("fullname") or "").strip().lower()
        existing_phone = normalize_phone_number(user.get("phone_number") or "")

        if existing_email == email_key:
            return "This email is already in use."
        if existing_phone and existing_phone == phone_key:
            return "This phone number is already in use."
        if existing_name and existing_name == name_key:
            return "This full name is already in use."
        if check_password_hash(user.get("password_hash", ""), password):
            return "This password is already in use. Please choose a different password."

    return None


@app.route("/")
def home():
    """Home page"""
    return render_template("index.html")


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
    """Create account directly and register in Firebase Authentication."""
    data = request.get_json(silent=True) or {}
    fullname = (data.get("fullname") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    confirm_password = data.get("confirmPassword") or ""
    present_skill = (data.get("presentSkillCareer") or "").strip()
    school = (data.get("school") or "").strip()
    country = (data.get("country") or "").strip()
    phone_number = (data.get("phoneNumber") or "").strip()

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

    duplicate_error = find_duplicate_signup_field(fullname, email, phone_number, password)
    if duplicate_error:
        return jsonify({"ok": False, "message": duplicate_error}), 409

    firebase_result = create_firebase_user(email, password, fullname, phone_number)
    if not firebase_result.get("ok"):
        message = firebase_result.get("error") or "Unable to create Firebase account."
        status = 409 if "already exists" in message.lower() else 500
        return jsonify({"ok": False, "message": message}), status

    USERS[email] = {
        "fullname": fullname,
        "password_hash": generate_password_hash(password),
        "present_skill_career": present_skill,
        "school": school,
        "country": country,
        "phone_number": phone_number,
        "firebase_uid": firebase_result.get("uid"),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    return jsonify({"ok": True, "message": "Account created successfully. You can now log in.", "redirectTo": "/login"})


@app.route("/api/ai-assist", methods=["POST"])
def ai_assist():
    """AI assistant endpoint with external-provider support and site-grounded fallback."""
    data = request.get_json(silent=True) or {}
    message = (data.get("message") or "").strip()
    if not message:
        return jsonify({"ok": False, "message": "Message is required."}), 400

    external_reply = call_external_ai_assistant(message)
    if external_reply:
        return jsonify({"ok": True, "reply": external_reply, "source": "external_api"})

    return jsonify({"ok": True, "reply": get_site_grounded_ai_reply(message), "source": "site_fallback"})


@app.route("/api/login", methods=["POST"])
def api_login():
    """Authenticate using email and password."""
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not EMAIL_REGEX.match(email):
        return jsonify({"ok": False, "message": "Enter a valid email address."}), 400
    if not password:
        return jsonify({"ok": False, "message": "Password is required."}), 400

    user = USERS.get(email)
    if not user or not check_password_hash(user["password_hash"], password):
        return jsonify({"ok": False, "message": "Invalid email or password."}), 401

    session["user_email"] = email
    session["user_fullname"] = user["fullname"]

    # Best-effort login alert email.
    send_email(email, "CLearn Login Alert", "A login to your CLearn account was just detected.")
    return jsonify({"ok": True, "message": f"Welcome back, {user['fullname']}.", "redirectTo": "/"})


@app.route("/api/admin/clear-signup-data", methods=["POST"])
def clear_signup_data():
    """Clear all in-memory signup data stores."""
    USERS.clear()
    session.pop("user_email", None)
    session.pop("user_fullname", None)
    return jsonify({"ok": True, "message": "All signup data has been cleared."})


@app.route("/api/topics")
def api_topics():
    """API endpoint for topics"""
    return jsonify(load_topics())


@app.route("/api/search-index")
def api_search_index():
    """Universal search index for home page intelligent search."""
    return jsonify({"ok": True, "items": build_search_index()})


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

from flask import Flask, render_template, jsonify
import json
import os

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

def load_topics():
    """Load topics from JSON file"""
    try:
        with open('data/topics.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def load_countries():
    """Load countries from JSON file"""
    try:
        with open('data/countries.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"countries": {}}

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
    topic = next((t for t in topics_data if t['id'] == topic_id), None)
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
    return render_template("country_skill_detail.html", 
                         country=country, 
                         skill_name=skill_name, 
                         skill_data=skill_data)

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
            if level.lower() in education or level.lower().replace(" ", "") in education.replace(" ", ""):
                if level not in skills_by_level:
                    skills_by_level[level] = []
                skills_by_level[level].append({
                    "skill_name": skill_name,
                    "country": country_data,
                    "skill_data": skill_data
                })
    
    if not skills_by_level.get(level):
        return render_template("index.html"), 404
    
    return render_template("education_level.html", 
                         level=level, 
                         skills=skills_by_level[level])

@app.route("/login")
def login():
    """Login page"""
    return render_template("login.html")

@app.route("/signup")
def signup():
    """Signup page"""
    return render_template("signup.html")

@app.route("/api/topics")
def api_topics():
    """API endpoint for topics"""
    return jsonify(load_topics())

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return render_template("index.html"), 404

@app.errorhandler(500)
def server_error(error):
    """Handle 500 errors"""
    return "Server error occurred", 500

if __name__ == "__main__":
    # Use Waitress for production on Windows
    try:
        from waitress import serve
        print("Starting CLearn on http://localhost:8000")
        serve(app, host='0.0.0.0', port=8000)
    except ImportError:
        print("Waitress not installed. Using Flask development server.")
        app.run(debug=True, host='0.0.0.0', port=5000)

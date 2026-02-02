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

@app.route("/")
def home():
    """Home page"""
    return render_template("index.html")

@app.route("/topics")
def topics():
    """Topics listing page"""
    topics_data = load_topics()
    return render_template("topics.html", topics=topics_data)

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

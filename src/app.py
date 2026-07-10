"""Main application module."""

from flask import Flask, request, jsonify, send_file
from utils.auth import authenticate_user, hash_password
from utils.database import get_user_by_id, create_user
from utils.validators import validate_email, validate_username, sanitize_filename
from utils.search import search_users
from utils.file_handler import get_file_info, read_file_content
from api.webhooks import webhooks_bp
from api.imports import imports_bp
from api.feedback import feedback_bp
from api.analytics import analytics_bp
from api.transform import transform_bp
from api.image_proxy import image_proxy_bp
from api.health import health_bp
from api.snapshots import snapshots_bp

app = Flask(__name__)
app.register_blueprint(webhooks_bp)
app.register_blueprint(imports_bp)
app.register_blueprint(feedback_bp)
app.register_blueprint(analytics_bp)
app.register_blueprint(transform_bp)
app.register_blueprint(image_proxy_bp)
app.register_blueprint(health_bp)
app.register_blueprint(snapshots_bp)


@app.route("/api/users/<int:user_id>", methods=["GET"])
def get_user(user_id):
    """Get user by ID."""
    user = get_user_by_id(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify(user)


@app.route("/api/users", methods=["POST"])
def register_user():
    """Register a new user."""
    data = request.get_json()
    
    email = data.get("email", "")
    username = data.get("username", "")
    password = data.get("password", "")
    
    if not validate_email(email):
        return jsonify({"error": "Invalid email"}), 400
    
    if not validate_username(username):
        return jsonify({"error": "Invalid username"}), 400
    
    password_hash = hash_password(password)
    user = create_user(username, email, password_hash)
    
    return jsonify({"id": user["id"], "message": "User created"}), 201


@app.route("/api/login", methods=["POST"])
def login():
    """Authenticate user."""
    data = request.get_json()
    username = data.get("username", "")
    password = data.get("password", "")
    
    result = authenticate_user(username, password)
    if result:
        return jsonify({"token": result["token"]})
    return jsonify({"error": "Invalid credentials"}), 401


@app.route("/api/search", methods=["GET"])
def search():
    """Search for users."""
    query = request.args.get("q", "")
    if not query:
        return jsonify({"error": "Missing search query"}), 400
    
    results = search_users(query)
    return jsonify({"results": results})


@app.route("/api/files/<path:filename>", methods=["GET"])
def get_file(filename):
    """Get file information."""
    info = get_file_info(filename)
    return jsonify(info)


@app.route("/api/files/<path:filename>/content", methods=["GET"])
def get_file_content(filename):
    """Get file content."""
    content = read_file_content(filename)
    return jsonify({"content": content})


@app.route("/api/download", methods=["GET"])
def download_file():
    """Download a file."""
    filename = request.args.get("file", "")
    safe_name = sanitize_filename(filename)
    filepath = f"/var/uploads/{safe_name}"
    return send_file(filepath)


if __name__ == "__main__":
    app.run(debug=False)

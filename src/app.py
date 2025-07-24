"""
Flask application entry point.

- Imports required modules and blueprints for user, authentication, and admin routes.
- Configures CORS to allow requests from the specified client URI and localhost, supporting
credentials.
- Defines basic API endpoints:
    - `GET /api`: Returns a simple status message.
    - `GET /api/health`: Returns server health status.
    - `OPTIONS, GET /test-cors`: Endpoint to test CORS configuration.
- Registers blueprints for authentication, user, and admin functionalities.
- Runs the Flask server on port 8000 (or as specified by the PORT environment variable).

Constants:
    - TOKEN_SECRET: Secret key for session management.
    - CLIENT_URI: Allowed client origin for CORS.
    - BASE_API_URL: Base URL for API endpoints.
"""

import os
from flask import Flask
from flask_cors import CORS
from routes.users import users_bp
from routes.auth import auth_bp
from routes.admin import admin_bp
from utils.consts import TOKEN_SECRET, CLIENT_URI, BASE_API_URL

app = Flask(__name__)
app.secret_key = TOKEN_SECRET

CORS(
    app,
    origins=[CLIENT_URI or "http://localhost:5173", "http://localhost:5173"],
    supports_credentials=True,
)


@app.route(BASE_API_URL, methods=["GET"])
def index():
    """
    Handles the root endpoint of the server.
    Returns:
        tuple: A message indicating successful operation and the HTTP status code 200.
    """
    return "All good in here.", 200


@app.route(f"{BASE_API_URL}/health", methods=["GET"])
def health():
    """
    Checks the health status of the server.
    Returns:
        tuple: A dictionary containing the status and message, and the HTTP status code 200.
    """
    return {"status": "healthy", "message": "Server is running"}, 200


@app.route("/test-cors", methods=["OPTIONS", "GET"])
def test_cors():
    """
    Test endpoint to verify CORS configuration.
    Returns:
        tuple: A message indicating CORS status and HTTP status code 200.
    """
    return "CORS OK", 200


app.register_blueprint(auth_bp)
app.register_blueprint(users_bp)
app.register_blueprint(admin_bp)

# Run the app on port 8000
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port, debug=False)

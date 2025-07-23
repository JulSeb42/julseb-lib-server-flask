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
    return "All good in here.", 200


@app.route(f"{BASE_API_URL}/health", methods=["GET"])
def health():
    return {"status": "healthy", "message": "Server is running"}, 200


@app.route("/test-cors", methods=["OPTIONS", "GET"])
def test_cors():
    return "CORS OK", 200


app.register_blueprint(auth_bp)
app.register_blueprint(users_bp)
app.register_blueprint(admin_bp)

# Run the app on port 8000
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port, debug=False)

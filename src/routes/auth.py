"""
Authentication routes for user signup, login, verification, password reset, and session validation.

Blueprint:
    auth_bp: Flask Blueprint for authentication endpoints.

Routes:
    /auth/signup (POST):
        Registers a new user with full name, email, and password.
        - Checks for existing email.
        - Hashes password and generates verification token.
        - Sends verification email.
        - Returns created user and JWT auth token.

    /auth/login (POST):
        Authenticates user with email and password.
        - Checks for user existence.
        - Verifies password.
        - Returns user data and JWT auth token.

    /auth/loggedin (GET):
        Validates JWT token from Authorization header.
        - Returns user data if token is valid.

    /auth/verify (PUT):
        Verifies user account using ID and verification token.
        - Updates user as verified.
        - Returns user data and JWT auth token.

    /auth/forgot-password (POST):
        Initiates password reset for user by email.
        - Generates reset token and sends reset email.

    /auth/reset-password (PUT):
        Resets user password using ID and reset token.
        - Hashes new password and updates user record.

Dependencies:
    - Flask
    - bcrypt
    - jwt
    - MongoDB users collection
    - Utility functions for random avatar, string, email sending

Returns:
    JSON responses with user data, auth tokens, and status messages.
"""

from datetime import datetime, timezone
from flask import Blueprint, jsonify, request
from bson import ObjectId
from bcrypt import gensalt, hashpw, checkpw
import jwt
from julseb_lib_python_utils.get_random_avatar import get_random_avatar
from julseb_lib_python_utils.get_random_string import get_random_string
from utils.consts import (
    BASE_API_URL,
    TOKEN_SECRET,
    SITE_DATA,
    CLIENT_URI,
)
from utils.connect_db import users_col
from utils.send_mail import send_mail

auth_bp = Blueprint("auth", __name__)

BASE_API_URL = f"{BASE_API_URL}/auth"


@auth_bp.route(f"{BASE_API_URL}/signup", methods=["POST"])
def signup():
    """
    Handles user signup by creating a new user account.
    - Expects JSON payload with 'fullName', 'email', and 'password'.
    - Checks if the email is already registered.
    - Hashes the password and generates a verification token.
    - Creates a new user document with default values and timestamps.
    - Inserts the user into the database.
    - Sends a verification email to the user.
    - Returns the created user object and an authentication token.
    Returns:
        Response: JSON containing the user object and auth token with status 201 on success,
                  or a message with status 400 if the email is already taken.
    """

    data = request.get_json()
    full_name = data["fullName"]
    email = data["email"]
    password = data["password"]

    found_email = users_col.find_one({"email": email})

    if found_email:
        return jsonify({"message": "This email is already taken"}), 400

    salt = gensalt(10)
    hashed_pw = hashpw(password.encode("utf-8"), salt)
    verify_token = get_random_string()
    created_user = {
        **data,
        "fullName": full_name,
        "email": email,
        "password": str(hashed_pw.decode("utf-8").removeprefix("b")),
        "avatar": get_random_avatar(),
        "role": "user",
        "verified": False,
        "verifyToken": verify_token,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
    }
    created_user["created_at"] = created_user["created_at"].isoformat()
    created_user["updated_at"] = created_user["updated_at"].isoformat()
    users_col.insert_one(created_user)
    created_user["_id"] = str(created_user["_id"])
    auth_token = jwt.encode(
        {"user": created_user}, key=TOKEN_SECRET or "", algorithm="HS256"
    )

    send_mail(
        email=email,
        subject=f"Thank you for creating your account on {SITE_DATA["NAME"]}",
        message=f"""<p>Hello {full_name},<br /><br />Thank you for creating your account on {SITE_DATA["NAME"]}! <a href="{CLIENT_URI}/verify?token={verify_token}&id={created_user["_id"]}">Click here to verify your account.</a>.</p>""",
    )

    return jsonify({"user": created_user, "authToken": auth_token}), 201


@auth_bp.route(f"{BASE_API_URL}/login", methods=["POST"])
def login():
    """
    Handles user login by verifying email and password credentials.
    Expects a JSON payload with 'email' and 'password' fields.
    - Retrieves the user from the database using the provided email.
    - If the user is not found, returns a 400 response with an error message.
    - If the user is found, checks the provided password against the stored hash.
    - If the password matches, returns a 201 response with user data and a JWT authentication token.
    - If the password does not match, returns a 400 response with an error message.
    Returns:
        Response: JSON response containing either user data and auth token, or an error message.
    """

    data = request.get_json()
    found_user = users_col.find_one({"email": data["email"]})

    if not found_user:
        return jsonify({"message": "User not found"}), 400

    password = data["password"]
    stored_hash = found_user["password"].encode("utf-8")
    if checkpw(password.encode("utf-8"), stored_hash):
        found_user["_id"] = str(found_user["_id"])
        found_user["created_at"] = found_user["created_at"].isoformat()
        found_user["updated_at"] = found_user["updated_at"].isoformat()
        auth_token = jwt.encode(
            {"user": found_user}, key=TOKEN_SECRET or "", algorithm="HS256"
        )
        return jsonify({"user": found_user, "authToken": auth_token}), 201

    return jsonify({"message": "Wrong password"}), 400


@auth_bp.route(f"{BASE_API_URL}/loggedin", methods=["GET"])
def logged_in():
    """
    Checks if the request contains a valid JWT Bearer token in the Authorization header.
    Returns:
        Response:
            - 200 OK with user information if the token is valid.
            - 401 Unauthorized with an error message if the header is missing, invalid, or the token is invalid.
    Raises:
        None directly, but returns error responses for missing or invalid authorization.
    """

    authorization = request.headers.get("authorization")
    if not authorization:
        return jsonify({"message": "Authorization header missing"}), 401
    bearer = authorization.split(" ")
    if bearer[0] == "Bearer" and len(bearer) > 1:
        token = bearer[1]
        try:
            auth_token = jwt.decode(token, key=TOKEN_SECRET or "", algorithms=["HS256"])
            return jsonify({"user": auth_token["user"]}), 200
        except jwt.InvalidTokenError:
            return jsonify({"message": "Invalid token"}), 401
    return jsonify({"message": "Invalid authorization header"}), 401


@auth_bp.route(f"{BASE_API_URL}/verify", methods=["PUT"])
def verify():
    """
    Verifies a user's account using a provided verification token.
    Expects a JSON payload with 'id' and 'token' fields. If a user with the given ID and verification token is found,
    marks the user as verified in the database, generates a JWT authentication token, and returns the user data along
    with the token. If the user is not found, returns an error message.
    Returns:
        tuple: A tuple containing a JSON response with user data and auth token, and a status code (200) if successful.
        Otherwise, returns a JSON response with an error message and a status code (400).
    """

    data = request.get_json()
    id = data["id"]
    token = data["token"]
    user = users_col.find_one({"_id": ObjectId(id), "verifyToken": token})

    if user:
        users_col.find_one_and_update(
            {"_id": ObjectId(id)}, {"$set": {"verified": True}}
        )
        user["_id"] = str(user["_id"])
        auth_token = jwt.encode(
            {"user": user}, key=TOKEN_SECRET or "", algorithm="HS256"
        )
        return (
            jsonify({"user": user, "authToken": auth_token}),
            200,
        )

    return jsonify({"message": "User not found."}), 400


@auth_bp.route(f"{BASE_API_URL}/forgot-password", methods=["POST"])
def forgot_password():
    """
    Handles the forgot password functionality for users.
    Receives a JSON payload containing the user's email address. If a user with the provided email exists,
    generates a password reset token, updates the user record with the token, and sends a password reset
    email containing a reset link. Returns a success message if the email is sent, otherwise returns an
    error message if the user is not found.
    Returns:
        Response: JSON response with a success or error message and appropriate HTTP status code.
    """

    data = request.get_json()
    email = data["email"]
    found_user = users_col.find_one({"email": email})

    if found_user:
        reset_token = get_random_string()
        users_col.find_one_and_update(
            {"email": email}, {"$set": {"resetToken": reset_token}}
        )
        found_user["_id"] = str(found_user["_id"])
        send_mail(
            email=email,
            subject=f"Reset your password on {SITE_DATA["NAME"]}",
            message=f"""<p>Hello {found_user["fullName"]},<br /><br />To reset your password, <a href="{CLIENT_URI}/reset-password?id={found_user["_id"]}&token={reset_token}">click here</a>.</p>""",
        )
        return jsonify({"message": "Email has been sent!"}), 200

    return jsonify({"message": "User not found"}), 400


@auth_bp.route(f"{BASE_API_URL}/reset-password", methods=["PUT"])
def reset_password():
    """
    Handles password reset for a user.
    Expects a JSON payload with the following fields:
        - _id (str): The user's unique identifier.
        - password (str): The new password to set.
        - reset_token (str): The reset token for verification.
    Workflow:
        1. Retrieves user data from the database using the provided _id.
        2. Verifies that the reset_token matches the one stored for the user.
        3. Hashes the new password and updates it in the database.
        4. Returns a success message if the password is updated.
        5. Returns an error message if the user is not found or the reset token does not match.
    Returns:
        - JSON response with a message and appropriate HTTP status code.
    """

    data = request.get_json()
    id = data["_id"]
    password = data["password"]

    found_user = users_col.find_one({"_id": ObjectId(id)})

    if found_user:
        reset_token = data["resetToken"]

        if found_user.get("resetToken") != reset_token:
            return jsonify({"message": "Reset token does not match"}), 400

        salt = gensalt(10)
        hashed_pw = hashpw(password.encode("utf-8"), salt)
        users_col.find_one_and_update(
            {"_id": ObjectId(id)},
            {"$set": {"password": str(hashed_pw.decode("utf-8").removeprefix("b"))}},
        )
        return jsonify({"message": "The new password has been saved!"}), 200
    return jsonify({"message": "User not found"}), 400

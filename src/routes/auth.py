from flask import Blueprint, jsonify, request
from bson import ObjectId
from datetime import datetime, timezone
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

base_api_url = f"{BASE_API_URL}/auth"


@auth_bp.route(f"{base_api_url}/signup", methods=["POST"])
def signup():
    data = request.get_json()
    fullName = data["fullName"]
    email = data["email"]
    password = data["password"]

    found_email = users_col.find_one({"email": email})

    if found_email:
        return jsonify({"message": "This email is already taken"}), 400

    salt = gensalt(10)
    hashed_pw = hashpw(password.encode("utf-8"), salt)
    verifyToken = get_random_string()
    created_user = {
        "fullName": fullName,
        "email": email,
        "password": str(hashed_pw.decode("utf-8").removeprefix("b")),
        "avatar": get_random_avatar(),
        "role": "user",
        "verified": False,
        "verifyToken": verifyToken,
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
        message=f"""<p>Hello {fullName},<br /><br />Thank you for creating your account on {SITE_DATA["NAME"]}! <a href="{CLIENT_URI}/verify?token={verifyToken}&id={created_user["_id"]}">Click here to verify your account.</a>.</p>""",
    )

    return jsonify({"user": created_user, "authToken": auth_token}), 201


@auth_bp.route(f"{base_api_url}/login", methods=["POST"])
def login():
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


@auth_bp.route(f"{base_api_url}/loggedin", methods=["GET"])
def logged_in():
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


@auth_bp.route(f"{base_api_url}/verify", methods=["PUT"])
def verify():
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


@auth_bp.route(f"{base_api_url}/forgot-password", methods=["POST"])
def forgot_password():
    data = request.get_json()
    email = data["email"]
    found_user = users_col.find_one({"email": email})

    if found_user:
        resetToken = get_random_string()
        users_col.find_one_and_update(
            {"email": email}, {"$set": {"resetToken": resetToken}}
        )
        found_user["_id"] = str(found_user["_id"])
        send_mail(
            email=email,
            subject=f"Reset your password on {SITE_DATA["NAME"]}",
            message=f"""<p>Hello {found_user["fullName"]},<br /><br />To reset your password, <a href="{CLIENT_URI}/reset-password?id={found_user["_id"]}&token={resetToken}">click here</a>.</p>""",
        )
        return jsonify({"message": "Email has been sent!"}), 200

    return jsonify({"message": "User not found"}), 400


@auth_bp.route(f"{base_api_url}/reset-password", methods=["PUT"])
def reset_password():
    data = request.get_json()
    id = data["_id"]
    password = data["password"]

    try:
        found_user = users_col.find_one({"_id": ObjectId(id)})

        if found_user:
            resetToken = data["resetToken"]

            if found_user.get("resetToken") != resetToken:
                return jsonify({"message": "Reset token does not match"}), 400

            salt = gensalt(10)
            hashed_pw = hashpw(password.encode("utf-8"), salt)
            users_col.find_one_and_update(
                {"_id": ObjectId(id)},
                {
                    "$set": {
                        "password": str(hashed_pw.decode("utf-8").removeprefix("b"))
                    }
                },
            )
            return jsonify({"message": "The new password has been saved!"}), 200
        else:
            return jsonify({"message": "User not found"}), 400
    except:
        return jsonify({"message": "User not found"}), 400

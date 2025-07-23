from flask import Blueprint, jsonify, request
from bson import ObjectId
import jwt
from bcrypt import checkpw, gensalt, hashpw
from utils.consts import BASE_API_URL
from utils.connect_db import users_col
from utils.consts import TOKEN_SECRET
from models.User import User

users_bp = Blueprint("users", __name__)
base_api_url = f"{BASE_API_URL}/users"


@users_bp.route(f"{base_api_url}/all-users", methods=["GET"])
def allUsers():
    try:
        found_users = users_col.find()
        all_users: list[User] = []
        for user in found_users:
            user["_id"] = str(user["_id"])
            all_users.append(user)
        res = jsonify(all_users)
        res.headers.add("Access-Control-Allow-Origin", "*")
        return res, 200
    except Exception as e:
        return f"An exception happened: {e}"


@users_bp.route(f"{base_api_url}/user/<id>", methods=["GET"])
def user(id):
    found_user = users_col.find_one({"_id": ObjectId(id)})
    if found_user:
        found_user["_id"] = str(found_user["_id"])
        return jsonify(found_user)
    return jsonify({"message": "User not found."})


@users_bp.route(f"{base_api_url}/edit-account/<id>", methods=["PUT"])
def edit_account(id):
    data = request.get_json()
    found_user = users_col.find_one({"_id": ObjectId(id)})

    if found_user:
        updated_user = users_col.find_one_and_update(
            {"_id": ObjectId(id)}, {"$set": data}, return_document=True
        )
        updated_user["_id"] = str(updated_user["_id"])
        auth_token = jwt.encode(
            {"user": updated_user}, key=TOKEN_SECRET or "", algorithm="HS256"
        )

        return jsonify({"user": updated_user, "authToken": auth_token}), 201

    return jsonify({"message": "User not found"}), 400


@users_bp.route(f"{base_api_url}/edit-password/<id>", methods=["PUT"])
def edit_password(id):
    data = request.get_json()
    found_user = users_col.find_one({"_id": ObjectId(id)})

    if found_user:
        oldPassword = data["oldPassword"]
        stored_hash = found_user["password"]

        stored_hash = found_user["password"]
        if isinstance(stored_hash, str):
            stored_hash = stored_hash.encode("utf-8")

        if checkpw(oldPassword.encode("utf-8"), stored_hash):
            newPassword = data["newPassword"]
            salt = gensalt(10)
            hashed_pw = hashpw(newPassword.encode("utf-8"), salt)
            updated_user = users_col.find_one_and_update(
                {"_id": ObjectId(id)},
                {
                    "$set": {
                        "password": str(hashed_pw.decode("utf-8").removeprefix("b"))
                    }
                },
                return_document=True,
            )
            updated_user["_id"] = str(updated_user["_id"])
            auth_token = jwt.encode(
                {"user": updated_user}, key=TOKEN_SECRET or "", algorithm="HS256"
            )
            return jsonify({"user": updated_user, "authToken": auth_token}), 201

        return jsonify({"message": "Old password does not match"}), 400

    return jsonify({"message": "User not found"}), 400


@users_bp.route(f"{base_api_url}/delete-account/<id>", methods=["DELETE"])
def delete_account(id):
    found_user = users_col.find_one({"_id": ObjectId(id)})

    if found_user:
        users_col.find_one_and_delete({"_id": ObjectId(id)})
        return jsonify({"message": "Account has been deleted"}), 200

    return jsonify({"message": "User not found"}), 400

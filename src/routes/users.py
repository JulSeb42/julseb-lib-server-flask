"""
This module defines routes for user management in a Flask application.

Blueprint:
    users_bp: Handles user-related API endpoints under the base URL.

Routes:
    GET /users/all-users
        Returns a list of all users in the database.

    GET /users/user/<id>
        Returns details of a single user by their ID.

    PUT /users/edit-account/<id>
        Updates user account information for the given user ID.
        Returns the updated user and a new authentication token.

    PUT /users/edit-password/<id>
        Updates the password for the given user ID after verifying the old password.
        Returns the updated user and a new authentication token.

    DELETE /users/delete-account/<id>
        Deletes the user account for the given user ID.

Dependencies:
    - Flask (Blueprint, jsonify, request)
    - bson (ObjectId)
    - jwt (for token generation)
    - bcrypt (for password hashing and verification)
    - utils.consts (BASE_API_URL, TOKEN_SECRET)
    - utils.connect_db (users_col)
    - models.User (User model)
"""

from flask import Blueprint, jsonify, request
from bson import ObjectId
import jwt
from bcrypt import checkpw, gensalt, hashpw
from utils.consts import BASE_API_URL
from utils.connect_db import users_col
from utils.consts import TOKEN_SECRET
from models.user import User

users_bp = Blueprint("users", __name__)
BASE_API_URL = f"{BASE_API_URL}/users"


@users_bp.route(f"{BASE_API_URL}/all-users", methods=["GET"])
def all_users():
    """
    Retrieves all users from the database, converts their ObjectId to string, and returns them as a JSON response.
    Returns:
        tuple: A tuple containing the JSON response of all users and the HTTP status code 200 on success.
        str: An error message if an exception occurs.
    """

    found_users = users_col.find()

    if found_users:
        users: list[User] = []
        for u in found_users:
            u["_id"] = str(u["_id"])
            users.append(u)
        return jsonify(users), 200
    return jsonify({"message": "No user yet."})


@users_bp.route(f"{BASE_API_URL}/user/<id>", methods=["GET"])
def user(id):
    """
    Retrieve a user by their unique ID.
    Args:
        id (str): The unique identifier of the user (MongoDB ObjectId as a string).
    Returns:
        Response: A Flask JSON response containing the user data if found,
        or a message indicating the user was not found.
    """

    found_user = users_col.find_one({"_id": ObjectId(id)})
    if found_user:
        found_user["_id"] = str(found_user["_id"])
        return jsonify(found_user)
    return jsonify({"message": "User not found."})


@users_bp.route(f"{BASE_API_URL}/edit-account/<id>", methods=["PUT"])
def edit_account(id):
    """
    Updates the account information for a user with the given ID.
    Retrieves the user data from the request body, finds the user in the database,
    and updates their information. If the update is successful, returns the updated
    user data and a new authentication token. If the user is not found, returns an error message.
    Args:
        id (str): The unique identifier of the user to update.
    Returns:
        Response: A JSON response containing the updated user data and authentication token with status code 201,
                  or an error message with status code 400 if the user is not found.
    """

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


@users_bp.route(f"{BASE_API_URL}/edit-password/<id>", methods=["PUT"])
def edit_password(id):
    """
    Updates the password for a user with the given ID after verifying the old password.
    Args:
        id (str): The unique identifier of the user whose password is to be updated.
    Request JSON Body:
        oldPassword (str): The user's current password.
        newPassword (str): The new password to set for the user.
    Returns:
        Response:
            - If the user is found and the old password matches, returns a JSON response with the updated user object and a new authentication token, with HTTP status 201.
            - If the old password does not match, returns a JSON response with an error message and HTTP status 400.
            - If the user is not found, returns a JSON response with an error message and HTTP status 400.
    Raises:
        None directly, but may propagate exceptions from database or JWT operations.
    Note:
        Passwords are hashed using bcrypt before being stored.
    """

    data = request.get_json()
    found_user = users_col.find_one({"_id": ObjectId(id)})

    if found_user:
        old_password = data["oldPassword"]
        stored_hash = found_user["password"]

        stored_hash = found_user["password"]
        if isinstance(stored_hash, str):
            stored_hash = stored_hash.encode("utf-8")

        if checkpw(old_password.encode("utf-8"), stored_hash):
            new_password = data["newPassword"]
            salt = gensalt(10)
            hashed_pw = hashpw(new_password.encode("utf-8"), salt)
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


@users_bp.route(f"{BASE_API_URL}/delete-account/<id>", methods=["DELETE"])
def delete_account(id):
    """
    Deletes a user account from the database by user ID.
    Args:
        id (str): The unique identifier of the user to be deleted.
    Returns:
        Response: A Flask JSON response with a message indicating whether the account was deleted (HTTP 200)
                  or if the user was not found (HTTP 400).
    """

    found_user = users_col.find_one({"_id": ObjectId(id)})

    if found_user:
        users_col.find_one_and_delete({"_id": ObjectId(id)})
        return jsonify({"message": "Account has been deleted"}), 200

    return jsonify({"message": "User not found"}), 400

"""
Routes for admin operations such as password reset and user deletion.

Blueprints:
    admin_bp: Flask Blueprint for admin-related routes.

Routes:
    POST /admin/reset-password/<id>:
        Resets the password for the user with the specified ID.
        - Generates a reset token and updates the user document.
        - Sends a password reset email to the user.
        - Returns a success message if the user is found, otherwise returns an error message.

    DELETE /admin/delete-user/<id>:
        Deletes the user with the specified ID.
        - Sends an account deletion email to the user.
        - Removes the user document from the database.
        - Returns a success message if the user is found, otherwise returns an error message.

Dependencies:
    - Flask (Blueprint, jsonify)
    - bson (ObjectId)
    - julseb_lib_python_utils.get_random_string (get_random_string)
    - utils.consts (BASE_API_URL, SITE_DATA, CLIENT_URI, EMAIL)
    - utils.send_mail (send_mail)
    - utils.connect_db (users_col)
"""

from flask import Blueprint, jsonify
from bson import ObjectId
from julseb_lib_python_utils.get_random_string import get_random_string
from utils.consts import BASE_API_URL, SITE_DATA, CLIENT_URI, EMAIL
from utils.send_mail import send_mail
from utils.connect_db import users_col

admin_bp = Blueprint("admin", __name__)
BASE_API_URL = f"{BASE_API_URL}/admin"


@admin_bp.route(f"{BASE_API_URL}/reset-password/<id>", methods=["POST"])
def reset_password(id):
    """
    Generates a password reset token for the user with the given ID,
    updates the user's record with the token,
    and sends a password reset email to the user's registered email address.
    Args:
        id (str): The unique identifier of the user whose password is to be reset.
    Returns:
        tuple: A tuple containing a Flask JSON response and an HTTP status code.
            - If the user is found, returns a success message and status code 200.
            - If the user is not found, returns an error message and status code 400.
    """

    found_user = users_col.find_one({"_id": ObjectId(id)})

    if found_user:
        reset_token = get_random_string()
        users_col.find_one_and_update(
            {"_id": ObjectId(id)}, {"$set": {"resetToken": reset_token}}
        )
        send_mail(
            email=found_user["email"],
            subject=f"Reset your password on {SITE_DATA["NAME"]}",
            message=f"""<p>Hello {found_user["fullName"]},
            <br /><br />To reset your password,
            <a href="{CLIENT_URI}/reset-password?id={found_user["_id"]}&token={reset_token}">
            click here
            </a>.</p>""",
        )
        return (
            jsonify(
                {
                    "message": f"An email was just sent to {found_user["fullName"]} to reset their password!"
                }
            ),
            200,
        )

    return jsonify({"message": "User not found"}), 400


@admin_bp.route(f"{BASE_API_URL}/delete-user/<id>", methods=["DELETE"])
def delete_user(id):
    """
    Deletes a user from the database by their ID.
    If the user is found, sends an email notification to the user's email address informing them that their account has been deleted.
    Then, deletes the user from the database and returns a success message with HTTP status 200.
    If the user is not found, returns an error message with HTTP status 400.
    Args:
        id (str): The unique identifier of the user to be deleted.
    Returns:
        tuple: A tuple containing a JSON response and an HTTP status code.
    """

    found_user = users_col.find_one({"_id": ObjectId(id)})

    if found_user:
        send_mail(
            email=found_user["email"],
            subject=f"Your account on {SITE_DATA["NAME"]} has been deleted",
            message=f"""<p>Your account on {SITE_DATA["NAME"]} has been deleted. If you think this is an error, please <a href="mailto:{EMAIL}">contact us</a>.</p>""",
        )
        users_col.find_one_and_delete({"_id": ObjectId(id)})
        return (
            jsonify({"message": f"User {found_user["fullName"]} has been deleted"}),
            200,
        )

    return jsonify({"message": "User not found"}), 400

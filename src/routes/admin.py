from flask import Blueprint, jsonify, request
from bson import ObjectId
from julseb_lib_python_utils.get_random_string import get_random_string
from utils.consts import BASE_API_URL, SITE_DATA, CLIENT_URI, EMAIL
from utils.send_mail import send_mail
from utils.connect_db import users_col

admin_bp = Blueprint("admin", __name__)
base_api_url = f"{BASE_API_URL}/admin"


@admin_bp.route(f"{base_api_url}/reset-password/<id>", methods=["POST"])
def reset_password(id):
    found_user = users_col.find_one({"_id": ObjectId(id)})

    if found_user:
        resetToken = get_random_string()
        users_col.find_one_and_update(
            {"_id": ObjectId(id)}, {"$set": {"resetToken": resetToken}}
        )
        send_mail(
            email=found_user["email"],
            subject=f"Reset your password on {SITE_DATA["NAME"]}",
            message=f"""<p>Hello {found_user["fullName"]},<br /><br />To reset your password, <a href="{CLIENT_URI}/reset-password?id={found_user["_id"]}&token={resetToken}">click here</a>.</p>""",
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


@admin_bp.route(f"{base_api_url}/delete-user/<id>", methods=["DELETE"])
def delete_user(id):
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

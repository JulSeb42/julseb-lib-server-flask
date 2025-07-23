"""Constant values from .env"""

import os
from dotenv import load_dotenv

load_dotenv()
TOKEN_SECRET = os.getenv("TOKEN_SECRET")
MONGODB_CLUSTER = os.getenv("MONGODB_CLUSTER")
MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME")
MONGODB_URI = os.getenv("MONGODB_URI")
CLIENT_URI = os.getenv("CLIENT_URI")
CLOUDINARY_CLOUD_NAME = os.getenv("CLOUDINARY_CLOUD_NAME")
CLOUDINARY_API_KEY = os.getenv("CLOUDINARY_API_KEY")
CLOUDINARY_API_SECRET = os.getenv("CLOUDINARY_API_SECRET")
CLOUDINARY_FOLDER = os.getenv("CLOUDINARY_FOLDER")
EMAIL = os.getenv("EMAIL")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

SITE_DATA = {"NAME": "julseb-lib-boilerplate-fullstack"}

BASE_API_URL = "/api"

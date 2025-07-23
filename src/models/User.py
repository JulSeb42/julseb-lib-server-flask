"""
This module defines the User model for MongoDB using MongoEngine.

Classes:
    Role (Enum): Enumeration for user roles ('admin', 'user').
    User (Document): MongoEngine document representing a user.

Attributes of User:
    fullName (str): The full name of the user. Required.
    email (str): The user's email address. Required and unique.
    password (str): The user's hashed password. Required.
    avatar (str): URL or path to the user's avatar image. Optional.
    role (str): The user's role, must be one of the values defined in Role. Required.
    created_at (datetime): Timestamp when the user was created. Defaults to current UTC time.
    updated_at (datetime): Timestamp when the user was last updated. Defaults to current UTC time.
"""

from mongoengine import Document, StringField, DateTimeField, BooleanField
from datetime import datetime, timezone
from enum import Enum


class Role(Enum):
    ADMIN = "admin"
    USER = "user"


class User(Document):
    fullName = StringField(required=True)
    email = StringField(required=True, unique=True)
    password = StringField(required=True)
    avatar = StringField()
    role = StringField(choices=[role.value for role in Role], required=True)
    verified = BooleanField(required=True)
    verifyToken = StringField(required=True)
    resetToken = StringField()
    created_at = DateTimeField(default=datetime.now(timezone.utc))
    updated_at = DateTimeField(default=datetime.now(timezone.utc))

"""
This module defines the User model for MongoDB using MongoEngine.

Classes:
    Role (Enum): Defines user roles ('admin', 'user').
    User (Document): Represents a user with fields for full name, email, password, avatar, role,
    verification status, tokens, and timestamps.

Attributes:
    fullName (str): The user's full name. Required.
    email (str): The user's email address. Required and unique.
    password (str): The user's hashed password. Required.
    avatar (str): URL or path to the user's avatar image. Optional.
    role (str): The user's role, either 'admin' or 'user'. Required.
    verified (bool): Indicates if the user's email is verified. Required.
    verifyToken (str): Token used for email verification. Required.
    resetToken (str): Token used for password reset. Optional.
    created_at (datetime): Timestamp when the user was created. Defaults to current UTC time.
    updated_at (datetime): Timestamp when the user was last updated. Defaults to current UTC time.
"""

from datetime import datetime, timezone
from enum import Enum
from mongoengine import Document, StringField, DateTimeField, BooleanField


class Role(Enum):
    """
    An enumeration representing user roles within the system.
    Attributes:
        ADMIN (str): Represents an administrator user with elevated privileges.
        USER (str): Represents a standard user with regular access rights.
    """

    ADMIN = "admin"
    USER = "user"


class User(Document):
    """
    User model representing application users.
    Attributes:
        fullName (StringField): The user's full name. Required.
        email (StringField): The user's email address. Must be unique. Required.
        password (StringField): The user's hashed password. Required.
        avatar (StringField): URL or path to the user's avatar image. Optional.
        role (StringField): The user's role in the system. Must be one of the predefined
        roles. Required.
        verified (BooleanField): Indicates if the user's email is verified. Required.
        verifyToken (StringField): Token used for email verification. Required.
        resetToken (StringField): Token used for password reset. Optional.
        created_at (DateTimeField): Timestamp when the user was created.
        Defaults to current UTC time.
        updated_at (DateTimeField): Timestamp when the user was last updated.
        Defaults to current UTC time.
    """

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

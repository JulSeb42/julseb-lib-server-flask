"""
This script seeds the MongoDB 'users' collection with a set of predefined and randomly generated user documents.

- Imports necessary modules for fake data generation, password hashing, and database connection.
- Defines two real user accounts (admin and user) with hashed passwords.
- Generates additional fake users using the Faker library, each with a unique email and random avatar.
- All users have timestamps for creation and last update.
- Inserts all user documents into the MongoDB collection and prints the number of users seeded.

Usage:
    Run this script to populate the 'users' collection for development or testing purposes.
"""

from faker import Faker
from datetime import datetime, timezone
from bcrypt import hashpw, gensalt
from julseb_lib_python_utils.get_random_avatar import get_random_avatar
from julseb_lib_python_utils.get_random_string import get_random_string
from utils.connect_db import users_col

fake = Faker()

from typing import Union

hashed_pw = hashpw("Password42".encode("utf-8"), gensalt(10))

real_users: list[dict[str, Union[str, datetime, bool]]] = [
    {
        "fullName": "Julien Admin",
        "email": "julien@admin.com",
        "password": str(hashed_pw.decode("utf-8").removeprefix("b")),
        "avatar": "",
        "role": "admin",
        "verified": True,
        "verifyToken": get_random_string(),
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
    },
    {
        "fullName": "Julien User",
        "email": "julien@user.com",
        "password": str(hashed_pw.decode("utf-8").removeprefix("b")),
        "avatar": "",
        "role": "user",
        "verified": True,
        "verifyToken": get_random_string(),
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
    },
]

NUM_USERS = 98

users = [*real_users]

for _ in range(NUM_USERS):
    user = {
        "fullName": fake.name(),
        "email": fake.unique.email(),
        "password": str(hashed_pw.decode("utf-8").removeprefix("b")),
        "avatar": get_random_avatar(),
        "role": "user",
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
        "verified": True,
        "verifyToken": get_random_string(),
    }
    users.append(user)

results = users_col.insert_many(users)
print(f"Seeded {len(results.inserted_ids)} users to MongoDB.")

# Run `PYTHONPATH=src python src/seed/seed_users.py` from the root folder

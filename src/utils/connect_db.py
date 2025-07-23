"""Connect to MongoDB
All variables for MongoDB
"""

from pymongo import MongoClient
from utils.consts import (
    MONGODB_CLUSTER,
    MONGODB_USERNAME,
    MONGODB_PW,
    MONGODB_DB_NAME,
    MONGODB_URI,
)

client = MongoClient(MONGODB_URI)
db = client[MONGODB_DB_NAME or ""]
users_col = db["users"]

print("🚀 DB connected")
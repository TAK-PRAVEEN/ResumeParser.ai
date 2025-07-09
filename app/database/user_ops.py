from .db import db
import bcrypt

users = db["users"]

def register_user(email, password):
    if users.find_one({"email": email}):
        return False, "Email already exists"
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    users.insert_one({"email": email, "password": hashed})
    return True, "User registered"

def validate_login(email, password):
    user = users.find_one({"email": email})
    if user and bcrypt.checkpw(password.encode(), user["password"]):
        return True
    return False

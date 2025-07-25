from .db import db
import bcrypt

users = db["users"]

def get_user_by_email(email):
    """
    Check if the user exists and return a boolean
    """
    return users.find_one({"email": email}) is not None

def register_user(email, password):
    """
    Register user and storing email & hashed password in MongoDB collection.
    """
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    result = users.insert_one({"email": email, "password": hashed})
    return result.inserted_id, "Successful insertion"  

def validate_login(email, password):
    """
    Validate Login user and gets email & hashed password from MongoDB collection.
    """
    user = users.find_one({"email": email})
    if user and bcrypt.checkpw(password.encode(), user["password"]):
        return True
    return False

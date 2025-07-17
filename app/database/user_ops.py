# from .db import db
# import bcrypt

# users = db["users"]

# def get_user_by_email(email):
#     if users.find_one({"email": email}):
#         return True, "Email already exists"
#     else:
#         return False

# def register_user(email, password):
#     hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
#     users.insert_one({"email": email, "password": hashed})
#     return True, "User registered"

# def validate_login(email, password):
#     user = users.find_one({"email": email})
#     if user and bcrypt.checkpw(password.encode(), user["password"]):
#         return True
#     return False

from .db import db
import bcrypt

users = db["users"]

def get_user_by_email(email):
    # Check if the user exists and return a boolean
    return users.find_one({"email": email}) is not None

def register_user(email, password):
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    result = users.insert_one({"email": email, "password": hashed})
    return result.inserted_id, "Successful insertion"  # You can return a message if needed

def validate_login(email, password):
    user = users.find_one({"email": email})
    if user and bcrypt.checkpw(password.encode(), user["password"]):
        return True
    return False

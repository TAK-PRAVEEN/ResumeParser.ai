from .db import db

resumes = db["resumes"]

def insert_resume(email, resume_data):
    """
    Insert the email and resume_data to MongoDB collection.
    """
    inserted = resumes.insert_one({"email": email, "resume": resume_data})
    print("Inserted ID:", inserted.inserted_id)
    return inserted.inserted_id

def get_format_resume(id, email, format):
    """
    Extract the fromatted file from MongoDB collection.
    """
    if format == "json":
        extracted = resumes.find_one({ "$and" : [{ "id": id }, { "email": email }]}, {"json": 1})
    elif format == "csv":
        extracted = resumes.find_one({ "$and" : [{ "id": id }, { "email": email }]}, {"csv": 1})
    elif format == "json":
        extracted = resumes.find_one({ "$and" : [{ "id": id }, { "email": email }]}, {"excel": 1})
    else:
        return "No data matched"
    return extracted

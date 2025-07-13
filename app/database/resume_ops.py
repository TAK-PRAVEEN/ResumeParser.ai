from .db import db
from bson.objectid import ObjectId

resumes = db["resumes"]

def insert_resume(email, resume_data):
    inserted = resumes.insert_one({"email": email, "resume": resume_data})
    print("Inserted ID:", inserted.inserted_id)
    return inserted.inserted_id

def get_resumes_by_email(email):
    return list(resumes.find({"email": email}))

def get_resume_by_id(resume_id):
    return resumes.find_one({"_id": ObjectId(resume_id)})

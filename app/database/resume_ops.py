from .db import db
from bson.objectid import ObjectId
from gridfs import GridFS
import tempfile
import os

resumes = db["resumes"]
fs = GridFS(db)

def insert_resume(email, resume_data):
    inserted = resumes.insert_one({"email": email, "resume": resume_data})
    print("Inserted ID:", inserted.inserted_id)
    return inserted.inserted_id

def save_file_to_db(email, file):
    # Save the resume file to GridFS
    file_id = fs.put(file.read(), filename=file.filename, content_type=file.content_type)
    # Optionally, you can also store the email with the file ID in the resumes collection
    resumes.insert_one({"email": email, "file_id": file_id})
    return str(file_id)

def get_file_from_db(file_id):
    grid_out = fs.get(ObjectId(file_id))
    file_bytes = grid_out.read()
    filename = grid_out.filename

    # Save temporarily in a known location
    temp_path = os.path.join(tempfile.gettempdir(), filename)
    with open(temp_path, "wb") as f:
        f.write(file_bytes)

    return temp_path

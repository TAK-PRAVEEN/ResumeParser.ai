from .db import db
# from bson.objectid import ObjectId

resumes = db["resumes"]

def insert_resume(id, email, resume_data, json_format, csv_format, excel_format):
    inserted = resumes.insert_one({"id": id, "email": email, "resume": resume_data, "json": json_format, "csv": csv_format, "excel": excel_format})
    print("Inserted ID:", inserted.inserted_id)
    return inserted.inserted_id

def get_format_resume(id, email, format):
    if format == "json":
        extracted = resumes.find_one({ "$and" : [{ "id": id }, { "email": email }]}, {"json": 1})
    elif format == "csv":
        extracted = resumes.find_one({ "$and" : [{ "id": id }, { "email": email }]}, {"csv": 1})
    elif format == "json":
        extracted = resumes.find_one({ "$and" : [{ "id": id }, { "email": email }]}, {"excel": 1})
    else:
        return "No data matched"
    return extracted

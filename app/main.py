from flask import Flask, request, jsonify, render_template, session, send_file, after_this_request
from database import db, user_ops, resume_ops
from resume_parser import ResumeParser
import os
import uuid
import logging
from werkzeug.utils import secure_filename
import json
import tempfile
import csv
import pandas as pd

base_path = os.path.abspath(os.path.dirname(__file__))
template_path = os.path.join(base_path, 'frontend', 'templates')
static_path = os.path.join(base_path, 'frontend', 'static')


logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__, template_folder=template_path, static_folder=static_path)
app.secret_key = "account123456789"

UPLOAD_DIR = os.path.join(os.getcwd(), 'uploads')
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.route('/')
def home():
    return render_template("home.html")

@app.route('/register', methods=['POST'])
def register():
    email = request.form.get('register-email') 
    password = request.form.get('register-password') 

    if not email or not password:
        return jsonify({'msg': 'Missing form fields'}), 400  # Add this for safety

    if user_ops.get_user_by_email(email):
        return jsonify({'msg': 'Email already exists'}), 409

    user_ops.register_user(email, password)
    session['user_email'] = email  # Store email in session
    return jsonify({'msg': 'Registration successful'}), 201

@app.route('/login', methods=['POST'])
def login():
    email = request.form.get('login-email')
    password = request.form.get('login-password')
    
    if not email or not password:
        return jsonify({'msg': 'Missing form fields'}), 400
    
    if user_ops.validate_login(email, password):
        session['user_email'] = email  # Store email in session
        return jsonify({'msg': 'Login Successful'}), 200  
    return jsonify({'msg': 'Invalid Email/Password'}), 401  

@app.route('/check_email', methods=['POST'])
def check_email():
    data = request.get_json()
    email = data.get('email')
    existing_user = user_ops.get_user_by_email(email)
    return jsonify({'exists': existing_user})

@app.route("/parsing", methods=["GET", "POST"])
def parsing():
    if request.method == "POST":
        if 'resume' not in request.files:
            return jsonify({'msg': 'No file part'}), 400
           
        file = request.files['resume']
        if file.filename == '':
            return jsonify({'msg': 'No selected file'}), 400
           
        # Save the file temporarily with a unique name
        unique_filename = f"{uuid.uuid4()}_{file.filename}"
        file_path = os.path.join(static_path, unique_filename)
        file.save(file_path)

        # Check if the file is empty
        if os.path.getsize(file_path) == 0:
            os.remove(file_path)  # Clean up the empty file
            return jsonify({'msg': 'Uploaded file is empty'}), 400

        # Use ResumeParser to parse the resume
        try:
            email = session.get('user_email')  # Retrieve email from session
            if not email:
                return jsonify({'msg': 'User  not logged in'}), 401  # Ensure user is logged in

            resume_data = ResumeParser(file_path).section_identification()

            print("Parsed Data:", resume_data)
            session['file_path'] = file_path  # Store the file path in session for download
            return jsonify(resume_data)  # Return parsed data as JSON
        except Exception as e:
            print("Error parsing resume:", e)
            return jsonify({'msg': 'Error parsing resume', 'error': str(e)}), 500
        finally:
            # Ensure the file is deleted after processing
            if os.path.exists(file_path):
                os.remove(file_path)
    return render_template('parsing.html')


@app.route('/upload', methods=['POST'])
def upload_resume():
    if 'resume' not in request.files:
        return jsonify({'msg': 'No file part'}), 400

    file = request.files['resume']
    if file.filename == '':
        return jsonify({'msg': 'No selected file'}), 400

    try:
        email = session.get('user_email')  # Retrieve email from session
        if not email:
            return jsonify({'msg': 'User  not logged in'}), 401  # Ensure user is logged in

        # Save the file to MongoDB
        file_id = resume_ops.save_file_to_db(email, file)

        # Store the file ID in the session for later retrieval
        session['file_id'] = file_id

        return jsonify({'msg': 'Uploaded and stored in MongoDB', 'file_id': file_id}), 200
    except Exception as e:
        logging.exception("Error in upload")
        return jsonify({'msg': 'Error', 'error': str(e)}), 500


@app.route("/download/<format>")
def download_file(format):
    file_id = session.get("file_id")  # Get the file ID from the session
    if not file_id:
        return jsonify({"error": "Missing file ID"}), 400

    try:
        # Retrieve the file from MongoDB
        file_path = resume_ops.get_file_from_db(file_id)

        # Use ResumeParser to convert the file to the requested format
        resume_parser = ResumeParser(file_path)
        if format == "json":
            output_path = resume_parser.json_format()
        elif format == "csv":
            output_path = resume_parser.csv_format()
        elif format == "excel":
            output_path = resume_parser.excel_format()
        else:
            return jsonify({"error": "Invalid format"}), 400

        return send_file(output_path, as_attachment=True)

    except Exception as e:
        logging.exception("Download failed")
        return jsonify({"error": "Server error", "details": str(e)}), 500

@app.route('/terms-and-conditions')
def terms():
    return render_template('Terms&Condition.html')

@app.route('/privacy-policy')
def privacy():
    return render_template('PrivacyPolicy.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

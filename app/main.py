from flask import Flask, request, jsonify, render_template, flash, redirect, session, url_for
from database import db, user_ops, resume_ops
from resume_parser import ResumeParser
import os

base_path = os.path.abspath(os.path.dirname(__file__))
template_path = os.path.join(base_path, 'frontend', 'templates')
static_path = os.path.join(base_path, 'frontend', 'static')

app = Flask(__name__, template_folder=template_path, static_folder=static_path)
app.secret_key = "account123456789"

@app.route('/')
def home():
    return render_template("home.html")

@app.route('/register', methods=['POST'])
def register():
    email = request.form.get('register-email') 
    password = request.form.get('register-password') 

    # if not email or not password:
    #     return jsonify({'msg': 'Missing form fields'}), 400  # Add this for safety

    if user_ops.get_user_by_email(email):
        return jsonify({'msg': 'Email already exists'}), 409

    user_ops.register_user(email, password)
    return jsonify({'msg': 'Registration successful'}), 201

@app.route('/login', methods=['POST'])
def login():
    email = request.form.get('login-email')
    password = request.form.get('login-password')
    
    if not email or not password:
        return jsonify({'msg': 'Missing form fields'}), 400
    
    if user_ops.validate_login(email, password):
        session['user_email'] = email  
        return jsonify({'msg': 'Login Successful'}), 200  
    return jsonify({'msg': 'Invalid Email/Password'}), 401  

@app.route('/check_email', methods=['POST'])
def check_email():
    data = request.get_json()
    email = data.get('email')
    existing_user = user_ops.get_user_by_email(email)
    return jsonify({'exists': existing_user})

import uuid

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
           return jsonify({'msg': 'Uploaded file is empty'}), 400
        # Use ResumeParser to parse the resume
        try:
            resume_data = ResumeParser(file_path).section_identification()
            print("Parsed Data:", resume_data)  # Debugging line to check the output
        finally:
            # Ensure the file is deleted after processing
            if os.path.exists(file_path):
                os.remove(file_path)

        # Render the template with the parsed data
        return render_template("parsing.html", resume_data=resume_data)
    else:
        return render_template("parsing.html")
   




@app.route('/terms-and-conditions')
def terms():
    return render_template('Terms&Condition.html')

@app.route('/privacy-policy')
def privacy():
    return render_template('PrivacyPolicy.html')

if __name__ == '__main__':
    app.run(debug=True)

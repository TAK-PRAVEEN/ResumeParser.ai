from flask import Flask, request, jsonify, render_template, session, send_file, redirect, url_for
from flask_dance.contrib.google import make_google_blueprint, google
from database import user_ops, resume_ops
from resume_parser import ResumeParser
import os
import uuid
import logging

base_path = os.path.abspath(os.path.dirname(__file__))
template_path = os.path.join(base_path, 'frontend', 'templates')
static_path = os.path.join(base_path, 'frontend', 'static')


logging.basicConfig(filename='app.log', level=logging.WARNING, format='%(asctime)s %(levelname)s %(message)s')

app = Flask(__name__, template_folder=template_path, static_folder=static_path)
app.secret_key = "account123456789"


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
        logging.debug("Just entered into parsing page")
        if 'resume' not in request.files:
            return jsonify({'msg': 'No file part'}), 400
           
        file = request.files['resume']
        if file.filename == '':
            return jsonify({'msg': 'No selected file'}), 400
           
        # Save the file temporarily with a unique name
        unique_filename = f"{file.filename}"

        uploads_dir = "uploads"
        os.makedirs(uploads_dir, exist_ok=True)

        file_path = os.path.join(uploads_dir, unique_filename)
        file.save(file_path)
        logging.debug(f"File Path =  {file_path}")
        
        # Use ResumeParser to parse the resume
        try:
            email = session.get('user_email')  # Retrieve email from session
            if not email:
                return jsonify({'msg': 'User  not logged in'}), 401  # Ensure user is logged in

            resume_data = ResumeParser(file_path).section_identification()
            logging.debug(f"Resume Data: {resume_data}")

            session['file_path'] = file_path  # Store the file path in session for download

            print("Parsed Data:", resume_data) 

            resume_ops.insert_resume(email, resume_data)
            logging.debug("Inserting the resume into mongodb.")
            return jsonify(resume_data)  # Return parsed data as JSON
        except Exception as e:
            print("Error parsing resume:", e)
            return jsonify({'msg': 'Error parsing resume', 'error': str(e)}), 500
        # finally:
        #     # Ensure the file is deleted after processing
        #     if os.path.exists(file_path):
        #         os.remove(file_path)
    return render_template('parsing.html')


@app.route('/upload', methods=['POST'])
def upload_resume():
    logging.debug("Wow just entered upload_resume function")
    if 'resume' not in request.files:
        return jsonify({'msg': 'No file part'}), 400

    file = request.files['resume']
    if file.filename == '':
        return jsonify({'msg': 'No selected file'}), 400

    try:
        email = session.get('user_email')  # Retrieve email from session
        if not email:
            return jsonify({'msg': 'User  not logged in'}), 401  # Ensure user is logged in
        
    except Exception as e:
        logging.exception("Error in upload")
        return jsonify({'msg': 'Error', 'error': str(e)}), 500


@app.route("/download")
def download_file():
    logging.debug("Wow just entered download_file function")
    try:
        format = request.args.get("format")
    
        logging.debug(f"Format = {format}")
        file_path = session.get('file_path')
        logging.debug(f"Going to convert the file {file_path}")
        
        resume_parser = ResumeParser(file_path)
        if format == "json":
            output_file = resume_parser.json_format()
        elif format == "csv":
            output_file = resume_parser.csv_format()
        elif format == "excel":
            output_file = resume_parser.excel_format()
        else:
            logging.error("Getting issue in fromatting of file.")
            return jsonify({"error": "Invalid format"}), 400
        
        uploads_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'uploads'))
        os.makedirs(uploads_dir, exist_ok=True)  # Create the directory if it doesn't exist

        output_path = os.path.join(uploads_dir, output_file)
        logging.debug("Format selected and going to download formatted file.")
        logging.debug(f"Output Path = {output_path}")

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

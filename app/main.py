from flask import Flask, request, jsonify, render_template, session, send_file, after_this_request
from database import db, user_ops, resume_ops
from resume_parser import ResumeParser
import os
import uuid
import logging
from werkzeug.utils import secure_filename

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
            resume_ops.insert_resume(email, resume_data)  # Store resume with associated email

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

    # Save the uploaded file to a temporary location
    filename = secure_filename(file.filename)
    unique_filename = f"{uuid.uuid4()}_{filename}"
    save_path = os.path.join(app.root_path, 'uploads', unique_filename)

    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    file.save(save_path)

    try:
        # Parse and generate output formats immediately
        resume_parser = ResumeParser(save_path)

        json_path = resume_parser.json_format()
        csv_path = resume_parser.csv_format()
        excel_path = resume_parser.excel_format()

        # Save generated paths to session
        session['json_path'] = json_path
        session['csv_path'] = csv_path
        session['excel_path'] = excel_path

        # Optionally remove the uploaded file after parsing
        os.remove(save_path)

        return jsonify({'msg': 'File uploaded and parsed successfully'}), 200
    except Exception as e:
        logging.exception("Error during resume parsing")
        return jsonify({'msg': 'Resume parsing failed', 'error': str(e)}), 500

@app.route('/download', methods=['GET'])
def download():
    format = request.args.get('format')
    file_path = session.get(f'{format}_path')  # e.g. 'json_path'

    if not file_path or not os.path.exists(file_path):
        return jsonify({'msg': 'Requested file not available'}), 400

    try:
        response = send_file(file_path, as_attachment=True)

        @after_this_request
        def cleanup(response):
            try:
                os.remove(file_path)
            except Exception as e:
                logging.error("Error deleting file: %s", e)
            return response

        return response
    except Exception as e:
        logging.exception("Error sending file")
        return jsonify({'msg': 'Download failed', 'error': str(e)}), 500

# @app.route('/download', methods=['GET'])
# def download():
#     format = request.args.get('format')
#     file_path = session.get('file_path')  # Get the file path from the session
#     if not file_path:
#         return jsonify({'msg': 'No file available for download'}), 400  # Ensure file is available

#     # Call the ResumeParser class to generate the file in the requested format
#     try:
#         resume_parser = ResumeParser(file_path)  # Initialize the parser with the file path

#         if format == 'json':
#             download_path = resume_parser.json_format()  # Generate the JSON file
#         elif format == 'csv':
#             download_path = resume_parser.csv_format()  # Generate the CSV file
#         elif format == 'excel':
#             download_path = resume_parser.excel_format()  # Generate the Excel file
#         else:
#             return jsonify({'msg': 'Invalid format'}), 400

#         # Check if the file exists and is not empty
#         if not os.path.exists(download_path):
#             return jsonify({'msg': 'Generated file does not exist'}), 500

#         # Serve the file for download
#         response = send_file(download_path, as_attachment=True)  # Send the file for download

#         # Delete the temporary file after sending
#         @after_this_request
#         def cleanup(response):
#             try:
#                 os.remove(download_path)
#             except Exception as e:
#                 logging.error("Error deleting temporary file: %s", e)
#             return response

#         return response
#     except Exception as e:
#         return jsonify({'msg': 'Error generating file', 'error': str(e)}), 500




@app.route('/terms-and-conditions')
def terms():
    return render_template('Terms&Condition.html')

@app.route('/privacy-policy')
def privacy():
    return render_template('PrivacyPolicy.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

from flask import Flask, request, jsonify, send_file, render_template
from werkzeug.utils import secure_filename
import os
# import parser
from database import db, resume_ops, user_ops
import uuid

base_path = os.path.abspath(os.path.dirname(__file__))
template_path = os.path.join(base_path, 'frontend', 'templates')
static_path = os.path.join(base_path, 'frontend', 'static')

app = Flask(__name__, template_folder=template_path, static_folder=static_path)
# UPLOAD_FOLDER = 'uploads'
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure upload directory exists
# os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def home():
    return render_template("home.html")

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('home.html')
    else:
        email = request.get.form('email')
        password = request.get.form('password')
        user_ops.register_user(email, password)
    
@app.route('/parsing')
def parsing():
    return render_template('parsing.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('home.html')
    else:
        email = request.get.form('email')
        password = request.get.form('password')
        if user_ops.register_user(email, password):
            return True
        else:
            return "Invalid Email/Password"

# @app.route('/upload', methods=['POST'])
# def upload_resume():
#     file = request.files.get('file')
#     email = request.form.get('email')
    
#     if not file or not email:
#         return jsonify({"error": "File and Email are required"}), 400

#     filename = secure_filename(file.filename)
#     filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
#     file.save(filepath)

#     # Parse and segment
#     raw_text = data_ingestion(filepath)
#     tokenized = preprocess(raw_text)
#     structured_data = section_identification(tokenized, raw_text)

#     # Save to DB
#     structured_data['email'] = email
#     structured_data['resume_id'] = str(uuid.uuid4())
#     save_to_mongo(structured_data)

#     # Save formats locally (optional)
#     csv_format(structured_data)
#     json_format(structured_data)
#     excel_format(structured_data)

#     return jsonify({
#         "message": "Resume processed and stored",
#         "resume_data": structured_data
#     }), 200

# @app.route('/get_resume', methods=['GET'])
# def get_resume():
#     email = request.args.get('email')
#     if not email:
#         return jsonify({"error": "Email is required"}), 400

#     data = get_resume_by_email(email)
#     if not data:
#         return jsonify({"error": "Resume not found"}), 404

#     return jsonify(data), 200

# @app.route('/download/<filetype>', methods=['GET'])
# def download_file(filetype):
#     if filetype == 'json':
#         path = "resume_data.json"
#     elif filetype == 'csv':
#         path = "resume_data.csv"
#     elif filetype == 'excel':
#         path = "resume_data.xlsx"
#     else:
#         return jsonify({"error": "Invalid filetype"}), 400

#     return send_file(path, as_attachment=True)

@app.route('/terms-and-conditions')
def terms():
    return render_template('Terms&Condition.html')

@app.route('/privacy-policy')
def privacy():
    return render_template('PrivacyPolicy.html')

if __name__ == '__main__':
    app.run(debug=True)

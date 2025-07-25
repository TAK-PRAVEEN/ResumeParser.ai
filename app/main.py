from flask import Flask, request, jsonify, render_template, session, send_file, redirect, url_for
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_dance.contrib.google import make_google_blueprint, google
from database import user_ops, resume_ops
from resume_parser import ResumeParser
import os
import logging
from dotenv import load_dotenv

load_dotenv()

base_path = os.path.abspath(os.path.dirname(__file__)) # gets the absolute path of the directory where the current script is located
template_path = os.path.join(base_path, 'frontend', 'templates') # constructs the path to the 'templates' directory within the 'frontend' directory
static_path = os.path.join(base_path, 'frontend', 'static') # constructs the path to the 'static' directory within the 'frontend' directory

logging.basicConfig(filename='app.log', level=logging.WARNING, format='%(asctime)s %(levelname)s %(message)s') # logging 

app = Flask(__name__, template_folder=template_path, static_folder=static_path)
app.secret_key = "account123456789"
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
    # Configures the WSGI middleware for handling proxies:
        # ProxyFix: helps Flask work correctly behind reverse proxies (like Nginx)
        # x_proto=1: tells Flask to trust the X-Forwarded-Proto header
        # x_host=1: tells Flask to trust the X-Forwarded-Host header

# Set up Google OAuth
client_id = os.getenv('GOOGLE_CLIENT_ID')
client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
google_bp = make_google_blueprint(
    client_id=client_id,
    client_secret=client_secret,
    scope=[
        "https://www.googleapis.com/auth/userinfo.profile", 
        "https://www.googleapis.com/auth/userinfo.email", 
        "openid"],
    redirect_url="/google_login"
)
app.register_blueprint(google_bp, url_prefix='/google_login')

@app.route('/')
def home():
    """
    Route to home.html.
    """
    return render_template("home.html")

@app.route('/register', methods=['POST'])
def register():
    """
    Handles the Register Modal for the Parsing Page.
    """
    email = request.form.get('register-email') 
    password = request.form.get('register-password') 

    if not email or not password:
        return jsonify({'msg': 'Missing form fields'}), 400 

    if user_ops.get_user_by_email(email):
        return jsonify({'msg': 'Email already exists'}), 409

    user_ops.register_user(email, password)
    session['user_email'] = email 
    return jsonify({'msg': 'Registration successful'}), 201

@app.route('/login', methods=['POST'])
def login():
    """
    Handles the Login Modal for the Parsing Page.
    """
    email = request.form.get('login-email')
    password = request.form.get('login-password')
    
    if not email or not password:
        return jsonify({'msg': 'Missing form fields'}), 400
    
    if user_ops.validate_login(email, password):
        session['user_email'] = email  
        return jsonify({'msg': 'Login Successful'}), 200  
    return jsonify({'msg': 'Invalid Email/Password'}), 401  

@app.route('/google_login')
def google_login():
    """
    Handles the Login through Google API for the Parsing Page.
    """
    if not google.authorized:
        return redirect(url_for('google.login'))
    
    try:
        resp = google.get('/oauth2/v2/userinfo')
        assert resp.ok, resp.text
        user_info = resp.json()
        
        email = email = user_info.get('email')
        if not email:
            return "Email not found in user info", 400  
        
        session['user_email'] = email

        if not user_ops.get_user_by_email(email):
            user_ops.register_user(email, "default_password")  
        
        return redirect(url_for('parsing')) 

    except Exception as e:
        return f"Error during login: {e}", 500  


@app.route('/check_email', methods=['POST'])
def check_email():
    """
    Checks the valid email through database module.
    """
    data = request.get_json()
    email = data.get('email')
    existing_user = user_ops.get_user_by_email(email)
    return jsonify({'exists': existing_user})

@app.route("/parsing", methods=["GET", "POST"])
def parsing():
    """
    Handles the parsing.html page.
    """
    if request.method == "POST":
        logging.debug("Just entered into parsing page")
        if 'resume' not in request.files:
            return jsonify({'msg': 'No file part'}), 400
           
        file = request.files['resume']
        if file.filename == '':
            return jsonify({'msg': 'No selected file'}), 400
           
        # Save the file
        unique_filename = f"{file.filename}"

        uploads_dir = "uploads"
        os.makedirs(uploads_dir, exist_ok=True)

        file_path = os.path.join(uploads_dir, unique_filename)
        file.save(file_path)
        logging.debug(f"File Path =  {file_path}")
        
        try:
            email = session.get('user_email')
            if not email:
                return jsonify({'msg': 'User  not logged in'}), 401

            resume_data = ResumeParser(file_path).section_identification()
            logging.debug(f"Resume Data: {resume_data}")

            session['file_path'] = file_path 

            print("Parsed Data:", resume_data) 

            resume_ops.insert_resume(email, resume_data)
            logging.debug("Inserting the resume into mongodb.")
            return jsonify(resume_data)  
        except Exception as e:
            print("Error parsing resume:", e)
            return jsonify({'msg': 'Error parsing resume', 'error': str(e)}), 500
    return render_template('parsing.html')

@app.route("/download")
def download_file():
    """
    Handles the download of formatted resume on parsing.html.
    """
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
            logging.error("Getting issue in formatting of file.")
            return jsonify({"error": "Invalid format"}), 400
        
        uploads_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'uploads'))
        os.makedirs(uploads_dir, exist_ok=True) 

        output_path = os.path.join(uploads_dir, output_file)
        logging.debug("Format selected and going to download formatted file.")
        logging.debug(f"Output Path = {output_path}")

        return send_file(output_path, as_attachment=True)
    
    except Exception as e:
        logging.exception("Download failed")
        return jsonify({"error": "Server error", "details": str(e)}), 500

@app.route('/terms-and-conditions')
def terms():
    """
    Handles Terms&Condition.html.
    """
    return render_template('Terms&Condition.html')

@app.route('/privacy-policy')
def privacy():
    """
    Handles PrivacyPolicy.html.
    """
    return render_template('PrivacyPolicy.html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)


from flask import Flask, request, jsonify, render_template, flash, redirect, session, url_for
from database import db, user_ops
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
    email = request.form.get('register-email')  # Must match input name
    password = request.form.get('register-password')  # Must match input name

    if not email or not password:
        return jsonify({'msg': 'Missing form fields'}), 400  # Add this for safety

    if user_ops.get_user_by_email(email):
        return jsonify({'msg': 'Email already exists'}), 409

    user_ops.register_user(email, password)
    return jsonify({'msg': 'Registration successful'}), 201

@app.route('/login', methods=['POST'])
def login():
    email = request.form.get('login-email')
    password = request.form.get('login-password')
    
    # Validate input
    if not email or not password:
        return jsonify({'msg': 'Missing form fields'}), 400
    
    # Check credentials
    if user_ops.validate_login(email, password):
        session['user_email'] = email  # Store user email in session
        return jsonify({'msg': 'Login Successful'}), 200  # Use 200 for success
    
    return jsonify({'msg': 'Invalid Email/Password'}), 401  # Use 401 for unauthorized


@app.route('/check_email', methods=['POST'])
def check_email():
    data = request.get_json()
    email = data.get('email')
    existing_user = user_ops.get_user_by_email(email)
    return jsonify({'exists': existing_user})

@app.route("/parsing", methods=["GET", "POST"])
def parsing():
    if request.method == "POST":
        # your code to parse and save to MongoDB
        return "Parsed and saved!"
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

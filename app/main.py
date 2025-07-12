from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import os
import uuid
from werkzeug.utils import secure_filename

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.urandom(24)  # Secret key for session management

# Configure upload folder
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Create upload folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def parse_resume(filepath):
    """
    Placeholder function for resume parsing logic.
    Replace this with your actual resume parsing implementation.
    """
    # This is where you would integrate your NLP/ML model for parsing
    return {
        'name': 'John Doe',
        'email': 'john@example.com',
        'skills': ['Python', 'Flask', 'Machine Learning'],
        'experience': ['Software Engineer at XYZ (2020-present)'],
        'education': ['BSc in Computer Science']
    }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash('No file selected')
        return redirect(url_for('index'))
    
    file = request.files['file']
    if file.filename == '':
        flash('No file selected')
        return redirect(url_for('index'))
    
    if file and allowed_file(file.filename):
        # Generate unique filename to prevent collisions
        filename = str(uuid.uuid4()) + '_' + secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Parse the resume
        try:
            parsed_data = parse_resume(filepath)
            return render_template('results.html', data=parsed_data)
        except Exception as e:
            flash(f'Error parsing resume: {str(e)}')
            return redirect(url_for('index'))
    else:
        flash('Allowed file types are pdf, doc, docx')
        return redirect(url_for('index'))

@app.route('/api/parse', methods=['POST'])
def api_parse():
    """
    API endpoint for resume parsing
    """
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if not file:
        return jsonify({'error': 'Empty file uploaded'}), 400
    
    if file and allowed_file(file.filename):
        filename = str(uuid.uuid4()) + '_' + secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        try:
            parsed_data = parse_resume(filepath)
            return jsonify({'success': True, 'data': parsed_data})
        except Exception as e:
            return jsonify({'error': f'Parsing error: {str(e)}'}), 500
    
    return jsonify({'error': 'Invalid file type'}), 400

if __name__ == '__main__':
    app.run(debug=True)

from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename
import os
import uuid
from datetime import datetime
import threading
from translate_and_fill_bubbles import process_comic_page
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'outputs'

# Ensure folders exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)
os.makedirs('static', exist_ok=True)

# Store translation jobs
translation_jobs = {}

# Supported languages
SUPPORTED_LANGUAGES = {
    'en': 'English',
    'ru': 'Russian',
    'es': 'Spanish',
    'fr': 'French',
    'de': 'German',
    'it': 'Italian',
    'pt': 'Portuguese',
    'ja': 'Japanese',
    'ko': 'Korean',
    'zh': 'Chinese',
    'ar': 'Arabic',
    'hi': 'Hindi'
}

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html', languages=SUPPORTED_LANGUAGES)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    source_lang = request.form.get('source_lang', 'en')
    target_lang = request.form.get('target_lang', 'ru')
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and allowed_file(file.filename):
        # Generate unique job ID
        job_id = str(uuid.uuid4())
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_filename = f"{timestamp}_{job_id}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(filepath)
        
        # Initialize job status
        translation_jobs[job_id] = {
            'status': 'processing',
            'progress': 0,
            'input_file': filepath,
            'output_file': None,
            'source_lang': source_lang,
            'target_lang': target_lang,
            'error': None
        }
        
        # Start translation in background thread
        thread = threading.Thread(
            target=process_translation,
            args=(job_id, filepath, source_lang, target_lang)
        )
        thread.start()
        
        return jsonify({'job_id': job_id}), 200
    
    return jsonify({'error': 'Invalid file type'}), 400

def process_translation(job_id, input_path, source_lang, target_lang):
    """Process the translation job in background"""
    try:
        # Update progress
        translation_jobs[job_id]['progress'] = 10
        
        # Generate output filename
        output_filename = f"translated_{job_id}.png"
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)
        
        # Get API key
        api_key = os.getenv("api_key")
        if not api_key:
            raise Exception("API key not configured")
        
        # Update progress
        translation_jobs[job_id]['progress'] = 30
        
        # Process the comic with language parameters
        process_comic_page_multilang(
            input_path, 
            output_path, 
            api_key,
            source_lang=SUPPORTED_LANGUAGES[source_lang],
            target_lang=SUPPORTED_LANGUAGES[target_lang]
        )
        
        # Update job status
        translation_jobs[job_id]['status'] = 'completed'
        translation_jobs[job_id]['progress'] = 100
        translation_jobs[job_id]['output_file'] = output_path
        
    except Exception as e:
        translation_jobs[job_id]['status'] = 'failed'
        translation_jobs[job_id]['error'] = str(e)

@app.route('/status/<job_id>')
def get_status(job_id):
    if job_id not in translation_jobs:
        return jsonify({'error': 'Job not found'}), 404
    
    job = translation_jobs[job_id]
    return jsonify({
        'status': job['status'],
        'progress': job['progress'],
        'error': job['error']
    })

@app.route('/download/<job_id>')
def download_result(job_id):
    if job_id not in translation_jobs:
        return jsonify({'error': 'Job not found'}), 404
    
    job = translation_jobs[job_id]
    if job['status'] != 'completed' or not job['output_file']:
        return jsonify({'error': 'Translation not ready'}), 400
    
    return send_file(
        job['output_file'],
        as_attachment=True,
        download_name=f"translated_comic_{job_id}.png"
    )

# Import and modify the process_comic_page function to support multiple languages
def process_comic_page_multilang(image_path, output_path, api_key, source_lang="English", target_lang="Russian"):
    """Wrapper to call process_comic_page with language parameters"""
    # This will be implemented by modifying the existing function
    # For now, we'll import the modified version
    from translate_and_fill_bubbles_multilang import process_comic_page_with_languages
    process_comic_page_with_languages(image_path, output_path, api_key, source_lang, target_lang)

if __name__ == '__main__':
    app.run(debug=True, port=5000) 
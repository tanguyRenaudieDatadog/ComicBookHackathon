import os
import sys

# Force headless mode for OpenCV BEFORE any imports
os.environ['QT_QPA_PLATFORM'] = 'offscreen'
os.environ['DISPLAY'] = ''
os.environ['OPENCV_OPENCL_RUNTIME'] = ''

from flask import Flask, render_template, request, jsonify, send_file, send_from_directory
from werkzeug.utils import secure_filename
import uuid
from datetime import datetime
import threading
import logging
from logging.handlers import RotatingFileHandler
from dotenv import load_dotenv
import asyncio

# Import translation modules
from translate_and_fill_bubbles_multilang import process_comic_page_with_languages
from translate_pdf_comic import translate_pdf_comic, images_to_pdf

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'outputs'

# Production configuration
if os.getenv('FLASK_ENV') == 'production':
    # Serve frontend build files in production
    frontend_build_path = os.path.join(os.path.dirname(__file__), 'frontend', 'out')
    if os.path.exists(frontend_build_path):
        app.static_folder = frontend_build_path
        app.static_url_path = '/'

# Configure logging
def setup_logging():
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)
    
    # Configure root logger
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Create app-specific logger
    logger = logging.getLogger('comic_translator')
    logger.setLevel(logging.INFO)
    
    # File handler with rotation
    file_handler = RotatingFileHandler(
        'logs/comic_translator.log',
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setFormatter(
        logging.Formatter('%(asctime)s [%(levelname)s] %(name)s: %(message)s')
    )
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(
        logging.Formatter('%(asctime)s [%(levelname)s] %(name)s: %(message)s')
    )
    
    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

# Initialize logger
logger = setup_logging()

# Ensure folders exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)
os.makedirs('static', exist_ok=True)

logger.info("Application folders initialized successfully")

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

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    # In production, serve the Next.js build
    if os.getenv('FLASK_ENV') == 'production':
        frontend_build_path = os.path.join(os.path.dirname(__file__), 'frontend', 'out')
        if os.path.exists(os.path.join(frontend_build_path, 'index.html')):
            return send_from_directory(frontend_build_path, 'index.html')
    
    # Fallback to Flask template
    return render_template('index.html', languages=SUPPORTED_LANGUAGES)

# Serve static assets for production
@app.route('/<path:path>')
def serve_static(path):
    if os.getenv('FLASK_ENV') == 'production':
        frontend_build_path = os.path.join(os.path.dirname(__file__), 'frontend', 'out')
        if os.path.exists(frontend_build_path):
            try:
                # First try to serve the exact file
                return send_from_directory(frontend_build_path, path)
            except:
                # If that fails, try to serve path/index.html for directory routes
                try:
                    index_path = os.path.join(path, 'index.html')
                    return send_from_directory(frontend_build_path, index_path)
                except:
                    # Final fallback to main index.html for SPA routing
                    return send_from_directory(frontend_build_path, 'index.html')
    
    # Fallback for development
    return jsonify({'error': 'Not found'}), 404

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        logger.warning("Upload attempt with no file part")
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    source_lang = request.form.get('source_lang', 'en')
    target_lang = request.form.get('target_lang', 'ru')
    
    if file.filename == '':
        logger.warning("Upload attempt with no selected file")
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
        
        logger.info(f"File uploaded successfully: {filename} (Job ID: {job_id})")
        
        # Initialize job status
        translation_jobs[job_id] = {
            'status': 'processing',
            'progress': 0,
            'input_file': filepath,
            'output_file': None,
            'source_lang': source_lang,
            'target_lang': target_lang,
            'error': None,
            'is_pdf': filename.lower().endswith('.pdf')
        }
        
        # Log translation task launch
        logger.info(f"🚀 LAUNCHING TRANSLATION TASK - Job ID: {job_id}, "
                   f"File: {filename}, Source: {SUPPORTED_LANGUAGES[source_lang]}, "
                   f"Target: {SUPPORTED_LANGUAGES[target_lang]}, "
                   f"Type: {'PDF' if filename.lower().endswith('.pdf') else 'Image'}")
        
        # Start translation in background thread
        thread = threading.Thread(
            target=process_translation,
            args=(job_id, filepath, source_lang, target_lang)
        )
        thread.start()
        
        logger.info(f"Translation thread started for job {job_id}")
        
        return jsonify({'job_id': job_id}), 200
    
    logger.warning(f"Invalid file type uploaded: {file.filename}")
    return jsonify({'error': 'Invalid file type'}), 400

def process_translation(job_id, input_path, source_lang, target_lang):
    """Process the translation job in background"""
    logger.info(f"Starting translation processing for job {job_id}")
    
    try:
        # Update progress
        translation_jobs[job_id]['progress'] = 10
        logger.debug(f"Job {job_id}: Progress updated to 10%")
        
        # Get API key
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            logger.error(f"Job {job_id}: API key not configured")
            raise Exception("API key not configured")
        
        # Update progress
        translation_jobs[job_id]['progress'] = 30
        logger.debug(f"Job {job_id}: Progress updated to 30%")
        
        # Check if this is a PDF
        is_pdf = translation_jobs[job_id]['is_pdf']
        logger.info(f"Job {job_id}: Processing {'PDF' if is_pdf else 'image'} file")
        
        if is_pdf:
            # Process PDF comic
            output_prefix = os.path.join(app.config['OUTPUT_FOLDER'], f"translated_{job_id}")
            logger.info(f"Job {job_id}: Starting PDF translation with output prefix: {output_prefix}")
            
            translated_files = translate_pdf_comic(
                input_path,
                output_prefix=output_prefix,
                temp_dir=f"temp_{job_id}_pages",
                debug=False,
                source_lang=SUPPORTED_LANGUAGES[source_lang],
                target_lang=SUPPORTED_LANGUAGES[target_lang]
            )
            
            if not translated_files:
                logger.error(f"Job {job_id}: Failed to translate PDF - no output files generated")
                raise Exception("Failed to translate PDF")
            
            logger.info(f"Job {job_id}: PDF translation completed, {len(translated_files)} pages processed")
            
            # Combine translated images back into PDF
            output_pdf = os.path.join(app.config['OUTPUT_FOLDER'], f"translated_{job_id}.pdf")
            logger.info(f"Job {job_id}: Combining images into PDF: {output_pdf}")
            images_to_pdf(translated_files, output_pdf)
            
            # Store both the PDF and individual images
            translation_jobs[job_id]['output_file'] = translated_files[0]  # First page for preview
            translation_jobs[job_id]['all_pages'] = translated_files
            translation_jobs[job_id]['pdf_file'] = output_pdf
            
            logger.info(f"Job {job_id}: PDF successfully created at {output_pdf}")
        else:
            # Process single image
            output_filename = f"translated_{job_id}.png"
            output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)
            
            logger.info(f"Job {job_id}: Starting image translation, output: {output_path}")
            
            try:
                # Process the comic with language parameters
                asyncio.run(process_comic_page_with_languages(
                    input_path, 
                    output_path, 
                    api_key,
                    source_lang=SUPPORTED_LANGUAGES[source_lang],
                    target_lang=SUPPORTED_LANGUAGES[target_lang]
                ))
                
                # Verify the output file was created
                if not os.path.exists(output_path):
                    logger.error(f"Job {job_id}: Translation completed but output file not found: {output_path}")
                    raise Exception(f"Translation completed but output file was not created: {output_path}")
                    
                logger.info(f"Job {job_id}: Image translation completed successfully at {output_path}")
                
            except Exception as translation_error:
                logger.error(f"Job {job_id}: Translation function failed: {str(translation_error)}")
                raise Exception(f"Translation failed: {str(translation_error)}")
            
            translation_jobs[job_id]['output_file'] = output_path
        
        # Update job status
        translation_jobs[job_id]['status'] = 'completed'
        translation_jobs[job_id]['progress'] = 100
        
        logger.info(f"✅ TRANSLATION COMPLETED - Job ID: {job_id}, "
                   f"Source: {SUPPORTED_LANGUAGES[source_lang]}, "
                   f"Target: {SUPPORTED_LANGUAGES[target_lang]}")
        
    except Exception as e:
        translation_jobs[job_id]['status'] = 'failed'
        translation_jobs[job_id]['error'] = str(e)
        logger.error(f"❌ TRANSLATION FAILED - Job ID: {job_id}, Error: {str(e)}")

@app.route('/status/<job_id>')
def get_status(job_id):
    if job_id not in translation_jobs:
        logger.warning(f"Status request for unknown job ID: {job_id}")
        return jsonify({'error': 'Job not found'}), 404
    
    job = translation_jobs[job_id]
    logger.debug(f"Status request for job {job_id}: {job['status']} ({job['progress']}%)")
    return jsonify({
        'status': job['status'],
        'progress': job['progress'],
        'error': job['error'],
        'is_pdf': job.get('is_pdf', False),
        'all_pages': job.get('all_pages', [])
    })

@app.route('/download/<job_id>')
def download_result(job_id):
    if job_id not in translation_jobs:
        logger.warning(f"Download request for unknown job ID: {job_id}")
        return jsonify({'error': 'Job not found'}), 404
    
    job = translation_jobs[job_id]
    if job['status'] != 'completed' or not job['output_file']:
        logger.warning(f"Download request for incomplete job {job_id}")
        return jsonify({'error': 'Translation not ready'}), 400
    
    logger.info(f"📥 File download initiated for job {job_id}: {job['output_file']}")
    
    return send_file(
        job['output_file'],
        as_attachment=True,
        download_name=f"translated_comic_{job_id}.png"
    )

@app.route('/download/all/<job_id>')
def download_all_pages(job_id):
    if job_id not in translation_jobs:
        logger.warning(f"Download all request for unknown job ID: {job_id}")
        return jsonify({'error': 'Job not found'}), 404
    
    job = translation_jobs[job_id]
    if job['status'] != 'completed':
        logger.warning(f"Download all request for incomplete job {job_id}")
        return jsonify({'error': 'Translation not ready'}), 400
    
    # For PDFs, return the combined PDF
    if job.get('is_pdf') and job.get('pdf_file'):
        logger.info(f"📥 PDF download initiated for job {job_id}: {job['pdf_file']}")
        return send_file(
            job['pdf_file'],
            as_attachment=True,
            download_name=f"translated_comic_{job_id}.pdf"
        )
    
    # For single images, return the image
    if job.get('output_file'):
        logger.info(f"📥 Image download initiated for job {job_id}: {job['output_file']}")
        return send_file(
            job['output_file'],
            as_attachment=True,
            download_name=f"translated_comic_{job_id}.png"
        )
    
    logger.error(f"No output file available for job {job_id}")
    return jsonify({'error': 'No output file available'}), 400

@app.route('/download/original/<job_id>')
def download_original(job_id):
    if job_id not in translation_jobs:
        logger.warning(f"Original download request for unknown job ID: {job_id}")
        return jsonify({'error': 'Job not found'}), 404

    job = translation_jobs[job_id]
    if job['status'] != 'completed':
        logger.warning(f"Original download request for incomplete job {job_id}")
        return jsonify({'error': 'Translation not ready'}), 400

    input_file = job.get('input_file')
    if not input_file or not os.path.exists(input_file):
        logger.error(f"Original file not found for job {job_id}")
        return jsonify({'error': 'Original file not found'}), 404

    # If the original is already a PDF, serve it directly
    if input_file.lower().endswith('.pdf'):
        logger.info(f"📥 Original PDF download for job {job_id}: {input_file}")
        return send_file(
            input_file,
            as_attachment=True,
            download_name=f"original_{job_id}.pdf"
        )

    # For images, convert to a single-page PDF so the reader handles it uniformly
    original_pdf = os.path.join(app.config['OUTPUT_FOLDER'], f"original_{job_id}.pdf")
    if not os.path.exists(original_pdf):
        try:
            images_to_pdf([input_file], original_pdf)
        except Exception as e:
            logger.error(f"Failed to convert original to PDF for job {job_id}: {e}")
            return jsonify({'error': 'Failed to convert original to PDF'}), 500

    logger.info(f"📥 Original (converted) PDF download for job {job_id}: {original_pdf}")
    return send_file(
        original_pdf,
        as_attachment=True,
        download_name=f"original_{job_id}.pdf"
    )

def process_comic_page_multilang(image_path, output_path, api_key, source_lang="English", target_lang="Russian"):
    """Wrapper to call process_comic_page_with_languages with async support"""
    asyncio.run(process_comic_page_with_languages(
        image_path, 
        output_path, 
        api_key,
        source_lang=source_lang,
        target_lang=target_lang
    ))

if __name__ == '__main__':
    logger.info("🚀 Starting Comic Translator Flask Application")
    
    # Railway configuration - ALWAYS bind to 0.0.0.0 for Railway
    port = int(os.getenv('PORT', 8080))
    host = '0.0.0.0'  # Always use 0.0.0.0 for Railway deployment
    debug = os.getenv('FLASK_ENV') != 'production'
    
    logger.info(f"Server will be available at http://{host}:{port}")
    logger.info(f"Upload folder: {app.config['UPLOAD_FOLDER']}")
    logger.info(f"Output folder: {app.config['OUTPUT_FOLDER']}")
    logger.info(f"Environment: {os.getenv('FLASK_ENV', 'development')}")
    
    app.run(debug=debug, host=host, port=port) 
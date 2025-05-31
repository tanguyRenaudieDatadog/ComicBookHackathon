# Comic Book Translator Web Application

A beautiful web interface for the Comic Book Translation system that allows users to upload comic pages and translate them between multiple languages.

## Features

- 🌐 **Multi-language Support**: Translate between 12 languages including English, Spanish, French, German, Italian, Portuguese, Russian, Japanese, Korean, Chinese, Arabic, and Hindi
- 📤 **Easy Upload**: Drag-and-drop or click to upload comic pages
- 🎨 **Beautiful UI**: Modern, comic-themed interface with animations
- 📊 **Real-time Progress**: Track translation progress with visual indicators
- 💾 **Download Results**: Download your translated comics with one click
- 🔄 **Context-Aware**: Uses accumulated context for better translations

## Setup

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Ensure the `.env` file exists** with your Llama API key:
   ```
   api_key=YOUR_LLAMA_API_KEY_HERE
   ```

3. **Make sure the YOLO model is downloaded** in `weights/ogkalu_model.pt`

## Running the Application

1. **Start the Flask server**:
   ```bash
   python app.py
   ```

2. **Open your browser** and navigate to:
   ```
   http://localhost:5000
   ```

## How to Use

1. **Select Languages**: Choose your source language (what the comic is written in) and target language (what you want to translate to)

2. **Upload Comic**: 
   - Click the upload area or drag-and-drop your comic page
   - Supported formats: PNG, JPG, JPEG, GIF, WEBP
   - Maximum file size: 16MB

3. **Start Translation**: Click the "Start Translation" button

4. **Wait for Processing**: Watch the progress bar and steps:
   - Detect Bubbles
   - Extract Text
   - Translate
   - Apply Text

5. **Download Result**: Once complete, download your translated comic

## API Endpoints

- `GET /` - Main web interface
- `POST /upload` - Upload comic and start translation
- `GET /status/<job_id>` - Check translation progress
- `GET /download/<job_id>` - Download translated comic

## File Structure

```
ComicBookHackathon/
├── app.py                          # Flask application
├── templates/
│   └── index.html                  # Web interface
├── static/
│   ├── css/
│   │   └── style.css              # Beautiful styling
│   └── js/
│       └── app.js                 # Frontend logic
├── uploads/                        # Uploaded comics (created automatically)
├── outputs/                        # Translated comics (created automatically)
└── translate_and_fill_bubbles_multilang.py  # Multi-language translation logic
```

## Supported Languages

- 🇬🇧 English
- 🇪🇸 Spanish
- 🇫🇷 French
- 🇩🇪 German
- 🇮🇹 Italian
- 🇵🇹 Portuguese
- 🇷🇺 Russian
- 🇯🇵 Japanese
- 🇰🇷 Korean
- 🇨🇳 Chinese
- 🇸🇦 Arabic
- 🇮🇳 Hindi

## Notes

- The application uses threading to handle translations in the background
- Each translation job gets a unique ID for tracking
- Uploaded files are temporarily stored and cleaned up after processing
- Font selection is automatic based on target language

## Troubleshooting

- **"API key not configured"**: Make sure your `.env` file contains the `api_key`
- **Font issues**: The app automatically selects appropriate fonts for each language
- **Upload errors**: Check file size (<16MB) and format
- **Translation fails**: Check console logs for detailed error messages 
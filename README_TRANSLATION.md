# Comic Book Translation Script

This script automatically detects speech bubbles in comic images, extracts text, translates it from English to Russian using Llama 4, and places the translated text back into the bubbles.

## Setup

1. **Create a `.env` file** in the ComicBookHackathon directory with your Llama API key:
   ```
   api_key=YOUR_LLAMA_API_KEY_HERE
   ```

2. **Install dependencies** (if not already installed):
   ```bash
   pip install ultralytics opencv-python pillow llama-api-client python-dotenv
   ```

3. **Ensure the model is downloaded** (should already be in `weights/ogkalu_model.pt`)

## Usage

Run the translation script:
```bash
python translate_and_fill_bubbles.py
```

The script will:
1. Detect all speech bubbles in `image.png`
2. Extract text from each bubble using Llama's vision capabilities
3. Translate the text from English to Russian
4. Draw white ellipses to cover the original text
5. Place the translated text into the bubbles

## Output

- `translated_comic_russian.png` - The translated comic image
- `translated_comic_russian_translations.json` - JSON file with all translations and bubble positions

## Features

- Automatic bubble detection using YOLOv8
- Text extraction using Llama 4's vision capabilities
- Translation using Llama 4
- Automatic text sizing and wrapping to fit bubbles
- Text centering in bubbles
- White outline on text for better visibility

## Customization

You can modify the script to:
- Change source/target languages
- Adjust font sizes
- Change text colors
- Use custom fonts (add font path in `draw_text_in_bubble` function) 
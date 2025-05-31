# Comic Book Translation Script

This script automatically detects speech bubbles in comic images, extracts text, translates it from English to Russian using Llama 4, and places the translated text back into the bubbles.

## Key Features

### Context-Aware Translation
The translation system now maintains context as it progresses through the comic:
- **Accumulating Context**: Each translated bubble is added to the context window
- **Better Consistency**: Character names and tone remain consistent throughout
- **Smart Ordering**: Bubbles are processed top-to-bottom, left-to-right for natural reading flow
- **Context Management**: Separate module handles context to keep code clean

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
2. Sort bubbles by reading order (top-to-bottom, left-to-right)
3. Extract text from each bubble using Llama's vision capabilities
4. Translate text with accumulating context for better accuracy
5. Draw white ellipses to cover the original text
6. Place the translated text into the bubbles

## Output

- `translated_comic_russian.png` - The translated comic image
- `translated_comic_russian_translations.json` - JSON file with all translations and context
- `translated_comic_russian_context.json` - Separate context file for reuse

## Context-Aware Translation

The system builds understanding as it reads:
- First bubbles translate with no context
- Each subsequent bubble benefits from previous translations
- Character names are detected and maintained consistently
- Dialogue tone and style remain coherent

## Features

- Automatic bubble detection using YOLOv8
- Text extraction using Llama 4's vision capabilities
- Context-aware translation using Llama 4
- Automatic text sizing and wrapping to fit bubbles
- Text centering in bubbles
- White outline on text for better visibility
- Context accumulation for improved translation quality

## Customization

You can modify the script to:
- Change source/target languages
- Adjust font sizes
- Change text colors
- Use custom fonts (add font path in `draw_text_in_bubble` function)
- Adjust context window size (default: 8 previous bubbles)
- Extend context extraction (locations, emotions, etc.) 
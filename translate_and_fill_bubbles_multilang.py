"""
Multi-language Comic Book Translation
Supports translation between any language pairs
"""
#%%
import os
# Force headless mode for OpenCV
os.environ['QT_QPA_PLATFORM'] = 'offscreen'
os.environ['DISPLAY'] = ''

import time
import base64
import asyncio
import uuid
from typing import List, Dict, Tuple
from PIL import Image, ImageDraw, ImageFont
import cv2
import numpy as np
from ultralytics import YOLO
from openai import OpenAI, AsyncOpenAI
from dotenv import load_dotenv
import textwrap
from translation_context import TranslationContext
import logging
logger = logging.getLogger('comic_translator')
# Load environment variables
load_dotenv()

def load_speech_bubble_model():
    """Load the finetuned YOLOv8 model for speech bubble detection"""
    try:
        model = YOLO('weights/ogkalu_model.pt')
        print("✅ Successfully loaded speech bubble detection model")
        return model
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        return None

def detect_speech_bubbles(model, image_path, conf_threshold=0.5):
    """Detect speech bubbles in an image using the loaded model"""
    results = model(image_path, conf=conf_threshold)
    
    bubble_data = []
    
    for result in results:
        boxes = result.boxes
        if boxes is not None:
            for i, box in enumerate(boxes):
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                confidence = box.conf[0].cpu().numpy()
                
                bubble_info = {
                    'bubble_id': i + 1,
                    'x': int(x1),
                    'y': int(y1),
                    'width': int(x2 - x1),
                    'height': int(y2 - y1),
                    'confidence': float(confidence),
                    'center_x': int((x1 + x2) / 2),
                    'center_y': int((y1 + y2) / 2)
                }
                bubble_data.append(bubble_info)
    
    print(f"🔍 Detected {len(bubble_data)} speech bubbles")
    return bubble_data

def encode_image(image_path):
    """Encode image to base64 for OpenAI API"""
    with open(image_path, "rb") as img:
        return base64.b64encode(img.read()).decode('utf-8')

def crop_bubble_region(image_path, bubble_info, padding=10, job_id=None):
    """Crop the bubble region from the image with some padding"""
    img = cv2.imread(image_path)

    x = max(0, bubble_info['x'] - padding)
    y = max(0, bubble_info['y'] - padding)
    x2 = min(img.shape[1], bubble_info['x'] + bubble_info['width'] + padding)
    y2 = min(img.shape[0], bubble_info['y'] + bubble_info['height'] + padding)

    cropped = img[y:y2, x:x2]

    # Save temporary cropped image with unique prefix to avoid collisions
    prefix = job_id or uuid.uuid4().hex[:8]
    temp_path = f"temp_bubble_{prefix}_{bubble_info['bubble_id']}.png"
    cv2.imwrite(temp_path, cropped)

    return temp_path

def extract_text_from_bubble(client, bubble_image_path, bubble_info):
    """Extract text from a single bubble using OpenAI's vision capabilities"""
    base64_image = encode_image(bubble_image_path)

    prompt = """Extract ONLY the text content from this speech bubble.
    Return just the text, nothing else. If there's no text, return 'EMPTY'.
    Do not include any explanations or additional information."""

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt,
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            },
                        },
                    ],
                },
            ],
        )

        extracted_text = response.choices[0].message.content.strip()

        # Clean up temporary file
        os.remove(bubble_image_path)

        return extracted_text
    except Exception as e:
        print(f"Error extracting text from bubble {bubble_info['bubble_id']}: {e}")
        if os.path.exists(bubble_image_path):
            os.remove(bubble_image_path)
        return "ERROR"


async def extract_text_from_bubble_async(client: AsyncOpenAI, bubble_image: os.PathLike, bubble: dict):
    base64_image = encode_image(bubble_image)

    prompt = """Extract ONLY the text content from this speech bubble.
    Return just the text, nothing else. If there's no text, return 'EMPTY'.
    Do not include any explanations or additional information."""

    messages = [
        {
            "role": "system",
            "content": "You are a helpful assistant that provides concise answers."
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": prompt,
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_image}"
                    }
                }
            ]
        }
    ]

    try:
        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
        )
        extracted_text = response.choices[0].message.content.strip()
        # Clean up temporary file
        os.remove(bubble_image)

        return extracted_text
    except Exception as e:
        print(f"Error extracting text from bubble {bubble['bubble_id']}: {e}")
        if os.path.exists(bubble_image):
            os.remove(bubble_image)
        return "ERROR"


def translate_text(client, text, context_manager=None, bubble_id=None, source_lang="English", target_lang="Russian", debug=False):
    """Translate text using OpenAI with context awareness"""
    if text in ["EMPTY", "ERROR"]:
        return text

    # Build context-aware prompt
    prompt_parts = []

    # Add context if available
    if context_manager:
        context_prompt = context_manager.get_context_prompt(max_previous_bubbles=8)
        if context_prompt:
            prompt_parts.append("You are translating a comic book. Here's the context so far:")
            prompt_parts.append(context_prompt)
            prompt_parts.append("\n" + "="*50 + "\n")

    prompt_parts.append(f"""Now translate the following text to {target_lang}.
    The user indicated the source language is {source_lang}, but detect the actual language of the text.
    If the text is in a different language than {source_lang}, translate from the detected language instead.
    Consider the context and maintain consistency with character names and tone.
    Return ONLY the translated text, nothing else.
    Keep the translation natural and appropriate for comic book dialogue.

    Text to translate: {text}""")

    prompt = "\n".join(prompt_parts)

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
        )

        translated = response.choices[0].message.content.strip()
        return translated
    except Exception as e:
        if debug:
            print(f"Error translating text: {e}")
        return text

async def translate_text_async(client, text, context_manager=None, bubble_id=None, source_lang="English", target_lang="Russian", debug=False):
    """Translate text using OpenAI with context awareness"""
    if text in ["EMPTY", "ERROR"]:
        return text

    # Build context-aware prompt
    prompt_parts = []

    # Add context if available
    if context_manager:
        context_prompt = context_manager.get_context_prompt(max_previous_bubbles=8)
        if context_prompt:
            prompt_parts.append("You are translating a comic book. Here's the context so far:")
            prompt_parts.append(context_prompt)
            prompt_parts.append("\n" + "="*50 + "\n")

    prompt_parts.append(f"""Now translate the following text to {target_lang}.
    The user indicated the source language is {source_lang}, but detect the actual language of the text.
    If the text is in a different language than {source_lang}, translate from the detected language instead.
    Consider the context and maintain consistency with character names and tone.
    Return ONLY the translated text, nothing else.
    Keep the translation natural and appropriate for comic book dialogue.

    Text to translate: {text}""")

    prompt = "\n".join(prompt_parts)

    try:
        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
        )
        translated = response.choices[0].message.content.strip()
        return translated
    except Exception as e:
        if debug:
            print(f"Error translating text: {e}")
        return text

#%%
def _find_matplotlib_font():
    """Find the DejaVuSans font bundled with matplotlib as ultimate fallback"""
    try:
        import matplotlib
        mpl_data = os.path.join(os.path.dirname(matplotlib.__file__), 'mpl-data', 'fonts', 'ttf')
        dejavu = os.path.join(mpl_data, 'DejaVuSans.ttf')
        if os.path.exists(dejavu):
            return dejavu
    except ImportError:
        pass
    return None

def get_font_for_language(target_lang):
    """Select appropriate font based on target language"""
    # Language-specific font mappings (macOS + Linux paths)
    font_mappings = {
        'Japanese': [
            '/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc',
            '/System/Library/Fonts/Hiragino Sans GB.ttc',
            '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',
            '/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc',
            '/usr/share/fonts/noto-cjk/NotoSansCJK-Regular.ttc',
        ],
        'Chinese': [
            '/System/Library/Fonts/PingFang.ttc',
            '/System/Library/Fonts/STHeiti Light.ttc',
            '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',
            '/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc',
            '/usr/share/fonts/noto-cjk/NotoSansCJK-Regular.ttc',
        ],
        'Korean': [
            '/System/Library/Fonts/AppleSDGothicNeo.ttc',
            '/System/Library/Fonts/NanumGothic.ttc',
            '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',
            '/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc',
            '/usr/share/fonts/noto-cjk/NotoSansCJK-Regular.ttc',
        ],
        'Arabic': [
            '/System/Library/Fonts/GeezaPro.ttc',
            '/System/Library/Fonts/Baghdad.ttc',
            '/usr/share/fonts/truetype/noto/NotoSansArabic-Regular.ttf',
            '/usr/share/fonts/noto/NotoSansArabic-Regular.ttf',
        ],
        'Hindi': [
            '/System/Library/Fonts/Kohinoor.ttc',
            '/System/Library/Fonts/DevanagariMT.ttc',
            '/usr/share/fonts/truetype/noto/NotoSansDevanagari-Regular.ttf',
            '/usr/share/fonts/noto/NotoSansDevanagari-Regular.ttf',
        ],
        'Russian': [
            '/Library/Fonts/Arial Unicode.ttf',
            '/System/Library/Fonts/Helvetica.ttc',
            '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
            '/usr/share/fonts/truetype/freefont/FreeSans.ttf',
        ],
    }

    # Default fonts (macOS + Linux)
    default_fonts = [
        "/Library/Fonts/Arial Unicode.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "/System/Library/Fonts/HelveticaNeue.ttc",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ]

    # Get fonts for the target language
    language_fonts = font_mappings.get(target_lang, [])
    all_fonts = language_fonts + default_fonts

    # Find first available font
    for font_path in all_fonts:
        if os.path.exists(font_path):
            return font_path

    # Ultimate fallback: matplotlib's bundled DejaVuSans
    mpl_font = _find_matplotlib_font()
    if mpl_font:
        return mpl_font

    return None

def draw_text_in_bubble(draw, text, bubble_info, target_lang="English", max_font_size=40, debug=False):
    """Draw text inside a bubble, automatically wrapping and sizing to fit"""
    x = bubble_info['x']
    y = bubble_info['y']
    width = bubble_info['width']
    height = bubble_info['height']
    
    # Get appropriate font for language
    font_path = get_font_for_language(target_lang)
    
    # Start with a large font and decrease until text fits
    font_size = max_font_size
    
    while font_size > 8:
        try:
            if font_path:
                font = ImageFont.truetype(font_path, font_size)
                if debug:
                    print(f"Using font: {font_path} for {target_lang}")
            else:
                font = ImageFont.load_default()
                if debug:
                    print(f"⚠️ Warning: No appropriate font found for {target_lang}")
        except:
            font = ImageFont.load_default()
        
        # Wrap text to fit width
        avg_char_width = font_size * 0.6
        max_chars_per_line = int(width * 0.8 / avg_char_width)
        
        if max_chars_per_line > 0:
            wrapped_lines = textwrap.fill(text, width=max_chars_per_line).split('\n')
        else:
            wrapped_lines = [text]
        
        # Calculate total text height
        line_height = font_size * 1.2
        total_height = len(wrapped_lines) * line_height
        
        # Check if text fits in bubble
        if total_height <= height * 0.8:
            # Center text in bubble
            text_y = y + (height - total_height) / 2
            
            for line in wrapped_lines:
                # Get text width for centering
                bbox = draw.textbbox((0, 0), line, font=font)
                text_width = bbox[2] - bbox[0]
                text_x = x + (width - text_width) / 2
                
                # Draw text with outline for better visibility
                # Draw outline
                for dx in [-1, 0, 1]:
                    for dy in [-1, 0, 1]:
                        if dx != 0 or dy != 0:
                            draw.text((text_x + dx, text_y + dy), line, font=font, fill='white')
                
                # Draw main text
                draw.text((text_x, text_y), line, font=font, fill='black')
                
                text_y += line_height
            
            return True
        
        font_size -= 2
    
    # If text doesn't fit, draw it anyway with smallest font
    draw.text((x + 5, y + 5), text[:20] + "...", font=font, fill='black')
    return False
#%%
async def process_comic_page_with_languages(image_path, output_path, api_key=None, source_lang="English", target_lang="Russian", debug=False):
    """Main function to process a comic page with multi-language support"""
    
    # Load bubble detection model
    bubble_model = load_speech_bubble_model()
    if not bubble_model:
        logger.error("Failed to load speech bubble detection model")
        return
    
    # Detect bubbles
    logger.info("📍 Detecting speech bubbles...")
    bubble_data = detect_speech_bubbles(bubble_model, image_path, conf_threshold=0.3)
    
    # Sort bubbles by position (top to bottom, left to right) for better context flow
    bubble_data.sort(key=lambda b: (b['y'], b['x']))
    
    if not bubble_data:
        logger.warning("No speech bubbles detected in the image")
        return
    
    # Extract text from each bubble using async approach
    logger.info("📖 Extracting text from bubbles asynchronously...")
    client = AsyncOpenAI()
    t0_extract = time.time()
    
    # Create tasks for text extraction
    extraction_tasks = []
    for bubble in bubble_data:
        bubble_image = crop_bubble_region(image_path, bubble)
        extraction_tasks.append(extract_text_from_bubble_async(client, bubble_image, bubble))
    
    # Execute all extraction tasks
    extraction_results = await asyncio.gather(*extraction_tasks)
    tf_extract = time.time()
    logger.info(f"Time taken to extract text from bubbles: {tf_extract - t0_extract:.2f} seconds")
    
    # Assign extracted text to bubbles and build translation context
    context_manager = TranslationContext()
    for i, bubble in enumerate(bubble_data):
        bubble['original_text'] = extraction_results[i]
        logger.info(f"Bubble {bubble['bubble_id']}: {bubble['original_text']}")
        # Add original text to context so all translations see surrounding dialogue
        if bubble['original_text'] not in ["EMPTY", "ERROR"]:
            context_manager.add_bubble_to_context(bubble['bubble_id'], bubble['original_text'])

    # Translate texts asynchronously
    logger.info(f"🌐 Translating from {source_lang} to {target_lang}...")
    t0_translate = time.time()

    # Create translation tasks only for bubbles with text
    translation_tasks = []
    translation_indices = []  # Track which bubbles are being translated

    for i, bubble in enumerate(bubble_data):
        if bubble['original_text'] not in ["EMPTY", "ERROR"]:
            translation_tasks.append(translate_text_async(
                client,
                bubble['original_text'],
                context_manager=context_manager,
                bubble_id=bubble['bubble_id'],
                source_lang=source_lang,
                target_lang=target_lang,
                debug=debug
            ))
            translation_indices.append(i)
        else:
            logger.info(f"Bubble {bubble['bubble_id']} is empty or error. Skipping translation.")
            bubble['translated_text'] = bubble['original_text']

    # Execute translation tasks if any exist
    if translation_tasks:
        translation_results = await asyncio.gather(*translation_tasks)

        # Assign translation results to the correct bubbles
        for task_index, bubble_index in enumerate(translation_indices):
            bubble_data[bubble_index]['translated_text'] = translation_results[task_index]
            if debug:
                logger.info(f"✓ {bubble_data[bubble_index]['original_text']} → {bubble_data[bubble_index]['translated_text']}")
    
    await client.close()
    
    tf_translate = time.time()
    translated_count = len(translation_tasks)
    logger.info(f"Time taken to translate {translated_count} bubbles: {tf_translate - t0_translate:.2f} seconds")
    
    # Create image with white bubbles
    logger.info("🎨 Creating output image...")
    img = Image.open(image_path).convert("RGBA")
    draw = ImageDraw.Draw(img)
    
    # First, draw white ellipses to cover original text
    for bubble in bubble_data:
        if bubble['original_text'] not in ["EMPTY", "ERROR"]:
            # Calculate ellipse parameters
            center_x = bubble['center_x']
            center_y = bubble['center_y']
            
            padding_factor = 0.98
            semi_major = (bubble['width'] / 2) * padding_factor
            semi_minor = (bubble['height'] / 2) * padding_factor
            
            left = center_x - semi_major
            top = center_y - semi_minor
            right = center_x + semi_major
            bottom = center_y + semi_minor
            
            # Draw white filled ellipse
            draw.ellipse([left, top, right, bottom], fill='white', outline='white')
    
    # Then, draw translated text
    for bubble in bubble_data:
        if bubble.get('translated_text') and bubble['translated_text'] not in ["EMPTY", "ERROR"]:
            draw_text_in_bubble(draw, bubble['translated_text'], bubble, target_lang, debug=debug)
    
    # Save result
    img.save(output_path)
    logger.info(f"✅ Saved translated comic to: {output_path}")
    
    # Log final summary
    total_bubbles = len(bubble_data)
    translated_bubbles = len([b for b in bubble_data if b['original_text'] not in ["EMPTY", "ERROR"]])
    logger.info(f"📊 Translation complete: {translated_bubbles}/{total_bubbles} bubbles processed")

#%%
# Example usage
if __name__ == "__main__":
    import sys
    
    # Check for debug flag
    debug_mode = "--debug" in sys.argv
    if debug_mode:
        sys.argv.remove("--debug")
    
    if len(sys.argv) < 2:
        print("Usage: python translate_and_fill_bubbles_multilang.py <image_path> [output_path] [--debug]")
        print("       --debug    Show detailed translation information")
        sys.exit(1)
    
    image_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else "translated_" + os.path.basename(image_path)
    
    if debug_mode:
        print("🐛 Debug mode enabled - showing detailed translation")
    
    process_comic_page_with_languages(image_path, output_path, debug=debug_mode) 
# %%

"""
Enhanced Comic Book Translation with Multimodal Context Understanding
Uses Llama4's vision capabilities for comprehensive page-level context awareness
"""

import os
import json
import base64
from typing import List, Dict, Tuple
from PIL import Image, ImageDraw, ImageFont
import cv2
import numpy as np
from ultralytics import YOLO
from llama_api_client import LlamaAPIClient
from dotenv import load_dotenv
import textwrap
from translation_context import MultimodalTranslationContext

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
    """Encode image to base64 for Llama API"""
    with open(image_path, "rb") as img:
        return base64.b64encode(img.read()).decode('utf-8')

def crop_bubble_region(image_path, bubble_info, padding=10):
    """Crop the bubble region from the image with some padding"""
    img = cv2.imread(image_path)
    
    x = max(0, bubble_info['x'] - padding)
    y = max(0, bubble_info['y'] - padding)
    x2 = min(img.shape[1], bubble_info['x'] + bubble_info['width'] + padding)
    y2 = min(img.shape[0], bubble_info['y'] + bubble_info['height'] + padding)
    
    cropped = img[y:y2, x:x2]
    
    # Save temporary cropped image
    temp_path = f"temp_bubble_{bubble_info['bubble_id']}.png"
    cv2.imwrite(temp_path, cropped)
    
    return temp_path

def extract_text_from_bubble(client, bubble_image_path, bubble_info):
    """Extract text from a single bubble using Llama's vision capabilities"""
    base64_image = encode_image(bubble_image_path)
    
    prompt = """Extract ONLY the text content from this speech bubble. 
    Return just the text, nothing else. If there's no text, return 'EMPTY'.
    Do not include any explanations or additional information."""
    
    try:
        response = client.chat.completions.create(
            model="Llama-4-Maverick-17B-128E-Instruct-FP8",
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
        
        extracted_text = response.completion_message.content.text.strip()
        
        # Clean up temporary file
        os.remove(bubble_image_path)
        
        return extracted_text
    except Exception as e:
        print(f"Error extracting text from bubble {bubble_info['bubble_id']}: {e}")
        if os.path.exists(bubble_image_path):
            os.remove(bubble_image_path)
        return "ERROR"

def translate_text(client, text, context_manager=None, bubble_id=None, source_lang="English", target_lang="Russian"):
    """Translate text using Llama with context awareness"""
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
    
    prompt_parts.append(f"""Now translate the following {source_lang} text to {target_lang}.
Consider the context and maintain consistency with character names and tone.
Return ONLY the translated text, nothing else.
Keep the translation natural and appropriate for comic book dialogue.

Text to translate: {text}""")
    
    prompt = "\n".join(prompt_parts)
    
    try:
        response = client.chat.completions.create(
            model="Llama-4-Maverick-17B-128E-Instruct-FP8",
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
        )
        
        translated = response.completion_message.content.text.strip()
        
        # Add to context after successful translation
        if context_manager and bubble_id:
            context_manager.add_bubble_to_context(bubble_id, text, translated)
        
        return translated
    except Exception as e:
        print(f"Error translating text: {e}")
        return text

def get_font_for_language(target_lang):
    """Select appropriate font based on target language"""
    # Language-specific font mappings
    font_mappings = {
        'Japanese': ['/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc', '/System/Library/Fonts/Hiragino Sans GB.ttc'],
        'Chinese': ['/System/Library/Fonts/PingFang.ttc', '/System/Library/Fonts/STHeiti Light.ttc'],
        'Korean': ['/System/Library/Fonts/AppleSDGothicNeo.ttc', '/System/Library/Fonts/NanumGothic.ttc'],
        'Arabic': ['/System/Library/Fonts/GeezaPro.ttc', '/System/Library/Fonts/Baghdad.ttc'],
        'Hindi': ['/System/Library/Fonts/Kohinoor.ttc', '/System/Library/Fonts/DevanagariMT.ttc'],
        'Russian': ['/Library/Fonts/Arial Unicode.ttf', '/System/Library/Fonts/Helvetica.ttc']
    }
    
    # Default fonts for other languages
    default_fonts = [
        "/Library/Fonts/Arial Unicode.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "/System/Library/Fonts/HelveticaNeue.ttc"
    ]
    
    # Get fonts for the target language
    language_fonts = font_mappings.get(target_lang, [])
    all_fonts = language_fonts + default_fonts
    
    # Find first available font
    for font_path in all_fonts:
        if os.path.exists(font_path):
            return font_path
    
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

def process_comic_page_multimodal(image_path, output_path, api_key=None, source_lang="English", 
                                target_lang="Russian", page_number=1, context_manager=None, debug=False):
    """
    Enhanced comic page processing with page-level multimodal context understanding
    """
    # Initialize Llama client
    client = LlamaAPIClient(
        api_key=api_key or os.environ.get("LLAMA_API_KEY")
    )
    
    # Initialize or use existing context manager
    if context_manager is None:
        context_manager = MultimodalTranslationContext(client)
    
    # Load bubble detection model
    bubble_model = load_speech_bubble_model()
    if not bubble_model:
        return context_manager
    
    if debug:
        print(f"\n🧠 Analyzing page {page_number} context with multimodal AI...")
    else:
        print(f"\n🧠 Analyzing page {page_number} with AI...")
    
    # Analyze the entire page for context (this is the main analysis)
    page_context = context_manager.analyze_page_context(image_path, page_number)
    
    if debug:
        print(f"✓ Page analysis complete:")
        print(f"  📍 Location: {page_context.location}")
        print(f"  🎭 Genre: {page_context.genre}")
        print(f"  😊 Mood: {page_context.mood}")
        print(f"  👥 Characters: {', '.join(page_context.characters_present) if page_context.characters_present else 'None identified'}")
    else:
        print(f"✓ Page context analyzed - {page_context.genre} genre")
    
    # Detect bubbles
    print(f"\n📍 Detecting speech bubbles...")
    bubble_data = detect_speech_bubbles(bubble_model, image_path, conf_threshold=0.3)
    
    # Sort bubbles by position (top to bottom, left to right) for better context flow
    bubble_data.sort(key=lambda b: (b['y'], b['x']))
    
    # Extract and translate text from each bubble using page context
    if debug:
        print(f"\n📖 Extracting and translating text with page context...")
    else:
        print(f"\n📖 Translating {len(bubble_data)} bubbles...")
    
    for i, bubble in enumerate(bubble_data):
        # Crop bubble region for text extraction
        bubble_image = crop_bubble_region(image_path, bubble)
        
        # Extract text
        original_text = extract_text_from_bubble(client, bubble_image, bubble)
        bubble['original_text'] = original_text
        
        if original_text not in ["EMPTY", "ERROR"]:
            # Identify likely speaker using page context
            speaker, emotion = context_manager.identify_speaker_for_bubble(bubble, original_text)
            
            if debug:
                print(f"\nBubble {bubble['bubble_id']}:")
                print(f"  Original: {original_text}")
                print(f"  Speaker: {speaker}")
                print(f"  Scene: {page_context.scene_description}")
            else:
                print(f"Bubble {bubble['bubble_id']}: {original_text[:50]}{'...' if len(original_text) > 50 else ''}")
            
            # Get enhanced translation prompt with page context
            translation_prompt = context_manager.get_enhanced_translation_prompt(
                original_text, bubble, source_lang=source_lang, target_lang=target_lang
            )
            
            # Translate with rich context
            try:
                response = client.chat.completions.create(
                    model="Llama-4-Maverick-17B-128E-Instruct-FP8",
                    messages=[{"role": "user", "content": translation_prompt}]
                )
                translated_text = response.completion_message.content.text.strip()
                bubble['translated_text'] = translated_text
                
                if debug:
                    print(f"  Translated: {translated_text}")
                else:
                    print(f"→ {translated_text[:50]}{'...' if len(translated_text) > 50 else ''}")
                
                # Add to context
                context_manager.add_bubble_to_context(
                    bubble['bubble_id'], original_text, translated_text, bubble
                )
                
            except Exception as e:
                print(f"  Error translating: {e}")
                bubble['translated_text'] = original_text
        else:
            bubble['translated_text'] = original_text
    
    # Create image with white bubbles and translated text
    print(f"\n🎨 Creating output image...")
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
        if bubble['translated_text'] not in ["EMPTY", "ERROR"]:
            draw_text_in_bubble(draw, bubble['translated_text'], bubble, target_lang, debug=debug)
    
    # Save result
    img.save(output_path)
    print(f"\n✅ Saved translated comic to: {output_path}")
    
    return context_manager

def process_comic_page_with_languages(image_path, output_path, api_key=None, source_lang="English", target_lang="Russian", debug=False):
    """
    Main function to process a comic page with multi-language support
    Now uses multimodal context understanding
    """
    return process_comic_page_multimodal(
        image_path=image_path,
        output_path=output_path, 
        api_key=api_key,
        source_lang=source_lang,
        target_lang=target_lang,
        page_number=1,
        context_manager=None,
        debug=debug
    )

# Example usage
if __name__ == "__main__":
    import sys
    
    # Check for debug flag
    debug_mode = "--debug" in sys.argv
    if debug_mode:
        sys.argv.remove("--debug")
    
    if len(sys.argv) < 2:
        print("Usage: python translate_and_fill_bubbles_multilang.py <image_path> [output_path] [--debug]")
        print("       --debug    Show detailed analysis and translation information")
        sys.exit(1)
    
    image_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else "translated_" + os.path.basename(image_path)
    
    if debug_mode:
        print("🐛 Debug mode enabled - showing detailed analysis")
    
    process_comic_page_multimodal(image_path, output_path, debug=debug_mode) 
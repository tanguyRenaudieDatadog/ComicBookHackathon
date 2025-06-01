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

def load_speech_bubble_model(debug=False):
    """Load the finetuned YOLOv8 model for speech bubble detection"""
    try:
        model = YOLO('weights/ogkalu_model.pt')
        if debug:
            print("✅ Successfully loaded speech bubble detection model")
        return model
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        return None

def detect_speech_bubbles(model, image_path, conf_threshold=0.5, debug=False):
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
    
    if debug:
        print(f"🔍 Detected {len(bubble_data)} speech bubbles")
    else:
        print(f"🔍 Found {len(bubble_data)} speech bubbles")
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

def extract_text_from_bubble(client, bubble_image_path, bubble_info, debug=False):
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
        if debug:
            print(f"Error extracting text from bubble {bubble_info['bubble_id']}: {e}")
        if os.path.exists(bubble_image_path):
            os.remove(bubble_image_path)
        return "ERROR"

def translate_text(client, text, context_manager=None, bubble_id=None, source_lang="English", target_lang="Russian", debug=False):
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
        if debug:
            print(f"Error translating text: {e}")
        return text

def draw_text_in_bubble(draw, text, bubble_info, font_path=None, max_font_size=40, debug=False):
    """Draw text inside a bubble, automatically wrapping and sizing to fit"""
    x = bubble_info['x']
    y = bubble_info['y']
    width = bubble_info['width']
    height = bubble_info['height']
    
    # Start with a large font and decrease until text fits
    font_size = max_font_size
    
    # Try to use a font that supports Cyrillic
    cyrillic_fonts = [
        "/Library/Fonts/Arial Unicode.ttf",  # Has full Unicode support including Cyrillic
        "/System/Library/Fonts/Helvetica.ttc",
        "/System/Library/Fonts/HelveticaNeue.ttc", 
        "/System/Library/Fonts/ArialHB.ttc",
        "/System/Library/Fonts/Times.ttc",
        "/System/Library/Fonts/Supplemental/Arial Unicode.ttf"
    ]
    
    # Find first available Cyrillic font
    font_to_use = None
    for font_candidate in cyrillic_fonts:
        if os.path.exists(font_candidate):
            font_to_use = font_candidate
            if debug:
                print(f"Using font: {font_candidate}")
            break
    
    if not font_to_use and font_path and os.path.exists(font_path):
        font_to_use = font_path
    
    while font_size > 8:
        try:
            if font_to_use:
                font = ImageFont.truetype(font_to_use, font_size)
            else:
                # Fallback to default, but warn user
                if debug:
                    print("⚠️ Warning: No Cyrillic font found, text may not display correctly!")
                font = ImageFont.load_default()
        except Exception as e:
            if debug:
                print(f"Error loading font: {e}")
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

def process_comic_page(image_path, output_path, api_key=None, debug=False):
    """Main function to process a comic page with context-aware translation"""
    # Initialize Llama client
    client = LlamaAPIClient(
        api_key=api_key or os.environ.get("LLAMA_API_KEY")
    )
    
    # Initialize context manager
    context_manager = TranslationContext()
    
    # Load bubble detection model
    bubble_model = load_speech_bubble_model(debug)
    if not bubble_model:
        return
    
    # Detect bubbles
    print("📍 Detecting speech bubbles...")
    bubble_data = detect_speech_bubbles(bubble_model, image_path, conf_threshold=0.3, debug=debug)
    
    # Sort bubbles by position (top to bottom, left to right) for better context flow
    bubble_data.sort(key=lambda b: (b['y'], b['x']))
    
    # Extract text from each bubble
    print("📖 Extracting text from bubbles...")
    for bubble in bubble_data:
        # Crop bubble region
        bubble_image = crop_bubble_region(image_path, bubble)
        
        # Extract text
        bubble['original_text'] = extract_text_from_bubble(client, bubble_image, bubble, debug)
        if debug:
            print(f"Bubble {bubble['bubble_id']}: {bubble['original_text']}")
    
    # Translate texts with accumulating context
    print("🌐 Translating texts to Russian with context awareness...")
    if debug:
        print("Context will accumulate as translation progresses for better accuracy.\n")
    
    for i, bubble in enumerate(bubble_data):
        if bubble['original_text'] not in ["EMPTY", "ERROR"]:
            # Show context status
            if debug:
                context_size = len(context_manager.context_window)
                print(f"Translating bubble {bubble['bubble_id']} (with {context_size} previous bubbles as context)")
            
            # Translate with context
            bubble['translated_text'] = translate_text(
                client, 
                bubble['original_text'],
                context_manager=context_manager,
                bubble_id=bubble['bubble_id'],
                debug=debug
            )
            
            if debug:
                print(f"✓ {bubble['original_text']} → {bubble['translated_text']}\n")
        else:
            bubble['translated_text'] = bubble['original_text']
    
    # Generate and print summary
    summary = context_manager.generate_summary()
    if summary and debug:
        print("\n📊 Translation Context Summary:")
        print(summary)
    
    # Create image with white bubbles
    print("🎨 Creating output image...")
    img = Image.open(image_path).convert("RGBA")
    draw = ImageDraw.Draw(img)
    
    # First, draw white ellipses to cover original text
    for bubble in bubble_data:
        if bubble['original_text'] not in ["EMPTY", "ERROR"]:
            # Calculate ellipse parameters
            center_x = bubble['center_x']
            center_y = bubble['center_y']
            
            padding_factor = 0.98  # Match the latest update
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
            draw_text_in_bubble(draw, bubble['translated_text'], bubble, debug=debug)
    
    # Save result
    img.save(output_path)
    print(f"✅ Saved translated comic to: {output_path}")
    
    # Save translation data with context
    translation_data = {
        'bubbles': [
            {
                'id': b['bubble_id'],
                'position': {'x': b['x'], 'y': b['y'], 'width': b['width'], 'height': b['height']},
                'original': b['original_text'],
                'translated': b['translated_text']
            }
            for b in bubble_data
        ],
        'context': context_manager.get_full_context()
    }
    
    json_path = output_path.replace('.png', '_translations.json')
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(translation_data, f, ensure_ascii=False, indent=2)
    if debug:
        print(f"📝 Saved translation data to: {json_path}")
    
    # Save context separately for reuse
    context_path = output_path.replace('.png', '_context.json')
    context_manager.save_context(context_path)
    if debug:
        print(f"📚 Saved translation context to: {context_path}")

if __name__ == "__main__":
    import sys
    
    # Check for debug flag
    debug_mode = "--debug" in sys.argv
    if debug_mode:
        sys.argv.remove("--debug")
    
    # Process the comic page
    input_image = "image.png"
    output_image = "translated_comic_russian.png"
    
    # Load API key from .env file
    load_dotenv()
    api_key = os.getenv("api_key")  # Using 'api_key' as specified
    
    if not api_key:
        print("❌ Error: api_key not found in .env file")
    else:
        if debug_mode:
            print("🐛 Debug mode enabled")
        process_comic_page(input_image, output_image, api_key, debug=debug_mode) 
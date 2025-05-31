from ultralytics import YOLO
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import matplotlib.pyplot as plt

MODEL_PATH = 'weights/ogkalu_model.pt'

def load_speech_bubble_model():
    """
    Load the finetuned YOLOv8 model for speech bubble detection
    """
    try:
        # Load the finetuned model from Hugging Face
        model = YOLO(MODEL_PATH)
        print("✅ Successfully loaded kitsumed/yolov8m_seg-speech-bubble model")
        return model
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        print("Make sure you have ultralytics installed: pip install ultralytics")
        return None

def detect_speech_bubbles(model, image_path, conf_threshold=0.5):
    """
    Detect speech bubbles in an image using the loaded model
    
    Args:
        model: Loaded YOLO model
        image_path: Path to the image
        conf_threshold: Confidence threshold for detections
    
    Returns:
        results: YOLO detection results
        bubble_data: List of dictionaries with bubble information
    """
    # Run inference
    results = model(image_path, conf=conf_threshold)
    
    bubble_data = []
    
    # Process results
    for result in results:
        boxes = result.boxes
        if boxes is not None:
            for i, box in enumerate(boxes):
                # Get bounding box coordinates
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                confidence = box.conf[0].cpu().numpy()
                
                bubble_info = {
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
    return results, bubble_data

def visualize_detections(image_path, bubble_data, save_path=None):
    """
    Visualize the detected speech bubbles on the image
    """
    # Load image
    image = cv2.imread(image_path)
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    # Draw bounding boxes
    for i, bubble in enumerate(bubble_data):
        x, y, w, h = bubble['x'], bubble['y'], bubble['width'], bubble['height']
        confidence = bubble['confidence']
        
        # Draw rectangle
        cv2.rectangle(image_rgb, (x, y), (x + w, y + h), (255, 0, 0), 2)
        
        # Add confidence label
        label = f"Bubble {i+1}: {confidence:.2f}"
        cv2.putText(image_rgb, label, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)
    
    # Display
    plt.figure(figsize=(12, 8))
    plt.imshow(image_rgb)
    plt.axis('off')
    plt.title(f"Detected Speech Bubbles ({len(bubble_data)} found)")
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    
    plt.show()
    
    return image_rgb

def get_segmentation_masks(model, image_path, conf_threshold=0.5):
    """
    Get segmentation masks for speech bubbles (if the model supports segmentation)
    """
    results = model(image_path, conf=conf_threshold)
    
    masks_data = []
    
    for result in results:
        if hasattr(result, 'masks') and result.masks is not None:
            masks = result.masks.data.cpu().numpy()
            boxes = result.boxes
            
            for i, (mask, box) in enumerate(zip(masks, boxes)):
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                confidence = box.conf[0].cpu().numpy()
                
                mask_info = {
                    'mask': mask,
                    'bbox': {
                        'x': int(x1),
                        'y': int(y1),
                        'width': int(x2 - x1),
                        'height': int(y2 - y1)
                    },
                    'confidence': float(confidence)
                }
                masks_data.append(mask_info)
    
    return masks_data

def draw_white_ellipses_on_boxes(image_path, box_data, output_path=None, debug=True):
    """
    Draw white ellipses fitted to bounding boxes to cover text bubbles
    
    Args:
        image_path: Path to the original image
        box_data: List of dictionaries with box coordinates and dimensions
                 Can be from detect_speech_bubbles() or get_segmentation_masks()
        output_path: Path to save the modified image (optional)
        debug: Print debug information about image dimensions and scaling
    
    Returns:
        PIL Image object with white ellipses drawn
    """
    # Open the original image
    img = Image.open(image_path).convert("RGBA")
    original_width, original_height = img.size
    
    if debug:
        print(f"Original image dimensions: {original_width} x {original_height}")
        print(f"Aspect ratio: {original_width/original_height:.3f}")
    
    # Create a drawing context
    draw = ImageDraw.Draw(img)
    
    # Draw white ellipses for each text bubble box
    for i, box in enumerate(box_data):
        # Handle different data formats
        if 'bbox' in box:
            # Format from get_segmentation_masks()
            bbox = box['bbox']
            x = bbox['x']
            y = bbox['y']
            width = bbox['width']
            height = bbox['height']
            confidence = box.get('confidence', 1.0)
        else:
            # Format from detect_speech_bubbles()
            x = box['x']
            y = box['y']
            width = box['width']
            height = box['height']
            confidence = box.get('confidence', 1.0)
        
        if debug:
            print(f"\nBox {i+1}: x={x}, y={y}, w={width}, h={height}")
            print(f"  Box covers: ({x}, {y}) to ({x+width}, {y+height})")
            print(f"  Box aspect ratio: {width/height:.3f}")
            print(f"  Confidence: {confidence:.3f}")
        
        # Calculate ellipse parameters to fit the bounding box
        center_x = x + width / 2
        center_y = y + height / 2
        
        # Increase padding and adjust for potential compression
        padding_factor = 0.98  # Increased padding
        
        semi_major = (width / 2) * padding_factor
        semi_minor = (height / 2) * padding_factor
        
        # Calculate bounding box for the ellipse
        left = center_x - semi_major
        top = center_y - semi_minor
        right = center_x + semi_major
        bottom = center_y + semi_minor
        
        if debug:
            print(f"  Ellipse center: ({center_x:.1f}, {center_y:.1f})")
            print(f"  Ellipse semi-axes: {semi_major:.1f} x {semi_minor:.1f}")
            print(f"  Ellipse bounds: ({left:.1f}, {top:.1f}) to ({right:.1f}, {bottom:.1f})")
        
        # Draw white filled ellipse
        draw.ellipse([left, top, right, bottom], fill='white', outline='white')
        
        if debug:
            print(f"Drew ellipse for bubble {i+1} (confidence: {confidence:.3f})")
    
    # Save the image if output path is provided
    if output_path:
        img.save(output_path)
    
    return img

def add_translations_to_bubbles(image_path, translations, model, font_path="Death_Note.ttf", 
                               conf_threshold=0.3, font_size_base=16, output_path=None):
    """
    Add translations to detected speech bubbles on top of white ellipses
    
    Args:
        image_path: Path to the image
        translations: List of translation strings
        model: Loaded YOLO model for bubble detection
        font_path: Path to the font file
        conf_threshold: Confidence threshold for bubble detection
        font_size_base: Base font size (will be adjusted per bubble)
        output_path: Path to save the translated image
    
    Returns:
        PIL Image object with translations added on white ellipses
    """
    # Detect speech bubbles
    results, bubble_data = detect_speech_bubbles(model, image_path, conf_threshold)
    
    # Sort bubbles by position (top-left to bottom-right reading order)
    bubble_data_sorted = sorted(bubble_data, key=lambda b: (b['y'], b['x']))
    
    # First, draw white ellipses over the detected bubbles
    image_with_ellipses = draw_white_ellipses_on_boxes(
        image_path, bubble_data_sorted, debug=False
    )
    
    # Create a drawing context on the image with ellipses
    draw = ImageDraw.Draw(image_with_ellipses)
    
    print(f"🔍 Found {len(bubble_data_sorted)} bubbles, have {len(translations)} translations")
    
    # Apply translations to bubbles
    num_translations = min(len(bubble_data_sorted), len(translations))
    
    for i in range(num_translations):
        bubble = bubble_data_sorted[i]
        text = translations[i]
        
        # Calculate font size based on bubble size
        bubble_area = bubble['width'] * bubble['height']
        font_size = max(12, min(24, int(font_size_base * (bubble_area / 10000) ** 0.3)))
        
        try:
            font = ImageFont.truetype(font_path, font_size)
        except:
            # Fallback to default font if custom font not found
            font = ImageFont.load_default()
            print(f"⚠️  Could not load {font_path}, using default font")
        
        # Position text at the center of the bubble
        text_x = bubble['center_x'] - 50  # Offset to center text better
        text_y = bubble['center_y'] - 10
        
        # Ensure text stays within image bounds
        text_x = max(10, min(text_x, image_with_ellipses.width - 100))
        text_y = max(10, min(text_y, image_with_ellipses.height - 20))
        
        # Draw the translation on top of the white ellipse
        draw.text((text_x, text_y), text, fill="black", font=font)
        
        print(f"✅ Added translation {i+1}: '{text[:30]}...' at bubble center ({bubble['center_x']}, {bubble['center_y']})")
    
    # Save if output path provided
    if output_path:
        image_with_ellipses.save(output_path)
        print(f"💾 Saved translated image to: {output_path}")
    
    return image_with_ellipses

# Example usage function
def translate_manga_page(image_path, translations_italian, output_path="translated_manga.png"):
    """
    Complete pipeline to translate a manga page
    
    Args:
        image_path: Path to the manga image
        translations_italian: List of Italian translations
        output_path: Path to save the result
    """
    # Load the model
    model = load_speech_bubble_model()
    
    if model is None:
        print("❌ Could not load model")
        return None
    
    # Add translations to detected bubbles
    translated_image = add_translations_to_bubbles(
        image_path=image_path,
        translations=translations_italian,
        model=model,
        font_path="Death_Note.ttf",
        conf_threshold=0.3,
        output_path=output_path
    )
    
    # Display the result
    plt.figure(figsize=(12, 16))
    plt.imshow(translated_image)
    plt.axis('off')
    plt.title('Translated Manga Page')
    plt.tight_layout()
    plt.show()
    
    return translated_image

# Example usage
if __name__ == "__main__":
    # Italian translations
    translations_italian = [
        "Figlia, mostra il dovuto rispetto al Signore del Fuoco.",
        "Signore del Fuoco Azulon!",
        "Ursa, giusto? Alzati, lasciami darti un'occhiata.",
        "Magistrato Jinzuk, tua moglie ha cresciuto una figlia ancora più bella dei suoi fiori!",
        "Abbiamo avuto molte difficoltà a trovare i discendenti dell'Avatar Roku. Sembrava volersi nascondere da noi!",
        "Ma ora è chiaro che lo sforzo è stato utile. I saggi del fuoco mi dicono che l'unione della nipote dell'Avatar con mio figlio genererà una stirpe potente, che garantirà il dominio della mia famiglia per secoli dopo la mia morte.",
        "Ursa, permettimi di presentarti il principe del fuoco Ozai, il mio secondogenito.",
        "Ha una proposta per te."
    ]
    
    # Use the complete pipeline
    image_path = "image.png"
    translated_image = translate_manga_page(image_path, translations_italian) 
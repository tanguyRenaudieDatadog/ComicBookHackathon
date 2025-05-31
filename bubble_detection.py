from ultralytics import YOLO
import cv2
import numpy as np
from PIL import Image, ImageDraw
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
        padding_factor = 1.2  # Increased padding
        height_compensation = 1.3  # Extra compensation for vertical compression
        
        semi_major = (width / 2) * padding_factor
        semi_minor = (height / 2) * padding_factor * height_compensation
        
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


# Example usage
if __name__ == "__main__":
    # Load the model
    model = load_speech_bubble_model()
    
    if model is not None:
        # Test with your image
        image_path = "image.png"  # or "ComicBookHackathon/image.png"
        
        # Method 1: Using detect_speech_bubbles (bounding boxes only)
        print("=== Using detect_speech_bubbles ===")
        results, bubble_data = detect_speech_bubbles(model, image_path, conf_threshold=0.3)
        
        # Print detection results
        print("\n📊 Detection Results:")
        for i, bubble in enumerate(bubble_data):
            print(f"Bubble {i+1}: x={bubble['x']}, y={bubble['y']}, "
                  f"w={bubble['width']}, h={bubble['height']}, "
                  f"confidence={bubble['confidence']:.3f}")
        
        # Visualize results
        visualize_detections(image_path, bubble_data, save_path="detected_bubbles.png")
        
        # Draw ellipses using detection results
        img_with_ellipses = draw_white_ellipses_on_boxes(
            image_path, bubble_data, 
            output_path="image_with_ellipses_detection.png"
        )
        
        # Method 2: Using get_segmentation_masks (if available)
        print("\n=== Using get_segmentation_masks ===")
        try:
            masks_data = get_segmentation_masks(model, image_path, conf_threshold=0.3)
            if masks_data:
                print(f"🎭 Got {len(masks_data)} segmentation masks")
                
                # Draw ellipses using segmentation mask bboxes
                img_with_ellipses_seg = draw_white_ellipses_on_boxes(
                    image_path, masks_data,
                    output_path="image_with_ellipses_segmentation.png"
                )
                print("✅ Created ellipses from segmentation masks")
            else:
                print("ℹ️  No segmentation masks available (model might be detection-only)")
        except Exception as e:
            print(f"ℹ️  Segmentation not available: {e}") 
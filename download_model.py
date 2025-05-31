from huggingface_hub import hf_hub_download
import os
import shutil

# Download the model from Hugging Face
print("Downloading speech bubble detection model from Hugging Face...")
model_path = hf_hub_download(
    repo_id="ogkalu/comic-speech-bubble-detector-yolov8m",
    filename="comic-speech-bubble-detector.pt",  
    local_dir="weights",
    local_dir_use_symlinks=False
)
print(f"Model downloaded to: {model_path}")

# Rename to match what the script expects
if os.path.exists("weights/comic-speech-bubble-detector.pt"):
    shutil.move("weights/comic-speech-bubble-detector.pt", "weights/ogkalu_model.pt")
    print("Model renamed to: weights/ogkalu_model.pt") 
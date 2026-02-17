#!/bin/bash

echo "🚀 Starting Comic Translator Build Process..."

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Download the YOLOv8 model
echo "🤖 Downloading YOLOv8 model from Hugging Face..."
python download_model.py

# Build the frontend
echo "🎨 Building Next.js frontend..."
cd frontend
npm install
npm run build
cd ..

echo "✅ Build completed successfully!" 
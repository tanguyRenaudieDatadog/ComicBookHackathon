# ---- Stage 1: Build Next.js frontend ----
FROM node:20-slim AS frontend-builder

WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm ci
COPY frontend/ ./
RUN npm run build


# ---- Stage 2: Python runtime ----
FROM python:3.11-slim

# System dependencies:
#  - libgl1/libglib2.0: OpenCV headless still needs these at import time
#  - libgomp1: ultralytics / torch threading
#  - fonts-dejavu + fonts-noto-cjk: multi-language text rendering in bubbles
#  - git: huggingface_hub may invoke git to clone
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    libgomp1 \
    fonts-dejavu-core \
    fonts-noto-cjk \
    git \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install PyTorch CPU-only FIRST (avoids 2.5GB CUDA download from ultralytics)
RUN pip install --no-cache-dir torch torchvision --index-url https://download.pytorch.org/whl/cpu

# Install remaining Python deps (ultralytics will skip torch since it's already installed)
COPY requirements.txt constraints.txt ./
RUN pip install --no-cache-dir -c constraints.txt -r requirements.txt

# Copy application code
COPY app.py \
     translate_and_fill_bubbles_multilang.py \
     translate_pdf_comic.py \
     translation_context.py \
     manga_pdf_context.py \
     download_model.py \
     ./

# Copy Flask fallback templates/static
COPY templates/ templates/
COPY static/ static/

# Copy the built frontend from stage 1
COPY --from=frontend-builder /app/frontend/out/ frontend/out/

# Download YOLO model at build time (50 MB, cached in this layer)
RUN python download_model.py

# Create writable dirs for runtime uploads/outputs
RUN mkdir -p uploads outputs logs

# Force headless OpenCV — no display server on Railway
ENV QT_QPA_PLATFORM=offscreen \
    DISPLAY="" \
    OPENCV_OPENCL_RUNTIME="" \
    FLASK_ENV=production \
    PORT=8080

EXPOSE 8080

CMD ["gunicorn", "app:app", \
     "--bind", "0.0.0.0:8080", \
     "--workers", "2", \
     "--threads", "4", \
     "--timeout", "300", \
     "--max-requests", "100", \
     "--max-requests-jitter", "20"]

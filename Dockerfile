# ---- Stage 1: Build Next.js frontend ----
FROM node:20-slim AS frontend-builder

WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm ci
COPY frontend/ ./
RUN npm run build


# ---- Stage 2: Python runtime ----
FROM python:3.11-slim

# System dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    libgomp1 \
    fonts-dejavu-core \
    fonts-noto-cjk \
    git \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install all Python deps in one shot to avoid cache conflicts:
# 1) torch CPU-only first from PyTorch index
# 2) then ultralytics + everything else from PyPI
COPY requirements.txt constraints.txt ./
RUN pip install --no-cache-dir \
      --extra-index-url https://download.pytorch.org/whl/cpu \
      torch torchvision \
  && pip install --no-cache-dir -c constraints.txt -r requirements.txt \
  && python -c "from ultralytics import YOLO; print('ultralytics OK')"

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

CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:8080", "--workers", "2", "--threads", "4", "--timeout", "300", "--max-requests", "100", "--max-requests-jitter", "20"]

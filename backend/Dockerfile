FROM python:3.11-slim

WORKDIR /app

# Install system dependencies (ffmpeg for video stitching, fonts for Matplotlib and PIL rendering)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    fonts-dejavu \
    fonts-freefont-ttf \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install python packages
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy backend source code into /app/backend to preserve backend package namespace
COPY . /app/backend

# Set Python path so `backend.app...` and `app...` imports resolve correctly
ENV PYTHONPATH=/app:/app/backend
ENV PYTHONUNBUFFERED=1

# Expose FastAPI port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/api/v1/health || exit 1

# Launch FastAPI ASGI server
CMD ["python3", "-m", "uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]

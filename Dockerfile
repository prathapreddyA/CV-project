# Use Python 3.11.9 official image
FROM python:3.11.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Download the AI model file with verification
RUN echo "Downloading AI model file..." && \
    curl -L -o colorization_release_v2.caffemodel "https://www.dropbox.com/s/dx0qvhhp5hbcx7z/colorization_release_v2.caffemodel?dl=1" && \
    echo "Verifying model file..." && \
    ls -lh colorization_release_v2.caffemodel && \
    echo "✅ Model file downloaded successfully!"

# Copy the rest of the application
COPY . .

# Create necessary directories
RUN mkdir -p uploads outputs

# Expose port
EXPOSE 5000

# Set environment variables
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT:-5000}/health || exit 1

# Create start script
RUN echo '#!/bin/bash\necho "Starting server on port ${PORT:-5000}"\ngunicorn web_colorizer:app --bind 0.0.0.0:${PORT:-5000} --workers 2 --timeout 120' > start.sh && chmod +x start.sh

# Run the application
CMD ["./start.sh"]

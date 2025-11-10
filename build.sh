#!/bin/bash

# Build script for Render deployment
# Downloads the model file and installs dependencies

echo "🔧 Starting build process..."

# Install dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Download the AI model file
echo "📥 Downloading AI model file..."
curl -L -o colorization_release_v2.caffemodel "https://www.dropbox.com/s/dx0qvhhp5hbcx7z/colorization_release_v2.caffemodel?dl=1"

# Verify model file was downloaded
if [ -f "colorization_release_v2.caffemodel" ]; then
    echo "✅ Model file downloaded successfully"
    ls -lh colorization_release_v2.caffemodel
else
    echo "❌ Failed to download model file"
    exit 1
fi

echo "🎉 Build completed successfully!"

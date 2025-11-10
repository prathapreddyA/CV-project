#!/bin/bash
# Quick Start Script for Local Testing

echo "🎨 AI Image Colorizer - Local Test Server"
echo "=========================================="
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements_render.txt

# Check for model files
echo "🔍 Checking for model files..."
if [ ! -f "colorization_deploy_v2.prototxt" ]; then
    echo "❌ Missing: colorization_deploy_v2.prototxt"
    exit 1
fi

if [ ! -f "colorization_release_v2.caffemodel" ]; then
    echo "❌ Missing: colorization_release_v2.caffemodel"
    exit 1
fi

if [ ! -f "pts_in_hull.npy" ]; then
    echo "❌ Missing: pts_in_hull.npy"
    exit 1
fi

echo "✅ All model files found!"
echo ""

# Start server
echo "🚀 Starting web server..."
echo "📍 Server will be available at: http://localhost:5000"
echo "⏹️  Press Ctrl+C to stop"
echo ""

python web_colorizer.py

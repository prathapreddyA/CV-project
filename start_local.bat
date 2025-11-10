@echo off
REM Quick Start Script for Local Testing (Windows)

echo 🎨 AI Image Colorizer - Local Test Server
echo ==========================================
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo 📥 Installing dependencies...
pip install -r requirements_render.txt

REM Check for model files
echo 🔍 Checking for model files...
if not exist "colorization_deploy_v2.prototxt" (
    echo ❌ Missing: colorization_deploy_v2.prototxt
    exit /b 1
)

if not exist "colorization_release_v2.caffemodel" (
    echo ❌ Missing: colorization_release_v2.caffemodel
    exit /b 1
)

if not exist "pts_in_hull.npy" (
    echo ❌ Missing: pts_in_hull.npy
    exit /b 1
)

echo ✅ All model files found!
echo.

REM Start server
echo 🚀 Starting web server...
echo 📍 Server will be available at: http://localhost:5000
echo ⏹️  Press Ctrl+C to stop
echo.

python web_colorizer.py

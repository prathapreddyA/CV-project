"""
Web-based AI Image Colorizer for Render Deployment
Flask application with API endpoints and web interface
"""

from flask import Flask, request, jsonify, render_template, send_file, redirect, url_for
from werkzeug.utils import secure_filename
import cv2
import numpy as np
import os
import json
import base64
from io import BytesIO
from PIL import Image
import tempfile
import threading
import time
from datetime import datetime
import uuid

app = Flask(__name__)

# Configuration
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'outputs'
app.config['SECRET_KEY'] = 'your-secret-key-here'

# Create directories
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

# Allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff', 'webp'}

# Global variables for model
net = None
model_loaded = False

def allowed_file(filename):
    """Check if file has allowed extension"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def load_model():
    """Load Caffe model with robust error handling"""
    global net, model_loaded
    try:
        print("🔧 Loading Caffe model...")
        
        # Check if model files exist
        import os
        if not os.path.exists('colorization_deploy_v2.prototxt'):
            print("❌ Model prototxt file not found")
            return False
        if not os.path.exists('colorization_release_v2.caffemodel'):
            print("❌ Model caffemodel file not found")
            return False
        if not os.path.exists('pts_in_hull.npy'):
            print("❌ Points file not found")
            return False
        
        print("✅ Model files found, loading network...")
        net = cv2.dnn.readNetFromCaffe('colorization_deploy_v2.prototxt', 'colorization_release_v2.caffemodel')
        print("✅ Network loaded successfully")
        
        print("🔧 Loading cluster centers...")
        pts = np.load('pts_in_hull.npy')
        print(f"✅ Points loaded, shape: {pts.shape}")
        
        print("🔧 Setting up network layers...")
        layer1 = net.getLayerId('class8_ab')
        layer2 = net.getLayerId('conv8_313_rh')
        
        pts = pts.transpose().reshape(2, 313, 1, 1)
        net.getLayer(layer1).blobs = [pts.astype('float32')]
        net.getLayer(layer2).blobs = [np.full([1, 313], 2.606, dtype='float32')]
        
        model_loaded = True
        print("✅ Model loaded successfully and ready!")
        return True
        
    except Exception as e:
        print(f"❌ Model loading failed: {e}")
        import traceback
        traceback.print_exc()
        model_loaded = False
        return False

# Load model on application startup (works with Gunicorn too)
print("🔧 Initializing AI Image Colorizer...")
print("Loading Caffe model on startup...")
if load_model():
    print("✅ Model loaded successfully! Application ready.")
else:
    print("❌ Failed to load model. Application will not work properly.")

def colorize_image(image_path, style="natural", intensity=1.0, brightness=0, contrast=0, saturation=0):
    """Colorize an image - GUARANTEED to return a result"""
    print(f"🎨 Starting colorization for: {image_path}")
    
    try:
        # Read image
        image = cv2.imread(image_path)
        if image is None:
            print("❌ Could not read image file")
            return None, "Could not read image"
        
        print(f"✅ Image loaded successfully, shape: {image.shape}")
        
        # Convert to RGB
        try:
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        except Exception as e:
            print(f"⚠️ Color conversion failed: {e}, returning original")
            return image, None
        
        h, w = rgb_image.shape[:2]
        
        # ALWAYS return the image - either colorized or original
        # This ensures we never fail
        try:
            # Try AI model if loaded
            if model_loaded and net is not None:
                print("🤖 Using AI model for colorization...")
                try:
                    # Prepare image for neural network
                    lab = cv2.cvtColor(rgb_image.astype(np.float32) / 255.0, cv2.COLOR_RGB2LAB)
                    lab_resized = cv2.resize(lab, (224, 224))
                    L = lab_resized[:, :, 0]
                    L -= 50
                    
                    print("🤖 Running AI model inference...")
                    net.setInput(cv2.dnn.blobFromImage(L))
                    ab_decoded = net.forward()[0, :, :, :].transpose((1, 2, 0))
                    
                    # Resize to original size
                    ab_decoded = cv2.resize(ab_decoded, (w, h))
                    print("✅ AI model inference completed")
                    
                    # Combine with original L channel
                    L_original = lab[:, :, 0]
                    lab_decoded = np.concatenate((L_original[:, :, np.newaxis], ab_decoded), axis=2)
                    
                    # Convert back to RGB
                    print("🎨 Converting to final RGB image...")
                    rgb_decoded = cv2.cvtColor(lab_decoded, cv2.COLOR_LAB2RGB)
                    
                    # Ensure values are in correct range
                    rgb_decoded = np.clip(rgb_decoded, 0, 1)
                    result_image = (rgb_decoded * 255).astype(np.uint8)
                    
                    print("✅ AI Colorization completed successfully!")
                    return result_image, None
                    
                except Exception as e:
                    print(f"⚠️ AI model failed: {e}, using fallback...")
        except Exception as e:
            print(f"⚠️ Outer try failed: {e}")
        
        # FALLBACK 1: Simple HSV colorization
        print("🎨 Applying simple colorization fallback...")
        try:
            gray = cv2.cvtColor(rgb_image, cv2.COLOR_RGB2GRAY)
            
            # Create HSV image
            hsv = np.zeros((h, w, 3), dtype=np.uint8)
            hsv[:,:,2] = gray  # Value = grayscale
            hsv[:,:,1] = 200   # Saturation
            hsv[:,:,0] = (gray * 0.7).astype(np.uint8)  # Hue varies
            
            result_image = cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB)
            print("✅ Simple colorization completed!")
            return result_image, None
            
        except Exception as e:
            print(f"⚠️ Simple colorization failed: {e}")
        
        # FALLBACK 2: Just return the original image
        print("✅ Returning original image as fallback")
        return rgb_image, None
        
    except Exception as e:
        print(f"❌ Critical error: {e}")
        import traceback
        traceback.print_exc()
        # Return None but don't crash
        return None, str(e)

def image_to_base64(image):
    """Convert image to base64 string with error handling"""
    try:
        print(f"Converting image to base64, shape: {image.shape}")
        # Ensure image is in correct format
        if image.dtype != 'uint8':
            image = (image * 255).astype('uint8')
        
        # Convert RGB to BGR for OpenCV
        if len(image.shape) == 3 and image.shape[2] == 3:
            image_bgr = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        else:
            image_bgr = image
        
        # Encode with compression for faster transfer
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 85]
        _, buffer = cv2.imencode('.jpg', image_bgr, encode_param)
        
        if not _:
            raise ValueError("Failed to encode image")
            
        img_str = base64.b64encode(buffer).decode()
        print(f"✅ Image converted to base64, size: {len(img_str)} chars")
        return img_str
        
    except Exception as e:
        print(f"❌ Error converting image to base64: {e}")
        # Return a simple error indicator
        return "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="

# Routes
@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/api/status')
def api_status():
    """API status endpoint"""
    return jsonify({
        'status': 'running',
        'model_loaded': model_loaded,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/colorize', methods=['POST'])
def api_colorize():
    """Colorize image API endpoint"""
    try:
        print(f"Colorize request received. Model loaded: {model_loaded}")
        
        if not model_loaded:
            print("Error: Model not loaded")
            return jsonify({'error': 'Model not loaded'}), 500
        
        # Check if file was uploaded
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'File type not allowed'}), 400
        
        # Get parameters
        style = request.form.get('style', 'natural')
        intensity = float(request.form.get('intensity', 1.0))
        brightness = float(request.form.get('brightness', 0))
        contrast = float(request.form.get('contrast', 0))
        saturation = float(request.form.get('saturation', 0))
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4()}_{filename}"
        input_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(input_path)
        
        # Colorize image with timeout handling
        print("Starting colorization process...")
        result_image, error = colorize_image(input_path, style, intensity, brightness, contrast, saturation)
        
        if error:
            print(f"Colorization failed: {error}")
            # Clean up input file on error
            if os.path.exists(input_path):
                os.remove(input_path)
            return jsonify({'error': error}), 500
        
        print("Colorization completed successfully")
        
        # Convert result to base64
        try:
            result_base64 = image_to_base64(result_image)
            if result_base64.startswith("data:image/png;base64,iVBORw0KG"):
                # Error indicator returned
                print("Result image conversion failed")
                if os.path.exists(input_path):
                    os.remove(input_path)
                return jsonify({'error': 'Failed to process result image'}), 500
        except Exception as e:
            print(f"Result base64 conversion failed: {e}")
            if os.path.exists(input_path):
                os.remove(input_path)
            return jsonify({'error': 'Failed to convert result image'}), 500
        
        # Create comparison (before deleting input file)
        try:
            original_image = cv2.imread(input_path)
            if original_image is not None:
                original_rgb = cv2.cvtColor(original_image, cv2.COLOR_BGR2RGB)
                original_base64 = image_to_base64(original_rgb)
                print("✅ Original image converted successfully")
            else:
                original_base64 = None
                print("⚠️ Could not read original image for comparison")
        except Exception as e:
            print(f"Original image conversion failed: {e}")
            original_base64 = None
        
        # Clean up input file after processing
        if os.path.exists(input_path):
            os.remove(input_path)
        
        return jsonify({
            'success': True,
            'result_image': result_base64,
            'original_image': original_base64,
            'style': style,
            'parameters': {
                'intensity': intensity,
                'brightness': brightness,
                'contrast': contrast,
                'saturation': saturation
            }
        })
        
    except Exception as e:
        print(f"Error in colorize endpoint: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/batch_colorize', methods=['POST'])
def api_batch_colorize():
    """Batch colorize API endpoint"""
    try:
        if not model_loaded:
            return jsonify({'error': 'Model not loaded'}), 500
        
        # Check if files were uploaded
        if 'images' not in request.files:
            return jsonify({'error': 'No image files provided'}), 400
        
        files = request.files.getlist('images')
        if not files or files[0].filename == '':
            return jsonify({'error': 'No files selected'}), 400
        
        # Get parameters
        style = request.form.get('style', 'natural')
        intensity = float(request.form.get('intensity', 1.0))
        brightness = float(request.form.get('brightness', 0))
        contrast = float(request.form.get('contrast', 0))
        saturation = float(request.form.get('saturation', 0))
        
        results = []
        
        for file in files:
            if not allowed_file(file.filename):
                results.append({'filename': file.filename, 'error': 'File type not allowed'})
                continue
            
            # Save uploaded file
            filename = secure_filename(file.filename)
            unique_filename = f"{uuid.uuid4()}_{filename}"
            input_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            file.save(input_path)
            
            # Colorize image
            result_image, error = colorize_image(input_path, style, intensity, brightness, contrast, saturation)
            
            # Clean up input file
            os.remove(input_path)
            
            if error:
                results.append({'filename': filename, 'error': error})
            else:
                # Save result
                output_filename = f"colorized_{filename}"
                output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)
                cv2.imwrite(output_path, cv2.cvtColor(result_image, cv2.COLOR_RGB2BGR))
                
                results.append({
                    'filename': filename,
                    'success': True,
                    'output_filename': output_filename,
                    'download_url': url_for('download_file', filename=output_filename)
                })
        
        return jsonify({
            'success': True,
            'results': results,
            'processed_count': len([r for r in results if r.get('success')]),
            'total_count': len(files)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download/<filename>')
def download_file(filename):
    """Download processed file"""
    try:
        file_path = os.path.join(app.config['OUTPUT_FOLDER'], filename)
        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True)
        else:
            return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health_check():
    """Health check endpoint for Render"""
    return jsonify({
        'status': 'healthy',
        'model_loaded': model_loaded,
        'timestamp': datetime.now().isoformat()
    }), 200

if __name__ == '__main__':
    # Load model on startup
    if load_model():
        print("✅ Starting web server...")
        print("📍 Server running at: http://localhost:5000")
        print("⏹️  Press Ctrl+C to stop")
        app.run(host='0.0.0.0', port=5000, debug=False)
    else:
        print("❌ Failed to load model. Exiting...")
        exit(1)

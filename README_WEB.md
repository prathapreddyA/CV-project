# 🎨 AI Image Colorizer - Web Application

## Professional AI-Powered Image Colorization Service

Transform black and white images into vibrant, colorful masterpieces using state-of-the-art deep learning technology.

---

## ✨ Features

### 🎨 **Colorization Styles**
- **Natural**: Realistic, true-to-life colors
- **Vibrant**: Enhanced saturation for bold colors
- **Vintage**: Classic sepia and retro tones
- **Artistic**: Creative color interpretations
- **Dramatic**: High contrast with intense colors
- **Cinematic**: Film-like color grading

### ⚙️ **Advanced Controls**
- Brightness adjustment (-100 to +100)
- Contrast enhancement (-100 to +100)
- Saturation control (-100 to +100)
- Style intensity (0.1 to 2.0)
- One-click presets (Auto, Vintage, Cinematic)

### 🖼️ **Image Processing**
- Support for multiple formats (JPG, PNG, BMP, TIFF, WebP)
- Maximum file size: 16MB
- High-quality output
- Before/After comparison view
- Instant preview

### 🌐 **Web Interface**
- Professional dark theme design
- Responsive layout
- Real-time progress tracking
- Drag & drop upload
- One-click download

### 🔌 **API Endpoints**
- RESTful API for integration
- Single image processing
- Batch processing support
- JSON responses with base64 images
- Health monitoring

---

## 🚀 Quick Start

### **Local Development:**

#### Windows:
```bash
start_local.bat
```

#### Linux/Mac:
```bash
chmod +x start_local.sh
./start_local.sh
```

Then open your browser to: `http://localhost:5000`

### **Manual Start:**

```bash
# Install dependencies
pip install -r requirements_render.txt

# Run the application
python web_colorizer.py
```

---

## 📦 Deployment

### **Deploy to Render:**

1. **Push to GitHub:**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git push origin main
   ```

2. **Create Web Service on Render:**
   - Go to https://render.com
   - Click "New +" → "Web Service"
   - Connect your repository
   - Configure:
     - Build Command: `pip install -r requirements_render.txt`
     - Start Command: `gunicorn web_colorizer:app --bind 0.0.0.0:$PORT`

3. **Set Environment Variables:**
   ```
   FLASK_ENV=production
   SECRET_KEY=your-secret-key
   ```

4. **Deploy!**

See [RENDER_DEPLOYMENT_GUIDE.md](RENDER_DEPLOYMENT_GUIDE.md) for detailed instructions.

---

## 🔧 API Documentation

### **Status Check**
```http
GET /api/status
```

**Response:**
```json
{
  "status": "running",
  "model_loaded": true,
  "timestamp": "2024-11-10T10:25:00"
}
```

### **Colorize Image**
```http
POST /api/colorize
Content-Type: multipart/form-data
```

**Parameters:**
- `image` (file): Image file to colorize
- `style` (string): Colorization style (default: "natural")
- `intensity` (float): Style intensity (default: 1.0)
- `brightness` (int): Brightness adjustment (default: 0)
- `contrast` (int): Contrast adjustment (default: 0)
- `saturation` (int): Saturation adjustment (default: 0)

**Response:**
```json
{
  "success": true,
  "result_image": "base64_encoded_image",
  "original_image": "base64_encoded_image",
  "style": "vibrant",
  "parameters": {
    "intensity": 1.2,
    "brightness": 10,
    "contrast": 15,
    "saturation": 20
  }
}
```

### **Batch Colorize**
```http
POST /api/batch_colorize
Content-Type: multipart/form-data
```

**Parameters:**
- `images` (files): Multiple image files
- Same parameters as single colorize

**Response:**
```json
{
  "success": true,
  "results": [
    {
      "filename": "image1.jpg",
      "success": true,
      "output_filename": "colorized_image1.jpg",
      "download_url": "/download/colorized_image1.jpg"
    }
  ],
  "processed_count": 5,
  "total_count": 5
}
```

### **Health Check**
```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "model_loaded": true,
  "timestamp": "2024-11-10T10:25:00"
}
```

---

## 📊 Example Usage

### **Python:**

```python
import requests

# Colorize an image
url = "http://localhost:5000/api/colorize"
files = {'image': open('photo.jpg', 'rb')}
data = {
    'style': 'vibrant',
    'intensity': 1.2,
    'brightness': 10,
    'contrast': 15,
    'saturation': 20
}

response = requests.post(url, files=files, data=data)
result = response.json()

if result['success']:
    import base64
    from PIL import Image
    from io import BytesIO
    
    # Decode and save
    img_data = base64.b64decode(result['result_image'])
    img = Image.open(BytesIO(img_data))
    img.save('colorized.jpg')
```

### **cURL:**

```bash
curl -X POST http://localhost:5000/api/colorize \
  -F "image=@photo.jpg" \
  -F "style=vibrant" \
  -F "intensity=1.2" \
  -F "brightness=10" \
  -F "contrast=15" \
  -F "saturation=20"
```

### **JavaScript:**

```javascript
const formData = new FormData();
formData.append('image', fileInput.files[0]);
formData.append('style', 'vibrant');
formData.append('intensity', '1.2');

fetch('http://localhost:5000/api/colorize', {
    method: 'POST',
    body: formData
})
.then(response => response.json())
.then(data => {
    if (data.success) {
        const img = document.createElement('img');
        img.src = 'data:image/jpeg;base64,' + data.result_image;
        document.body.appendChild(img);
    }
});
```

---

## 🛠️ Technology Stack

- **Backend**: Flask (Python web framework)
- **AI Model**: Caffe deep learning framework
- **Image Processing**: OpenCV, NumPy, Pillow
- **Web Server**: Gunicorn
- **Frontend**: HTML5, CSS3, JavaScript
- **Deployment**: Render (cloud platform)

---

## 📁 Project Structure

```
ai-image-colorizer/
├── web_colorizer.py              # Flask application
├── templates/
│   └── index.html                # Web interface
├── uploads/                      # Temporary uploads
├── outputs/                      # Processed images
├── requirements_render.txt       # Dependencies
├── Procfile                      # Process configuration
├── runtime.txt                   # Python version
├── render.yaml                   # Render config
├── .gitignore                    # Git ignore rules
├── start_local.bat               # Windows start script
├── start_local.sh                # Linux/Mac start script
├── RENDER_DEPLOYMENT_GUIDE.md    # Deployment guide
├── README_WEB.md                 # This file
└── Model files:
    ├── colorization_deploy_v2.prototxt
    ├── colorization_release_v2.caffemodel
    └── pts_in_hull.npy
```

---

## ⚙️ Configuration

### **Environment Variables:**

Create a `.env` file (or set in Render dashboard):

```env
FLASK_ENV=production
FLASK_DEBUG=0
MAX_CONTENT_LENGTH=16777216
SECRET_KEY=your-secret-key-here
```

### **Application Settings:**

Edit `web_colorizer.py`:

```python
# Maximum file size (16MB)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# Allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff', 'webp'}
```

---

## 🔒 Security

- File type validation
- File size limits
- Secure filename handling
- HTTPS on Render (automatic)
- Environment variable protection
- Input sanitization

---

## 📈 Performance

### **Optimization Tips:**

1. **Image Size**: Resize large images before processing
2. **Workers**: Adjust Gunicorn workers based on RAM
3. **Timeout**: Increase for large images
4. **Caching**: Implement Redis for repeated requests
5. **CDN**: Use for static assets

### **Benchmarks:**

- Small images (< 1MB): ~2-3 seconds
- Medium images (1-5MB): ~5-8 seconds
- Large images (5-16MB): ~10-15 seconds

---

## 🐛 Troubleshooting

### **Model not loading:**
- Ensure all 3 model files are present
- Check file permissions
- Verify file paths

### **Out of memory:**
- Reduce image size
- Decrease Gunicorn workers
- Upgrade to larger instance

### **Slow processing:**
- Check server resources
- Optimize image size
- Use faster instance type

### **API errors:**
- Check request format
- Verify file types
- Review error logs

---

## 📝 License

This project uses the Caffe colorization model. Please refer to the original model's license for usage terms.

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

## 📧 Support

For issues and questions:
- Open an issue on GitHub
- Check the deployment guide
- Review API documentation

---

## 🎉 Credits

- **Colorization Model**: Based on research by Zhang et al.
- **Framework**: Flask, OpenCV, Caffe
- **Deployment**: Render cloud platform

---

## 🚀 **Ready to Deploy!**

Your AI Image Colorizer web application is ready for deployment to Render. Follow the deployment guide and start transforming images online!

**Live Demo**: Deploy to see it in action at `https://your-app.onrender.com`

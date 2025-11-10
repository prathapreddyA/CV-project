# 🎨 AI Image Colorizer

**Professional AI-Powered Image Colorization** - Transform black and white images into vibrant, colorful masterpieces using deep learning.

**Author**: prathapreddyA

---

## 📥 **Important: Download Model File First**

The AI model file (`colorization_release_v2.caffemodel` - 123 MB) is too large for GitHub.

### **Download the Model:**

**Option 1: Direct Download**
```
https://www.dropbox.com/s/dx0qvhhp5hbcx7z/colorization_release_v2.caffemodel
```

**Option 2: Original Source**
```
https://github.com/richzhang/colorization/blob/caffe/colorization/models/colorization_release_v2.caffemodel
```

**Place the downloaded file in the project root directory.**

---

## 🚀 Quick Start

### **Option 1: Web Application (Recommended for Deployment)**

#### Local Testing:
```bash
# Windows
start_local.bat

# Linux/Mac
chmod +x start_local.sh
./start_local.sh
```

Then open: `http://localhost:5000`

#### Deploy to Render:
See [RENDER_DEPLOYMENT_GUIDE.md](RENDER_DEPLOYMENT_GUIDE.md) for complete instructions.

### **Option 2: Desktop Application**

#### Professional Version (Advanced Features):
```bash
python professional_colorizer.py
```
Features: Comparison tools, analytics, real-time enhancements, 6 styles

#### Simple Version (Basic):
```bash
python fixed_colorizer.py
```
Features: Basic colorization, batch processing

---

## 📦 What's Included

### **🌐 Web Application**
- Modern web interface with dark theme
- RESTful API for integration
- 6 colorization styles
- Real-time enhancements
- Before/After comparison
- Batch processing support

### **🖥️ Desktop Applications**
- **Professional**: Advanced GUI with comparison tools and analytics
- **Fixed**: Simple, reliable GUI for basic use

### **🤖 AI Model**
- Pre-trained Caffe deep learning model
- High-quality colorization
- Multiple style support

---

## ✨ Features

### **Colorization Styles:**
- 🎨 **Natural** - Realistic, true-to-life colors
- 💥 **Vibrant** - Enhanced saturation for bold colors
- 📼 **Vintage** - Classic sepia and retro tones
- 🎭 **Artistic** - Creative color interpretations
- ⚡ **Dramatic** - High contrast with intense colors
- 🎬 **Cinematic** - Film-like color grading

### **Enhancement Controls:**
- ☀️ Brightness adjustment
- 🔲 Contrast enhancement
- 🌈 Saturation control
- 🎚️ Style intensity
- ✨ One-click presets

### **Processing:**
- 📸 Single image colorization
- 📋 Batch processing
- 🔀 Before/After comparison
- 📊 Analytics and histograms
- 💾 Multiple export formats

---

## 📁 Project Structure

```
ai-image-colorizer/
├── 🌐 Web Application
│   ├── web_colorizer.py          # Flask web app
│   └── templates/
│       └── index.html            # Web interface
│
├── 🖥️ Desktop Applications
│   ├── professional_colorizer.py # Advanced GUI
│   └── fixed_colorizer.py        # Simple GUI
│
├── 🤖 AI Model Files
│   ├── colorization_deploy_v2.prototxt
│   ├── colorization_release_v2.caffemodel
│   └── pts_in_hull.npy
│
├── 🚀 Deployment Configuration
│   ├── requirements_render.txt   # Python dependencies
│   ├── Procfile                  # Process config
│   ├── runtime.txt               # Python version
│   ├── render.yaml               # Render config
│   └── .env.example              # Environment variables
│
├── 📚 Documentation
│   ├── README.md                 # This file
│   ├── README_WEB.md             # Web app docs
│   ├── RENDER_DEPLOYMENT_GUIDE.md
│   └── DEPLOYMENT_COMPLETE.md
│
├── 🧪 Testing Scripts
│   ├── start_local.bat           # Windows
│   └── start_local.sh            # Linux/Mac
│
└── 📁 Directories
    ├── Gray Image/               # Sample images
    ├── uploads/                  # Web app uploads
    └── outputs/                  # Web app outputs
```

---

## 🛠️ Technology Stack

- **Backend**: Flask (Python web framework)
- **AI Model**: Caffe deep learning framework
- **Image Processing**: OpenCV, NumPy, Pillow
- **Desktop GUI**: CustomTkinter
- **Web Server**: Gunicorn
- **Deployment**: Render cloud platform

---

## 📊 Supported Formats

**Input/Output:**
- JPEG (.jpg, .jpeg)
- PNG (.png)
- BMP (.bmp)
- TIFF (.tiff)
- WebP (.webp)
- GIF (.gif)

**Maximum File Size:** 16MB (configurable)

---

## 🌐 API Documentation

### **Endpoints:**

#### Status Check
```http
GET /api/status
```

#### Colorize Image
```http
POST /api/colorize
Content-Type: multipart/form-data

Parameters:
- image (file): Image to colorize
- style (string): Colorization style
- intensity (float): Style intensity
- brightness (int): Brightness adjustment
- contrast (int): Contrast adjustment
- saturation (int): Saturation adjustment
```

#### Health Check
```http
GET /health
```

See [README_WEB.md](README_WEB.md) for complete API documentation.

---

## 🚀 Deployment

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
   - Use automatic configuration (render.yaml)

3. **Your app will be live at:**
   ```
   https://your-app-name.onrender.com
   ```

**Detailed Guide:** See [RENDER_DEPLOYMENT_GUIDE.md](RENDER_DEPLOYMENT_GUIDE.md)

---

## 💻 Local Development

### **Requirements:**
- Python 3.11+
- pip (Python package manager)

### **Installation:**

```bash
# Install dependencies
pip install -r requirements_render.txt

# Run web app
python web_colorizer.py

# Or run desktop app
python professional_colorizer.py
```

---

## 🎯 Usage Examples

### **Web Interface:**
1. Open http://localhost:5000
2. Upload an image
3. Select style and adjust settings
4. Click "Colorize Image"
5. Download result

### **Desktop Application:**
1. Run the application
2. Click "Load Image"
3. Choose colorization style
4. Adjust enhancements
5. Click "Colorize"
6. View comparison and save

### **API (Python):**
```python
import requests

url = "http://localhost:5000/api/colorize"
files = {'image': open('photo.jpg', 'rb')}
data = {'style': 'vibrant', 'intensity': 1.2}

response = requests.post(url, files=files, data=data)
result = response.json()
```

---

## 📈 Performance

- **Small images** (< 1MB): ~2-3 seconds
- **Medium images** (1-5MB): ~5-8 seconds
- **Large images** (5-16MB): ~10-15 seconds

*Processing time depends on image size and server resources*

---

## 🔒 Security

- File type validation
- File size limits
- Secure filename handling
- HTTPS on Render (automatic)
- Environment variable protection

---

## 📝 License

This project uses the Caffe colorization model. Please refer to the original model's license for usage terms.

---

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Report bugs
- Suggest features
- Submit pull requests

---

## 📧 Support

- **Documentation**: Check the docs folder
- **Issues**: Open an issue on GitHub
- **Deployment**: See RENDER_DEPLOYMENT_GUIDE.md

---

## 🎉 Credits

- **Colorization Model**: Based on research by Zhang et al.
- **Frameworks**: Flask, OpenCV, Caffe, CustomTkinter
- **Deployment**: Render cloud platform

---

## 🚀 Get Started Now!

1. **Test Locally**: `start_local.bat` or `start_local.sh`
2. **Deploy Online**: Follow [RENDER_DEPLOYMENT_GUIDE.md](RENDER_DEPLOYMENT_GUIDE.md)
3. **Use Desktop App**: `python professional_colorizer.py`

**Transform your black and white images into vibrant colors with AI!** 🎨✨

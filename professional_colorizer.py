"""
Professional AI Colorizer with Comparison Features - Compatible Version
Works with current CustomTkinter installation
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import customtkinter as ctk
from PIL import Image, ImageTk, ImageEnhance
import cv2
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import os
import threading
from pathlib import Path
from datetime import datetime

# Configure matplotlib for dark theme
plt.style.use('dark_background')

# Set appearance mode
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class ProfessionalColorizerApp:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("🎨 AI Image Colorizer - Professional with Comparison")
        self.root.geometry("1500x900")
        
        # Initialize variables
        self.original_image = None
        self.processed_image = None
        self.current_file = None
        self.processing = False
        
        # Enhancement variables
        self.brightness_var = tk.DoubleVar(value=0)
        self.contrast_var = tk.DoubleVar(value=0)
        self.saturation_var = tk.DoubleVar(value=0)
        self.warmth_var = tk.DoubleVar(value=0)
        self.sharpness_var = tk.DoubleVar(value=0)
        
        # Style variables
        self.style_var = tk.StringVar(value="Natural")
        self.intensity_var = tk.DoubleVar(value=1.0)
        
        # History
        self.processing_history = []
        
        # Load Caffe model
        self.load_model()
        
        # Create GUI
        self.create_widgets()
        
    def load_model(self):
        """Load Caffe model"""
        try:
            print("Loading Caffe model...")
            self.net = cv2.dnn.readNetFromCaffe('colorization_deploy_v2.prototxt', 'colorization_release_v2.caffemodel')
            pts = np.load('pts_in_hull.npy')
            
            layer1 = self.net.getLayerId('class8_ab')
            layer2 = self.net.getLayerId('conv8_313_rh')
            
            pts = pts.transpose().reshape(2, 313, 1, 1)
            self.net.getLayer(layer1).blobs = [pts.astype('float32')]
            self.net.getLayer(layer2).blobs = [np.full([1, 313], 2.606, dtype='float32')]
            
            print("✅ Model loaded successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load model: {e}")
            print(f"Model loading error: {e}")
    
    def create_widgets(self):
        """Create professional GUI widgets"""
        # Main container
        main_container = ctk.CTkFrame(self.root)
        main_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Title bar
        title_frame = ctk.CTkFrame(main_container, height=60)
        title_frame.pack(fill="x", padx=5, pady=5)
        title_frame.pack_propagate(False)
        
        title_label = ctk.CTkLabel(title_frame, text="🎨 AI Image Colorizer - Professional with Comparison", 
                                   font=ctk.CTkFont(size=20, weight="bold"))
        title_label.pack(pady=15)
        
        # Status bar
        self.status_label = ctk.CTkLabel(title_frame, text="🟢 Ready", 
                                        font=ctk.CTkFont(size=12))
        self.status_label.pack(side="right", padx=20)
        
        # Create main frame with manual layout (instead of PanedWindow)
        self.main_frame = ctk.CTkFrame(main_container)
        self.main_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Left panel for controls (fixed width)
        self.left_panel = ctk.CTkFrame(self.main_frame, width=400)
        self.left_panel.pack(side="left", fill="y", padx=(0, 5))
        self.left_panel.pack_propagate(False)
        
        # Right panel for images (expanding)
        self.right_panel = ctk.CTkFrame(self.main_frame)
        self.right_panel.pack(side="right", fill="both", expand=True, padx=(5, 0))
        
        # Create control panels
        self.create_control_panels()
        
        # Create image display area
        self.create_image_area()
        
        # Bottom progress bar
        progress_frame = ctk.CTkFrame(main_container, height=50)
        progress_frame.pack(fill="x", padx=5, pady=5)
        progress_frame.pack_propagate(False)
        
        self.progress_bar = ctk.CTkProgressBar(progress_frame)
        self.progress_bar.pack(fill="x", padx=10, pady=10)
        self.progress_bar.set(0)
    
    def create_control_panels(self):
        """Create advanced control panels"""
        # Create scrollable frame
        scrollable = ctk.CTkScrollableFrame(self.left_panel, height=750)
        scrollable.pack(fill="both", expand=True, padx=10, pady=10)
        
        # File Operations Panel
        self.create_file_panel(scrollable)
        
        # Enhancement Controls Panel
        self.create_enhancement_panel(scrollable)
        
        # Style Selection Panel
        self.create_style_panel(scrollable)
        
        # Processing Panel
        self.create_processing_panel(scrollable)
        
        # Export Panel
        self.create_export_panel(scrollable)
        
        # History Panel
        self.create_history_panel(scrollable)
    
    def create_file_panel(self, parent):
        """Create file operations panel"""
        panel = ctk.CTkFrame(parent)
        panel.pack(fill="x", pady=10)
        
        ctk.CTkLabel(panel, text="📁 File Operations", 
                    font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)
        
        # Button grid
        button_frame = ctk.CTkFrame(panel)
        button_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkButton(button_frame, text="📂 Load Image", 
                     command=self.load_image, height=40).pack(fill="x", pady=3)
        ctk.CTkButton(button_frame, text="📋 Batch Process", 
                     command=self.batch_process, height=40).pack(fill="x", pady=3)
        ctk.CTkButton(button_frame, text="📸 Webcam Capture", 
                     command=self.capture_webcam, height=40).pack(fill="x", pady=3)
        ctk.CTkButton(button_frame, text="🔄 Reset All", 
                     command=self.reset_all, height=40).pack(fill="x", pady=3)
    
    def create_enhancement_panel(self, parent):
        """Create enhancement controls panel"""
        panel = ctk.CTkFrame(parent)
        panel.pack(fill="x", pady=10)
        
        ctk.CTkLabel(panel, text="⚙️ Enhancement Controls", 
                    font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)
        
        # Enhancement sliders
        controls = [
            ("☀️ Brightness", self.brightness_var, -100, 100),
            ("🔲 Contrast", self.contrast_var, -100, 100),
            ("🌈 Saturation", self.saturation_var, -100, 100),
            ("🌡️ Warmth", self.warmth_var, -50, 50),
            ("🔍 Sharpness", self.sharpness_var, -100, 100)
        ]
        
        for label_text, variable, min_val, max_val in controls:
            frame = ctk.CTkFrame(panel)
            frame.pack(fill="x", padx=10, pady=5)
            
            ctk.CTkLabel(frame, text=label_text, width=100).pack(side="left", padx=5)
            
            slider = ctk.CTkSlider(frame, from_=min_val, to=max_val, 
                                  variable=variable, width=200)
            slider.pack(side="left", padx=5)
            
            value_label = ctk.CTkLabel(frame, text="0", width=40)
            value_label.pack(side="left", padx=5)
            
            # Update label when slider changes
            def update_label(val, lbl=value_label, var=variable):
                lbl.configure(text=f"{var.get():.0f}")
                if self.processed_image is not None:
                    self.apply_real_time_enhancements()
            
            slider.configure(command=update_label)
        
        # Preset buttons
        preset_frame = ctk.CTkFrame(panel)
        preset_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkButton(preset_frame, text="✨ Auto Enhance", 
                     command=self.auto_enhance, width=120).pack(side="left", padx=5)
        ctk.CTkButton(preset_frame, text="🎭 Vintage", 
                     command=self.vintage_preset, width=120).pack(side="left", padx=5)
        ctk.CTkButton(preset_frame, text="🎬 Cinematic", 
                     command=self.cinematic_preset, width=120).pack(side="left", padx=5)
    
    def create_style_panel(self, parent):
        """Create style selection panel"""
        panel = ctk.CTkFrame(parent)
        panel.pack(fill="x", pady=10)
        
        ctk.CTkLabel(panel, text="🎨 Colorization Style", 
                    font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)
        
        # Style dropdown
        style_frame = ctk.CTkFrame(panel)
        style_frame.pack(fill="x", padx=10, pady=5)
        
        styles = ["Natural", "Vibrant", "Vintage", "Artistic", "Dramatic", "Cinematic"]
        self.style_combo = ctk.CTkComboBox(style_frame, variable=self.style_var, 
                                          values=styles, width=200)
        self.style_combo.pack(side="left", padx=5)
        
        # Intensity slider
        ctk.CTkLabel(style_frame, text="Intensity:", width=70).pack(side="left", padx=5)
        intensity_slider = ctk.CTkSlider(style_frame, from_=0.1, to=2.0, 
                                       variable=self.intensity_var, width=150)
        intensity_slider.pack(side="left", padx=5)
        
        self.intensity_label = ctk.CTkLabel(style_frame, text="1.0", width=40)
        self.intensity_label.pack(side="left", padx=5)
        
        def update_intensity(val):
            self.intensity_label.configure(text=f"{self.intensity_var.get():.1f}")
            if self.processed_image is not None:
                self.apply_real_time_enhancements()
        
        intensity_slider.configure(command=update_intensity)
    
    def create_processing_panel(self, parent):
        """Create processing panel"""
        panel = ctk.CTkFrame(parent)
        panel.pack(fill="x", pady=10)
        
        ctk.CTkLabel(panel, text="🚀 Processing", 
                    font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)
        
        self.process_button = ctk.CTkButton(panel, text="🎨 Colorize Image", 
                                           command=self.colorize_image,
                                           height=50, fg_color="green",
                                           hover_color="darkgreen",
                                           font=ctk.CTkFont(size=16, weight="bold"))
        self.process_button.pack(fill="x", padx=10, pady=5)
        
        # Comparison buttons
        comp_frame = ctk.CTkFrame(panel)
        comp_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkButton(comp_frame, text="🔀 Split View", 
                     command=self.show_split_view, width=140).pack(side="left", padx=5)
        ctk.CTkButton(comp_frame, text="📊 Analytics", 
                     command=self.show_analytics, width=140).pack(side="left", padx=5)
        ctk.CTkButton(comp_frame, text="🔄 Difference", 
                     command=self.show_difference, width=140).pack(side="left", padx=5)
    
    def create_export_panel(self, parent):
        """Create export panel"""
        panel = ctk.CTkFrame(parent)
        panel.pack(fill="x", pady=10)
        
        ctk.CTkLabel(panel, text="💾 Export Options", 
                    font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)
        
        # Format selection
        format_frame = ctk.CTkFrame(panel)
        format_frame.pack(fill="x", padx=10, pady=5)
        
        self.format_var = tk.StringVar(value="JPEG")
        formats = ["JPEG", "PNG", "TIFF", "WebP"]
        self.format_combo = ctk.CTkComboBox(format_frame, variable=self.format_var, 
                                           values=formats, width=150)
        self.format_combo.pack(side="left", padx=5)
        
        # Quality slider
        self.quality_var = tk.IntVar(value=95)
        ctk.CTkLabel(format_frame, text="Quality:", width=60).pack(side="left", padx=5)
        quality_slider = ctk.CTkSlider(format_frame, from_=10, to=100, 
                                      variable=self.quality_var, width=120)
        quality_slider.pack(side="left", padx=5)
        
        self.quality_label = ctk.CTkLabel(format_frame, text="95", width=30)
        self.quality_label.pack(side="left", padx=5)
        
        def update_quality(val):
            self.quality_label.configure(text=f"{self.quality_var.get()}")
        
        quality_slider.configure(command=update_quality)
        
        # Export buttons
        export_frame = ctk.CTkFrame(panel)
        export_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkButton(export_frame, text="💾 Save Image", 
                     command=self.save_image, height=40).pack(fill="x", pady=3)
        ctk.CTkButton(export_frame, text="📋 Export Comparison", 
                     command=self.export_comparison, height=40).pack(fill="x", pady=3)
    
    def create_history_panel(self, parent):
        """Create history panel"""
        panel = ctk.CTkFrame(parent)
        panel.pack(fill="x", pady=10)
        
        ctk.CTkLabel(panel, text="📜 Processing History", 
                    font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)
        
        # History listbox
        history_frame = ctk.CTkFrame(panel)
        history_frame.pack(fill="x", padx=10, pady=5)
        
        self.history_listbox = tk.Listbox(history_frame, height=4, 
                                         bg="gray20", fg="white", 
                                         selectbackground="gray40")
        self.history_listbox.pack(fill="x", padx=5, pady=5)
        
        # History buttons
        button_frame = ctk.CTkFrame(panel)
        button_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkButton(button_frame, text="🗑️ Clear", 
                     command=self.clear_history, width=80).pack(side="left", padx=5)
        ctk.CTkButton(button_frame, text="📄 Export", 
                     command=self.export_history, width=80).pack(side="left", padx=5)
    
    def create_image_area(self):
        """Create advanced image display area"""
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.right_panel)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Original tab
        self.original_frame = ctk.CTkFrame(self.notebook)
        self.notebook.add(self.original_frame, text="📷 Original")
        
        self.original_label = ctk.CTkLabel(self.original_frame, text="No image loaded")
        self.original_label.pack(expand=True)
        
        # Processed tab
        self.processed_frame = ctk.CTkFrame(self.notebook)
        self.notebook.add(self.processed_frame, text="🎨 Colorized")
        
        self.processed_label = ctk.CTkLabel(self.processed_frame, text="No processed image")
        self.processed_label.pack(expand=True)
        
        # Split view tab
        self.split_frame = ctk.CTkFrame(self.notebook)
        self.notebook.add(self.split_frame, text="🔀 Split View")
        
        self.split_label = ctk.CTkLabel(self.split_frame, text="Process images to see comparison")
        self.split_label.pack(expand=True)
        
        # Analytics tab
        self.analytics_frame = ctk.CTkFrame(self.notebook)
        self.notebook.add(self.analytics_frame, text="📊 Analytics")
        
        self.analytics_label = ctk.CTkLabel(self.analytics_frame, text="Process images to see analytics")
        self.analytics_label.pack(expand=True)
    
    def load_image(self):
        """Load an image file"""
        file_path = filedialog.askopenfilename(
            title="Select an image",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.tiff *.webp")]
        )
        
        if file_path:
            try:
                # Read image
                image = cv2.imread(file_path)
                if image is None:
                    messagebox.showerror("Error", "Could not read image file")
                    return
                
                # Convert to RGB
                self.original_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                self.current_file = file_path
                
                # Display image
                self.display_image(self.original_image, self.original_label)
                
                self.status_label.configure(text=f"✅ Loaded: {os.path.basename(file_path)}")
                self.add_to_history(f"📂 Loaded: {os.path.basename(file_path)}")
                
                # Switch to original tab
                self.notebook.select(0)
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load image: {e}")
    
    def colorize_image(self):
        """Colorize the loaded image"""
        if self.original_image is None:
            messagebox.showwarning("Warning", "Please load an image first")
            return
        
        if self.processing:
            return
        
        self.processing = True
        self.process_button.configure(state="disabled")
        
        # Start processing in thread
        thread = threading.Thread(target=self._colorize_thread)
        thread.daemon = True
        thread.start()
    
    def _colorize_thread(self):
        """Thread function for colorization"""
        try:
            self.root.after(0, lambda: self.status_label.configure(text="🔄 Colorizing..."))
            self.root.after(0, lambda: self.progress_bar.set(0.1))
            
            # Convert to grayscale and back to RGB
            gray = cv2.cvtColor(self.original_image, cv2.COLOR_RGB2GRAY)
            test_image = cv2.cvtColor(gray, cv2.COLOR_GRAY2RGB)
            
            self.root.after(0, lambda: self.progress_bar.set(0.3))
            
            # Normalize and convert to LAB
            normalized = test_image.astype("float32") / 255.0
            lab_image = cv2.cvtColor(normalized, cv2.COLOR_RGB2LAB)
            resized = cv2.resize(lab_image, (224, 224))
            
            self.root.after(0, lambda: self.progress_bar.set(0.5))
            
            # Extract L channel and process
            L = cv2.split(resized)[0]
            L -= 50
            
            # Forward pass through network
            self.net.setInput(cv2.dnn.blobFromImage(L))
            ab = self.net.forward()[0, :, :, :].transpose((1, 2, 0))
            ab = cv2.resize(ab, (test_image.shape[1], test_image.shape[0]))
            
            self.root.after(0, lambda: self.progress_bar.set(0.7))
            
            # Combine channels and convert back
            L = cv2.split(lab_image)[0]
            Lab_colored = np.concatenate((L[:, :, np.newaxis], ab), axis=2)
            RGB_colored = cv2.cvtColor(Lab_colored, cv2.COLOR_LAB2RGB)
            
            # Apply style and enhancements
            RGB_colored = self.apply_style(RGB_colored)
            RGB_colored = self.apply_enhancements(RGB_colored)
            
            # Clip and convert to uint8
            RGB_colored = np.clip(RGB_colored, 0, 1)
            self.processed_image = (255 * RGB_colored).astype('uint8')
            
            self.root.after(0, lambda: self.progress_bar.set(0.9))
            
            # Update GUI
            self.root.after(0, self._colorize_complete)
            
        except Exception as e:
            self.root.after(0, lambda: self._colorize_error(str(e)))
    
    def _colorize_complete(self):
        """Called when colorization is complete"""
        self.display_image(self.processed_image, self.processed_label)
        self.status_label.configure(text="✅ Colorization complete!")
        self.progress_bar.set(1.0)
        self.add_to_history(f"🎨 Colorized: {os.path.basename(self.current_file) if self.current_file else 'Image'}")
        
        # Create comparison views
        self.create_split_view()
        self.create_analytics()
        
        # Switch to processed tab
        self.notebook.select(1)
        
        # Reset after delay
        self.root.after(2000, lambda: self.progress_bar.set(0))
    
    def _colorize_error(self, error_msg):
        """Called when colorization fails"""
        self.status_label.configure(text=f"❌ Error: {error_msg}")
        self.progress_bar.set(0)
        messagebox.showerror("Error", f"Colorization failed: {error_msg}")
    
    def apply_style(self, image):
        """Apply colorization style"""
        style = self.style_var.get()
        intensity = self.intensity_var.get()
        
        if style == "Vibrant":
            hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
            hsv[:, :, 1] = np.clip(hsv[:, :, 1] * 1.5 * intensity, 0, 1)
            image = cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB)
        elif style == "Vintage":
            sepia_filter = np.array([[0.393, 0.769, 0.189],
                                    [0.349, 0.686, 0.168],
                                    [0.272, 0.534, 0.131]])
            image = np.dot(image, sepia_filter.T)
            image = np.clip(image, 0, 1)
        elif style == "Artistic":
            image[:, :, 0] = np.clip(image[:, :, 0] * 1.2 * intensity, 0, 1)
            image[:, :, 2] = np.clip(image[:, :, 2] * 0.8, 0, 1)
        elif style == "Dramatic":
            image = (image - 0.5) * 1.3 * intensity + 0.5
            hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
            hsv[:, :, 1] = np.clip(hsv[:, :, 1] * 1.3, 0, 1)
            image = cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB)
        elif style == "Cinematic":
            image = (image - 0.5) * 1.2 * intensity + 0.5
            image[image < 0.3] *= np.array([0.9, 0.95, 1.1])
            image[image > 0.7] *= np.array([1.1, 1.05, 0.95])
            
        return np.clip(image, 0, 1)
    
    def apply_enhancements(self, image):
        """Apply image enhancements"""
        img_float = image.astype(np.float32)
        
        # Apply brightness
        img_float += self.brightness_var.get() / 100.0
        
        # Apply contrast
        contrast = (self.contrast_var.get() + 100) / 100.0
        img_float = (img_float - 0.5) * contrast + 0.5
        
        # Apply saturation
        saturation = (self.saturation_var.get() + 100) / 100.0
        hsv = cv2.cvtColor(img_float, cv2.COLOR_RGB2HSV)
        hsv[:, :, 1] = np.clip(hsv[:, :, 1] * saturation, 0, 1)
        img_float = cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB)
        
        # Apply warmth
        warmth = self.warmth_var.get() / 100.0
        if warmth > 0:
            img_float[:, :, 0] = np.clip(img_float[:, :, 0] * (1 + warmth), 0, 1)
            img_float[:, :, 2] = np.clip(img_float[:, :, 2] * (1 - warmth * 0.5), 0, 1)
        else:
            img_float[:, :, 0] = np.clip(img_float[:, :, 0] * (1 + warmth * 0.5), 0, 1)
            img_float[:, :, 2] = np.clip(img_float[:, :, 2] * (1 - warmth), 0, 1)
        
        # Apply sharpness
        sharpness = (self.sharpness_var.get() + 100) / 100.0
        if sharpness != 1.0:
            kernel = np.array([[-1, -1, -1],
                             [-1, 9, -1],
                             [-1, -1, -1]]) * (sharpness - 1.0)
            kernel[1, 1] += 9 - 8 * (sharpness - 1.0)
            img_float = cv2.filter2D(img_float, -1, kernel)
        
        return np.clip(img_float, 0, 1)
    
    def apply_real_time_enhancements(self):
        """Apply enhancements in real-time"""
        if self.original_image is None:
            return
        
        try:
            # Quick re-process with current settings
            gray = cv2.cvtColor(self.original_image, cv2.COLOR_RGB2GRAY)
            test_image = cv2.cvtColor(gray, cv2.COLOR_GRAY2RGB)
            
            normalized = test_image.astype("float32") / 255.0
            lab_image = cv2.cvtColor(normalized, cv2.COLOR_RGB2LAB)
            resized = cv2.resize(lab_image, (224, 224))
            
            L = cv2.split(resized)[0]
            L -= 50
            
            self.net.setInput(cv2.dnn.blobFromImage(L))
            ab = self.net.forward()[0, :, :, :].transpose((1, 2, 0))
            ab = cv2.resize(ab, (test_image.shape[1], test_image.shape[0]))
            
            L = cv2.split(lab_image)[0]
            Lab_colored = np.concatenate((L[:, :, np.newaxis], ab), axis=2)
            RGB_colored = cv2.cvtColor(Lab_colored, cv2.COLOR_LAB2RGB)
            
            # Apply style and enhancements
            RGB_colored = self.apply_style(RGB_colored)
            RGB_colored = self.apply_enhancements(RGB_colored)
            
            RGB_colored = np.clip(RGB_colored, 0, 1)
            self.processed_image = (255 * RGB_colored).astype('uint8')
            
            # Update display
            self.display_image(self.processed_image, self.processed_label)
            
        except Exception as e:
            print(f"Real-time enhancement error: {e}")
    
    def create_split_view(self):
        """Create before/after split view"""
        if self.original_image is None or self.processed_image is None:
            return
        
        try:
            # Resize images to same height
            h1, w1 = self.original_image.shape[:2]
            h2, w2 = self.processed_image.shape[:2]
            
            target_height = min(h1, h2, 400)
            
            orig_resized = cv2.resize(self.original_image, 
                                     (int(w1 * target_height / h1), target_height))
            proc_resized = cv2.resize(self.processed_image, 
                                     (int(w2 * target_height / h2), target_height))
            
            # Create comparison
            split_image = np.hstack([orig_resized, proc_resized])
            
            # Add dividing line
            line_x = orig_resized.shape[1]
            cv2.line(split_image, (line_x, 0), (line_x, target_height), (255, 255, 255), 2)
            
            # Add labels
            cv2.putText(split_image, "BEFORE", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            cv2.putText(split_image, "AFTER", (line_x + 10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            
            self.display_image(split_image, self.split_label)
            
        except Exception as e:
            print(f"Error creating split view: {e}")
    
    def create_analytics(self):
        """Create analytics display"""
        if self.original_image is None or self.processed_image is None:
            return
        
        try:
            # Clear previous widgets
            for widget in self.analytics_frame.winfo_children():
                widget.destroy()
            
            # Create matplotlib figure
            fig = Figure(figsize=(10, 6), facecolor='#1a1a1a')
            
            # Create subplots
            ax1 = fig.add_subplot(2, 2, 1)
            ax2 = fig.add_subplot(2, 2, 2)
            ax3 = fig.add_subplot(2, 2, 3)
            ax4 = fig.add_subplot(2, 2, 4)
            
            # Original RGB histograms
            colors = ['red', 'green', 'blue']
            for i, color in enumerate(colors):
                hist = cv2.calcHist([self.original_image], [i], None, [256], [0, 256])
                ax1.plot(hist, color=color, alpha=0.7, label=f'{color.upper()}')
            ax1.set_title('Original Image Histogram')
            ax1.set_xlabel('Pixel Value')
            ax1.set_ylabel('Frequency')
            ax1.legend()
            ax1.grid(True, alpha=0.3)
            
            # Processed RGB histograms
            for i, color in enumerate(colors):
                hist = cv2.calcHist([self.processed_image], [i], None, [256], [0, 256])
                ax2.plot(hist, color=color, alpha=0.7, label=f'{color.upper()}')
            ax2.set_title('Processed Image Histogram')
            ax2.set_xlabel('Pixel Value')
            ax2.set_ylabel('Frequency')
            ax2.legend()
            ax2.grid(True, alpha=0.3)
            
            # Color distribution comparison
            orig_mean = np.mean(self.original_image, axis=(0, 1))
            proc_mean = np.mean(self.processed_image, axis=(0, 1))
            
            x = np.arange(3)
            width = 0.35
            
            ax3.bar(x - width/2, orig_mean, width, label='Original', color=['red', 'green', 'blue'])
            ax3.bar(x + width/2, proc_mean, width, label='Processed', color=['darkred', 'darkgreen', 'darkblue'])
            ax3.set_title('Mean Color Values')
            ax3.set_xlabel('Channel')
            ax3.set_ylabel('Mean Value')
            ax3.set_xticks(x)
            ax3.set_xticklabels(['Red', 'Green', 'Blue'])
            ax3.legend()
            ax3.grid(True, alpha=0.3)
            
            # Image statistics
            orig_stats = {
                'Mean': np.mean(self.original_image),
                'Std': np.std(self.original_image),
                'Min': np.min(self.original_image),
                'Max': np.max(self.original_image)
            }
            
            proc_stats = {
                'Mean': np.mean(self.processed_image),
                'Std': np.std(self.processed_image),
                'Min': np.min(self.processed_image),
                'Max': np.max(self.processed_image)
            }
            
            stats_data = [orig_stats, proc_stats]
            row_labels = ['Original', 'Processed']
            col_labels = list(orig_stats.keys())
            
            ax4.axis('tight')
            ax4.axis('off')
            table = ax4.table(cellText=[[f"{stats_data[i][col]:.1f}" for col in col_labels] 
                                       for i in range(len(stats_data))],
                             rowLabels=row_labels,
                             colLabels=col_labels,
                             loc='center',
                             cellLoc='center')
            table.auto_set_font_size(False)
            table.set_fontsize(10)
            table.scale(1.2, 1.5)
            ax4.set_title('Image Statistics', pad=20)
            
            plt.tight_layout()
            
            # Embed in tkinter
            canvas = FigureCanvasTkAgg(fig, self.analytics_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)
            
        except Exception as e:
            print(f"Error creating analytics: {e}")
    
    def show_split_view(self):
        """Show split view tab"""
        if self.original_image is None or self.processed_image is None:
            messagebox.showwarning("Warning", "Please load and process an image first")
            return
        self.notebook.select(2)
    
    def show_analytics(self):
        """Show analytics tab"""
        if self.original_image is None or self.processed_image is None:
            messagebox.showwarning("Warning", "Please load and process an image first")
            return
        self.notebook.select(3)
    
    def show_difference(self):
        """Show difference map"""
        if self.original_image is None or self.processed_image is None:
            messagebox.showwarning("Warning", "Please load and process an image first")
            return
        
        # Create difference window
        diff_window = ctk.CTkToplevel(self.root)
        diff_window.title("🔄 Difference Map")
        diff_window.geometry("800x600")
        
        # Calculate difference
        diff = cv2.absdiff(self.original_image, self.processed_image)
        
        # Display difference
        diff_label = ctk.CTkLabel(diff_window)
        diff_label.pack(expand=True, fill="both", padx=10, pady=10)
        
        self.display_image(diff, diff_label)
    
    def auto_enhance(self):
        """Auto enhancement preset"""
        self.brightness_var.set(10)
        self.contrast_var.set(15)
        self.saturation_var.set(20)
        self.warmth_var.set(5)
        self.sharpness_var.set(10)
        self.intensity_var.set(1.2)
        
        if self.processed_image is not None:
            self.apply_real_time_enhancements()
        
        self.add_to_history("✨ Auto Enhance applied")
    
    def vintage_preset(self):
        """Vintage preset"""
        self.brightness_var.set(-5)
        self.contrast_var.set(10)
        self.saturation_var.set(-20)
        self.warmth_var.set(20)
        self.sharpness_var.set(-5)
        self.style_var.set("Vintage")
        self.intensity_var.set(1.0)
        
        if self.processed_image is not None:
            self.apply_real_time_enhancements()
        
        self.add_to_history("🎭 Vintage preset applied")
    
    def cinematic_preset(self):
        """Cinematic preset"""
        self.brightness_var.set(5)
        self.contrast_var.set(25)
        self.saturation_var.set(15)
        self.warmth_var.set(-10)
        self.sharpness_var.set(15)
        self.style_var.set("Cinematic")
        self.intensity_var.set(1.3)
        
        if self.processed_image is not None:
            self.apply_real_time_enhancements()
        
        self.add_to_history("🎬 Cinematic preset applied")
    
    def reset_all(self):
        """Reset all settings"""
        self.brightness_var.set(0)
        self.contrast_var.set(0)
        self.saturation_var.set(0)
        self.warmth_var.set(0)
        self.sharpness_var.set(0)
        self.style_var.set("Natural")
        self.intensity_var.set(1.0)
        
        if self.processed_image is not None:
            self.apply_real_time_enhancements()
        
        self.add_to_history("🔄 All settings reset")
    
    def batch_process(self):
        """Process multiple images"""
        folder_path = filedialog.askdirectory(title="Select folder with images")
        
        if not folder_path:
            return
        
        # Start batch processing in thread
        thread = threading.Thread(target=self._batch_process_thread, args=(folder_path,))
        thread.daemon = True
        thread.start()
    
    def _batch_process_thread(self, folder_path):
        """Thread function for batch processing"""
        try:
            self.root.after(0, lambda: self.status_label.configure(text="🔄 Starting batch process..."))
            
            # Find image files
            image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']
            image_files = []
            
            for ext in image_extensions:
                image_files.extend(Path(folder_path).glob(f'*{ext}'))
                image_files.extend(Path(folder_path).glob(f'*{ext.upper()}'))
            
            if not image_files:
                self.root.after(0, lambda: messagebox.showinfo("Info", "No image files found"))
                return
            
            # Create output folder
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_folder = os.path.join(folder_path, f"colorized_batch_{timestamp}")
            os.makedirs(output_folder, exist_ok=True)
            
            total_files = len(image_files)
            processed_count = 0
            
            for i, image_path in enumerate(image_files):
                try:
                    # Update progress
                    progress = i / total_files
                    self.root.after(0, lambda p=progress: self.progress_bar.set(p))
                    self.root.after(0, lambda f=image_path.name: self.status_label.configure(
                        text=f"🔄 Processing: {f}"))
                    
                    # Read and process image (same logic as single image)
                    image = cv2.imread(str(image_path))
                    if image is None:
                        continue
                    
                    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                    test_image = cv2.cvtColor(gray, cv2.COLOR_GRAY2RGB)
                    
                    normalized = test_image.astype("float32") / 255.0
                    lab_image = cv2.cvtColor(normalized, cv2.COLOR_RGB2LAB)
                    resized = cv2.resize(lab_image, (224, 224))
                    
                    L = cv2.split(resized)[0]
                    L -= 50
                    
                    self.net.setInput(cv2.dnn.blobFromImage(L))
                    ab = self.net.forward()[0, :, :, :].transpose((1, 2, 0))
                    ab = cv2.resize(ab, (test_image.shape[1], test_image.shape[0]))
                    
                    L = cv2.split(lab_image)[0]
                    Lab_colored = np.concatenate((L[:, :, np.newaxis], ab), axis=2)
                    RGB_colored = cv2.cvtColor(Lab_colored, cv2.COLOR_LAB2RGB)
                    
                    # Apply current settings
                    RGB_colored = self.apply_style(RGB_colored)
                    RGB_colored = self.apply_enhancements(RGB_colored)
                    
                    RGB_colored = np.clip(RGB_colored, 0, 1)
                    result_image = (255 * RGB_colored).astype('uint8')
                    
                    # Save result
                    output_path = os.path.join(output_folder, f"colorized_{image_path.name}")
                    bgr_image = cv2.cvtColor(result_image, cv2.COLOR_RGB2BGR)
                    cv2.imwrite(output_path, bgr_image)
                    
                    processed_count += 1
                    
                except Exception as e:
                    print(f"Error processing {image_path}: {e}")
            
            # Complete
            self.root.after(0, lambda: self._batch_complete(processed_count, total_files, output_folder))
            
        except Exception as e:
            self.root.after(0, lambda: self._batch_error(str(e)))
    
    def _batch_complete(self, processed_count, total_files, output_folder):
        """Called when batch processing is complete"""
        self.status_label.configure(text=f"✅ Batch complete: {processed_count}/{total_files} files")
        self.progress_bar.set(1.0)
        self.add_to_history(f"📋 Batch: {processed_count}/{total_files} files processed")
        messagebox.showinfo("Complete", 
                          f"Batch processing complete!\n"
                          f"Processed: {processed_count}/{total_files} files\n"
                          f"Output folder: {output_folder}")
        
        # Reset progress bar
        self.root.after(3000, lambda: self.progress_bar.set(0))
    
    def _batch_error(self, error_msg):
        """Called when batch processing fails"""
        self.status_label.configure(text=f"❌ Batch error: {error_msg}")
        self.progress_bar.set(0)
        messagebox.showerror("Error", f"Batch processing failed: {error_msg}")
    
    def capture_webcam(self):
        """Capture from webcam"""
        try:
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                messagebox.showerror("Error", "Could not access webcam")
                return
            
            ret, frame = cap.read()
            cap.release()
            
            if not ret:
                messagebox.showerror("Error", "Could not capture frame")
                return
            
            self.original_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            self.current_file = "webcam_capture.jpg"
            
            self.display_image(self.original_image, self.original_label)
            self.status_label.configure(text="📸 Webcam image captured")
            self.add_to_history("📸 Webcam capture")
            
            # Switch to original tab
            self.notebook.select(0)
            
        except Exception as e:
            messagebox.showerror("Error", f"Webcam capture failed: {e}")
    
    def save_image(self):
        """Save the processed image"""
        if self.processed_image is None:
            messagebox.showwarning("Warning", "No processed image to save")
            return
        
        format_name = self.format_var.get()
        quality = self.quality_var.get()
        
        extensions = {
            "JPEG": ".jpg",
            "PNG": ".png",
            "TIFF": ".tiff",
            "WebP": ".webp"
        }
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=extensions[format_name],
            filetypes=[(f"{format_name} files", f"*{extensions[format_name]}"), 
                      ("All files", "*.*")]
        )
        
        if file_path:
            try:
                # Convert RGB to BGR for OpenCV
                bgr_image = cv2.cvtColor(self.processed_image, cv2.COLOR_RGB2BGR)
                
                if format_name == "JPEG":
                    params = [cv2.IMWRITE_JPEG_QUALITY, quality]
                elif format_name == "PNG":
                    params = [cv2.IMWRITE_PNG_COMPRESSION, int(quality / 10)]
                else:
                    params = [cv2.IMWRITE_WEBP_QUALITY, quality]
                
                success = cv2.imwrite(file_path, bgr_image, params)
                
                if success:
                    self.status_label.configure(text=f"✅ Saved: {os.path.basename(file_path)}")
                    self.add_to_history(f"💾 Saved: {os.path.basename(file_path)}")
                    messagebox.showinfo("Success", "Image saved successfully!")
                else:
                    messagebox.showerror("Error", "Failed to save image")
                    
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save image: {e}")
    
    def export_comparison(self):
        """Export before/after comparison"""
        if self.original_image is None or self.processed_image is None:
            messagebox.showwarning("Warning", "Please load and process an image first")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".jpg",
            filetypes=[("JPEG files", "*.jpg"), ("PNG files", "*.png")]
        )
        
        if file_path:
            try:
                # Create comparison image
                h1, w1 = self.original_image.shape[:2]
                h2, w2 = self.processed_image.shape[:2]
                
                target_height = min(h1, h2, 600)
                
                orig_resized = cv2.resize(self.original_image, 
                                         (int(w1 * target_height / h1), target_height))
                proc_resized = cv2.resize(self.processed_image, 
                                         (int(w2 * target_height / h2), target_height))
                
                comparison = np.hstack([orig_resized, proc_resized])
                
                # Add dividing line and labels
                line_x = orig_resized.shape[1]
                cv2.line(comparison, (line_x, 0), (line_x, target_height), (255, 255, 255), 3)
                cv2.putText(comparison, "BEFORE", (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 3)
                cv2.putText(comparison, "AFTER", (line_x + 20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 3)
                
                # Save comparison
                bgr_comparison = cv2.cvtColor(comparison, cv2.COLOR_RGB2BGR)
                success = cv2.imwrite(file_path, bgr_comparison)
                
                if success:
                    self.status_label.configure(text=f"✅ Comparison exported: {os.path.basename(file_path)}")
                    self.add_to_history(f"📊 Comparison exported: {os.path.basename(file_path)}")
                    messagebox.showinfo("Success", "Comparison exported successfully!")
                else:
                    messagebox.showerror("Error", "Failed to export comparison")
                    
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export comparison: {e}")
    
    def add_to_history(self, action):
        """Add action to history"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.processing_history.append(f"[{timestamp}] {action}")
        
        self.history_listbox.insert(0, f"[{timestamp}] {action}")
        
        if self.history_listbox.size() > 10:
            self.history_listbox.delete(10, tk.END)
    
    def clear_history(self):
        """Clear processing history"""
        self.processing_history = []
        self.history_listbox.delete(0, tk.END)
        self.add_to_history("🗑️ History cleared")
    
    def export_history(self):
        """Export processing history"""
        if not self.processing_history:
            messagebox.showinfo("Info", "No history to export")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'w') as f:
                    f.write("AI Image Colorizer - Processing History\n")
                    f.write("=" * 50 + "\n")
                    f.write(f"Exported: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write("=" * 50 + "\n\n")
                    
                    for entry in self.processing_history:
                        f.write(entry + "\n")
                
                messagebox.showinfo("Success", "History exported successfully!")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export history: {e}")
    
    def display_image(self, image, label):
        """Display an image in a label"""
        try:
            # Resize for display
            h, w = image.shape[:2]
            max_size = 500
            
            if h > max_size or w > max_size:
                if h > w:
                    new_h = max_size
                    new_w = int(w * max_size / h)
                else:
                    new_w = max_size
                    new_h = int(h * max_size / w)
                image = cv2.resize(image, (new_w, new_h))
            
            # Convert to PIL Image and then to PhotoImage
            pil_image = Image.fromarray(image)
            photo = ImageTk.PhotoImage(image=pil_image)
            
            label.configure(image=photo, text="")
            label.image = photo  # Keep a reference
            
        except Exception as e:
            print(f"Error displaying image: {e}")
            label.configure(text="Error displaying image")
    
    def run(self):
        """Start the application"""
        self.root.mainloop()

if __name__ == "__main__":
    app = ProfessionalColorizerApp()
    app.run()

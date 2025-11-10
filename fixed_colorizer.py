"""
Fixed AI Image Colorizer - Working Version
Simple and reliable implementation
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import customtkinter as ctk
from PIL import Image, ImageTk
import cv2
import numpy as np
import os
import threading
from pathlib import Path

# Set appearance mode
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class FixedColorizerApp:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("AI Image Colorizer - Fixed Version")
        self.root.geometry("1200x800")
        
        # Initialize variables
        self.original_image = None
        self.processed_image = None
        self.current_file = None
        
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
            
            print("Model loaded successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load model: {e}")
            print(f"Model loading error: {e}")
    
    def create_widgets(self):
        """Create GUI widgets"""
        # Main container
        main_frame = ctk.CTkFrame(self.root)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Title
        title = ctk.CTkLabel(main_frame, text="🎨 AI Image Colorizer", 
                           font=ctk.CTkFont(size=24, weight="bold"))
        title.pack(pady=10)
        
        # Button frame
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.pack(fill="x", padx=10, pady=5)
        
        # Buttons
        ctk.CTkButton(button_frame, text="📂 Load Image", 
                     command=self.load_image, width=150).pack(side="left", padx=5)
        ctk.CTkButton(button_frame, text="🎨 Colorize", 
                     command=self.colorize_image, width=150).pack(side="left", padx=5)
        ctk.CTkButton(button_frame, text="📋 Batch Process", 
                     command=self.batch_process, width=150).pack(side="left", padx=5)
        ctk.CTkButton(button_frame, text="💾 Save", 
                     command=self.save_image, width=150).pack(side="left", padx=5)
        
        # Status label
        self.status_label = ctk.CTkLabel(main_frame, text="Ready to load an image")
        self.status_label.pack(pady=5)
        
        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(main_frame)
        self.progress_bar.pack(fill="x", padx=10, pady=5)
        self.progress_bar.set(0)
        
        # Image display frame
        image_frame = ctk.CTkFrame(main_frame)
        image_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(image_frame)
        self.notebook.pack(fill="both", expand=True)
        
        # Original tab
        original_frame = ctk.CTkFrame(self.notebook)
        self.notebook.add(original_frame, text="Original")
        self.original_label = ctk.CTkLabel(original_frame, text="No image loaded")
        self.original_label.pack(expand=True)
        
        # Processed tab
        processed_frame = ctk.CTkFrame(self.notebook)
        self.notebook.add(processed_frame, text="Colorized")
        self.processed_label = ctk.CTkLabel(processed_frame, text="No processed image")
        self.processed_label.pack(expand=True)
    
    def load_image(self):
        """Load an image file"""
        file_path = filedialog.askopenfilename(
            title="Select an image",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.tiff")]
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
                
                self.status_label.configure(text=f"Loaded: {os.path.basename(file_path)}")
                self.notebook.select(0)  # Show original tab
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load image: {e}")
    
    def colorize_image(self):
        """Colorize the loaded image"""
        if self.original_image is None:
            messagebox.showwarning("Warning", "Please load an image first")
            return
        
        # Start processing in thread
        thread = threading.Thread(target=self._colorize_thread)
        thread.daemon = True
        thread.start()
    
    def _colorize_thread(self):
        """Thread function for colorization"""
        try:
            self.root.after(0, lambda: self.status_label.configure(text="Colorizing..."))
            self.root.after(0, lambda: self.progress_bar.set(0.2))
            
            # Convert to grayscale and back to RGB
            gray = cv2.cvtColor(self.original_image, cv2.COLOR_RGB2GRAY)
            test_image = cv2.cvtColor(gray, cv2.COLOR_GRAY2RGB)
            
            self.root.after(0, lambda: self.progress_bar.set(0.4))
            
            # Normalize and convert to LAB
            normalized = test_image.astype("float32") / 255.0
            lab_image = cv2.cvtColor(normalized, cv2.COLOR_RGB2LAB)
            resized = cv2.resize(lab_image, (224, 224))
            
            self.root.after(0, lambda: self.progress_bar.set(0.6))
            
            # Extract L channel and process
            L = cv2.split(resized)[0]
            L -= 50
            
            # Forward pass through network
            self.net.setInput(cv2.dnn.blobFromImage(L))
            ab = self.net.forward()[0, :, :, :].transpose((1, 2, 0))
            ab = cv2.resize(ab, (test_image.shape[1], test_image.shape[0]))
            
            self.root.after(0, lambda: self.progress_bar.set(0.8))
            
            # Combine channels and convert back
            L = cv2.split(lab_image)[0]
            Lab_colored = np.concatenate((L[:, :, np.newaxis], ab), axis=2)
            RGB_colored = cv2.cvtColor(Lab_colored, cv2.COLOR_LAB2RGB)
            
            # Clip and convert to uint8
            RGB_colored = np.clip(RGB_colored, 0, 1)
            self.processed_image = (255 * RGB_colored).astype('uint8')
            
            # Update GUI
            self.root.after(0, self._colorize_complete)
            
        except Exception as e:
            self.root.after(0, lambda: self._colorize_error(str(e)))
    
    def _colorize_complete(self):
        """Called when colorization is complete"""
        self.display_image(self.processed_image, self.processed_label)
        self.status_label.configure(text="Colorization complete!")
        self.progress_bar.set(1.0)
        self.notebook.select(1)  # Show processed tab
        
        # Reset progress bar after delay
        self.root.after(2000, lambda: self.progress_bar.set(0))
    
    def _colorize_error(self, error_msg):
        """Called when colorization fails"""
        self.status_label.configure(text=f"Error: {error_msg}")
        self.progress_bar.set(0)
        messagebox.showerror("Error", f"Colorization failed: {error_msg}")
    
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
            self.root.after(0, lambda: self.status_label.configure(text="Starting batch process..."))
            
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
            output_folder = os.path.join(folder_path, "colorized_output")
            os.makedirs(output_folder, exist_ok=True)
            
            total_files = len(image_files)
            processed_count = 0
            
            for i, image_path in enumerate(image_files):
                try:
                    # Update progress
                    progress = i / total_files
                    self.root.after(0, lambda p=progress: self.progress_bar.set(p))
                    self.root.after(0, lambda f=image_path.name: self.status_label.configure(
                        text=f"Processing: {f}"))
                    
                    # Read image
                    image = cv2.imread(str(image_path))
                    if image is None:
                        continue
                    
                    # Convert to grayscale and process
                    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                    test_image = cv2.cvtColor(gray, cv2.COLOR_GRAY2RGB)
                    
                    # Normalize and convert to LAB
                    normalized = test_image.astype("float32") / 255.0
                    lab_image = cv2.cvtColor(normalized, cv2.COLOR_RGB2LAB)
                    resized = cv2.resize(lab_image, (224, 224))
                    
                    # Extract L channel and process
                    L = cv2.split(resized)[0]
                    L -= 50
                    
                    # Forward pass through network
                    self.net.setInput(cv2.dnn.blobFromImage(L))
                    ab = self.net.forward()[0, :, :, :].transpose((1, 2, 0))
                    ab = cv2.resize(ab, (test_image.shape[1], test_image.shape[0]))
                    
                    # Combine channels and convert back
                    L = cv2.split(lab_image)[0]
                    Lab_colored = np.concatenate((L[:, :, np.newaxis], ab), axis=2)
                    RGB_colored = cv2.cvtColor(Lab_colored, cv2.COLOR_LAB2RGB)
                    
                    # Clip and convert to uint8
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
        self.status_label.configure(text=f"Batch complete: {processed_count}/{total_files} files")
        self.progress_bar.set(1.0)
        messagebox.showinfo("Complete", 
                          f"Batch processing complete!\n"
                          f"Processed: {processed_count}/{total_files} files\n"
                          f"Output folder: {output_folder}")
        
        # Reset progress bar
        self.root.after(3000, lambda: self.progress_bar.set(0))
    
    def _batch_error(self, error_msg):
        """Called when batch processing fails"""
        self.status_label.configure(text=f"Batch error: {error_msg}")
        self.progress_bar.set(0)
        messagebox.showerror("Error", f"Batch processing failed: {error_msg}")
    
    def save_image(self):
        """Save the processed image"""
        if self.processed_image is None:
            messagebox.showwarning("Warning", "No processed image to save")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".jpg",
            filetypes=[("JPEG files", "*.jpg"), ("PNG files", "*.png"), 
                      ("All files", "*.*")]
        )
        
        if file_path:
            try:
                # Convert RGB to BGR for OpenCV
                bgr_image = cv2.cvtColor(self.processed_image, cv2.COLOR_RGB2BGR)
                success = cv2.imwrite(file_path, bgr_image)
                
                if success:
                    self.status_label.configure(text=f"Saved: {os.path.basename(file_path)}")
                    messagebox.showinfo("Success", "Image saved successfully!")
                else:
                    messagebox.showerror("Error", "Failed to save image")
                    
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save image: {e}")
    
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
    app = FixedColorizerApp()
    app.run()

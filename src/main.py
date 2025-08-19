import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import threading
from qr_code_maker import process_csv


class QRCodeMakerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("QR Code Maker")
        self.root.geometry("700x700")
        self.root.resizable(True, True)
        
        # Variables
        self.single_title = tk.StringVar()
        self.single_url = tk.StringVar()
        self.csv_file_path = tk.StringVar()
        self.save_directory = tk.StringVar()
        self.font_file_path = tk.StringVar()
        
        # Set default values
        self.save_directory.set(os.path.abspath("output"))
        self.font_file_path.set("")
        
        self.setup_ui()
    
    def setup_ui(self):
        # Main frame with padding
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="QR Code Maker", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Save Directory Section (moved to top, above both sections)
        save_frame = ttk.LabelFrame(main_frame, text="Save Directory", padding="10")
        save_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 20))
        save_frame.columnconfigure(1, weight=1)
        
        # Save Directory Selection
        ttk.Label(save_frame, text="Save Directory:").grid(row=0, column=0, sticky=tk.W, pady=5)
        save_entry = ttk.Entry(save_frame, textvariable=self.save_directory, width=50)
        save_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 5), pady=5)
        ttk.Button(save_frame, text="Browse", command=self.browse_save_dir).grid(row=0, column=2, pady=5)
        
        # Font File Section (moved to top, above both sections)
        font_frame = ttk.LabelFrame(main_frame, text="Font Settings", padding="10")
        font_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 20))
        font_frame.columnconfigure(1, weight=1)
        
        # Font File Selection
        ttk.Label(font_frame, text="Font File:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.font_entry = ttk.Entry(font_frame, textvariable=self.font_file_path, width=50)
        self.font_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 5), pady=5)
        self.font_browse_button = ttk.Button(font_frame, text="Browse", command=self.browse_font)
        self.font_browse_button.grid(row=0, column=2, pady=5)
        
        # Optional checkbox
        self.use_custom_font = tk.BooleanVar(value=False)
        font_check = ttk.Checkbutton(font_frame, text="Use custom font (optional)", 
                                   variable=self.use_custom_font, command=self.toggle_font_field)
        font_check.grid(row=1, column=1, sticky=tk.W, pady=5)
        
        # Single QR Code Section
        single_frame = ttk.LabelFrame(main_frame, text="Single QR Code", padding="10")
        single_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 20))
        single_frame.columnconfigure(1, weight=1)
        
        # Title input
        ttk.Label(single_frame, text="Title:").grid(row=0, column=0, sticky=tk.W, pady=5)
        title_entry = ttk.Entry(single_frame, textvariable=self.single_title, width=50)
        title_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 5), pady=5)
        
        # URL input
        ttk.Label(single_frame, text="URL:").grid(row=1, column=0, sticky=tk.W, pady=5)
        url_entry = ttk.Entry(single_frame, textvariable=self.single_url, width=50)
        url_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(10, 5), pady=5)
        
        # Single QR Code button
        self.single_button = ttk.Button(single_frame, text="Generate Single QR Code", 
                                       command=self.generate_single_qr, style="Accent.TButton")
        self.single_button.grid(row=2, column=0, columnspan=2, pady=10)
        
        # CSV Batch Processing Section
        csv_frame = ttk.LabelFrame(main_frame, text="Batch Processing (CSV)", padding="10")
        csv_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 20))
        csv_frame.columnconfigure(1, weight=1)
        
        # CSV File Selection
        ttk.Label(csv_frame, text="CSV File:").grid(row=0, column=0, sticky=tk.W, pady=5)
        csv_entry = ttk.Entry(csv_frame, textvariable=self.csv_file_path, width=50)
        csv_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 5), pady=5)
        ttk.Button(csv_frame, text="Browse", command=self.browse_csv).grid(row=0, column=2, pady=5)
        
        # CSV Process button
        self.csv_process_button = ttk.Button(csv_frame, text="Generate QR Codes from CSV", 
                                           command=self.process_qr_codes, style="Accent.TButton")
        self.csv_process_button.grid(row=1, column=0, columnspan=2, pady=10)
        
        # Progress bar
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        # Status label
        self.status_label = ttk.Label(main_frame, text="Ready to generate QR codes")
        self.status_label.grid(row=6, column=0, columnspan=3, pady=5)
        
        # Initially disable font field
        self.toggle_font_field()
    
    def toggle_font_field(self):
        """Enable/disable font field based on checkbox"""
        if self.use_custom_font.get():
            self.font_entry.config(state='normal')
            self.font_browse_button.config(state='normal')
        else:
            self.font_entry.config(state='disabled')
            self.font_browse_button.config(state='disabled')
    
    def browse_csv(self):
        """Browse for CSV file"""
        filename = filedialog.askopenfilename(
            title="Select CSV File",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if filename:
            self.csv_file_path.set(filename)
    
    def browse_save_dir(self):
        """Browse for save directory"""
        directory = filedialog.askdirectory(title="Select Save Directory")
        if directory:
            # Convert to absolute path to show full directory
            self.save_directory.set(os.path.abspath(directory))
    
    def browse_font(self):
        """Browse for font file"""
        filename = filedialog.askopenfilename(
            title="Select Font File",
            filetypes=[("Font files", "*.ttf;*.otf"), ("All files", "*.*")]
        )
        if filename:
            self.font_file_path.set(filename)
    
    def validate_single_inputs(self):
        """Validate single QR code inputs"""
        if not self.single_title.get().strip():
            messagebox.showerror("Error", "Please enter a title")
            return False
        
        if not self.single_url.get().strip():
            messagebox.showerror("Error", "Please enter a URL")
            return False
        
        # Create save directory if it doesn't exist
        save_dir = self.save_directory.get()
        if save_dir and not os.path.exists(save_dir):
            try:
                os.makedirs(save_dir)
            except Exception as e:
                messagebox.showerror("Error", f"Could not create save directory: {e}")
                return False
        
        return True
    
    def validate_csv_inputs(self):
        """Validate CSV processing inputs"""
        if not self.csv_file_path.get():
            messagebox.showerror("Error", "Please select a CSV file")
            return False
        
        if not os.path.exists(self.csv_file_path.get()):
            messagebox.showerror("Error", "CSV file does not exist")
            return False
        
        # Create save directory if it doesn't exist
        save_dir = self.save_directory.get()
        if save_dir and not os.path.exists(save_dir):
            try:
                os.makedirs(save_dir)
            except Exception as e:
                messagebox.showerror("Error", f"Could not create save directory: {e}")
                return False
        
        return True
    
    def generate_single_qr(self):
        """Generate a single QR code"""
        if not self.validate_single_inputs():
            return
        
        # Disable UI during processing
        self.single_button.config(state='disabled')
        self.csv_process_button.config(state='disabled')
        self.progress.start()
        self.status_label.config(text="Generating single QR code...")
        
        # Get font path (empty string if not using custom font)
        font_path = self.font_file_path.get() if self.use_custom_font.get() else ""
        
        # Start processing in separate thread
        thread = threading.Thread(
            target=self._process_single_thread,
            args=(self.single_title.get().strip(), self.single_url.get().strip(), 
                  self.save_directory.get(), font_path)
        )
        thread.daemon = True
        thread.start()
    
    def process_qr_codes(self):
        """Process CSV QR code generation in a separate thread"""
        if not self.validate_csv_inputs():
            return
        
        # Disable UI during processing
        self.single_button.config(state='disabled')
        self.csv_process_button.config(state='disabled')
        self.progress.start()
        self.status_label.config(text="Generating QR codes from CSV...")
        
        # Get font path (empty string if not using custom font)
        font_path = self.font_file_path.get() if self.use_custom_font.get() else ""
        
        # Start processing in separate thread
        thread = threading.Thread(
            target=self._process_csv_thread,
            args=(self.csv_file_path.get(), self.save_directory.get(), font_path)
        )
        thread.daemon = True
        thread.start()
    
    def _process_single_thread(self, title, url, save_dir, font_path):
        """Process single QR code in separate thread"""
        try:
            from qr_code_maker import create_full_page_image, clean_filename
            import os
            
            # Create the image
            img = create_full_page_image(title, url, font_path, save_dir)
            
            # Save the image
            clean_title = clean_filename(title)
            filename = f"{clean_title}.png"
            filepath = os.path.join(save_dir, filename)
            img.save(filepath, format='PNG', dpi=(300, 300))
            
            # Update UI on main thread
            self.root.after(0, self._processing_complete, True, f"Single QR code generated successfully: {filename}")
            
        except Exception as e:
            # Update UI on main thread
            self.root.after(0, self._processing_complete, False, f"Error: {str(e)}")
    
    def _process_csv_thread(self, csv_path, save_dir, font_path):
        """Process CSV QR codes in separate thread"""
        try:
            process_csv(csv_path, save_dir, font_path)
            
            # Update UI on main thread
            self.root.after(0, self._processing_complete, True, "QR codes from CSV generated successfully!")
            
        except Exception as e:
            # Update UI on main thread
            self.root.after(0, self._processing_complete, False, f"Error: {str(e)}")
    
    def _processing_complete(self, success, message):
        """Handle processing completion"""
        self.progress.stop()
        self.single_button.config(state='normal')
        self.csv_process_button.config(state='normal')
        
        if success:
            self.status_label.config(text=message)
            messagebox.showinfo("Success", message)
        else:
            self.status_label.config(text=message)
            messagebox.showerror("Error", message)


def main():
    root = tk.Tk()
    app = QRCodeMakerGUI(root)
    
    # Configure style
    style = ttk.Style()
    style.theme_use('clam')
    
    # Center window on screen
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
    y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
    root.geometry(f"+{x}+{y}")
    
    root.mainloop()


if __name__ == "__main__":
    main()

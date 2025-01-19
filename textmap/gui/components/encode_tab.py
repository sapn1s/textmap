import tkinter as tk
from tkinter import ttk, messagebox
from ..utils import browse_file, create_scrolled_text, copy_to_clipboard, save_to_file
from ...encoder import MnemonicEncoder
from ...text_processor import TextProcessor

class EncodeTab:
    def __init__(self, parent):
        self.encoder = MnemonicEncoder()
        self.processor = TextProcessor()
        
        self.frame = ttk.Frame(parent, padding="5")
        self.frame.columnconfigure(1, weight=1)
        
        self.setup_ui()
        
    def setup_ui(self):
        # Source Text Input Options
        ttk.Label(self.frame, text="Source Text File:").grid(row=0, column=0, sticky=tk.W)
        
        # File Selection with clear button
        file_frame = ttk.Frame(self.frame)
        file_frame.grid(row=0, column=1, columnspan=2, sticky=(tk.W, tk.E))
        file_frame.columnconfigure(0, weight=1)
        
        self.source_file_var = tk.StringVar()
        source_entry = ttk.Entry(file_frame, textvariable=self.source_file_var)
        source_entry.grid(row=0, column=0, padx=5, sticky=(tk.W, tk.E))
        
        ttk.Button(file_frame, text="Browse", 
                  command=self.browse_source_file).grid(row=0, column=1, padx=2)
        ttk.Button(file_frame, text="Clear", 
                  command=self.clear_source).grid(row=0, column=2)
        
        # Source Text Area with scrollbar
        ttk.Label(self.frame, text="Source Text:").grid(row=1, column=0, sticky=tk.W)
        source_frame, self.source_text = create_scrolled_text(self.frame, height=10)
        source_frame.grid(row=2, column=0, columnspan=3, pady=5, sticky=(tk.W, tk.E))
        
        # Bind text changes to clear file path
        self.source_text.bind('<<Modified>>', self.on_text_modified)
        
        # Secret Information
        ttk.Label(self.frame, text="Secret Information:").grid(row=3, column=0, sticky=tk.W)
        secret_frame, self.secret_text = create_scrolled_text(self.frame, height=3)
        secret_frame.grid(row=4, column=0, columnspan=3, pady=5, sticky=(tk.W, tk.E))

       # Bottom button frame
        button_frame = ttk.Frame(self.frame)
        button_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Button(button_frame, text="Encode", 
                  command=self.encode).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Clear All", 
                  command=self.clear_all).pack(side=tk.LEFT, padx=5)
        self.status_label = ttk.Label(button_frame, text="")
        self.status_label.pack(side=tk.LEFT, padx=5)

        # Key Display Frame
        key_frame = ttk.LabelFrame(self.frame, text="Generated Key", padding="5")
        key_frame.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        key_frame.columnconfigure(1, weight=1)

        self.key_var = tk.StringVar()
        self.key_entry = ttk.Entry(key_frame, textvariable=self.key_var, state='readonly')
        self.key_entry.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), padx=5, pady=5)

        key_buttons_frame = ttk.Frame(key_frame)
        key_buttons_frame.grid(row=1, column=0, columnspan=2, pady=5)
        
        ttk.Button(key_buttons_frame, text="Copy Key", 
                  command=self.copy_key).pack(side=tk.LEFT, padx=5)
        ttk.Button(key_buttons_frame, text="Save Key", 
                  command=self.save_key).pack(side=tk.LEFT, padx=5)

    def browse_source_file(self):
        """Handle file browsing and loading"""
        filename = browse_file(self.source_file_var)
        if filename:
            try:
                text = self.processor.prepare_text_for_encoding(filename)
                self.source_text.delete(1.0, tk.END)
                self.source_text.insert(1.0, text)
            except Exception as e:
                messagebox.showerror("Error", f"Error loading file: {str(e)}")
                self.source_file_var.set("")
    
    def on_text_modified(self, event=None):
        """Clear file path if text is modified directly"""
        if self.source_text.edit_modified():
            self.source_file_var.set("")
            self.source_text.edit_modified(False)
    
    def clear_source(self):
        """Clear source text and file path"""
        self.source_file_var.set("")
        self.source_text.delete(1.0, tk.END)
    
    def clear_all(self):
        """Clear all input fields"""
        self.clear_source()
        self.secret_text.delete(1.0, tk.END)
        self.key_var.set("")
        self.status_label.config(text="")
    
    def get_source_text(self):
        """Get text from text widget"""
        text = self.source_text.get(1.0, tk.END).strip()
        if not text:
            raise ValueError("Please provide source text")
        return self.processor.normalize_text(text)
    
    def copy_key(self):
        """Copy key to clipboard"""
        key = self.key_var.get()
        if key:
            copy_to_clipboard(self.frame.winfo_toplevel(), key)

    def save_key(self):
        """Save key to file"""
        key = self.key_var.get()
        if key:
            save_to_file(key)
    
    def encode(self):
        try:
            text = self.get_source_text()
            secret = self.secret_text.get(1.0, tk.END).strip()
            
            if not secret:
                raise ValueError('Please provide secret information to encode')
                
            if not self.processor.validate_text_source(text):
                if not messagebox.askyesno("Warning", 
                    "The source text might not be suitable for secure encoding. Continue anyway?"):
                    return
                    
            _, key = self.encoder.encode(secret, text)
            
            # Update key display
            self.key_var.set(key)
            
            self.status_label.config(text="Encoding successful", foreground="green")
            
        except Exception as e:
            self.status_label.config(text=f"Error: {str(e)}", foreground="red")
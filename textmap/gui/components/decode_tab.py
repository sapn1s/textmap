import tkinter as tk
from tkinter import ttk, messagebox
from ..utils import browse_file, create_scrolled_text
from ...encoder import MnemonicEncoder
from ...text_processor import TextProcessor

class DecodeTab:
    def __init__(self, parent):
        self.encoder = MnemonicEncoder()
        self.processor = TextProcessor()
        
        self.frame = ttk.Frame(parent, padding="5")
        self.frame.columnconfigure(1, weight=1)
        
        self.setup_ui()
        
    def setup_ui(self):
        # Encoded Text Input Options
        ttk.Label(self.frame, text="Encoded Text File:").grid(row=0, column=0, sticky=tk.W)
        
        # File Selection with clear button
        file_frame = ttk.Frame(self.frame)
        file_frame.grid(row=0, column=1, columnspan=2, sticky=(tk.W, tk.E))
        file_frame.columnconfigure(0, weight=1)
        
        self.encoded_file_var = tk.StringVar()
        encoded_entry = ttk.Entry(file_frame, textvariable=self.encoded_file_var)
        encoded_entry.grid(row=0, column=0, padx=5, sticky=(tk.W, tk.E))
        
        ttk.Button(file_frame, text="Browse", 
                  command=self.browse_encoded_file).grid(row=0, column=1, padx=2)
        ttk.Button(file_frame, text="Clear", 
                  command=self.clear_encoded).grid(row=0, column=2)
        
        # Encoded Text Area with scrollbar
        ttk.Label(self.frame, text="Encoded Text:").grid(row=1, column=0, sticky=tk.W)
        encoded_frame, self.encoded_text = create_scrolled_text(self.frame, height=10)
        encoded_frame.grid(row=2, column=0, columnspan=3, pady=5, sticky=(tk.W, tk.E))
        
        # Bind text changes to clear file path
        self.encoded_text.bind('<<Modified>>', self.on_text_modified)
        
        # Key Input
        ttk.Label(self.frame, text="Key:").grid(row=3, column=0, sticky=tk.W)
        key_frame, self.key_text = create_scrolled_text(self.frame, height=3)
        key_frame.grid(row=4, column=0, columnspan=3, pady=5, sticky=(tk.W, tk.E))

        # Bottom button frame
        button_frame = ttk.Frame(self.frame)
        button_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Button(button_frame, text="Decode", 
                  command=self.decode).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Clear All", 
                  command=self.clear_all).pack(side=tk.LEFT, padx=5)
        self.status_label = ttk.Label(button_frame, text="")
        self.status_label.pack(side=tk.LEFT, padx=5)

        # Decoded Output
        output_frame = ttk.LabelFrame(self.frame, text="Decoded Output", padding="5")
        output_frame.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        decoded_frame, self.decoded_text = create_scrolled_text(output_frame, height=3)
        decoded_frame.grid(row=0, column=0, columnspan=3, pady=5, sticky=(tk.W, tk.E))
        self.decoded_text.config(state='disabled')
    
    def browse_encoded_file(self):
        """Handle file browsing and loading"""
        filename = browse_file(self.encoded_file_var)
        if filename:
            try:
                text = self.processor.prepare_text_for_encoding(filename)
                self.encoded_text.delete(1.0, tk.END)
                self.encoded_text.insert(1.0, text)
            except Exception as e:
                messagebox.showerror("Error", f"Error loading file: {str(e)}")
                self.encoded_file_var.set("")
    
    def on_text_modified(self, event=None):
        """Clear file path if text is modified directly"""
        if self.encoded_text.edit_modified():
            self.encoded_file_var.set("")
            self.encoded_text.edit_modified(False)
    
    def clear_encoded(self):
        """Clear encoded text and file path"""
        self.encoded_file_var.set("")
        self.encoded_text.delete(1.0, tk.END)
    
    def clear_all(self):
        """Clear all input fields"""
        self.clear_encoded()
        self.key_text.delete(1.0, tk.END)
        self.decoded_text.config(state='normal')
        self.decoded_text.delete(1.0, tk.END)
        self.decoded_text.config(state='disabled')
        self.status_label.config(text="")
    
    def get_encoded_text(self):
        """Get encoded text from text widget"""
        text = self.encoded_text.get(1.0, tk.END).strip()
        if not text:
            raise ValueError("Please provide encoded text")
        return text
    
    def decode(self):
        try:
            encoded_text = self.get_encoded_text()
            key = self.key_text.get(1.0, tk.END).strip()
            
            if not key:
                raise ValueError('Please provide the decoding key')
                
            decoded = self.encoder.decode(encoded_text, key)
            
            # Update decoded output
            self.decoded_text.config(state='normal')
            self.decoded_text.delete(1.0, tk.END)
            self.decoded_text.insert(1.0, decoded)
            self.decoded_text.config(state='disabled')
            
            self.status_label.config(text="Decoding successful", foreground="green")
            
        except Exception as e:
            self.status_label.config(text=f"Error: {str(e)}", foreground="red")
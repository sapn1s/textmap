import tkinter as tk
from tkinter import ttk
from ..utils import save_to_file, copy_to_clipboard, create_scrolled_text

class OutputFrame:
    def __init__(self, parent):
        self.frame = ttk.LabelFrame(parent, text="Output", padding="5")
        self.frame.columnconfigure(0, weight=1)
        self.parent = parent  # Save reference for clipboard operations
        
        self.setup_ui()
        
    def setup_ui(self):
        # Output Text with scrollbar
        output_frame, self.output_text = create_scrolled_text(self.frame, height=10)
        output_frame.grid(row=0, column=0, columnspan=3, pady=5, sticky=(tk.W, tk.E))
        self.output_text.config(state='disabled')
        
        # Key Display (optional, shown only when encoding)
        key_frame = ttk.Frame(self.frame)
        key_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        key_frame.columnconfigure(1, weight=1)
        
        self.key_label = ttk.Label(key_frame, text="Generated Key:")
        self.key_label.grid(row=0, column=0, padx=5)
        
        self.key_var = tk.StringVar()
        self.key_display = ttk.Entry(key_frame, textvariable=self.key_var, state='readonly')
        self.key_display.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5)
        
        ttk.Button(key_frame, text="Copy Key", 
                  command=self.copy_key).grid(row=0, column=2, padx=5)
        
        # Initially hide key-related widgets
        self.hide_key_widgets()
        
        # Buttons Frame
        button_frame = ttk.Frame(self.frame)
        button_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Button(button_frame, text="Copy Output", 
                  command=self.copy_output).pack(side=tk.LEFT, padx=5)
# Buttons Frame (continued)
        ttk.Button(button_frame, text="Save Output", 
                  command=self.save_output).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Save Key", 
                  command=self.save_key).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Clear", 
                  command=self.clear_output).pack(side=tk.LEFT, padx=5)
    
    def set_output(self, text: str) -> None:
        """Update the output text widget"""
        self.output_text.config(state='normal')
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(1.0, text)
        self.output_text.config(state='disabled')
    
    def clear_output(self) -> None:
        """Clear all output fields"""
        self.output_text.config(state='normal')
        self.output_text.delete(1.0, tk.END)
        self.output_text.config(state='disabled')
        self.key_var.set("")
        self.hide_key_widgets()
    
    def set_key(self, key: str) -> None:
        """Set the key and show key-related widgets"""
        self.key_var.set(key)
        self.show_key_widgets()
    
    def show_key_widgets(self) -> None:
        """Show the key-related widgets"""
        self.key_label.grid()
        self.key_display.grid()
    
    def hide_key_widgets(self) -> None:
        """Hide the key-related widgets"""
        self.key_label.grid_remove()
        self.key_display.grid_remove()
    
    def copy_output(self) -> None:
        """Copy output text to clipboard"""
        output_text = self.output_text.get(1.0, tk.END).strip()
        if output_text:
            copy_to_clipboard(self.parent.winfo_toplevel(), output_text)
    
    def copy_key(self) -> None:
        """Copy key to clipboard"""
        key = self.key_var.get()
        if key:
            copy_to_clipboard(self.parent.winfo_toplevel(), key)
    
    def save_output(self) -> None:
        """Save output text to file"""
        output_text = self.output_text.get(1.0, tk.END).strip()
        if output_text:
            save_to_file(output_text)
    
    def save_key(self) -> None:
        """Save key to file"""
        key = self.key_var.get()
        if key:
            save_to_file(key)
import tkinter as tk
from tkinter import ttk, messagebox
import sys

from .components.encode_tab import EncodeTab
from .components.decode_tab import DecodeTab

class TextMapApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("TextMap")
        
        # Configure root window scaling
        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)
        
        # Set minimum window size
        self.root.minsize(900, 600)  # Reduced height since we removed output frame
        
        self.setup_ui()
        
    def setup_ui(self):
        # Main container with padding
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Title
        title = ttk.Label(main_frame, text="TextMap - Secure Information Embedding", 
                         font=('Helvetica', 16))
        title.grid(row=0, column=0, pady=10, sticky=(tk.W, tk.E))
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        # Create and add tabs
        self.encode_tab = EncodeTab(self.notebook)
        self.decode_tab = DecodeTab(self.notebook)
        
        self.notebook.add(self.encode_tab.frame, text="Encode")
        self.notebook.add(self.decode_tab.frame, text="Decode")
    
    def run(self):
        self.root.mainloop()

def main():
    try:
        app = TextMapApp()
        app.run()
    except Exception as e:
        messagebox.showerror("Error", f"Error launching GUI: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import Optional, Tuple

def browse_file(entry_var: tk.StringVar) -> Optional[str]:
    """
    Browse for a file and update the entry variable.
    
    Args:
        entry_var: StringVar to store the file path
    
    Returns:
        Selected filename or None if cancelled
    """
    try:
        filename = filedialog.askopenfilename(
            filetypes=[
                ("Text files", "*.txt"),
                ("All files", "*.*")
            ]
        )
        if filename:
            # Verify file is readable
            with open(filename, 'r', encoding='utf-8') as _:
                pass
            entry_var.set(filename)
            return filename
    except (OSError, IOError) as e:
        messagebox.showerror("Error", f"Cannot access file: {str(e)}")
    except Exception as e:
        messagebox.showerror("Error", f"Unexpected error: {str(e)}")
    return None

def save_to_file(content: str, default_extension: str = ".txt") -> bool:
    """
    Save content to a file with comprehensive error handling.
    
    Args:
        content: The text content to save
        default_extension: Default file extension to use
    
    Returns:
        True if save was successful, False otherwise
    """
    if not content:
        messagebox.showerror("Error", "No content to save")
        return False
        
    try:
        filename = filedialog.asksaveasfilename(
            defaultextension=default_extension,
            filetypes=[
                ("Text files", "*.txt"),
                ("All files", "*.*")
            ]
        )
        
        if not filename:
            return False
            
        # Create directory if it doesn't exist
        directory = os.path.dirname(filename)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
            
        # Test write permissions
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
            
        messagebox.showinfo("Success", "File saved successfully")
        return True
        
    except PermissionError:
        messagebox.showerror("Error", "Permission denied. Cannot write to specified location")
    except OSError as e:
        messagebox.showerror("Error", f"System error while saving file: {str(e)}")
    except Exception as e:
        messagebox.showerror("Error", f"Unexpected error while saving: {str(e)}")
    return False

def copy_to_clipboard(root: tk.Tk, content: str) -> bool:
    """
    Copy content to system clipboard with proper error handling.
    
    Args:
        root: Tk root instance for clipboard access
        content: Content to copy
    
    Returns:
        True if successful, False otherwise
    """
    if not content:
        return False
        
    try:
        root.clipboard_clear()
        root.clipboard_append(content)
        root.update()  # Required to finalize clipboard update
        
        # Verify clipboard content
        clipboard_content = root.clipboard_get()
        if clipboard_content == content:
            messagebox.showinfo("Success", "Content copied to clipboard")
            return True
        else:
            raise ValueError("Clipboard verification failed")
            
    except tk.TclError as e:
        messagebox.showerror("Error", "Could not access system clipboard")
        return False
    except Exception as e:
        messagebox.showerror("Error", f"Error copying to clipboard: {str(e)}")
        return False

def create_scrolled_text(parent: tk.Widget, height: int = 10, **kwargs) -> Tuple[ttk.Frame, tk.Text]:
    """
    Create a Text widget with an attached scrollbar in a frame.
    
    Args:
        parent: Parent widget
        height: Height in lines
        **kwargs: Additional arguments for the Text widget
    
    Returns:
        Tuple of (frame, text_widget)
    """
    frame = ttk.Frame(parent)
    frame.grid_rowconfigure(0, weight=1)
    frame.grid_columnconfigure(0, weight=1)
    
    # Create scrollbars
    y_scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL)
    x_scrollbar = ttk.Scrollbar(frame, orient=tk.HORIZONTAL)
    
    # Create text widget
    text_widget = tk.Text(
        frame,
        height=height,
        wrap=tk.NONE,  # Allow horizontal scrolling
        yscrollcommand=y_scrollbar.set,
        xscrollcommand=x_scrollbar.set,
        **kwargs
    )
    
    # Configure scrollbars
    y_scrollbar.config(command=text_widget.yview)
    x_scrollbar.config(command=text_widget.xview)
    
    # Layout widgets
    text_widget.grid(row=0, column=0, sticky="nsew")
    y_scrollbar.grid(row=0, column=1, sticky="ns")
    x_scrollbar.grid(row=1, column=0, sticky="ew")
    
    return frame, text_widget

def validate_text_length(text: str, min_length: int = 0, max_length: Optional[int] = None) -> bool:
    """
    Validate text length is within specified bounds.
    
    Args:
        text: Text to validate
        min_length: Minimum allowed length
        max_length: Maximum allowed length (optional)
    
    Returns:
        True if text length is valid, False otherwise
    
    Raises:
        ValueError: If min_length is negative or max_length is less than min_length
    """
    if min_length < 0:
        raise ValueError("min_length cannot be negative")
    
    if max_length is not None:
        if max_length < min_length:
            raise ValueError("max_length cannot be less than min_length")
    
    if not isinstance(text, str):
        return False
        
    text_length = len(text.strip())
    
    if text_length < min_length:
        return False
        
    if max_length is not None and text_length > max_length:
        return False
        
    return True

def show_error(message: str, title: str = "Error") -> None:
    """
    Show an error message dialog.
    
    Args:
        message: Error message to display
        title: Dialog title
    """
    messagebox.showerror(title, message)

def show_warning(message: str, title: str = "Warning") -> bool:
    """
    Show a warning message dialog with Yes/No options.
    
    Args:
        message: Warning message to display
        title: Dialog title
    
    Returns:
        True if user clicked Yes, False otherwise
    """
    return messagebox.askyesno(title, message)

def show_info(message: str, title: str = "Information") -> None:
    """
    Show an information message dialog.
    
    Args:
        message: Information message to display
        title: Dialog title
    """
    messagebox.showinfo(title, message)
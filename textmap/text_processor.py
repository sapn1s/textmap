import re
import unicodedata
from pathlib import Path
from typing import Union, Tuple

class TextProcessor:
    """Handles text processing and normalization for various file formats."""
    
    # Characters to preserve (alphanumeric + punctuation + whitespace)
    VALID_CHARS = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.,!? \n\t')
    
    @classmethod
    def normalize_text(cls, text: str) -> str:
        """
        Normalize text while preserving exact character positions:
        1. Replace invalid characters with spaces
        2. Keep all original spacing and formatting
        """
        if not text:
            return ""
        
        # Replace any characters not in VALID_CHARS with spaces
        normalized_chars = []
        for char in text:
            if char in cls.VALID_CHARS:
                normalized_chars.append(char)
            else:
                normalized_chars.append(' ')
                
        return ''.join(normalized_chars)

    @classmethod
    def format_output(cls, text: str) -> str:
        """
        Format text for display. Unlike normalize_text, this modifies spacing.
        Used only for display, never for encoding/decoding operations.
        """
        # Add formatting for display (80 chars per line, space every 5 chars)
        chars = []
        char_count = 0
        
        for char in text:
            if char.isspace():
                continue
            chars.append(char)
            char_count += 1
            if char_count % 80 == 0:
                chars.append('\n')
            elif char_count % 5 == 0:
                chars.append(' ')
        
        return ''.join(chars)

    @classmethod
    def validate_text_source(cls, text: str) -> bool:
        """Verify that text is suitable for encoding."""
        if not text:
            return False
            
        # Check text length (ignoring whitespace)
        non_whitespace = ''.join(char for char in text if not char.isspace())
        if len(non_whitespace) < 100:
            return False
            
        # Check character variety
        unique_chars = set(char for char in text if not char.isspace())
        if len(unique_chars) < 20:
            return False
            
        # Check character distribution
        char_counts = {}
        total_chars = 0
        for char in non_whitespace:
            char_counts[char] = char_counts.get(char, 0) + 1
            total_chars += 1
            
        if total_chars > 0:
            max_freq = max(char_counts.values()) / total_chars
            if max_freq > 0.3:
                return False
                
        # Check for both upper and lowercase
        has_upper = any(c.isupper() for c in text)
        has_lower = any(c.islower() for c in text)
        if not (has_upper and has_lower):
            return False
            
        return True
        
    @classmethod
    def prepare_text_for_encoding(cls, file_path: Union[str, Path]) -> str:
        """Prepare text from a file for encoding."""
        # Read the file using appropriate encoding
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
            
        normalized_text = cls.normalize_text(text)
        
        if not cls.validate_text_source(normalized_text):
            raise ValueError(
                "Text is not suitable for encoding. Ensure the source text:\n"
                "- Has at least 100 non-whitespace characters\n"
                "- Contains at least 20 unique characters\n"
                "- Has a good mix of upper and lowercase letters\n"
                "- Doesn't have any character appearing too frequently"
            )
            
        return normalized_text
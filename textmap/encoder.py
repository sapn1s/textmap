import hashlib
import secrets
import logging
from typing import Tuple, List
from .text_processor import TextProcessor

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class MnemonicEncoder:
    # Special offset value to indicate a space (255 is unlikely to occur naturally)
    SPACE_MARKER = 255
    
    def __init__(self):
        self.text_processor = TextProcessor()
    
    def _strip_whitespace(self, text: str) -> str:
        """Strip all whitespace, keeping only content characters."""
        return ''.join(c for c in text if not c.isspace())
        
    def _normalize_inputs(self, text: str, mnemonic: str = None) -> tuple[str, str]:
        """
        Normalize inputs differently for source text and mnemonic:
        - Source text: Clean and strip all whitespace
        - Mnemonic: Clean but preserve whitespace
        """
        # First clean the text (replace invalid chars with spaces)
        text = self.text_processor.normalize_text(text)
        # Then strip all whitespace from source text for position mapping
        text = self._strip_whitespace(text)
        
        if mnemonic is not None:
            # For mnemonic, normalize but preserve spaces
            mnemonic = self.text_processor.normalize_text(mnemonic)
            return text, mnemonic
        return text, None

    def _generate_mapping(self, text_length: int, mnemonic_length: int, main_key: str) -> List[int]:
        """Generate a secure mapping of positions using only the main key component."""
        if mnemonic_length > text_length:
            raise ValueError("Mnemonic length cannot be longer than text length")
            
        positions = []
        used_positions = set()
        current_seed = main_key
        
        while len(positions) < mnemonic_length:
            mapping_seed = hashlib.sha512(current_seed.encode()).digest()
            
            for i in range(0, len(mapping_seed) - 8, 8):
                if len(positions) >= mnemonic_length:
                    break
                    
                num = int.from_bytes(mapping_seed[i:i+8], 'big')
                pos = num % text_length
                
                while pos in used_positions:
                    pos = (pos + 1) % text_length
                
                positions.append(pos)
                used_positions.add(pos)
                
            current_seed = hashlib.sha256(current_seed.encode()).hexdigest()
        
        logger.debug(f"Generated positions: {positions}")
        return positions[:mnemonic_length]

    def _encode_char_offset(self, target_char: str, base_char: str = None) -> int:
        """Calculate the offset between two characters or mark as space."""
        if target_char.isspace():
            return self.SPACE_MARKER
            
        offset = (ord(target_char) - ord(base_char)) % 255  # Use 255 instead of 256 to reserve space marker
        logger.debug(f"Encoding: '{base_char}'({ord(base_char)}) + {offset} = '{target_char}'({ord(target_char)})")
        return offset

    def _decode_char_offset(self, base_char: str, offset: int) -> str:
        """Recover the original character from base character and offset."""
        if offset == self.SPACE_MARKER:
            return ' '
            
        recovered = chr((ord(base_char) + offset) % 255)
        logger.debug(f"Decoding: '{base_char}'({ord(base_char)}) + {offset} = '{recovered}'({ord(recovered)})")
        return recovered

    def _extract_key_parts(self, key: str) -> Tuple[str, int, str, List[int]]:
        """Extract components from the key string."""
        try:
            logger.debug(f"Extracting key parts from: {key[:50]}...")
            
            parts = key.split('-')
            if len(parts) < 3:
                raise ValueError("Invalid key format")
                
            version = parts[0]
            length = int(parts[1], 16)
            main_key = parts[2]
            offsets = []
            
            if len(parts) > 3:
                offsets_hex = parts[3]
                offsets = [int(offsets_hex[i:i+2], 16) for i in range(0, len(offsets_hex), 2)]
                logger.debug(f"Parsed {len(offsets)} offsets")
                
            return version, length, main_key, offsets
            
        except Exception as e:
            logger.error(f"Failed to parse key: {str(e)}")
            raise ValueError(f"Failed to parse key: {str(e)}")

    def encode(self, mnemonic: str, text: str) -> Tuple[str, str]:
        """Encode a mnemonic phrase within the provided text."""
        logger.debug("Starting encoding process")
        
        # Normalize inputs (preserves spaces in mnemonic)
        text, mnemonic = self._normalize_inputs(text, mnemonic)
        
        if not mnemonic or not text:
            raise ValueError("Mnemonic and text must not be empty")
            
        # Count non-whitespace characters in mnemonic for length check
        mnemonic_content_length = len([c for c in mnemonic if not c.isspace()])
        if len(text) < mnemonic_content_length:
            raise ValueError("Text must be at least as long as non-whitespace characters in mnemonic")
            
        if not self.text_processor.validate_text_source(text):
            logger.warning("Text might not be suitable for secure encoding")
        
        main_key = secrets.token_hex(32)
        version = "v1"
        length_hex = f"{len(mnemonic):04x}"
        
        # Count non-space characters for position mapping
        mnemonic_chars = list(mnemonic)
        content_chars = [c for c in mnemonic_chars if not c.isspace()]
        
        positions = self._generate_mapping(len(text), len(content_chars), main_key)
        
        text_chars = list(text)
        offsets = []
        
        logger.debug("Calculating character offsets:")
        pos_idx = 0
        for target_char in mnemonic_chars:
            if target_char.isspace():
                offsets.append(self.SPACE_MARKER)
            else:
                base_char = text_chars[positions[pos_idx]]
                offset = self._encode_char_offset(target_char, base_char)
                offsets.append(offset)
                pos_idx += 1
                logger.debug(f"Position {pos_idx-1}: {positions[pos_idx-1]} -> base='{base_char}' + {offset} = '{target_char}'")
        
        offsets_hex = ''.join(f"{offset:02x}" for offset in offsets)
        key = f"{version}-{length_hex}-{main_key}-{offsets_hex}"
        
        # Format output for display
        formatted_output = self.text_processor.format_output(text)
        return formatted_output, key

    def decode(self, encoded_text: str, key: str) -> str:
        """Decode a mnemonic phrase using character offsets."""
        logger.debug("Starting decoding process")
        
        # Normalize and strip whitespace for position mapping
        encoded_text, _ = self._normalize_inputs(encoded_text)
        
        if not encoded_text or not key:
            raise ValueError("Encoded text and key must not be empty")
        
        try:
            version, length, main_key, offsets = self._extract_key_parts(key)
            
            if version != "v1":
                raise ValueError("Unsupported encoding version")
            
            # Count non-space characters for position mapping
            content_count = sum(1 for x in offsets if x != self.SPACE_MARKER)
            positions = self._generate_mapping(len(encoded_text), content_count, main_key)
            
            if any(pos >= len(encoded_text) for pos in positions):
                raise ValueError("Invalid key: positions exceed text length")
            
            logger.debug("Recovering characters:")
            result = []
            pos_idx = 0
            
            for offset in offsets:
                if offset == self.SPACE_MARKER:
                    result.append(' ')
                else:
                    base_char = encoded_text[positions[pos_idx]]
                    recovered_char = self._decode_char_offset(base_char, offset)
                    logger.debug(f"Position {pos_idx}: {positions[pos_idx]} -> base='{base_char}' + {offset} = '{recovered_char}'")
                    result.append(recovered_char)
                    pos_idx += 1
            
            decoded = ''.join(result)
            logger.debug(f"Decoded result: {repr(decoded)}")
            
            return decoded
            
        except Exception as e:
            logger.error(f"Decoding failed: {str(e)}")
            raise ValueError(f"Failed to decode: {str(e)}")

    def validate_text_source(self, text: str) -> bool:
        """Validate if the provided text is suitable as a source for encoding."""
        # First normalize the text
        text, _ = self._normalize_inputs(text)
        return self.text_processor.validate_text_source(text)
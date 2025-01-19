#!/usr/bin/env python3
import argparse
import sys
from typing import Optional
from .encoder import MnemonicEncoder

def read_file_or_stdin(file_path: Optional[str] = None) -> str:
    """Read content from a file or stdin."""
    if file_path:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    return sys.stdin.read()

def write_output(content: str, output_file: Optional[str] = None) -> None:
    """Write content to a file or stdout."""
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)
    else:
        print(content)

def main() -> None:
    parser = argparse.ArgumentParser(
        description="TextMap: Securely embed and retrieve information within text."
    )
    
     # Add gui argument before subparsers
    parser.add_argument('--gui', action='store_true', help='Launch GUI interface')
    
    # Early check for GUI
    args, remaining_args = parser.parse_known_args()
    if args.gui:
        from .gui.app import main as gui_main
        gui_main()
        return
    
    subparsers = parser.add_subparsers(dest='command', required=True)

    # Encode command
    encode_parser = subparsers.add_parser('encode')
    encode_parser.add_argument('--text-file', '-t', help='Source text file (or use stdin)')
    encode_parser.add_argument('--mnemonic', '-m', help='Information to encode')
    encode_parser.add_argument('--output', '-o', help='Output file (default: stdout)')
    encode_parser.add_argument('--key-file', '-k', help='Key output file (default: stdout)')

    # Decode command
    decode_parser = subparsers.add_parser('decode')
    decode_parser.add_argument('--text-file', '-t', help='Encoded text file (or use stdin)')
    decode_parser.add_argument('--key', '-k', required=True, help='Key used for encoding')
    decode_parser.add_argument('--output', '-o', help='Output file (default: stdout)')
    
    args = parser.parse_args()
    encoder = MnemonicEncoder()

    try:
        if args.command == 'encode':
            text = read_file_or_stdin(args.text_file)
            mnemonic = args.mnemonic
            
            if not encoder.validate_text_source(text):
                print("Warning: Text might not be suitable for secure encoding.", 
                      file=sys.stderr)
            
            encoded_text, key = encoder.encode(mnemonic, text)
            write_output(encoded_text, args.output)
            
            if args.key_file:
                write_output(key, args.key_file)
            else:
                print(f"Key: {key}", file=sys.stderr)
                
        elif args.command == 'decode':
            encoded_text = read_file_or_stdin(args.text_file)
            decoded = encoder.decode(encoded_text, args.key)
            write_output(decoded, args.output)
            
    except ValueError as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
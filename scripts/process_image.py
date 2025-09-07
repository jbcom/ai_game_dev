#!/usr/bin/env python3
"""
Process a single image with automatic frame detection and transparency removal.
"""

import sys
from ai_game_dev.assets.image_processor import process_image_cli


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/process_image.py INPUT_PATH [OUTPUT_PATH]")
        sys.exit(1)
    
    input_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None
    
    process_image_cli(input_path, output_path)


if __name__ == "__main__":
    main()
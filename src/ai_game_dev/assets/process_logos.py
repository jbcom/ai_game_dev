#!/usr/bin/env python3
"""
Process homepage logos to remove excess transparency.
"""

from pathlib import Path
from ai_game_dev.assets.image_processor import ImageProcessor


def main():
    """Process both homepage logos to remove excess transparency."""
    processor = ImageProcessor()
    
    logos_dir = Path("src/ai_game_dev/server/static/assets/logos")
    
    # Process Game Workshop logo
    workshop_path = logos_dir / "game-workshop-condensed.png"
    if workshop_path.exists():
        results = processor.process_asset(
            workshop_path, workshop_path, 
            remove_transparency=True, detect_frames=False
        )
        print(f"✅ Game Workshop: {results['original_size']} -> {results.get('processed_size', 'unchanged')}")
    else:
        print("❌ Game Workshop logo not found")
    
    # Process Arcade Academy logo  
    academy_path = logos_dir / "arcade-academy-condensed.png"
    if academy_path.exists():
        results = processor.process_asset(
            academy_path, academy_path,
            remove_transparency=True, detect_frames=False
        )
        print(f"✅ Arcade Academy: {results['original_size']} -> {results.get('processed_size', 'unchanged')}")
    else:
        print("❌ Arcade Academy logo not found")


if __name__ == "__main__":
    main()
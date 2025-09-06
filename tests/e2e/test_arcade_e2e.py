"""End-to-end test for Arcade game generation with real OpenAI calls."""
import pytest
from pathlib import Path
import json

from ai_game_dev.providers import create_default_manager
from ai_game_dev.models import GameSpec, GameEngine, GameType, ComplexityLevel
from ai_game_dev.generators import GameGenerator
from ai_game_dev.assets.asset_tools import AssetManager
from ai_game_dev.graphics.cc0_libraries import CC0GraphicsLibrary
from ai_game_dev.audio.music_generator import MusicGenerator


class TestArcadeE2E:
    """End-to-end tests for Arcade game generation."""

    @pytest.mark.e2e
    def test_generate_arcade_twin_stick_shooter(self, openai_vcr, real_openai_key, e2e_output_dir):
        """Generate a complete Arcade twin-stick shooter with real assets."""
        
        game_spec = GameSpec(
            title="AI Neon Assault",
            description="An intense twin-stick shooter with neon visuals, wave-based enemies, and power-up systems",
            engine=GameEngine.ARCADE,
            game_type=GameType.ACTION,
            complexity=ComplexityLevel.ADVANCED,
            target_audience="Action game fans who enjoy fast-paced combat and high scores",
            core_mechanics=[
                "Twin-stick controls - WASD to move, mouse to aim and shoot",
                "Wave-based enemy spawning with increasing difficulty",
                "Multiple weapon types with different firing patterns",
                "Power-up system with temporary abilities",
                "Screen-wrapping movement boundaries",
                "Score multiplier system for consecutive hits"
            ],
            visual_style="High-contrast neon colors with particle effects and screen shake",
            audio_requirements=[
                "High-energy electronic music with heavy bass",
                "Weapon firing sounds with different tones per weapon",
                "Enemy destruction and power-up collection sounds",
                "Screen shake and impact audio feedback"
            ],
            technical_requirements={
                "resolution": "1280x720",
                "target_fps": 60,
                "input_methods": ["keyboard", "mouse"],
                "particle_effects": True,
                "screen_effects": True
            }
        )

        with openai_vcr.use_cassette("arcade_twin_stick.yaml"):
            provider_manager = create_default_manager()
            asset_manager = AssetManager()
            graphics_lib = CC0GraphicsLibrary()
            music_gen = MusicGenerator(provider_manager.get_provider("openai"))
            game_generator = GameGenerator(provider_manager, asset_manager)
            
            # Generate complete Arcade game
            result = game_generator.generate_complete_game(game_spec)
            
            assert result.success
            assert len(result.generated_files) > 0
            
            # Verify main game file
            main_files = [f for f in result.generated_files if "main.py" in f.filename]
            assert len(main_files) >= 1
            
            main_game = main_files[0]
            main_content = main_game.content.lower()
            
            # Check for Arcade-specific imports and structure
            assert "import arcade" in main_content
            assert "arcade.window" in main_content or "arcade.view" in main_content
            assert "class" in main_content and "arcade" in main_content
            
            # Verify twin-stick shooter mechanics
            assert any(word in main_content for word in ["mouse", "aim", "shoot", "weapon"])
            assert any(word in main_content for word in ["enemy", "spawn", "wave"])
            assert "update" in main_content and "draw" in main_content
            
            # Generate neon-themed assets
            neon_assets = graphics_lib.get_neon_themed_sprites([
                "player_ship", "enemy_basic", "enemy_fast", "enemy_heavy",
                "bullet_player", "bullet_enemy", "power_up_speed", "power_up_weapon"
            ])
            assert len(neon_assets) >= 8
            
            # Generate particle effect textures
            particle_assets = graphics_lib.get_particle_textures([
                "explosion_small", "explosion_large", "muzzle_flash", "trail_effect"
            ])
            
            # Generate high-energy music
            combat_music = music_gen.generate_electronic_track(
                title="Neon Assault Combat",
                duration=180,  # 3 minutes looping
                style="high-energy electronic with heavy bass"
            )
            
            # Save complete game
            game_dir = e2e_output_dir / "arcade_neon_assault"
            game_dir.mkdir(exist_ok=True)
            
            # Write game files
            for game_file in result.generated_files:
                file_path = game_dir / game_file.filename
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_text(game_file.content)
            
            # Write assets
            assets_dir = game_dir / "assets"
            sprites_dir = assets_dir / "sprites"
            sounds_dir = assets_dir / "sounds"
            
            for dir_path in [assets_dir, sprites_dir, sounds_dir]:
                dir_path.mkdir(exist_ok=True)
            
            # Save sprite assets
            for asset_name, asset_data in neon_assets.items():
                sprite_path = sprites_dir / f"{asset_name}.png"
                sprite_path.write_bytes(asset_data)
            
            # Save particle assets
            for particle_name, particle_data in particle_assets.items():
                particle_path = sprites_dir / f"{particle_name}.png"
                particle_path.write_bytes(particle_data)
            
            # Save music
            if combat_music:
                music_path = sounds_dir / "combat_music.wav"
                music_path.write_bytes(combat_music)
            
            # Create requirements file
            requirements_path = game_dir / "requirements.txt"
            requirements_content = """arcade>=3.0.0
numpy>=1.20.0
"""
            requirements_path.write_text(requirements_content)
            
            # Create launcher script
            launcher_path = game_dir / "run_game.py"
            launcher_content = """#!/usr/bin/env python3
\"\"\"Launcher script for AI Neon Assault.\"\"\"

import sys
import subprocess

def main():
    print("🎮 Starting AI Neon Assault...")
    print("Controls:")
    print("  - WASD: Move")
    print("  - Mouse: Aim and shoot")
    print("  - ESC: Exit")
    print()
    
    try:
        subprocess.run([sys.executable, "main.py"])
    except KeyboardInterrupt:
        print("\\nGame closed by user.")
    except Exception as e:
        print(f"Error running game: {e}")

if __name__ == "__main__":
    main()
"""
            launcher_path.write_text(launcher_content)
            
            # Create comprehensive README
            readme_path = game_dir / "README.md"
            readme_content = f"""# {game_spec.title}

{game_spec.description}

## Generated by AI Game Dev Library - Arcade Engine

This complete twin-stick shooter was generated using real AI models with Python Arcade.

## Requirements
- Python 3.11+
- Arcade 3.0.0+
- NumPy 1.20.0+

## Installation
```bash
pip install -r requirements.txt
```

## Running the Game
```bash
python run_game.py
```

Or directly:
```bash
python main.py
```

## Controls
- **WASD**: Move your ship
- **Mouse**: Aim and shoot
- **ESC**: Exit game

## Game Features
- {chr(10).join('- ' + mechanic for mechanic in game_spec.core_mechanics)}

## Assets Generated
- **Sprites**: {len(neon_assets)} neon-themed game sprites
- **Particles**: {len(particle_assets)} particle effect textures  
- **Music**: {'✅' if combat_music else '❌'} High-energy combat soundtrack
- **Sound Effects**: Weapon and explosion sounds

## Technical Details
- **Engine**: Python Arcade 3.0+
- **Resolution**: {game_spec.technical_requirements.get('resolution', 'Dynamic')}
- **Target FPS**: {game_spec.technical_requirements.get('target_fps', 60)}
- **Effects**: Particles, screen shake, neon glow

Generated with AI Game Dev Library - E2E Test Suite
"""
            readme_path.write_text(readme_content)
            
            # Verification tests
            assert (game_dir / "main.py").exists()
            assert (game_dir / "requirements.txt").exists()
            assert (game_dir / "run_game.py").exists()
            assert (sprites_dir).exists()
            assert len(list(sprites_dir.glob("*.png"))) >= len(neon_assets)
            
            # Create verification report
            report = {
                "test_name": "arcade_twin_stick_shooter_e2e",
                "game_spec": game_spec.model_dump(),
                "generation_successful": result.success,
                "files_generated": len(result.generated_files),
                "sprites_generated": len(neon_assets),
                "particles_generated": len(particle_assets),
                "music_generated": combat_music is not None,
                "output_location": str(game_dir),
                "verification": {
                    "has_main_file": (game_dir / "main.py").exists(),
                    "has_arcade_import": "import arcade" in main_content,
                    "has_game_class": "class" in main_content and "arcade" in main_content,
                    "has_twin_stick_mechanics": any(word in main_content for word in ["mouse", "aim", "shoot"]),
                    "has_enemy_system": "enemy" in main_content,
                    "has_update_loop": "update" in main_content,
                    "has_draw_method": "draw" in main_content,
                    "has_sprite_assets": len(neon_assets) >= 8,
                    "has_particle_assets": len(particle_assets) > 0,
                    "launcher_script": (game_dir / "run_game.py").exists()
                }
            }
            
            report_path = e2e_output_dir / "arcade_neon_assault_report.json"
            report_path.write_text(json.dumps(report, indent=2))
            
            print(f"\n✅ Arcade E2E Test Complete!")
            print(f"📂 Game generated at: {game_dir}")
            print(f"📊 Report saved at: {report_path}")
            print(f"🕹️ Twin-stick shooter with {len(result.generated_files)} files, {len(neon_assets)} sprites, {len(particle_assets)} particles")


    @pytest.mark.e2e
    def test_generate_arcade_educational(self, openai_vcr, real_openai_key, e2e_output_dir):
        """Generate a complete Arcade educational game with real assets."""
        
        game_spec = GameSpec(
            title="AI Math Galaxy",
            description="An educational space-themed game that teaches math concepts through interactive gameplay",
            engine=GameEngine.ARCADE, 
            game_type=GameType.EDUCATIONAL,
            complexity=ComplexityLevel.BEGINNER,
            target_audience="Elementary school students learning basic math",
            core_mechanics=[
                "Math problems presented as space missions",
                "Multiple choice answers to solve puzzles",
                "Progress tracking and rewards system",
                "Adaptive difficulty based on performance",
                "Colorful space exploration theme"
            ],
            visual_style="Bright, child-friendly cartoon space theme"
        )

        with openai_vcr.use_cassette("arcade_educational.yaml"):
            provider_manager = create_default_manager()
            game_generator = GameGenerator(provider_manager, AssetManager())
            
            result = game_generator.generate_complete_game(game_spec)
            
            # Save educational game
            game_dir = e2e_output_dir / "arcade_math_galaxy"
            game_dir.mkdir(exist_ok=True)
            
            for game_file in result.generated_files:
                file_path = game_dir / game_file.filename
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_text(game_file.content)
            
            assert result.success
            assert (game_dir / "main.py").exists()
            
            # Verify educational elements
            main_content = (game_dir / "main.py").read_text().lower()
            assert "math" in main_content or "question" in main_content or "answer" in main_content
            assert "score" in main_content or "progress" in main_content
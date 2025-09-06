"""End-to-end test for Pygame game generation with real OpenAI calls."""
import pytest
from pathlib import Path
import json
import zipfile

from ai_game_dev.providers import create_default_manager
from ai_game_dev.models import GameSpec, GameEngine, GameType, ComplexityLevel
from ai_game_dev.generators import GameGenerator
from ai_game_dev.assets.asset_tools import AssetManager
from ai_game_dev.graphics.cc0_libraries import CC0GraphicsLibrary
from ai_game_dev.audio.music_generator import MusicGenerator


class TestPygameE2E:
    """End-to-end tests for Pygame game generation."""

    @pytest.mark.e2e
    def test_generate_pygame_space_shooter(self, openai_vcr, real_openai_key, e2e_output_dir):
        """Generate a complete Pygame space shooter with real assets."""
        
        # Create game specification
        game_spec = GameSpec(
            title="AI Space Defender",
            description="A classic space shooter where you defend Earth from alien invaders",
            engine=GameEngine.PYGAME,
            game_type=GameType.ACTION,
            complexity=ComplexityLevel.INTERMEDIATE,
            target_audience="Casual gamers who enjoy retro arcade games",
            core_mechanics=[
                "Player ship movement with WASD or arrow keys",
                "Shooting projectiles with spacebar", 
                "Enemy waves spawn from top of screen",
                "Collision detection for hits and damage",
                "Score system with increasing difficulty"
            ],
            visual_style="Retro 16-bit pixel art with bright neon colors",
            audio_requirements=[
                "Background music - electronic/synthwave style",
                "Sound effects for shooting, explosions, enemy destruction"
            ],
            technical_requirements={
                "resolution": "800x600",
                "target_fps": 60,
                "input_methods": ["keyboard"],
                "save_system": False
            }
        )

        # Use VCR to record/replay OpenAI calls
        with openai_vcr.use_cassette("pygame_space_shooter.yaml"):
            # Initialize providers with real API key
            provider_manager = create_default_manager()
            
            # Create asset manager and generators
            asset_manager = AssetManager()
            graphics_lib = CC0GraphicsLibrary()
            music_gen = MusicGenerator(provider_manager.get_provider("openai"))
            game_generator = GameGenerator(provider_manager, asset_manager)
            
            # Generate the complete game
            result = game_generator.generate_complete_game(game_spec)
            
            # Verify core game files were generated
            assert result.success
            assert len(result.generated_files) > 0
            
            # Check for main game file
            main_files = [f for f in result.generated_files if "main.py" in f.filename]
            assert len(main_files) >= 1
            
            # Verify game logic structure
            main_game = main_files[0]
            assert "pygame" in main_game.content.lower()
            assert "player" in main_game.content.lower()
            assert "bullet" in main_game.content.lower() or "projectile" in main_game.content.lower()
            assert "enemy" in main_game.content.lower()
            
            # Generate and verify assets
            sprite_assets = graphics_lib.get_space_themed_sprites(["player_ship", "enemy_ship", "bullet"])
            assert len(sprite_assets) >= 3
            
            # Generate background music
            background_music = music_gen.generate_synthwave_track(
                title="Space Defender Theme",
                duration=120,  # 2 minutes
                style="energetic synthwave"
            )
            assert background_music is not None
            
            # Save complete game to output directory
            game_dir = e2e_output_dir / "pygame_space_shooter"
            game_dir.mkdir(exist_ok=True)
            
            # Write game files
            for game_file in result.generated_files:
                file_path = game_dir / game_file.filename
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_text(game_file.content)
            
            # Write assets
            assets_dir = game_dir / "assets"
            assets_dir.mkdir(exist_ok=True)
            
            for asset_name, asset_data in sprite_assets.items():
                asset_path = assets_dir / f"{asset_name}.png"
                asset_path.write_bytes(asset_data)
            
            # Write music
            if background_music:
                music_path = assets_dir / "background_music.wav"
                music_path.write_bytes(background_music)
            
            # Create a requirements.txt
            requirements_path = game_dir / "requirements.txt"
            requirements_path.write_text("pygame>=2.5.0\n")
            
            # Create README with instructions
            readme_path = game_dir / "README.md"
            readme_content = f"""# {game_spec.title}

{game_spec.description}

## Generated by AI Game Dev Library

This complete game was generated using real AI models and assets.

## Requirements
- Python 3.11+
- pygame 2.5.0+

## Installation
```bash
pip install -r requirements.txt
```

## Running the Game
```bash
python main.py
```

## Controls
- WASD or Arrow Keys: Move ship
- Spacebar: Shoot
- ESC: Exit game

## Features
- {chr(10).join('- ' + mechanic for mechanic in game_spec.core_mechanics)}

Generated with AI Game Dev Library - E2E Test Suite
"""
            readme_path.write_text(readme_content)
            
            # Verify the complete game package
            assert (game_dir / "main.py").exists()
            assert (game_dir / "requirements.txt").exists() 
            assert (game_dir / "README.md").exists()
            assert (assets_dir).exists()
            
            # Create verification report
            report = {
                "test_name": "pygame_space_shooter_e2e",
                "game_spec": game_spec.model_dump(),
                "generation_successful": result.success,
                "files_generated": len(result.generated_files),
                "assets_generated": len(sprite_assets),
                "music_generated": background_music is not None,
                "output_location": str(game_dir),
                "verification": {
                    "has_main_file": (game_dir / "main.py").exists(),
                    "has_pygame_import": "pygame" in main_game.content.lower(),
                    "has_game_loop": "while" in main_game.content and ("running" in main_game.content or "game_loop" in main_game.content),
                    "has_player_logic": "player" in main_game.content.lower(),
                    "has_enemy_logic": "enemy" in main_game.content.lower(),
                    "has_collision_detection": "collide" in main_game.content.lower() or "collision" in main_game.content.lower()
                }
            }
            
            report_path = e2e_output_dir / "pygame_space_shooter_report.json"
            report_path.write_text(json.dumps(report, indent=2))
            
            print(f"\n✅ Pygame E2E Test Complete!")
            print(f"📂 Game generated at: {game_dir}")
            print(f"📊 Report saved at: {report_path}")
            print(f"🎮 Files: {len(result.generated_files)} | Assets: {len(sprite_assets)} | Music: {'✅' if background_music else '❌'}")


    @pytest.mark.e2e 
    def test_generate_pygame_platformer(self, openai_vcr, real_openai_key, e2e_output_dir):
        """Generate a complete Pygame platformer with real assets."""
        
        game_spec = GameSpec(
            title="AI Pixel Adventure",
            description="A charming 2D platformer with collectibles and obstacles",
            engine=GameEngine.PYGAME,
            game_type=GameType.PLATFORMER,
            complexity=ComplexityLevel.BEGINNER,
            target_audience="Family-friendly for all ages",
            core_mechanics=[
                "Character movement with arrow keys or WASD",
                "Jumping with spacebar",
                "Collecting coins or gems for points",
                "Avoiding enemies and obstacles",
                "Level progression system"
            ],
            visual_style="Colorful cartoon pixel art",
            audio_requirements=[
                "Upbeat background music",
                "Jump sound effects",
                "Coin collection sounds"
            ]
        )

        with openai_vcr.use_cassette("pygame_platformer.yaml"):
            provider_manager = create_default_manager()
            asset_manager = AssetManager()
            game_generator = GameGenerator(provider_manager, asset_manager)
            
            result = game_generator.generate_complete_game(game_spec)
            
            # Save and verify platformer
            game_dir = e2e_output_dir / "pygame_platformer"
            game_dir.mkdir(exist_ok=True)
            
            for game_file in result.generated_files:
                file_path = game_dir / game_file.filename
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_text(game_file.content)
            
            assert result.success
            assert (game_dir / "main.py").exists()
            
            # Verify platformer-specific elements
            main_content = (game_dir / "main.py").read_text().lower()
            assert "jump" in main_content or "gravity" in main_content
            assert "platform" in main_content or "ground" in main_content
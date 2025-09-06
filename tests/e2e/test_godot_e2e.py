"""End-to-end test for Godot game generation with real OpenAI calls."""
import pytest
from pathlib import Path
import json

from ai_game_dev.providers import create_default_manager
from ai_game_dev.models import GameSpec, GameEngine, GameType, ComplexityLevel
from ai_game_dev.generators import GameGenerator
from ai_game_dev.assets.asset_tools import AssetManager
from ai_game_dev.engines.godot.workflow import GodotProjectGenerator


class TestGodotE2E:
    """End-to-end tests for Godot game generation."""

    @pytest.mark.e2e
    def test_generate_godot_rpg(self, openai_vcr, real_openai_key, e2e_output_dir):
        """Generate a complete Godot RPG with real assets."""
        
        game_spec = GameSpec(
            title="AI Fantasy Quest",
            description="A classic 2D RPG with turn-based combat, character progression, and an epic storyline",
            engine=GameEngine.GODOT,
            game_type=GameType.RPG,
            complexity=ComplexityLevel.ADVANCED,
            target_audience="RPG enthusiasts who enjoy character development and storytelling",
            core_mechanics=[
                "Turn-based combat system with strategic depth",
                "Character leveling and skill trees",
                "Inventory management with equipment upgrades",
                "Quest system with branching storylines",
                "Town exploration and NPC interactions",
                "World map with multiple locations"
            ],
            visual_style="16-bit inspired pixel art with detailed character sprites and environments",
            audio_requirements=[
                "Orchestral fantasy soundtrack with multiple themes",
                "Combat sound effects and spell casting sounds",
                "Ambient sounds for different environments"
            ],
            technical_requirements={
                "resolution": "1920x1080",
                "target_fps": 60,
                "input_methods": ["keyboard", "gamepad"],
                "save_system": True,
                "platform": "desktop"
            }
        )

        with openai_vcr.use_cassette("godot_rpg.yaml"):
            provider_manager = create_default_manager()
            asset_manager = AssetManager()
            godot_generator = GodotProjectGenerator(provider_manager)
            
            # Generate complete Godot project
            result = godot_generator.generate_complete_project(game_spec)
            
            assert result.success
            assert len(result.generated_files) > 0
            
            # Verify essential Godot files
            project_godot = next((f for f in result.generated_files if f.filename == "project.godot"), None)
            main_scene = next((f for f in result.generated_files if "Main.tscn" in f.filename), None)
            player_script = next((f for f in result.generated_files if "Player.gd" in f.filename), None)
            
            assert project_godot is not None
            assert main_scene is not None
            assert player_script is not None
            
            # Check project.godot configuration
            project_content = project_godot.content
            assert "[application]" in project_content
            assert "config/name" in project_content
            assert game_spec.title in project_content
            
            # Check GDScript structure
            script_content = player_script.content
            assert "extends" in script_content
            assert "func _ready()" in script_content or "func _init()" in script_content
            assert "func _process(" in script_content or "func _physics_process(" in script_content
            
            # Generate RPG-specific assets
            character_sprites = asset_manager.generate_character_set(
                ["hero", "wizard", "warrior", "rogue", "dragon", "goblin"]
            )
            ui_elements = asset_manager.generate_ui_pack(
                ["health_bar", "mana_bar", "inventory_panel", "dialog_box"]
            )
            
            # Save complete project
            game_dir = e2e_output_dir / "godot_fantasy_quest"
            game_dir.mkdir(exist_ok=True)
            
            # Write all generated files
            for game_file in result.generated_files:
                file_path = game_dir / game_file.filename
                file_path.parent.mkdir(parents=True, exist_ok=True)
                if file_path.suffix == ".tscn":
                    # Handle Godot scene files
                    file_path.write_text(game_file.content)
                elif file_path.suffix == ".gd":
                    # Handle GDScript files
                    file_path.write_text(game_file.content)
                else:
                    file_path.write_text(game_file.content)
            
            # Write game assets
            assets_dir = game_dir / "assets"
            assets_dir.mkdir(exist_ok=True)
            
            # Save character sprites
            sprites_dir = assets_dir / "sprites"
            sprites_dir.mkdir(exist_ok=True)
            for char_name, sprite_data in character_sprites.items():
                sprite_path = sprites_dir / f"{char_name}.png"
                sprite_path.write_bytes(sprite_data)
            
            # Save UI elements
            ui_dir = assets_dir / "ui"
            ui_dir.mkdir(exist_ok=True)
            for ui_name, ui_data in ui_elements.items():
                ui_path = ui_dir / f"{ui_name}.png"
                ui_path.write_bytes(ui_data)
            
            # Create Godot-specific documentation
            godot_readme = game_dir / "GODOT_README.md"
            godot_content = f"""# {game_spec.title} - Godot Project

## Opening in Godot
1. Open Godot Engine 4.x
2. Click "Import" 
3. Navigate to this folder and select `project.godot`
4. Click "Import & Edit"

## Project Structure
- `scenes/` - Game scenes (.tscn files)
- `scripts/` - GDScript files (.gd files)
- `assets/` - Game assets (sprites, sounds, etc.)

## Generated Components
- Character system with RPG mechanics
- Turn-based combat system
- Inventory and equipment system
- Dialog and quest system
- Save/load functionality

## Controls
- Arrow Keys/WASD: Move character
- Enter/Space: Interact/Confirm
- ESC: Menu/Cancel

Generated by AI Game Dev Library
"""
            godot_readme.write_text(godot_content)
            
            # Verification tests
            assert (game_dir / "project.godot").exists()
            assert (sprites_dir).exists()
            assert len(character_sprites) >= 6
            
            # Create verification report
            report = {
                "test_name": "godot_rpg_e2e", 
                "game_spec": game_spec.model_dump(),
                "generation_successful": result.success,
                "files_generated": len(result.generated_files),
                "character_sprites": len(character_sprites),
                "ui_elements": len(ui_elements),
                "output_location": str(game_dir),
                "verification": {
                    "has_project_file": (game_dir / "project.godot").exists(),
                    "has_main_scene": main_scene is not None,
                    "has_player_script": player_script is not None,
                    "has_gdscript_structure": "extends" in script_content,
                    "has_character_assets": len(character_sprites) > 0,
                    "has_ui_assets": len(ui_elements) > 0,
                    "project_importable": "[application]" in project_content
                }
            }
            
            report_path = e2e_output_dir / "godot_fantasy_quest_report.json"
            report_path.write_text(json.dumps(report, indent=2))
            
            print(f"\n✅ Godot E2E Test Complete!")
            print(f"📂 Game generated at: {game_dir}")
            print(f"📊 Report saved at: {report_path}")
            print(f"🎮 Godot project with {len(result.generated_files)} files and {len(character_sprites)} character sprites")


    @pytest.mark.e2e
    def test_generate_godot_puzzle(self, openai_vcr, real_openai_key, e2e_output_dir):
        """Generate a complete Godot puzzle game with real assets."""
        
        game_spec = GameSpec(
            title="AI Mind Maze",
            description="A challenging puzzle game with increasingly complex brain teasers and spatial reasoning challenges", 
            engine=GameEngine.GODOT,
            game_type=GameType.PUZZLE,
            complexity=ComplexityLevel.INTERMEDIATE,
            core_mechanics=[
                "Grid-based puzzle solving",
                "Block pushing and manipulation",
                "Switch and door mechanisms", 
                "Progressive difficulty levels",
                "Undo/redo system for moves"
            ],
            visual_style="Clean minimalist design with bright, contrasting colors"
        )

        with openai_vcr.use_cassette("godot_puzzle.yaml"):
            provider_manager = create_default_manager()
            godot_generator = GodotProjectGenerator(provider_manager)
            
            result = godot_generator.generate_complete_project(game_spec)
            
            # Save puzzle game
            game_dir = e2e_output_dir / "godot_mind_maze"
            game_dir.mkdir(exist_ok=True)
            
            for game_file in result.generated_files:
                file_path = game_dir / game_file.filename
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_text(game_file.content)
            
            assert result.success
            assert (game_dir / "project.godot").exists()
            
            # Verify puzzle-specific elements
            puzzle_scripts = [f for f in result.generated_files if f.filename.endswith(".gd")]
            assert len(puzzle_scripts) > 0
            
            # Check for puzzle logic in scripts
            script_content = " ".join([f.content for f in puzzle_scripts])
            assert any(word in script_content.lower() for word in ["puzzle", "grid", "block", "move", "solve"])
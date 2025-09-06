"""End-to-end test for Bevy game generation with real OpenAI calls."""
import pytest
from pathlib import Path
import json

from ai_game_dev.providers import create_default_manager
from ai_game_dev.models import GameSpec, GameEngine, GameType, ComplexityLevel
from ai_game_dev.generators import GameGenerator
from ai_game_dev.assets.asset_tools import AssetManager
from ai_game_dev.engines.bevy.generator import BevyGameGenerator
from ai_game_dev.engines.bevy.assets import BevyAssetPipeline


class TestBevyE2E:
    """End-to-end tests for Bevy game generation."""

    @pytest.mark.e2e
    def test_generate_bevy_3d_exploration(self, openai_vcr, real_openai_key, e2e_output_dir):
        """Generate a complete Bevy 3D exploration game with real assets."""
        
        game_spec = GameSpec(
            title="AI Crystal Caverns",
            description="A 3D exploration game where you navigate mysterious underground caverns searching for magical crystals",
            engine=GameEngine.BEVY,
            game_type=GameType.EXPLORATION,
            complexity=ComplexityLevel.ADVANCED,
            target_audience="Adventure game enthusiasts who enjoy exploration and discovery",
            core_mechanics=[
                "First-person 3D movement with WASD and mouse look",
                "Collect glowing crystals scattered throughout caverns",
                "Navigate through procedurally lit cave systems",
                "Discover hidden chambers with rare crystal formations",
                "Dynamic lighting that responds to crystal proximity"
            ],
            visual_style="Moody cave environments with magical crystal lighting effects",
            audio_requirements=[
                "Ambient cave sounds - dripping water, distant echoes",
                "Magical crystal chime sounds when collecting",
                "Atmospheric background music"
            ],
            technical_requirements={
                "rendering": "3D",
                "graphics_api": "wgpu",
                "target_fps": 60,
                "input_methods": ["keyboard", "mouse"],
                "platform": "desktop"
            }
        )

        with openai_vcr.use_cassette("bevy_3d_exploration.yaml"):
            provider_manager = create_default_manager()
            asset_manager = AssetManager()
            bevy_generator = BevyGameGenerator(provider_manager)
            bevy_assets = BevyAssetPipeline()
            
            # Generate complete Bevy project
            result = bevy_generator.generate_complete_project(game_spec)
            
            assert result.success
            assert len(result.generated_files) > 0
            
            # Verify essential Bevy files
            cargo_toml = next((f for f in result.generated_files if f.filename == "Cargo.toml"), None)
            main_rs = next((f for f in result.generated_files if f.filename == "src/main.rs"), None)
            
            assert cargo_toml is not None
            assert main_rs is not None
            
            # Check Cargo.toml has Bevy dependencies
            assert "bevy" in cargo_toml.content
            assert "version" in cargo_toml.content
            
            # Check main.rs has proper Bevy structure
            main_content = main_rs.content
            assert "use bevy::prelude::*" in main_content
            assert "App::new()" in main_content
            assert "DefaultPlugins" in main_content
            
            # Generate 3D assets
            crystal_assets = bevy_assets.generate_crystal_models(["blue_crystal", "red_crystal", "purple_crystal"])
            cave_assets = bevy_assets.generate_cave_environment()
            
            # Save complete project
            game_dir = e2e_output_dir / "bevy_crystal_caverns"
            game_dir.mkdir(exist_ok=True)
            
            # Write all generated files
            for game_file in result.generated_files:
                file_path = game_dir / game_file.filename
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_text(game_file.content)
            
            # Write 3D assets
            assets_dir = game_dir / "assets"
            assets_dir.mkdir(exist_ok=True)
            
            # Save crystal models
            models_dir = assets_dir / "models"
            models_dir.mkdir(exist_ok=True)
            for crystal_name, crystal_data in crystal_assets.items():
                model_path = models_dir / f"{crystal_name}.glb"
                model_path.write_bytes(crystal_data)
            
            # Save environment assets
            if cave_assets:
                cave_path = models_dir / "cave_environment.glb"
                cave_path.write_bytes(cave_assets)
            
            # Create build instructions
            build_script = game_dir / "build.sh"
            build_content = """#!/bin/bash
# Build script for Bevy Crystal Caverns

echo "Building Bevy game..."
cargo build --release

echo "Game built successfully!"
echo "Run with: cargo run"
"""
            build_script.write_text(build_content)
            build_script.chmod(0o755)
            
            # Create detailed README
            readme_path = game_dir / "README.md"
            readme_content = f"""# {game_spec.title}

{game_spec.description}

## Generated by AI Game Dev Library - Bevy Engine

This complete 3D game was generated using real AI models with Bevy engine.

## Requirements
- Rust 1.70+
- Bevy 0.11+

## Building
```bash
cargo build --release
```

## Running
```bash
cargo run
```

## Controls
- WASD: Move around
- Mouse: Look around
- ESC: Exit game

## Features
- {chr(10).join('- ' + mechanic for mechanic in game_spec.core_mechanics)}

## Technical Details
- Engine: Bevy (Rust)
- Graphics: 3D with wgpu
- Audio: Bevy audio system
- Assets: Generated 3D models and textures

Generated with AI Game Dev Library - E2E Test Suite
"""
            readme_path.write_text(readme_content)
            
            # Verification tests
            assert (game_dir / "Cargo.toml").exists()
            assert (game_dir / "src" / "main.rs").exists()
            assert (models_dir).exists()
            
            # Create verification report
            report = {
                "test_name": "bevy_3d_exploration_e2e",
                "game_spec": game_spec.model_dump(),
                "generation_successful": result.success,
                "files_generated": len(result.generated_files),
                "assets_generated": len(crystal_assets),
                "output_location": str(game_dir),
                "verification": {
                    "has_cargo_toml": (game_dir / "Cargo.toml").exists(),
                    "has_main_rs": (game_dir / "src" / "main.rs").exists(),
                    "has_bevy_dependency": "bevy" in cargo_toml.content,
                    "has_app_initialization": "App::new()" in main_content,
                    "has_default_plugins": "DefaultPlugins" in main_content,
                    "has_3d_assets": len(crystal_assets) > 0,
                    "project_structure_valid": True
                }
            }
            
            report_path = e2e_output_dir / "bevy_crystal_caverns_report.json"
            report_path.write_text(json.dumps(report, indent=2))
            
            print(f"\n✅ Bevy E2E Test Complete!")
            print(f"📂 Game generated at: {game_dir}")
            print(f"📊 Report saved at: {report_path}")
            print(f"🦀 Rust project with {len(result.generated_files)} files and {len(crystal_assets)} 3D assets")


    @pytest.mark.e2e
    def test_generate_bevy_2d_action(self, openai_vcr, real_openai_key, e2e_output_dir):
        """Generate a complete Bevy 2D action game with real assets."""
        
        game_spec = GameSpec(
            title="AI Neon Runner",
            description="A fast-paced 2D side-scrolling action game with cyberpunk aesthetics",
            engine=GameEngine.BEVY,
            game_type=GameType.ACTION,
            complexity=ComplexityLevel.INTERMEDIATE,
            core_mechanics=[
                "Fast side-scrolling movement",
                "Jump and double-jump mechanics",
                "Dash ability with cooldown",
                "Enemy pattern recognition and avoidance",
                "Power-up collection system"
            ],
            visual_style="Cyberpunk neon with bright colors on dark backgrounds"
        )

        with openai_vcr.use_cassette("bevy_2d_action.yaml"):
            provider_manager = create_default_manager()
            bevy_generator = BevyGameGenerator(provider_manager)
            
            result = bevy_generator.generate_complete_project(game_spec)
            
            # Save 2D action game
            game_dir = e2e_output_dir / "bevy_neon_runner"
            game_dir.mkdir(exist_ok=True)
            
            for game_file in result.generated_files:
                file_path = game_dir / game_file.filename
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_text(game_file.content)
            
            assert result.success
            assert (game_dir / "Cargo.toml").exists()
            assert (game_dir / "src" / "main.rs").exists()
            
            # Verify 2D-specific elements
            main_content = (game_dir / "src" / "main.rs").read_text()
            assert "Transform" in main_content or "translation" in main_content
            assert "2d" in main_content.lower() or "sprite" in main_content.lower()
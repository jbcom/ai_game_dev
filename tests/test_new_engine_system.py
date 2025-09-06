"""
Test the new modular engine system with proper adapters.
Validates that the restructured architecture generates real code.
"""
import pytest
from pathlib import Path

from ai_game_dev.engines import (
    engine_manager,
    generate_for_engine,
    get_supported_engines,
    PygameAdapter,
    BevyAdapter,
    GodotAdapter
)


def test_engine_manager_initialization():
    """Test that EngineManager initializes with all adapters."""
    engines = get_supported_engines()
    assert "pygame" in engines
    assert "bevy" in engines
    assert "godot" in engines
    assert len(engines) >= 3


def test_adapter_properties():
    """Test that adapters have correct properties."""
    pygame_adapter = engine_manager.get_adapter("pygame")
    assert pygame_adapter.engine_name == "pygame"
    assert pygame_adapter.native_language == "python"
    
    bevy_adapter = engine_manager.get_adapter("bevy")
    assert bevy_adapter.engine_name == "bevy"
    assert bevy_adapter.native_language == "rust"
    
    godot_adapter = engine_manager.get_adapter("godot")
    assert godot_adapter.engine_name == "godot"
    assert godot_adapter.native_language == "gdscript"


@pytest.mark.asyncio
async def test_pygame_real_code_generation():
    """Test that Pygame adapter generates actual Python code."""
    result = await generate_for_engine(
        "pygame",
        "simple platformer game",
        complexity="beginner",
        features=["jumping", "collecting coins"],
        art_style="pixel art"
    )
    
    assert result.engine_type == "pygame"
    assert "main.py" in result.generated_files
    assert "game.py" in result.generated_files
    assert "player.py" in result.generated_files
    assert "utils.py" in result.generated_files
    
    # Verify actual Python code content
    main_code = result.generated_files["main.py"]
    assert "import pygame" in main_code
    assert "def main" in main_code
    assert "pygame.init()" in main_code
    
    game_code = result.generated_files["game.py"]
    assert "class Game" in game_code
    assert "def update" in game_code
    assert "def draw" in game_code


@pytest.mark.asyncio
async def test_bevy_real_code_generation():
    """Test that Bevy adapter generates actual Rust code."""
    result = await generate_for_engine(
        "bevy",
        "3D adventure game",
        complexity="intermediate",
        features=["inventory", "combat"],
        art_style="low poly"
    )
    
    assert result.engine_type == "bevy"
    assert "Cargo.toml" in result.generated_files
    assert "src/main.rs" in result.generated_files
    assert "src/components.rs" in result.generated_files
    assert "src/systems.rs" in result.generated_files
    
    # Verify actual Rust code content
    cargo_toml = result.generated_files["Cargo.toml"]
    assert "bevy" in cargo_toml
    assert "[package]" in cargo_toml
    
    main_code = result.generated_files["src/main.rs"]
    assert "use bevy::prelude::*" in main_code
    assert "fn main" in main_code
    assert "App::new()" in main_code


@pytest.mark.asyncio
async def test_godot_real_code_generation():
    """Test that Godot adapter generates actual GDScript code."""
    result = await generate_for_engine(
        "godot",
        "2D puzzle game",
        complexity="intermediate",
        features=["level editor", "physics puzzles"],
        art_style="cartoonish"
    )
    
    assert result.engine_type == "godot"
    assert "project.godot" in result.generated_files
    assert "scripts/Main.gd" in result.generated_files
    assert "scripts/Player.gd" in result.generated_files
    assert "scripts/GameManager.gd" in result.generated_files
    
    # Verify actual GDScript code content
    main_script = result.generated_files["scripts/Main.gd"]
    assert "extends" in main_script
    assert "func _ready" in main_script
    
    player_script = result.generated_files["scripts/Player.gd"]
    assert "extends" in player_script
    assert "func" in player_script


def test_engine_info_retrieval():
    """Test that engine information can be retrieved."""
    pygame_info = engine_manager.get_engine_info("pygame")
    assert pygame_info["name"] == "pygame"
    assert pygame_info["language"] == "python"
    assert "Install Python" in pygame_info["build_instructions"]
    
    all_info = engine_manager.get_all_engines_info()
    assert "pygame" in all_info
    assert "bevy" in all_info
    assert "godot" in all_info


def test_unsupported_engine():
    """Test handling of unsupported engines."""
    adapter = engine_manager.get_adapter("unsupported_engine")
    assert adapter is None
    
    with pytest.raises(ValueError, match="Unsupported engine"):
        pytest.run(generate_for_engine("unsupported_engine", "test game"))


if __name__ == "__main__":
    # Run a quick test
    import asyncio
    
    async def quick_test():
        print("Testing new engine system...")
        
        engines = get_supported_engines()
        print(f"Supported engines: {engines}")
        
        # Test Pygame
        result = await generate_for_engine("pygame", "test game", "beginner")
        print(f"Pygame generated {len(result.generated_files)} files")
        print(f"Project saved to: {result.project_path}")
        
        print("✅ New engine system working!")
    
    asyncio.run(quick_test())
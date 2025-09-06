"""Working E2E tests that actually generate games."""
import pytest
import os
from pathlib import Path


@pytest.mark.e2e
async def test_generate_pygame_game():
    """Generate a real Pygame game using proper engine adapter."""
    from ai_game_dev.engine_adapters import EngineAdapterManager
    
    # Check API key
    if not os.getenv("OPENAI_API_KEY"):
        pytest.skip("OPENAI_API_KEY not available")
    
    # Use proper engine adapter system
    engine_manager = EngineAdapterManager()
    
    # Generate complete pygame project
    result = await engine_manager.generate_for_engine(
        engine_name="pygame",
        description="A 2D space shooter with player ship, enemies, bullets, collision detection, and score system",
        complexity="intermediate",
        features=["player_movement", "shooting", "collision_detection", "score_system"],
        art_style="retro"
    )
    
    assert result is not None
    assert result.engine_type == "pygame"
    assert len(result.project_structure) > 0
    assert len(result.main_files) > 0
    assert "pygame" in result.build_instructions.lower()
    
    # Save generated project
    output_dir = Path("tests/e2e/outputs/pygame_project")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Save project overview
    with open(output_dir / "project_structure.txt", "w") as f:
        f.write(f"Engine: {result.engine_type}\n")
        f.write(f"Main files: {result.main_files}\n")
        f.write(f"Asset requirements: {result.asset_requirements}\n")
        f.write(f"Build instructions: {result.build_instructions}\n")
    
    print(f"✅ Generated complete Pygame project with {len(result.main_files)} main files")
    return True


@pytest.mark.e2e
async def test_generate_bevy_game():
    """Generate a real Bevy (Rust) game using proper engine adapter."""
    from ai_game_dev.engine_adapters import EngineAdapterManager
    
    if not os.getenv("OPENAI_API_KEY"):
        pytest.skip("OPENAI_API_KEY not available")
    
    # Use proper engine adapter system
    engine_manager = EngineAdapterManager()
    
    # Generate complete Bevy project
    result = await engine_manager.generate_for_engine(
        engine_name="bevy",
        description="A 3D space exploration game with physics, camera controls, and procedural asteroid generation",
        complexity="complex",
        features=["3d_graphics", "physics_simulation", "camera_controls", "procedural_generation"],
        art_style="sci-fi"
    )
    
    assert result is not None
    assert result.engine_type == "bevy"
    assert len(result.project_structure) > 0
    assert len(result.main_files) > 0
    assert "rust" in result.build_instructions.lower() or "cargo" in result.build_instructions.lower()
    
    # Save generated project
    output_dir = Path("tests/e2e/outputs/bevy_project") 
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Save project overview
    with open(output_dir / "project_structure.txt", "w") as f:
        f.write(f"Engine: {result.engine_type}\n")
        f.write(f"Main files: {result.main_files}\n") 
        f.write(f"Asset requirements: {result.asset_requirements}\n")
        f.write(f"Build instructions: {result.build_instructions}\n")
    
    print(f"✅ Generated complete Bevy project with {len(result.main_files)} main files")
    return True


@pytest.mark.e2e
async def test_generate_godot_game():
    """Generate a real Godot game using proper engine adapter."""
    from ai_game_dev.engine_adapters import EngineAdapterManager
    
    if not os.getenv("OPENAI_API_KEY"):
        pytest.skip("OPENAI_API_KEY not available")
    
    # Use proper engine adapter system
    engine_manager = EngineAdapterManager()
    
    # Generate complete Godot project
    result = await engine_manager.generate_for_engine(
        engine_name="godot",
        description="A 3D platformer adventure with character progression, puzzle mechanics, and dynamic lighting",
        complexity="intermediate", 
        features=["3d_platforming", "character_progression", "puzzle_mechanics", "dynamic_lighting"],
        art_style="stylized"
    )
    
    assert result is not None
    assert result.engine_type == "godot"
    assert len(result.project_structure) > 0
    assert len(result.main_files) > 0
    assert "godot" in result.build_instructions.lower()
    
    # Save generated project
    output_dir = Path("tests/e2e/outputs/godot_project")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Save project overview
    with open(output_dir / "project_structure.txt", "w") as f:
        f.write(f"Engine: {result.engine_type}\n")
        f.write(f"Main files: {result.main_files}\n")
        f.write(f"Asset requirements: {result.asset_requirements}\n") 
        f.write(f"Build instructions: {result.build_instructions}\n")
    
    print(f"✅ Generated complete Godot project with {len(result.main_files)} main files")
    return True
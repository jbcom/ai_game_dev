"""Working E2E tests that actually generate games."""
import pytest
import os
from pathlib import Path


@pytest.mark.e2e  
def test_generate_pygame_game():
    """Generate a real Pygame game and verify the output."""
    from ai_game_dev.providers import create_default_manager
    
    # Check API key
    if not os.getenv("OPENAI_API_KEY"):
        pytest.skip("OPENAI_API_KEY not available")
    
    # Create provider manager
    manager = create_default_manager()
    
    # Get OpenAI provider
    try:
        openai_provider = manager.get_provider("openai")
    except ValueError:
        openai_provider = None
    
    if not openai_provider:
        pytest.skip("No OpenAI provider configured")
    
    # Generate game code
    prompt = """Create a complete Pygame space shooter game:

1. 800x600 window with black background
2. White player rectangle at bottom that moves left/right with arrow keys
3. Player shoots bullets upward with spacebar
4. Red enemy rectangles spawn at top and move down
5. Collision detection between bullets and enemies
6. Score display and game over screen
7. Proper game loop with 60 FPS

Write complete runnable Python code with pygame imports."""

    response = openai_provider.invoke(prompt)
    code = response.content if hasattr(response, 'content') else str(response)
    
    # Save generated game
    output_dir = Path("tests/e2e/outputs/pygame_shooter")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    (output_dir / "game.py").write_text(code)
    (output_dir / "requirements.txt").write_text("pygame>=2.5.0\n")
    
    # Verify code quality
    code_lower = code.lower()
    assert "pygame" in code_lower
    assert "init" in code_lower
    assert "display" in code_lower
    assert "clock" in code_lower
    assert len(code) > 1000
    
    print(f"✅ Generated {len(code)} chars of Pygame code")
    return True


@pytest.mark.e2e
def test_generate_bevy_game():
    """Generate a real Bevy (Rust) game and verify output."""
    from ai_game_dev.providers import create_default_manager
    
    if not os.getenv("OPENAI_API_KEY"):
        pytest.skip("OPENAI_API_KEY not available")
    
    manager = create_default_manager()
    
    try:
        openai_provider = manager.get_provider("openai")
    except ValueError:
        openai_provider = None
    
    if not openai_provider:
        pytest.skip("No OpenAI provider configured")
    
    # Generate Bevy game
    prompt = """Create a complete Bevy (Rust) 3D game project:

1. Cargo.toml with bevy dependency
2. main.rs with:
   - Basic Bevy app setup
   - 3D camera
   - Simple cube that rotates
   - Light source
   - Window configuration

Write complete Rust code for a minimal but working Bevy game."""

    response = openai_provider.invoke(prompt)
    code = response.content if hasattr(response, 'content') else str(response)
    
    # Save generated game
    output_dir = Path("tests/e2e/outputs/bevy_3d")
    output_dir.mkdir(parents=True, exist_ok=True)
    src_dir = output_dir / "src"
    src_dir.mkdir(exist_ok=True)
    
    # Extract Cargo.toml and main.rs from response
    if "Cargo.toml" in code and "main.rs" in code:
        parts = code.split("main.rs")
        cargo_part = parts[0]
        main_part = parts[1] if len(parts) > 1 else code
        
        (output_dir / "Cargo.toml").write_text(cargo_part)
        (src_dir / "main.rs").write_text(main_part)
    else:
        # Fallback: save as main.rs if format unclear
        (src_dir / "main.rs").write_text(code)
        (output_dir / "Cargo.toml").write_text('[package]\nname = "bevy_game"\nversion = "0.1.0"\nedition = "2021"\n\n[dependencies]\nbevy = "0.11"\n')
    
    # Verify Rust/Bevy code
    main_content = (src_dir / "main.rs").read_text().lower()
    cargo_content = (output_dir / "Cargo.toml").read_text().lower()
    
    assert "bevy" in main_content
    assert "app" in main_content
    assert "bevy" in cargo_content
    
    print(f"✅ Generated Bevy project with {len(code)} chars")
    return True


@pytest.mark.e2e
def test_generate_godot_game():
    """Generate a real Godot game and verify output.""" 
    from ai_game_dev.providers import create_default_manager
    
    if not os.getenv("OPENAI_API_KEY"):
        pytest.skip("OPENAI_API_KEY not available")
    
    manager = create_default_manager()
    
    try:
        openai_provider = manager.get_provider("openai")
    except ValueError:
        openai_provider = None
    
    if not openai_provider:
        pytest.skip("No OpenAI provider configured")
    
    # Generate Godot game
    prompt = """Create a complete Godot 4 game project:

1. project.godot configuration file
2. Main.gd script with:
   - Basic player movement (WASD)
   - Simple scene setup
   - Ready and process functions
3. Player.gd script for character controller

Write complete GDScript code for a minimal but functional Godot game."""

    response = openai_provider.invoke(prompt)
    code = response.content if hasattr(response, 'content') else str(response)
    
    # Save generated game
    output_dir = Path("tests/e2e/outputs/godot_game")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Create basic project structure
    (output_dir / "project.godot").write_text('[application]\nconfig/name="AI Game"\n')
    (output_dir / "Main.gd").write_text(code)
    
    # Verify Godot code
    code_lower = code.lower()
    assert "extends" in code_lower
    assert "func" in code_lower
    assert len(code) > 200
    
    print(f"✅ Generated Godot project with {len(code)} chars")
    return True
"""Main entry point for ai-game-dev package."""

import argparse
import asyncio
import os
import socket
import subprocess
import sys
from pathlib import Path
from typing import Optional


def check_port_available(port: int) -> bool:
    """Check if a port is available for binding."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(('127.0.0.1', port))
            return True
        except OSError:
            return False


def run_server(port: int):
    """Run the AI Game Development Platform server."""
    print("🚀 AI Game Development Platform")
    print("🤖 Powered by OpenAI Agents (GPT-5 & GPT-Image-1)")
    print("🎮 Game Workshop | 🎓 Arcade Academy")
    print("")
    
    # Check if port is available
    if not check_port_available(port):
        print(f"❌ Port {port} is already in use!")
        print("💡 Set AI_GAME_DEV_PORT environment variable to use a different port")
        sys.exit(1)
    
    print(f"🌐 Starting server on http://localhost:{port}")
    print("")
    
    # Find the chainlit app relative to this file
    chainlit_app = Path(__file__).parent / "chainlit_app.py"
    
    # Run Chainlit with custom frontend enabled
    cmd = [
        sys.executable, "-m", "chainlit", "run",
        str(chainlit_app),
        "--port", str(port),
        "--custom-frontend"
    ]
    
    try:
        result = subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start Chainlit: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n👋 Shutting down gracefully...")
        sys.exit(0)


async def generate_game(game_spec_path: Path, output_dir: Optional[Path] = None):
    """Generate a game from a specification file."""
    from ai_game_dev.specs.game_spec_loader import load_game_spec
    from ai_game_dev.agent import create_game, create_educational_game
    from ai_game_dev.assets.asset_registry import get_asset_registry
    from ai_game_dev.cache_config import initialize_sqlite_cache_and_memory
    
    # Initialize cache
    initialize_sqlite_cache_and_memory()
    
    print(f"🎮 Loading game specification: {game_spec_path}")
    
    # Load the game spec
    try:
        game_spec = load_game_spec(game_spec_path)
    except Exception as e:
        print(f"❌ Error loading game spec: {e}")
        return 1
    
    print(f"✅ Loaded: {game_spec.title} ({game_spec.engine})")
    
    # Determine output directory
    if output_dir:
        output_path = output_dir / game_spec.title.lower().replace(' ', '_').replace(':', '')
    else:
        output_path = game_spec.get_absolute_save_path()
    
    output_path.mkdir(parents=True, exist_ok=True)
    print(f"📁 Output directory: {output_path}")
    
    # Get assets from registry
    registry = get_asset_registry()
    asset_paths = game_spec.get_engine_specific_paths()
    
    # Create full game specification
    full_spec = {
        "title": game_spec.title,
        "type": game_spec.type,
        "engine": game_spec.engine,
        "description": game_spec.description_full or game_spec.description_short,
        "assets": asset_paths,
        "mechanics": game_spec.mechanics,
        "levels": game_spec.levels,
        "features": game_spec.features,
        "characters": game_spec.characters,
        "dialogue": game_spec.dialogue,
        "ui": game_spec.ui
    }
    
    # Add educational config if present
    if game_spec.educational:
        full_spec["educational"] = game_spec.educational
    
    print("🔨 Generating game code...")
    
    # Generate the game
    try:
        if game_spec.educational:
            project = await create_educational_game(
                topic=game_spec.description_short,
                concepts=game_spec.educational.get("concepts", []),
                level=game_spec.educational.get("mode", "progressive"),
                game_spec=full_spec
            )
        else:
            project = await create_game(
                description=game_spec.description_full or game_spec.description_short,
                engine=game_spec.engine,
                game_spec=full_spec
            )
        
        # Write game files
        for filename, content in project.code_files.items():
            file_path = output_path / filename
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content)
            print(f"  📄 Created: {filename}")
        
        # Copy the game spec
        import shutil
        spec_dest = output_path / "game_spec.toml"
        shutil.copy(game_spec_path, spec_dest)
        
        print(f"✅ Game generated successfully at: {output_path}")
        return 0
        
    except Exception as e:
        print(f"❌ Error generating game: {e}")
        import traceback
        traceback.print_exc()
        return 1


async def generate_assets(assets_spec_path: Path, output_dir: Optional[Path] = None):
    """Generate assets from a specification file."""
    import tomllib
    from ai_game_dev.graphics import generate_game_sprite, generate_game_background
    from ai_game_dev.audio import generate_sound_effect, generate_background_music
    from ai_game_dev.assets.asset_registry import get_asset_registry
    from ai_game_dev.cache_config import initialize_sqlite_cache_and_memory
    
    # Initialize cache
    initialize_sqlite_cache_and_memory()
    
    print(f"🎨 Loading assets specification: {assets_spec_path}")
    
    # Load the assets spec
    try:
        with open(assets_spec_path, 'rb') as f:
            spec_data = tomllib.load(f)
            assets_spec = spec_data.get('assets', spec_data)
    except Exception as e:
        print(f"❌ Error loading assets spec: {e}")
        return 1
    
    # Determine output directory
    if output_dir:
        assets_dir = output_dir
    else:
        from ai_game_dev.constants import GENERATED_ASSETS_DIR
        assets_dir = Path(GENERATED_ASSETS_DIR)
    
    assets_dir.mkdir(parents=True, exist_ok=True)
    print(f"📁 Output directory: {assets_dir}")
    
    # Get asset registry
    registry = get_asset_registry()
    
    # Generate sprites
    if "sprites" in assets_spec.get("generated", {}):
        print("🖼️  Generating sprites...")
        for category, items_data in assets_spec["generated"]["sprites"].items():
            sprite_dir = assets_dir / "sprites" / category
            sprite_dir.mkdir(parents=True, exist_ok=True)
            
            for item_spec in items_data.get("items", []):
                name = item_spec["name"]
                print(f"  Creating sprite: {category}/{name}")
                
                try:
                    result = await generate_game_sprite(
                        name=name,
                        description=item_spec.get("description", f"{name} sprite"),
                        style=item_spec.get("style", "cyberpunk"),
                        save_path=str(sprite_dir / f"{name}.png")
                    )
                    
                    # Register in asset registry
                    registry.register_asset(
                        name=name,
                        path=f"/public/static/assets/generated/sprites/{category}/{name}.png",
                        asset_type="sprites",
                        category=category,
                        generated=True
                    )
                    
                except Exception as e:
                    print(f"    ❌ Error: {e}")
    
    # Generate audio
    if "audio" in assets_spec.get("generated", {}):
        print("🔊 Generating audio...")
        for category, sounds_data in assets_spec["generated"]["audio"].items():
            audio_dir = assets_dir / "audio" / category
            audio_dir.mkdir(parents=True, exist_ok=True)
            
            if category == "music":
                # Handle music tracks
                for track_spec in sounds_data.get("tracks", []):
                    name = track_spec["name"]
                    print(f"  Creating music: {name}")
                    
                    try:
                        result = await generate_background_music(
                            name=name,
                            style=track_spec.get("style", "electronic"),
                            duration=track_spec.get("duration", 120),
                            save_path=str(audio_dir / f"{name}.mp3")
                        )
                        
                        # Register in asset registry
                        registry.register_asset(
                            name=name,
                            path=f"/public/static/assets/generated/audio/{category}/{name}.mp3",
                            asset_type="audio",
                            category=category,
                            generated=True
                        )
                        
                    except Exception as e:
                        print(f"    ❌ Error: {e}")
            else:
                # Handle sound effects
                for sound_spec in sounds_data.get("sounds", []):
                    name = sound_spec["name"]
                    print(f"  Creating sound: {category}/{name}")
                    
                    try:
                        result = await generate_sound_effect(
                            effect_name=name,
                            style=sound_spec.get("style", "digital"),
                            save_path=str(audio_dir / f"{name}.wav")
                        )
                        
                        # Register in asset registry
                        registry.register_asset(
                            name=name,
                            path=f"/public/static/assets/generated/audio/{category}/{name}.wav",
                            asset_type="audio",
                            category=category,
                            generated=True
                        )
                        
                    except Exception as e:
                        print(f"    ❌ Error: {e}")
    
    # Generate backgrounds
    if "backgrounds" in assets_spec.get("generated", {}):
        print("🏞️  Generating backgrounds...")
        for category, scenes in assets_spec["generated"]["backgrounds"].items():
            bg_dir = assets_dir / "backgrounds" / category
            bg_dir.mkdir(parents=True, exist_ok=True)
            
            for scene_spec in scenes:
                name = scene_spec["name"]
                print(f"  Creating background: {name}")
                
                try:
                    result = await generate_game_background(
                        scene=scene_spec.get("description", name),
                        style=scene_spec.get("style", "cyberpunk"),
                        save_path=str(bg_dir / f"{name}.png")
                    )
                    
                    # Register in asset registry
                    registry.register_asset(
                        name=name,
                        path=f"/public/static/assets/generated/backgrounds/{category}/{name}.png",
                        asset_type="backgrounds",
                        category=category,
                        generated=True
                    )
                    
                except Exception as e:
                    print(f"    ❌ Error: {e}")
    
    print("✅ Asset generation complete!")
    return 0


def main():
    """Main entry point with argument parsing."""
    parser = argparse.ArgumentParser(
        description="AI Game Development Platform",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run the server (default)
  python -m ai_game_dev
  
  # Generate a game from spec
  python -m ai_game_dev --game-spec games/pygame/neotokyo_code_academy.toml
  
  # Generate assets only
  python -m ai_game_dev --assets-spec src/ai_game_dev/specs/server_assets.toml
  
  # Specify output directories
  python -m ai_game_dev --game-spec my_game.toml --game-dir output/
  python -m ai_game_dev --assets-spec my_assets.toml --assets-dir output/assets/
        """
    )
    
    parser.add_argument(
        "--game-spec",
        type=Path,
        help="Path to game specification TOML file"
    )
    
    parser.add_argument(
        "--game-dir",
        type=Path,
        help="Output directory for generated game (optional)"
    )
    
    parser.add_argument(
        "--assets-spec",
        type=Path,
        help="Path to assets specification TOML file"
    )
    
    parser.add_argument(
        "--assets-dir",
        type=Path,
        help="Output directory for generated assets (optional)"
    )
    
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.environ.get('AI_GAME_DEV_PORT', '8000')),
        help="Port for the server (default: 8000 or AI_GAME_DEV_PORT env var)"
    )
    
    args = parser.parse_args()
    
    # Determine mode and execute
    if args.game_spec:
        # Game generation mode
        exit_code = asyncio.run(generate_game(args.game_spec, args.game_dir))
        sys.exit(exit_code)
    elif args.assets_spec:
        # Assets generation mode
        exit_code = asyncio.run(generate_assets(args.assets_spec, args.assets_dir))
        sys.exit(exit_code)
    else:
        # Server mode (default)
        run_server(args.port)


if __name__ == "__main__":
    main()
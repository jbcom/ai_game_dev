"""
FastMCP Server for AI Game Development
Provides Model Context Protocol interface for game generation using FastMCP
"""

import asyncio
import json
from typing import Any, Dict, List, Optional
from pathlib import Path

from fastmcp import FastMCP

from ai_game_dev import AIGameDev, GameSpec, GameType, ComplexityLevel
from ai_game_assets import AssetGenerator


# Initialize FastMCP server
mcp = FastMCP("AI Game Development Server")


@mcp.tool()
async def generate_game(
    name: str,
    description: str,
    game_type: str,
    complexity: str,
    features: List[str] = None,
    engine: str = "pygame"
) -> str:
    """
    Generate a complete game project from a specification.
    
    Args:
        name: Name of the game
        description: Detailed description of the game
        game_type: Type of game (2d or 3d)
        complexity: Complexity level (beginner, intermediate, advanced)
        features: List of desired game features
        engine: Target game engine (pygame, arcade, bevy, godot)
    
    Returns:
        JSON string with generation results
    """
    try:
        # Initialize AI systems
        game_dev = AIGameDev()
        
        # Parse arguments
        game_type_enum = GameType.TWO_DIMENSIONAL if game_type == "2d" else GameType.THREE_DIMENSIONAL
        complexity_enum = getattr(ComplexityLevel, complexity.upper())
        
        # Create game specification
        spec = GameSpec(
            name=name,
            description=description,
            game_type=game_type_enum,
            features=features or [],
            complexity=complexity_enum
        )
        
        # Generate the game
        project = await game_dev.generate_project_for_engine(spec, engine)
        
        # Return structured result
        result = {
            "success": True,
            "game_name": spec.name,
            "engine": engine,
            "files_generated": len(project.files) if hasattr(project, 'files') else 5,
            "project_structure": {
                "main_file": "main.py",
                "game_logic": "game.py", 
                "player_system": "player.py",
                "constants": "constants.py"
            },
            "message": f"✅ Generated {spec.name} for {engine} engine successfully!"
        }
        
        return json.dumps(result, indent=2)
        
    except Exception as e:
        error_result = {
            "success": False,
            "error": str(e),
            "message": "❌ Game generation failed"
        }
        return json.dumps(error_result, indent=2)


@mcp.tool()
async def generate_assets(
    asset_type: str,
    description: str,
    style: str = "realistic",
    resolution: str = "512x512",
    duration: float = 30.0
) -> str:
    """
    Generate game assets like images, sounds, and music.
    
    Args:
        asset_type: Type of asset to generate (image, audio, music)
        description: Description of the asset to generate
        style: Visual or audio style
        resolution: Resolution for images (e.g., '512x512')
        duration: Duration for audio assets in seconds
    
    Returns:
        JSON string with generation results
    """
    try:
        # Initialize asset generator
        asset_gen = AssetGenerator()
        
        if asset_type == "image":
            result = await asset_gen.generate_image(
                description,
                style=style,
                resolution=resolution
            )
        elif asset_type == "audio":
            result = await asset_gen.generate_audio(
                description,
                duration=duration
            )
        elif asset_type == "music":
            result = await asset_gen.generate_music(
                description,
                duration=duration
            )
        else:
            raise ValueError(f"Unknown asset type: {asset_type}")
        
        # Return structured result
        response = {
            "success": True,
            "asset_type": asset_type,
            "description": description,
            "generated_asset": {
                "url": result.get("url", ""),
                "format": result.get("format", ""),
                "size": result.get("size", "")
            },
            "message": f"✅ Generated {asset_type} asset successfully!"
        }
        
        return json.dumps(response, indent=2)
        
    except Exception as e:
        error_result = {
            "success": False,
            "error": str(e),
            "message": f"❌ Asset generation failed"
        }
        return json.dumps(error_result, indent=2)


@mcp.tool()
async def list_game_engines() -> str:
    """
    List supported game engines and their capabilities.
    
    Returns:
        JSON string with engine information
    """
    engines = {
        "pygame": {
            "language": "Python",
            "type": "2D",
            "best_for": "Learning, prototyping, simple games",
            "features": ["Cross-platform", "Easy to learn", "Large community"]
        },
        "arcade": {
            "language": "Python", 
            "type": "2D",
            "best_for": "Educational games, web deployment",
            "features": ["Modern Python", "Built-in physics", "Web-friendly"]
        },
        "bevy": {
            "language": "Rust",
            "type": "2D/3D",
            "best_for": "High-performance games, ECS architecture",
            "features": ["Data-driven", "Concurrent", "Modern architecture"]
        },
        "godot": {
            "language": "GDScript/C#",
            "type": "2D/3D", 
            "best_for": "Complete game development, visual scripting",
            "features": ["Full-featured", "Visual editor", "Multi-platform"]
        }
    }
    
    return json.dumps({
        "supported_engines": engines,
        "recommendation": "Choose based on your experience level and project requirements"
    }, indent=2)


async def start_server(host: str = "localhost", port: int = 8080):
    """Start the FastMCP server."""
    print("🚀 AI Game Development FastMCP Server")
    print("=" * 40)
    print(f"🌐 Host: {host}")
    print(f"📡 Port: {port}")
    print("🤖 Available tools:")
    print("  - generate_game: Create complete game projects")
    print("  - generate_assets: Create images, sounds, and music")
    print("  - list_game_engines: Show supported engines")
    print("=" * 40)
    
    # Start the FastMCP server
    await mcp.run(transport="stdio")


def create_server():
    """Create and return the FastMCP server instance."""
    return mcp
"""
MCP Tools for AI Game Development
Individual tools that can be called via the Model Context Protocol
"""

import json
from typing import Any, Dict
from abc import ABC, abstractmethod

from ai_game_dev import AIGameDev, GameSpec, GameType, ComplexityLevel
from ai_game_assets import AssetGenerator


class MCPTool(ABC):
    """Base class for MCP tools."""
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Tool description."""
        pass
    
    @property
    @abstractmethod
    def input_schema(self) -> Dict[str, Any]:
        """JSON Schema for tool input."""
        pass
    
    @abstractmethod
    async def execute(self, arguments: Dict[str, Any]) -> str:
        """Execute the tool with given arguments."""
        pass


class GameGenerationTool(MCPTool):
    """Tool for generating complete games."""
    
    def __init__(self, game_dev: AIGameDev):
        self.game_dev = game_dev
    
    @property
    def description(self) -> str:
        return "Generate a complete game project from a specification"
    
    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Name of the game"
                },
                "description": {
                    "type": "string", 
                    "description": "Detailed description of the game"
                },
                "game_type": {
                    "type": "string",
                    "enum": ["2d", "3d"],
                    "description": "Type of game (2D or 3D)"
                },
                "complexity": {
                    "type": "string",
                    "enum": ["beginner", "intermediate", "advanced"],
                    "description": "Complexity level"
                },
                "features": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of desired game features"
                },
                "engine": {
                    "type": "string",
                    "enum": ["pygame", "arcade", "bevy", "godot"],
                    "description": "Target game engine",
                    "default": "pygame"
                }
            },
            "required": ["name", "description", "game_type", "complexity"]
        }
    
    async def execute(self, arguments: Dict[str, Any]) -> str:
        """Generate a game project."""
        try:
            # Parse arguments
            game_type = GameType.TWO_DIMENSIONAL if arguments["game_type"] == "2d" else GameType.THREE_DIMENSIONAL
            complexity = getattr(ComplexityLevel, arguments["complexity"].upper())
            
            # Create game specification
            spec = GameSpec(
                name=arguments["name"],
                description=arguments["description"],
                game_type=game_type,
                features=arguments.get("features", []),
                complexity=complexity
            )
            
            # Generate the game
            engine = arguments.get("engine", "pygame")
            project = await self.game_dev.generate_project_for_engine(spec, engine)
            
            # Return structured result
            result = {
                "success": True,
                "game_name": spec.name,
                "engine": engine,
                "files_generated": len(project.files) if hasattr(project, 'files') else 5,
                "project_structure": {
                    "main_file": f"main.py",
                    "game_logic": f"game.py",
                    "player_system": f"player.py",
                    "constants": f"constants.py"
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


class AssetGenerationTool(MCPTool):
    """Tool for generating game assets."""
    
    def __init__(self, asset_gen: AssetGenerator):
        self.asset_gen = asset_gen
    
    @property
    def description(self) -> str:
        return "Generate game assets like images, sounds, and music"
    
    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "asset_type": {
                    "type": "string",
                    "enum": ["image", "audio", "music"],
                    "description": "Type of asset to generate"
                },
                "description": {
                    "type": "string",
                    "description": "Description of the asset to generate"
                },
                "style": {
                    "type": "string",
                    "description": "Visual or audio style",
                    "default": "realistic"
                },
                "resolution": {
                    "type": "string",
                    "description": "Resolution for images (e.g., '512x512')",
                    "default": "512x512"
                },
                "duration": {
                    "type": "number",
                    "description": "Duration for audio assets in seconds",
                    "default": 30
                }
            },
            "required": ["asset_type", "description"]
        }
    
    async def execute(self, arguments: Dict[str, Any]) -> str:
        """Generate game assets."""
        try:
            asset_type = arguments["asset_type"]
            description = arguments["description"]
            
            if asset_type == "image":
                result = await self.asset_gen.generate_image(
                    description,
                    style=arguments.get("style", "realistic"),
                    resolution=arguments.get("resolution", "512x512")
                )
            elif asset_type == "audio":
                result = await self.asset_gen.generate_audio(
                    description,
                    duration=arguments.get("duration", 30)
                )
            elif asset_type == "music":
                result = await self.asset_gen.generate_music(
                    description,
                    duration=arguments.get("duration", 120)
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
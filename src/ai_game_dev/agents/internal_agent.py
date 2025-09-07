"""
Internal Asset Generation Agent
Uses LangChain DALLE directly for all asset generation
"""

import asyncio
import json
import toml
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

try:
    from ai_game_dev.agents.base_agent import PygameAgent, AgentConfig
except ImportError:
    from .base_agent import PygameAgent, AgentConfig

# LangChain DALLE imports
from langchain_community.utilities.dalle_image_generator import DallEAPIWrapper
from langchain_community.tools.openai_dalle_image_generation import OpenAIDALLEImageGenerationTool
import requests

# Image post-processing
from ai_game_dev.assets.image_processor import ImageProcessor


@dataclass
class InternalAssetTask:
    """Represents a task for internal asset generation."""
    task_type: str  # "static_assets", "educational_game", "educational_assets"
    description: str
    dependencies: List[str] = None
    completed: bool = False
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []


class InternalAssetAgent(PygameAgent):
    """
    Internal agent that coordinates all asset generation using LangChain DALLE.
    """
    
    def __init__(self):
        # Configure for internal asset generation
        config = AgentConfig(
            model="gpt-4o",
            temperature=0.2,
            instructions=self._get_internal_asset_instructions()
        )
        super().__init__(config)
        self.dalle_wrapper = None
        self.dalle_tool = None
        self.tasks: List[InternalAssetTask] = []
        self.image_processor = ImageProcessor()
        
    async def initialize(self):
        """Initialize the internal agent with LangChain DALLE."""
        
        # Initialize parent pygame agent
        await super().initialize()
        
        # Initialize LangChain DALLE tool
        self.dalle_wrapper = DallEAPIWrapper()
        self.dalle_tool = OpenAIDALLEImageGenerationTool(api_wrapper=self.dalle_wrapper)
        
    async def __aenter__(self):
        await self.initialize()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        # No cleanup needed for LangChain DALLE tool
        pass
        
    def _get_internal_asset_instructions(self) -> str:
        """Get specialized instructions for internal asset generation."""
        return """
        
        INTERNAL ASSET GENERATION WITH LANGCHAIN DALLE:
        
        You coordinate all internal asset generation using LangChain DALLE tool.
        Your responsibilities include:
        
        1. PLATFORM STATIC ASSETS:
           - Generate cyberpunk UI elements (buttons, icons, panels)
           - Create engine showcase artwork (pygame, bevy, godot panels)
           - Produce branding and logo assets
           
        2. EDUCATIONAL RPG ASSETS:
           - Create Professor Pixel character assets
           - Generate cyberpunk character sprites
           - Produce NeoTokyo environment tilesets
           - Create educational UI elements
           
        3. ASSET QUALITY STANDARDS:
           - All images generated using LangChain DALLE tool
           - Cyberpunk aesthetic consistency
           - Production-quality results
           
        Always return dict responses with:
        - success: bool
        - generated: list of generated assets
        - failed: list of failed assets
        - assets_created: int count
        """
        
    async def execute_task(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute an internal asset generation task."""
        
        # Determine task type from context
        asset_type = context.get("asset_type", "")
        
        if "static" in asset_type:
            return await self._generate_static_assets(context)
        elif "educational" in asset_type and "code" in asset_type:
            return await self._generate_educational_game_code(context)
        elif "educational" in asset_type and "asset" in asset_type:
            return await self._generate_educational_assets(context)
        else:
            return {
                "success": False,
                "message": f"Unknown asset type: {asset_type}",
                "generated": [],
                "failed": [],
                "assets_created": 0
            }
    
    async def _generate_static_assets(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate static platform assets using LangChain DALLE."""
        
        results = {
            "success": True,
            "generated": [],
            "failed": [],
            "assets_created": 0,
            "message": "Static assets generated successfully"
        }
        
        try:
            # Define platform UI assets to generate
            ui_dir = Path("src/ai_game_dev/server/static/assets")
            ui_dir.mkdir(parents=True, exist_ok=True)
            
            ui_assets = [
                {
                    "prompt": "Cyberpunk AI Game Dev main logo with neon blue accents and futuristic typography",
                    "filename": "main-logo.png"
                },
                {
                    "prompt": "Pygame engine panel with Python snake logo and game development icons, cyberpunk interface design",
                    "filename": "pygame-panel.png"
                },
                {
                    "prompt": "Bevy engine panel with Rust gear logo and ECS component icons, cyberpunk interface design",
                    "filename": "bevy-panel.png"
                },
                {
                    "prompt": "Godot engine panel with robot head logo and node-based icons, cyberpunk interface design",
                    "filename": "godot-panel.png"
                }
            ]
            
            # Generate UI assets using LangChain DALLE directly
            for asset in ui_assets:
                try:
                    # Generate image URL using LangChain DALLE
                    image_url = self.dalle_tool.run(asset["prompt"])
                    
                    # Download the image
                    response = requests.get(image_url)
                    if response.status_code == 200:
                        image_data = response.content
                        
                        # Save to platform assets
                        asset_path = ui_dir / asset["filename"]
                        with open(asset_path, "wb") as f:
                            f.write(image_data)
                        
                        # Automatic post-processing (detects frames vs sprites automatically)
                        try:
                            process_results = self.image_processor.process_asset(asset_path, asset_path)
                            print(f"✅ Auto-processed {asset_path}: {process_results.get('processing_type', 'unknown')}")
                        except Exception as proc_e:
                            # Log processing error but don't fail entire generation
                            print(f"Warning: Image post-processing failed for {asset_path}: {proc_e}")
                        
                        results["generated"].append({
                            "type": "ui_asset",
                            "path": str(asset_path),
                            "size": len(image_data),
                            "prompt": asset["prompt"]
                        })
                    else:
                        results["failed"].append({
                            "type": "ui_asset", 
                            "request": asset["prompt"],
                            "error": f"Failed to download image from {image_url}"
                        })
                        
                except Exception as e:
                    results["failed"].append({
                        "type": "ui_asset", 
                        "request": asset["prompt"],
                        "error": str(e)
                    })
                        
        except Exception as e:
            results["failed"].append({
                "task": "static_asset_generation",
                "error": str(e)
            })
            results["success"] = False
            results["message"] = f"Static asset generation failed: {str(e)}"
            
        results["assets_created"] = len(results["generated"])
        return results
    
    async def _generate_educational_game_code(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate educational RPG code files."""
        
        results = {
            "success": True,
            "files": [],
            "failed": [],
            "message": "Educational RPG code generated successfully"
        }
        
        try:
            # Create educational game directory
            game_dir = Path("src/ai_game_dev/educational_game")
            game_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate main.py
            main_code = await self._generate_pygame_main_file()
            main_path = game_dir / "main.py"
            with open(main_path, "w") as f:
                f.write(main_code)
            results["files"].append(str(main_path))
            
            # Generate game.py
            game_code = await self._generate_pygame_game_file()
            game_path = game_dir / "game.py"
            with open(game_path, "w") as f:
                f.write(game_code)
            results["files"].append(str(game_path))
            
            # Generate player.py
            player_code = await self._generate_pygame_player_file()
            player_path = game_dir / "player.py"
            with open(player_path, "w") as f:
                f.write(player_code)
            results["files"].append(str(player_path))
            
            # Generate requirements.txt
            requirements = "pygame>=2.1.0\n"
            req_path = game_dir / "requirements.txt"
            with open(req_path, "w") as f:
                f.write(requirements)
            results["files"].append(str(req_path))
            
        except Exception as e:
            results["failed"].append({
                "task": "educational_game_code",
                "error": str(e)
            })
            results["success"] = False
            results["message"] = f"Educational RPG code generation failed: {str(e)}"
            
        return results
    
    async def _generate_educational_assets(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate educational RPG assets using LangChain DALLE."""
        
        results = {
            "success": True,
            "characters": [],
            "environments": [],
            "ui_elements": [],
            "failed": [],
            "message": "Educational assets generated successfully"
        }
        
        try:
            # Create educational asset directories
            base_dir = Path("src/ai_game_dev/educational_game/assets")
            char_dir = base_dir / "characters"
            env_dir = base_dir / "environments"
            ui_dir = base_dir / "ui"
            
            for dir_path in [char_dir, env_dir, ui_dir]:
                dir_path.mkdir(parents=True, exist_ok=True)
            
            # Generate character assets
            characters = [
                {
                    "prompt": "Professor Pixel: Cyberpunk coding mentor with neon purple hair, AR glasses, holographic code interface, pixel art style",
                    "filename": "professor-pixel.png"
                },
                {
                    "prompt": "Code Knight: Cyberpunk warrior with algorithmic armor and data sword, pixel art character sprite",
                    "filename": "code-knight.png"
                },
                {
                    "prompt": "Data Sage: Cyberpunk wise character with database robes and query staff, pixel art character sprite",
                    "filename": "data-sage.png"
                }
            ]
            
            for char in characters:
                try:
                    image_url = self.dalle_tool.run(char["prompt"])
                    response = requests.get(image_url)
                    if response.status_code == 200:
                        char_path = char_dir / char["filename"]
                        with open(char_path, "wb") as f:
                            f.write(response.content)
                        
                        # Automatic post-processing (will detect if sprite or frame)
                        try:
                            process_results = self.image_processor.process_asset(char_path, char_path)
                            print(f"✅ Auto-processed character: {process_results.get('processing_type', 'unknown')}")
                        except Exception as proc_e:
                            print(f"Warning: Character processing failed for {char_path}: {proc_e}")
                            
                        results["characters"].append(str(char_path))
                    else:
                        results["failed"].append({
                            "type": "character",
                            "request": char["prompt"],
                            "error": f"Failed to download from {image_url}"
                        })
                except Exception as e:
                    results["failed"].append({
                        "type": "character",
                        "request": char["prompt"],
                        "error": str(e)
                    })
            
            # Generate environment assets
            environments = [
                {
                    "prompt": "NeoTokyo Code Academy: Underground cyberpunk hacker school with holographic displays, neon lighting, pixel art tileset",
                    "filename": "neotokyo-academy.png"
                },
                {
                    "prompt": "Data Labs: Cyberpunk laboratory with server racks and holographic interfaces, pixel art environment",
                    "filename": "data-labs.png"
                }
            ]
            
            for env in environments:
                try:
                    image_url = self.dalle_tool.run(env["prompt"])
                    response = requests.get(image_url)
                    if response.status_code == 200:
                        env_path = env_dir / env["filename"]
                        with open(env_path, "wb") as f:
                            f.write(response.content)
                        results["environments"].append(str(env_path))
                    else:
                        results["failed"].append({
                            "type": "environment",
                            "request": env["prompt"],
                            "error": f"Failed to download from {image_url}"
                        })
                except Exception as e:
                    results["failed"].append({
                        "type": "environment",
                        "request": env["prompt"],
                        "error": str(e)
                    })
            
            # Generate UI elements
            ui_elements = [
                {
                    "prompt": "Cyberpunk coding progress bar with neon blue fill and binary numbers, UI element design",
                    "filename": "progress-bar.png"
                },
                {
                    "prompt": "Cyberpunk achievement badge for programming skills, hexagonal design with neon accents",
                    "filename": "achievement-badge.png"
                }
            ]
            
            for ui in ui_elements:
                try:
                    image_url = self.dalle_tool.run(ui["prompt"])
                    response = requests.get(image_url)
                    if response.status_code == 200:
                        ui_path = ui_dir / ui["filename"]
                        with open(ui_path, "wb") as f:
                            f.write(response.content)
                        results["ui_elements"].append(str(ui_path))
                    else:
                        results["failed"].append({
                            "type": "ui_element",
                            "request": ui["prompt"],
                            "error": f"Failed to download from {image_url}"
                        })
                except Exception as e:
                    results["failed"].append({
                        "type": "ui_element",
                        "request": ui["prompt"],
                        "error": str(e)
                    })
                        
        except Exception as e:
            results["failed"].append({
                "task": "educational_asset_generation",
                "error": str(e)
            })
            results["success"] = False
            results["message"] = f"Educational asset generation failed: {str(e)}"
            
        return results
        
    async def _generate_pygame_main_file(self) -> str:
        """Generate the main.py file for the educational RPG."""
        
        prompt = """Create a complete main.py file for "NeoTokyo Code Academy: The Binary Rebellion" - a cyberpunk educational RPG.

Requirements:
- Pygame initialization and proper cleanup
- 800x600 screen with cyberpunk color scheme
- Professional game loop with 60 FPS
- Import game and player modules
- Error handling and graceful shutdown
- Entry point that starts the educational RPG

The game teaches programming concepts through cyberpunk RPG mechanics with Professor Pixel as guide.

Generate production-ready Python code with proper structure and comments."""

        messages = [{"role": "user", "content": prompt}]
        response = await self.llm.ainvoke(messages)
        
        return response.content
        
    async def _generate_pygame_game_file(self) -> str:
        """Generate the game.py file for the educational RPG."""
        
        prompt = """Create a complete game.py file for "NeoTokyo Code Academy: The Binary Rebellion" educational RPG.

Requirements:
- Game class with proper state management (menu, playing, game_over)
- Educational progression system with coding challenges
- Character classes: Code Knight, Data Sage, Bug Hunter, Web Weaver
- Professor Pixel as cyberpunk mentor/guide
- NeoTokyo environments (academy, labs, towers)
- Asset loading and resource management
- Collision detection and RPG mechanics
- Educational content integration (Python concepts)

Game Features:
- Turn-based combat with programming puzzles
- Skill trees for different programming concepts
- Inventory system for code tools and data structures
- Quest system teaching algorithms and data structures

Generate production-ready pygame code with proper class structure."""

        messages = [{"role": "user", "content": prompt}]
        response = await self.llm.ainvoke(messages)
        
        return response.content
        
    async def _generate_pygame_player_file(self) -> str:
        """Generate the player.py file for the educational RPG."""
        
        prompt = """Create a complete player.py file for "NeoTokyo Code Academy: The Binary Rebellion" educational RPG.

Requirements:
- Player class with movement and controls
- Character progression and skill system
- Inventory management for code tools
- Experience and leveling system
- Input processing (keyboard/mouse)
- Animation and sprite handling
- Health, mana, and coding skill attributes

Educational Elements:
- Skills represent programming concepts (loops, functions, OOP, etc.)
- Experience gained through solving coding challenges
- Equipment represents development tools (IDEs, debuggers, etc.)
- Abilities map to programming paradigms

Generate production-ready pygame player class with proper state management."""

        messages = [{"role": "user", "content": prompt}]
        response = await self.llm.ainvoke(messages)
        
        return response.content
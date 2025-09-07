"""
Internal Asset Generation Agent
Inherits from pygame agent and adds comprehensive asset generation capabilities
"""

import asyncio
import json
import toml
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

try:
    from ai_game_dev.agents.base_agent import PygameAgent, AgentConfig
    from ai_game_dev.assets.generator import AssetGenerator, AssetRequest
except ImportError:
    from .base_agent import PygameAgent, AgentConfig
    from ..assets.generator import AssetGenerator, AssetRequest


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
    Internal agent that coordinates all static asset generation for the platform.
    
    Inherits from PygameAgent and extends it with:
    - Comprehensive asset generation coordination
    - Educational RPG asset creation
    - Platform UI asset management
    - Batch processing coordination
    - Quality assurance and validation
    """
    
    def __init__(self):
        # Configure for internal asset generation
        config = AgentConfig(
            model="gpt-4o",
            temperature=0.2,  # Lower temperature for consistent asset generation
            instructions=self._get_internal_asset_instructions()
        )
        super().__init__(config)
        self.asset_generator = None
        self.tasks: List[InternalAssetTask] = []
        self.asset_specification = None
        
    async def initialize(self):
        """Initialize the internal agent with asset generation capabilities."""
        
        # Initialize parent pygame agent
        await super().initialize()
        
        # Initialize asset generator
        self.asset_generator = AssetGenerator()
        await self.asset_generator.__aenter__()
        
        # Load unified asset specification
        await self._load_asset_specification()
        
    async def __aenter__(self):
        await self.initialize()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.asset_generator:
            await self.asset_generator.__aexit__(exc_type, exc_val, exc_tb)
        
    def _get_internal_asset_instructions(self) -> str:
        """Get specialized instructions for internal asset generation."""
        return """
        
        INTERNAL ASSET GENERATION EXTENSIONS:
        
        You are now equipped with advanced asset generation capabilities for internal platform development.
        Your responsibilities include:
        
        1. PLATFORM STATIC ASSETS:
           - Generate cyberpunk UI elements (buttons, icons, panels)
           - Create engine showcase artwork (pygame, bevy, godot panels)
           - Produce audio interface components
           - Generate branding and logo assets
           
        2. EDUCATIONAL RPG ASSETS:
           - Create Professor Pixel character assets (portraits, sprites, avatars)
           - Generate cyberpunk character class sprites (Code Knight, Data Sage, etc.)
           - Produce NeoTokyo environment tilesets (academy, labs, towers)
           - Create educational UI elements (progress bars, badges, tutorials)
           
        3. ASSET QUALITY STANDARDS:
           - All images must be production-quality using OpenAI DALL-E 3
           - Cyberpunk aesthetic consistency across all assets
           - Proper transparency for UI elements
           - Appropriate sizing for different use cases
           - Batch generation with proper concurrency control
           
        4. COORDINATION RESPONSIBILITIES:
           - Process unified asset specifications (TOML files)
           - Manage dependencies between asset types
           - Ensure idempotent generation (check existing assets)
           - Validate asset completeness and quality
           - Report progress and handle failures gracefully
           
        5. EDUCATIONAL GAME INTEGRATION:
           - Generate assets that integrate with the educational pygame RPG
           - Ensure character sprites work with the game mechanics
           - Create tilesets that support the cyberpunk storyline
           - Produce UI elements that enhance the learning experience
           
        When generating assets, always:
        - Use descriptive, style-consistent prompts
        - Generate high-quality, production-ready assets
        - Maintain the cyberpunk aesthetic across all pieces
        - Ensure assets serve their functional purpose
        - Batch process efficiently with proper error handling
        """
            
    async def _load_asset_specification(self):
        """Load the unified asset specification from TOML."""
        
        spec_path = Path("src/ai_game_dev/specs/web_platform_assets.toml")
        
        if spec_path.exists():
            try:
                with open(spec_path, 'r') as f:
                    content = f.read()
                    # Handle potential TOML parsing issues
                    self.asset_specification = toml.loads(content)
            except Exception as e:
                # If TOML parsing fails, create a basic specification
                self.asset_specification = self._create_fallback_specification()
        else:
            # Create fallback specification if file doesn't exist
            self.asset_specification = self._create_fallback_specification()
            
    def _create_fallback_specification(self) -> Dict[str, Any]:
        """Create a fallback asset specification if TOML parsing fails."""
        return {
            "platform_info": {
                "name": "AI Game Dev Platform",
                "description": "Asset specification for platform and educational game"
            },
            "assets": {
                "ui_elements": {
                    "prompts": [
                        "cyberpunk play button with neon glow",
                        "cyberpunk pause button with tech design", 
                        "cyberpunk stop button futuristic style",
                        "cyberpunk navigation arrow left neon cyan",
                        "cyberpunk navigation arrow right neon cyan"
                    ],
                    "size": "256x256",
                    "category": "ui_controls"
                },
                "character_sprites": {
                    "prompts": [
                        "Professor Pixel cyberpunk mentor AR glasses neon hair",
                        "Code Knight cybernetic warrior plasma sword",
                        "Data Sage mystical hacker holographic robes", 
                        "Bug Hunter agile cyber-assassin stealth cloak",
                        "Web Weaver digital architect quantum tablet"
                    ],
                    "size": "64x64",
                    "category": "rpg_characters"
                },
                "environments": {
                    "prompts": [
                        "NeoTokyo Code Academy cyberpunk school exterior",
                        "Underground programming lab rebel classroom",
                        "Algorithm Tower corporate data center interior"
                    ],
                    "size": "512x512", 
                    "category": "educational_environments"
                }
            }
        }
            
    async def generate_all_static_assets(self, force_rebuild: bool = False) -> Dict[str, Any]:
        """Generate all platform static assets from the specification."""
        
        if not self.asset_specification:
            raise RuntimeError("Asset specification not loaded")
            
        results = {
            "generated": [],
            "skipped": [],
            "failed": [],
            "total_processed": 0
        }
        
        # Check if assets already exist (idempotent behavior)
        assets_dir = Path("src/ai_game_dev/server/static/assets")
        if not force_rebuild and self._check_static_assets_complete(assets_dir):
            results["skipped"] = ["All static assets already exist"]
            return results
            
        # Process each asset category
        for category_key, category_data in self.asset_specification.items():
            if not category_key.startswith("assets."):
                continue
                
            category_name = category_key.replace("assets.", "")
            
            try:
                # Generate assets for this category
                category_results = await self._generate_asset_category(category_name, category_data)
                results["generated"].extend(category_results)
                results["total_processed"] += len(category_results)
                
            except Exception as e:
                error_info = {
                    "category": category_name,
                    "error": str(e)
                }
                results["failed"].append(error_info)
                
        return results
        
    async def generate_educational_assets(self, force_rebuild: bool = False) -> Dict[str, Any]:
        """Generate all educational RPG assets."""
        
        results = {
            "characters": [],
            "environments": [],
            "ui_elements": [],
            "failed": []
        }
        
        # Check if assets already exist
        game_dir = Path("src/ai_game_dev/education/generated_game")
        assets_dir = game_dir / "assets"
        
        if not force_rebuild and self._check_educational_assets_complete(assets_dir):
            results["skipped"] = ["Educational assets already exist"]
            return results
            
        # Ensure directories exist
        sprites_dir = assets_dir / "sprites"
        tilesets_dir = assets_dir / "tilesets"
        ui_dir = assets_dir / "ui"
        
        sprites_dir.mkdir(parents=True, exist_ok=True)
        tilesets_dir.mkdir(parents=True, exist_ok=True)
        ui_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            # Generate character sprites
            character_requests = self._create_character_asset_requests()
            character_assets = await self.asset_generator.generate_batch(character_requests)
            
            for i, asset in enumerate(character_assets):
                if not isinstance(asset, Exception) and asset.data:
                    filename = f"{character_requests[i].description.lower().replace(' ', '_')}.png"
                    sprite_path = sprites_dir / filename
                    
                    with open(sprite_path, "wb") as f:
                        f.write(asset.data)
                        
                    results["characters"].append(str(sprite_path))
                    
            # Generate environment tilesets
            environment_requests = self._create_environment_asset_requests()
            environment_assets = await self.asset_generator.generate_batch(environment_requests)
            
            for i, asset in enumerate(environment_assets):
                if not isinstance(asset, Exception) and asset.data:
                    filename = f"{environment_requests[i].description.lower().replace(' ', '_')}.png"
                    tileset_path = tilesets_dir / filename
                    
                    with open(tileset_path, "wb") as f:
                        f.write(asset.data)
                        
                    results["environments"].append(str(tileset_path))
                    
            # Generate UI elements
            ui_requests = self._create_ui_asset_requests()
            ui_assets = await self.asset_generator.generate_batch(ui_requests)
            
            for i, asset in enumerate(ui_assets):
                if not isinstance(asset, Exception) and asset.data:
                    filename = f"{ui_requests[i].description.lower().replace(' ', '_')}.png"
                    ui_path = ui_dir / filename
                    
                    with open(ui_path, "wb") as f:
                        f.write(asset.data)
                        
                    results["ui_elements"].append(str(ui_path))
                    
        except Exception as e:
            results["failed"].append({
                "task": "educational_assets",
                "error": str(e)
            })
            
        return results
        
    async def _generate_asset_category(self, category: str, category_data: Dict[str, Any]) -> List[str]:
        """Generate assets for a specific category."""
        
        prompts = category_data.get("prompts", [])
        size = category_data.get("size", "512x512")
        category_type = category_data.get("category", "ui_controls")
        
        # Determine asset type based on category
        if "character" in category_type or "rpg" in category_type:
            asset_type = "sprite"
        elif "environment" in category_type or "tileset" in category_type:
            asset_type = "tileset"
        else:
            asset_type = "ui_icon"
        
        # Convert prompts to asset requests
        requests = []
        for prompt in prompts:
            if asset_type == "tileset":
                request = AssetRequest(
                    asset_type=asset_type,
                    description=prompt,
                    style="cyberpunk futuristic",
                    format="PNG",
                    additional_params={"tile_size": 32, "grid_size": (8, 8)}
                )
            else:
                request = AssetRequest(
                    asset_type=asset_type,
                    description=prompt,
                    style="cyberpunk futuristic",
                    dimensions=self._parse_size(size),
                    format="PNG"
                )
            requests.append(request)
            
        # Generate assets in batch
        assets = await self.asset_generator.generate_batch(requests)
        
        # Save generated assets to appropriate directories
        if "character" in category_type or "rpg" in category_type:
            output_dir = Path("src/ai_game_dev/education/generated_game/assets/sprites")
        elif "environment" in category_type:
            output_dir = Path("src/ai_game_dev/education/generated_game/assets/tilesets")
        else:
            output_dir = Path("src/ai_game_dev/server/static/assets/generated")
            
        output_dir.mkdir(parents=True, exist_ok=True)
        
        generated_files = []
        
        for i, asset in enumerate(assets):
            if not isinstance(asset, Exception) and asset.data:
                # Create descriptive filename
                prompt_words = prompts[i].split()[:3]  # First 3 words
                filename = f"{'_'.join(prompt_words).lower()}_{category}_{i+1}.png"
                # Clean filename
                filename = ''.join(c for c in filename if c.isalnum() or c in '._-')
                file_path = output_dir / filename
                
                with open(file_path, "wb") as f:
                    f.write(asset.data)
                    
                generated_files.append(str(file_path))
                
        return generated_files
        
    def _create_character_asset_requests(self) -> List[AssetRequest]:
        """Create asset requests for educational character sprites."""
        
        characters = [
            "Professor Pixel cyberpunk mentor with neon hair and AR glasses",
            "Code Knight cybernetic warrior with plasma sword",
            "Data Sage mystical hacker with holographic robes",
            "Bug Hunter agile cyber-assassin with stealth cloak",
            "Web Weaver digital architect with quantum tablet"
        ]
        
        requests = []
        for char_desc in characters:
            request = AssetRequest(
                asset_type="sprite",
                description=f"{char_desc}, 64x64 pixel art",
                style="cyberpunk pixel art",
                dimensions=(64, 64),
                format="PNG"
            )
            requests.append(request)
            
        return requests
        
    def _create_environment_asset_requests(self) -> List[AssetRequest]:
        """Create asset requests for educational environment tilesets."""
        
        environments = [
            "NeoTokyo Code Academy exterior cyberpunk school building",
            "Underground programming lab rebel coding classroom",
            "Algorithm Tower corporate data center interior"
        ]
        
        requests = []
        for env_desc in environments:
            request = AssetRequest(
                asset_type="tileset",
                description=f"{env_desc}, 16-bit isometric pixel art",
                style="cyberpunk pixel art",
                format="PNG",
                additional_params={"tile_size": 32, "grid_size": (8, 8)}
            )
            requests.append(request)
            
        return requests
        
    def _create_ui_asset_requests(self) -> List[AssetRequest]:
        """Create asset requests for educational UI elements."""
        
        ui_elements = [
            "Code learning progress bar cyberpunk style with skill points",
            "XP gain notification popup cyberpunk design",
            "Lesson complete badge cyberpunk achievement icon"
        ]
        
        requests = []
        for ui_desc in ui_elements:
            request = AssetRequest(
                asset_type="ui_icon",
                description=f"{ui_desc}, transparent background",
                style="cyberpunk futuristic",
                dimensions=(256, 256),
                format="PNG"
            )
            requests.append(request)
            
        return requests
        
    def _check_static_assets_complete(self, assets_dir: Path) -> bool:
        """Check if static platform assets are complete."""
        required_dirs = [
            "logos", "engine-panels", "audio", "fonts", 
            "textures", "frames", "characters", "generated"
        ]
        
        for dir_name in required_dirs:
            dir_path = assets_dir / dir_name
            if not dir_path.exists() or not any(dir_path.iterdir()):
                return False
                
        return True
        
    def _check_educational_assets_complete(self, assets_dir: Path) -> bool:
        """Check if educational assets are complete."""
        required_dirs = ["sprites", "tilesets"]
        
        for dir_name in required_dirs:
            dir_path = assets_dir / dir_name
            if not dir_path.exists() or not any(dir_path.iterdir()):
                return False
                
        return True
        
    def _parse_size(self, size_str: str) -> tuple:
        """Parse size string like '512x512' into tuple."""
        if 'x' in size_str:
            width, height = size_str.split('x')
            return (int(width), int(height))
        else:
            size = int(size_str)
            return (size, size)
            
    async def _tool_execution_node(self, state: Any) -> Any:
        """Execute asset generation tools based on the task context."""
        
        # Get task context
        context = state.context or {}
        asset_type = context.get("asset_type", "")
        force_rebuild = context.get("force_rebuild", False)
        
        try:
            if asset_type == "static_platform":
                # Generate all static platform assets
                results = await self.generate_all_static_assets(force_rebuild)
                state.outputs.update({
                    "assets_created": len(results.get("generated", [])),
                    "assets_skipped": len(results.get("skipped", [])),
                    "assets_failed": len(results.get("failed", [])),
                    "details": results
                })
                
            elif asset_type == "educational_game_assets":
                # Generate educational RPG assets
                results = await self.generate_educational_assets(force_rebuild)
                state.outputs.update({
                    "assets_created": len(results.get("characters", [])) + len(results.get("environments", [])) + len(results.get("ui_elements", [])),
                    "details": results
                })
                
            elif asset_type == "educational_game_code":
                # Generate educational game code
                results = await self.generate_educational_game_code(force_rebuild)
                state.outputs.update({
                    "code_files_created": len(results.get("files", [])),
                    "details": results
                })
                
            elif asset_type == "test_ui_icon":
                # Generate single test asset
                request = AssetRequest(
                    asset_type="ui_icon",
                    description="cyberpunk play button for testing",
                    style="cyberpunk futuristic",
                    dimensions=(256, 256),
                    format="PNG"
                )
                
                asset = await self.asset_generator.generate_ui_icon(request)
                
                # Save test asset
                test_dir = Path("generated_assets/test")
                test_dir.mkdir(parents=True, exist_ok=True)
                test_path = test_dir / "test_play_button.png"
                
                if asset.data:
                    with open(test_path, "wb") as f:
                        f.write(asset.data)
                    
                    state.outputs.update({
                        "test_asset_created": str(test_path),
                        "asset_size": len(asset.data)
                    })
                
            else:
                state.errors.append(f"Unknown asset type: {asset_type}")
                
        except Exception as e:
            state.errors.append(f"Tool execution error: {str(e)}")
            
        return state
        
    async def generate_educational_game_code(self, force_rebuild: bool = False) -> Dict[str, Any]:
        """Generate the complete educational RPG game code."""
        
        results = {
            "files": [],
            "failed": []
        }
        
        # Check if game code already exists
        game_dir = Path("src/ai_game_dev/education/generated_game")
        
        if not force_rebuild and self._check_educational_rpg_complete(game_dir):
            results["skipped"] = ["Educational game code already exists"]
            return results
            
        # Ensure directories exist
        game_dir.mkdir(parents=True, exist_ok=True)
        
        try:
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
        
    def _check_educational_rpg_complete(self, game_dir: Path) -> bool:
        """Check if educational RPG code is complete."""
        required_files = ["main.py", "game.py", "player.py", "requirements.txt"]
        
        for filename in required_files:
            file_path = game_dir / filename
            if not file_path.exists() or file_path.stat().st_size < 100:
                return False
                
        return True
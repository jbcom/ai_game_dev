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

from ai_game_dev.agents.base_agent import PygameAgent, AgentConfig
from ai_game_dev.assets.generator import AssetGenerator, AssetRequest


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
            with open(spec_path, 'r') as f:
                self.asset_specification = toml.load(f)
        else:
            raise FileNotFoundError(f"Asset specification not found: {spec_path}")
            
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
        quality = category_data.get("quality", "hd")
        
        # Convert prompts to asset requests
        requests = []
        for prompt in prompts:
            request = AssetRequest(
                asset_type="ui_icon",  # Most platform assets are UI icons
                description=prompt,
                style="cyberpunk futuristic",
                dimensions=self._parse_size(size),
                format="PNG"
            )
            requests.append(request)
            
        # Generate assets in batch
        assets = await self.asset_generator.generate_batch(requests)
        
        # Save generated assets
        output_dir = Path("src/ai_game_dev/server/static/assets/generated")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        generated_files = []
        
        for i, asset in enumerate(assets):
            if not isinstance(asset, Exception) and asset.data:
                # Create filename from category and index
                filename = f"{category}_{i+1}_{hash(prompts[i]) % 10000000000000000000}.png"
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
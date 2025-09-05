"""Bevy-specific asset generation and management."""

import asyncio
import json
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from enum import Enum

import aiofiles
from openai import AsyncOpenAI
from PIL import Image, ImageDraw
import math

from openai_mcp_server.config import settings
from openai_mcp_server.logging_config import get_logger
from openai_mcp_server.models import ImageSize, GenerationResult
from openai_mcp_server.utils import ensure_directory_exists

logger = get_logger(__name__, component="bevy_assets")


class BevyAssetType(str, Enum):
    """Bevy-specific asset types."""
    SPRITE_2D = "sprite_2d"
    TILEMAP = "tilemap"
    UI_ELEMENT = "ui_element"
    PARTICLE_TEXTURE = "particle_texture"
    SKYBOX = "skybox"
    ENVIRONMENT_MAP = "environment_map"
    NORMAL_MAP = "normal_map"
    ROUGHNESS_MAP = "roughness_map"
    METALLIC_MAP = "metallic_map"
    EMISSION_MAP = "emission_map"
    SPRITE_ATLAS = "sprite_atlas"


class BevyMaterialType(str, Enum):
    """Bevy material system types."""
    STANDARD_MATERIAL = "standard"
    UNLIT_MATERIAL = "unlit"
    SPRITE_MATERIAL = "sprite"
    UI_MATERIAL = "ui"
    CUSTOM_MATERIAL = "custom"


class BevyAssetSpec:
    """Specification for Bevy-compatible assets."""
    
    def __init__(
        self,
        asset_type: BevyAssetType,
        name: str,
        description: str,
        size: ImageSize = "1024x1024",
        material_type: BevyMaterialType = BevyMaterialType.STANDARD_MATERIAL,
        tile_size: Optional[Tuple[int, int]] = None,
        atlas_layout: Optional[Tuple[int, int]] = None,
        animation_frames: int = 1,
        seamless: bool = False,
        transparent: bool = False,
        game_style: str = "fantasy",
        bevy_components: Optional[List[str]] = None
    ):
        self.asset_type = asset_type
        self.name = name
        self.description = description
        self.size = size
        self.material_type = material_type
        self.tile_size = tile_size
        self.atlas_layout = atlas_layout
        self.animation_frames = animation_frames
        self.seamless = seamless
        self.transparent = transparent
        self.game_style = game_style
        self.bevy_components = bevy_components or []
        self.id = str(uuid.uuid4())


class BevyAssetGenerator:
    """Specialized Bevy asset generator with proper subpackage integration."""
    
    def __init__(self, openai_client: AsyncOpenAI):
        self.client = openai_client
        self.assets_dir = settings.cache_dir / "bevy_assets"
        
    async def initialize(self):
        """Initialize the Bevy asset generator."""
        await ensure_directory_exists(self.assets_dir)
        await ensure_directory_exists(self.assets_dir / "sprites")
        await ensure_directory_exists(self.assets_dir / "tilemaps")
        await ensure_directory_exists(self.assets_dir / "ui")
        await ensure_directory_exists(self.assets_dir / "materials")
        await ensure_directory_exists(self.assets_dir / "atlases")
    
    async def generate_bevy_asset(self, spec: BevyAssetSpec) -> GenerationResult:
        """Generate a Bevy-compatible asset based on specification."""
        
        try:
            logger.info(f"Generating Bevy {spec.asset_type.value} asset: {spec.name}")
            
            # Route to appropriate generation method
            if spec.asset_type == BevyAssetType.SPRITE_2D:
                return await self._generate_sprite_2d(spec)
            elif spec.asset_type == BevyAssetType.TILEMAP:
                return await self._generate_tilemap(spec)
            elif spec.asset_type == BevyAssetType.UI_ELEMENT:
                return await self._generate_ui_element(spec)
            elif spec.asset_type == BevyAssetType.PARTICLE_TEXTURE:
                return await self._generate_particle_texture(spec)
            elif spec.asset_type == BevyAssetType.SPRITE_ATLAS:
                return await self._generate_sprite_atlas(spec)
            else:
                return await self._generate_material_map(spec)
                
        except Exception as e:
            logger.error(f"Bevy asset generation failed: {e}")
            raise
    
    async def _generate_sprite_2d(self, spec: BevyAssetSpec) -> GenerationResult:
        """Generate a 2D sprite for Bevy."""
        
        # Enhanced prompt for Bevy sprite generation
        enhanced_prompt = self._create_bevy_sprite_prompt(spec)
        
        # Generate image using OpenAI
        response = await self.client.images.generate(
            model="dall-e-3",
            prompt=enhanced_prompt,
            size=spec.size,
            quality="hd",
            n=1
        )
        
        # Save the asset
        sprite_path = self.assets_dir / "sprites" / f"{spec.name}.png"
        
        # In production, download and save the actual image
        # For now, create a result
        return self._create_generation_result(spec, sprite_path)
    
    async def _generate_tilemap(self, spec: BevyAssetSpec) -> GenerationResult:
        """Generate tilemap assets for Bevy."""
        
        # Define tile types for the tilemap
        tile_types = [
            {"type": "grass", "id": 0},
            {"type": "stone", "id": 1},
            {"type": "water", "id": 2},
            {"type": "dirt", "id": 3},
            {"type": "sand", "id": 4}
        ]
        
        # Create tile atlas
        atlas_path = await self._create_tile_atlas(tile_types, spec.game_style)
        
        # Generate Bevy tilemap configuration
        config = self._generate_tilemap_config(tile_types, atlas_path)
        
        # Save configuration
        config_path = self.assets_dir / "tilemaps" / f"{spec.name}_config.json"
        async with aiofiles.open(config_path, 'w') as f:
            await f.write(json.dumps(config, indent=2))
        
        result = self._create_generation_result(spec, atlas_path)
        result.metadata["tilemap_config"] = str(config_path)
        result.metadata["tile_types"] = tile_types
        
        return result
    
    async def _generate_ui_element(self, spec: BevyAssetSpec) -> GenerationResult:
        """Generate UI element for Bevy."""
        
        ui_prompt = f"""
        Create a {spec.game_style} game UI element: {spec.description}
        
        Requirements:
        - Clean, readable design
        - Appropriate for {spec.game_style} aesthetic
        - High contrast for good visibility
        - {'Transparent background' if spec.transparent else 'Solid background'}
        - Optimized for {spec.size} resolution
        """
        
        # Generate UI element
        response = await self.client.images.generate(
            model="dall-e-3",
            prompt=ui_prompt,
            size=spec.size,
            quality="hd",
            n=1
        )
        
        ui_path = self.assets_dir / "ui" / f"{spec.name}.png"
        
        return self._create_generation_result(spec, ui_path)
    
    async def _generate_particle_texture(self, spec: BevyAssetSpec) -> GenerationResult:
        """Generate particle texture for Bevy effects."""
        
        particle_prompt = f"""
        Create a particle texture for {spec.description}
        
        Requirements:
        - Single particle on transparent background
        - Suitable for particle system multiplication
        - {spec.game_style} visual style
        - High quality, crisp edges
        - Optimized for GPU rendering
        """
        
        response = await self.client.images.generate(
            model="dall-e-3",
            prompt=particle_prompt,
            size=spec.size,
            quality="hd",
            n=1
        )
        
        particle_path = self.assets_dir / "particles" / f"{spec.name}.png"
        
        return self._create_generation_result(spec, particle_path)
    
    async def _generate_sprite_atlas(self, spec: BevyAssetSpec) -> GenerationResult:
        """Generate sprite atlas for Bevy."""
        
        if not spec.atlas_layout:
            spec.atlas_layout = (4, 4)  # Default 4x4 atlas
        
        cols, rows = spec.atlas_layout
        
        # Generate individual sprites and combine into atlas
        sprites = []
        for i in range(cols * rows):
            sprite_desc = f"{spec.description} variation {i+1}"
            sprites.append({"description": sprite_desc, "index": i})
        
        atlas_path = await self._create_sprite_atlas(sprites, spec)
        
        result = self._create_generation_result(spec, atlas_path)
        result.metadata["atlas_layout"] = spec.atlas_layout
        result.metadata["sprite_count"] = len(sprites)
        
        return result
    
    async def _generate_material_map(self, spec: BevyAssetSpec) -> GenerationResult:
        """Generate material maps (normal, roughness, metallic, etc.) for Bevy."""
        
        map_type = spec.asset_type.value.replace("_map", "")
        
        material_prompt = f"""
        Generate a {map_type} map texture for {spec.description}
        
        Requirements:
        - Seamless/tileable texture
        - Appropriate for {spec.game_style} materials
        - High quality {map_type} information
        - Grayscale for single-channel maps
        - Optimized for Bevy StandardMaterial
        """
        
        response = await self.client.images.generate(
            model="dall-e-3",
            prompt=material_prompt,
            size=spec.size,
            quality="hd",
            n=1
        )
        
        material_path = self.assets_dir / "materials" / f"{spec.name}_{map_type}.png"
        
        return self._create_generation_result(spec, material_path)
    
    def _create_bevy_sprite_prompt(self, spec: BevyAssetSpec) -> str:
        """Create an enhanced prompt for Bevy sprite generation."""
        
        prompt_parts = [
            f"Create a {spec.game_style} game sprite: {spec.description}",
            f"Art style: {spec.game_style}",
            f"Resolution: {spec.size}",
        ]
        
        if spec.transparent:
            prompt_parts.append("Transparent background, PNG format")
        
        if spec.bevy_components:
            prompt_parts.append(f"Designed for Bevy components: {', '.join(spec.bevy_components)}")
        
        if spec.animation_frames > 1:
            prompt_parts.append(f"Static sprite suitable for {spec.animation_frames}-frame animation")
        
        return " | ".join(prompt_parts)
    
    async def _create_tile_atlas(self, tiles: List[Dict], theme: str) -> Path:
        """Create tile atlas from individual tiles."""
        atlas_dir = self.assets_dir / "atlases"
        await ensure_directory_exists(atlas_dir)
        atlas_path = atlas_dir / f"{theme}_tilemap_atlas.png"
        
        try:
            # Calculate atlas dimensions
            tile_count = len(tiles)
            if tile_count == 0:
                # Create minimal single-tile atlas
                atlas = Image.new('RGBA', (64, 64), (255, 255, 255, 0))
                atlas.save(atlas_path)
                return atlas_path
            
            # Calculate grid layout (square-ish)
            grid_size = math.ceil(math.sqrt(tile_count))
            tile_size = 64
            atlas_width = grid_size * tile_size
            atlas_height = grid_size * tile_size
            
            # Create atlas image
            atlas = Image.new('RGBA', (atlas_width, atlas_height), (255, 255, 255, 0))
            
            # Generate procedural tiles based on tile types
            for i, tile in enumerate(tiles):
                x = (i % grid_size) * tile_size
                y = (i // grid_size) * tile_size
                
                # Generate tile based on type
                tile_type = tile.get("type", "grass")
                tile_img = self._generate_procedural_tile(tile_type, tile_size)
                atlas.paste(tile_img, (x, y))
            
            atlas.save(atlas_path)
            return atlas_path
            
        except Exception as e:
            logger.error(f"Failed to create tile atlas: {e}")
            # Create empty file as fallback
            atlas_path.touch()
            return atlas_path
    
    def _generate_procedural_tile(self, tile_type: str, size: int) -> Image.Image:
        """Generate a procedural tile texture based on type."""
        tile = Image.new('RGBA', (size, size), (255, 255, 255, 255))
        draw = ImageDraw.Draw(tile)
        
        # Generate different patterns based on tile type
        if tile_type == "grass":
            # Green base with some texture
            tile = Image.new('RGBA', (size, size), (34, 139, 34, 255))
            # Add some noise-like pattern
            for i in range(0, size, 4):
                for j in range(0, size, 4):
                    if (i + j) % 8 == 0:
                        draw.rectangle([i, j, i+2, j+2], fill=(46, 125, 50, 255))
        
        elif tile_type == "stone":
            # Gray base with darker edges
            tile = Image.new('RGBA', (size, size), (128, 128, 128, 255))
            draw.rectangle([0, 0, size-1, size-1], outline=(64, 64, 64, 255), width=2)
        
        elif tile_type == "water":
            # Blue with wave pattern
            tile = Image.new('RGBA', (size, size), (0, 119, 190, 255))
            for i in range(0, size, 8):
                draw.line([(0, i), (size, i)], fill=(0, 150, 255, 255), width=1)
        
        elif tile_type == "dirt":
            # Brown with texture
            tile = Image.new('RGBA', (size, size), (139, 69, 19, 255))
            for i in range(0, size, 6):
                for j in range(0, size, 6):
                    draw.point((i, j), fill=(160, 82, 45, 255))
        
        else:
            # Default tile - light gray
            tile = Image.new('RGBA', (size, size), (200, 200, 200, 255))
            draw.text((size//4, size//2), tile_type[:4], fill=(0, 0, 0, 255))
        
        return tile
    
    async def _create_sprite_atlas(self, sprites: List[Dict], spec: BevyAssetSpec) -> Path:
        """Create sprite atlas from individual sprites."""
        atlas_dir = self.assets_dir / "atlases"
        await ensure_directory_exists(atlas_dir)
        atlas_path = atlas_dir / f"{spec.name}_atlas.png"
        
        cols, rows = spec.atlas_layout
        sprite_size = 64  # Individual sprite size within atlas
        atlas_width = cols * sprite_size
        atlas_height = rows * sprite_size
        
        # Create atlas image
        atlas = Image.new('RGBA', (atlas_width, atlas_height), (255, 255, 255, 0))
        
        # For now, create procedural sprite variations
        for i, sprite in enumerate(sprites):
            if i >= cols * rows:
                break
                
            x = (i % cols) * sprite_size
            y = (i // cols) * sprite_size
            
            # Generate a simple procedural sprite
            sprite_img = self._generate_procedural_sprite(sprite["description"], sprite_size, spec.game_style)
            atlas.paste(sprite_img, (x, y))
        
        atlas.save(atlas_path)
        return atlas_path
    
    def _generate_procedural_sprite(self, description: str, size: int, style: str) -> Image.Image:
        """Generate a simple procedural sprite."""
        sprite = Image.new('RGBA', (size, size), (255, 255, 255, 0))
        draw = ImageDraw.Draw(sprite)
        
        # Create a simple colored rectangle with border
        color = (hash(description) % 256, hash(style) % 256, hash(description + style) % 256, 255)
        draw.rectangle([4, 4, size-4, size-4], fill=color, outline=(0, 0, 0, 255))
        
        return sprite
    
    def _generate_tilemap_config(self, tiles: List[Dict], atlas_path: Path) -> Dict[str, Any]:
        """Generate Bevy tilemap configuration."""
        
        return {
            "atlas_path": str(atlas_path),
            "tile_size": {"x": 64, "y": 64},
            "tiles": {tile["type"]: tile["id"] for tile in tiles},
            "bevy_integration": "TiledMap compatible"
        }
    
    def _create_generation_result(self, spec: BevyAssetSpec, asset_path: Path) -> GenerationResult:
        """Create generation result with Bevy metadata."""
        
        return GenerationResult(
            id=spec.id,
            type="image",
            file_path=str(asset_path),
            metadata={
                "bevy_asset_type": spec.asset_type.value,
                "bevy_material_type": spec.material_type.value,
                "bevy_components": spec.bevy_components,
                "game_style": spec.game_style,
                "transparent": spec.transparent,
                "seamless": spec.seamless,
                "size": spec.size,
                "name": spec.name
            }
        )
"""Simplified Bevy game engine asset generation system."""

import asyncio
import json
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from enum import Enum

import aiofiles
from openai import AsyncOpenAI
from PIL import Image

from .config import settings
from .logging_config import get_logger
from .models import ImageSize, GenerationResult
from .utils import ensure_directory_exists

logger = get_logger(__name__, component="bevy_assets")


class BevyAssetType(str, Enum):
    """Bevy-specific asset types."""
    SPRITE_2D = "sprite_2d"
    TILEMAP = "tilemap"
    UI_ELEMENT = "ui_element"
    PARTICLE_TEXTURE = "particle_texture"
    PBR_MATERIAL = "pbr_material"


class BevyAssetGenerator:
    """Simplified Bevy asset generator."""
    
    def __init__(self, openai_client: AsyncOpenAI):
        self.client = openai_client
        self.assets_dir = settings.cache_dir / "bevy_assets"
        
    async def generate_sprite_2d(
        self,
        name: str,
        description: str,
        size: ImageSize = "512x512",
        transparent: bool = True,
        style: str = "pixel art",
        animation_frames: int = 1
    ) -> GenerationResult:
        """Generate 2D sprite optimized for Bevy."""
        
        prompt = f"Game sprite: {description}, {style} style, optimized for game engine"
        if transparent:
            prompt += ", transparent background"
            
        response = await self.client.images.generate(
            prompt=prompt,
            size=size,
            quality="standard",
            n=1
        )
        
        # Save asset
        asset_path = await self._save_asset(response.data[0].url, name, "sprite")
        
        return GenerationResult(
            id=str(uuid.uuid4()),
            type="image",
            file_path=str(asset_path),
            metadata={
                "bevy_asset_type": BevyAssetType.SPRITE_2D.value,
                "name": name,
                "style": style,
                "transparent": transparent,
                "animation_frames": animation_frames
            }
        )
    
    async def generate_tilemap_set(
        self,
        theme: str,
        tile_count: int = 16,
        tile_size: Tuple[int, int] = (64, 64),
        seamless: bool = True
    ) -> Dict[str, Any]:
        """Generate tilemap set for Bevy."""
        
        tiles = []
        tile_types = ["grass", "dirt", "stone", "water", "wall", "floor"]
        
        for i, tile_type in enumerate(tile_types[:tile_count]):
            prompt = f"{tile_type} tile for {theme} game, seamless tileable texture, top-down perspective"
            
            response = await self.client.images.generate(
                prompt=prompt,
                size="256x256",
                quality="standard",
                n=1
            )
            
            tile_path = await self._save_asset(response.data[0].url, f"{theme}_{tile_type}_tile", "tilemap")
            tiles.append({
                "type": tile_type,
                "path": str(tile_path),
                "id": i
            })
        
        return {
            "tilemap_name": f"{theme}_tilemap",
            "tiles": tiles,
            "tile_count": len(tiles)
        }
    
    async def _save_asset(self, image_url: str, name: str, asset_type: str) -> Path:
        """Save asset with proper structure."""
        
        asset_dir = self.assets_dir / asset_type
        await ensure_directory_exists(asset_dir)
        
        asset_path = asset_dir / f"{name}.png"
        
        import aiohttp
        async with aiohttp.ClientSession() as session:
            async with session.get(image_url) as response:
                if response.status == 200:
                    async with aiofiles.open(asset_path, 'wb') as f:
                        await f.write(await response.read())
        
        return asset_path
"""
Production Asset Generator using OpenAI's latest image generation capabilities.
Supports single generation, batch processing, variants, and masked edits.
"""

import asyncio
import base64
import os
from pathlib import Path
from typing import Dict, List, Optional, Any, Literal
from dataclasses import dataclass, field

import aiofiles
from openai import AsyncOpenAI


@dataclass
class AssetRequest:
    """Request for asset generation."""
    asset_type: str
    description: str
    style: str = "modern"
    dimensions: Optional[tuple[int, int]] = None
    format: str = "PNG"
    additional_params: Dict[str, Any] = field(default_factory=dict)


@dataclass
class GeneratedAsset:
    """Generated asset with data and metadata."""
    asset_type: str
    description: str
    data: Optional[bytes] = None
    file_path: Optional[Path] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class AssetGenerator:
    """Production asset generator using OpenAI's image generation capabilities."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.client = AsyncOpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
        self.cache_dir = Path("generated_assets")
        self.cache_dir.mkdir(exist_ok=True)
        
    async def __aenter__(self):
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.close()

    async def generate_sprite(self, request: AssetRequest) -> GeneratedAsset:
        """Generate a game sprite using OpenAI image generation."""
        dimensions = request.dimensions or (64, 64)
        
        prompt = self._create_sprite_prompt(request.description, request.style, dimensions)
        
        image_data = await self._generate_image(
            prompt=prompt,
            size=self._get_openai_size(dimensions),
            style="vivid" if "cyberpunk" in request.style.lower() else "natural"
        )
        
        return GeneratedAsset(
            asset_type="sprite",
            description=request.description,
            data=image_data,
            metadata={
                "dimensions": dimensions,
                "style": request.style,
                "format": request.format,
                "prompt": prompt
            }
        )

    async def generate_tileset(self, request: AssetRequest) -> GeneratedAsset:
        """Generate a tileset for backgrounds."""
        tile_size = request.additional_params.get("tile_size", 32)
        grid_size = request.additional_params.get("grid_size", (8, 8))
        
        prompt = self._create_tileset_prompt(request.description, request.style, tile_size, grid_size)
        
        tileset_data = await self._generate_image(
            prompt=prompt,
            size="1024x1024",
            style="vivid" if "cyberpunk" in request.style.lower() else "natural"
        )
        
        return GeneratedAsset(
            asset_type="tileset",
            description=request.description,
            data=tileset_data,
            metadata={
                "tile_size": tile_size,
                "grid_size": grid_size,
                "style": request.style,
                "format": request.format,
                "prompt": prompt
            }
        )

    async def generate_ui_icon(self, request: AssetRequest) -> GeneratedAsset:
        """Generate UI icons using OpenAI image generation."""
        dimensions = request.dimensions or (256, 256)
        
        prompt = self._create_ui_icon_prompt(request.description, request.style, dimensions)
        
        icon_data = await self._generate_image(
            prompt=prompt,
            size=self._get_openai_size(dimensions),
            style="vivid" if "cyberpunk" in request.style.lower() else "natural"
        )
        
        return GeneratedAsset(
            asset_type="ui_icon",
            description=request.description,
            data=icon_data,
            metadata={
                "dimensions": dimensions,
                "style": request.style,
                "format": request.format,
                "prompt": prompt
            }
        )

    async def generate_image_variant(self, base_image_data: bytes, request: AssetRequest) -> GeneratedAsset:
        """Generate variants of an existing image."""
        
        temp_path = self.cache_dir / "temp_base.png"
        async with aiofiles.open(temp_path, "wb") as f:
            await f.write(base_image_data)
            
        try:
            with open(temp_path, "rb") as image_file:
                response = await self.client.images.create_variation(
                    image=image_file,
                    n=1,
                    size=request.additional_params.get("size", "1024x1024"),
                    response_format="b64_json"
                )
                
            if response.data and response.data[0].b64_json:
                variant_data = base64.b64decode(response.data[0].b64_json)
            else:
                raise RuntimeError("No variant data returned from OpenAI")
            
            return GeneratedAsset(
                asset_type="variant",
                description=f"Variant of: {request.description}",
                data=variant_data,
                metadata={
                    "base_description": request.description,
                    "style": request.style,
                    "format": request.format
                }
            )
            
        finally:
            if temp_path.exists():
                temp_path.unlink()

    async def generate_masked_edit(self, base_image_data: bytes, mask_data: bytes, request: AssetRequest) -> GeneratedAsset:
        """Generate targeted edits using image masks."""
        
        temp_base = self.cache_dir / "temp_base.png"
        temp_mask = self.cache_dir / "temp_mask.png"
        
        async with aiofiles.open(temp_base, "wb") as f:
            await f.write(base_image_data)
        async with aiofiles.open(temp_mask, "wb") as f:
            await f.write(mask_data)
            
        try:
            with open(temp_base, "rb") as image_file, open(temp_mask, "rb") as mask_file:
                response = await self.client.images.edit(
                    image=image_file,
                    mask=mask_file,
                    prompt=request.description,
                    n=1,
                    size=request.additional_params.get("size", "1024x1024"),
                    response_format="b64_json"
                )
                
            if response.data and response.data[0].b64_json:
                edited_data = base64.b64decode(response.data[0].b64_json)
            else:
                raise RuntimeError("No edited data returned from OpenAI")
            
            return GeneratedAsset(
                asset_type="masked_edit",
                description=request.description,
                data=edited_data,
                metadata={
                    "edit_prompt": request.description,
                    "style": request.style,
                    "format": request.format
                }
            )
            
        finally:
            if temp_base.exists():
                temp_base.unlink()
            if temp_mask.exists():
                temp_mask.unlink()

    async def generate_batch(self, requests: List[AssetRequest]) -> List[GeneratedAsset]:
        """Generate multiple assets in batch with concurrency control."""
        
        async def generate_single(request: AssetRequest) -> GeneratedAsset:
            if request.asset_type == "sprite":
                return await self.generate_sprite(request)
            elif request.asset_type == "tileset":
                return await self.generate_tileset(request)
            elif request.asset_type == "ui_icon":
                return await self.generate_ui_icon(request)
            else:
                raise ValueError(f"Unsupported asset type: {request.asset_type}")
                
        # Process in batches to respect rate limits
        batch_size = 5
        results = []
        
        for i in range(0, len(requests), batch_size):
            batch = requests[i:i + batch_size]
            batch_results = await asyncio.gather(
                *[generate_single(req) for req in batch],
                return_exceptions=True
            )
            results.extend(batch_results)
            
            # Small delay between batches to respect rate limits
            if i + batch_size < len(requests):
                await asyncio.sleep(2)
                
        return results

    async def _generate_image(
        self, 
        prompt: str, 
        size: Literal["256x256", "512x512", "1024x1024", "1024x1792", "1792x1024"] = "1024x1024",
        style: Literal["vivid", "natural"] = "natural"
    ) -> bytes:
        """Core image generation using OpenAI DALL-E 3."""
        
        try:
            response = await self.client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size=size,
                quality="hd",
                style=style,
                n=1,
                response_format="b64_json"
            )
            
            if response.data and response.data[0].b64_json:
                return base64.b64decode(response.data[0].b64_json)
            else:
                raise RuntimeError("No image data returned from OpenAI")
            
        except Exception as e:
            raise RuntimeError(f"Failed to generate image: {e}")

    def _create_sprite_prompt(self, description: str, style: str, dimensions: tuple) -> str:
        """Create optimized prompt for sprite generation."""
        return (
            f"{description}, {style} style, {dimensions[0]}x{dimensions[1]} pixel art sprite, "
            f"transparent background, game asset, high quality, detailed, "
            f"suitable for 2D game development, centered composition"
        )
        
    def _create_tileset_prompt(self, description: str, style: str, tile_size: int, grid_size: tuple) -> str:
        """Create optimized prompt for tileset generation."""
        return (
            f"{description}, {style} style, seamless tileable pattern, "
            f"{tile_size}px tiles in {grid_size[0]}x{grid_size[1]} grid, "
            f"game tileset, environment asset, high quality, detailed, "
            f"suitable for 2D game backgrounds, repeatable pattern"
        )
        
    def _create_ui_icon_prompt(self, description: str, style: str, dimensions: tuple) -> str:
        """Create optimized prompt for UI icon generation."""
        return (
            f"{description}, {style} style, {dimensions[0]}x{dimensions[1]} UI icon, "
            f"transparent background, clean design, high contrast, "
            f"user interface element, game UI, vector-style, minimalist"
        )
        
    def _get_openai_size(self, dimensions: tuple) -> Literal["256x256", "512x512", "1024x1024", "1024x1792", "1792x1024"]:
        """Convert dimensions to OpenAI supported sizes."""
        width, height = dimensions
        
        # Map to closest supported OpenAI size
        if width <= 256 and height <= 256:
            return "256x256"
        elif width <= 512 and height <= 512:
            return "512x512"
        elif width > height:
            return "1792x1024"
        elif height > width:
            return "1024x1792"
        else:
            return "1024x1024"
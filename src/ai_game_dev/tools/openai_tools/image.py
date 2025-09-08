"""
OpenAI image generation tools for game assets.
Uses GPT-Image-1 (DALL-E 3) for high-quality game art generation.
"""
from pathlib import Path
from typing import Literal

import aiofiles
import httpx
from openai import AsyncOpenAI
from pydantic import BaseModel, Field

from agents import function_tool


class ImageGenerationParams(BaseModel):
    """Parameters for image generation."""
    prompt: str = Field(description="Detailed description of the image to generate")
    style: Literal["natural", "vivid"] = Field(default="vivid", description="Image style")
    quality: Literal["standard", "hd"] = Field(default="hd", description="Image quality")
    size: Literal["1024x1024", "1792x1024", "1024x1792"] = Field(
        default="1024x1024", 
        description="Image dimensions"
    )


class GeneratedImage(BaseModel):
    """Result of image generation."""
    url: str
    revised_prompt: str
    local_path: str | None = None


@function_tool
async def generate_game_asset(
    asset_type: Literal["sprite", "background", "ui", "icon"],
    description: str,
    art_style: str = "pixel art",
    size: Literal["1024x1024", "1792x1024", "1024x1792"] = "1024x1024",
    save_path: str | None = None,
) -> GeneratedImage:
    """Generate a game asset using DALL-E 3."""
    client = AsyncOpenAI()
    
    # Build detailed prompt based on asset type
    prompts = {
        "sprite": f"Game sprite of {description}, {art_style} style, transparent background, suitable for 2D games",
        "background": f"Game background: {description}, {art_style} style, seamless and tileable",
        "ui": f"Game UI element: {description}, {art_style} style, clean and modern game interface",
        "icon": f"Game icon: {description}, {art_style} style, clear and recognizable at small sizes"
    }
    
    prompt = prompts.get(asset_type, f"Game asset: {description}, {art_style} style")
    
    response = await client.images.generate(
        model="gpt-image-1",  # Using the latest image model
        prompt=prompt,
        size=size,
        quality="hd",
        style="vivid",
        n=1
    )
    
    image_url = response.data[0].url
    revised_prompt = response.data[0].revised_prompt
    
    # Download and save if path provided
    local_path = None
    if save_path:
        local_path = await _download_image(image_url, save_path)
    
    return GeneratedImage(
        url=image_url,
        revised_prompt=revised_prompt,
        local_path=str(local_path) if local_path else None
    )


@function_tool
async def generate_character_sprite(
    character_name: str,
    character_description: str,
    pose: str = "idle",
    art_style: str = "pixel art",
    save_path: str | None = None,
) -> GeneratedImage:
    """Generate a character sprite for games."""
    prompt = (
        f"Character sprite sheet of {character_name}: {character_description}, "
        f"showing {pose} pose, {art_style} style, transparent background, "
        f"suitable for 2D game animation, consistent character design"
    )
    
    return await generate_game_asset(
        asset_type="sprite",
        description=prompt,
        art_style=art_style,
        save_path=save_path
    )


@function_tool
async def generate_environment(
    environment_name: str,
    description: str,
    time_of_day: Literal["day", "night", "sunset", "dawn"] = "day",
    art_style: str = "pixel art",
    save_path: str | None = None,
) -> GeneratedImage:
    """Generate an environment/background for games."""
    prompt = (
        f"Game environment {environment_name}: {description}, "
        f"{time_of_day} lighting, {art_style} style, "
        f"suitable for 2D platformer or RPG game"
    )
    
    return await generate_game_asset(
        asset_type="background",
        description=prompt,
        art_style=art_style,
        size="1792x1024",  # Wide format for backgrounds
        save_path=save_path
    )


@function_tool  
async def generate_ui_element(
    element_type: Literal["button", "panel", "health_bar", "menu", "dialog_box"],
    theme: str = "cyberpunk",
    description: str = "",
    save_path: str | None = None,
) -> GeneratedImage:
    """Generate UI elements for games."""
    ui_descriptions = {
        "button": f"{theme} game button, glowing edges, interactive feel",
        "panel": f"{theme} UI panel, semi-transparent with borders",
        "health_bar": f"{theme} health/energy bar, dynamic and futuristic",
        "menu": f"{theme} game menu interface, clean and modern",
        "dialog_box": f"{theme} dialogue box for RPG games, readable and stylish"
    }
    
    full_description = ui_descriptions.get(element_type, element_type)
    if description:
        full_description += f", {description}"
    
    return await generate_game_asset(
        asset_type="ui",
        description=full_description,
        art_style=f"{theme} UI design",
        save_path=save_path
    )


async def _download_image(url: str, save_path: str) -> Path:
    """Download image from URL and save locally."""
    path = Path(save_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()
        
        async with aiofiles.open(path, 'wb') as f:
            await f.write(response.content)
    
    return path
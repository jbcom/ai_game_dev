"""
OpenAI function tools for graphics and image generation.
Integrates GPT-Image-1, CC0 libraries, and Pillow processing.
"""
from pathlib import Path
from typing import Literal, Any
from PIL import Image

import aiofiles
import httpx
from openai import AsyncOpenAI
from pydantic import BaseModel

from agents import function_tool

from ai_game_dev.constants import OPENAI_MODELS
from ai_game_dev.graphics.cc0_libraries import CC0Libraries
from ai_game_dev.graphics.image_processor import ImageProcessor


class GeneratedImage(BaseModel):
    """Result of image generation."""
    type: str
    description: str
    path: str | None
    size: tuple[int, int]
    url: str | None = None


@function_tool
async def generate_sprite(
    object_name: str,
    art_style: Literal["pixel", "cartoon", "realistic", "minimalist", "hand-drawn"] = "pixel",
    size: Literal["32x32", "64x64", "128x128", "256x256"] = "64x64",
    animation_frames: int = 1,
    color_palette: str | None = None,
    save_path: str | None = None,
) -> GeneratedImage:
    """Generate a game sprite using DALL-E 3 (GPT-Image-1).
    
    Args:
        object_name: Name/description of the sprite (character, enemy, item, etc.)
        art_style: Visual style for the sprite
        size: Sprite dimensions
        animation_frames: Number of animation frames (if >1, creates sprite sheet)
        color_palette: Optional color palette constraint
        save_path: Optional path to save the sprite
        
    Returns:
        GeneratedImage with file path and metadata
    """
    client = AsyncOpenAI()
    
    # Build the prompt
    prompt = f"Game sprite: {object_name}, {art_style} art style"
    
    if animation_frames > 1:
        prompt += f", sprite sheet with {animation_frames} frames showing animation sequence"
    else:
        prompt += ", single sprite on transparent background"
    
    if color_palette:
        prompt += f", using {color_palette} color palette"
    
    prompt += f", clean edges, suitable for {size} game resolution"
    
    # DALL-E 3 only supports specific sizes, so we'll generate at 1024x1024 and note the target size
    response = await client.images.generate(
        model=OPENAI_MODELS["image"]["default"],  # GPT-Image-1
        prompt=prompt,
        size="1024x1024",
        quality="hd",
        style="vivid",
        n=1
    )
    
    image_url = response.data[0].url
    
    # Parse the target size
    width, height = map(int, size.split('x'))
    
    # Download and save if path provided
    if save_path:
        path = Path(save_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        async with httpx.AsyncClient() as http_client:
            img_response = await http_client.get(image_url)
            img_response.raise_for_status()
            
            async with aiofiles.open(path, 'wb') as f:
                await f.write(img_response.content)
        
        return GeneratedImage(
            type="sprite",
            description=f"{art_style} sprite of {object_name}",
            path=str(path),
            size=(width, height),
            url=image_url
        )
    
    return GeneratedImage(
        type="sprite",
        description=f"{art_style} sprite of {object_name}",
        path=None,
        size=(width, height),
        url=image_url
    )


@function_tool
async def generate_tileset(
    environment: str,
    tile_size: Literal["16x16", "32x32", "64x64"] = "32x32",
    art_style: Literal["pixel", "cartoon", "realistic", "minimalist"] = "pixel",
    tile_types: list[str] | None = None,
    save_path: str | None = None,
) -> GeneratedImage:
    """Generate a tileset for level design.
    
    Args:
        environment: Environment theme (forest, dungeon, city, space, etc.)
        tile_size: Size of individual tiles
        art_style: Visual style
        tile_types: Specific tiles needed (wall, floor, corner, etc.)
        save_path: Optional save path
        
    Returns:
        GeneratedImage with tileset
    """
    client = AsyncOpenAI()
    
    # Build comprehensive prompt
    prompt = f"Game tileset for {environment} environment, {art_style} art style"
    prompt += f", grid of {tile_size} tiles"
    
    if tile_types:
        prompt += f", including tiles for: {', '.join(tile_types)}"
    else:
        prompt += ", including floor, wall, corner, and decoration tiles"
    
    prompt += ", seamless tiling, consistent style, organized grid layout"
    
    response = await client.images.generate(
        model=OPENAI_MODELS["image"]["default"],
        prompt=prompt,
        size="1024x1024",
        quality="hd",
        style="vivid",
        n=1
    )
    
    image_url = response.data[0].url
    tile_width, tile_height = map(int, tile_size.split('x'))
    
    if save_path:
        path = Path(save_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        async with httpx.AsyncClient() as http_client:
            img_response = await http_client.get(image_url)
            img_response.raise_for_status()
            
            async with aiofiles.open(path, 'wb') as f:
                await f.write(img_response.content)
        
        return GeneratedImage(
            type="tileset",
            description=f"{environment} tileset with {tile_size} tiles",
            path=str(path),
            size=(1024, 1024),
            url=image_url
        )
    
    return GeneratedImage(
        type="tileset",
        description=f"{environment} tileset with {tile_size} tiles",
        path=None,
        size=(1024, 1024),
        url=image_url
    )


@function_tool
async def generate_background(
    scene: str,
    style: Literal["pixel", "painted", "cartoon", "realistic", "abstract"] = "painted",
    time_of_day: Literal["day", "night", "sunset", "dawn"] = "day",
    layers: int = 1,
    resolution: Literal["1920x1080", "1280x720", "800x600"] = "1920x1080",
    save_path: str | None = None,
) -> GeneratedImage:
    """Generate a game background or environment.
    
    Args:
        scene: Scene description (forest, city skyline, space station, etc.)
        style: Art style
        time_of_day: Lighting/time setting
        layers: Number of parallax layers (1-3)
        resolution: Target resolution
        save_path: Optional save path
        
    Returns:
        GeneratedImage with background
    """
    client = AsyncOpenAI()
    
    # Build detailed prompt
    prompt = f"Game background: {scene} during {time_of_day}, {style} art style"
    
    if layers > 1:
        prompt += f", suitable for {layers}-layer parallax scrolling"
        prompt += ", clear depth separation between foreground and background elements"
    
    prompt += f", optimized for {resolution} display"
    prompt += ", atmospheric and immersive"
    
    # DALL-E 3 supports landscape format
    response = await client.images.generate(
        model=OPENAI_MODELS["image"]["default"],
        prompt=prompt,
        size="1792x1024",  # Landscape format
        quality="hd",
        style="vivid",
        n=1
    )
    
    image_url = response.data[0].url
    
    if save_path:
        path = Path(save_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        async with httpx.AsyncClient() as http_client:
            img_response = await http_client.get(image_url)
            img_response.raise_for_status()
            
            async with aiofiles.open(path, 'wb') as f:
                await f.write(img_response.content)
        
        return GeneratedImage(
            type="background",
            description=f"{scene} background at {time_of_day}",
            path=str(path),
            size=(1792, 1024),
            url=image_url
        )
    
    return GeneratedImage(
        type="background",
        description=f"{scene} background at {time_of_day}",
        path=None,
        size=(1792, 1024),
        url=image_url
    )


@function_tool
async def generate_ui_elements(
    ui_theme: str,
    elements: list[str],
    style: Literal["flat", "glass", "neon", "retro", "minimalist"] = "flat",
    color_scheme: str | None = None,
    save_path: str | None = None,
) -> list[GeneratedImage]:
    """Generate UI elements for game interface.
    
    Args:
        ui_theme: Overall theme (sci-fi, fantasy, modern, etc.)
        elements: List of UI elements needed (button, panel, health_bar, etc.)
        style: Visual style for UI
        color_scheme: Optional color scheme
        save_path: Optional base path for saving (elements saved as separate files)
        
    Returns:
        List of GeneratedImage for each UI element
    """
    client = AsyncOpenAI()
    results = []
    
    for element in elements:
        # Build element-specific prompt
        prompt = f"Game UI element: {element}, {ui_theme} theme, {style} style"
        
        if color_scheme:
            prompt += f", {color_scheme} color scheme"
        
        # Add element-specific details
        if "button" in element.lower():
            prompt += ", with normal, hover, and pressed states shown"
        elif "bar" in element.lower():
            prompt += ", showing empty and full states"
        elif "panel" in element.lower():
            prompt += ", with border decoration and semi-transparent background"
        
        prompt += ", clean vector graphics, suitable for game UI"
        
        response = await client.images.generate(
            model=OPENAI_MODELS["image"]["default"],
            prompt=prompt,
            size="1024x1024",
            quality="standard",  # UI doesn't need HD
            style="vivid",
            n=1
        )
        
        image_url = response.data[0].url
        element_path = None
        
        if save_path:
            base = Path(save_path)
            element_path = base / f"{element}.png"
            element_path.parent.mkdir(parents=True, exist_ok=True)
            
            async with httpx.AsyncClient() as http_client:
                img_response = await http_client.get(image_url)
                img_response.raise_for_status()
                
                async with aiofiles.open(element_path, 'wb') as f:
                    await f.write(img_response.content)
        
        results.append(GeneratedImage(
            type="ui_element",
            description=f"{ui_theme} {element} ({style} style)",
            path=str(element_path) if element_path else None,
            size=(1024, 1024),
            url=image_url
        ))
    
    return results


@function_tool
async def generate_graphics_pack(
    game_title: str,
    game_genre: str,
    art_style: str = "pixel",
    characters: list[str] | None = None,
    environments: list[str] | None = None,
    ui_theme: str | None = None,
    output_dir: str | None = None,
) -> dict[str, list[GeneratedImage]]:
    """Generate a complete graphics pack for a game.
    
    Creates all necessary visual assets including sprites, backgrounds, and UI.
    
    Args:
        game_title: Title of the game
        game_genre: Genre (platformer, rpg, shooter, etc.)
        art_style: Overall art style
        characters: List of characters/sprites needed
        environments: List of environments/backgrounds needed
        ui_theme: UI theme (defaults to genre-appropriate)
        output_dir: Directory to save all graphics
        
    Returns:
        Dictionary with 'sprites', 'backgrounds', 'tilesets', and 'ui' lists
    """
    results = {
        "sprites": [],
        "backgrounds": [],
        "tilesets": [],
        "ui": []
    }
    
    # Default lists if not provided
    if not characters:
        characters = ["player", "enemy", "collectible"]
    
    if not environments:
        environments = ["main_level", "menu_background"]
    
    if not ui_theme:
        ui_theme = "sci-fi" if game_genre in ["shooter", "space"] else "fantasy"
    
    # Base output directory
    if output_dir:
        base_path = Path(output_dir)
        base_path.mkdir(parents=True, exist_ok=True)
    else:
        base_path = None
    
    # Generate character sprites
    for char in characters:
        sprite_path = str(base_path / "sprites" / f"{char}.png") if base_path else None
        sprite = await generate_sprite(
            object_name=char,
            art_style=art_style,
            save_path=sprite_path
        )
        results["sprites"].append(sprite)
    
    # Generate backgrounds
    for env in environments:
        bg_path = str(base_path / "backgrounds" / f"{env}.png") if base_path else None
        background = await generate_background(
            scene=env,
            style=art_style,
            save_path=bg_path
        )
        results["backgrounds"].append(background)
    
    # Generate a tileset if it's a platformer or RPG
    if game_genre in ["platformer", "rpg", "metroidvania"]:
        tileset_path = str(base_path / "tilesets" / "main_tileset.png") if base_path else None
        tileset = await generate_tileset(
            environment=environments[0] if environments else "generic",
            art_style=art_style,
            save_path=tileset_path
        )
        results["tilesets"].append(tileset)
    
    # Generate UI elements
    ui_elements = ["button", "panel", "health_bar", "dialog_box"]
    ui_path = str(base_path / "ui") if base_path else None
    ui_results = await generate_ui_elements(
        ui_theme=ui_theme,
        elements=ui_elements,
        save_path=ui_path
    )
    results["ui"].extend(ui_results)
    
    return results
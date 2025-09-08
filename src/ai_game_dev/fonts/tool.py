"""
OpenAI function tools for font and text rendering.
"""
from pathlib import Path
from typing import Literal, Any
from PIL import Image, ImageDraw, ImageFont
import requests

from agents import function_tool

from ai_game_dev.fonts.google_fonts import GoogleFonts


@function_tool(strict_mode=False)
async def find_game_font(
    style: Literal["pixel", "fantasy", "sci-fi", "casual", "retro", "horror"] = "casual",
    weight: Literal["regular", "bold", "light"] = "regular",
    download: bool = True,
    save_path: str | None = None,
) -> dict[str, Any]:
    """Find and download appropriate game fonts from Google Fonts.
    
    Args:
        style: Game style to match
        weight: Font weight
        download: Whether to download the font
        save_path: Where to save the font file
        
    Returns:
        Font information and path
    """
    # Map game styles to font categories
    style_mapping = {
        "pixel": ["display", "monospace"],
        "fantasy": ["serif", "display"],
        "sci-fi": ["sans-serif", "monospace"],
        "casual": ["handwriting", "display"],
        "retro": ["display", "serif"],
        "horror": ["display", "serif"]
    }
    
    google_fonts = GoogleFonts()
    categories = style_mapping.get(style, ["sans-serif"])
    
    # Search for appropriate fonts
    results = []
    for category in categories:
        fonts = await google_fonts.search_fonts("game", category=category)
        results.extend(fonts[:3])  # Top 3 from each category
    
    if not results:
        # Fallback to popular gaming fonts
        results = [
            {"family": "Press Start 2P", "category": "display"},
            {"family": "Orbitron", "category": "sans-serif"},
            {"family": "Audiowide", "category": "display"}
        ]
    
    # Select the first suitable font
    font = results[0]
    font_info = {
        "name": font["family"],
        "category": font.get("category", "sans-serif"),
        "style": style,
        "weight": weight
    }
    
    if download and save_path:
        # Download the font
        font_data = await google_fonts.download_font(font["family"])
        if font_data:
            path = Path(save_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            
            for variant, data in font_data.items():
                if weight in variant.lower() or (weight == "regular" and variant == "regular"):
                    font_path = path.parent / f"{font['family'].replace(' ', '_')}_{variant}.ttf"
                    font_path.write_bytes(data)
                    font_info["path"] = str(font_path)
                    break
    
    return font_info


@function_tool(strict_mode=False)
async def render_game_text(
    text: str,
    font_style: Literal["title", "ui", "dialogue", "score"] = "ui",
    color: str = "white",
    size: int = 32,
    effects: list[Literal["shadow", "outline", "glow"]] | None = None,
    save_path: str | None = None,
) -> dict[str, Any]:
    """Render game text with effects.
    
    Args:
        text: Text to render
        font_style: Style preset for the text
        color: Text color
        size: Font size in pixels
        effects: Visual effects to apply
        save_path: Where to save the rendered text
        
    Returns:
        Rendered text information
    """
    # Style presets
    style_presets = {
        "title": {"style": "fantasy", "weight": "bold", "size_mult": 2.0},
        "ui": {"style": "casual", "weight": "regular", "size_mult": 1.0},
        "dialogue": {"style": "casual", "weight": "regular", "size_mult": 0.8},
        "score": {"style": "retro", "weight": "bold", "size_mult": 1.5}
    }
    
    preset = style_presets.get(font_style, style_presets["ui"])
    adjusted_size = int(size * preset["size_mult"])
    
    # Find appropriate font
    font_info = await find_game_font(
        style=preset["style"],
        weight=preset["weight"],
        download=True,
        save_path="temp_font.ttf" if not save_path else None
    )
    
    # Create image with text
    # Estimate text size (rough approximation)
    img_width = len(text) * adjusted_size
    img_height = adjusted_size * 2
    
    # Create transparent image
    img = Image.new('RGBA', (img_width, img_height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Try to load font, fallback to default
    try:
        if "path" in font_info:
            font = ImageFont.truetype(font_info["path"], adjusted_size)
        else:
            font = ImageFont.load_default()
    except:
        font = ImageFont.load_default()
    
    # Get actual text size
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    # Recreate image with proper size
    img = Image.new('RGBA', (text_width + 20, text_height + 20), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Apply effects
    if effects:
        if "shadow" in effects:
            # Draw shadow
            shadow_color = (0, 0, 0, 128)
            draw.text((12, 12), text, font=font, fill=shadow_color)
        
        if "outline" in effects:
            # Draw outline
            outline_color = (0, 0, 0, 255)
            for dx in [-2, 0, 2]:
                for dy in [-2, 0, 2]:
                    if dx != 0 or dy != 0:
                        draw.text((10 + dx, 10 + dy), text, font=font, fill=outline_color)
    
    # Draw main text
    draw.text((10, 10), text, font=font, fill=color)
    
    # Apply glow effect if requested
    if effects and "glow" in effects:
        # Simple glow simulation with blur
        from PIL import ImageFilter
        glow_img = img.filter(ImageFilter.GaussianBlur(radius=3))
        img = Image.alpha_composite(glow_img, img)
    
    result = {
        "text": text,
        "font": font_info["name"],
        "style": font_style,
        "size": adjusted_size,
        "effects": effects or []
    }
    
    if save_path:
        path = Path(save_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        img.save(path, "PNG")
        result["path"] = str(path)
        result["dimensions"] = (img.width, img.height)
    
    return result


@function_tool(strict_mode=False)
async def generate_text_assets(
    game_title: str,
    ui_texts: list[str] | None = None,
    style: Literal["pixel", "fantasy", "sci-fi", "casual", "retro"] = "casual",
    output_dir: str | None = None,
) -> dict[str, list[dict[str, Any]]]:
    """Generate all text assets for a game.
    
    Args:
        game_title: Title of the game
        ui_texts: List of UI texts to render
        style: Overall game style
        output_dir: Directory to save text assets
        
    Returns:
        Dictionary of generated text assets
    """
    if not ui_texts:
        ui_texts = ["Start Game", "Options", "Quit", "Score:", "Level:", "Game Over"]
    
    results = {
        "title": [],
        "ui": [],
        "fonts": []
    }
    
    base_dir = Path(output_dir) if output_dir else Path("text_assets")
    
    # Generate title
    title_path = str(base_dir / "title.png")
    title_result = await render_game_text(
        text=game_title,
        font_style="title",
        size=64,
        effects=["shadow", "outline"],
        save_path=title_path
    )
    results["title"].append(title_result)
    
    # Generate UI texts
    for ui_text in ui_texts:
        ui_path = str(base_dir / "ui" / f"{ui_text.lower().replace(' ', '_')}.png")
        ui_result = await render_game_text(
            text=ui_text,
            font_style="ui",
            size=24,
            effects=["shadow"],
            save_path=ui_path
        )
        results["ui"].append(ui_result)
    
    # Download fonts for the game
    for font_style in ["regular", "bold"]:
        font_path = str(base_dir / "fonts" / f"game_font_{font_style}.ttf")
        font_info = await find_game_font(
            style=style,
            weight=font_style,
            download=True,
            save_path=font_path
        )
        results["fonts"].append(font_info)
    
    return results
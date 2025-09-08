"""
Unified graphics and visual asset generation module.
Combines OpenAI image generation, CC0 libraries, and Pillow processing.
"""

from ai_game_dev.graphics.cc0_libraries import CC0Libraries
from ai_game_dev.graphics.image_processor import ImageProcessor
from ai_game_dev.graphics.tool import (
    generate_sprite,
    generate_tileset,
    generate_background,
    generate_ui_elements,
    find_or_generate_sprite,
    process_spritesheet,
    generate_graphics_pack,
)

# Import 3D capabilities if available
try:
    from ai_game_dev.graphics.point_cloud_3d import (
        generate_3d_model,
        generate_game_3d_asset,
        generate_3d_sprite_sheet
    )
    _3D_AVAILABLE = True
except ImportError:
    _3D_AVAILABLE = False

__all__ = [
    "CC0Libraries",
    "ImageProcessor",
    "generate_sprite",
    "generate_tileset",
    "generate_background",
    "generate_ui_elements",
    "find_or_generate_sprite",
    "process_spritesheet",
    "generate_graphics_pack",
]

# Add 3D tools if available
if _3D_AVAILABLE:
    __all__.extend([
        "generate_3d_model",
        "generate_game_3d_asset",
        "generate_3d_sprite_sheet"
    ])
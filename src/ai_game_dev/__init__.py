"""AI Game Development Library - Revolutionary multi-agent game creation with universal language support."""

__version__ = "1.0.0"

# Core library exports
from ai_game_dev.library import AIGameDev, GameEngine, create_game, demo
from ai_game_dev.rust_bindings import (
    RustIntegratedGameDev, 
    create_rust_integrated_dev,
    create_bevy_game_optimized,
    check_rust_support
)

# Legacy MCP server functionality
from ai_game_dev.models import (
    ImageSize,
    ImageQuality,
    ImageDetail,
    MaterialProperties,
    GeometrySpec,
    TextureRequirement,
    Model3DSpec,
    ImageAnalysis,
)
from ai_game_dev.server import MCPServer
from ai_game_dev.generators import (
    ImageGenerator,
    Model3DGenerator,
)

# Main library interface
__all__ = [
    # Core library classes
    "AIGameDev",
    "GameEngine", 
    "create_game",
    "demo",
    # Rust integration
    "RustIntegratedGameDev",
    "create_rust_integrated_dev", 
    "create_bevy_game_optimized",
    "check_rust_support",
    # Legacy MCP server components
    # Data models
    "ImageSize",
    "ImageQuality", 
    "ImageDetail",
    "MaterialProperties",
    "GeometrySpec",
    "TextureRequirement",
    "Model3DSpec",
    "ImageAnalysis",
    # MCP Server
    "MCPServer",
    # Content generators
    "ImageGenerator",
    "Model3DGenerator",
]
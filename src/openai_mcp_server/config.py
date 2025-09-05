"""Configuration and settings for the MCP server."""

import os
from pathlib import Path

# Configuration
CACHE_DIR = Path("generated_assets")
IMAGES_DIR = CACHE_DIR / "images"
MODELS_3D_DIR = CACHE_DIR / "3d_models"
VERIFICATION_CACHE = CACHE_DIR / "verification_cache.json"

def setup_directories() -> None:
    """Ensure all required directories exist."""
    CACHE_DIR.mkdir(exist_ok=True)
    IMAGES_DIR.mkdir(exist_ok=True)
    MODELS_3D_DIR.mkdir(exist_ok=True)

def get_openai_api_key() -> str:
    """Get OpenAI API key from environment."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is required")
    return api_key
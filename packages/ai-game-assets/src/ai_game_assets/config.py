"""
Configuration management for AI Game Assets library.
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings
from xdg_base_dirs import xdg_cache_home, xdg_data_home


class AssetConfig(BaseSettings):
    """Configuration for AI Game Assets."""
    
    # API Keys
    openai_api_key: Optional[str] = None
    freesound_api_key: Optional[str] = None
    
    # Cache and storage directories
    cache_dir: str = str(xdg_cache_home() / "ai_game_assets")
    data_dir: str = str(xdg_data_home() / "ai_game_assets")
    
    # Generation settings
    default_image_size: str = "1024x1024"
    default_audio_format: str = "mp3"
    default_music_tempo: int = 120
    
    class Config:
        env_prefix = "AI_GAME_ASSETS_"
        env_file = ".env"


def get_config() -> AssetConfig:
    """Get the current configuration instance."""
    return AssetConfig()
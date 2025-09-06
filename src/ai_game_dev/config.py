"""Configuration and settings for the MCP server."""

from pathlib import Path
from typing import ClassVar

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from xdg_base_dirs import xdg_cache_home, xdg_data_home


class ServerSettings(BaseSettings):
    """Server configuration using pydantic-settings with XDG base directories."""
    
    model_config: ClassVar[SettingsConfigDict] = SettingsConfigDict(
        env_prefix="OPENAI_MCP_",
        case_sensitive=False,
        env_file=".env",
        env_file_encoding="utf-8",
    )
    
    # OpenAI API configuration
    openai_api_key: str = Field(
        ..., 
        alias="OPENAI_API_KEY",
        description="OpenAI API key for accessing AI services"
    )
    
    # Directory configuration using XDG standards
    cache_base_dir: Path = Field(
        default_factory=lambda: xdg_cache_home() / "openai-mcp-server",
        description="Base cache directory following XDG standards"
    )
    
    data_base_dir: Path = Field(
        default_factory=lambda: xdg_data_home() / "openai-mcp-server", 
        description="Base data directory following XDG standards"
    )
    
    # Server configuration
    server_name: str = Field(
        default="openai-multimodal-server",
        description="MCP server name"
    )
    
    # Cache settings
    enable_caching: bool = Field(
        default=True,
        description="Enable content caching for efficiency"
    )
    
    @property
    def cache_dir(self) -> Path:
        """Cache directory for temporary generated assets."""
        return self.cache_base_dir / "assets"
    
    @property
    def images_dir(self) -> Path:
        """Directory for cached images."""
        return self.cache_dir / "images"
    
    @property
    def models_3d_dir(self) -> Path:
        """Directory for cached 3D models."""
        return self.cache_dir / "3d_models"
    
    @property
    def verification_cache_path(self) -> Path:
        """Path to verification cache file."""
        return self.data_base_dir / "verification_cache.json"
    
    def setup_directories(self) -> None:
        """Ensure all required directories exist."""
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.images_dir.mkdir(parents=True, exist_ok=True)
        self.models_3d_dir.mkdir(parents=True, exist_ok=True)
        self.data_base_dir.mkdir(parents=True, exist_ok=True)


# Global settings instance
settings = ServerSettings()  # type: ignore[call-arg]

# Legacy exports for backward compatibility
CACHE_DIR = settings.cache_dir
IMAGES_DIR = settings.images_dir
MODELS_3D_DIR = settings.models_3d_dir
VERIFICATION_CACHE = settings.verification_cache_path

def setup_directories() -> None:
    """Ensure all required directories exist."""
    settings.setup_directories()

def get_openai_api_key() -> str:
    """Get OpenAI API key from settings."""
    return settings.openai_api_key
"""AI Game Development Library.

A revolutionary unified Python package for AI-powered game development
featuring multi-LLM support, comprehensive asset generation, and 
engine-specific TOML specifications.
"""

from ai_game_dev.models import (
    GameSpec,
    GameEngine,
    GameType,
    ComplexityLevel
)
from ai_game_dev.providers import (
    LLMProvider,
    ModelConfig,
    setup_openai,
    setup_anthropic,
    setup_google,
    setup_ollama,
    create_default_manager
)
from ai_game_dev.library import AIGameDev
from ai_game_dev.audio import AudioTools
from ai_game_dev.graphics import CC0Libraries
from ai_game_dev.fonts import GoogleFonts

# Version info
__version__ = "1.0.0"
__author__ = "AI Game Dev Team"
__email__ = "team@ai-game-dev.com"

# Public API
__all__ = [
    # Data models
    "GameSpec",
    "GameEngine",
    "GameType",
    "ComplexityLevel",
    
    # LLM providers
    "LLMProvider",
    "ModelConfig",
    "setup_openai",
    "setup_anthropic", 
    "setup_google",
    "setup_ollama",
    "create_default_manager",
    
    # Main library
    "AIGameDev",
    
    # Audio tools
    "AudioTools",
    
    # Graphics and fonts
    "CC0Libraries",
    "GoogleFonts",
    
    # Version
    "__version__",
]


def get_version() -> str:
    """Get the current version of ai-game-dev."""
    return __version__


def get_supported_engines() -> list[str]:
    """Get list of supported game engines."""
    return ["pygame", "bevy", "godot", "arcade"]


def get_supported_llm_providers() -> list[str]:
    """Get list of supported LLM providers."""
    return [provider.value for provider in LLMProvider]
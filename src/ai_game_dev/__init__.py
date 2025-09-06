"""AI Game Development Library.

A revolutionary unified Python package for AI-powered game development
featuring multi-LLM support, comprehensive asset generation, and 
engine-specific TOML specifications.
"""

from ai_game_dev.library import AIGameDev
from ai_game_dev.models import (
    GameSpec,
    GameEngine,
    GameType,
    ComplexityLevel
)
from ai_game_dev.providers import (
    LLMProviderManager,
    LLMProvider,
    ModelConfig,
    setup_openai,
    setup_anthropic,
    setup_google,
    setup_ollama,
    create_default_manager
)

# Asset management
from ai_game_dev.assets.asset_tools import AssetTools
from ai_game_dev.assets.audio.audio_tools import AudioTools

# Version info
__version__ = "1.0.0"
__author__ = "AI Game Dev Team"
__email__ = "team@ai-game-dev.com"

# Public API
__all__ = [
    # Core classes
    "AIGameDev",
    
    # Data models
    "GameSpec",
    "GameEngine",
    "GameType",
    "ComplexityLevel",
    
    # LLM providers
    "LLMProviderManager",
    "LLMProvider",
    "ModelConfig",
    "setup_openai",
    "setup_anthropic", 
    "setup_google",
    "setup_ollama",
    "create_default_manager",
    
    # Asset tools
    "AssetTools",
    "AudioTools",
    
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
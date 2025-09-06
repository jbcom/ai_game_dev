"""AI Game Development Library.

A revolutionary unified Python package for AI-powered game development
featuring multi-LLM support, comprehensive asset generation, and 
engine-specific TOML specifications.
"""

from .library import AIGameDev
from .models import (
    GameSpec,
    AssetPackage,
    DialogueSystem,
    QuestSystem,
    GameEngineTarget
)
from .providers import (
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
from .assets.asset_tools import AssetTools
from .assets.audio.audio_tools import AudioTools

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
    "AssetPackage", 
    "DialogueSystem",
    "QuestSystem",
    "GameEngineTarget",
    
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
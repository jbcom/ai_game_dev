"""AI Game Development Library.

A revolutionary unified Python package for AI-powered game development
using OpenAI agents for comprehensive asset generation and multi-engine support.
"""

from ai_game_dev.models import (
    ComplexityLevel,
    GameEngine,
    GameSpec,
    GameType,
)
from ai_game_dev.providers import (
    LLMProvider,
    ModelConfig,
    create_default_manager,
    setup_anthropic,
    setup_google,
    setup_ollama,
    setup_openai,
)
from ai_game_dev.agent import (
    create_game,
    create_educational_game,
    process_request,
)

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
    
    # Agent functions
    "create_game",
    "create_educational_game",
    "process_request",
    
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
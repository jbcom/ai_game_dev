"""
OpenAI-based tools for game development.
Uses direct OpenAI APIs for better control and quality.
"""

from ai_game_dev.tools.openai_tools.audio import (
    generate_music,
    generate_sound_effect,
    generate_voice,
)
from ai_game_dev.tools.openai_tools.image import (
    generate_character_sprite,
    generate_environment,
    generate_game_asset,
    generate_ui_element,
)
from ai_game_dev.tools.openai_tools.text import (
    generate_dialogue,
    generate_game_code,
    generate_quest,
    identify_teachable_moments,
)

__all__ = [
    # Audio tools
    "generate_voice",
    "generate_sound_effect", 
    "generate_music",
    # Image tools
    "generate_game_asset",
    "generate_character_sprite",
    "generate_environment",
    "generate_ui_element",
    # Text tools
    "generate_dialogue",
    "generate_quest",
    "generate_game_code",
    "identify_teachable_moments",
]
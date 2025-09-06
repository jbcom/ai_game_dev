"""
AI Game Assets Library
Standalone multimedia asset generation with OpenAI, Google Fonts, CC0 resources, and semantic seeding.
"""

from ai_game_dev.assets.ai_game_assets.audio.audio_tools import AudioTools, TTSGenerator, MusicGenerator, FreesoundClient
from ai_game_dev.assets.ai_game_assets.assets.asset_tools import AssetTools

__version__ = "1.0.0"

__all__ = [
    "AudioTools",
    "TTSGenerator",
    "MusicGenerator", 
    "FreesoundClient",
    "AssetTools",
]
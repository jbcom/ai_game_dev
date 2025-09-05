"""
AI Game Assets Library
Standalone multimedia asset generation with OpenAI, Google Fonts, CC0 resources, and semantic seeding.
"""

from .audio import AudioTools, TTSGenerator, MusicGenerator, FreesoundClient
from .assets import AssetTools, CC0AssetLibrary, GoogleFontsManager, InternetArchiveSeeder

__version__ = "1.0.0"

__all__ = [
    "AudioTools",
    "TTSGenerator",
    "MusicGenerator", 
    "FreesoundClient",
    "AssetTools",
    "CC0AssetLibrary",
    "GoogleFontsManager",
    "InternetArchiveSeeder",
]
"""
Audio generation and processing tools.
Provides OpenAI function tools for TTS, music, and sound effects.
"""

from ai_game_dev.audio.audio_tools import AudioTools
from ai_game_dev.audio.tts_generator import TTSGenerator
from ai_game_dev.audio.music_generator import MusicGenerator
from ai_game_dev.audio.freesound_client import FreesoundClient
from ai_game_dev.audio.tool import (
    generate_voice_acting,
    generate_sound_effect,
    generate_background_music,
    generate_audio_pack,
)

__all__ = [
    "AudioTools",
    "TTSGenerator", 
    "MusicGenerator",
    "FreesoundClient",
    # OpenAI function tools
    "generate_voice_acting",
    "generate_sound_effect",
    "generate_background_music",
    "generate_audio_pack",
]
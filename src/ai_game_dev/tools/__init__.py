"""
Tools package - exports functionality from audio, graphics, fonts, and variants.
Each subpackage provides OpenAI function tools.
"""

# Re-export from subpackages
from ai_game_dev.audio import *
from ai_game_dev.graphics import *
from ai_game_dev.fonts import *
from ai_game_dev.variants import *

__all__ = [
    # From audio
    "AudioTools",
    "TTSGenerator", 
    "MusicGenerator",
    "FreesoundClient",
    "generate_voice_acting",
    "generate_sound_effect",
    "generate_background_music",
    "generate_audio_pack",
    
    # From graphics
    "CC0Libraries",
    "ImageProcessor",
    "generate_game_sprite",
    "generate_game_background", 
    "generate_ui_pack",
    "find_cc0_assets",
    "process_game_image",
    "generate_complete_graphics_pack",
    "find_or_generate_sprite",
    "process_spritesheet",
    
    # From fonts
    "GoogleFonts",
    "find_game_font",
    "render_game_text", 
    "generate_text_assets",
    
    # From variants
    "VariantType",
    "VariantChoice", 
    "VariantPoint",
    "FeatureFlags",
    "VariantGenerator",
    "VariantCodeInjector",
    "InteractiveVariantSystem",
    "create_variant_enabled_game",
    "generate_mechanic_variants",
    "identify_interactive_moments",
    "apply_variant_to_code",
    "generate_educational_variants",
    "create_variant_pack",
]
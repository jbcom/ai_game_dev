"""
pygame_game_dev - AI-powered 2D game development with PyGame
Specialized library built on ai_game_dev for 2D game creation.
"""

__version__ = "1.0.0"

# Core pygame integration
from pygame_game_dev.core import PyGameDev, create_2d_game
from pygame_game_dev.sprites import AISprite, SpriteGenerator
from pygame_game_dev.physics import PhysicsWorld, PhysicsBody
from pygame_game_dev.audio import SoundManager, MusicManager
from pygame_game_dev.tiles import TileMap, TileSetGenerator
from pygame_game_dev.ui import UIManager, MenuSystem
from pygame_game_dev.animation import AnimationSystem, SpriteAnimator

# Game templates and presets
from pygame_game_dev.templates import (
    PlatformerTemplate,
    TopDownTemplate, 
    PuzzleTemplate,
    EducationalTemplate,
)

# Asset generation specialized for 2D
from pygame_game_dev.assets import (
    generate_sprite_sheet,
    generate_tile_set,
    generate_ui_elements,
    generate_particle_effects,
)

__all__ = [
    # Core functionality
    "PyGameDev",
    "create_2d_game",
    
    # Sprites and graphics
    "AISprite", 
    "SpriteGenerator",
    
    # Physics
    "PhysicsWorld",
    "PhysicsBody",
    
    # Audio
    "SoundManager",
    "MusicManager",
    
    # Tiles and maps
    "TileMap",
    "TileSetGenerator", 
    
    # UI and menus
    "UIManager",
    "MenuSystem",
    
    # Animation
    "AnimationSystem",
    "SpriteAnimator",
    
    # Templates
    "PlatformerTemplate",
    "TopDownTemplate",
    "PuzzleTemplate", 
    "EducationalTemplate",
    
    # Asset generation
    "generate_sprite_sheet",
    "generate_tile_set",
    "generate_ui_elements", 
    "generate_particle_effects",
]
"""Game engine integrations module.

Modern modular engine architecture with dedicated adapters.
"""

from .base import BaseEngineAdapter, EngineGenerationResult
from .manager import EngineManager, engine_manager, generate_for_engine, get_supported_engines
from .pygame import PygameAdapter
from .bevy import BevyAdapter
from .godot import GodotAdapter

__all__ = [
    "BaseEngineAdapter",
    "EngineGenerationResult", 
    "EngineManager",
    "engine_manager",
    "generate_for_engine",
    "get_supported_engines",
    "PygameAdapter",
    "BevyAdapter", 
    "GodotAdapter"
]
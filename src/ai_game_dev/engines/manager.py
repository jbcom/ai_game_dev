"""
Modern engine management system with proper adapter architecture.
Replaces the old monolithic engine_adapters.py with clean, modular design.
"""
from typing import Dict, Optional, List
from pathlib import Path

from ai_game_dev.engines.base import BaseEngineAdapter, EngineGenerationResult
from ai_game_dev.engines.pygame import PygameAdapter
from ai_game_dev.engines.bevy import BevyAdapter  
from ai_game_dev.engines.godot import GodotAdapter


class EngineManager:
    """
    Modern engine management system with proper adapter architecture.
    Provides clean interface for game generation across multiple engines.
    """
    
    def __init__(self):
        self._adapters: Dict[str, BaseEngineAdapter] = {
            "pygame": PygameAdapter(),
            "bevy": BevyAdapter(),
            "godot": GodotAdapter()
        }
    
    def get_supported_engines(self) -> List[str]:
        """Get list of supported game engines."""
        return list(self._adapters.keys())
    
    def get_adapter(self, engine_name: str) -> Optional[BaseEngineAdapter]:
        """Get adapter for specific engine."""
        return self._adapters.get(engine_name.lower())
    
    async def generate_for_engine(
        self,
        engine_name: str,
        description: str,
        complexity: str = "intermediate",
        features: List[str] = None,
        art_style: str = "modern"
    ) -> EngineGenerationResult:
        """
        Generate a complete game project for the specified engine.
        
        Args:
            engine_name: Target engine (pygame, bevy, godot)
            description: Game description and requirements
            complexity: Game complexity level (beginner, intermediate, advanced)
            features: List of specific features to implement
            art_style: Visual art style preference
            
        Returns:
            EngineGenerationResult with complete project files and metadata
        """
        adapter = self.get_adapter(engine_name)
        if not adapter:
            raise ValueError(f"Unsupported engine: {engine_name}")
        
        return await adapter.generate_game_project(
            description=description,
            complexity=complexity,
            features=features or [],
            art_style=art_style
        )
    
    def get_engine_info(self, engine_name: str) -> Optional[Dict[str, str]]:
        """Get information about a specific engine."""
        adapter = self.get_adapter(engine_name)
        if not adapter:
            return None
        
        return {
            "name": adapter.engine_name,
            "language": adapter.native_language,
            "build_instructions": adapter.get_build_instructions(),
            "project_template": str(adapter.get_project_template())
        }
    
    def get_all_engines_info(self) -> Dict[str, Dict[str, str]]:
        """Get information about all supported engines."""
        return {
            engine: self.get_engine_info(engine)
            for engine in self.get_supported_engines()
        }


# Create global instance for backward compatibility
engine_manager = EngineManager()


# Convenience functions for backward compatibility
async def generate_for_engine(
    engine_name: str,
    description: str,
    complexity: str = "intermediate", 
    features: List[str] = None,
    art_style: str = "modern"
) -> EngineGenerationResult:
    """Generate game project using the global engine manager."""
    return await engine_manager.generate_for_engine(
        engine_name, description, complexity, features, art_style
    )


def get_supported_engines() -> List[str]:
    """Get supported engines using the global engine manager."""
    return engine_manager.get_supported_engines()
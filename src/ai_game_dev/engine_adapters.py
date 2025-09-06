"""
Legacy engine adapters module - DEPRECATED.
This module is maintained for backward compatibility only.
New code should use ai_game_dev.engines package directly.

The new modular engine system provides:
- Dedicated adapter packages for each engine
- Real code generation instead of placeholders
- Better separation of concerns
- Professional project structure
"""
import warnings
from typing import Dict, Any, List, Optional

# Import from new modular system
try:
    from ai_game_dev.engines.base import BaseEngineAdapter, EngineGenerationResult
    from ai_game_dev.engines.manager import engine_manager
    from ai_game_dev.engines import PygameAdapter, BevyAdapter, GodotAdapter
except ImportError:
    # Fallback for testing
    warnings.warn("New engine system not available, using legacy adapters")
    from dataclasses import dataclass
    from abc import ABC, abstractmethod
    from pathlib import Path
    
    @dataclass
    class EngineGenerationResult:
        """Result from engine-specific generation."""
        engine_type: str
        project_structure: Dict[str, Any]
        main_files: List[str]
        asset_requirements: List[str]
        build_instructions: str
        deployment_notes: str
        generated_files: Dict[str, str] = None
        project_path: Optional[Path] = None
    
    class BaseEngineAdapter(ABC):
        """Legacy base adapter."""
        @abstractmethod
        async def generate_game_project(self, description: str, **kwargs) -> EngineGenerationResult:
            pass


# Legacy adapter aliases for backward compatibility
class EngineAdapter(BaseEngineAdapter):
    """Legacy base class - use BaseEngineAdapter from engines.base instead."""
    
    def __init__(self):
        warnings.warn(
            "EngineAdapter is deprecated. Use BaseEngineAdapter from ai_game_dev.engines.base",
            DeprecationWarning,
            stacklevel=2
        )
        super().__init__()


class EngineAdapterManager:
    """
    Legacy engine manager - DEPRECATED.
    Use EngineManager from ai_game_dev.engines.manager instead.
    """
    
    def __init__(self):
        warnings.warn(
            "EngineAdapterManager is deprecated. Use EngineManager from ai_game_dev.engines.manager", 
            DeprecationWarning,
            stacklevel=2
        )
        try:
            self.manager = engine_manager
        except NameError:
            self.manager = None
    
    def get_adapter(self, engine_name: str) -> Optional[BaseEngineAdapter]:
        """Get adapter for engine - delegates to new system."""
        if self.manager:
            return self.manager.get_adapter(engine_name)
        return None
    
    async def generate_game(self, engine_name: str, description: str, **kwargs) -> EngineGenerationResult:
        """Generate game - delegates to new system."""
        if self.manager:
            return await self.manager.generate_for_engine(engine_name, description, **kwargs)
        
        # Fallback
        return EngineGenerationResult(
            engine_type=engine_name,
            project_structure={},
            main_files=[],
            asset_requirements=[],
            build_instructions="Legacy adapter - please use new engine system",
            deployment_notes="Update to new ai_game_dev.engines package"
        )


# Legacy adapter classes - these delegate to new system when possible
class PygameEngineAdapter(EngineAdapter):
    """Legacy Pygame adapter - use PygameAdapter from engines.pygame instead."""
    
    def __init__(self):
        super().__init__()
        try:
            self._adapter = PygameAdapter()
        except NameError:
            self._adapter = None
    
    @property
    def engine_name(self) -> str:
        return "pygame"
    
    @property
    def native_language(self) -> str:
        return "python"
    
    async def generate_game_project(self, description: str, **kwargs) -> EngineGenerationResult:
        if self._adapter:
            return await self._adapter.generate_game_project(description, **kwargs)
        
        # Fallback for legacy compatibility
        return EngineGenerationResult(
            engine_type="pygame",
            project_structure={"main.py": "Legacy placeholder"},
            main_files=["main.py"],
            asset_requirements=["player.png"],
            build_instructions="Use new engines.pygame.PygameAdapter",
            deployment_notes="Migrate to new engine system"
        )


class BevyEngineAdapter(EngineAdapter):
    """Legacy Bevy adapter - use BevyAdapter from engines.bevy instead."""
    
    def __init__(self):
        super().__init__()
        try:
            self._adapter = BevyAdapter()
        except NameError:
            self._adapter = None
    
    @property
    def engine_name(self) -> str:
        return "bevy"
    
    @property  
    def native_language(self) -> str:
        return "rust"
    
    async def generate_game_project(self, description: str, **kwargs) -> EngineGenerationResult:
        if self._adapter:
            return await self._adapter.generate_game_project(description, **kwargs)
        
        return EngineGenerationResult(
            engine_type="bevy",
            project_structure={"Cargo.toml": "Legacy placeholder"},
            main_files=["Cargo.toml", "src/main.rs"],
            asset_requirements=["player_model.gltf"],
            build_instructions="Use new engines.bevy.BevyAdapter",
            deployment_notes="Migrate to new engine system"
        )


class GodotEngineAdapter(EngineAdapter):
    """Legacy Godot adapter - use GodotAdapter from engines.godot instead."""
    
    def __init__(self):
        super().__init__()
        try:
            self._adapter = GodotAdapter()
        except NameError:
            self._adapter = None
    
    @property
    def engine_name(self) -> str:
        return "godot"
    
    @property
    def native_language(self) -> str:
        return "gdscript"
    
    async def generate_game_project(self, description: str, **kwargs) -> EngineGenerationResult:
        if self._adapter:
            return await self._adapter.generate_game_project(description, **kwargs)
        
        return EngineGenerationResult(
            engine_type="godot",
            project_structure={"project.godot": "Legacy placeholder"},
            main_files=["Main.gd", "Player.gd"],
            asset_requirements=["player.png"],
            build_instructions="Use new engines.godot.GodotAdapter",
            deployment_notes="Migrate to new engine system"
        )


# Re-export for backward compatibility
__all__ = [
    "EngineGenerationResult",
    "EngineAdapter", 
    "BaseEngineAdapter",
    "EngineAdapterManager",
    "PygameEngineAdapter",
    "BevyEngineAdapter", 
    "GodotEngineAdapter"
]
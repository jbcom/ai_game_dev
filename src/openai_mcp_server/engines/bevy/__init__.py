"""Bevy game engine integration with ECS optimizations."""

from .generator import BevyGenerator
from .ecs_components import ECSlibrary
from .asset_pipeline import BevyAssetPipeline
from .templates import BevyTemplateManager

__all__ = [
    "BevyGenerator",
    "ECSlibrary", 
    "BevyAssetPipeline",
    "BevyTemplateManager"
]

class BevyEngine:
    """Bevy-specific game engine integration."""
    
    def __init__(self, openai_client):
        self.client = openai_client
        self.generator = BevyGenerator(openai_client)
        self.ecs = ECSlibrary()
        self.assets = BevyAssetPipeline()
        self.templates = BevyTemplateManager()
    
    async def initialize(self):
        """Initialize Bevy engine integration."""
        await self.generator.initialize()
        await self.templates.initialize()
    
    def get_capabilities(self):
        """Get Bevy-specific capabilities."""
        return {
            "ecs_architecture": True,
            "rust_code_generation": True, 
            "asset_hot_reloading": True,
            "system_parallelization": True,
            "component_derive_macros": True,
            "resource_management": True,
            "event_driven_architecture": True,
            "plugin_system": True
        }
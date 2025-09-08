"""
Protocol definitions for AI Game Development.
Defines interfaces for various components.
"""
from typing import Protocol, runtime_checkable
from pathlib import Path

from ai_game_dev.types import (
    DialogueNode,
    Quest,
    GameNarrative,
    CharacterProfile,
    LessonPlan,
    TeachableMoment,
    GameSpec,
    CodeRepository
)


@runtime_checkable
class TextGenerator(Protocol):
    """Protocol for text generation tools."""
    
    async def generate_dialogue(self, context: str) -> DialogueNode:
        """Generate dialogue tree."""
        ...
    
    async def generate_quest(self, theme: str) -> Quest:
        """Generate quest chain."""
        ...
    
    async def generate_narrative(self, genre: str) -> GameNarrative:
        """Generate game narrative."""
        ...


@runtime_checkable  
class AssetGenerator(Protocol):
    """Protocol for asset generation tools."""
    
    async def generate_sprite(self, name: str, style: str) -> Path:
        """Generate a sprite."""
        ...
    
    async def generate_background(self, scene: str, style: str) -> Path:
        """Generate a background."""
        ...
    
    async def generate_audio(self, type: str, description: str) -> Path:
        """Generate audio asset."""
        ...


@runtime_checkable
class CodeGenerator(Protocol):
    """Protocol for code generation tools."""
    
    async def generate_game_code(self, spec: GameSpec) -> CodeRepository:
        """Generate complete game code."""
        ...
    
    async def generate_module(self, name: str, purpose: str) -> str:
        """Generate a single module."""
        ...


@runtime_checkable
class EducationalGenerator(Protocol):
    """Protocol for educational content generation."""
    
    async def create_lesson(self, topic: str, level: str) -> LessonPlan:
        """Create a lesson plan."""
        ...
    
    async def identify_moment(self, code: str) -> TeachableMoment:
        """Identify teachable moment."""
        ...
    
    async def create_exercise(self, concept: str) -> str:
        """Create practice exercise."""
        ...


@runtime_checkable
class AssetRegistry(Protocol):
    """Protocol for asset registry."""
    
    def register_asset(self, name: str, path: str, asset_type: str, **metadata) -> None:
        """Register an asset."""
        ...
    
    def get_asset(self, name: str) -> str | None:
        """Get asset path by name."""
        ...
    
    def get_assets_by_type(self, asset_type: str) -> dict[str, str]:
        """Get all assets of a type."""
        ...
    
    def get_assets_for_game(self, game_name: str) -> dict[str, dict[str, str]]:
        """Get all assets for a game."""
        ...


@runtime_checkable
class TemplateRenderer(Protocol):
    """Protocol for template rendering."""
    
    def render(self, template_name: str, **context) -> str:
        """Render a template."""
        ...
    
    async def render_async(self, template_name: str, **context) -> str:
        """Async render a template."""
        ...
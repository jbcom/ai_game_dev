"""
Interactive Variant System for AI Game Development

Provides A/B testing capabilities with live preview and feature flags.
Works across all engines (pygame, godot, bevy) as a core Game Workshop feature.
"""

from .variant_system import (
    VariantType,
    VariantChoice,
    VariantPoint,
    FeatureFlags,
    VariantGenerator,
    VariantCodeInjector,
    InteractiveVariantSystem,
    create_variant_enabled_game
)

__all__ = [
    "VariantType",
    "VariantChoice", 
    "VariantPoint",
    "FeatureFlags",
    "VariantGenerator",
    "VariantCodeInjector",
    "InteractiveVariantSystem",
    "create_variant_enabled_game"
]
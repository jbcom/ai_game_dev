"""
Interactive Variant System for AI Game Development

Provides A/B testing capabilities with live preview and feature flags.
Works across all engines (pygame, godot, bevy) as a core Game Workshop feature.
Also provides OpenAI function tools for generating variants.
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

from .tool import (
    generate_mechanic_variants,
    identify_interactive_moments,
    apply_variant_to_code,
    generate_educational_variants,
    create_variant_pack,
)

__all__ = [
    # Original variant system
    "VariantType",
    "VariantChoice", 
    "VariantPoint",
    "FeatureFlags",
    "VariantGenerator",
    "VariantCodeInjector",
    "InteractiveVariantSystem",
    "create_variant_enabled_game",
    # OpenAI function tools
    "generate_mechanic_variants",
    "identify_interactive_moments",
    "apply_variant_to_code",
    "generate_educational_variants",
    "create_variant_pack",
]
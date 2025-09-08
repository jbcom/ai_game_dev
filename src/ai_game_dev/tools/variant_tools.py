"""
Variant generation tools for creating game variations.
Helps create A/B testable game mechanics and features.
"""
from pathlib import Path
from typing import Any, Literal

from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field


class VariantInput(BaseModel):
    """Input for variant generation."""
    feature_type: Literal["movement", "combat", "ui", "gameplay", "visual"] = Field(
        description="Type of feature to create variants for"
    )
    base_implementation: str = Field(
        description="Base code or description to create variants from"
    )
    variant_count: int = Field(
        default=2,
        description="Number of variants to generate"
    )
    engine: Literal["pygame", "godot", "bevy"] = Field(
        description="Target game engine"
    )
    educational_mode: bool = Field(
        default=False,
        description="Include educational explanations"
    )


class VariantTool:
    """Tool for generating game feature variants."""
    
    def generate_variants(
        self,
        feature_type: str,
        base_implementation: str,
        variant_count: int = 2,
        engine: str = "pygame",
        educational_mode: bool = False,
        **kwargs
    ) -> dict[str, Any]:
        """Generate variants of a game feature."""
        
        variants = []
        
        if feature_type == "movement":
            # Generate movement variants
            if engine == "pygame":
                variants = self._generate_pygame_movement_variants(
                    base_implementation, 
                    variant_count
                )
            elif engine == "godot":
                variants = self._generate_godot_movement_variants(
                    base_implementation,
                    variant_count
                )
            elif engine == "bevy":
                variants = self._generate_bevy_movement_variants(
                    base_implementation,
                    variant_count
                )
        
        elif feature_type == "combat":
            # Generate combat variants
            variants = self._generate_combat_variants(
                base_implementation,
                variant_count,
                engine
            )
        
        elif feature_type == "ui":
            # Generate UI variants
            variants = self._generate_ui_variants(
                base_implementation,
                variant_count,
                engine
            )
        
        # Add educational content if requested
        if educational_mode and variants:
            for variant in variants:
                variant["educational_note"] = self._add_educational_content(
                    feature_type,
                    variant.get("name", "")
                )
        
        return {
            "status": "generated",
            "feature_type": feature_type,
            "variants": variants,
            "config": self._generate_feature_config(variants)
        }
    
    def _generate_pygame_movement_variants(
        self, 
        base: str, 
        count: int
    ) -> list[dict[str, Any]]:
        """Generate Pygame movement variants."""
        variants = []
        
        # Variant 1: Grid-based movement
        if count >= 1:
            variants.append({
                "name": "grid_movement",
                "code": '''# Grid-based movement
GRID_SIZE = 32

def move_player(self, dx, dy):
    """Move player on grid."""
    new_x = self.rect.x + dx * GRID_SIZE
    new_y = self.rect.y + dy * GRID_SIZE
    
    # Check bounds
    if 0 <= new_x < SCREEN_WIDTH - GRID_SIZE:
        self.rect.x = new_x
    if 0 <= new_y < SCREEN_HEIGHT - GRID_SIZE:
        self.rect.y = new_y''',
                "description": "Discrete grid-based movement"
            })
        
        # Variant 2: Smooth movement
        if count >= 2:
            variants.append({
                "name": "smooth_movement",
                "code": '''# Smooth continuous movement
def update(self, dt):
    """Update with smooth movement."""
    keys = pygame.key.get_pressed()
    
    # Calculate velocity
    self.velocity.x = 0
    self.velocity.y = 0
    
    if keys[pygame.K_LEFT]:
        self.velocity.x = -self.speed
    if keys[pygame.K_RIGHT]:
        self.velocity.x = self.speed
    if keys[pygame.K_UP]:
        self.velocity.y = -self.speed
    if keys[pygame.K_DOWN]:
        self.velocity.y = self.speed
    
    # Apply movement
    self.rect.x += self.velocity.x * dt
    self.rect.y += self.velocity.y * dt''',
                "description": "Smooth continuous movement with velocity"
            })
        
        return variants
    
    def _generate_godot_movement_variants(
        self,
        base: str,
        count: int
    ) -> list[dict[str, Any]]:
        """Generate Godot movement variants."""
        variants = []
        
        if count >= 1:
            variants.append({
                "name": "physics_movement",
                "code": '''# Physics-based movement
extends CharacterBody2D

@export var speed = 300.0

func _physics_process(delta):
    var input_dir = Input.get_vector("ui_left", "ui_right", "ui_up", "ui_down")
    velocity = input_dir * speed
    move_and_slide()''',
                "description": "Physics-based character movement"
            })
        
        return variants
    
    def _generate_bevy_movement_variants(
        self,
        base: str,
        count: int
    ) -> list[dict[str, Any]]:
        """Generate Bevy movement variants."""
        # Bevy-specific variants would go here
        return []
    
    def _generate_combat_variants(
        self,
        base: str,
        count: int,
        engine: str
    ) -> list[dict[str, Any]]:
        """Generate combat system variants."""
        variants = []
        
        # Turn-based variant
        variants.append({
            "name": "turn_based_combat",
            "description": "Turn-based combat system",
            "features": ["action_queue", "turn_order", "action_points"]
        })
        
        # Real-time variant
        if count >= 2:
            variants.append({
                "name": "realtime_combat", 
                "description": "Real-time action combat",
                "features": ["cooldowns", "combos", "dodge_mechanics"]
            })
        
        return variants
    
    def _generate_ui_variants(
        self,
        base: str,
        count: int,
        engine: str
    ) -> list[dict[str, Any]]:
        """Generate UI layout variants."""
        return [
            {
                "name": "minimal_ui",
                "description": "Minimalist UI with essential info only"
            },
            {
                "name": "detailed_ui",
                "description": "Detailed UI with all stats visible"
            }
        ][:count]
    
    def _add_educational_content(
        self,
        feature_type: str,
        variant_name: str
    ) -> str:
        """Add educational explanations."""
        educational_notes = {
            "movement": {
                "grid_movement": "Grid movement is easier to implement and debug. It's great for puzzle games and strategy games.",
                "smooth_movement": "Smooth movement feels more natural but requires delta time and velocity calculations."
            },
            "combat": {
                "turn_based_combat": "Turn-based combat allows players to think strategically without time pressure.",
                "realtime_combat": "Real-time combat creates excitement and tests reflexes."
            }
        }
        
        return educational_notes.get(feature_type, {}).get(
            variant_name,
            f"This variant demonstrates different approaches to {feature_type}."
        )
    
    def _generate_feature_config(self, variants: list[dict[str, Any]]) -> dict[str, Any]:
        """Generate feature toggle configuration."""
        config = {
            "features": {},
            "default_variant": variants[0]["name"] if variants else None
        }
        
        for variant in variants:
            config["features"][variant["name"]] = {
                "enabled": variant == variants[0],  # First variant is default
                "description": variant.get("description", "")
            }
        
        return config


# Create the structured tool
variant_tool = StructuredTool.from_function(
    func=VariantTool().generate_variants,
    name="generate_variants",
    description="Generate A/B testable variants of game features",
    args_schema=VariantInput
)
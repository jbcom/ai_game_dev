"""
Revolutionary Variant Points System for Interactive Game Development

Enables A/B testing of game mechanics with live preview and feature flags.
Students can experiment with different approaches and see immediate results.
Works across all engines (pygame, godot, bevy) with unified configuration.
"""

import asyncio
import toml
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, field
from pathlib import Path
from enum import Enum

try:
    from langchain_core.messages import HumanMessage, SystemMessage
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False


class VariantType(Enum):
    """Types of variants that can be generated."""
    VISUAL = "visual"  # Different visual approaches (hex vs square tiles)
    MECHANICAL = "mechanical"  # Different game mechanics (turn-based vs real-time)
    ALGORITHMIC = "algorithmic"  # Different algorithms (pathfinding, AI behavior)
    ARCHITECTURAL = "architectural"  # Different code organization approaches
    PERFORMANCE = "performance"  # Different optimization strategies


@dataclass
class VariantChoice:
    """Represents a single variant choice (A or B path)."""
    id: str
    name: str
    description: str
    code_snippet: str
    assets_needed: List[str] = field(default_factory=list)
    performance_impact: str = "neutral"  # "better", "worse", "neutral"
    difficulty_level: str = "same"  # "easier", "harder", "same"
    educational_notes: str = ""


@dataclass
class VariantPoint:
    """Represents a decision point with multiple implementation choices."""
    id: str
    name: str
    description: str
    variant_type: VariantType
    context: str  # Where in the code this appears
    educational_value: str  # What this teaches
    choices: List[VariantChoice]
    default_choice: str  # ID of default choice (A)
    engine_compatibility: List[str] = field(default_factory=lambda: ["pygame", "godot", "bevy"])
    
    def get_choice(self, choice_id: str) -> Optional[VariantChoice]:
        """Get a specific choice by ID."""
        return next((choice for choice in self.choices if choice.id == choice_id), None)
    
    def get_default_choice(self) -> VariantChoice:
        """Get the default choice."""
        return self.get_choice(self.default_choice)


@dataclass
class FeatureFlags:
    """Feature flag configuration for variant system."""
    flags: Dict[str, str] = field(default_factory=dict)  # variant_id -> choice_id
    
    def set_variant(self, variant_id: str, choice_id: str):
        """Set which choice is active for a variant."""
        self.flags[variant_id] = choice_id
    
    def get_active_choice(self, variant_id: str, default: str = "a") -> str:
        """Get the active choice for a variant."""
        return self.flags.get(variant_id, default)
    
    def to_toml(self) -> str:
        """Export to TOML format."""
        config = {
            "features": {
                "description": "Feature flags for game variants - toggle A/B implementations",
                "variants": self.flags
            }
        }
        return toml.dumps(config)
    
    @classmethod
    def from_toml(cls, toml_content: str) -> 'FeatureFlags':
        """Load from TOML content."""
        config = toml.loads(toml_content)
        flags = config.get("features", {}).get("variants", {})
        return cls(flags=flags)


class VariantGenerator:
    """Generates variant points and choices using AI analysis."""
    
    def __init__(self, llm_manager):
        self.llm_manager = llm_manager
        self.common_variants = self._build_common_variants()
    
    def _build_common_variants(self) -> Dict[str, VariantPoint]:
        """Build library of common variant patterns."""
        return {
            "grid_system": VariantPoint(
                id="grid_system",
                name="Grid System",
                description="Choose between different tile grid systems",
                variant_type=VariantType.VISUAL,
                context="Map/level generation",
                educational_value="Learn about coordinate systems and spatial organization",
                choices=[
                    VariantChoice(
                        id="a_square",
                        name="Square Grid",
                        description="Traditional square tiles - easier to understand",
                        code_snippet="# Square grid system\ngrid_size = 32\nx_pos = col * grid_size\ny_pos = row * grid_size",
                        difficulty_level="easier",
                        educational_notes="Square grids use simple x,y coordinates"
                    ),
                    VariantChoice(
                        id="b_hexagonal",
                        name="Hexagonal Grid",
                        description="Hexagonal tiles - more complex but visually interesting",
                        code_snippet="# Hexagonal grid system\nimport math\nhex_size = 32\nx_pos = col * hex_size * 1.5\ny_pos = row * hex_size * math.sqrt(3) + (col % 2) * hex_size * math.sqrt(3) / 2",
                        difficulty_level="harder",
                        educational_notes="Hexagonal grids require trigonometry and offset calculations"
                    )
                ],
                default_choice="a_square"
            ),
            
            "combat_system": VariantPoint(
                id="combat_system", 
                name="Combat System",
                description="Choose between different combat mechanics",
                variant_type=VariantType.MECHANICAL,
                context="Player vs enemy interactions",
                educational_value="Learn about game loops, timing, and state management",
                choices=[
                    VariantChoice(
                        id="a_turn_based",
                        name="Turn-Based Combat",
                        description="Players take turns - easier to program and understand",
                        code_snippet="# Turn-based combat\nif current_turn == 'player':\n    handle_player_action()\n    current_turn = 'enemy'\nelse:\n    handle_enemy_action()\n    current_turn = 'player'",
                        difficulty_level="easier",
                        educational_notes="Turn-based systems use simple state switching"
                    ),
                    VariantChoice(
                        id="b_realtime",
                        name="Real-Time Combat", 
                        description="Continuous action - more exciting but complex timing",
                        code_snippet="# Real-time combat\nattack_cooldown -= delta_time\nif attack_key_pressed and attack_cooldown <= 0:\n    perform_attack()\n    attack_cooldown = attack_delay",
                        difficulty_level="harder",
                        educational_notes="Real-time systems require timing and delta calculations"
                    )
                ],
                default_choice="a_turn_based"
            ),
            
            "movement_system": VariantPoint(
                id="movement_system",
                name="Player Movement",
                description="Choose how the player character moves",
                variant_type=VariantType.MECHANICAL,
                context="Player input handling",
                educational_value="Learn about input processing and physics",
                choices=[
                    VariantChoice(
                        id="a_discrete",
                        name="Grid-Based Movement",
                        description="Move one tile at a time - like classic RPGs",
                        code_snippet="# Grid-based movement\nif key_pressed('UP') and not moving:\n    target_y -= grid_size\n    moving = True",
                        difficulty_level="easier",
                        educational_notes="Discrete movement uses simple position updates"
                    ),
                    VariantChoice(
                        id="b_continuous",
                        name="Smooth Movement",
                        description="Fluid movement with momentum - more natural feeling",
                        code_snippet="# Smooth movement\nvelocity_x += acceleration * input_x * delta_time\nvelocity_x *= friction\nposition_x += velocity_x * delta_time",
                        difficulty_level="harder", 
                        educational_notes="Smooth movement requires velocity, acceleration, and physics"
                    )
                ],
                default_choice="a_discrete"
            ),
            
            "ai_behavior": VariantPoint(
                id="ai_behavior",
                name="Enemy AI",
                description="Choose how enemies behave and make decisions",
                variant_type=VariantType.ALGORITHMIC,
                context="Enemy decision making",
                educational_value="Learn about algorithms and decision trees",
                choices=[
                    VariantChoice(
                        id="a_simple",
                        name="Simple Chase AI",
                        description="Enemies move directly toward player - predictable but easy",
                        code_snippet="# Simple chase AI\nif player_x > enemy_x:\n    enemy_x += enemy_speed\nelif player_x < enemy_x:\n    enemy_x -= enemy_speed",
                        difficulty_level="easier",
                        educational_notes="Simple AI uses basic conditionals"
                    ),
                    VariantChoice(
                        id="b_pathfinding",
                        name="Smart Pathfinding AI",
                        description="Enemies navigate around obstacles - more realistic behavior",
                        code_snippet="# Pathfinding AI\npath = find_path(enemy_pos, player_pos, obstacles)\nif path:\n    next_pos = path[1]  # Next step in path\n    move_towards(next_pos)",
                        difficulty_level="harder",
                        educational_notes="Pathfinding AI uses algorithms like A* and graph traversal"
                    )
                ],
                default_choice="a_simple"
            )
        }
    
    async def detect_variant_opportunities(
        self, 
        code: str, 
        engine: str,
        educational_context: Optional[Dict[str, Any]] = None
    ) -> List[VariantPoint]:
        """Analyze code to detect opportunities for variant implementations."""
        
        detected_variants = []
        
        # Pattern-based detection
        for variant_id, variant in self.common_variants.items():
            if engine in variant.engine_compatibility:
                if self._code_matches_variant_pattern(code, variant):
                    detected_variants.append(variant)
        
        # AI-enhanced detection for custom variants
        if LANGCHAIN_AVAILABLE:
            ai_variants = await self._ai_detect_variants(code, engine, educational_context)
            detected_variants.extend(ai_variants)
        
        return detected_variants
    
    def _code_matches_variant_pattern(self, code: str, variant: VariantPoint) -> bool:
        """Check if code contains patterns that match a variant opportunity."""
        
        patterns = {
            "grid_system": ["grid", "tile", "cell", "map", "level"],
            "combat_system": ["attack", "damage", "health", "combat", "battle"],
            "movement_system": ["move", "position", "velocity", "input", "control"],
            "ai_behavior": ["enemy", "ai", "behavior", "chase", "patrol"]
        }
        
        if variant.id in patterns:
            return any(pattern in code.lower() for pattern in patterns[variant.id])
        
        return False
    
    async def _ai_detect_variants(
        self, 
        code: str, 
        engine: str,
        educational_context: Optional[Dict[str, Any]] = None
    ) -> List[VariantPoint]:
        """Use AI to detect custom variant opportunities in code."""
        
        prompt = f"""
        Analyze this {engine} game code for opportunities to offer A/B variant choices:
        
        ```{engine}
        {code}
        ```
        
        Look for places where we could offer the developer different implementation approaches that would:
        1. Teach different programming concepts
        2. Show different game design philosophies  
        3. Demonstrate performance trade-offs
        4. Offer different complexity levels
        
        For each opportunity, suggest:
        - What the choice is between (A vs B)
        - Why each option is educationally valuable
        - How the player would see/feel the difference
        - Which option is better for beginners
        
        Focus on choices that create visible, experiential differences in the game.
        """
        
        try:
            llm = await self.llm_manager.get_model("gpt-4o")
            response = await llm.ainvoke([
                SystemMessage(content="You are an expert game developer who identifies opportunities for educational A/B testing."),
                HumanMessage(content=prompt)
            ])
            
            # Parse AI response into variant points (simplified for now)
            return self._parse_ai_variants(response.content, engine)
            
        except Exception:
            return []
    
    def _parse_ai_variants(self, ai_response: str, engine: str) -> List[VariantPoint]:
        """Parse AI response into VariantPoint objects."""
        # For now, return empty list - in production would parse structured AI output
        return []


class VariantCodeInjector:
    """Injects variant points into generated code with feature flag support."""
    
    def __init__(self):
        self.injection_patterns = {
            "pygame": self._pygame_injection_patterns(),
            "godot": self._godot_injection_patterns(), 
            "bevy": self._bevy_injection_patterns()
        }
    
    def inject_variants(
        self, 
        code: str, 
        variants: List[VariantPoint], 
        engine: str,
        feature_flags: FeatureFlags
    ) -> Tuple[str, str]:
        """
        Inject variant points into code with feature flag system.
        Returns (enhanced_code, features_toml)
        """
        
        enhanced_code = code
        
        for variant in variants:
            if engine in variant.engine_compatibility:
                enhanced_code = self._inject_single_variant(
                    enhanced_code, variant, engine, feature_flags
                )
        
        # Generate features.toml
        features_toml = feature_flags.to_toml()
        
        return enhanced_code, features_toml
    
    def _inject_single_variant(
        self, 
        code: str, 
        variant: VariantPoint, 
        engine: str,
        feature_flags: FeatureFlags
    ) -> str:
        """Inject a single variant point into code."""
        
        # Get the injection pattern for this engine
        pattern = self.injection_patterns.get(engine, {})
        
        # Build feature flag check
        flag_check = pattern.get("flag_check", "").format(
            variant_id=variant.id,
            choice_a_id=variant.choices[0].id,
            choice_b_id=variant.choices[1].id if len(variant.choices) > 1 else "b"
        )
        
        # Build choice implementations
        choice_a_code = variant.choices[0].code_snippet
        choice_b_code = variant.choices[1].code_snippet if len(variant.choices) > 1 else "# Alternative implementation"
        
        # Create the full variant injection
        variant_injection = pattern.get("template", "").format(
            flag_check=flag_check,
            variant_id=variant.id,
            choice_a_code=choice_a_code,
            choice_b_code=choice_b_code,
            variant_description=variant.description
        )
        
        # Find injection point and insert
        injection_point = self._find_injection_point(code, variant)
        if injection_point != -1:
            lines = code.split('\n')
            lines.insert(injection_point, variant_injection)
            code = '\n'.join(lines)
        
        return code
    
    def _find_injection_point(self, code: str, variant: VariantPoint) -> int:
        """Find the best place to inject variant code."""
        lines = code.split('\n')
        
        # Look for context clues based on variant type
        context_keywords = {
            VariantType.VISUAL: ["render", "draw", "display", "screen"],
            VariantType.MECHANICAL: ["update", "tick", "loop", "game"],
            VariantType.ALGORITHMIC: ["calculate", "process", "compute"],
            VariantType.ARCHITECTURAL: ["init", "setup", "create"]
        }
        
        keywords = context_keywords.get(variant.variant_type, [])
        
        for i, line in enumerate(lines):
            if any(keyword in line.lower() for keyword in keywords):
                return i + 1
        
        # Default: insert near the end
        return len(lines) - 2
    
    def _pygame_injection_patterns(self) -> Dict[str, str]:
        """Injection patterns for pygame."""
        return {
            "flag_check": "config.get_variant('{variant_id}') == '{choice_a_id}'",
            "template": """
# Variant Point: {variant_description}
if {flag_check}:
    {choice_a_code}
else:
    {choice_b_code}
"""
        }
    
    def _godot_injection_patterns(self) -> Dict[str, str]:
        """Injection patterns for Godot/GDScript."""
        return {
            "flag_check": "GameConfig.get_variant('{variant_id}') == '{choice_a_id}'",
            "template": """
# Variant Point: {variant_description}
if {flag_check}:
	{choice_a_code}
else:
	{choice_b_code}
"""
        }
    
    def _bevy_injection_patterns(self) -> Dict[str, str]:
        """Injection patterns for Bevy/Rust."""
        return {
            "flag_check": "config.variants.{variant_id} == VariantChoice::{choice_a_id}",
            "template": """
// Variant Point: {variant_description}
if {flag_check} {{
    {choice_a_code}
}} else {{
    {choice_b_code}
}}
"""
        }


class InteractiveVariantSystem:
    """Manages interactive variant selection and preview system."""
    
    def __init__(self, llm_manager):
        self.variant_generator = VariantGenerator(llm_manager)
        self.code_injector = VariantCodeInjector()
        self.active_variants = {}
        self.preview_cache = {}
    
    async def generate_interactive_game_with_variants(
        self, 
        base_code: str, 
        engine: str,
        educational_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Generate a game with interactive variant points."""
        
        # Detect variant opportunities
        variants = await self.variant_generator.detect_variant_opportunities(
            base_code, engine, educational_context
        )
        
        # Create default feature flags (all A choices)
        feature_flags = FeatureFlags()
        for variant in variants:
            feature_flags.set_variant(variant.id, variant.default_choice)
        
        # Inject variants into code
        enhanced_code, features_toml = self.code_injector.inject_variants(
            base_code, variants, engine, feature_flags
        )
        
        # Generate preview data for each variant choice
        preview_data = await self._generate_preview_data(variants, engine)
        
        return {
            "enhanced_code": enhanced_code,
            "features_toml": features_toml,
            "variants": [self._variant_to_dict(v) for v in variants],
            "preview_data": preview_data,
            "engine": engine,
            "interactive_points": len(variants)
        }
    
    async def _generate_preview_data(
        self, 
        variants: List[VariantPoint], 
        engine: str
    ) -> Dict[str, Any]:
        """Generate preview data for split-screen comparison."""
        
        preview_data = {}
        
        for variant in variants:
            variant_previews = {}
            
            for choice in variant.choices:
                # Generate preview description and visual hints
                variant_previews[choice.id] = {
                    "name": choice.name,
                    "description": choice.description,
                    "code_snippet": choice.code_snippet,
                    "educational_notes": choice.educational_notes,
                    "difficulty": choice.difficulty_level,
                    "performance_impact": choice.performance_impact,
                    "visual_hint": self._generate_visual_hint(choice, engine)
                }
            
            preview_data[variant.id] = {
                "name": variant.name,
                "type": variant.variant_type.value,
                "educational_value": variant.educational_value,
                "choices": variant_previews
            }
        
        return preview_data
    
    def _generate_visual_hint(self, choice: VariantChoice, engine: str) -> str:
        """Generate a visual description of what this choice looks like."""
        
        visual_hints = {
            "a_square": "🟦 Orderly grid of square tiles, like Tetris or chess",
            "b_hexagonal": "⬡ Honeycomb pattern of hexagonal tiles, like Civilization",
            "a_turn_based": "⏸️ Classic turn-by-turn combat, like Final Fantasy",
            "b_realtime": "⚡ Fast-paced action combat, like Zelda",
            "a_discrete": "📐 Snap-to-grid movement, like classic Pac-Man",
            "b_continuous": "🏃 Smooth flowing movement, like modern platformers",
            "a_simple": "🎯 Enemies beeline directly toward player",
            "b_pathfinding": "🧠 Enemies intelligently navigate around obstacles"
        }
        
        return visual_hints.get(choice.id, f"🎮 {choice.name} implementation")
    
    def _variant_to_dict(self, variant: VariantPoint) -> Dict[str, Any]:
        """Convert VariantPoint to dictionary for JSON serialization."""
        return {
            "id": variant.id,
            "name": variant.name,
            "description": variant.description,
            "type": variant.variant_type.value,
            "context": variant.context,
            "educational_value": variant.educational_value,
            "choices": [{
                "id": choice.id,
                "name": choice.name,
                "description": choice.description,
                "difficulty": choice.difficulty_level,
                "performance": choice.performance_impact
            } for choice in variant.choices],
            "default_choice": variant.default_choice
        }


async def create_variant_enabled_game(
    base_code: str,
    engine: str = "pygame",
    llm_manager = None
) -> Dict[str, Any]:
    """Factory function to create a game with variant system enabled."""
    
    if llm_manager is None:
        from ..models.llm_manager import LLMManager
        llm_manager = LLMManager()
    
    variant_system = InteractiveVariantSystem(llm_manager)
    
    return await variant_system.generate_interactive_game_with_variants(
        base_code, engine
    )
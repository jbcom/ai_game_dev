"""
OpenAI function tools for game mechanic variants.
"""
from pathlib import Path
from typing import Literal, Any
import json

from openai import AsyncOpenAI
from pydantic import BaseModel

from agents import function_tool

from ai_game_dev.constants import OPENAI_MODELS
from ai_game_dev.variants.variant_system import InteractiveVariantSystem


class GameVariant(BaseModel):
    """A game mechanic variant."""
    name: str
    description: str
    code: str
    difficulty: Literal["easy", "medium", "hard"]
    educational_value: str | None = None


@function_tool(strict_mode=False)
async def generate_mechanic_variants(
    base_code: str,
    mechanic_type: Literal["movement", "combat", "inventory", "puzzles", "ai"],
    count: int = 3,
    difficulty_range: list[Literal["easy", "medium", "hard"]] | None = None,
    educational_mode: bool = False,
) -> list[GameVariant]:
    """Generate variants of a game mechanic using GPT-5.
    
    Args:
        base_code: The original code implementing the mechanic
        mechanic_type: Type of game mechanic
        count: Number of variants to generate
        difficulty_range: Difficulties to include
        educational_mode: Add educational explanations
        
    Returns:
        List of game mechanic variants
    """
    client = AsyncOpenAI()
    
    if not difficulty_range:
        difficulty_range = ["easy", "medium", "hard"]
    
    prompt = f"""Generate {count} creative variants of this {mechanic_type} game mechanic.

Original Code:
```python
{base_code}
```

Requirements:
1. Each variant should offer a different gameplay experience
2. Maintain the same interface/API as the original
3. Include variants for these difficulties: {', '.join(difficulty_range)}
4. Be creative - add juice, game feel, or new mechanics
5. Keep code clean and well-commented

Generate as a JSON array with each variant having:
- name: Creative name for the variant
- description: What makes it different
- code: Complete implementation
- difficulty: easy/medium/hard
{"- educational_value: What programming concept it teaches" if educational_mode else ""}
"""
    
    response = await client.chat.completions.create(
        model=OPENAI_MODELS["text"]["code_generation"],
        messages=[
            {"role": "system", "content": "You are a creative game developer who specializes in creating engaging game mechanic variations."},
            {"role": "user", "content": prompt}
        ],
        response_format={"type": "json_object"},
        temperature=0.8  # Higher creativity for variants
    )
    
    variants_data = json.loads(response.choices[0].message.content)
    variants = []
    
    for variant_data in variants_data.get("variants", [])[:count]:
        variant = GameVariant(
            name=variant_data["name"],
            description=variant_data["description"],
            code=variant_data["code"],
            difficulty=variant_data["difficulty"],
            educational_value=variant_data.get("educational_value") if educational_mode else None
        )
        variants.append(variant)
    
    return variants


@function_tool(strict_mode=False)
async def identify_interactive_moments(
    game_code: str,
    game_description: str,
    focus_areas: list[Literal["mechanics", "ui", "progression", "narrative"]] | None = None,
) -> dict[str, list[dict[str, Any]]]:
    """Identify moments in a game where variants could enhance interactivity.
    
    Args:
        game_code: The game's source code
        game_description: Description of the game
        focus_areas: Specific areas to focus on
        
    Returns:
        Dictionary of interactive moments by category
    """
    client = AsyncOpenAI()
    
    if not focus_areas:
        focus_areas = ["mechanics", "ui", "progression", "narrative"]
    
    prompt = f"""Analyze this game code and identify opportunities for enhanced interactivity.

Game Description: {game_description}

Code:
```python
{game_code}
```

Focus on these areas: {', '.join(focus_areas)}

For each area, identify:
1. Current implementation
2. Opportunity for enhancement
3. Suggested variant approach
4. Impact on player experience

Return as JSON with structure:
{{
    "mechanics": [
        {{
            "location": "line numbers or function name",
            "current": "what it does now",
            "opportunity": "what could be improved",
            "variant": "suggested change",
            "impact": "player experience benefit"
        }}
    ],
    // ... other focus areas
}}
"""
    
    response = await client.chat.completions.create(
        model=OPENAI_MODELS["text"]["default"],
        messages=[
            {"role": "system", "content": "You are a game design analyst specializing in player engagement and interactivity."},
            {"role": "user", "content": prompt}
        ],
        response_format={"type": "json_object"},
        temperature=0.5
    )
    
    moments = json.loads(response.choices[0].message.content)
    return moments


@function_tool(strict_mode=False)
async def apply_variant_to_code(
    original_code: str,
    variant: GameVariant,
    integration_points: list[str] | None = None,
) -> str:
    """Apply a variant to existing game code.
    
    Args:
        original_code: The original game code
        variant: The variant to apply
        integration_points: Specific points to integrate (function names, etc.)
        
    Returns:
        Modified code with variant applied
    """
    client = AsyncOpenAI()
    
    prompt = f"""Integrate this game mechanic variant into the existing code.

Original Code:
```python
{original_code}
```

Variant to Apply:
Name: {variant.name}
Description: {variant.description}

Variant Code:
```python
{variant.code}
```

{"Integration Points: " + ", ".join(integration_points) if integration_points else ""}

Requirements:
1. Seamlessly integrate the variant
2. Preserve existing functionality where appropriate
3. Add smooth transitions if needed
4. Include comments explaining the variant
5. Ensure no breaking changes to the game

Return the complete modified code.
"""
    
    response = await client.chat.completions.create(
        model=OPENAI_MODELS["text"]["code_generation"],
        messages=[
            {"role": "system", "content": "You are an expert at code integration and refactoring."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3  # Lower temperature for code modification
    )
    
    return response.choices[0].message.content


@function_tool(strict_mode=False)
async def generate_educational_variants(
    concept: str,
    base_mechanic: str,
    student_level: Literal["beginner", "intermediate", "advanced"] = "beginner",
    count: int = 2,
) -> list[GameVariant]:
    """Generate educational variants that teach programming concepts.
    
    Args:
        concept: Programming concept to teach (loops, conditionals, etc.)
        base_mechanic: Base game mechanic to modify
        student_level: Target student level
        count: Number of variants
        
    Returns:
        Educational game variants
    """
    # Use the existing variant system with educational mode
    educational_context = f"""
This is for teaching {concept} to {student_level} students.
The mechanic should demonstrate the concept clearly.
"""
    
    variants = await generate_mechanic_variants(
        base_code=base_mechanic + "\n\n# Educational Context: " + educational_context,
        mechanic_type="movement",  # Generic type
        count=count,
        difficulty_range=[student_level],
        educational_mode=True
    )
    
    # Enhance with educational metadata
    for variant in variants:
        variant.educational_value = f"Teaches {concept} through {variant.name}"
    
    return variants


@function_tool(strict_mode=False)
async def create_variant_pack(
    game_path: str,
    variant_types: list[str] | None = None,
    output_dir: str | None = None,
) -> dict[str, Any]:
    """Create a complete variant pack for a game.
    
    Args:
        game_path: Path to the game's main file
        variant_types: Types of variants to create
        output_dir: Where to save variant files
        
    Returns:
        Complete variant pack with all modifications
    """
    if not variant_types:
        variant_types = ["movement", "combat", "puzzles"]
    
    # Read the game code
    game_code = Path(game_path).read_text()
    
    results = {
        "variants": {},
        "interactive_moments": {},
        "files": []
    }
    
    # Identify interactive moments
    moments = await identify_interactive_moments(
        game_code=game_code,
        game_description="Game from " + game_path
    )
    results["interactive_moments"] = moments
    
    # Generate variants for each type
    for variant_type in variant_types:
        # Extract relevant code section (simplified)
        # In a real implementation, would parse and extract specific mechanics
        variants = await generate_mechanic_variants(
            base_code=game_code[:1000],  # First 1000 chars as sample
            mechanic_type=variant_type,
            count=2
        )
        results["variants"][variant_type] = [v.model_dump() for v in variants]
        
        # Save variant files if output directory specified
        if output_dir:
            base_dir = Path(output_dir)
            base_dir.mkdir(parents=True, exist_ok=True)
            
            for i, variant in enumerate(variants):
                variant_file = base_dir / f"{variant_type}_variant_{i}.py"
                variant_file.write_text(variant.code)
                results["files"].append(str(variant_file))
    
    return results
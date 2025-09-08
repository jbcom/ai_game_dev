"""
Simple OpenAI-based game development agent.
Replaces complex LangChain/LangGraph orchestration.
"""
import asyncio
from typing import Any, Literal

from agents import Agent, Runner
from pydantic import BaseModel

from ai_game_dev.graphics import (
    generate_game_sprite,
    generate_game_background,
    generate_ui_pack,
)
from ai_game_dev.audio import (
    generate_voice_acting,
    generate_sound_effect,
    generate_background_music,
)
from ai_game_dev.fonts import render_game_text
from ai_game_dev.variants import generate_mechanic_variants
from ai_game_dev.text import (
    generate_dialogue_tree,
    generate_quest_chain,
    generate_code_repository,
    find_literary_inspirations,
    enhance_game_narrative,
    create_lesson_plan,
    identify_teachable_moment,
    create_educational_dialogue,
)


class GameSpec(BaseModel):
    """Game specification."""
    title: str
    description: str
    engine: Literal["pygame", "godot", "bevy"] = "pygame"
    features: list[str] = []
    art_style: str = "pixel art"
    genre: str = "platformer"
    educational_mode: bool = False


class GameProject(BaseModel):
    """Complete game project."""
    spec: GameSpec
    code_files: dict[str, str]
    assets: dict[str, str]
    dialogue_files: dict[str, str] = {}
    quest_data: dict[str, Any] = {}
    teachable_moments: list[dict[str, Any]] = []


# Workshop Agent - Creates games
workshop_agent = Agent(
    name="Game Workshop",
    instructions="""You are a game development assistant that helps create complete games.
    
Your process:
1. Understand what kind of game the user wants
2. Create a game specification
3. Generate all necessary code
4. Create required assets (sprites, sounds, music)
5. Add dialogue and quests if needed
6. Provide a complete, playable game

Be creative but practical. Focus on making fun, complete games.""",
    tools=[
        generate_code_repository,
        generate_game_sprite,
        generate_game_background,
        generate_ui_pack,
        generate_sound_effect,
        generate_background_music,
        generate_voice_acting,
        generate_dialogue_tree,
        generate_quest_chain,
        find_literary_inspirations,
        enhance_game_narrative,
    ]
)


# Academy Agent - Educational game creation
academy_agent = Agent(
    name="Arcade Academy", 
    instructions="""You are Professor Pixel, an educational game development tutor.
    
Your mission:
1. Create games that teach programming concepts
2. Identify teachable moments in code
3. Add educational comments and exercises
4. Make learning fun through game development
5. Adapt to the student's skill level

Always be encouraging and explain concepts clearly.""",
    tools=[
        generate_code_repository,  # With educational mode
        create_lesson_plan,
        identify_teachable_moment,
        create_educational_dialogue,
        generate_game_sprite,
        generate_voice_acting,
        generate_mechanic_variants,  # For educational variants
    ]
)


async def create_game(description: str, engine: str = "pygame") -> GameProject:
    """Create a complete game from a description."""
    
    # First, create a game specification
    spec = GameSpec(
        title="Generated Game",
        description=description,
        engine=engine,
        features=["player movement", "enemies", "scoring"],
        art_style="pixel art"
    )
    
    # Run the workshop agent
    result = await Runner.run(
        workshop_agent,
        input=f"Create a {engine} game: {description}"
    )
    
    # Extract generated assets from the conversation
    # In a real implementation, we'd parse the tool calls
    project = GameProject(
        spec=spec,
        code_files={"main.py": "# Game code here"},
        assets={}
    )
    
    return project


async def create_educational_game(
    topic: str,
    concepts: list[str],
    level: Literal["beginner", "intermediate", "advanced"] = "beginner"
) -> GameProject:
    """Create an educational game that teaches programming concepts."""
    
    spec = GameSpec(
        title=f"Learn {topic} Game",
        description=f"Educational game teaching {', '.join(concepts)}",
        engine="pygame",
        educational_mode=True
    )
    
    # Run the academy agent
    result = await Runner.run(
        academy_agent,
        input=f"""Create an educational game that teaches {topic}.
        Focus on these concepts: {', '.join(concepts)}
        Target level: {level}
        Make it fun and interactive!"""
    )
    
    # Parse results
    project = GameProject(
        spec=spec,
        code_files={"main.py": "# Educational game code"},
        assets={},
        teachable_moments=[]
    )
    
    return project


# Variant generation function
async def generate_variants(
    code: str,
    feature: Literal["movement", "combat", "inventory"],
    count: int = 2
) -> list[dict[str, str]]:
    """Generate variants of a game feature."""
    
    # Template loading is now integrated into the variant generation
    
    # Create a temporary agent for variant generation
    variant_agent = Agent(
        name="Variant Generator",
        instructions=f"Generate creative variants for {feature} mechanics in games",
        tools=[]
    )
    
    result = await Runner.run(
        variant_agent,
        input=f"Generate {count} variants of {feature} for this code:\n{code}"
    )
    
    # Parse variants from response
    return [{"name": f"variant_{i}", "code": "..."} for i in range(count)]


# Dialogue generation function  
async def create_dialogue_tree(
    character: str,
    scenario: str,
    branches: int = 3
) -> str:
    """Create an interactive dialogue tree."""
    
    # For now, return a placeholder - dialogue generation should be added to a text module
    return f"Dialogue tree for {character} in scenario: {scenario} with {branches} branches"


# Main entry point for web UI
async def process_request(
    mode: Literal["workshop", "academy"],
    user_input: str,
    **kwargs
) -> dict[str, Any]:
    """Process a game creation request."""
    
    if mode == "workshop":
        # Extract engine preference
        engine = "pygame"  # default
        for eng in ["pygame", "godot", "bevy"]:
            if eng in user_input.lower():
                engine = eng
                break
        
        project = await create_game(user_input, engine)
        
        return {
            "success": True,
            "project": project.model_dump(),
            "message": f"Created {project.spec.title}!"
        }
    
    else:  # academy mode
        # Extract learning topics
        concepts = kwargs.get("concepts", ["variables", "loops"])
        level = kwargs.get("level", "beginner")
        
        project = await create_educational_game(
            topic="Programming Basics",
            concepts=concepts,
            level=level
        )
        
        return {
            "success": True,
            "project": project.model_dump(),
            "message": "Ready to learn through game creation!"
        }
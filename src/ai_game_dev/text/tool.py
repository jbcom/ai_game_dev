"""
OpenAI structured tools for text generation (dialogue, quests, code).
"""
import json
from pathlib import Path
from typing import Any, Literal

from agents import function_tool
from openai import AsyncOpenAI

from ai_game_dev.constants import OPENAI_MODELS
from ai_game_dev.templates import TemplateLoader
from ai_game_dev.assets.asset_registry import get_asset_registry

# Initialize components
client = AsyncOpenAI()  # Will use OPENAI_API_KEY env var automatically
template_loader = TemplateLoader()


@function_tool(strict_mode=False)
async def generate_dialogue_tree(
    characters: list[str],
    scenario: str,
    branches: int = 3,
    dialogue_style: str = "natural",
    emotion_tags: bool = True
) -> str:
    """
    Generate an interactive dialogue tree in Yarnspinner format.
    
    Args:
        characters: List of character names involved in dialogue
        scenario: The scenario or context for the dialogue
        branches: Number of choice branches (default: 3)
        dialogue_style: Style of dialogue ("natural", "formal", "comedic", "dramatic")
        emotion_tags: Whether to include emotion tags for voice acting
        
    Returns:
        Yarnspinner-formatted dialogue tree
    """
    prompt = f"""Create a Yarnspinner dialogue tree for this scenario:
    
Characters: {', '.join(characters)}
Scenario: {scenario}
Style: {dialogue_style}
Branches: {branches} choices at key decision points
Emotion Tags: {'Include emotion tags in square brackets' if emotion_tags else 'No emotion tags'}

Format the output as valid Yarnspinner with:
- title: SceneName
- tags: 
- ---
- Character: [emotion] Dialogue text
- -> Choice text
    <<jump NodeName>>

Create an engaging, branching conversation that fits the scenario."""

    response = await client.chat.completions.create(
        model=OPENAI_MODELS["text"]["default"],  # GPT-5
        messages=[
            {"role": "system", "content": "You are a game dialogue writer specializing in interactive narratives."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.8
    )
    
    return response.choices[0].message.content


@function_tool(strict_mode=False)
async def generate_quest_chain(
    quest_theme: str,
    quest_count: int = 3,
    difficulty_progression: bool = True,
    include_side_objectives: bool = True
) -> dict[str, Any]:
    """
    Generate a chain of related quests with objectives and rewards.
    
    Args:
        quest_theme: Main theme of the quest chain
        quest_count: Number of quests in the chain
        difficulty_progression: Whether difficulty should increase
        include_side_objectives: Include optional side objectives
        
    Returns:
        Dictionary containing quest chain data
    """
    prompt = f"""Design a quest chain for a game:

Theme: {quest_theme}
Number of Quests: {quest_count}
Progression: {'Increasing difficulty' if difficulty_progression else 'Consistent difficulty'}
Side Objectives: {'Include optional objectives' if include_side_objectives else 'Main objectives only'}

For each quest provide:
1. Title and description
2. Main objectives (step by step)
3. Optional objectives (if enabled)
4. Rewards (experience, items, story progress)
5. NPCs involved
6. How it connects to the next quest

Format as JSON."""

    response = await client.chat.completions.create(
        model=OPENAI_MODELS["text"]["default"],
        messages=[
            {"role": "system", "content": "You are a game designer specializing in quest and narrative design."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        response_format={"type": "json_object"}
    )
    
    return json.loads(response.choices[0].message.content)


@function_tool(strict_mode=False)
async def generate_game_narrative(
    genre: str,
    setting: str,
    protagonists: list[str],
    antagonist: str,
    tone: str = "balanced",
    acts: int = 3
) -> dict[str, Any]:
    """
    Generate a complete game narrative structure.
    
    Args:
        genre: Game genre (e.g., "fantasy", "sci-fi", "mystery")
        setting: World setting description
        protagonists: List of main character names/roles
        antagonist: Main antagonist name/description
        tone: Narrative tone ("dark", "light", "balanced", "comedic", "epic")
        acts: Number of story acts
        
    Returns:
        Dictionary containing full narrative structure
    """
    prompt = f"""Create a complete game narrative structure:

Genre: {genre}
Setting: {setting}
Protagonists: {', '.join(protagonists)}
Antagonist: {antagonist}
Tone: {tone}
Acts: {acts}

Include:
1. Overall story arc
2. Act breakdowns with key events
3. Character arcs for each protagonist
4. Major plot points and twists
5. Climax and resolution options
6. Themes and motifs
7. World-building elements

Format as structured JSON."""

    response = await client.chat.completions.create(
        model=OPENAI_MODELS["text"]["default"],
        messages=[
            {"role": "system", "content": "You are a narrative designer creating compelling game stories."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.8,
        response_format={"type": "json_object"}
    )
    
    return json.loads(response.choices[0].message.content)


@function_tool(strict_mode=False)
async def generate_character_backstory(
    character_name: str,
    character_role: str,
    personality_traits: list[str],
    relationships: list[str] | None = None,
    secrets: int = 1
) -> dict[str, Any]:
    """
    Generate detailed character backstory and profile.
    
    Args:
        character_name: Name of the character
        character_role: Role in the story (e.g., "hero", "mentor", "rival")
        personality_traits: List of personality traits
        relationships: List of relationships to other characters
        secrets: Number of secrets to include
        
    Returns:
        Dictionary containing character profile and backstory
    """
    relationships_text = f"\nRelationships: {', '.join(relationships)}" if relationships else ""
    
    prompt = f"""Create a detailed character profile:

Name: {character_name}
Role: {character_role}
Personality: {', '.join(personality_traits)}{relationships_text}
Secrets: Include {secrets} hidden secret(s)

Provide:
1. Background and origin story
2. Motivations and goals
3. Fears and weaknesses
4. Skills and abilities
5. Character arc potential
6. The secret(s) that could be revealed
7. Memorable quotes or catchphrases

Format as structured JSON."""

    response = await client.chat.completions.create(
        model=OPENAI_MODELS["text"]["default"],
        messages=[
            {"role": "system", "content": "You are a character writer creating deep, memorable game characters."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.8,
        response_format={"type": "json_object"}
    )
    
    return json.loads(response.choices[0].message.content)


@function_tool(strict_mode=False)
async def create_yarnspinner_dialogue(
    scene_name: str,
    participants: list[str],
    context: str,
    word_count: int = 500,
    include_stage_directions: bool = True
) -> str:
    """
    Create dialogue in Yarnspinner format for a specific scene.
    
    Args:
        scene_name: Name of the scene/node
        participants: Characters in the scene
        context: Context and what happens in the scene
        word_count: Approximate word count
        include_stage_directions: Include action descriptions
        
    Returns:
        Yarnspinner-formatted dialogue
    """
    prompt = f"""Write Yarnspinner dialogue for this scene:

Scene: {scene_name}
Characters: {', '.join(participants)}
Context: {context}
Length: Approximately {word_count} words
Stage Directions: {'Include action descriptions in parentheses' if include_stage_directions else 'Dialogue only'}

Use proper Yarnspinner format:
- Start with title: {scene_name}
- Use Character: for speaker names
- Use -> for choices with <<jump NodeName>>
- Use [[ ]] for inline choices
- Include <<if $variable>> conditionals where appropriate

Make the dialogue engaging and true to each character."""

    response = await client.chat.completions.create(
        model=OPENAI_MODELS["text"]["default"],
        messages=[
            {"role": "system", "content": "You are an expert in writing game dialogue in Yarnspinner format."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.8
    )
    
    return response.choices[0].message.content


@function_tool(strict_mode=False)
async def generate_educational_content(
    programming_concept: str,
    difficulty_level: Literal["beginner", "intermediate", "advanced"],
    game_context: str,
    include_exercises: bool = True
) -> dict[str, Any]:
    """
    Generate educational content for teaching programming through games.
    
    Args:
        programming_concept: Concept to teach (e.g., "loops", "variables", "functions")
        difficulty_level: Target difficulty level
        game_context: How it relates to the game being built
        include_exercises: Whether to include practice exercises
        
    Returns:
        Dictionary containing educational content and exercises
    """
    prompt = f"""Create educational content for teaching programming:

Concept: {programming_concept}
Level: {difficulty_level}
Game Context: {game_context}
Exercises: {'Include hands-on exercises' if include_exercises else 'Explanation only'}

Provide:
1. Clear explanation of the concept
2. Why it's important in game development
3. Practical examples in game context
4. Common mistakes to avoid
5. Step-by-step implementation guide
{"6. 3-5 practice exercises with solutions" if include_exercises else ""}
7. Tips for mastery

Use encouraging language appropriate for {difficulty_level} learners.
Format as structured JSON."""

    response = await client.chat.completions.create(
        model=OPENAI_MODELS["text"]["educational"],
        messages=[
            {"role": "system", "content": "You are Professor Pixel, an expert at teaching programming through game development."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        response_format={"type": "json_object"}
    )
    
    return json.loads(response.choices[0].message.content)


@function_tool(strict_mode=False)
async def generate_code_repository(
    engine: Literal["pygame", "godot", "bevy"],
    game_spec: dict[str, Any],
    include_comments: bool = True,
    educational_mode: bool = False
) -> dict[str, str]:
    """
    Generate a complete code repository for a game engine.
    
    Args:
        engine: Target game engine
        game_spec: Game specification dictionary
        include_comments: Include explanatory comments
        educational_mode: Add educational comments and exercises
        
    Returns:
        Dictionary mapping file paths to code content
    """
    # Get available assets from registry
    registry = get_asset_registry()
    game_type = game_spec.get('type', 'general')
    assets_config = registry.get_assets_for_game(game_type, engine)
    
    # Merge assets into game spec
    if 'assets' not in game_spec:
        game_spec['assets'] = {}
    game_spec['assets'].update(assets_config)
    
    # Load engine-specific templates
    template = template_loader.render_engine_prompt(
        engine,
        "code_structure",
        game_spec=game_spec,
        educational_mode=educational_mode,
        assets=assets_config
    )
    
    instructions = template_loader.render_engine_prompt(
        engine,
        "architecture",
        game_spec=game_spec,
        include_comments=include_comments,
        assets=assets_config
    )
    
    prompt = f"""{instructions}

{template}

Game Specification:
{json.dumps(game_spec, indent=2)}

Available Assets:
{json.dumps(assets_config, indent=2)}

Generate a complete, working code repository with:
1. All necessary files for the {engine} engine
2. {'Detailed educational comments' if educational_mode else 'Clear comments' if include_comments else 'Minimal comments'}
3. Proper project structure
4. Asset loading and management using the provided asset paths
5. Game mechanics implementation
6. UI and controls

Provide as JSON mapping file paths to code content."""

    response = await client.chat.completions.create(
        model=OPENAI_MODELS["text"]["code_generation"],
        messages=[
            {"role": "system", "content": f"You are an expert {engine} game developer creating production-ready code."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
        response_format={"type": "json_object"}
    )
    
    return json.loads(response.choices[0].message.content)
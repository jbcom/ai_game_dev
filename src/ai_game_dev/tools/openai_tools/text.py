"""
OpenAI text generation tools for game content.
Generates dialogue, quests, and code using GPT-5.
"""
import json
from pathlib import Path
from typing import Any, Literal

from openai import AsyncOpenAI
from pydantic import BaseModel, Field

from agents import function_tool

from ai_game_dev.constants import OPENAI_MODELS
from .template_loader import template_loader


class DialogueNode(BaseModel):
    """A node in a dialogue tree."""
    title: str
    tags: list[str] = Field(default_factory=list)
    content: str
    options: list[dict[str, str]] = Field(default_factory=list)


class QuestData(BaseModel):
    """Quest information."""
    id: str
    name: str
    description: str
    objectives: list[str]
    rewards: dict[str, Any]
    dialogue_nodes: list[DialogueNode]


class GeneratedCode(BaseModel):
    """Generated code result."""
    files: dict[str, str]
    main_file: str
    readme: str


@function_tool
async def generate_dialogue(
    character_name: str,
    context: str,
    personality: str = "friendly",
    dialogue_style: Literal["yarn", "json", "plain"] = "yarn",
    num_branches: int = 2,
    save_path: str | None = None,
) -> str:
    """Generate character dialogue in YarnSpinner or other formats."""
    client = AsyncOpenAI()
    
    prompt = f"""Generate dialogue for {character_name} with personality: {personality}
Context: {context}

Create an interactive dialogue tree with {num_branches} meaningful player choices.
Each choice should lead to different outcomes or reveal different information.

Format: {dialogue_style}
"""
    
    if dialogue_style == "yarn":
        prompt += """
Use YarnSpinner format:
---
title: NodeName
tags: tag1 tag2
---
Character: Dialogue text
-> Option 1
    <<jump NextNode1>>
-> Option 2  
    <<jump NextNode2>>
===
"""
    
    response = await client.chat.completions.create(
        model=OPENAI_MODELS["text"]["default"],  # GPT-5
        messages=[
            {"role": "system", "content": "You are a game dialogue writer specializing in interactive narratives."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.8
    )
    
    dialogue = response.choices[0].message.content
    
    if save_path:
        path = Path(save_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(dialogue)
    
    return dialogue


@function_tool
async def generate_quest(
    quest_theme: str,
    game_genre: Literal["rpg", "adventure", "puzzle", "action"],
    difficulty: Literal["easy", "medium", "hard"] = "medium",
    include_dialogue: bool = True,
    save_path: str | None = None,
) -> QuestData:
    """Generate a complete quest with objectives and dialogue."""
    client = AsyncOpenAI()
    
    objective_counts = {"easy": 2, "medium": 3, "hard": 5}
    
    prompt = f"""Create a {difficulty} quest for a {game_genre} game.
Theme: {quest_theme}

Include:
1. Quest name and description
2. {objective_counts[difficulty]} clear objectives
3. Appropriate rewards
4. {"Dialogue for quest giver and completion" if include_dialogue else "No dialogue needed"}

Make it engaging and appropriate for the genre."""
    
    response = await client.chat.completions.create(
        model=OPENAI_MODELS["text"]["default"],  # GPT-5
        messages=[
            {"role": "system", "content": "You are a game designer creating engaging quests."},
            {"role": "user", "content": prompt}
        ],
        response_format={"type": "json_object"},
        temperature=0.7
    )
    
    quest_data = response.choices[0].message.content
    quest_json = json.loads(quest_data)
    
    # Generate dialogue if requested
    dialogue_nodes = []
    if include_dialogue:
        # Quest start dialogue
        start_dialogue = await generate_dialogue(
            character_name="Quest Giver",
            context=f"Giving quest: {quest_json.get('name', quest_theme)}",
            dialogue_style="yarn"
        )
        dialogue_nodes.append(DialogueNode(
            title="quest_start",
            content=start_dialogue,
            tags=["quest", "start"]
        ))
        
        # Quest complete dialogue
        complete_dialogue = await generate_dialogue(
            character_name="Quest Giver",
            context=f"Player completed quest: {quest_json.get('name', quest_theme)}",
            dialogue_style="yarn"
        )
        dialogue_nodes.append(DialogueNode(
            title="quest_complete",
            content=complete_dialogue,
            tags=["quest", "complete"]
        ))
    
    quest = QuestData(
        id=quest_theme.lower().replace(" ", "_"),
        name=quest_json.get("name", quest_theme),
        description=quest_json.get("description", ""),
        objectives=quest_json.get("objectives", []),
        rewards=quest_json.get("rewards", {}),
        dialogue_nodes=dialogue_nodes
    )
    
    if save_path:
        path = Path(save_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(quest.model_dump_json(indent=2))
    
    return quest


@function_tool
async def generate_game_code(
    game_spec: dict[str, Any],
    engine: Literal["pygame", "godot", "bevy"],
    include_comments: bool = True,
    educational_mode: bool = False,
    save_dir: str | None = None,
) -> GeneratedCode:
    """Generate complete game code for specified engine."""
    client = AsyncOpenAI()
    
    # Get engine-specific template and instructions
    template = template_loader.render_engine_prompt(
        engine, 
        "code_structure",
        game_spec=game_spec,
        educational_mode=educational_mode
    )
    instructions = template_loader.render_engine_prompt(
        engine,
        "architecture", 
        game_spec=game_spec,
        include_comments=include_comments
    )
    
    prompt = f"""Generate a complete {engine} game based on this specification:
{json.dumps(game_spec, indent=2)}

{instructions}

{"Include educational comments explaining key concepts." if educational_mode else ""}
{"Include helpful comments." if include_comments else "Minimal comments."}
"""
    
    response = await client.chat.completions.create(
        model=OPENAI_MODELS["text"]["code_generation"],  # GPT-5 for code
        messages=[
            {"role": "system", "content": template},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
        max_tokens=4000
    )
    
    # Parse the response to extract files
    content = response.choices[0].message.content
    
    # This is simplified - in reality we'd parse the response more carefully
    files = {}
    main_file = ""
    
    if engine == "pygame":
        files["main.py"] = content
        main_file = "main.py"
    elif engine == "godot":
        files["Main.gd"] = content
        files["project.godot"] = _generate_godot_project(game_spec)
        main_file = "Main.gd"
    elif engine == "bevy":
        files["src/main.rs"] = content
        files["Cargo.toml"] = _generate_cargo_toml(game_spec)
        main_file = "src/main.rs"
    
    # Generate README
    readme = f"""# {game_spec.get('title', 'Game')}

{game_spec.get('description', 'A game')}

## Engine: {engine.title()}

## Running the game

{_get_run_instructions(engine)}

## Controls

WASD or Arrow Keys - Move
Space - Action

## Features

{chr(10).join(f"- {f}" for f in game_spec.get('features', []))}
"""
    
    if save_dir:
        base_dir = Path(save_dir)
        for filename, content in files.items():
            filepath = base_dir / filename
            filepath.parent.mkdir(parents=True, exist_ok=True)
            filepath.write_text(content)
        
        (base_dir / "README.md").write_text(readme)
    
    return GeneratedCode(
        files=files,
        main_file=main_file,
        readme=readme
    )


@function_tool
async def identify_teachable_moments(
    code: str,
    programming_level: Literal["beginner", "intermediate", "advanced"] = "beginner",
    concepts_to_highlight: list[str] | None = None,
) -> list[dict[str, Any]]:
    """Identify educational opportunities in game code."""
    client = AsyncOpenAI()
    
    concepts_list = concepts_to_highlight or [
        "variables", "loops", "conditionals", "functions",
        "classes", "inheritance", "event handling"
    ]
    
    prompt = f"""Analyze this game code and identify teachable moments for a {programming_level} programmer.
Focus on these concepts: {', '.join(concepts_list)}

Code:
```
{code}
```

For each teachable moment, provide:
1. Line number or code section
2. Concept being demonstrated
3. Brief explanation suitable for {programming_level} level
4. A simple exercise to reinforce the concept
"""
    
    response = await client.chat.completions.create(
        model=OPENAI_MODELS["text"]["educational"],  # GPT-5 for education
        messages=[
            {"role": "system", "content": "You are a programming educator analyzing code for learning opportunities."},
            {"role": "user", "content": prompt}
        ],
        response_format={"type": "json_object"},
        temperature=0.5
    )
    
    moments = json.loads(response.choices[0].message.content)
    
    return moments.get("teachable_moments", [])


def _generate_godot_project(spec: dict[str, Any]) -> str:
    """Generate Godot project.godot file."""
    return f"""[application]
config/name="{spec.get('title', 'Game')}"
run/main_scene="res://Main.tscn"
config/features=PackedStringArray("4.2")

[display]
window/size/viewport_width=1280
window/size/viewport_height=720

[input]
move_left={{
"deadzone": 0.5,
"events": [Object(InputEventKey,"resource_local_to_scene":false,"device":0,"keycode":65)]
}}
"""


def _generate_cargo_toml(spec: dict[str, Any]) -> str:
    """Generate Bevy Cargo.toml file."""
    return f"""[package]
name = "{spec.get('title', 'game').lower().replace(' ', '_')}"
version = "0.1.0"
edition = "2021"

[dependencies]
bevy = "0.12"
"""


def _get_run_instructions(engine: str) -> str:
    """Get engine-specific run instructions."""
    instructions = {
        "pygame": "```bash\npython main.py\n```",
        "godot": "Open project.godot in Godot Engine and press F5",
        "bevy": "```bash\ncargo run\n```"
    }
    return instructions.get(engine, "See engine documentation")
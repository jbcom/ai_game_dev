"""
Text generation module for game dialogue, quests, and narrative.
"""
from .tool import (
    generate_dialogue_tree,
    generate_quest_chain,
    generate_game_narrative,
    generate_character_backstory,
    create_yarnspinner_dialogue,
    generate_educational_content,
    generate_code_repository,
)

__all__ = [
    "generate_dialogue_tree",
    "generate_quest_chain", 
    "generate_game_narrative",
    "generate_character_backstory",
    "create_yarnspinner_dialogue",
    "generate_educational_content",
    "generate_code_repository",
]
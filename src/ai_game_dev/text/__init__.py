"""
Text generation module for game dialogue, quests, narrative, and educational content.
Consolidates literary seeding, dialogue generation, and educational game text.
"""
# Original text generation tools
from .tool import (
    generate_dialogue_tree,
    generate_quest_chain,
    generate_game_narrative,
    generate_character_backstory,
    create_yarnspinner_dialogue,
    generate_educational_content,
    generate_code_repository,
)

# Literary seeding tools (moved from seeding module)
from .seeding_tools import (
    seed_narrative_content,
    extract_narrative_patterns,
    find_literary_inspirations,
    generate_quest_seeds,
    create_character_backstory as seed_character_backstory,
    enhance_game_narrative,
)

# Educational content tools (moved from education module)
from .yarn_dialogue import YarnDialogueGenerator
from .characters_and_story import CharacterGenerator, StoryGenerator
from .rpg_specification import get_rpg_specification
from .educational_tools import (
    create_lesson_plan,
    identify_teachable_moment,
    generate_educational_game_spec,
    create_educational_dialogue,
    generate_academy_characters,
    create_coding_challenge,
)

# Literary seeder class
from .literary_seeder import LiterarySeeder, SeedingRequest

__all__ = [
    # Core text generation
    "generate_dialogue_tree",
    "generate_quest_chain", 
    "generate_game_narrative",
    "generate_character_backstory",
    "create_yarnspinner_dialogue",
    "generate_educational_content",
    "generate_code_repository",
    
    # Literary seeding
    "seed_narrative_content",
    "extract_narrative_patterns", 
    "find_literary_inspirations",
    "generate_quest_seeds",
    "seed_character_backstory",
    "enhance_game_narrative",
    "LiterarySeeder",
    "SeedingRequest",
    
    # Educational content
    "YarnDialogueGenerator",
    "CharacterGenerator",
    "StoryGenerator", 
    "get_rpg_specification",
    "create_lesson_plan",
    "identify_teachable_moment",
    "generate_educational_game_spec",
    "create_educational_dialogue",
    "generate_academy_characters",
    "create_coding_challenge",
]
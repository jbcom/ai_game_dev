"""
OpenAI structured tools for narrative seeding from literary sources.
"""
import json
from pathlib import Path
from typing import Any, Dict, List

from agents import function_tool

from .literary_seeder import LiterarySeeder, SeedingRequest, SeededContent


# Initialize the seeder
_seeder = LiterarySeeder()


@function_tool
async def seed_narrative_content(
    themes: list[str],
    genres: list[str],
    character_types: list[str] | None = None,
    settings: list[str] | None = None,
    tone: str = "neutral",
    max_sources: int = 5
) -> Dict[str, Any]:
    """
    Seed narrative content from literary sources based on themes and genres.
    
    Args:
        themes: List of themes to explore (e.g., ["heroism", "mystery", "redemption"])
        genres: List of genres to draw from (e.g., ["fantasy", "sci-fi", "adventure"])
        character_types: Optional list of character archetypes to find
        settings: Optional list of setting types to explore
        tone: Desired tone of content ("neutral", "dark", "light", "dramatic")
        max_sources: Maximum number of sources to return
        
    Returns:
        Dictionary containing seeded narrative content, themes, patterns, and inspirations
    """
    request = SeedingRequest(
        themes=themes,
        genres=genres,
        character_types=character_types or [],
        settings=settings or [],
        tone=tone,
        max_sources=max_sources
    )
    
    result = await _seeder.seed_from_request(request)
    return result


@function_tool
async def extract_narrative_patterns(
    text: str,
    analysis_type: str = "comprehensive"
) -> Dict[str, Any]:
    """
    Extract narrative patterns and literary elements from text.
    
    Args:
        text: Text to analyze
        analysis_type: Type of analysis ("comprehensive", "themes", "characters", "settings", "style")
        
    Returns:
        Dictionary containing extracted patterns and elements
    """
    # Create a temporary seeded content object for analysis
    content = SeededContent(
        source="user_provided",
        content_type="text",
        text_content=text
    )
    
    results = {}
    
    if analysis_type in ["comprehensive", "themes"]:
        results["themes"] = _seeder._extract_themes(text)
        
    if analysis_type in ["comprehensive", "characters"]:
        results["characters"] = _seeder._extract_character_concepts([content])
        
    if analysis_type in ["comprehensive", "settings"]:
        results["settings"] = _seeder._extract_setting_concepts([content])
        
    if analysis_type in ["comprehensive", "style"]:
        results["style"] = _seeder._analyze_literary_style([content])
        
    return results


@function_tool
async def find_literary_inspirations(
    game_description: str,
    target_audience: str = "general",
    inspiration_count: int = 3
) -> Dict[str, Any]:
    """
    Find literary inspirations for a game based on its description.
    
    Args:
        game_description: Description of the game to find inspirations for
        target_audience: Target audience ("children", "teen", "general", "mature")
        inspiration_count: Number of inspirations to return
        
    Returns:
        Dictionary containing literary inspirations, themes, and narrative suggestions
    """
    # Extract themes and genres from game description
    themes = []
    genres = []
    
    desc_lower = game_description.lower()
    
    # Simple theme extraction
    if any(word in desc_lower for word in ["hero", "save", "quest", "journey"]):
        themes.append("heroism")
    if any(word in desc_lower for word in ["mystery", "puzzle", "secret", "hidden"]):
        themes.append("mystery")
    if any(word in desc_lower for word in ["space", "sci-fi", "future", "alien"]):
        genres.append("sci-fi")
    if any(word in desc_lower for word in ["fantasy", "magic", "wizard", "dragon"]):
        genres.append("fantasy")
    if any(word in desc_lower for word in ["adventure", "explore", "discover"]):
        genres.append("adventure")
        
    # Default if no themes/genres detected
    if not themes:
        themes = ["adventure", "discovery"]
    if not genres:
        genres = ["general", "adventure"]
        
    # Adjust tone based on audience
    tone_map = {
        "children": "light",
        "teen": "neutral", 
        "general": "neutral",
        "mature": "dramatic"
    }
    tone = tone_map.get(target_audience, "neutral")
    
    # Get seeded content
    result = await seed_narrative_content(
        themes=themes,
        genres=genres,
        tone=tone,
        max_sources=inspiration_count
    )
    
    # Format for game development
    return {
        "inspirations": result.get("seeded_content", []),
        "suggested_themes": result.get("themes_found", []),
        "narrative_elements": {
            "character_ideas": result.get("character_inspirations", []),
            "setting_ideas": result.get("setting_inspirations", []),
            "story_patterns": result.get("narrative_patterns", {})
        },
        "style_guide": result.get("style_analysis", {}),
        "audience_notes": f"Content filtered for {target_audience} audience with {tone} tone"
    }


@function_tool
async def generate_quest_seeds(
    game_genre: str,
    quest_count: int = 5,
    complexity: str = "medium"
) -> List[Dict[str, Any]]:
    """
    Generate quest seeds based on literary patterns.
    
    Args:
        game_genre: Genre of the game (e.g., "fantasy", "sci-fi", "mystery")
        quest_count: Number of quest seeds to generate
        complexity: Quest complexity ("simple", "medium", "complex")
        
    Returns:
        List of quest seed dictionaries with objectives and narrative hooks
    """
    # Get narrative seeds
    result = await seed_narrative_content(
        themes=["quest", "challenge", "discovery"],
        genres=[game_genre],
        max_sources=3
    )
    
    quest_seeds = []
    
    # Generate quest ideas based on patterns
    patterns = result.get("narrative_patterns", {})
    themes = result.get("themes_found", [])
    
    # Quest templates based on complexity
    if complexity == "simple":
        templates = [
            {"type": "fetch", "template": "Retrieve the {item} from {location}"},
            {"type": "deliver", "template": "Deliver {item} to {character}"},
            {"type": "defeat", "template": "Defeat the {enemy} threatening {location}"}
        ]
    elif complexity == "complex":
        templates = [
            {"type": "multi_part", "template": "Uncover the secret of {mystery} by finding {count} {items}"},
            {"type": "moral_choice", "template": "Choose between helping {faction1} or {faction2} in their conflict"},
            {"type": "investigation", "template": "Investigate the {phenomenon} affecting {location}"}
        ]
    else:  # medium
        templates = [
            {"type": "rescue", "template": "Rescue {character} from {danger}"},
            {"type": "explore", "template": "Explore {location} and discover its {secret}"},
            {"type": "protect", "template": "Protect {target} from {threat} for {duration}"}
        ]
    
    # Generate quests
    for i in range(quest_count):
        template = templates[i % len(templates)]
        
        quest = {
            "id": f"quest_{i+1}",
            "type": template["type"],
            "title": f"Quest {i+1}",
            "description": template["template"],
            "objectives": [],
            "narrative_hook": f"Inspired by {themes[i % len(themes)] if themes else 'adventure'} themes",
            "complexity": complexity,
            "rewards": ["experience", "items", "story_progression"]
        }
        
        # Add objectives based on type
        if template["type"] in ["fetch", "deliver"]:
            quest["objectives"] = ["Find the item", "Return to quest giver"]
        elif template["type"] == "defeat":
            quest["objectives"] = ["Locate the enemy", "Defeat in combat"]
        elif template["type"] == "multi_part":
            quest["objectives"] = ["Find first clue", "Gather all items", "Solve the mystery"]
            
        quest_seeds.append(quest)
        
    return quest_seeds


@function_tool  
async def create_character_backstory(
    character_name: str,
    character_role: str,
    personality_traits: list[str],
    world_setting: str = "fantasy"
) -> Dict[str, Any]:
    """
    Create a character backstory using literary archetypes and patterns.
    
    Args:
        character_name: Name of the character
        character_role: Role in the game (e.g., "hero", "mentor", "villain", "companion")
        personality_traits: List of personality traits
        world_setting: Setting of the game world
        
    Returns:
        Dictionary containing backstory, motivations, and relationships
    """
    # Map roles to literary archetypes
    archetype_map = {
        "hero": ["unlikely_hero", "chosen_one", "reluctant_warrior"],
        "mentor": ["wise_guide", "mysterious_teacher", "fallen_master"],
        "villain": ["tragic_villain", "power_hungry", "corrupted_noble"],
        "companion": ["loyal_friend", "comic_relief", "skilled_specialist"]
    }
    
    archetypes = archetype_map.get(character_role, ["unique_individual"])
    
    # Get literary inspirations
    result = await seed_narrative_content(
        themes=[character_role] + personality_traits[:2],
        genres=[world_setting],
        character_types=archetypes,
        max_sources=2
    )
    
    # Extract character patterns
    char_inspirations = result.get("character_inspirations", [])
    
    backstory = {
        "name": character_name,
        "role": character_role,
        "archetype": archetypes[0] if archetypes else "original",
        "personality": personality_traits,
        "backstory": {
            "origin": f"Born in a {world_setting} world",
            "formative_event": "A defining moment that shaped their path",
            "motivation": f"Driven by {personality_traits[0] if personality_traits else 'purpose'}",
            "secret": "A hidden truth about their past"
        },
        "relationships": {
            "allies": ["trusted companions"],
            "rivals": ["competitive peers"],
            "mentors": ["guiding figures"]
        },
        "character_arc": {
            "start": f"Begins as {personality_traits[0] if personality_traits else 'uncertain'}",
            "growth": "Learns important lessons",
            "potential_end": "Fulfills their destiny or finds new purpose"
        },
        "literary_inspiration": char_inspirations[0] if char_inspirations else {
            "archetype": "original",
            "description": "A unique character for your story"
        }
    }
    
    return backstory


@function_tool
async def enhance_game_narrative(
    game_spec: Dict[str, Any],
    narrative_depth: str = "medium"
) -> Dict[str, Any]:
    """
    Enhance a game specification with narrative elements from literary sources.
    
    Args:
        game_spec: Game specification dictionary
        narrative_depth: Level of narrative enhancement ("light", "medium", "deep")
        
    Returns:
        Enhanced game specification with narrative elements
    """
    # Extract key elements from game spec
    title = game_spec.get("title", "Untitled Game")
    description = game_spec.get("description", "")
    genre = game_spec.get("genre", "adventure")
    
    # Get narrative seeds
    inspirations = await find_literary_inspirations(
        game_description=description,
        inspiration_count=3 if narrative_depth == "deep" else 2
    )
    
    # Generate quest seeds
    quests = await generate_quest_seeds(
        game_genre=genre,
        quest_count=5 if narrative_depth == "deep" else 3,
        complexity="medium" if narrative_depth == "medium" else "simple"
    )
    
    # Enhance the game spec
    enhanced_spec = game_spec.copy()
    
    enhanced_spec["narrative"] = {
        "themes": inspirations["suggested_themes"],
        "story_elements": inspirations["narrative_elements"],
        "style_guide": inspirations["style_guide"],
        "main_quest": {
            "title": f"The {title} Journey",
            "description": f"An epic quest through the world of {title}",
            "acts": 3 if narrative_depth == "deep" else 2
        },
        "side_quests": quests,
        "world_building": {
            "setting_inspiration": inspirations["narrative_elements"]["setting_ideas"],
            "lore_depth": narrative_depth,
            "cultural_elements": []
        }
    }
    
    # Add characters if not present
    if "characters" not in enhanced_spec:
        enhanced_spec["characters"] = []
        
    # Add narrative hooks
    enhanced_spec["narrative_hooks"] = [
        "Opening mystery that draws players in",
        "Mid-game revelation that changes perspective",
        "Climactic choice that affects the ending"
    ]
    
    return enhanced_spec
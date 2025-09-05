"""Advanced world building and meta-generation system."""

import asyncio
import json
import uuid
import random
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from enum import Enum
from dataclasses import dataclass, asdict

import aiofiles
from openai import AsyncOpenAI

from .config import settings
from .logging_config import get_logger
from .seed_system import seed_queue, SeedType, SeedPriority
from .narrative_system import NarrativeGenerator
from .utils import ensure_directory_exists

logger = get_logger(__name__, component="world_builder")


class GameType(str, Enum):
    """Supported game types with specific generation patterns."""
    RPG = "rpg"
    PLATFORMER = "platformer"
    FPS = "fps"
    PUZZLE = "puzzle"
    ADVENTURE = "adventure"
    ROGUELIKE = "roguelike"
    STRATEGY = "strategy"


class LocationType(str, Enum):
    """Types of game locations."""
    TOWN = "town"
    DUNGEON = "dungeon"
    WILDERNESS = "wilderness"
    CASTLE = "castle"
    TEMPLE = "temple"
    CAVE = "cave"
    FOREST = "forest"
    MOUNTAIN = "mountain"
    DESERT = "desert"
    SWAMP = "swamp"


@dataclass
class WorldFormat:
    """Structured world definition format."""
    id: str
    name: str
    game_type: GameType
    theme: str
    setting: str
    tone: str
    complexity: str  # "simple", "medium", "complex"
    
    # Name generation data
    person_names: Dict[str, List[str]]  # {"male": [...], "female": [...], "surname": [...]}
    place_names: Dict[str, List[str]]   # {"towns": [...], "regions": [...], "landmarks": [...]}
    
    # Game-specific features
    core_mechanics: List[str]
    progression_systems: List[str]
    content_types: List[str]
    
    # World structure
    regions: List[Dict[str, Any]]
    factions: List[Dict[str, Any]]
    conflicts: List[Dict[str, Any]]
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class GenerationPlan:
    """Complete plan for generating game content."""
    world_id: str
    total_locations: int
    asset_count: Dict[str, int]  # {"sprites": 50, "tiles": 20, ...}
    narrative_count: Dict[str, int]  # {"quests": 10, "npcs": 30, ...}
    generation_order: List[Dict[str, Any]]  # Step-by-step execution plan
    estimated_time: int  # minutes
    

class WorldBuilder:
    """Builds complete game worlds with coordinated content generation."""
    
    def __init__(self, openai_client: AsyncOpenAI):
        self.client = openai_client
        self.worlds_dir = settings.cache_dir / "worlds"
        self.narrative_generator = NarrativeGenerator(openai_client)
        
    async def initialize(self):
        """Initialize world builder."""
        await ensure_directory_exists(self.worlds_dir)
        await self.narrative_generator.initialize()
    
    async def create_world_format(
        self,
        world_brief: str,
        game_type: GameType,
        complexity: str = "medium"
    ) -> WorldFormat:
        """Create a comprehensive world format from a brief description."""
        
        world_prompt = f"""
        Create a complete world format for a {game_type.value} game.
        
        Brief: {world_brief}
        Complexity: {complexity}
        
        Generate a comprehensive world including:
        
        1. Core world details (name, theme, setting, tone)
        
        2. Name generation systems:
           - Person names by gender and surnames
           - Place names for different location types
           - Culturally consistent naming patterns
        
        3. Game-specific mechanics based on {game_type.value}:
           - Core gameplay systems
           - Progression mechanics
           - Content types needed
        
        4. World structure:
           - 3-5 distinct regions with themes
           - Major factions and their goals
           - Central conflicts driving gameplay
        
        Create rich, interconnected world systems that support compelling gameplay.
        Format as detailed JSON matching the WorldFormat structure.
        """
        
        response = await self.client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": world_prompt}],
            response_format={"type": "json_object"}
        )
        
        world_data = json.loads(response.choices[0].message.content)
        
        world_format = WorldFormat(
            id=str(uuid.uuid4()),
            name=world_data["name"],
            game_type=game_type,
            theme=world_data["theme"],
            setting=world_data["setting"],
            tone=world_data["tone"],
            complexity=complexity,
            person_names=world_data["person_names"],
            place_names=world_data["place_names"],
            core_mechanics=world_data["core_mechanics"],
            progression_systems=world_data["progression_systems"],
            content_types=world_data["content_types"],
            regions=world_data["regions"],
            factions=world_data["factions"],
            conflicts=world_data["conflicts"]
        )
        
        # Create world seeds for consistent generation
        await self._create_world_seeds(world_format)
        
        # Save world format
        await self._save_world_format(world_format)
        
        return world_format
    
    async def generate_meta_prompts(
        self,
        world_format: WorldFormat,
        target_content: Dict[str, int]  # {"locations": 5, "quests": 10, "npcs": 20, ...}
    ) -> List[Dict[str, Any]]:
        """Generate meta-prompts for coordinated content creation."""
        
        meta_prompt = f"""
        Create a comprehensive content generation plan for this world:
        
        World: {world_format.name}
        Type: {world_format.game_type.value}
        Theme: {world_format.theme}
        Setting: {world_format.setting}
        
        Regions: {json.dumps(world_format.regions, indent=2)}
        Factions: {json.dumps(world_format.factions, indent=2)}
        
        Target Content: {json.dumps(target_content)}
        
        Generate detailed prompts for creating:
        1. Key locations in each region
        2. Important NPCs for each faction
        3. Interconnected quest lines
        4. Environmental assets for each region
        5. UI elements matching the world theme
        
        Each prompt should reference world context and maintain consistency.
        Include specific asset requirements, narrative connections, and technical specs.
        
        Format as JSON array of prompt objects with: type, priority, description, context, requirements.
        """
        
        response = await self.client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": meta_prompt}],
            response_format={"type": "json_object"}
        )
        
        prompts_data = json.loads(response.choices[0].message.content)
        return prompts_data.get("prompts", [])
    
    async def generate_names(
        self,
        world_format: WorldFormat,
        name_type: str,  # "person", "place"
        subtype: str,    # "male", "female", "town", "region", etc.
        count: int = 10
    ) -> List[str]:
        """Generate contextually appropriate names."""
        
        if name_type == "person":
            base_names = world_format.person_names.get(subtype, [])
        else:
            base_names = world_format.place_names.get(subtype, [])
        
        # If we have base names, use them as examples
        if base_names:
            name_prompt = f"""
            Generate {count} {name_type} names ({subtype}) for the world "{world_format.name}".
            
            World theme: {world_format.theme}
            Setting: {world_format.setting}
            
            Use these existing names as style examples: {base_names[:5]}
            
            Generate names that match the cultural style and world theme.
            Return as JSON array of strings.
            """
        else:
            name_prompt = f"""
            Generate {count} {name_type} names ({subtype}) for a {world_format.theme} world.
            
            World: {world_format.name}
            Setting: {world_format.setting}
            
            Create names that fit the world's cultural and thematic style.
            Return as JSON array of strings.
            """
        
        response = await self.client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": name_prompt}],
            response_format={"type": "json_object"}
        )
        
        names_data = json.loads(response.choices[0].message.content)
        return names_data.get("names", [])
    
    async def create_generation_plan(
        self,
        world_format: WorldFormat,
        scope: str = "single_area"  # "single_area", "full_region", "entire_world"
    ) -> GenerationPlan:
        """Create coordinated generation plan for game content."""
        
        if scope == "single_area":
            target_content = {
                "locations": 1,
                "quests": 2,
                "npcs": 5,
                "sprites": 10,
                "tiles": 8,
                "ui_elements": 3
            }
        elif scope == "full_region":
            target_content = {
                "locations": 3,
                "quests": 5,
                "npcs": 15,
                "sprites": 25,
                "tiles": 15,
                "ui_elements": 8
            }
        else:  # entire_world
            target_content = {
                "locations": len(world_format.regions) * 3,
                "quests": 20,
                "npcs": 50,
                "sprites": 100,
                "tiles": 40,
                "ui_elements": 20
            }
        
        # Generate meta-prompts
        meta_prompts = await self.generate_meta_prompts(world_format, target_content)
        
        # Create execution order
        generation_order = []
        
        # First: Core world assets
        generation_order.append({
            "step": 1,
            "type": "world_setup",
            "description": "Initialize world seeds and base assets",
            "actions": ["create_style_guide", "setup_color_palette", "generate_base_tiles"]
        })
        
        # Then: Locations and environments
        for i, prompt in enumerate([p for p in meta_prompts if p.get("type") == "location"]):
            generation_order.append({
                "step": i + 2,
                "type": "location_generation",
                "prompt": prompt,
                "actions": ["generate_location_art", "create_location_lore", "populate_with_npcs"]
            })
        
        # Then: Characters and NPCs
        for i, prompt in enumerate([p for p in meta_prompts if p.get("type") == "character"]):
            generation_order.append({
                "step": len(generation_order) + 1,
                "type": "character_generation", 
                "prompt": prompt,
                "actions": ["generate_character_sprite", "create_dialogue", "set_quest_relationships"]
            })
        
        # Finally: Quests and narrative
        for i, prompt in enumerate([p for p in meta_prompts if p.get("type") == "quest"]):
            generation_order.append({
                "step": len(generation_order) + 1,
                "type": "quest_generation",
                "prompt": prompt,
                "actions": ["create_quest_structure", "generate_dialogue_tree", "export_yarn_files"]
            })
        
        estimated_time = len(generation_order) * 2  # 2 minutes per step estimate
        
        plan = GenerationPlan(
            world_id=world_format.id,
            total_locations=target_content["locations"],
            asset_count={
                "sprites": target_content["sprites"],
                "tiles": target_content["tiles"],
                "ui_elements": target_content["ui_elements"]
            },
            narrative_count={
                "quests": target_content["quests"],
                "npcs": target_content["npcs"]
            },
            generation_order=generation_order,
            estimated_time=estimated_time
        )
        
        return plan
    
    async def execute_generation_plan(
        self,
        plan: GenerationPlan,
        world_format: WorldFormat
    ) -> Dict[str, Any]:
        """Execute the complete generation plan."""
        
        results = {
            "world_id": plan.world_id,
            "completed_steps": [],
            "generated_assets": {},
            "generated_narrative": {},
            "status": "in_progress"
        }
        
        try:
            for step in plan.generation_order:
                logger.info(f"Executing step {step['step']}: {step['type']}")
                
                step_results = await self._execute_generation_step(step, world_format)
                
                results["completed_steps"].append({
                    "step": step["step"],
                    "type": step["type"],
                    "results": step_results,
                    "timestamp": asyncio.get_event_loop().time()
                })
                
                # Update counters
                if step["type"] == "location_generation":
                    results["generated_assets"]["locations"] = results["generated_assets"].get("locations", 0) + 1
                elif step["type"] == "character_generation":
                    results["generated_narrative"]["npcs"] = results["generated_narrative"].get("npcs", 0) + 1
                elif step["type"] == "quest_generation":
                    results["generated_narrative"]["quests"] = results["generated_narrative"].get("quests", 0) + 1
            
            results["status"] = "completed"
            
        except Exception as e:
            logger.error(f"Generation plan execution failed: {e}")
            results["status"] = "failed"
            results["error"] = str(e)
        
        # Save results
        await self._save_generation_results(results)
        
        return results
    
    async def _create_world_seeds(self, world_format: WorldFormat):
        """Create comprehensive seed data for consistent world generation."""
        
        project_context = f"{world_format.name.lower().replace(' ', '_')}_{world_format.game_type.value}"
        
        # Style guide seed
        await seed_queue.add_seed(
            seed_type=SeedType.STYLE_GUIDE,
            title=f"{world_format.name} Visual Style",
            content=f"{world_format.theme} aesthetic in {world_format.setting}, {world_format.tone} tone, {world_format.game_type.value} game style",
            priority=SeedPriority.CRITICAL,
            tags=["style", "visual", world_format.theme.lower()],
            project_context=project_context
        )
        
        # World lore seed
        await seed_queue.add_seed(
            seed_type=SeedType.WORLD_LORE,
            title=f"{world_format.name} World Lore",
            content=f"World setting: {world_format.setting}. Regions: {', '.join([r['name'] for r in world_format.regions])}. Major conflicts: {', '.join([c['description'] for c in world_format.conflicts])}",
            priority=SeedPriority.HIGH,
            tags=["world", "lore", "setting"],
            project_context=project_context
        )
        
        # Technical specs seed
        await seed_queue.add_seed(
            seed_type=SeedType.TECHNICAL_SPEC,
            title=f"{world_format.game_type.value.upper()} Technical Requirements",
            content=f"Game type: {world_format.game_type.value}. Core mechanics: {', '.join(world_format.core_mechanics)}. Content types: {', '.join(world_format.content_types)}",
            priority=SeedPriority.HIGH,
            tags=["technical", world_format.game_type.value, "bevy"],
            project_context=project_context
        )
        
        # Faction seeds
        for faction in world_format.factions:
            await seed_queue.add_seed(
                seed_type=SeedType.CHARACTER_SHEET,
                title=f"{faction['name']} Faction",
                content=f"Faction: {faction['name']}. Goals: {faction['goals']}. Characteristics: {faction['characteristics']}",
                priority=SeedPriority.MEDIUM,
                tags=["faction", faction['name'].lower(), "character"],
                project_context=project_context
            )
    
    async def _execute_generation_step(
        self,
        step: Dict[str, Any],
        world_format: WorldFormat
    ) -> Dict[str, Any]:
        """Execute a single generation step."""
        
        # This is a simplified implementation - in practice, each step would
        # call the appropriate generation tools based on the step type
        
        if step["type"] == "world_setup":
            return {"message": "World seeds created", "assets": ["base_style_guide"]}
        
        elif step["type"] == "location_generation":
            # Generate location using the prompt
            location_name = step["prompt"].get("name", f"Location_{step['step']}")
            return {
                "location": location_name,
                "assets": [f"{location_name}_tilemap", f"{location_name}_background"],
                "lore_file": f"{location_name}_lore.json"
            }
        
        elif step["type"] == "character_generation":
            character_name = step["prompt"].get("name", f"Character_{step['step']}")
            return {
                "character": character_name,
                "assets": [f"{character_name}_sprite"],
                "dialogue": f"{character_name}_dialogue.yarn"
            }
        
        elif step["type"] == "quest_generation":
            quest_title = step["prompt"].get("name", f"Quest_{step['step']}")
            return {
                "quest": quest_title,
                "dialogue_tree": f"{quest_title}_quest.yarn",
                "requirements": step["prompt"].get("requirements", [])
            }
        
        return {"message": f"Executed {step['type']}", "step": step["step"]}
    
    async def _save_world_format(self, world_format: WorldFormat):
        """Save world format to disk."""
        world_file = self.worlds_dir / f"{world_format.id}.json"
        
        async with aiofiles.open(world_file, 'w') as f:
            await f.write(json.dumps(world_format.to_dict(), indent=2))
    
    async def _save_generation_results(self, results: Dict[str, Any]):
        """Save generation results."""
        results_file = self.worlds_dir / f"{results['world_id']}_generation_results.json"
        
        async with aiofiles.open(results_file, 'w') as f:
            await f.write(json.dumps(results, indent=2))
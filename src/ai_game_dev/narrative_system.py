"""Advanced narrative and dialogue generation system with YarnSpinner integration."""

import asyncio
import json
import re
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
from enum import Enum
from dataclasses import dataclass, asdict
from datetime import datetime

import aiofiles
from openai import AsyncOpenAI

from ai_game_dev.config import settings
from ai_game_dev.logging_config import get_logger
from ai_game_dev.seed_system import seed_queue, SeedType, SeedPriority
from ai_game_dev.utils import ensure_directory_exists

logger = get_logger(__name__, component="narrative_system")


class DialogueType(str, Enum):
    """Types of dialogue content."""
    QUEST_GIVER = "quest_giver"
    SHOPKEEPER = "shopkeeper" 
    NPC_CHAT = "npc_chat"
    STORY_EXPOSITION = "story_exposition"
    TUTORIAL = "tutorial"
    FLAVOR_TEXT = "flavor_text"
    COMBAT_BARK = "combat_bark"
    ITEM_DESCRIPTION = "item_description"


class NarrativeContext(str, Enum):
    """Narrative context types."""
    MAIN_QUEST = "main_quest"
    SIDE_QUEST = "side_quest"
    WORLD_BUILDING = "world_building"
    CHARACTER_BACKSTORY = "character_backstory"
    LOCATION_LORE = "location_lore"
    ITEM_LORE = "item_lore"


@dataclass
class QuestData:
    """Structured quest information."""
    id: str
    title: str
    description: str
    objectives: List[str]
    rewards: List[str]
    difficulty: str
    location: str
    quest_giver: str
    requirements: List[str]
    dialogue_tree: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class DialogueNode:
    """Individual dialogue node."""
    id: str
    character: str
    text: str
    options: List[Dict[str, str]]  # {"text": "...", "next": "node_id"}
    conditions: List[str]  # Game state conditions
    consequences: List[str]  # Actions this dialogue triggers
    
    def to_yarn_format(self) -> str:
        """Convert to YarnSpinner format."""
        yarn_content = f"title: {self.id}\n"
        yarn_content += f"tags: {self.character}\n"
        yarn_content += "---\n"
        yarn_content += f"{self.character}: {self.text}\n"
        
        if self.options:
            for i, option in enumerate(self.options):
                yarn_content += f"-> {option['text']}\n"
                if option.get('next'):
                    yarn_content += f"    <<jump {option['next']}>>\n"
                if option.get('condition'):
                    yarn_content += f"    <<if {option['condition']}>>\n"
        
        yarn_content += "===\n"
        return yarn_content


class NarrativeGenerator:
    """Generates rich narrative content and dialogue trees."""
    
    def __init__(self, openai_client: AsyncOpenAI):
        self.client = openai_client
        self.narrative_dir = settings.cache_dir / "narrative"
        self.yarn_dir = self.narrative_dir / "yarn"
        
    async def initialize(self):
        """Initialize narrative directories."""
        await ensure_directory_exists(self.narrative_dir)
        await ensure_directory_exists(self.yarn_dir)
    
    async def generate_quest_with_dialogue(
        self,
        quest_brief: str,
        location: str,
        difficulty: str = "medium",
        quest_type: str = "main_quest",
        project_context: Optional[str] = None
    ) -> QuestData:
        """Generate complete quest with full dialogue tree."""
        
        # Consume relevant seeds for context
        context_seeds = await seed_queue.consume_seeds(
            query_tags=["quest", "narrative", "dialogue", "story"],
            project_context=project_context,
            max_seeds=5
        )
        
        # Build enhanced context
        world_context = self._build_narrative_context(context_seeds, quest_brief, location)
        
        # Generate quest structure
        quest_prompt = f"""
        Create a detailed {difficulty} difficulty {quest_type} for a fantasy RPG game.

        Brief: {quest_brief}
        Location: {location}
        
        World Context: {world_context}
        
        Generate a quest with:
        1. Compelling title and description
        2. 3-5 clear objectives
        3. Appropriate rewards
        4. Quest giver character with personality
        5. Requirements/prerequisites
        
        Format as JSON with keys: title, description, objectives, rewards, quest_giver, requirements.
        """
        
        response = await self.client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": quest_prompt}],
            response_format={"type": "json_object"}
        )
        
        quest_data = json.loads(response.choices[0].message.content)
        
        # Generate dialogue tree for the quest
        dialogue_tree = await self._generate_dialogue_tree(
            quest_data, world_context, project_context
        )
        
        quest = QuestData(
            id=str(uuid.uuid4()),
            title=quest_data["title"],
            description=quest_data["description"],
            objectives=quest_data["objectives"],
            rewards=quest_data["rewards"],
            difficulty=difficulty,
            location=location,
            quest_giver=quest_data["quest_giver"],
            requirements=quest_data.get("requirements", []),
            dialogue_tree=dialogue_tree
        )
        
        # Save quest data
        await self._save_quest(quest, project_context)
        
        return quest
    
    async def generate_npc_dialogue(
        self,
        character_name: str,
        character_role: str,
        location: str,
        dialogue_type: DialogueType,
        context: Optional[str] = None,
        project_context: Optional[str] = None
    ) -> List[DialogueNode]:
        """Generate contextual NPC dialogue."""
        
        # Get character and world context from seeds
        context_seeds = await seed_queue.consume_seeds(
            query_tags=["character", "npc", "dialogue", character_role.lower()],
            project_context=project_context,
            max_seeds=3
        )
        
        world_context = self._build_narrative_context(context_seeds, context or "", location)
        
        dialogue_prompt = f"""
        Create engaging dialogue for an NPC in a fantasy RPG.
        
        Character: {character_name} ({character_role})
        Location: {location}
        Dialogue Type: {dialogue_type.value}
        Context: {context or "General interaction"}
        
        World Context: {world_context}
        
        Generate 3-5 dialogue options that:
        1. Match the character's role and personality
        2. Fit the location and world context
        3. Provide meaningful player choices
        4. Include appropriate consequences
        
        Format as JSON array with objects containing: text, character_response, consequences.
        """
        
        response = await self.client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": dialogue_prompt}],
            response_format={"type": "json_object"}
        )
        
        dialogue_data = json.loads(response.choices[0].message.content)
        
        # Convert to dialogue nodes
        dialogue_nodes = []
        for i, option in enumerate(dialogue_data.get("dialogue_options", [])):
            node = DialogueNode(
                id=f"{character_name.lower()}_{dialogue_type.value}_{i}",
                character=character_name,
                text=option["character_response"],
                options=[{
                    "text": option["text"],
                    "next": None  # Can be linked later
                }],
                conditions=[],
                consequences=option.get("consequences", [])
            )
            dialogue_nodes.append(node)
        
        return dialogue_nodes
    
    async def generate_location_lore(
        self,
        location_name: str,
        location_type: str,
        importance: str = "medium",
        project_context: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate rich lore and descriptions for game locations."""
        
        # Get world-building seeds
        context_seeds = await seed_queue.consume_seeds(
            query_tags=["world", "lore", "location", location_type.lower()],
            project_context=project_context,
            max_seeds=4
        )
        
        world_context = self._build_narrative_context(context_seeds, "", location_name)
        
        lore_prompt = f"""
        Create rich lore and descriptions for a game location.
        
        Location: {location_name}
        Type: {location_type}
        Importance: {importance}
        
        World Context: {world_context}
        
        Generate comprehensive lore including:
        1. Visual description (for asset generation)
        2. Historical background
        3. Current situation/conflicts
        4. Notable NPCs who might be found here
        5. Secrets or hidden elements
        6. Connections to other locations
        
        Format as JSON with keys: visual_description, history, current_situation, notable_npcs, secrets, connections.
        """
        
        response = await self.client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": lore_prompt}],
            response_format={"type": "json_object"}
        )
        
        lore_data = json.loads(response.choices[0].message.content)
        
        # Save location lore
        await self._save_location_lore(location_name, lore_data, project_context)
        
        return lore_data
    
    async def export_to_yarnspinner(
        self,
        dialogue_nodes: List[DialogueNode],
        filename: str,
        project_context: Optional[str] = None
    ) -> str:
        """Export dialogue to YarnSpinner format."""
        
        yarn_content = []
        
        for node in dialogue_nodes:
            yarn_content.append(node.to_yarn_format())
        
        # Create project-specific directory
        if project_context:
            yarn_project_dir = self.yarn_dir / project_context
            await ensure_directory_exists(yarn_project_dir)
            yarn_file_path = yarn_project_dir / f"{filename}.yarn"
        else:
            yarn_file_path = self.yarn_dir / f"{filename}.yarn"
        
        # Write YarnSpinner file
        async with aiofiles.open(yarn_file_path, 'w') as f:
            await f.write("\n".join(yarn_content))
        
        logger.info(f"Exported dialogue to YarnSpinner: {yarn_file_path}")
        return str(yarn_file_path)
    
    def _build_narrative_context(
        self,
        seeds: List[Any],
        base_context: str,
        location: str
    ) -> str:
        """Build enhanced narrative context from seeds."""
        
        context_parts = [base_context] if base_context else []
        
        for seed in seeds:
            if seed.seed_type == SeedType.WORLD_LORE:
                context_parts.append(f"World: {seed.content}")
            elif seed.seed_type == SeedType.CHARACTER_SHEET:
                context_parts.append(f"Character reference: {seed.content}")
            elif seed.seed_type == SeedType.NARRATIVE_CONTEXT:
                context_parts.append(f"Story context: {seed.content}")
            elif seed.seed_type == SeedType.STYLE_GUIDE:
                context_parts.append(f"Tone/Style: {seed.content}")
        
        context_parts.append(f"Setting: {location}")
        
        return ". ".join(context_parts)
    
    async def _generate_dialogue_tree(
        self,
        quest_data: Dict[str, Any],
        world_context: str,
        project_context: Optional[str]
    ) -> Dict[str, Any]:
        """Generate complete dialogue tree for quest."""
        
        tree_prompt = f"""
        Create a complete dialogue tree for this quest:
        
        Quest: {quest_data['title']}
        Description: {quest_data['description']}
        Quest Giver: {quest_data['quest_giver']}
        
        Context: {world_context}
        
        Generate dialogue tree with:
        1. Initial quest offer conversation
        2. Quest progress check-ins
        3. Quest completion dialogue
        4. Optional rejection/alternative paths
        
        Include player response options and branching paths.
        Format as nested JSON structure with node IDs and connections.
        """
        
        response = await self.client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": tree_prompt}],
            response_format={"type": "json_object"}
        )
        
        return json.loads(response.choices[0].message.content)
    
    async def _save_quest(
        self,
        quest: QuestData,
        project_context: Optional[str]
    ):
        """Save quest data to disk."""
        
        if project_context:
            quest_dir = self.narrative_dir / project_context / "quests"
        else:
            quest_dir = self.narrative_dir / "quests"
        
        await ensure_directory_exists(quest_dir)
        
        quest_file = quest_dir / f"{quest.id}.json"
        
        async with aiofiles.open(quest_file, 'w') as f:
            await f.write(json.dumps(quest.to_dict(), indent=2))
    
    async def _save_location_lore(
        self,
        location_name: str,
        lore_data: Dict[str, Any],
        project_context: Optional[str]
    ):
        """Save location lore to disk."""
        
        if project_context:
            lore_dir = self.narrative_dir / project_context / "locations"
        else:
            lore_dir = self.narrative_dir / "locations"
        
        await ensure_directory_exists(lore_dir)
        
        lore_file = lore_dir / f"{location_name.lower().replace(' ', '_')}.json"
        
        async with aiofiles.open(lore_file, 'w') as f:
            await f.write(json.dumps(lore_data, indent=2))
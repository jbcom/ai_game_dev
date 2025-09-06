"""Advanced game specification analyzer and metaprompt refinement system."""

import asyncio
import json
import re
import yaml
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, Tuple
from enum import Enum
from dataclasses import dataclass, asdict

import aiofiles
import tomli
from openai import AsyncOpenAI

from ai_game_dev.config import settings
from ai_game_dev.logging_config import get_logger
from ai_game_dev.seed_system import seed_queue, SeedType, SeedPriority
from ai_game_dev.utils import ensure_directory_exists

logger = get_logger(__name__, component="spec_analyzer")


class SpecFormat(str, Enum):
    """Supported specification formats."""
    NATURAL_LANGUAGE = "natural_language"
    JSON = "json"
    YAML = "yaml"
    TOML = "toml"
    MARKDOWN = "markdown"
    MIXED = "mixed"
    UNKNOWN = "unknown"


class GameEngine(str, Enum):
    """Supported game engines with specific workflows."""
    BEVY = "bevy"
    UNITY = "unity"
    GODOT = "godot"
    UNREAL = "unreal"
    PYGAME = "pygame"
    LOVE2D = "love2d"
    GENERIC = "generic"


@dataclass
class EngineWorkflow:
    """Engine-specific workflow recommendations."""
    engine: GameEngine
    project_structure: Dict[str, Any]
    asset_pipeline: List[str]
    code_patterns: Dict[str, str]
    integration_steps: List[str]
    yarn_integration: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class WorldWorkflow:
    """World-building workflow recommendations."""
    world_structure: Dict[str, Any]
    content_organization: Dict[str, List[str]]
    generation_priorities: List[str]
    narrative_structure: Dict[str, Any]
    asset_categories: Dict[str, List[str]]
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class RefinedGameSpec:
    """Refined and structured game specification."""
    original_format: SpecFormat
    game_title: str
    game_type: str
    target_engine: GameEngine
    
    # Core game elements
    world_description: str
    gameplay_mechanics: List[str]
    narrative_elements: Dict[str, Any]
    visual_style: Dict[str, Any]
    
    # Extracted seeds
    suggested_seeds: List[Dict[str, Any]]
    
    # Workflows
    engine_workflow: EngineWorkflow
    world_workflow: WorldWorkflow
    
    # Generation plan
    recommended_generation_order: List[Dict[str, Any]]
    estimated_complexity: str
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class GameSpecAnalyzer:
    """Analyzes game specifications in any format and creates optimized workflows."""
    
    def __init__(self, openai_client: AsyncOpenAI):
        self.client = openai_client
        self.specs_dir = settings.cache_dir / "game_specs"
        
    async def initialize(self):
        """Initialize the spec analyzer."""
        await ensure_directory_exists(self.specs_dir)
    
    async def analyze_game_spec(
        self,
        spec_content: str,
        spec_format: Optional[SpecFormat] = None
    ) -> RefinedGameSpec:
        """Analyze any format game specification and create refined workflows."""
        
        # Auto-detect format if not provided
        if spec_format is None:
            spec_format = self._detect_format(spec_content)
        
        # Parse content based on format
        structured_data = await self._parse_spec_content(spec_content, spec_format)
        
        # Extract game elements using AI analysis
        game_elements = await self._extract_game_elements(spec_content, structured_data)
        
        # Determine optimal engine
        recommended_engine = await self._recommend_engine(game_elements)
        
        # Create engine workflow
        engine_workflow = await self._create_engine_workflow(
            recommended_engine, game_elements
        )
        
        # Create world workflow
        world_workflow = await self._create_world_workflow(game_elements)
        
        # Generate suggested seeds
        suggested_seeds = await self._generate_suggested_seeds(game_elements)
        
        # Create generation order
        generation_order = await self._create_generation_order(
            game_elements, recommended_engine
        )
        
        refined_spec = RefinedGameSpec(
            original_format=spec_format,
            game_title=game_elements.get("title", "Untitled Game"),
            game_type=game_elements.get("game_type", "adventure"),
            target_engine=recommended_engine,
            world_description=game_elements.get("world_description", ""),
            gameplay_mechanics=game_elements.get("mechanics", []),
            narrative_elements=game_elements.get("narrative", {}),
            visual_style=game_elements.get("visual_style", {}),
            suggested_seeds=suggested_seeds,
            engine_workflow=engine_workflow,
            world_workflow=world_workflow,
            recommended_generation_order=generation_order,
            estimated_complexity=game_elements.get("complexity", "medium")
        )
        
        # Save refined spec
        await self._save_refined_spec(refined_spec)
        
        return refined_spec
    
    def _detect_format(self, content: str) -> SpecFormat:
        """Auto-detect specification format."""
        content = content.strip()
        
        # Check for structured formats
        if content.startswith('{') and content.endswith('}'):
            try:
                json.loads(content)
                return SpecFormat.JSON
            except:
                pass
        
        if content.startswith('[') or any(line.strip().startswith('-') for line in content.split('\n')):
            try:
                yaml.safe_load(content)
                return SpecFormat.YAML
            except:
                pass
        
        if any(line.strip().startswith('[') and line.strip().endswith(']') for line in content.split('\n')):
            try:
                tomli.loads(content)
                return SpecFormat.TOML
            except:
                pass
        
        if content.startswith('#') or '##' in content or '###' in content:
            return SpecFormat.MARKDOWN
        
        # Check for mixed formats
        format_indicators = 0
        if '{' in content and '}' in content:
            format_indicators += 1
        if '- ' in content or '  - ' in content:
            format_indicators += 1
        if '[' in content and ']' in content:
            format_indicators += 1
        
        if format_indicators >= 2:
            return SpecFormat.MIXED
        
        return SpecFormat.NATURAL_LANGUAGE
    
    async def _parse_spec_content(
        self, 
        content: str, 
        spec_format: SpecFormat
    ) -> Dict[str, Any]:
        """Parse specification content based on format."""
        
        if spec_format == SpecFormat.JSON:
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                return {"raw_content": content}
        
        elif spec_format == SpecFormat.YAML:
            try:
                return yaml.safe_load(content)
            except yaml.YAMLError:
                return {"raw_content": content}
        
        elif spec_format == SpecFormat.TOML:
            try:
                return tomli.loads(content)
            except tomli.TOMLDecodeError:
                return {"raw_content": content}
        
        elif spec_format == SpecFormat.MARKDOWN:
            return self._parse_markdown_spec(content)
        
        else:  # Natural language or mixed
            return {"raw_content": content}
    
    def _parse_markdown_spec(self, content: str) -> Dict[str, Any]:
        """Parse markdown-formatted game specification."""
        
        parsed_data = {"sections": {}}
        current_section = None
        current_content = []
        
        for line in content.split('\n'):
            line = line.strip()
            
            if line.startswith('#'):
                # Save previous section
                if current_section:
                    parsed_data["sections"][current_section] = '\n'.join(current_content)
                
                # Start new section
                current_section = line.lstrip('#').strip().lower().replace(' ', '_')
                current_content = []
            
            elif line and current_section:
                current_content.append(line)
        
        # Save last section
        if current_section:
            parsed_data["sections"][current_section] = '\n'.join(current_content)
        
        return parsed_data
    
    async def _extract_game_elements(
        self, 
        raw_content: str, 
        structured_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Use AI to extract key game elements from specification."""
        
        extraction_prompt = f"""
        Analyze this game specification and extract key elements for game development:
        
        Raw Content:
        {raw_content}
        
        Structured Data:
        {json.dumps(structured_data, indent=2)}
        
        Extract and return JSON with these elements:
        {{
            "title": "Game title",
            "game_type": "rpg/platformer/fps/puzzle/adventure/etc",
            "world_description": "Detailed world setting and theme",
            "mechanics": ["core gameplay mechanics"],
            "narrative": {{
                "main_story": "Primary narrative arc",
                "themes": ["narrative themes"],
                "characters": ["key characters mentioned"],
                "conflicts": ["central conflicts"]
            }},
            "visual_style": {{
                "art_style": "Visual aesthetic description",
                "color_palette": "Color scheme description",
                "mood": "Visual mood and tone"
            }},
            "technical_requirements": {{
                "target_platform": "PC/mobile/console/web",
                "complexity": "simple/medium/complex",
                "special_features": ["unique technical needs"]
            }},
            "content_scope": {{
                "estimated_locations": number,
                "estimated_characters": number,
                "estimated_quests": number
            }}
        }}
        """
        
        response = await self.client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": extraction_prompt}],
            response_format={"type": "json_object"}
        )
        
        return json.loads(response.choices[0].message.content)
    
    async def _recommend_engine(self, game_elements: Dict[str, Any]) -> GameEngine:
        """Recommend optimal game engine based on game elements."""
        
        recommendation_prompt = f"""
        Based on this game specification, recommend the best game engine:
        
        Game Type: {game_elements.get('game_type', 'unknown')}
        Complexity: {game_elements.get('technical_requirements', {}).get('complexity', 'medium')}
        Platform: {game_elements.get('technical_requirements', {}).get('target_platform', 'PC')}
        Special Features: {game_elements.get('technical_requirements', {}).get('special_features', [])}
        
        World: {game_elements.get('world_description', '')}
        Mechanics: {game_elements.get('mechanics', [])}
        
        Consider these engines: Bevy (Rust, ECS, modern), Unity (C#, versatile), Godot (GDScript/C#, indie-friendly), 
        Unreal (C++/Blueprint, AAA), PyGame (Python, simple), Love2D (Lua, 2D focus).
        
        Return just the engine name: bevy, unity, godot, unreal, pygame, love2d, or generic.
        """
        
        response = await self.client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": recommendation_prompt}]
        )
        
        engine_name = response.choices[0].message.content.strip().lower()
        
        # Map to enum
        engine_mapping = {
            "bevy": GameEngine.BEVY,
            "unity": GameEngine.UNITY,
            "godot": GameEngine.GODOT,
            "unreal": GameEngine.UNREAL,
            "pygame": GameEngine.PYGAME,
            "love2d": GameEngine.LOVE2D
        }
        
        return engine_mapping.get(engine_name, GameEngine.BEVY)  # Default to Bevy
    
    async def _create_engine_workflow(
        self, 
        engine: GameEngine, 
        game_elements: Dict[str, Any]
    ) -> EngineWorkflow:
        """Create engine-specific workflow recommendations."""
        
        if engine == GameEngine.BEVY:
            return EngineWorkflow(
                engine=engine,
                project_structure={
                    "src/": ["main.rs", "lib.rs", "components/", "systems/", "resources/"],
                    "assets/": ["sprites/", "audio/", "fonts/", "dialogue/"],
                    "Cargo.toml": "Bevy dependencies and project config"
                },
                asset_pipeline=[
                    "Generate sprites as PNG with transparency",
                    "Create tilemaps as texture atlases",
                    "Export dialogue as .yarn files",
                    "Configure asset loading in Bevy systems"
                ],
                code_patterns={
                    "ecs_components": "Derive Component for game entities",
                    "systems": "Use In<> and Out<> for system parameters",
                    "resources": "Use Resource derive for global state",
                    "assets": "Handle<T> for asset references"
                },
                integration_steps=[
                    "Add bevy and bevy_yarnspinner to Cargo.toml",
                    "Create component definitions for game entities",
                    "Set up asset loading systems",
                    "Configure dialogue system integration",
                    "Implement game state management"
                ],
                yarn_integration={
                    "library": "bevy_yarnspinner",
                    "setup": "Add YarnSpinnerPlugin to app",
                    "dialogue_files": "Load .yarn files as assets",
                    "integration": "Use dialogue events in game systems"
                }
            )
        
        elif engine == GameEngine.GODOT:
            return EngineWorkflow(
                engine=engine,
                project_structure={
                    "scenes/": ["Main.tscn", "Player.tscn", "UI.tscn"],
                    "scripts/": ["Player.gd", "GameManager.gd", "DialogueManager.gd"],
                    "assets/": ["sprites/", "audio/", "fonts/", "dialogue/"],
                    "project.godot": "Project configuration"
                },
                asset_pipeline=[
                    "Import sprites as Texture2D resources",
                    "Create scenes for reusable components",
                    "Set up dialogue system with YarnSpinner-Godot",
                    "Configure resource paths"
                ],
                code_patterns={
                    "nodes": "Extend Node2D/3D for game objects",
                    "signals": "Connect signals for event communication",
                    "resources": "Create custom Resource classes",
                    "scenes": "Instantiate scenes for dynamic content"
                },
                integration_steps=[
                    "Install YarnSpinner for Godot addon",
                    "Create dialogue manager singleton",
                    "Set up character controller scripts",
                    "Configure UI system with dialogue boxes",
                    "Implement save/load system"
                ],
                yarn_integration={
                    "library": "YarnSpinner-Godot",
                    "setup": "Add YarnSpinner addon to project",
                    "dialogue_files": "Import .yarn files to dialogue folder",
                    "integration": "Use YarnDialogue node in scenes"
                }
            )
        
        else:  # Generic workflow
            return EngineWorkflow(
                engine=engine,
                project_structure={
                    "src/": ["main file", "game logic", "components/"],
                    "assets/": ["sprites/", "audio/", "dialogue/"],
                    "config/": ["settings", "asset definitions"]
                },
                asset_pipeline=[
                    "Organize assets by category",
                    "Create loading system for game assets",
                    "Set up dialogue file integration",
                    "Configure asset resolution and scaling"
                ],
                code_patterns={
                    "entities": "Create entity/component system",
                    "states": "Implement game state management", 
                    "events": "Set up event/message system",
                    "assets": "Create asset management system"
                },
                integration_steps=[
                    "Research YarnSpinner library for chosen engine",
                    "Set up project structure and dependencies",
                    "Create core game systems",
                    "Integrate dialogue and narrative system",
                    "Implement asset loading pipeline"
                ],
                yarn_integration={
                    "library": "Language-specific YarnSpinner binding",
                    "setup": "Install via package manager",
                    "dialogue_files": "Load and parse .yarn files",
                    "integration": "Connect to game event system"
                }
            )
    
    async def _create_world_workflow(self, game_elements: Dict[str, Any]) -> WorldWorkflow:
        """Create world-building workflow recommendations."""
        
        return WorldWorkflow(
            world_structure={
                "regions": f"Create {game_elements.get('content_scope', {}).get('estimated_locations', 3)} distinct areas",
                "factions": "Define major groups and their relationships",
                "timeline": "Establish world history and current events",
                "rules": "Define world's magic/technology systems"
            },
            content_organization={
                "narrative": ["main_story", "side_quests", "character_arcs", "world_lore"],
                "characters": ["protagonists", "antagonists", "npcs", "background_characters"],
                "locations": ["major_areas", "towns", "dungeons", "secret_areas"],
                "items": ["weapons", "tools", "collectibles", "quest_items"]
            },
            generation_priorities=[
                "Core world concept and theme",
                "Main story structure and conflicts",
                "Key locations and their purposes",
                "Primary characters and relationships",
                "Visual style and asset requirements",
                "Dialogue and narrative content",
                "Supporting content and polish"
            ],
            narrative_structure={
                "acts": "Divide story into 3-5 major acts",
                "pacing": "Balance action, exploration, and story",
                "player_choice": "Define meaningful decision points",
                "character_development": "Plan character growth arcs"
            },
            asset_categories={
                "characters": ["player", "npcs", "enemies", "background"],
                "environments": ["tiles", "backgrounds", "props", "effects"],
                "ui": ["menus", "dialogs", "hud", "buttons"],
                "audio": ["music", "sfx", "voice", "ambient"]
            }
        )
    
    async def _generate_suggested_seeds(self, game_elements: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate suggested seed data based on game elements."""
        
        seeds = []
        
        # Style guide seed
        if game_elements.get("visual_style"):
            seeds.append({
                "type": "style_guide",
                "priority": "critical",
                "title": f"{game_elements.get('title', 'Game')} Visual Style",
                "content": f"Art style: {game_elements['visual_style'].get('art_style', '')}. Color palette: {game_elements['visual_style'].get('color_palette', '')}. Mood: {game_elements['visual_style'].get('mood', '')}",
                "tags": ["style", "visual", "art"]
            })
        
        # World lore seed
        if game_elements.get("world_description"):
            seeds.append({
                "type": "world_lore",
                "priority": "high",
                "title": f"{game_elements.get('title', 'Game')} World",
                "content": game_elements["world_description"],
                "tags": ["world", "lore", "setting"]
            })
        
        # Character seeds
        if game_elements.get("narrative", {}).get("characters"):
            for character in game_elements["narrative"]["characters"][:3]:  # Limit to top 3
                seeds.append({
                    "type": "character_sheet", 
                    "priority": "high",
                    "title": f"Character: {character}",
                    "content": f"Key character in {game_elements.get('title', 'the game')}: {character}. Role and personality to be developed.",
                    "tags": ["character", character.lower().replace(" ", "_")]
                })
        
        # Technical spec seed
        if game_elements.get("technical_requirements"):
            tech_req = game_elements["technical_requirements"]
            seeds.append({
                "type": "technical_spec",
                "priority": "high",
                "title": "Technical Requirements",
                "content": f"Platform: {tech_req.get('target_platform', 'PC')}. Complexity: {tech_req.get('complexity', 'medium')}. Special features: {', '.join(tech_req.get('special_features', []))}",
                "tags": ["technical", "requirements"]
            })
        
        # Narrative context seed
        if game_elements.get("narrative", {}).get("main_story"):
            seeds.append({
                "type": "narrative_context",
                "priority": "medium",
                "title": "Main Story Context",
                "content": game_elements["narrative"]["main_story"],
                "tags": ["narrative", "story", "main_quest"]
            })
        
        return seeds
    
    async def _create_generation_order(
        self, 
        game_elements: Dict[str, Any], 
        engine: GameEngine
    ) -> List[Dict[str, Any]]:
        """Create recommended generation order for game content."""
        
        order = []
        
        # Phase 1: Foundation
        order.append({
            "phase": 1,
            "name": "Foundation Setup",
            "description": "Create world format and core seeds",
            "actions": [
                "Analyze game specification",
                "Create world format structure",
                "Generate foundational seeds",
                "Set up project structure"
            ],
            "estimated_time": "10-15 minutes"
        })
        
        # Phase 2: Core Content
        order.append({
            "phase": 2,
            "name": "Core Content Generation",
            "description": "Generate primary game elements",
            "actions": [
                "Create main locations and environments",
                "Generate key characters and NPCs",
                "Develop primary quests and storylines",
                "Create essential game assets"
            ],
            "estimated_time": "30-45 minutes"
        })
        
        # Phase 3: Narrative Integration
        order.append({
            "phase": 3,
            "name": "Narrative Integration",
            "description": "Create dialogue and story content",
            "actions": [
                "Generate dialogue trees for NPCs",
                "Create quest dialogue and cutscenes",
                "Export YarnSpinner files",
                "Link narrative to game mechanics"
            ],
            "estimated_time": "20-30 minutes"
        })
        
        # Phase 4: Engine Integration
        order.append({
            "phase": 4,
            "name": f"{engine.value.title()} Integration",
            "description": "Prepare content for game engine",
            "actions": [
                f"Generate {engine.value}-specific code templates",
                "Create component and system definitions",
                "Set up asset loading pipeline",
                "Configure dialogue system integration"
            ],
            "estimated_time": "15-20 minutes"
        })
        
        # Phase 5: Polish and Expansion
        order.append({
            "phase": 5,
            "name": "Polish and Expansion",
            "description": "Add supporting content and refinements",
            "actions": [
                "Generate additional environmental assets",
                "Create UI elements and themes",
                "Add ambient dialogue and flavor text",
                "Generate item descriptions and lore"
            ],
            "estimated_time": "20-30 minutes"
        })
        
        return order
    
    async def _save_refined_spec(self, spec: RefinedGameSpec):
        """Save refined specification to disk."""
        
        spec_file = self.specs_dir / f"{spec.game_title.lower().replace(' ', '_')}_refined_spec.json"
        
        async with aiofiles.open(spec_file, 'w') as f:
            await f.write(json.dumps(spec.to_dict(), indent=2))
        
        logger.info(f"Saved refined game spec: {spec_file}")
    
    async def create_automatic_seeds(self, refined_spec: RefinedGameSpec, project_context: str):
        """Automatically create seed data from refined specification."""
        
        for seed_data in refined_spec.suggested_seeds:
            await seed_queue.add_seed(
                seed_type=SeedType(seed_data["type"]),
                title=seed_data["title"],
                content=seed_data["content"],
                priority=SeedPriority(seed_data["priority"]),
                tags=seed_data["tags"],
                project_context=project_context
            )
        
        logger.info(f"Created {len(refined_spec.suggested_seeds)} automatic seeds for {refined_spec.game_title}")
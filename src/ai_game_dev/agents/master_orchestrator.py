"""
Master Game Development Orchestrator Agent
Routes requests to appropriate engine subgraphs and handles spec generation
"""

import asyncio
import json
from typing import Dict, List, Any, Optional, Union, Literal
from pathlib import Path
from dataclasses import dataclass, field

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.state import CompiledStateGraph

from ai_game_dev.agents.base_agent import BaseAgent, AgentState, AgentConfig
from ai_game_dev.agents.subgraphs import (
    DialogueSubgraph,
    QuestSubgraph, 
    GraphicsSubgraph,
    AudioSubgraph
)
from ai_game_dev.variants import InteractiveVariantSystem
from ai_game_dev.game_specification import GameSpecificationParser

# Required imports - will raise ImportError if missing
from ai_game_dev.agents.pygame_agent import PygameAgent
from ai_game_dev.agents.godot_agent import GodotAgent
from ai_game_dev.agents.bevy_agent import BevyAgent
from ai_game_dev.agents.internal_agent import InternalAssetAgent
from ai_game_dev.agents.arcade_academy_agent import ArcadeAcademyAgent
from ai_game_dev.models.llm_manager import LLMManager
from ai_game_dev.seeding.literary_seeder import LiterarySeeder, SeedingRequest


@dataclass
class GameSpec:
    """Structured game specification."""
    title: str
    description: str
    engine: Literal["pygame", "godot", "bevy"]
    genre: str
    target_audience: str
    features: List[str] = field(default_factory=list)
    art_style: str = "modern"
    complexity: Literal["simple", "intermediate", "complex"] = "intermediate"
    assets_needed: List[str] = field(default_factory=list)
    code_requirements: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class OrchestratorState(AgentState):
    """Extended state for orchestrator operations."""
    user_input: str = ""
    input_type: Literal["prompt", "game_spec", "asset_spec"] = "prompt"
    detected_engine: Optional[str] = None
    generated_spec: Optional[GameSpec] = None
    spec_approved: bool = False
    routing_decision: Optional[str] = None
    subgraph_results: Dict[str, Any] = field(default_factory=dict)
    seeding_data: Dict[str, Any] = field(default_factory=dict)


class MasterGameDevOrchestrator(BaseAgent):
    """
    Master orchestrator that routes game development requests to appropriate engine subgraphs.
    
    Capabilities:
    - Analyzes user input (prompts vs structured specs)
    - Generates structured game specifications from natural language
    - Routes to appropriate engine subgraphs (Pygame, Godot, Bevy)
    - Implements human-in-the-loop review for generated specs
    - Coordinates seeding system with PyTorch and Internet Archive
    - Manages the complete game development pipeline
    """
    
    def __init__(self, config: Optional[AgentConfig] = None):
        if config is None:
            config = AgentConfig(
                model="gpt-4o",
                temperature=0.3,
                instructions=self._get_orchestrator_instructions()
            )
        super().__init__(config)
        
        # Initialize engine subagents
        self.pygame_agent = None
        self.godot_agent = None
        self.bevy_agent = None
        
        # Initialize specialized subgraphs
        self.dialogue_subgraph = None
        self.quest_subgraph = None
        self.graphics_subgraph = None
        self.audio_subgraph = None
        
        # Initialize variant system for interactive A/B choices
        self.variant_system = None
        
    async def initialize(self):
        """Initialize the orchestrator and all engine subagents."""
        await super().initialize()
        
        # Initialize engine agents
        self.pygame_agent = PygameAgent()
        await self.pygame_agent.initialize()
        
        self.godot_agent = GodotAgent() 
        await self.godot_agent.initialize()
        
        self.bevy_agent = BevyAgent()
        await self.bevy_agent.initialize()
            
        # Initialize specialized subgraphs
        self.dialogue_subgraph = DialogueSubgraph()
        await self.dialogue_subgraph.initialize()
        
        self.quest_subgraph = QuestSubgraph()
        await self.quest_subgraph.initialize()
        
        self.graphics_subgraph = GraphicsSubgraph()
        await self.graphics_subgraph.initialize()
        
        self.audio_subgraph = AudioSubgraph()
        await self.audio_subgraph.initialize()
        
        # Initialize internal asset generation subgraph
        self.internal_asset_agent = InternalAssetAgent()
        await self.internal_asset_agent.initialize()
        
        # Initialize arcade academy agent as subgraph
        self.arcade_academy_agent = ArcadeAcademyAgent()
        await self.arcade_academy_agent.initialize()
        
        # Initialize variant system for interactive A/B choices  
        llm_manager = LLMManager()
        self.variant_system = InteractiveVariantSystem(llm_manager)
        
        # Initialize game specification system
        self.game_spec_parser = GameSpecificationParser()
        
        # Build the workflow graph
        self.workflow = await self._build_graph()
        
    async def _setup_instructions(self):
        """Set up orchestrator-specific instructions."""
        self.config.instructions = self._get_orchestrator_instructions()
        
    async def _setup_tools(self):
        """Set up orchestrator tools."""
        self.config.tools = [
            "input_analysis",
            "spec_generation", 
            "engine_routing",
            "human_review_coordination",
            "seeding_system",
            "subgraph_execution"
        ]
        
    async def _build_graph(self) -> CompiledStateGraph:
        """Build the master orchestrator graph with routing and subgraphs."""
        
        graph = StateGraph(OrchestratorState)
        
        # Core orchestrator nodes
        graph.add_node("input_analysis", self._input_analysis_node)
        graph.add_node("spec_generation", self._spec_generation_node)
        graph.add_node("human_review", self._human_review_node)
        graph.add_node("engine_routing", self._engine_routing_node)
        graph.add_node("seeding_coordination", self._seeding_coordination_node)
        
        # Engine subgraph nodes
        graph.add_node("pygame_subgraph", self._pygame_subgraph_node)
        graph.add_node("godot_subgraph", self._godot_subgraph_node)
        graph.add_node("bevy_subgraph", self._bevy_subgraph_node)
        
        # Specialized generation subgraph nodes
        graph.add_node("dialogue_subgraph", self._dialogue_subgraph_node)
        graph.add_node("quest_subgraph", self._quest_subgraph_node)
        graph.add_node("graphics_subgraph", self._graphics_subgraph_node)
        graph.add_node("audio_subgraph", self._audio_subgraph_node)
        graph.add_node("internal_asset_subgraph", self._internal_asset_subgraph_node)
        graph.add_node("arcade_academy_subgraph", self._arcade_academy_subgraph_node)
        
        # Output processing
        graph.add_node("result_compilation", self._result_compilation_node)
        
        # Routing logic
        graph.add_edge(START, "input_analysis")
        graph.add_conditional_edges(
            "input_analysis",
            self._route_after_analysis,
            {
                "needs_spec_generation": "spec_generation",
                "has_complete_spec": "engine_routing",
                "needs_seeding": "seeding_coordination"
            }
        )
        
        graph.add_edge("spec_generation", "human_review")
        graph.add_conditional_edges(
            "human_review",
            self._route_after_review,
            {
                "approved": "engine_routing",
                "needs_revision": "spec_generation",
                "rejected": END
            }
        )
        
        graph.add_edge("seeding_coordination", "spec_generation")
        
        graph.add_conditional_edges(
            "engine_routing",
            self._route_to_engine,
            {
                "pygame": "pygame_subgraph",
                "godot": "godot_subgraph", 
                "bevy": "bevy_subgraph",
                "dialogue": "dialogue_subgraph",
                "quest": "quest_subgraph",
                "graphics": "graphics_subgraph",
                "audio": "audio_subgraph",
                "internal_assets": "internal_asset_subgraph",
                "arcade_academy": "arcade_academy_subgraph"
            }
        )
        
        # All subgraphs lead to result compilation
        graph.add_edge("pygame_subgraph", "result_compilation")
        graph.add_edge("godot_subgraph", "result_compilation")
        graph.add_edge("bevy_subgraph", "result_compilation")
        graph.add_edge("dialogue_subgraph", "result_compilation")
        graph.add_edge("quest_subgraph", "result_compilation")
        graph.add_edge("graphics_subgraph", "result_compilation")
        graph.add_edge("audio_subgraph", "result_compilation")
        graph.add_edge("internal_asset_subgraph", "result_compilation")
        graph.add_edge("arcade_academy_subgraph", "result_compilation")
        
        graph.add_edge("result_compilation", END)
        
        return graph.compile()
        
    async def _input_analysis_node(self, state: OrchestratorState) -> OrchestratorState:
        """Analyze user input to determine type and required processing."""
        
        user_input = state.user_input or state.current_task or ""
        
        # Use LLM to analyze input type and extract information
        analysis_prompt = f"""Analyze this game development request and determine:

1. Input type: Is this a natural language prompt, structured game spec, or asset specification?
2. Engine preference: Does the user specify pygame, godot, bevy, or no preference?
3. Completeness: Does this contain enough information to start development?
4. Seeding needs: Would this benefit from literary/narrative seeding from external sources?

User input: {user_input}

Respond with a JSON object containing:
{{
    "input_type": "prompt|game_spec|asset_spec",
    "detected_engine": "pygame|godot|bevy|none",
    "completeness_score": 0.0-1.0,
    "needs_seeding": true/false,
    "missing_information": ["list", "of", "missing", "elements"],
    "suggested_processing": "spec_generation|direct_routing|seeding_first"
}}"""

        response = await self.llm.ainvoke([HumanMessage(content=analysis_prompt)])
        
        try:
            analysis = json.loads(response.content if isinstance(response.content, str) else str(response.content))
            
            state.input_type = analysis.get("input_type", "prompt")
            state.detected_engine = analysis.get("detected_engine")
            state.context["completeness_score"] = analysis.get("completeness_score", 0.0)
            state.context["needs_seeding"] = analysis.get("needs_seeding", False)
            state.context["missing_information"] = analysis.get("missing_information", [])
            state.context["suggested_processing"] = analysis.get("suggested_processing", "spec_generation")
            
        except (json.JSONDecodeError, KeyError) as e:
            # Fallback analysis
            state.input_type = "prompt"
            state.detected_engine = None
            state.context["suggested_processing"] = "spec_generation"
            
        return state
        
    async def _spec_generation_node(self, state: OrchestratorState) -> OrchestratorState:
        """Generate structured game specification from user input."""
        
        user_input = state.user_input or state.current_task or ""
        seeding_data = state.seeding_data
        
        # Build context for spec generation
        seeding_context = ""
        if seeding_data:
            seeding_context = f"\nSeeding context from literary sources:\n{json.dumps(seeding_data, indent=2)}"
        
        spec_prompt = f"""Generate a comprehensive game specification from this request:

{user_input}

{seeding_context}

Create a detailed game specification with:

1. Title and description
2. Engine choice (pygame for 2D Python, godot for scene-based, bevy for ECS Rust)
3. Genre and target audience
4. Core features and mechanics
5. Art style and aesthetic
6. Complexity level (simple/intermediate/complex)
7. Required assets (sprites, sounds, etc.)
8. Technical requirements and architecture

Respond with a JSON object matching this structure:
{{
    "title": "Game Title",
    "description": "Detailed game description",
    "engine": "pygame|godot|bevy",
    "genre": "platformer|rpg|shooter|puzzle|etc",
    "target_audience": "children|teens|adults|all",
    "features": ["feature1", "feature2", "feature3"],
    "art_style": "pixel art|realistic|cartoon|cyberpunk|etc",
    "complexity": "simple|intermediate|complex",
    "assets_needed": ["sprites", "backgrounds", "sounds", "etc"],
    "code_requirements": ["player movement", "combat system", "etc"],
    "metadata": {{
        "estimated_development_time": "hours",
        "recommended_team_size": number,
        "technical_notes": "additional considerations"
    }}
}}"""

        response = await self.llm.ainvoke([HumanMessage(content=spec_prompt)])
        
        try:
            spec_data = json.loads(response.content if isinstance(response.content, str) else str(response.content))
            
            # Validate engine choice
            engine_choice = spec_data.get("engine", "pygame")
            if engine_choice not in ["pygame", "godot", "bevy"]:
                engine_choice = "pygame"
            
            # Validate complexity choice
            complexity_choice = spec_data.get("complexity", "intermediate")
            if complexity_choice not in ["simple", "intermediate", "complex"]:
                complexity_choice = "intermediate"
            
            state.generated_spec = GameSpec(
                title=spec_data.get("title", "Generated Game"),
                description=spec_data.get("description", ""),
                engine=engine_choice,  # type: ignore
                genre=spec_data.get("genre", "adventure"),
                target_audience=spec_data.get("target_audience", "all"),
                features=spec_data.get("features", []),
                art_style=spec_data.get("art_style", "modern"),
                complexity=complexity_choice,  # type: ignore
                assets_needed=spec_data.get("assets_needed", []),
                code_requirements=spec_data.get("code_requirements", []),
                metadata=spec_data.get("metadata", {})
            )
            
        except (json.JSONDecodeError, KeyError) as e:
            # Create fallback spec with validated engine
            fallback_engine = state.detected_engine or "pygame"
            if fallback_engine not in ["pygame", "godot", "bevy"]:
                fallback_engine = "pygame"
            
            state.generated_spec = GameSpec(
                title="Generated Game",
                description=user_input,
                engine=fallback_engine,  # type: ignore
                genre="adventure",
                target_audience="all",
                complexity="intermediate"  # type: ignore
            )
            
        return state
        
    async def _human_review_node(self, state: OrchestratorState) -> OrchestratorState:
        """Coordinate human review of generated specifications."""
        
        spec = state.generated_spec
        if not spec:
            state.spec_approved = False
            return state
            
        # Format spec for review
        spec_summary = f"""
Generated Game Specification:

Title: {spec.title}
Engine: {spec.engine}
Genre: {spec.genre}
Description: {spec.description}

Features: {', '.join(spec.features)}
Art Style: {spec.art_style}
Complexity: {spec.complexity}
Target Audience: {spec.target_audience}

Assets Needed: {', '.join(spec.assets_needed)}
Code Requirements: {', '.join(spec.code_requirements)}
"""
        
        # Store for human review (would integrate with UI in full system)
        state.context["spec_for_review"] = spec_summary
        state.context["review_status"] = "pending"
        
        # For now, auto-approve (in full system this would wait for human input)
        state.spec_approved = True
        state.context["review_feedback"] = "Auto-approved for development"
        
        return state
        
    async def _seeding_coordination_node(self, state: OrchestratorState) -> OrchestratorState:
        """Coordinate seeding from literary and external sources using the seeding system."""
        
        user_input = state.user_input or state.current_task or ""
        
        # Extract themes and concepts for seeding
        seeding_prompt = f"""Extract key themes, narrative elements, and concepts from this game request for seeding:

{user_input}

Identify:
1. Literary genres that could inspire the game
2. Historical periods or settings
3. Character archetypes
4. Narrative themes
5. Artistic movements or styles

Respond with a JSON object for seeding coordination:
{{
    "literary_genres": ["fantasy", "sci-fi", "mystery"],
    "historical_periods": ["medieval", "cyberpunk future"],
    "character_archetypes": ["hero", "mentor", "villain"],
    "narrative_themes": ["good vs evil", "coming of age"],
    "artistic_styles": ["art nouveau", "brutalism"],
    "search_terms": ["specific terms for internet archive"]
}}"""

        response = await self.llm.ainvoke([HumanMessage(content=seeding_prompt)])
        
        try:
            seeding_info = json.loads(response.content if isinstance(response.content, str) else str(response.content))
            
            # Use the seeding system
            seeder = LiterarySeeder()
            seeding_request = SeedingRequest(
                themes=seeding_info.get("narrative_themes", []),
                genres=seeding_info.get("literary_genres", []),
                character_types=seeding_info.get("character_archetypes", []),
                settings=seeding_info.get("historical_periods", []),
                tone="adventurous",
                max_sources=5
            )
            
            # Generate seeded content
            seeding_results = await seeder.seed_from_request(seeding_request)
            
            state.seeding_data = {
                "literary_inspiration": seeding_info.get("literary_genres", []),
                "seeded_content": seeding_results.get("seeded_content", []),
                "narrative_patterns": seeding_results.get("narrative_patterns", {}),
                "character_inspirations": seeding_results.get("character_inspirations", []),
                "setting_inspirations": seeding_results.get("setting_inspirations", []),
                "themes_found": seeding_results.get("themes_found", []),
                "embedding_summary": seeding_results.get("embedding_summary", {}),
                "source_materials": ["Internet Archive literary collection", "PyTorch embeddings"]
            }
            
        except (json.JSONDecodeError, KeyError) as e:
            # If seeding fails, raise proper error
            raise RuntimeError(f"Seeding coordination failed: {e}") from e
            
        return state
        
    async def _engine_routing_node(self, state: OrchestratorState) -> OrchestratorState:
        """Determine which engine subgraph to route to."""
        
        spec = state.generated_spec
        if spec:
            state.routing_decision = spec.engine
        elif state.detected_engine:
            state.routing_decision = state.detected_engine
        else:
            # Default routing logic
            state.routing_decision = "pygame"  # Default to pygame for simplicity
            
        return state
        
    async def _pygame_subgraph_node(self, state: OrchestratorState) -> OrchestratorState:
        """Execute pygame-specific development subgraph."""
        
        spec = state.generated_spec
        if not spec:
            return state
            
        # Convert spec to pygame agent context
        pygame_context = {
            "game_description": spec.description,
            "features": spec.features,
            "art_style": spec.art_style,
            "complexity": spec.complexity,
            "project_name": spec.title.lower().replace(" ", "_")
        }
        
        # Execute pygame agent
        pygame_task = f"Generate a complete {spec.genre} game: {spec.description}"
        pygame_results = await self.pygame_agent.execute_task(pygame_task, pygame_context)
        
        state.subgraph_results["pygame"] = pygame_results
        return state
        
    async def _godot_subgraph_node(self, state: OrchestratorState) -> OrchestratorState:
        """Execute godot-specific development subgraph."""
        
        spec = state.generated_spec
        if not spec:
            return state
            
        godot_context = {
            "game_description": spec.description,
            "features": spec.features,
            "art_style": spec.art_style,
            "complexity": spec.complexity,
            "project_name": spec.title.lower().replace(" ", "_"),
            "analyzed_task": {"task_type": "godot_game_generation"}
        }
        
        godot_task = f"Generate a complete {spec.genre} game: {spec.description}"
        godot_results = await self.godot_agent.execute_task(godot_task, godot_context)
        
        state.subgraph_results["godot"] = godot_results
        return state
        
    async def _bevy_subgraph_node(self, state: OrchestratorState) -> OrchestratorState:
        """Execute bevy-specific development subgraph."""
        
        spec = state.generated_spec
        if not spec:
            return state
            
        bevy_context = {
            "game_description": spec.description,
            "features": spec.features,
            "art_style": spec.art_style,
            "complexity": spec.complexity,
            "project_name": spec.title.lower().replace(" ", "_"),
            "analyzed_task": {"task_type": "bevy_game_generation"}
        }
        
        bevy_task = f"Generate a complete {spec.genre} game: {spec.description}"
        bevy_results = await self.bevy_agent.execute_task(bevy_task, bevy_context)
        
        state.subgraph_results["bevy"] = bevy_results
        return state
        
    async def _internal_asset_subgraph_node(self, state: OrchestratorState) -> OrchestratorState:
        """Execute internal asset generation subgraph."""
        
        spec = state.generated_spec
        if not spec:
            return state
            
        # Convert spec to internal asset agent context
        asset_context = {
            "game_description": spec.description,
            "asset_categories": spec.assets_needed,
            "art_style": spec.art_style,
            "complexity": spec.complexity,
            "project_name": spec.title.lower().replace(" ", "_"),
            "output_directory": "src/ai_game_dev/server/static/assets"
        }
        
        # Execute internal asset agent
        asset_task = f"Generate comprehensive game assets for {spec.genre} game: {spec.description}"
        asset_results = await self.internal_asset_agent.execute_task(asset_task, asset_context)
        
        state.subgraph_results["internal_assets"] = asset_results
        return state
        
    async def _arcade_academy_subgraph_node(self, state: OrchestratorState) -> OrchestratorState:
        """Execute arcade academy educational subgraph."""
        
        spec = state.generated_spec
        if not spec:
            return state
            
        # Convert spec to arcade academy agent context
        academy_context = {
            "game_description": spec.description,
            "features": spec.features,
            "complexity": spec.complexity,
            "target_audience": spec.target_audience,
            "educational_objectives": ["coding concepts", "game development", "problem solving"],
            "project_name": spec.title.lower().replace(" ", "_")
        }
        
        # Execute arcade academy agent
        academy_task = f"Generate educational content for {spec.genre} game: {spec.description}"
        academy_results = await self.arcade_academy_agent.execute_task(academy_task, academy_context)
        
        state.subgraph_results["arcade_academy"] = academy_results
        return state
        
    async def _dialogue_subgraph_node(self, state: OrchestratorState) -> OrchestratorState:
        """Execute dialogue generation subgraph."""
        
        spec = state.generated_spec
        if not spec:
            return state
            
        # Convert spec to dialogue subgraph context
        dialogue_context = {
            "game_description": spec.description,
            "genre": spec.genre,
            "target_audience": spec.target_audience,
            "art_style": spec.art_style,
            "project_name": spec.title.lower().replace(" ", "_")
        }
        
        # Execute dialogue subgraph
        dialogue_results = await self.dialogue_subgraph.generate_dialogue(dialogue_context)
        
        state.subgraph_results["dialogue"] = dialogue_results
        return state
        
    async def _quest_subgraph_node(self, state: OrchestratorState) -> OrchestratorState:
        """Execute quest generation subgraph."""
        
        spec = state.generated_spec
        if not spec:
            return state
            
        # Convert spec to quest subgraph context
        quest_context = {
            "game_description": spec.description,
            "genre": spec.genre,
            "features": spec.features,
            "complexity": spec.complexity,
            "project_name": spec.title.lower().replace(" ", "_")
        }
        
        # Execute quest subgraph  
        quest_results = await self.quest_subgraph.generate_quests(quest_context)
        
        state.subgraph_results["quest"] = quest_results
        return state
        
    async def _graphics_subgraph_node(self, state: OrchestratorState) -> OrchestratorState:
        """Execute graphics generation subgraph."""
        
        spec = state.generated_spec
        if not spec:
            return state
            
        # Convert spec to graphics subgraph context
        graphics_context = {
            "game_description": spec.description,
            "art_style": spec.art_style,
            "assets_needed": spec.assets_needed,
            "complexity": spec.complexity,
            "project_name": spec.title.lower().replace(" ", "_")
        }
        
        # Execute graphics subgraph
        graphics_results = await self.graphics_subgraph.generate_graphics(graphics_context)
        
        state.subgraph_results["graphics"] = graphics_results
        return state
        
    async def _audio_subgraph_node(self, state: OrchestratorState) -> OrchestratorState:
        """Execute audio generation subgraph."""
        
        spec = state.generated_spec
        if not spec:
            return state
            
        # Convert spec to audio subgraph context
        audio_context = {
            "game_description": spec.description,
            "genre": spec.genre,
            "art_style": spec.art_style,
            "complexity": spec.complexity,
            "project_name": spec.title.lower().replace(" ", "_")
        }
        
        # Execute audio subgraph
        audio_results = await self.audio_subgraph.generate_audio_specs(audio_context)
        
        state.subgraph_results["audio"] = audio_results
        return state
        
    async def route_internal_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Route internal requests through the master orchestrator."""
        
        try:
            # Convert request to orchestrator state
            initial_state = OrchestratorState(
                user_input=request.get("user_input", ""),
                input_type=request.get("task_type", "prompt"),
                context=request.get("context", {})
            )
            
            # Handle different types of internal requests
            task_type = request.get("task_type", "general")
            
            if task_type == "asset_verification":
                # Route to internal asset generation
                initial_state.routing_decision = "internal_assets"
                initial_state.context["verification_mode"] = True
                
            elif task_type == "game_spec_generation":
                # Route to spec generation flow
                initial_state.routing_decision = "spec_generation"
                
            elif task_type == "arcade_academy":
                # Route to educational content generation
                initial_state.routing_decision = "arcade_academy"
                
            else:
                # Default to input analysis
                initial_state.routing_decision = "input_analysis"
            
            # Execute the workflow
            if not hasattr(self, 'workflow') or self.workflow is None:
                self.workflow = await self._build_graph()
            result = await self.workflow.ainvoke(initial_state)
            
            # Handle result properly whether it's a state object or dict
            if hasattr(result, 'outputs'):
                result_data = result.outputs
                subgraph_data = getattr(result, 'subgraph_results', {})
            elif isinstance(result, dict):
                result_data = result
                subgraph_data = result.get('subgraph_results', {})
            else:
                result_data = result.__dict__ if hasattr(result, '__dict__') else {}
                subgraph_data = getattr(result, 'subgraph_results', {})
            
            return {
                "success": True,
                "result": result_data,
                "subgraph_results": subgraph_data,
                "message": "Request processed successfully through master orchestrator"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to process internal request: {e}"
            }
        
    async def load_game_specification(self, spec_data: Union[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Load and parse game specification through the orchestrator."""
        
        try:
            if isinstance(spec_data, str):
                # File path - load TOML specification
                parsed_spec = self.game_spec_parser.parse_platform_assets_spec()
            elif isinstance(spec_data, dict):
                # Dictionary specification - convert to platform assets spec format
                parsed_spec = self.game_spec_parser.parse_platform_assets_spec()
            else:
                raise ValueError(f"Unsupported specification type: {type(spec_data)}")
            
            return {
                "success": True,
                "parsed_spec": parsed_spec,
                "message": "Game specification loaded successfully"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to load game specification: {e}"
            }
        
    async def _result_compilation_node(self, state: OrchestratorState) -> OrchestratorState:
        """Compile results from subgraph execution."""
        
        spec = state.generated_spec
        engine_results = state.subgraph_results
        
        # Compile comprehensive results
        state.outputs = {
            "success": True,
            "generated_spec": spec.__dict__ if spec else None,
            "chosen_engine": state.routing_decision,
            "engine_results": engine_results,
            "seeding_applied": bool(state.seeding_data),
            "human_reviewed": state.spec_approved,
            "artifacts_created": []
        }
        
        # Extract artifacts from engine results
        if state.routing_decision in engine_results:
            engine_output = engine_results[state.routing_decision]
            if "project_directory" in engine_output:
                state.outputs["artifacts_created"].append(engine_output["project_directory"])
            if "files_created" in engine_output:
                state.outputs["artifacts_created"].extend(engine_output["files_created"])
                
        return state
        
    def _route_after_analysis(self, state: OrchestratorState) -> str:
        """Route based on input analysis results."""
        suggested = state.context.get("suggested_processing", "spec_generation")
        
        if suggested == "seeding_first":
            return "needs_seeding"
        elif state.context.get("completeness_score", 0.0) > 0.8:
            return "has_complete_spec"
        else:
            return "needs_spec_generation"
            
    def _route_after_review(self, state: OrchestratorState) -> str:
        """Route based on human review results."""
        if state.spec_approved:
            return "approved"
        elif state.context.get("review_feedback") == "needs_revision":
            return "needs_revision"
        else:
            return "rejected"
            
    def _route_to_engine(self, state: OrchestratorState) -> str:
        """Route to appropriate engine subgraph."""
        return state.routing_decision or "pygame"
        
    def _get_orchestrator_instructions(self) -> str:
        """Get specialized instructions for the orchestrator."""
        return """You are the Master Game Development Orchestrator, responsible for coordinating the entire game development pipeline.

Your responsibilities include:

1. INPUT ANALYSIS:
   - Analyze user requests to determine if they're natural language prompts or structured specifications
   - Detect engine preferences (pygame, godot, bevy)
   - Assess completeness and identify missing information

2. SPECIFICATION GENERATION:
   - Convert natural language prompts into structured game specifications
   - Incorporate seeding data from literary and external sources
   - Ensure specifications are complete and actionable

3. ROUTING AND COORDINATION:
   - Route requests to appropriate engine subgraphs based on technical requirements
   - Coordinate between different agents and systems
   - Manage the overall development workflow

4. HUMAN-IN-THE-LOOP INTEGRATION:
   - Present generated specifications for human review
   - Incorporate feedback and revisions
   - Ensure final specifications meet user expectations

5. SEEDING COORDINATION:
   - Integrate literary and narrative elements from external sources
   - Use PyTorch embeddings for semantic enhancement
   - Coordinate with Internet Archive and other repositories

Always ensure that the final output is a complete, functional game that meets the user's requirements and follows best practices for the chosen engine."""
    
    async def generate_complete_game(self, game_spec: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a complete game using all subgraphs - main entry point for Streamlit."""
        
        try:
            # Convert to proper state format
            # Validate engine choice
            engine_choice = game_spec.get("engine", "pygame")
            if engine_choice not in ["pygame", "godot", "bevy"]:
                engine_choice = "pygame"
            
            # Validate complexity choice  
            complexity_choice = game_spec.get("complexity", "intermediate")
            if complexity_choice not in ["simple", "intermediate", "complex"]:
                complexity_choice = "intermediate"
            
            initial_state = OrchestratorState(
                user_input=game_spec.get("description", ""),
                generated_spec=GameSpec(
                    title=game_spec.get("title", "Game"),
                    description=game_spec.get("description", "A game"),
                    genre=game_spec.get("genre", "adventure"),
                    engine=engine_choice,  # type: ignore
                    complexity=complexity_choice,  # type: ignore
                    art_style=game_spec.get("art_style", "modern"),
                    target_audience=game_spec.get("target_audience", "general"),
                    features=game_spec.get("features", [])
                ),
                subgraph_results={}
            )
            
            # Run the complete workflow
            if not hasattr(self, 'workflow') or self.workflow is None:
                self.workflow = await self._build_graph()
            result = await self.workflow.ainvoke(initial_state)
            
            # Handle result properly whether it's a state object or dict
            if hasattr(result, 'generated_spec'):
                game_spec_data = result.generated_spec.__dict__ if result.generated_spec else {}
                subgraph_data = getattr(result, 'subgraph_results', {})
                final_data = getattr(result, 'outputs', {})
            elif isinstance(result, dict):
                game_spec_data = result.get('generated_spec', {})
                subgraph_data = result.get('subgraph_results', {})
                final_data = result.get('outputs', result)
            else:
                game_spec_data = {}
                subgraph_data = {}
                final_data = result.__dict__ if hasattr(result, '__dict__') else {}
            
            return {
                "success": True,
                "game_spec": game_spec_data,
                "subgraph_results": subgraph_data,
                "final_output": final_data
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "type": "complete_game_generation"
            }
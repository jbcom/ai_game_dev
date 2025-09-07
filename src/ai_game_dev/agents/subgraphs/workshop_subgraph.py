"""
Game Workshop Orchestration Subgraph
Routes game specifications to appropriate engine and asset subgraphs
"""
import asyncio
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from langgraph.graph import StateGraph, END
import json

from ai_game_dev.agents.base_agent import BaseAgent, AgentConfig
from ai_game_dev.agents.pygame_agent import PygameAgent
from ai_game_dev.agents.godot_agent import GodotAgent
from ai_game_dev.agents.bevy_agent import BevyAgent
from .dialogue_subgraph import DialogueSubgraph
from .quest_subgraph import QuestSubgraph
from .graphics_subgraph import GraphicsSubgraph
from .audio_subgraph import AudioSubgraph
from .game_spec_subgraph import GameSpecSubgraph


@dataclass
class WorkshopState:
    """State for game workshop orchestration."""
    # Input
    user_input: str = ""
    input_type: str = "description"  # "description" or "spec_upload"
    uploaded_spec: Optional[Dict[str, Any]] = None
    
    # Processing
    game_spec: Dict[str, Any] = field(default_factory=dict)
    engine: str = ""
    
    # Outputs
    generated_code: Dict[str, str] = field(default_factory=dict)
    generated_assets: Dict[str, List[Any]] = field(default_factory=dict)
    project_structure: Dict[str, Any] = field(default_factory=dict)
    
    # Status
    stage: str = "initializing"
    progress: float = 0.0
    errors: List[str] = field(default_factory=list)
    complete: bool = False


class GameWorkshopSubgraph(BaseAgent):
    """
    Master orchestrator for the Game Workshop.
    
    Workflow:
    1. Accept user description OR uploaded game spec
    2. Generate/validate game specification
    3. Route to appropriate engine subgraph for code generation
    4. Route in parallel to asset generation subgraphs
    5. Compile final project structure
    """
    
    def __init__(self):
        config = AgentConfig(
            model="gpt-4o",
            temperature=0.2,
            instructions=self._get_workshop_instructions()
        )
        super().__init__(config)
        
        # Initialize subgraphs
        self.spec_builder = GameSpecSubgraph()
        self.dialogue_subgraph = DialogueSubgraph()
        self.quest_subgraph = QuestSubgraph()
        self.graphics_subgraph = GraphicsSubgraph()
        self.audio_subgraph = AudioSubgraph()
        
        # Engine agents
        self.engine_agents = {
            "pygame": PygameAgent(),
            "godot": GodotAgent(),
            "bevy": BevyAgent()
        }
        
        self.graph = None
    
    def _get_workshop_instructions(self) -> str:
        return """You are the Game Workshop orchestrator responsible for coordinating
        the entire game development process.
        
        Your responsibilities:
        1. Process user input (descriptions or uploaded specs)
        2. Generate comprehensive game specifications
        3. Route to appropriate engine for code generation
        4. Coordinate parallel asset generation
        5. Compile the final project deliverable
        """
    
    async def initialize(self):
        """Initialize all subgraphs and build workflow."""
        await super().initialize()
        
        # Initialize all subgraphs
        await self.spec_builder.initialize()
        await self.dialogue_subgraph.initialize()
        await self.quest_subgraph.initialize()
        await self.graphics_subgraph.initialize()
        await self.audio_subgraph.initialize()
        
        # Initialize engine agents
        for agent in self.engine_agents.values():
            await agent.initialize()
        
        # Build the orchestration graph
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build the workshop orchestration workflow."""
        workflow = StateGraph(WorkshopState)
        
        # Add nodes
        workflow.add_node("process_input", self._process_input)
        workflow.add_node("build_spec", self._build_spec)
        workflow.add_node("validate_spec", self._validate_spec)
        workflow.add_node("generate_code", self._generate_code)
        workflow.add_node("generate_assets", self._generate_assets)
        workflow.add_node("compile_project", self._compile_project)
        
        # Add edges
        workflow.set_entry_point("process_input")
        
        # Conditional routing based on input type
        workflow.add_conditional_edges(
            "process_input",
            lambda x: "build_spec" if x.input_type == "description" else "validate_spec",
            {
                "build_spec": "build_spec",
                "validate_spec": "validate_spec"
            }
        )
        
        workflow.add_edge("build_spec", "validate_spec")
        
        # After validation, generate code and assets in parallel
        workflow.add_edge("validate_spec", "generate_code")
        workflow.add_edge("validate_spec", "generate_assets")
        
        # Both paths converge at compile
        workflow.add_edge("generate_code", "compile_project")
        workflow.add_edge("generate_assets", "compile_project")
        
        workflow.add_edge("compile_project", END)
        
        return workflow.compile()
    
    async def _process_input(self, state: WorkshopState) -> WorkshopState:
        """Process initial user input."""
        state.stage = "processing_input"
        state.progress = 0.1
        
        # Determine input type
        if state.uploaded_spec:
            state.input_type = "spec_upload"
            state.game_spec = state.uploaded_spec
        else:
            state.input_type = "description"
        
        return state
    
    async def _build_spec(self, state: WorkshopState) -> WorkshopState:
        """Build game specification from description."""
        state.stage = "building_specification"
        state.progress = 0.2
        
        # Use spec builder subgraph
        result = await self.spec_builder.process({
            "description": state.user_input,
            "engine": state.engine or "pygame"
        })
        
        if result["success"]:
            state.game_spec = result["spec"]
        else:
            state.errors.extend(result["errors"])
        
        return state
    
    async def _validate_spec(self, state: WorkshopState) -> WorkshopState:
        """Validate the game specification."""
        state.stage = "validating_specification"
        state.progress = 0.3
        
        spec = state.game_spec
        
        # Basic validation
        required_fields = ["title", "engine", "features"]
        for field in required_fields:
            if field not in spec:
                state.errors.append(f"Missing required field: {field}")
        
        # Set engine from spec
        state.engine = spec.get("engine", "pygame")
        
        # Validate engine
        if state.engine not in self.engine_agents:
            state.errors.append(f"Unsupported engine: {state.engine}")
        
        return state
    
    async def _generate_code(self, state: WorkshopState) -> WorkshopState:
        """Generate game code using appropriate engine agent."""
        state.stage = "generating_code"
        state.progress = 0.5
        
        if state.errors:
            return state
        
        # Get the appropriate engine agent
        engine_agent = self.engine_agents.get(state.engine)
        if not engine_agent:
            state.errors.append(f"Engine agent not found: {state.engine}")
            return state
        
        # Generate game code
        try:
            result = await engine_agent.generate_game(state.game_spec)
            state.generated_code = result.get("files", {})
            state.project_structure = result.get("structure", {})
        except Exception as e:
            state.errors.append(f"Code generation error: {str(e)}")
        
        return state
    
    async def _generate_assets(self, state: WorkshopState) -> WorkshopState:
        """Generate assets in parallel using subgraphs."""
        state.stage = "generating_assets"
        state.progress = 0.5
        
        if state.errors:
            return state
        
        spec = state.game_spec
        features = spec.get("features", [])
        
        # Prepare parallel asset generation tasks
        tasks = []
        
        # Always generate graphics
        tasks.append(self._generate_graphics(spec))
        
        # Generate audio
        tasks.append(self._generate_audio(spec))
        
        # Conditional generation based on features
        if "dialogue" in features or "story" in features:
            tasks.append(self._generate_dialogue(spec))
        
        if "rpg" in features or "quest" in features:
            tasks.append(self._generate_quests(spec))
        
        # Run all asset generation in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        state.generated_assets = {}
        asset_types = ["graphics", "audio", "dialogue", "quests"]
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                state.errors.append(f"Asset generation error ({asset_types[i]}): {str(result)}")
            elif result:
                state.generated_assets[asset_types[i]] = result
        
        return state
    
    async def _generate_graphics(self, spec: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate graphics assets."""
        assets_needed = spec.get("assets_needed", {}).get("sprites", [])
        backgrounds = spec.get("assets_needed", {}).get("backgrounds", [])
        
        graphics_tasks = []
        
        # Generate sprites
        for sprite_name in assets_needed[:5]:  # Limit to avoid overwhelming
            graphics_tasks.append({
                "task": "generate_sprite",
                "name": sprite_name,
                "style": spec.get("art_style", "modern"),
                "size": "64x64" if "pixel" in spec.get("art_style", "") else "128x128"
            })
        
        # Generate backgrounds
        for bg_name in backgrounds[:3]:
            graphics_tasks.append({
                "task": "generate_background",
                "name": bg_name,
                "style": spec.get("art_style", "modern"),
                "size": "1280x720"
            })
        
        # Process all graphics
        results = []
        for task in graphics_tasks:
            result = await self.graphics_subgraph.process(task)
            results.append(result)
        
        return results
    
    async def _generate_audio(self, spec: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate audio assets."""
        audio_specs = spec.get("audio_specs", {})
        sound_effects = audio_specs.get("sound_effects", [])
        
        audio_tasks = []
        
        # Generate music tracks
        track_count = audio_specs.get("music_tracks", 2)
        for i in range(min(track_count, 3)):  # Limit tracks
            audio_tasks.append({
                "task": "generate_music",
                "type": ["menu", "gameplay", "boss"][i],
                "genre": spec.get("genre", "arcade"),
                "duration": 120  # 2 minutes
            })
        
        # Generate sound effects
        for effect in sound_effects[:5]:  # Limit effects
            audio_tasks.append({
                "task": "generate_sound",
                "effect": effect,
                "duration": 0.5
            })
        
        # Process all audio
        results = []
        for task in audio_tasks:
            result = await self.audio_subgraph.process(task)
            results.append(result)
        
        return results
    
    async def _generate_dialogue(self, spec: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate dialogue content."""
        result = await self.dialogue_subgraph.process({
            "task": "generate_dialogue_tree",
            "context": spec,
            "characters": spec.get("characters", ["player", "npc"]),
            "style": spec.get("dialogue_style", "casual")
        })
        return [result]
    
    async def _generate_quests(self, spec: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate quest content."""
        result = await self.quest_subgraph.process({
            "task": "generate_quest_chain",
            "context": spec,
            "quest_count": min(spec.get("quest_count", 5), 10),
            "complexity": spec.get("complexity", "intermediate")
        })
        return [result]
    
    async def _compile_project(self, state: WorkshopState) -> WorkshopState:
        """Compile the final project structure."""
        state.stage = "compiling_project"
        state.progress = 0.9
        
        if state.errors:
            state.complete = False
            return state
        
        # Create final project structure
        project = {
            "metadata": {
                "title": state.game_spec.get("title"),
                "engine": state.engine,
                "created_with": "AI Game Workshop",
                "spec": state.game_spec
            },
            "code": state.generated_code,
            "assets": state.generated_assets,
            "structure": state.project_structure,
            "instructions": self._generate_instructions(state)
        }
        
        state.project_structure = project
        state.complete = True
        state.progress = 1.0
        
        return state
    
    def _generate_instructions(self, state: WorkshopState) -> Dict[str, str]:
        """Generate project setup and run instructions."""
        engine = state.engine
        
        instructions = {
            "pygame": {
                "setup": "pip install pygame",
                "run": "python main.py",
                "build": "pyinstaller --onefile main.py"
            },
            "godot": {
                "setup": "Open project.godot in Godot Engine",
                "run": "Press F5 in Godot Editor",
                "build": "Project > Export > Select Platform"
            },
            "bevy": {
                "setup": "cargo build",
                "run": "cargo run",
                "build": "cargo build --release"
            }
        }
        
        return instructions.get(engine, {})
    
    async def process(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Process workshop request."""
        # Create initial state
        initial_state = WorkshopState(
            user_input=inputs.get("description", ""),
            engine=inputs.get("engine", ""),
            uploaded_spec=inputs.get("uploaded_spec")
        )
        
        # Run the orchestration graph
        final_state = await self.graph.ainvoke(initial_state)
        
        return {
            "success": final_state.complete,
            "project": final_state.project_structure,
            "errors": final_state.errors,
            "progress": final_state.progress
        }
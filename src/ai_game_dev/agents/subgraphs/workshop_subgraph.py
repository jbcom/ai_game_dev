"""
Game Workshop Orchestration Subgraph
Routes game specifications to appropriate engine and asset subgraphs
"""
import asyncio
from typing import Any
from dataclasses import dataclass, field
from langgraph.graph import StateGraph, END
import json
from pathlib import Path
import os

from ai_game_dev.agents.base_agent import AgentConfig, BaseAgent
from .audio_subgraph import AudioSubgraph
from .bevy_subgraph import BevySubgraph
from .dialogue_subgraph import DialogueSubgraph
from .game_spec_subgraph import GameSpecSubgraph
from .godot_subgraph import GodotSubgraph
from .graphics_subgraph import GraphicsSubgraph
from .pygame_subgraph import PygameSubgraph
from .quest_subgraph import QuestSubgraph


@dataclass
class WorkshopState:
    """State for game workshop orchestration."""
    # Input
    user_input: str = ""
    input_type: str = "description"  # "description" or "spec_upload"
    uploaded_spec: dict[str, Any | None] = None
    
    # Processing
    game_spec: dict[str, Any] = field(default_factory=dict)
    engine: str = ""
    
    # Outputs
    generated_code: dict[str, str] = field(default_factory=dict)
    generated_assets: dict[str, list[Any]] = field(default_factory=dict)
    project_structure: dict[str, Any] = field(default_factory=dict)
    
    # Status
    stage: str = "initializing"
    progress: float = 0.0
    errors: list[str] = field(default_factory=list)
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
        
        # Engine subgraphs
        self.engine_subgraphs = {
            "pygame": PygameSubgraph(),
            "godot": GodotSubgraph(),
            "bevy": BevySubgraph()
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
        
        # Initialize engine subgraphs
        for subgraph in self.engine_subgraphs.values():
            await subgraph.initialize()
        
        # Build the orchestration graph
        self.graph = self._build_graph()
        
        # Determine workspace root
        self.workspace_root = self._find_workspace_root()
    
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
        if state.engine not in self.engine_subgraphs:
            state.errors.append(f"Unsupported engine: {state.engine}")
        
        return state
    
    async def _generate_code(self, state: WorkshopState) -> WorkshopState:
        """Generate game code using appropriate engine agent."""
        state.stage = "generating_code"
        state.progress = 0.5
        
        if state.errors:
            return state
        
        # Get the appropriate engine subgraph
        engine_subgraph = self.engine_subgraphs.get(state.engine)
        if not engine_subgraph:
            state.errors.append(f"Engine subgraph not found: {state.engine}")
            return state
        
        # Generate game code
        try:
            result = await engine_subgraph.process({"game_spec": state.game_spec})
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
    
    async def _generate_graphics(self, spec: dict[str, Any]) -> list[dict[str, Any]]:
        """Generate graphics assets."""
        assets_needed = spec.get("assets_needed", {}).get("sprites", [])
        backgrounds = spec.get("assets_needed", {}).get("backgrounds", [])
        
        graphics_tasks = []
        
        # Generate sprites
        for sprite_name in assets_needed[:5]:  # Limit to avoid overwhelming
            output_path = self._get_asset_path(spec, "sprites", f"{sprite_name}.png")
            graphics_tasks.append({
                "task": "generate_sprite",
                "name": sprite_name,
                "style": spec.get("art_style", "modern"),
                "size": "64x64" if "pixel" in spec.get("art_style", "") else "128x128",
                "output_path": str(output_path)
            })
        
        # Generate backgrounds
        for bg_name in backgrounds[:3]:
            output_path = self._get_asset_path(spec, "backgrounds", f"{bg_name}.png")
            graphics_tasks.append({
                "task": "generate_background",
                "name": bg_name,
                "style": spec.get("art_style", "modern"),
                "size": "1280x720",
                "output_path": str(output_path)
            })
        
        # Process all graphics
        results = []
        for task in graphics_tasks:
            # Ensure directory exists
            Path(task["output_path"]).parent.mkdir(parents=True, exist_ok=True)
            result = await self.graphics_subgraph.process(task)
            results.append(result)
        
        return results
    
    async def _generate_audio(self, spec: dict[str, Any]) -> list[dict[str, Any]]:
        """Generate audio assets."""
        audio_specs = spec.get("audio_specs", {})
        sound_effects = audio_specs.get("sound_effects", [])
        
        audio_tasks = []
        
        # Generate music tracks
        track_count = audio_specs.get("music_tracks", 2)
        track_types = ["menu", "gameplay", "boss"]
        for i in range(min(track_count, 3)):  # Limit tracks
            track_type = track_types[i]
            output_path = self._get_asset_path(spec, "audio/music", f"{track_type}.mp3")
            audio_tasks.append({
                "task": "generate_music",
                "type": track_type,
                "genre": spec.get("genre", "arcade"),
                "duration": 120,  # 2 minutes
                "output_path": str(output_path)
            })
        
        # Generate sound effects
        for effect in sound_effects[:5]:  # Limit effects
            output_path = self._get_asset_path(spec, "audio/effects", f"{effect}.wav")
            audio_tasks.append({
                "task": "generate_sound",
                "effect": effect,
                "duration": 0.5,
                "output_path": str(output_path)
            })
        
        # Process all audio
        results = []
        for task in audio_tasks:
            # Ensure directory exists
            Path(task["output_path"]).parent.mkdir(parents=True, exist_ok=True)
            result = await self.audio_subgraph.process(task)
            results.append(result)
        
        return results
    
    async def _generate_dialogue(self, spec: dict[str, Any]) -> list[dict[str, Any]]:
        """Generate dialogue content."""
        result = await self.dialogue_subgraph.process({
            "task": "generate_dialogue_tree",
            "context": spec,
            "characters": spec.get("characters", ["player", "npc"]),
            "style": spec.get("dialogue_style", "casual")
        })
        return [result]
    
    async def _generate_quests(self, spec: dict[str, Any]) -> list[dict[str, Any]]:
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
        
        # Get paths from spec
        code_path = self._get_code_path(state.game_spec)
        paths_config = state.game_spec.get("paths", {})
        
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
            "instructions": self._generate_instructions(state),
            "paths": {
                "code_root": str(code_path),
                "assets_root": str(self._resolve_path(paths_config.get("assets_base", ""), paths_config)),
                "project_name": paths_config.get("project_name", "unnamed_project"),
                "relative_to_repo": paths_config.get("use_relative_paths", True)
            }
        }
        
        state.project_structure = project
        state.complete = True
        state.progress = 1.0
        
        return state
    
    def _generate_instructions(self, state: WorkshopState) -> dict[str, str]:
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
    
    def _find_workspace_root(self) -> Path:
        """Find the workspace root directory."""
        # Look for pyproject.toml to identify root
        current = Path.cwd()
        while current != current.parent:
            if (current / "pyproject.toml").exists():
                return current
            current = current.parent
        return Path.cwd()  # Fallback to current directory
    
    def _resolve_path(self, path_spec: str, path_config: dict[str, Any]) -> Path:
        """Resolve a path based on specification configuration."""
        if path_config.get("use_relative_paths", True):
            # Relative to workspace root
            return self.workspace_root / path_spec
        else:
            # Absolute path
            return Path(path_spec)
    
    def _get_asset_path(self, spec: dict[str, Any], asset_type: str, asset_name: str) -> Path:
        """Get the full path for an asset based on spec configuration."""
        paths = spec.get("paths", {})
        assets_base = paths.get("assets_base", "public/static/assets/generated")
        project_name = paths.get("project_name", "unnamed_project")
        
        # Resolve base path
        base_path = self._resolve_path(assets_base, paths)
        
        # Create full asset path: base/project_name/asset_type/asset_name
        return base_path / project_name / asset_type / asset_name
    
    def _get_code_path(self, spec: dict[str, Any]) -> Path:
        """Get the base path for generated code."""
        paths = spec.get("paths", {})
        code_base = paths.get("code_base", "generated_games")
        project_name = paths.get("project_name", "unnamed_project")
        
        # Resolve base path
        base_path = self._resolve_path(code_base, paths)
        
        # Create full code path: base/project_name/
        return base_path / project_name
    
    async def process(self, inputs: dict[str, Any]) -> dict[str, Any]:
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
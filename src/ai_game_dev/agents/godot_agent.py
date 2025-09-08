"""
Godot Agent for Game Development
Specialized agent for Godot engine development with GDScript expertise
"""

from typing import Optional, Dict, Any
from pathlib import Path

from ai_game_dev.agents.base_agent import GameDevelopmentAgent, AgentConfig


class GodotAgent(GameDevelopmentAgent):
    """
    Godot-specific agent for game development using GDScript and Godot engine.
    
    Provides specialized capabilities for:
    - GDScript code generation with proper syntax and conventions
    - Scene and node structure creation
    - Resource management and autoloads
    - Signal system implementation
    - Godot-specific design patterns
    """
    
    def __init__(self, config: Optional[AgentConfig] = None):
        if config is None:
            config = AgentConfig(
                model="gpt-4o",
                temperature=0.3,
                instructions=self._get_godot_instructions()
            )
        super().__init__(config)
        
    async def _get_extended_instructions(self) -> str:
        """Add Godot-specific instructions."""
        return """
GODOT ENGINE EXPERTISE:

You are specialized in Godot game development using GDScript and the Godot engine.

Technical Requirements:
- Use GDScript syntax and conventions correctly
- Implement proper scene structure with nodes and components
- Handle Godot's signal system for event communication
- Use Godot's resource system for assets and data
- Implement proper scene transitions and game state management
- Follow Godot's node-based architecture patterns

GDScript Standards:
- Use snake_case for variables and functions
- Proper extends and class_name declarations
- Use @export for inspector-editable properties
- Implement _ready() and _process() methods correctly
- Handle input with _input() and _unhandled_input()
- Use proper signal connections and declarations

Godot Architecture:
- Scene-based design with proper node hierarchies
- Singleton pattern using autoloads for global managers
- Component-based entities using composition
- Proper use of PackedScenes and instantiation
- Resource loading and caching strategies
- Area2D/RigidBody2D for physics interactions

Project Structure:
- Organize scenes in logical folder structures
- Separate scripts, assets, and scenes appropriately
- Use proper naming conventions for files and directories
- Implement modular, reusable components
- Create proper project.godot configuration

Always generate complete, functional Godot projects with proper GDScript that follows Godot best practices and can be imported directly into Godot engine.
"""
        
    async def _setup_tools(self):
        """Set up Godot-specific tools."""
        await super()._setup_tools()
        
        # Add Godot-specific tools
        self.config.tools.extend([
            "gdscript_generation",
            "scene_structure_creation",
            "godot_project_setup",
            "resource_management",
            "signal_system_implementation"
        ])
        
    async def _tool_execution_node(self, state: Any) -> Any:
        """Execute Godot-specific tools."""
        
        context = state.context or {}
        task_type = context.get("analyzed_task", {}).get("task_type", "")
        
        if task_type == "godot_game_generation":
            await self._generate_godot_project(state)
        elif task_type == "gdscript_code_generation":
            await self._generate_gdscript_code(state)
        elif task_type == "godot_scene_creation":
            await self._generate_godot_scenes(state)
        else:
            # Fall back to base tool execution
            return await super()._tool_execution_node(state)
            
        return state
        
    async def _generate_godot_project(self, state: Any) -> None:
        """Generate a complete Godot project structure."""
        
        context = state.context or {}
        game_description = context.get("game_description", "2D platformer game")
        project_name = context.get("project_name", "godot_game")
        
        # Create project directory structure
        project_dir = Path(f"generated_projects/{project_name}")
        project_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate project.godot file
        project_config = await self._generate_project_config(game_description, project_name)
        (project_dir / "project.godot").write_text(project_config)
        
        # Generate main scene
        main_scene = await self._generate_main_scene_code(game_description)
        scenes_dir = project_dir / "scenes"
        scenes_dir.mkdir(exist_ok=True)
        (scenes_dir / "Main.tscn").write_text(main_scene)
        
        # Generate main script
        main_script = await self._generate_main_script(game_description)
        scripts_dir = project_dir / "scripts"
        scripts_dir.mkdir(exist_ok=True)
        (scripts_dir / "Main.gd").write_text(main_script)
        
        # Generate player script
        player_script = await self._generate_player_script(game_description)
        (scripts_dir / "Player.gd").write_text(player_script)
        
        # Update state with results
        state.outputs.update({
            "project_directory": str(project_dir),
            "files_created": [
                "project.godot",
                "scenes/Main.tscn", 
                "scripts/Main.gd",
                "scripts/Player.gd"
            ]
        })
        
    async def _generate_project_config(self, description: str, name: str) -> str:
        """Generate project.godot configuration file."""
        
        prompt = f"""Create a complete project.godot configuration file for a Godot game: {description}

Project name: {name}

Requirements:
- Proper Godot 4.x configuration format
- Main scene setup pointing to scenes/Main.tscn
- Input map for common game controls (movement, jump, action)
- Window settings for appropriate resolution
- Physics and rendering settings
- File and folder organization settings

Generate a production-ready project.godot file."""

        response = await self.llm.ainvoke([{"role": "user", "content": prompt}])
        return response.content
        
    async def _generate_main_scene_code(self, description: str) -> str:
        """Generate main scene structure."""
        
        prompt = f"""Create a complete Main.tscn scene file for a Godot game: {description}

Requirements:
- Proper Godot scene file format (.tscn)
- Node hierarchy appropriate for the game type
- Camera2D setup for 2D games or Camera3D for 3D
- UI layer for game interface
- Player spawn point and initial setup
- Background and environment nodes
- Proper node connections and groups

Generate a complete .tscn file that can be imported into Godot."""

        response = await self.llm.ainvoke([{"role": "user", "content": prompt}])
        return response.content
        
    async def _generate_main_script(self, description: str) -> str:
        """Generate main game script."""
        
        prompt = f"""Create a complete Main.gd script for a Godot game: {description}

Requirements:
- Proper GDScript syntax and structure
- Game state management (menu, playing, paused, game_over)
- Scene loading and transition handling
- Input processing and game controls
- UI updates and game progression
- Signal connections for game events
- Player spawning and management
- Game loop and update logic

Generate production-ready GDScript code with proper structure."""

        response = await self.llm.ainvoke([{"role": "user", "content": prompt}])
        return response.content
        
    async def _generate_player_script(self, description: str) -> str:
        """Generate player controller script."""
        
        prompt = f"""Create a complete Player.gd script for a Godot game: {description}

Requirements:
- Proper GDScript syntax for player controller
- Movement system (platformer, top-down, or appropriate for game type)
- Input handling with proper input map usage
- Physics integration (CharacterBody2D or RigidBody2D)
- Animation system integration
- Health and state management
- Collision detection and response
- Signal emissions for game events

Generate a complete, functional player controller in GDScript."""

        response = await self.llm.ainvoke([{"role": "user", "content": prompt}])
        return response.content
        
    async def _generate_gdscript_code(self, state: Any) -> None:
        """Generate specific GDScript code components."""
        
        context = state.context or {}
        code_type = context.get("code_type", "script")
        
        # Generate specific code based on type
        if code_type == "ui_script":
            code = await self._generate_ui_script(context.get("description", ""))
        elif code_type == "enemy_script":
            code = await self._generate_enemy_script(context.get("description", ""))
        elif code_type == "manager_script":
            code = await self._generate_manager_script(context.get("description", ""))
        else:
            code = await self._generate_generic_script(context.get("description", ""))
            
        state.outputs["generated_code"] = code
        
    async def _generate_ui_script(self, description: str) -> str:
        """Generate UI-specific GDScript."""
        
        prompt = f"""Create a GDScript for UI management: {description}

Requirements:
- Extends Control or CanvasLayer appropriately
- Proper UI node references and connections
- Button signal connections
- Menu transitions and animations
- Settings and options handling
- Game state integration
- Responsive design considerations

Generate clean, functional GDScript for UI."""

        response = await self.llm.ainvoke([{"role": "user", "content": prompt}])
        return response.content
        
    async def _generate_enemy_script(self, description: str) -> str:
        """Generate enemy AI GDScript."""
        
        prompt = f"""Create a GDScript for enemy AI: {description}

Requirements:
- Appropriate base class (CharacterBody2D, Area2D, etc.)
- AI state machine or behavior system
- Pathfinding and movement logic
- Combat and interaction systems
- Health and damage handling
- Animation integration
- Signal-based communication

Generate intelligent enemy AI in GDScript."""

        response = await self.llm.ainvoke([{"role": "user", "content": prompt}])
        return response.content
        
    async def _generate_manager_script(self, description: str) -> str:
        """Generate manager/singleton GDScript."""
        
        prompt = f"""Create a GDScript manager/singleton: {description}

Requirements:
- Singleton pattern using autoload
- Global state management
- Event system with signals
- Data persistence handling
- Cross-scene communication
- Resource management
- Performance considerations

Generate a robust manager script in GDScript."""

        response = await self.llm.ainvoke([{"role": "user", "content": prompt}])
        return response.content
        
    async def _generate_generic_script(self, description: str) -> str:
        """Generate general-purpose GDScript."""
        
        prompt = f"""Create a GDScript component: {description}

Requirements:
- Proper GDScript syntax and conventions
- Appropriate base class selection
- Clean, modular design
- Signal system integration
- Error handling and validation
- Performance optimization
- Documentation and comments

Generate professional GDScript code."""

        response = await self.llm.ainvoke([{"role": "user", "content": prompt}])
        return response.content
        
    async def _generate_godot_scenes(self, state: Any) -> None:
        """Generate Godot scene files."""
        
        context = state.context or {}
        scene_type = context.get("scene_type", "level")
        description = context.get("description", "game scene")
        
        scene_content = await self._generate_scene_file(scene_type, description)
        
        state.outputs.update({
            "scene_type": scene_type,
            "scene_content": scene_content
        })
        
    async def _generate_scene_file(self, scene_type: str, description: str) -> str:
        """Generate specific scene file content."""
        
        prompt = f"""Create a Godot .tscn scene file for {scene_type}: {description}

Requirements:
- Proper Godot scene file format
- Appropriate node hierarchy for {scene_type}
- Correct node types and properties
- Resource references and paths
- Signal connections where needed
- Groups and metadata setup
- Collision layers and physics setup

Generate a complete .tscn file for Godot."""

        response = await self.llm.ainvoke([{"role": "user", "content": prompt}])
        return response.content
        
    def _get_godot_instructions(self) -> str:
        """Get specialized instructions for Godot development."""
        return """You are an expert Godot game development agent specializing in GDScript and the Godot engine.

Your expertise includes:
- Complete Godot project structure and organization
- Production-ready GDScript with proper syntax and conventions
- Scene-based architecture with proper node hierarchies
- Signal system for event-driven programming
- Resource management and autoload singletons
- Physics integration and collision handling
- UI system and responsive design
- Animation and tweening systems
- Input handling and game controls

Always generate complete, functional Godot projects that can be imported directly into Godot engine and run without modification."""
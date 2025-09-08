"""
Bevy Agent for Game Development
Specialized agent for Bevy engine development with Rust expertise
"""

from typing import Optional, Dict, Any
from pathlib import Path

from ai_game_dev.agents.base_agent import GameDevelopmentAgent, AgentConfig


class BevyAgent(GameDevelopmentAgent):
    """
    Bevy-specific agent for game development using Rust and the Bevy engine.
    
    Provides specialized capabilities for:
    - Rust code generation with proper syntax and ownership
    - ECS (Entity Component System) architecture
    - Bevy systems and resources management
    - Asset loading and handling
    - Bevy-specific design patterns
    """
    
    def __init__(self, config: Optional[AgentConfig] = None):
        if config is None:
            config = AgentConfig(
                model="gpt-4o",
                temperature=0.3,
                instructions=self._get_bevy_instructions()
            )
        super().__init__(config)
        
    async def _get_extended_instructions(self) -> str:
        """Add Bevy-specific instructions."""
        return """
BEVY ENGINE EXPERTISE:

You are specialized in Bevy game development using Rust and the Bevy ECS engine.

Technical Requirements:
- Use Rust syntax with proper ownership and borrowing
- Implement ECS architecture with entities, components, and systems
- Handle Bevy's app builder pattern and plugin system
- Use Bevy's resource management and asset loading
- Implement proper game state management
- Follow Bevy's scheduling and system ordering

Rust/Bevy Standards:
- Use snake_case for functions and variables
- Use PascalCase for types and structs
- Proper derive macros for components and resources
- Use Bevy's prelude and common imports
- Handle Results and Options properly
- Implement proper error handling with ?

Bevy Architecture:
- Entity-Component-System design patterns
- Systems that operate on component queries
- Resources for global state and configuration
- Events for communication between systems
- Assets and asset loading strategies
- Proper plugin organization and modularity

Project Structure:
- Cargo.toml with proper Bevy dependencies
- Main.rs with app setup and plugin registration
- Modular system organization in separate files
- Component definitions with proper derives
- Resource structs for global state
- Event definitions for system communication

Performance Considerations:
- Efficient query patterns and system scheduling
- Proper use of ParallelIterator for performance
- Asset loading and caching strategies
- Memory management and entity cleanup

Always generate complete, functional Bevy projects with proper Rust code that compiles and runs with the latest Bevy version.
"""
        
    async def _setup_tools(self):
        """Set up Bevy-specific tools."""
        await super()._setup_tools()
        
        # Add Bevy-specific tools
        self.config.tools.extend([
            "rust_code_generation",
            "ecs_architecture_setup",
            "bevy_project_creation",
            "system_implementation",
            "component_design",
            "asset_pipeline_setup"
        ])
        
    async def _tool_execution_node(self, state: Any) -> Any:
        """Execute Bevy-specific tools."""
        
        context = state.context or {}
        task_type = context.get("analyzed_task", {}).get("task_type", "")
        
        if task_type == "bevy_game_generation":
            await self._generate_bevy_project(state)
        elif task_type == "rust_code_generation":
            await self._generate_rust_code(state)
        elif task_type == "ecs_system_creation":
            await self._generate_ecs_systems(state)
        else:
            # Fall back to base tool execution
            return await super()._tool_execution_node(state)
            
        return state
        
    async def _generate_bevy_project(self, state: Any) -> None:
        """Generate a complete Bevy project structure."""
        
        context = state.context or {}
        game_description = context.get("game_description", "2D space shooter game")
        project_name = context.get("project_name", "bevy_game")
        
        # Create project directory structure
        project_dir = Path(f"generated_projects/{project_name}")
        project_dir.mkdir(parents=True, exist_ok=True)
        src_dir = project_dir / "src"
        src_dir.mkdir(exist_ok=True)
        
        # Generate Cargo.toml
        cargo_toml = await self._generate_cargo_toml(game_description, project_name)
        (project_dir / "Cargo.toml").write_text(cargo_toml)
        
        # Generate main.rs
        main_rs = await self._generate_main_rs(game_description)
        (src_dir / "main.rs").write_text(main_rs)
        
        # Generate components.rs
        components_rs = await self._generate_components(game_description)
        (src_dir / "components.rs").write_text(components_rs)
        
        # Generate systems.rs
        systems_rs = await self._generate_systems(game_description)
        (src_dir / "systems.rs").write_text(systems_rs)
        
        # Generate resources.rs
        resources_rs = await self._generate_resources(game_description)
        (src_dir / "resources.rs").write_text(resources_rs)
        
        # Update state with results
        state.outputs.update({
            "project_directory": str(project_dir),
            "files_created": [
                "Cargo.toml",
                "src/main.rs",
                "src/components.rs",
                "src/systems.rs", 
                "src/resources.rs"
            ]
        })
        
    async def _generate_cargo_toml(self, description: str, name: str) -> str:
        """Generate Cargo.toml for Bevy project."""
        
        prompt = f"""Create a complete Cargo.toml file for a Bevy game: {description}

Project name: {name}

Requirements:
- Latest stable Bevy version as dependency
- Proper package metadata (name, version, edition)
- Essential Bevy features enabled
- Additional useful crates for game development
- Optimization settings for release builds
- Proper workspace configuration if needed

Generate a production-ready Cargo.toml for Bevy development."""

        response = await self.llm.ainvoke([{"role": "user", "content": prompt}])
        return response.content
        
    async def _generate_main_rs(self, description: str) -> str:
        """Generate main.rs for Bevy project."""
        
        prompt = f"""Create a complete main.rs file for a Bevy game: {description}

Requirements:
- Proper Bevy app setup with App::new()
- Default plugins and essential systems
- Custom plugin registration for game logic
- Window configuration and settings
- Game state management setup
- System scheduling and organization
- Proper imports and module declarations
- Resource initialization
- Startup systems for scene setup

Generate production-ready Rust code for Bevy main.rs."""

        response = await self.llm.ainvoke([{"role": "user", "content": prompt}])
        return response.content
        
    async def _generate_components(self, description: str) -> str:
        """Generate components.rs for the game."""
        
        prompt = f"""Create a complete components.rs file for a Bevy game: {description}

Requirements:
- Component structs with proper derives (Component, Debug, Clone)
- Game-specific components for entities
- Transform, physics, and rendering components
- UI and interaction components
- Health, inventory, and game state components
- Proper documentation and type safety
- Bundle structs for common entity patterns

Generate complete Bevy component definitions in Rust."""

        response = await self.llm.ainvoke([{"role": "user", "content": prompt}])
        return response.content
        
    async def _generate_systems(self, description: str) -> str:
        """Generate systems.rs for game logic."""
        
        prompt = f"""Create a complete systems.rs file for a Bevy game: {description}

Requirements:
- System functions with proper query parameters
- Movement, input, and physics systems
- Collision detection and response systems
- UI update and interaction systems
- Game state management systems
- Proper system scheduling and ordering
- Event handling and communication
- Resource access and modification

Generate efficient Bevy systems in Rust."""

        response = await self.llm.ainvoke([{"role": "user", "content": prompt}])
        return response.content
        
    async def _generate_resources(self, description: str) -> str:
        """Generate resources.rs for global state."""
        
        prompt = f"""Create a complete resources.rs file for a Bevy game: {description}

Requirements:
- Resource structs with proper derives (Resource, Debug, Default)
- Game configuration and settings resources
- Score, timer, and progression tracking
- Asset handles and loading state
- Input mapping and control configuration
- Global game state and flags
- Proper initialization and defaults

Generate complete Bevy resource definitions in Rust."""

        response = await self.llm.ainvoke([{"role": "user", "content": prompt}])
        return response.content
        
    async def _generate_rust_code(self, state: Any) -> None:
        """Generate specific Rust code components."""
        
        context = state.context or {}
        code_type = context.get("code_type", "system")
        
        # Generate specific code based on type
        if code_type == "plugin":
            code = await self._generate_plugin_code(context.get("description", ""))
        elif code_type == "component":
            code = await self._generate_component_code(context.get("description", ""))
        elif code_type == "resource":
            code = await self._generate_resource_code(context.get("description", ""))
        else:
            code = await self._generate_system_code(context.get("description", ""))
            
        state.outputs["generated_code"] = code
        
    async def _generate_plugin_code(self, description: str) -> str:
        """Generate Bevy plugin code."""
        
        prompt = f"""Create a Bevy plugin in Rust: {description}

Requirements:
- Implement Plugin trait properly
- Build method with app configuration
- System registration and scheduling
- Resource initialization
- Event setup and handling
- Proper module organization
- Configuration and customization options

Generate a complete, reusable Bevy plugin."""

        response = await self.llm.ainvoke([{"role": "user", "content": prompt}])
        return response.content
        
    async def _generate_component_code(self, description: str) -> str:
        """Generate Bevy component definitions."""
        
        prompt = f"""Create Bevy component structs: {description}

Requirements:
- Component derive macro
- Proper field types and documentation
- Default implementations where appropriate
- Related bundle structs if needed
- Type safety and validation
- Performance considerations

Generate robust Bevy components in Rust."""

        response = await self.llm.ainvoke([{"role": "user", "content": prompt}])
        return response.content
        
    async def _generate_resource_code(self, description: str) -> str:
        """Generate Bevy resource definitions."""
        
        prompt = f"""Create Bevy resource structs: {description}

Requirements:
- Resource derive macro
- Global state management
- Default trait implementation
- Thread safety considerations
- Proper initialization
- Update and access patterns

Generate efficient Bevy resources in Rust."""

        response = await self.llm.ainvoke([{"role": "user", "content": prompt}])
        return response.content
        
    async def _generate_system_code(self, description: str) -> str:
        """Generate Bevy system functions."""
        
        prompt = f"""Create Bevy system functions: {description}

Requirements:
- Proper query parameters and filters
- Resource access and modification
- Event reading and writing
- Command buffer usage for entity operations
- Efficient iteration and processing
- Error handling and validation
- System scheduling considerations

Generate optimized Bevy systems in Rust."""

        response = await self.llm.ainvoke([{"role": "user", "content": prompt}])
        return response.content
        
    async def _generate_ecs_systems(self, state: Any) -> None:
        """Generate ECS system architecture."""
        
        context = state.context or {}
        system_type = context.get("system_type", "gameplay")
        description = context.get("description", "game system")
        
        system_code = await self._generate_ecs_system(system_type, description)
        
        state.outputs.update({
            "system_type": system_type,
            "system_code": system_code
        })
        
    async def _generate_ecs_system(self, system_type: str, description: str) -> str:
        """Generate specific ECS system implementation."""
        
        prompt = f"""Create a Bevy ECS {system_type} system: {description}

Requirements:
- Efficient entity queries and component access
- Proper system parameters and filters
- Resource management and global state
- Event handling and communication
- Performance optimization techniques
- Proper error handling and edge cases
- Documentation and code clarity

Generate a complete ECS system in Rust for Bevy."""

        response = await self.llm.ainvoke([{"role": "user", "content": prompt}])
        return response.content
        
    def _get_bevy_instructions(self) -> str:
        """Get specialized instructions for Bevy development."""
        return """You are an expert Bevy game development agent specializing in Rust and the Bevy ECS engine.

Your expertise includes:
- Complete Bevy project structure with Cargo.toml and source organization
- Production-ready Rust code with proper ownership and borrowing
- Entity-Component-System architecture design
- Bevy's app builder pattern and plugin system
- Resource management and global state handling
- System scheduling and performance optimization
- Asset loading and pipeline management
- Event-driven architecture and communication

Always generate complete, functional Bevy projects that compile with the latest Rust and Bevy versions and run without modification."""
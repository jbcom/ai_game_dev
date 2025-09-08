"""
Bevy Engine Subgraph
Generates complete Bevy games with Rust and ECS
"""
from dataclasses import dataclass, field
from typing import Any

from langchain_core.messages import HumanMessage
from langgraph.graph import END, StateGraph

from ai_game_dev.agents.base_agent import AgentConfig, BaseAgent
from ai_game_dev.tools import variant_tool


@dataclass
class BevyState:
    """State for Bevy game generation."""
    game_spec: dict[str, Any] = field(default_factory=dict)
    generated_files: dict[str, str] = field(default_factory=dict)
    cargo_toml: str = ""
    main_file: str = ""
    components: list[str] = field(default_factory=list)
    systems: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    complete: bool = False


class BevySubgraph(BaseAgent):
    """
    Subgraph for generating Bevy games.
    
    Handles:
    - ECS architecture
    - Component and System generation
    - Resource management
    - Plugin creation
    - Asset loading
    """
    
    def __init__(self):
        config = AgentConfig(
            model="gpt-4o",
            temperature=0.2,
            instructions=self._get_bevy_instructions(),
            tools=["generate_variants"]  # Register variant tool
        )
        super().__init__(config)
        self.graph = None
    
    def _get_bevy_instructions(self) -> str:
        return """You are a Bevy game development expert specializing in Rust and ECS.
        
        Generate complete Bevy games with:
        1. Proper ECS architecture with Components, Systems, and Resources
        2. Idiomatic Rust code with proper error handling
        3. Efficient system ordering and stage management
        4. Asset loading and management
        5. Plugin-based architecture for modularity
        6. Educational comments explaining ECS concepts
        
        Follow Bevy best practices:
        - Use Queries for efficient entity access
        - Implement proper system sets and ordering
        - Handle resources and events appropriately
        - Use States for game flow management
        - Leverage Bevy's built-in plugins
        """
    
    async def initialize(self):
        """Initialize the Bevy subgraph."""
        await super().initialize()
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build the Bevy generation workflow."""
        workflow = StateGraph(BevyState)
        
        # Add nodes
        workflow.add_node("analyze_spec", self._analyze_spec)
        workflow.add_node("generate_cargo", self._generate_cargo)
        workflow.add_node("generate_main", self._generate_main)
        workflow.add_node("generate_components", self._generate_components)
        workflow.add_node("generate_systems", self._generate_systems)
        workflow.add_node("generate_plugins", self._generate_plugins)
        workflow.add_node("validate_code", self._validate_code)
        
        # Add edges
        workflow.set_entry_point("analyze_spec")
        workflow.add_edge("analyze_spec", "generate_cargo")
        workflow.add_edge("generate_cargo", "generate_main")
        workflow.add_edge("generate_main", "generate_components")
        workflow.add_edge("generate_components", "generate_systems")
        workflow.add_edge("generate_systems", "generate_plugins")
        workflow.add_edge("generate_plugins", "validate_code")
        workflow.add_edge("validate_code", END)
        
        return workflow.compile()
    
    async def _analyze_spec(self, state: BevyState) -> BevyState:
        """Analyze game specification for Bevy requirements."""
        spec = state.game_spec
        features = spec.get("features", [])
        
        # Determine required components and systems
        if "movement" in features or "player" in features:
            state.components.append("Player")
            state.systems.append("movement")
        
        if "enemies" in features:
            state.components.append("Enemy")
            state.systems.append("ai")
        
        if "physics" in features:
            state.systems.append("physics")
        
        if "ui" in features:
            state.systems.append("ui")
        
        return state
    
    async def _generate_cargo(self, state: BevyState) -> BevyState:
        """Generate Cargo.toml configuration."""
        spec = state.game_spec
        
        cargo_toml = f'''[package]
name = "{spec.get("title", "bevy-game").lower().replace(" ", "-")}"
version = "0.1.0"
edition = "2021"

[dependencies]
bevy = {{ version = "0.12", features = ["dynamic_linking"] }}
rand = "0.8"

# Enable optimizations for dependencies in debug mode
[profile.dev.package."*"]
opt-level = 3

# Enable optimizations for this crate in debug mode
[profile.dev]
opt-level = 1

# High optimizations for release
[profile.release]
opt-level = 3
lto = true
codegen-units = 1
'''
        
        state.cargo_toml = cargo_toml
        state.generated_files["Cargo.toml"] = cargo_toml
        
        return state
    
    async def _generate_main(self, state: BevyState) -> BevyState:
        """Generate main.rs file."""
        spec = state.game_spec
        
        main_rs = f'''//! {spec.get("title", "Bevy Game")}
//! {spec.get("description", "A game made with Bevy")}

use bevy::prelude::*;

mod components;
mod systems;
mod plugins;

use plugins::GamePlugin;

fn main() {{
    App::new()
        .add_plugins(DefaultPlugins.set(WindowPlugin {{
            primary_window: Some(Window {{
                title: "{spec.get("title", "Bevy Game")}".to_string(),
                resolution: (1280., 720.).into(),
                ..default()
            }}),
            ..default()
        }}))
        .add_plugins(GamePlugin)
        .run();
}}
'''
        
        state.main_file = "src/main.rs"
        state.generated_files["src/main.rs"] = main_rs
        
        return state
    
    async def _generate_components(self, state: BevyState) -> BevyState:
        """Generate ECS components."""
        # Check if we should generate movement variants
        if "movement" in str(state.game_spec.get("features", [])):
            # Use variant tool to generate movement options
            variant_result = variant_tool.invoke({
                "feature_type": "movement",
                "base_implementation": "basic movement",
                "variant_count": 2,
                "engine": "bevy",
                "educational_mode": True
            })
            
            # Store variant info for later use
            state.game_spec["movement_variants"] = variant_result.get("variants", [])
        
        components_rs = '''//! ECS Components

use bevy::prelude::*;

/// Player component
#[derive(Component)]
pub struct Player {
    pub speed: f32,
}

impl Default for Player {
    fn default() -> Self {
        Self { speed: 300.0 }
    }
}

/// Enemy component
#[derive(Component)]
pub struct Enemy {
    pub health: i32,
    pub damage: i32,
}

/// Health component
#[derive(Component)]
pub struct Health {
    pub current: i32,
    pub max: i32,
}

impl Health {
    pub fn new(max: i32) -> Self {
        Self { current: max, max }
    }
    
    pub fn take_damage(&mut self, amount: i32) {
        self.current = (self.current - amount).max(0);
    }
    
    pub fn is_dead(&self) -> bool {
        self.current <= 0
    }
}

/// Velocity component for movement
#[derive(Component, Default)]
pub struct Velocity(pub Vec3);

/// Grid position for grid-based movement
#[derive(Component)]
pub struct GridPosition {
    pub x: i32,
    pub y: i32,
}
'''
        
        state.generated_files["src/components.rs"] = components_rs
        
        return state
    
    async def _generate_systems(self, state: BevyState) -> BevyState:
        """Generate ECS systems."""
        # Base movement system
        movement_system = '''//! Game Systems

use bevy::prelude::*;
use crate::components::*;

/// Player movement system
pub fn player_movement_system(
    keyboard_input: Res<Input<KeyCode>>,
    mut query: Query<&mut Transform, With<Player>>,
    time: Res<Time>,
) {
    for mut transform in &mut query {
        let mut direction = Vec3::ZERO;
        
        // WASD or Arrow keys
        if keyboard_input.pressed(KeyCode::Left) || keyboard_input.pressed(KeyCode::A) {
            direction.x -= 1.0;
        }
        if keyboard_input.pressed(KeyCode::Right) || keyboard_input.pressed(KeyCode::D) {
            direction.x += 1.0;
        }
        if keyboard_input.pressed(KeyCode::Up) || keyboard_input.pressed(KeyCode::W) {
            direction.y += 1.0;
        }
        if keyboard_input.pressed(KeyCode::Down) || keyboard_input.pressed(KeyCode::S) {
            direction.y -= 1.0;
        }
        
        if direction.length() > 0.0 {
            direction = direction.normalize();
            transform.translation += direction * 300.0 * time.delta_seconds();
        }
    }
}

/// Spawn player system
pub fn spawn_player_system(
    mut commands: Commands,
    mut meshes: ResMut<Assets<Mesh>>,
    mut materials: ResMut<Assets<ColorMaterial>>,
) {
    commands.spawn((
        MaterialMesh2dBundle {
            mesh: meshes.add(shape::Circle::new(25.).into()).into(),
            material: materials.add(ColorMaterial::from(Color::LIME_GREEN)),
            transform: Transform::from_translation(Vec3::new(0., 0., 0.)),
            ..default()
        },
        Player::default(),
    ));
}

/// Camera setup system
pub fn setup_camera_system(mut commands: Commands) {
    commands.spawn(Camera2dBundle::default());
}
'''
        
        # Add movement variants if they exist
        if "movement_variants" in state.game_spec:
            movement_system += '''

// Movement variant implementations
#[allow(dead_code)]
pub mod movement_variants {
    use super::*;
    
    /// Grid-based movement system
    pub fn grid_movement_system(
        keyboard_input: Res<Input<KeyCode>>,
        mut query: Query<(&mut Transform, &mut GridPosition), With<Player>>,
    ) {
        const GRID_SIZE: f32 = 32.0;
        
        for (mut transform, mut grid_pos) in &mut query {
            if keyboard_input.just_pressed(KeyCode::Left) {
                grid_pos.x -= 1;
                transform.translation.x = grid_pos.x as f32 * GRID_SIZE;
            }
            if keyboard_input.just_pressed(KeyCode::Right) {
                grid_pos.x += 1;
                transform.translation.x = grid_pos.x as f32 * GRID_SIZE;
            }
            if keyboard_input.just_pressed(KeyCode::Up) {
                grid_pos.y += 1;
                transform.translation.y = grid_pos.y as f32 * GRID_SIZE;
            }
            if keyboard_input.just_pressed(KeyCode::Down) {
                grid_pos.y -= 1;
                transform.translation.y = grid_pos.y as f32 * GRID_SIZE;
            }
        }
    }
}
'''
        
        state.generated_files["src/systems.rs"] = movement_system
        
        return state
    
    async def _generate_plugins(self, state: BevyState) -> BevyState:
        """Generate game plugin."""
        plugin_rs = '''//! Game Plugin

use bevy::prelude::*;
use crate::systems::*;

/// Main game plugin
pub struct GamePlugin;

impl Plugin for GamePlugin {
    fn build(&self, app: &mut App) {
        app
            .add_systems(Startup, (setup_camera_system, spawn_player_system))
            .add_systems(Update, player_movement_system);
    }
}
'''
        
        state.generated_files["src/plugins.rs"] = plugin_rs
        
        # Add a simple README
        readme = f'''# {state.game_spec.get("title", "Bevy Game")}

{state.game_spec.get("description", "A game made with Bevy")}

## Running the game

```bash
cargo run
```

## Building for release

```bash
cargo build --release
```

## Controls

- WASD or Arrow Keys: Move player

## Architecture

This game uses Bevy's ECS (Entity Component System) architecture:
- **Components**: Data attached to entities (Player, Health, etc.)
- **Systems**: Functions that operate on components
- **Resources**: Global data shared between systems
'''
        
        state.generated_files["README.md"] = readme
        
        return state
    
    async def _validate_code(self, state: BevyState) -> BevyState:
        """Validate generated code."""
        # Check all required files exist
        required_files = [
            "Cargo.toml",
            "src/main.rs",
            "src/components.rs", 
            "src/systems.rs",
            "src/plugins.rs"
        ]
        
        for file in required_files:
            if file not in state.generated_files:
                state.errors.append(f"Missing required file: {file}")
        
        state.complete = len(state.errors) == 0
        
        return state
    
    async def process(self, inputs: dict[str, Any]) -> dict[str, Any]:
        """Process Bevy generation request."""
        initial_state = BevyState(
            game_spec=inputs.get("game_spec", inputs)
        )
        
        # Run the graph
        final_state = await self.graph.ainvoke(initial_state)
        
        return {
            "success": final_state.complete,
            "files": final_state.generated_files,
            "main_file": final_state.main_file,
            "errors": final_state.errors,
            "engine": "bevy"
        }
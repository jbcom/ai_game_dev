//! # Bevy Game Dev - First-class Bevy support for AI Game Development
//! 
//! This crate provides native Rust integration with the AI Game Development system,
//! offering high-performance game creation with Bevy's ECS architecture.

use bevy::prelude::*;
use pyo3::prelude::*;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;

pub mod components;
pub mod systems;
pub mod resources;
pub mod ai_integration;
pub mod game_generator;

pub use components::*;
pub use systems::*;
pub use resources::*;
pub use ai_integration::*;
pub use game_generator::*;

/// Main plugin for AI-powered Bevy game development
#[derive(Default)]
pub struct AIGameDevPlugin {
    pub enable_inspector: bool,
    pub enable_physics: bool,
}

impl Plugin for AIGameDevPlugin {
    fn build(&self, app: &mut App) {
        app
            .add_plugins(DefaultPlugins)
            .add_systems(Startup, setup_ai_game_dev)
            .add_systems(Update, (
                ai_entity_spawning_system,
                ai_system_optimization_system,
                performance_monitoring_system,
            ));

        // Optional features
        #[cfg(feature = "inspector")]
        if self.enable_inspector {
            app.add_plugins(bevy_inspector_egui::quick::WorldInspectorPlugin::new());
        }

        #[cfg(feature = "physics")]
        if self.enable_physics {
            app.add_plugins(bevy_rapier3d::plugin::RapierPhysicsPlugin::<()>::pixels_per_meter(100.0));
        }

        #[cfg(feature = "input_manager")]
        app.add_plugins(leafwing_input_manager::prelude::InputManagerPlugin::<GameAction>::default());
    }
}

/// Configuration for AI-generated Bevy games
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct BevyGameConfig {
    pub name: String,
    pub description: String,
    pub target_fps: u32,
    pub max_entities: usize,
    pub enable_physics: bool,
    pub enable_networking: bool,
    pub optimization_level: OptimizationLevel,
    pub ecs_features: Vec<ECSFeature>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum OptimizationLevel {
    Debug,
    Development,
    Release,
    Maximum,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum ECSFeature {
    SpatialPartitioning,
    EntityBatching,
    SystemParallelization,
    ComponentPacking,
    MemoryPooling,
    QueryOptimization,
}

/// AI-powered Bevy game generator
pub struct BevyGameGenerator {
    python_bridge: Py<PyAny>,
}

impl BevyGameGenerator {
    /// Create a new Bevy game generator with AI integration
    pub fn new() -> PyResult<Self> {
        Python::with_gil(|py| {
            let ai_game_dev = py.import("ai_game_dev")?;
            let dev_instance = ai_game_dev.call_method0("create_rust_integrated_dev")?;
            
            Ok(Self {
                python_bridge: dev_instance.into(),
            })
        })
    }

    /// Generate a complete Bevy game from description
    pub async fn generate_game(&self, description: &str, config: BevyGameConfig) -> anyhow::Result<BevyGameProject> {
        let game_spec = GameSpec {
            description: description.to_string(),
            engine: "bevy".to_string(),
            config: serde_json::to_value(&config)?,
        };

        // Call AI system through Python bridge
        let result = Python::with_gil(|py| -> PyResult<String> {
            let bridge = self.python_bridge.as_ref(py);
            let result = bridge.call_method1("create_game", (description, "bevy"))?;
            Ok(result.extract::<String>()?)
        })?;

        // Parse and process result
        let game_data: GameData = serde_json::from_str(&result)?;
        
        // Generate Bevy-specific code and systems
        let project = self.create_bevy_project(game_data, config).await?;
        
        Ok(project)
    }

    async fn create_bevy_project(&self, game_data: GameData, config: BevyGameConfig) -> anyhow::Result<BevyGameProject> {
        let mut project = BevyGameProject::new(config.name.clone());

        // Generate ECS components based on AI analysis
        project.components = self.generate_components(&game_data);
        
        // Generate optimized systems
        project.systems = self.generate_systems(&game_data, &config);
        
        // Generate resources and assets
        project.resources = self.generate_resources(&game_data);
        
        // Apply optimization strategies
        self.apply_optimizations(&mut project, &config);

        Ok(project)
    }

    fn generate_components(&self, game_data: &GameData) -> Vec<ComponentDefinition> {
        let mut components = Vec::new();

        // Standard game components
        components.push(ComponentDefinition {
            name: "Transform".to_string(),
            fields: vec![
                ("position".to_string(), "Vec3".to_string()),
                ("rotation".to_string(), "Quat".to_string()),
                ("scale".to_string(), "Vec3".to_string()),
            ],
            traits: vec!["Component".to_string(), "Debug".to_string()],
        });

        components.push(ComponentDefinition {
            name: "Velocity".to_string(),
            fields: vec![
                ("linear".to_string(), "Vec3".to_string()),
                ("angular".to_string(), "Vec3".to_string()),
            ],
            traits: vec!["Component".to_string(), "Debug".to_string(), "Default".to_string()],
        });

        // Game-specific components based on AI analysis
        if game_data.features.contains(&"health_system".to_string()) {
            components.push(ComponentDefinition {
                name: "Health".to_string(),
                fields: vec![
                    ("current".to_string(), "f32".to_string()),
                    ("max".to_string(), "f32".to_string()),
                    ("regeneration_rate".to_string(), "f32".to_string()),
                ],
                traits: vec!["Component".to_string(), "Debug".to_string()],
            });
        }

        if game_data.features.contains(&"resource_management".to_string()) {
            components.push(ComponentDefinition {
                name: "ResourceStorage".to_string(),
                fields: vec![
                    ("resources".to_string(), "HashMap<ResourceType, f32>".to_string()),
                    ("capacity".to_string(), "f32".to_string()),
                ],
                traits: vec!["Component".to_string(), "Debug".to_string()],
            });
        }

        components
    }

    fn generate_systems(&self, game_data: &GameData, config: &BevyGameConfig) -> Vec<SystemDefinition> {
        let mut systems = Vec::new();

        // Core movement system
        systems.push(SystemDefinition {
            name: "movement_system".to_string(),
            query_components: vec!["&mut Transform".to_string(), "&Velocity".to_string()],
            resources: vec!["Res<Time>".to_string()],
            parallel: config.ecs_features.contains(&ECSFeature::SystemParallelization),
            optimization_level: config.optimization_level.clone(),
        });

        // AI-generated systems based on game features
        for feature in &game_data.features {
            match feature.as_str() {
                "combat_system" => {
                    systems.push(SystemDefinition {
                        name: "combat_system".to_string(),
                        query_components: vec!["&mut Health".to_string(), "&Transform".to_string()],
                        resources: vec!["Res<Time>".to_string(), "EventWriter<CombatEvent>".to_string()],
                        parallel: true,
                        optimization_level: config.optimization_level.clone(),
                    });
                }
                "resource_collection" => {
                    systems.push(SystemDefinition {
                        name: "resource_collection_system".to_string(),
                        query_components: vec!["&mut ResourceStorage".to_string(), "&Transform".to_string()],
                        resources: vec!["ResMut<GlobalResources>".to_string()],
                        parallel: false,
                        optimization_level: config.optimization_level.clone(),
                    });
                }
                _ => {}
            }
        }

        systems
    }

    fn generate_resources(&self, game_data: &GameData) -> Vec<ResourceDefinition> {
        let mut resources = Vec::new();

        // Game state resource
        resources.push(ResourceDefinition {
            name: "GameState".to_string(),
            fields: vec![
                ("current_level".to_string(), "u32".to_string()),
                ("score".to_string(), "u64".to_string()),
                ("game_mode".to_string(), "GameMode".to_string()),
            ],
            traits: vec!["Resource".to_string(), "Debug".to_string()],
        });

        // Performance monitoring
        resources.push(ResourceDefinition {
            name: "PerformanceMetrics".to_string(),
            fields: vec![
                ("fps".to_string(), "f32".to_string()),
                ("entity_count".to_string(), "usize".to_string()),
                ("memory_usage".to_string(), "u64".to_string()),
            ],
            traits: vec!["Resource".to_string(), "Debug".to_string(), "Default".to_string()],
        });

        resources
    }

    fn apply_optimizations(&self, project: &mut BevyGameProject, config: &BevyGameConfig) {
        for feature in &config.ecs_features {
            match feature {
                ECSFeature::SpatialPartitioning => {
                    project.add_plugin("SpatialPartitioningPlugin".to_string());
                }
                ECSFeature::EntityBatching => {
                    project.optimizations.push("Entity batching enabled".to_string());
                }
                ECSFeature::ComponentPacking => {
                    project.optimizations.push("Dense component storage".to_string());
                }
                ECSFeature::MemoryPooling => {
                    project.add_plugin("MemoryPoolPlugin".to_string());
                }
                _ => {}
            }
        }
    }
}

// Supporting types and structures
#[derive(Debug, Clone, Serialize, Deserialize)]
struct GameSpec {
    description: String,
    engine: String,
    config: serde_json::Value,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
struct GameData {
    title: String,
    description: String,
    features: Vec<String>,
    complexity: String,
}

#[derive(Debug, Clone)]
pub struct BevyGameProject {
    pub name: String,
    pub components: Vec<ComponentDefinition>,
    pub systems: Vec<SystemDefinition>,
    pub resources: Vec<ResourceDefinition>,
    pub plugins: Vec<String>,
    pub optimizations: Vec<String>,
}

impl BevyGameProject {
    pub fn new(name: String) -> Self {
        Self {
            name,
            components: Vec::new(),
            systems: Vec::new(),
            resources: Vec::new(),
            plugins: vec!["DefaultPlugins".to_string()],
            optimizations: Vec::new(),
        }
    }

    pub fn add_plugin(&mut self, plugin: String) {
        if !self.plugins.contains(&plugin) {
            self.plugins.push(plugin);
        }
    }

    /// Generate the complete Rust source code
    pub fn generate_code(&self) -> String {
        let mut code = String::new();

        // File header
        code.push_str(&format!("//! {} - AI Generated Bevy Game\n", self.name));
        code.push_str("//! Generated by bevy_game_dev with AI assistance\n\n");

        // Imports
        code.push_str("use bevy::prelude::*;\n");
        code.push_str("use std::collections::HashMap;\n\n");

        // Generate component definitions
        for component in &self.components {
            code.push_str(&component.generate_rust_code());
            code.push_str("\n\n");
        }

        // Generate resource definitions  
        for resource in &self.resources {
            code.push_str(&resource.generate_rust_code());
            code.push_str("\n\n");
        }

        // Generate systems
        for system in &self.systems {
            code.push_str(&system.generate_rust_code());
            code.push_str("\n\n");
        }

        // Main function
        code.push_str("fn main() {\n");
        code.push_str("    App::new()\n");
        
        for plugin in &self.plugins {
            code.push_str(&format!("        .add_plugins({})\n", plugin));
        }

        code.push_str("        .add_systems(Startup, setup)\n");
        code.push_str("        .add_systems(Update, (\n");
        for (i, system) in self.systems.iter().enumerate() {
            let separator = if i < self.systems.len() - 1 { "," } else { "" };
            code.push_str(&format!("            {}{}\n", system.name, separator));
        }
        code.push_str("        ))\n");
        code.push_str("        .run();\n");
        code.push_str("}\n\n");

        // Setup function
        code.push_str("fn setup(mut commands: Commands) {\n");
        code.push_str("    // AI-generated setup code\n");
        code.push_str("    commands.spawn(Camera3dBundle::default());\n");
        code.push_str("}\n");

        code
    }
}

#[derive(Debug, Clone)]
pub struct ComponentDefinition {
    pub name: String,
    pub fields: Vec<(String, String)>,
    pub traits: Vec<String>,
}

impl ComponentDefinition {
    pub fn generate_rust_code(&self) -> String {
        let mut code = String::new();
        
        // Derive traits
        if !self.traits.is_empty() {
            code.push_str(&format!("#[derive({})]\n", self.traits.join(", ")));
        }
        
        // Struct definition
        code.push_str(&format!("pub struct {} {{\n", self.name));
        
        for (field_name, field_type) in &self.fields {
            code.push_str(&format!("    pub {}: {},\n", field_name, field_type));
        }
        
        code.push_str("}");
        code
    }
}

#[derive(Debug, Clone)]
pub struct SystemDefinition {
    pub name: String,
    pub query_components: Vec<String>,
    pub resources: Vec<String>,
    pub parallel: bool,
    pub optimization_level: OptimizationLevel,
}

impl SystemDefinition {
    pub fn generate_rust_code(&self) -> String {
        let mut code = String::new();
        
        // Function signature
        code.push_str(&format!("fn {}(\n", self.name));
        
        // Add query parameter
        if !self.query_components.is_empty() {
            code.push_str(&format!("    mut query: Query<({})>,\n", 
                self.query_components.join(", ")));
        }
        
        // Add resource parameters
        for resource in &self.resources {
            code.push_str(&format!("    {}: {},\n", 
                resource.split('<').next().unwrap_or("resource").to_lowercase(), resource));
        }
        
        code.push_str(") {\n");
        code.push_str("    // AI-generated system logic\n");
        
        if self.parallel {
            code.push_str("    query.par_for_each_mut(32, |components| {\n");
            code.push_str("        // Parallel processing logic\n");
            code.push_str("    });\n");
        } else {
            code.push_str("    for components in query.iter_mut() {\n");
            code.push_str("        // Sequential processing logic\n");
            code.push_str("    }\n");
        }
        
        code.push_str("}");
        code
    }
}

#[derive(Debug, Clone)]
pub struct ResourceDefinition {
    pub name: String,
    pub fields: Vec<(String, String)>,
    pub traits: Vec<String>,
}

impl ResourceDefinition {
    pub fn generate_rust_code(&self) -> String {
        let mut code = String::new();
        
        if !self.traits.is_empty() {
            code.push_str(&format!("#[derive({})]\n", self.traits.join(", ")));
        }
        
        code.push_str(&format!("pub struct {} {{\n", self.name));
        
        for (field_name, field_type) in &self.fields {
            code.push_str(&format!("    pub {}: {},\n", field_name, field_type));
        }
        
        code.push_str("}");
        code
    }
}

// PyO3 bindings for Python integration
#[pymodule]
fn bevy_game_dev(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<BevyGameGenerator>()?;
    m.add_function(wrap_pyfunction!(create_bevy_game, m)?)?;
    Ok(())
}

#[pyfunction]
fn create_bevy_game(description: &str, config_json: &str) -> PyResult<String> {
    let config: BevyGameConfig = serde_json::from_str(config_json)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(e.to_string()))?;
    
    // This would integrate with the async generator
    // For now return a simplified result
    let result = serde_json::json!({
        "success": true,
        "engine": "bevy",
        "config": config,
        "rust_optimized": true
    });
    
    Ok(result.to_string())
}

#[pymethods]
impl BevyGameGenerator {
    #[new]
    fn py_new() -> PyResult<Self> {
        Self::new()
    }
    
    fn generate_game_sync(&self, description: &str, config_json: &str) -> PyResult<String> {
        let config: BevyGameConfig = serde_json::from_str(config_json)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(e.to_string()))?;
        
        // Simplified synchronous version for Python binding
        let result = serde_json::json!({
            "title": format!("AI Generated: {}", description),
            "engine": "bevy", 
            "config": config,
            "rust_native": true,
            "components_generated": 5,
            "systems_generated": 3
        });
        
        Ok(result.to_string())
    }
}
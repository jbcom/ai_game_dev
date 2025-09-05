"""Bevy-specific asset and code generator with ECS optimizations."""

import asyncio
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

from openai import AsyncOpenAI
from jinja2 import Environment, FileSystemLoader

from openai_mcp_server.config import settings
from openai_mcp_server.logging_config import get_logger
from openai_mcp_server.utils import ensure_directory_exists
from openai_mcp_server.models import ImageSize, GenerationResult

logger = get_logger(__name__, component="bevy_generator")


@dataclass
class BevyComponent:
    """Bevy ECS component definition."""
    name: str
    fields: Dict[str, str]
    derives: List[str]
    description: str
    
    def to_rust_code(self) -> str:
        """Generate Rust code for the component."""
        derives_str = ", ".join(self.derives)
        fields_str = "\n    ".join(f"pub {name}: {type_}," for name, type_ in self.fields.items())
        
        return f'''#[derive({derives_str})]
pub struct {self.name} {{
    {fields_str}
}}'''


@dataclass 
class BevySystem:
    """Bevy system definition."""
    name: str
    query_params: List[str]
    resources: List[str]
    events: List[str]
    body: str
    
    def to_rust_code(self) -> str:
        """Generate Rust code for the system."""
        params = []
        if self.query_params:
            params.append(f"mut query: Query<{', '.join(self.query_params)}>")
        if self.resources:
            for resource in self.resources:
                params.append(f"{resource.lower()}: Res<{resource}>")
        if self.events:
            for event in self.events:
                params.append(f"mut {event.lower()}_events: EventWriter<{event}>")
        
        params_str = ",\n    ".join(params)
        
        return f'''pub fn {self.name}(
    {params_str}
) {{
    {self.body}
}}'''


class BevyGenerator:
    """Advanced Bevy game engine generator with ECS specialization."""
    
    def __init__(self, openai_client: AsyncOpenAI):
        self.client = openai_client
        self.templates_dir = settings.cache_dir / "templates" / "bevy"
        
    async def initialize(self):
        """Initialize the Bevy generator."""
        await ensure_directory_exists(self.templates_dir)
        
    async def generate_ecs_architecture(
        self,
        game_description: str,
        entities: List[str],
        project_context: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate complete ECS architecture for a Bevy game."""
        
        architecture_prompt = f"""
        Design a complete Bevy ECS architecture for this game:
        
        Game Description: {game_description}
        
        Entities: {', '.join(entities)}
        
        Create:
        1. Component definitions with appropriate Rust types
        2. System functions with proper Query parameters
        3. Resource definitions for global state
        4. Event definitions for communication
        5. Plugin structure for organization
        
        Focus on:
        - Rust best practices and ownership
        - Bevy ECS patterns and performance
        - Component composition over inheritance
        - System scheduling and dependencies
        - Resource management and lifecycle
        
        Return JSON with:
        {{
            "components": [{{
                "name": "ComponentName",
                "fields": {{"field_name": "Type"}},
                "derives": ["Component", "Debug"],
                "description": "What this component represents"
            }}],
            "systems": [{{
                "name": "system_name", 
                "query_params": ["&mut Transform", "&Velocity"],
                "resources": ["Time"],
                "events": ["CollisionEvent"],
                "description": "What this system does",
                "schedule": "Update"
            }}],
            "resources": [{{
                "name": "GameState",
                "fields": {{"score": "u32"}},
                "description": "Global game state"
            }}],
            "events": [{{
                "name": "PlayerDeathEvent",
                "fields": {{"player_id": "Entity"}},
                "description": "Fired when player dies"
            }}],
            "plugins": [{{
                "name": "GameplayPlugin",
                "systems": ["movement_system", "collision_system"],
                "description": "Core gameplay logic"
            }}]
        }}
        """
        
        response = await self.client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": architecture_prompt}],
            response_format={"type": "json_object"}
        )
        
        architecture = response.choices[0].message.content
        return await self._generate_bevy_code(architecture, project_context)
    
    async def _generate_bevy_code(
        self, 
        architecture_json: str, 
        project_context: Optional[str]
    ) -> Dict[str, Any]:
        """Generate complete Bevy Rust code from architecture."""
        
        import json
        arch = json.loads(architecture_json)
        
        # Generate components
        components_code = []
        for comp in arch.get("components", []):
            component = BevyComponent(
                name=comp["name"],
                fields=comp["fields"],
                derives=comp["derives"],
                description=comp["description"]
            )
            components_code.append(component.to_rust_code())
        
        # Generate systems
        systems_code = []
        for sys in arch.get("systems", []):
            # Generate system body based on description
            body = await self._generate_system_body(sys)
            system = BevySystem(
                name=sys["name"],
                query_params=sys.get("query_params", []),
                resources=sys.get("resources", []),
                events=sys.get("events", []),
                body=body
            )
            systems_code.append(system.to_rust_code())
        
        # Generate complete project structure
        project_structure = await self._generate_project_structure(
            arch, components_code, systems_code, project_context
        )
        
        return {
            "architecture": arch,
            "generated_code": {
                "components": components_code,
                "systems": systems_code,
                "project_files": project_structure
            },
            "bevy_optimized": True
        }
    
    async def _generate_system_body(self, system_def: Dict[str, Any]) -> str:
        """Generate Rust code body for a Bevy system."""
        
        body_prompt = f"""
        Generate Rust code body for this Bevy system:
        
        System: {system_def['name']}
        Description: {system_def['description']}
        Query Parameters: {system_def.get('query_params', [])}
        Resources: {system_def.get('resources', [])}
        Events: {system_def.get('events', [])}
        
        Generate idiomatic Rust code that:
        1. Iterates over query results properly
        2. Uses Bevy's component access patterns
        3. Handles resource reading/writing correctly  
        4. Sends events appropriately
        5. Follows Rust ownership and borrowing rules
        
        Return only the function body code (no function signature).
        """
        
        response = await self.client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": body_prompt}]
        )
        
        return response.choices[0].message.content.strip()
    
    async def _generate_project_structure(
        self,
        arch: Dict[str, Any],
        components: List[str],
        systems: List[str],
        project_context: Optional[str]
    ) -> Dict[str, str]:
        """Generate complete Bevy project file structure."""
        
        project_name = project_context or "bevy_game"
        
        files = {}
        
        # Main lib.rs
        files["src/lib.rs"] = f'''//! {project_name} - Generated Bevy game
use bevy::prelude::*;

mod components;
mod systems;
mod resources;
mod events;

use components::*;
use systems::*;
use resources::*;
use events::*;

pub struct GamePlugin;

impl Plugin for GamePlugin {{
    fn build(&self, app: &mut App) {{
        app
            // Add resources
            .init_resource::<GameState>()
            // Add events
            {self._generate_event_registrations(arch.get("events", []))}
            // Add systems
            {self._generate_system_registrations(arch.get("systems", []))}
            ;
    }}
}}

#[derive(Default, Resource)]
pub struct GameState {{
    pub score: u32,
    pub level: u32,
}}
'''
        
        # Components module
        files["src/components.rs"] = f'''//! Game components
use bevy::prelude::*;

{chr(10).join(components)}
'''
        
        # Systems module  
        files["src/systems.rs"] = f'''//! Game systems
use bevy::prelude::*;
use crate::components::*;
use crate::events::*;
use crate::resources::*;

{chr(10).join(systems)}
'''
        
        # Cargo.toml
        files["Cargo.toml"] = f'''[package]
name = "{project_name}"
version = "0.1.0"
edition = "2021"

[dependencies]
bevy = {{ version = "0.12", default-features = false, features = [
    "default",
    "wayland",
    "x11"
] }}
'''
        
        return files
    
    def _generate_event_registrations(self, events: List[Dict[str, Any]]) -> str:
        """Generate event registration code."""
        if not events:
            return ""
        
        registrations = []
        for event in events:
            registrations.append(f".add_event::<{event['name']}>()")
        
        return "\n            ".join(registrations)
    
    def _generate_system_registrations(self, systems: List[Dict[str, Any]]) -> str:
        """Generate system registration code."""
        if not systems:
            return ""
        
        by_schedule = {}
        for system in systems:
            schedule = system.get("schedule", "Update")
            if schedule not in by_schedule:
                by_schedule[schedule] = []
            by_schedule[schedule].append(system["name"])
        
        registrations = []
        for schedule, system_names in by_schedule.items():
            systems_str = ", ".join(system_names)
            registrations.append(f".add_systems({schedule}, ({systems_str}))")
        
        return "\n            ".join(registrations)
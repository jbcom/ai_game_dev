"""Bevy-specific LangGraph subgraph workflows."""

import json
from typing import Any, TypedDict
from datetime import datetime

from langchain_core.messages import HumanMessage, BaseMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END, START
from langgraph.prebuilt import ToolNode

from openai_mcp_server.config import settings
from openai_mcp_server.logging_config import get_logger
from openai_mcp_server.engines.bevy.generator import BevyGenerator
from openai_mcp_server.engines.bevy.assets import BevyAssetGenerator, BevyAssetSpec, BevyAssetType, BevyMaterialType

logger = get_logger(__name__, component="bevy_workflow")


class BevyWorkflowState(TypedDict):
    """State for Bevy-specific workflow."""
    messages: list[BaseMessage]
    game_description: str
    entities: list[str]
    assets_required: list[dict[str, Any]]
    generated_assets: list[dict[str, Any]]
    generated_code: dict[str, str]
    bevy_architecture: dict[str, Any]
    workflow_status: str


class BevyWorkflowGraph:
    """LangGraph subgraph for Bevy game engine workflows."""
    
    def __init__(self, openai_client, model_config: dict[str, Any] | None = None):
        self.client = openai_client
        
        # Use passed config or defaults
        config = model_config or {}
        self.llm = ChatOpenAI(
            model=config.get("model", "gpt-4o"),
            temperature=config.get("temperature", 0.7),
            api_key=config.get("api_key", self._get_api_key())
        )
        
        # Initialize Bevy-specific generators
        self.bevy_generator = BevyGenerator(openai_client)
        self.asset_generator = BevyAssetGenerator(openai_client)
        
        # Build the Bevy workflow graph
        self.graph = self._build_bevy_workflow()
    
    def _get_api_key(self) -> str:
        """Get OpenAI API key with proper handling."""
        if settings.openai_api_key:
            if hasattr(settings.openai_api_key, 'get_secret_value'):
                return settings.openai_api_key.get_secret_value()
            return str(settings.openai_api_key)
        return ""
    
    def _build_bevy_workflow(self) -> StateGraph:
        """Build the complete Bevy workflow subgraph."""
        workflow = StateGraph(BevyWorkflowState)
        
        # Add workflow nodes
        workflow.add_node("analyze_requirements", self._analyze_requirements_node)
        workflow.add_node("design_architecture", self._design_architecture_node)
        workflow.add_node("generate_assets", self._generate_assets_node)
        workflow.add_node("generate_code", self._generate_code_node)
        workflow.add_node("integrate_components", self._integrate_components_node)
        
        # Add workflow edges
        workflow.add_edge(START, "analyze_requirements")
        workflow.add_edge("analyze_requirements", "design_architecture")
        workflow.add_edge("design_architecture", "generate_assets")
        workflow.add_edge("generate_assets", "generate_code")
        workflow.add_edge("generate_code", "integrate_components")
        workflow.add_edge("integrate_components", END)
        
        return workflow.compile()
    
    async def _analyze_requirements_node(self, state: BevyWorkflowState) -> dict[str, Any]:
        """Analyze game requirements for Bevy-specific implementation."""
        game_description = state.get("game_description", "")
        
        analysis_prompt = f"""
        Analyze this game description for Bevy engine implementation:
        
        Game: {game_description}
        
        Identify:
        1. Required ECS entities and components
        2. Asset requirements (sprites, materials, audio)
        3. System requirements (movement, collision, rendering)
        4. Resource management needs
        5. Plugin architecture suggestions
        
        Return a JSON analysis focusing on Bevy-specific patterns.
        """
        
        messages = [HumanMessage(content=analysis_prompt)]
        response = await self.llm.ainvoke(messages)
        
        # Parse requirements from response
        try:
            requirements = self._extract_json_from_response(response.content)
            entities = requirements.get("entities", [])
            assets = requirements.get("assets", [])
        except:
            # Fallback parsing
            entities = ["Player", "Enemy", "Projectile", "Collectible"]
            assets = [
                {"type": "sprite", "name": "player_sprite", "description": "Main character sprite"},
                {"type": "tilemap", "name": "level_tilemap", "description": "Level environment tiles"}
            ]
        
        return {
            **state,
            "entities": entities,
            "assets_required": assets,
            "workflow_status": "requirements_analyzed",
            "messages": state.get("messages", []) + [response]
        }
    
    async def _design_architecture_node(self, state: BevyWorkflowState) -> dict[str, Any]:
        """Design Bevy ECS architecture."""
        game_description = state.get("game_description", "")
        entities = state.get("entities", [])
        
        # Use Bevy generator to create ECS architecture
        architecture = await self.bevy_generator.generate_ecs_architecture(
            game_description=game_description,
            entities=entities,
            project_context="bevy_game"
        )
        
        return {
            **state,
            "bevy_architecture": architecture,
            "workflow_status": "architecture_designed"
        }
    
    async def _generate_assets_node(self, state: BevyWorkflowState) -> dict[str, Any]:
        """Generate Bevy-compatible assets."""
        assets_required = state.get("assets_required", [])
        generated_assets = []
        
        for asset_req in assets_required:
            # Create Bevy asset specification
            asset_type = self._map_asset_type(asset_req.get("type", "sprite"))
            
            spec = BevyAssetSpec(
                asset_type=asset_type,
                name=asset_req.get("name", "default_asset"),
                description=asset_req.get("description", "Generated asset"),
                game_style="fantasy"
            )
            
            # Generate the asset
            try:
                result = await self.asset_generator.generate_bevy_asset(spec)
                generated_assets.append({
                    "spec": {
                        "asset_type": spec.asset_type.value,
                        "name": spec.name,
                        "description": spec.description
                    },
                    "result": {
                        "file_path": result.file_path,
                        "metadata": result.metadata
                    }
                })
            except Exception as e:
                logger.error(f"Asset generation failed: {e}")
                # Add placeholder for failed asset
                generated_assets.append({
                    "spec": asset_req,
                    "result": {"status": "failed", "error": str(e)}
                })
        
        return {
            **state,
            "generated_assets": generated_assets,
            "workflow_status": "assets_generated"
        }
    
    async def _generate_code_node(self, state: BevyWorkflowState) -> dict[str, Any]:
        """Generate Bevy Rust code."""
        architecture = state.get("bevy_architecture", {})
        
        # Extract generated code from architecture
        generated_code = architecture.get("generated_code", {})
        
        return {
            **state,
            "generated_code": generated_code,
            "workflow_status": "code_generated"
        }
    
    async def _integrate_components_node(self, state: BevyWorkflowState) -> dict[str, Any]:
        """Integrate assets and code into final Bevy project."""
        generated_assets = state.get("generated_assets", [])
        generated_code = state.get("generated_code", {})
        
        # Create integration manifest
        integration_manifest = {
            "project_type": "bevy_game",
            "assets": {
                asset["spec"]["name"]: asset["result"].get("file_path", "")
                for asset in generated_assets
                if asset["result"].get("status") != "failed"
            },
            "code_files": generated_code.get("project_files", {}),
            "bevy_version": "0.12",
            "ready_to_compile": True
        }
        
        return {
            **state,
            "workflow_status": "integration_complete",
            "integration_manifest": integration_manifest
        }
    
    def _map_asset_type(self, asset_type_str: str) -> BevyAssetType:
        """Map string asset type to Bevy enum."""
        asset_map = {
            "sprite": BevyAssetType.SPRITE_2D,
            "tilemap": BevyAssetType.TILEMAP,
            "ui": BevyAssetType.UI_ELEMENT,
            "particle": BevyAssetType.PARTICLE_TEXTURE,
            "material": BevyAssetType.NORMAL_MAP
        }
        return asset_map.get(asset_type_str, BevyAssetType.SPRITE_2D)
    
    def _extract_json_from_response(self, content: str) -> dict[str, Any]:
        """Extract JSON from LLM response."""
        try:
            # Try to find JSON block in response
            start = content.find('{')
            end = content.rfind('}') + 1
            if start != -1 and end != 0:
                json_str = content[start:end]
                return json.loads(json_str)
        except:
            pass
        return {}
    
    async def process_bevy_request(
        self,
        game_description: str,
        thread_id: str | None = None
    ) -> dict[str, Any]:
        """Process a complete Bevy game development request."""
        
        initial_state = {
            "messages": [HumanMessage(content=f"Create Bevy game: {game_description}")],
            "game_description": game_description,
            "entities": [],
            "assets_required": [],
            "generated_assets": [],
            "generated_code": {},
            "bevy_architecture": {},
            "workflow_status": "starting"
        }
        
        try:
            final_state = await self.graph.ainvoke(initial_state)
            
            return {
                "status": "success",
                "engine": "bevy",
                "game_description": game_description,
                "final_state": final_state,
                "thread_id": thread_id or f"bevy_{datetime.now().timestamp()}",
                "workflow_type": "bevy_subgraph"
            }
            
        except Exception as e:
            logger.error(f"Bevy workflow failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "engine": "bevy",
                "game_description": game_description
            }


async def create_bevy_subgraph(openai_client, model_config: dict[str, Any] | None = None) -> BevyWorkflowGraph:
    """Create and initialize Bevy workflow subgraph."""
    workflow = BevyWorkflowGraph(openai_client, model_config)
    await workflow.bevy_generator.initialize()
    await workflow.asset_generator.initialize()
    return workflow
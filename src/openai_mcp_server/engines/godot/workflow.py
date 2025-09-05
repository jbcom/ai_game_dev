"""Godot-specific LangGraph subgraph workflows."""

import json
from typing import Any, Dict, List, Optional, TypedDict
from datetime import datetime

from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, BaseMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END, START

from openai_mcp_server.config import settings
from openai_mcp_server.logging_config import get_logger

logger = get_logger(__name__, component="godot_workflow")


class GodotWorkflowState(TypedDict):
    """State for Godot-specific workflow."""
    messages: List[BaseMessage]
    game_description: str
    scenes_required: List[str]
    scripts_generated: Dict[str, str]
    assets_required: List[Dict[str, Any]]
    project_structure: Dict[str, Any]
    workflow_status: str


class GodotWorkflowGraph:
    """LangGraph subgraph for Godot game engine workflows."""
    
    def __init__(self, openai_client):
        self.client = openai_client
        self.llm = ChatOpenAI(
            model="gpt-4o",
            temperature=0.7,
            api_key=self._get_api_key()
        )
        
        # Build the Godot workflow graph
        self.graph = self._build_godot_workflow()
    
    def _get_api_key(self) -> str:
        """Get OpenAI API key with proper handling."""
        if settings.openai_api_key:
            if hasattr(settings.openai_api_key, 'get_secret_value'):
                return settings.openai_api_key.get_secret_value()
            return str(settings.openai_api_key)
        return ""
    
    def _build_godot_workflow(self) -> StateGraph:
        """Build the complete Godot workflow subgraph."""
        workflow = StateGraph(GodotWorkflowState)
        
        # Add workflow nodes
        workflow.add_node("analyze_scenes", self._analyze_scenes_node)
        workflow.add_node("generate_scripts", self._generate_scripts_node)
        workflow.add_node("create_project", self._create_project_node)
        
        # Add workflow edges
        workflow.add_edge(START, "analyze_scenes")
        workflow.add_edge("analyze_scenes", "generate_scripts")
        workflow.add_edge("generate_scripts", "create_project")
        workflow.add_edge("create_project", END)
        
        return workflow.compile()
    
    async def _analyze_scenes_node(self, state: GodotWorkflowState) -> Dict[str, Any]:
        """Analyze game for required Godot scenes."""
        game_description = state.get("game_description", "")
        
        analysis_prompt = f"""
        Analyze this game for Godot 4 scene structure:
        
        Game: {game_description}
        
        Identify required scenes and their hierarchy:
        1. Main scenes (Menu, Game, UI)
        2. Character scenes (Player, Enemies, NPCs)
        3. Environment scenes (Levels, Props)
        4. System scenes (HUD, Inventory, Dialog)
        
        Return JSON with scene names and their purposes.
        """
        
        messages = [HumanMessage(content=analysis_prompt)]
        response = await self.llm.ainvoke(messages)
        
        # Extract scenes from response
        try:
            analysis = self._extract_json_from_response(response.content)
            scenes = analysis.get("scenes", ["Main", "Player", "Enemy", "UI"])
        except:
            scenes = ["Main", "Player", "Enemy", "UI"]
        
        return {
            **state,
            "scenes_required": scenes,
            "workflow_status": "scenes_analyzed",
            "messages": state.get("messages", []) + [response]
        }
    
    async def _generate_scripts_node(self, state: GodotWorkflowState) -> Dict[str, Any]:
        """Generate GDScript files for scenes."""
        scenes = state.get("scenes_required", [])
        game_description = state.get("game_description", "")
        scripts_generated = {}
        
        for scene in scenes:
            script_prompt = f"""
            Generate GDScript for {scene} scene in this game:
            
            Game: {game_description}
            Scene: {scene}
            
            Create production-ready GDScript with:
            1. Proper class structure and extends
            2. _ready() and _process() functions
            3. Signal connections and input handling
            4. Comments explaining functionality
            5. Godot 4 best practices
            
            Return only the GDScript code.
            """
            
            messages = [HumanMessage(content=script_prompt)]
            response = await self.llm.ainvoke(messages)
            
            scripts_generated[f"{scene}.gd"] = response.content.strip()
        
        return {
            **state,
            "scripts_generated": scripts_generated,
            "workflow_status": "scripts_generated"
        }
    
    async def _create_project_node(self, state: GodotWorkflowState) -> Dict[str, Any]:
        """Create complete Godot project structure."""
        scripts = state.get("scripts_generated", {})
        game_description = state.get("game_description", "")
        
        # Create project.godot file content
        project_godot = f'''[application]

config/name="{game_description}"
run/main_scene="res://Main.tscn"

[rendering]

renderer/rendering_method="mobile"
textures/vram_compression/import_etc2_astc=true
'''
        
        project_structure = {
            "project.godot": project_godot,
            "scripts/": scripts,
            "scenes/": {scene: f"{scene}.tscn template" for scene in state.get("scenes_required", [])},
            "assets/": {
                "images/": "Image assets directory",
                "audio/": "Audio assets directory",
                "fonts/": "Font assets directory"
            }
        }
        
        return {
            **state,
            "project_structure": project_structure,
            "workflow_status": "project_created"
        }
    
    def _extract_json_from_response(self, content: str) -> Dict[str, Any]:
        """Extract JSON from LLM response."""
        try:
            start = content.find('{')
            end = content.rfind('}') + 1
            if start != -1 and end != 0:
                json_str = content[start:end]
                return json.loads(json_str)
        except:
            pass
        return {}
    
    async def process_godot_request(
        self,
        game_description: str,
        thread_id: str = None
    ) -> Dict[str, Any]:
        """Process a complete Godot game development request."""
        
        initial_state = {
            "messages": [HumanMessage(content=f"Create Godot game: {game_description}")],
            "game_description": game_description,
            "scenes_required": [],
            "scripts_generated": {},
            "assets_required": [],
            "project_structure": {},
            "workflow_status": "starting"
        }
        
        try:
            final_state = await self.graph.ainvoke(initial_state)
            
            return {
                "status": "success",
                "engine": "godot",
                "game_description": game_description,
                "final_state": final_state,
                "thread_id": thread_id or f"godot_{datetime.now().timestamp()}",
                "workflow_type": "godot_subgraph"
            }
            
        except Exception as e:
            logger.error(f"Godot workflow failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "engine": "godot",
                "game_description": game_description
            }


async def create_godot_subgraph(openai_client) -> GodotWorkflowGraph:
    """Create and initialize Godot workflow subgraph."""
    return GodotWorkflowGraph(openai_client)
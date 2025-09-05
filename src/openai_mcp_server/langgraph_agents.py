"""LangGraph-based agent system with simplified SQLite state management."""

import json
import sqlite3
from pathlib import Path
from typing import Any, TypedDict
from datetime import datetime

from langchain_core.messages import HumanMessage, BaseMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END, START
from langgraph.prebuilt import ToolNode
try:
    from langgraph.checkpoint.sqlite import SqliteSaver
except ImportError:
    try:
        from langgraph_checkpoint.sqlite import SqliteSaver  
    except ImportError:
        # Fallback - create a simple state manager without checkpointing
        SqliteSaver = None

from openai_mcp_server.langchain_tools import get_langchain_tools
from openai_mcp_server.config import settings
from openai_mcp_server.logging_config import get_logger
from openai_mcp_server.engines.bevy.workflow import create_bevy_subgraph
from openai_mcp_server.engines.godot.workflow import create_godot_subgraph

logger = get_logger(__name__, component="langgraph_agents")


class GameDevState(TypedDict):
    """State for game development agent workflow."""
    messages: list[BaseMessage]
    project_context: str
    current_task: str
    target_engine: str | None
    generated_assets: list[dict[str, Any]]
    subgraph_results: dict[str, Any]
    workflow_status: str
    game_description: str
    engine_analysis: str


class GameDevelopmentAgent:
    """LangGraph-based game development agent with persistent state."""
    
    def __init__(self, model: str = "gpt-5"):
        self.model = model
        api_key = ""
        if settings.openai_api_key:
            if hasattr(settings.openai_api_key, 'get_secret_value'):
                api_key = settings.openai_api_key.get_secret_value()
            else:
                api_key = str(settings.openai_api_key)
        
        self.llm = ChatOpenAI(
            model=model,
            temperature=0.7,
            api_key=api_key
        )
        
        # Initialize tools
        self.tools = get_langchain_tools()
        self.tool_node = ToolNode(self.tools)
        
        # Store model config for subgraphs
        self.model_config = {
            "model": model,
            "temperature": 0.7,
            "api_key": api_key
        }
        
        # Initialize engine subgraphs
        self.subgraphs = {}
        self._initialize_subgraphs_task = None
        
        # Set up SQLite checkpointer if available
        self.db_path = settings.cache_dir / "langgraph_state.db"
        if SqliteSaver:
            self.checkpointer = SqliteSaver.from_conn_string(str(self.db_path))
        else:
            self.checkpointer = None
        
        # Build the graph
        self.graph = self._build_graph()
    
    async def _initialize_subgraphs(self):
        """Initialize engine-specific subgraphs."""
        if not self.subgraphs:
            try:
                from openai import AsyncOpenAI
                client = AsyncOpenAI(api_key=self.model_config["api_key"])
                
                # Pass model config to subgraphs
                self.subgraphs["bevy"] = await create_bevy_subgraph(client, self.model_config)
                self.subgraphs["godot"] = await create_godot_subgraph(client, self.model_config)
                logger.info("Initialized engine subgraphs: bevy, godot")
            except Exception as e:
                logger.error(f"Failed to initialize subgraphs: {e}")
                self.subgraphs = {}
    
    def _build_graph(self) -> StateGraph:
        """Build the main LangGraph workflow following best practices."""
        
        workflow = StateGraph(GameDevState)
        
        # Add nodes following LangGraph patterns
        workflow.add_node("analyze_request", self._analyze_request_node)
        workflow.add_node("route_engine", self._route_engine_node) 
        workflow.add_node("bevy_workflow", self._bevy_workflow_node)
        workflow.add_node("godot_workflow", self._godot_workflow_node)
        workflow.add_node("tools", self.tool_node)
        
        # Set entry point
        workflow.set_entry_point("analyze_request")
        
        # Add edges following tutorial patterns
        workflow.add_conditional_edges(
            "analyze_request",
            self._determine_next_step,
            {
                "route_engine": "route_engine",
                "use_tools": "tools",
                "end": END
            }
        )
        
        workflow.add_conditional_edges(
            "route_engine", 
            self._select_engine,
            {
                "bevy": "bevy_workflow",
                "godot": "godot_workflow",
                "end": END
            }
        )
        
        workflow.add_edge("bevy_workflow", END)
        workflow.add_edge("godot_workflow", END)
        workflow.add_edge("tools", "analyze_request")
        
        if self.checkpointer:
            return workflow.compile(checkpointer=self.checkpointer)
        else:
            return workflow.compile()
    
    def _analyze_request_node(self, state: GameDevState) -> GameDevState:
        """Analyze the game development request."""
        current_task = state.get("current_task", "")
        messages = state.get("messages", [])
        
        # Create analysis prompt
        analysis_prompt = f"""
        Analyze this game development request:
        
        Request: {current_task}
        
        Determine:
        1. What type of game is being requested?
        2. What game engine would be most suitable?
        3. What specific features are needed?
        
        Provide a brief analysis focusing on engine selection.
        """
        
        response = self.llm.invoke([HumanMessage(content=analysis_prompt)])
        
        # Update state following LangGraph patterns
        return {
            **state,
            "messages": messages + [response],
            "engine_analysis": response.content,
            "workflow_status": "analyzed"
        }
    
    def _determine_next_step(self, state: GameDevState) -> str:
        """Determine next step following LangGraph patterns."""
        messages = state.get("messages", [])
        last_message = messages[-1] if messages else None
        current_task = state.get("current_task", "").lower()
        
        # Check for tool calls first
        if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
            return "use_tools"
        
        # Check if we need engine routing
        if any(engine in current_task for engine in ["bevy", "godot", "game", "create"]):
            return "route_engine"
        
        return "end"
    
    def _select_engine(self, state: GameDevState) -> str:
        """Select engine based on analysis following tutorial patterns."""
        engine_analysis = state.get("engine_analysis", "").lower()
        current_task = state.get("current_task", "").lower()
        target_engine = state.get("target_engine", "").lower()
        
        # Priority routing based on explicit mentions
        if "bevy" in current_task or "bevy" in engine_analysis or target_engine == "bevy":
            return "bevy"
        elif "godot" in current_task or "godot" in engine_analysis or target_engine == "godot":
            return "godot"
        elif "rust" in current_task or "ecs" in current_task:
            return "bevy"  # Bevy uses Rust and ECS
        elif "gdscript" in current_task or "scene" in current_task:
            return "godot"  # Godot uses GDScript and scenes
        
        # Default to Bevy for new projects
        return "bevy"
    
    def _route_engine_node(self, state: GameDevState) -> GameDevState:
        """Router node to determine target engine."""
        current_task = state.get("current_task", "")
        
        # Analyze task to determine best engine
        analysis_prompt = f"""
        Analyze this game development task to determine the best engine:
        
        Task: {current_task}
        
        Available engines: Bevy (Rust, ECS), Godot (GDScript, Scene-based)
        
        Which engine is most suitable? Return just the engine name: "bevy" or "godot"
        """
        
        response = self.llm.invoke([HumanMessage(content=analysis_prompt)])
        target_engine = response.content.strip().lower()
        
        if target_engine not in ["bevy", "godot"]:
            target_engine = "bevy"  # Default fallback
        
        return {
            **state,
            "target_engine": target_engine,
            "workflow_status": f"routed_to_{target_engine}"
        }
    
    async def _bevy_workflow_node(self, state: GameDevState) -> GameDevState:
        """Handle Bevy-specific processing using composed subgraph."""
        await self._ensure_subgraphs_initialized()
        
        if "bevy" not in self.subgraphs:
            return {
                **state,
                "subgraph_results": {"error": "Bevy subgraph not available"},
                "workflow_status": "subgraph_error"
            }
        
        current_task = state.get("current_task", "")
        bevy_workflow = self.subgraphs["bevy"]
        
        # Execute Bevy subgraph workflow directly
        result = await bevy_workflow.process_bevy_request(current_task)
        
        return {
            **state,
            "subgraph_results": result,
            "workflow_status": "bevy_complete"
        }
    
    async def _godot_workflow_node(self, state: GameDevState) -> GameDevState:
        """Handle Godot-specific processing using composed subgraph."""
        await self._ensure_subgraphs_initialized()
        
        if "godot" not in self.subgraphs:
            return {
                **state,
                "subgraph_results": {"error": "Godot subgraph not available"},
                "workflow_status": "subgraph_error"
            }
        
        current_task = state.get("current_task", "")
        godot_workflow = self.subgraphs["godot"]
        
        # Execute Godot subgraph workflow directly  
        result = await godot_workflow.process_godot_request(current_task)
        
        return {
            **state,
            "subgraph_results": result,
            "workflow_status": "godot_complete"
        }
    
    async def _ensure_subgraphs_initialized(self):
        """Ensure subgraphs are initialized."""
        if not self._initialize_subgraphs_task:
            self._initialize_subgraphs_task = asyncio.create_task(self._initialize_subgraphs())
        await self._initialize_subgraphs_task
    
    async def process_request(
        self,
        request: str,
        project_context: str = "new_project",
        thread_id: str = None
    ) -> dict[str, Any]:
        """Process a game development request."""
        
        initial_state = {
            "messages": [HumanMessage(content=request)],
            "project_context": project_context,
            "current_task": request,
            "generated_assets": [],
            "workflow_status": "starting"
        }
        
        config = {
            "configurable": {
                "thread_id": thread_id or f"thread_{datetime.now().timestamp()}"
            }
        }
        
        try:
            final_state = await self.graph.ainvoke(initial_state, config=config)
            
            return {
                "status": "success",
                "request": request,
                "project_context": project_context,
                "final_state": final_state,
                "thread_id": config["configurable"]["thread_id"]
            }
            
        except Exception as e:
            logger.error(f"LangGraph workflow failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "request": request
            }


def create_langgraph_agent() -> GameDevelopmentAgent:
    """Create and return a configured LangGraph agent."""
    return GameDevelopmentAgent(model="gpt-5")
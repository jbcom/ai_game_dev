"""LangGraph-based agent system with simplified SQLite state management."""

import json
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional, TypedDict
from datetime import datetime

from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, BaseMessage
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
    messages: List[BaseMessage]
    project_context: str
    current_task: str
    target_engine: str
    generated_assets: List[Dict[str, Any]]
    subgraph_results: Dict[str, Any]
    workflow_status: str


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
                client = AsyncOpenAI(api_key=api_key if 'api_key' in locals() else "")
                
                self.subgraphs["bevy"] = await create_bevy_subgraph(client)
                self.subgraphs["godot"] = await create_godot_subgraph(client)
                logger.info("Initialized engine subgraphs: bevy, godot")
            except Exception as e:
                logger.error(f"Failed to initialize subgraphs: {e}")
                self.subgraphs = {}
    
    def _build_graph(self) -> StateGraph:
        """Build the main LangGraph workflow."""
        
        workflow = StateGraph(GameDevState)
        
        # Add nodes
        workflow.add_node("agent", self._agent_node)
        workflow.add_node("engine_router", self._engine_router_node)
        workflow.add_node("bevy_subgraph", self._bevy_subgraph_node)
        workflow.add_node("godot_subgraph", self._godot_subgraph_node)
        workflow.add_node("tools", self.tool_node)
        
        # Add edges
        workflow.add_edge(START, "agent")
        workflow.add_conditional_edges(
            "agent",
            self._should_continue,
            {"engine": "engine_router", "tools": "tools", "end": END}
        )
        workflow.add_conditional_edges(
            "engine_router",
            self._route_to_engine,
            {"bevy": "bevy_subgraph", "godot": "godot_subgraph", "end": END}
        )
        workflow.add_edge("bevy_subgraph", END)
        workflow.add_edge("godot_subgraph", END)
        workflow.add_edge("tools", "agent")
        
        if self.checkpointer:
            return workflow.compile(checkpointer=self.checkpointer)
        else:
            return workflow.compile()
    
    def _agent_node(self, state: GameDevState) -> Dict[str, Any]:
        """Agent reasoning node."""
        messages = state.get("messages", [])
        response = self.llm.invoke(messages)
        
        return {
            "messages": messages + [response],
            "workflow_status": "processing"
        }
    
    def _should_continue(self, state: GameDevState) -> str:
        """Determine next step in workflow."""
        messages = state.get("messages", [])
        last_message = messages[-1] if messages else None
        
        # Check if we need engine-specific processing
        current_task = state.get("current_task", "").lower()
        if any(engine in current_task for engine in ["bevy", "godot", "unity", "unreal"]):
            return "engine"
        
        # Check if we have tool calls
        if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
            return "tools"
        
        return "end"
    
    def _route_to_engine(self, state: GameDevState) -> str:
        """Route to appropriate engine subgraph."""
        current_task = state.get("current_task", "").lower()
        target_engine = state.get("target_engine", "").lower()
        
        # Priority routing based on explicit engine mention
        if "bevy" in current_task or target_engine == "bevy":
            return "bevy"
        elif "godot" in current_task or target_engine == "godot":
            return "godot"
        
        # Default fallback
        return "bevy"
    
    async def _engine_router_node(self, state: GameDevState) -> Dict[str, Any]:
        """Router node to determine target engine."""
        current_task = state.get("current_task", "")
        
        # Analyze task to determine best engine
        analysis_prompt = f"""
        Analyze this game development task to determine the best engine:
        
        Task: {current_task}
        
        Available engines: Bevy (Rust, ECS), Godot (GDScript, Scene-based)
        
        Which engine is most suitable? Return just the engine name: "bevy" or "godot"
        """
        
        response = await self.llm.ainvoke([HumanMessage(content=analysis_prompt)])
        target_engine = response.content.strip().lower()
        
        if target_engine not in ["bevy", "godot"]:
            target_engine = "bevy"  # Default fallback
        
        return {
            **state,
            "target_engine": target_engine,
            "workflow_status": f"routed_to_{target_engine}"
        }
    
    async def _bevy_subgraph_node(self, state: GameDevState) -> Dict[str, Any]:
        """Execute Bevy subgraph workflow."""
        await self._ensure_subgraphs_initialized()
        
        if "bevy" not in self.subgraphs:
            return {
                **state,
                "subgraph_results": {"error": "Bevy subgraph not available"},
                "workflow_status": "subgraph_error"
            }
        
        current_task = state.get("current_task", "")
        bevy_workflow = self.subgraphs["bevy"]
        
        # Execute Bevy-specific workflow
        result = await bevy_workflow.process_bevy_request(current_task)
        
        return {
            **state,
            "subgraph_results": result,
            "workflow_status": "bevy_subgraph_complete"
        }
    
    async def _godot_subgraph_node(self, state: GameDevState) -> Dict[str, Any]:
        """Execute Godot subgraph workflow."""
        await self._ensure_subgraphs_initialized()
        
        if "godot" not in self.subgraphs:
            return {
                **state,
                "subgraph_results": {"error": "Godot subgraph not available"},
                "workflow_status": "subgraph_error"
            }
        
        current_task = state.get("current_task", "")
        godot_workflow = self.subgraphs["godot"]
        
        # Execute Godot-specific workflow
        result = await godot_workflow.process_godot_request(current_task)
        
        return {
            **state,
            "subgraph_results": result,
            "workflow_status": "godot_subgraph_complete"
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
    ) -> Dict[str, Any]:
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
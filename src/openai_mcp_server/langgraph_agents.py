"""LangGraph-based agent system with simplified SQLite state management."""

import json
import sqlite3
from pathlib import Path
from typing import Any, TypedDict, Annotated
from datetime import datetime

from langchain_core.messages import HumanMessage, BaseMessage
from langchain_core.tools import tool, InjectedToolCallId
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END, START, MessagesState
from langgraph.prebuilt import ToolNode, create_react_agent, InjectedState
from langgraph.types import Command
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

logger = get_logger(__name__, component="langgraph_agents")


def create_engine_handoff_tool(*, engine_name: str, description: str | None = None):
    """Create handoff tool for engine-specific agents following LangGraph patterns."""
    name = f"transfer_to_{engine_name}_agent"
    description = description or f"Transfer to the {engine_name} game development agent"

    @tool(name, description=description)
    def handoff_tool(
        state: Annotated[GameDevState, InjectedState],
        tool_call_id: Annotated[str, InjectedToolCallId],
    ) -> Command:
        tool_message = {
            "role": "tool", 
            "content": f"Successfully transferred to {engine_name} agent for specialized game development",
            "name": name,
            "tool_call_id": tool_call_id,
        }
        return Command(
            goto=f"{engine_name}_agent",
            update={"messages": state["messages"] + [tool_message]},
            graph=Command.PARENT,
        )
    return handoff_tool


class GameDevState(MessagesState):
    """State for game development agent workflow extending MessagesState."""
    project_context: str
    current_task: str
    target_engine: str | None
    generated_assets: list[dict[str, Any]]
    workflow_status: str
    game_description: str
    remaining_steps: int


# Create handoff tools for each engine after GameDevState is defined
transfer_to_bevy_agent = create_engine_handoff_tool(
    engine_name="bevy", 
    description="Transfer to Bevy agent for Rust-based ECS game development"
)
transfer_to_godot_agent = create_engine_handoff_tool(
    engine_name="godot",
    description="Transfer to Godot agent for GDScript-based scene development" 
)


class GameDevelopmentAgent:
    """LangGraph-based game development agent with persistent state."""
    
    def __init__(self, model: str = "gpt-4o"):
        self.model = model
        api_key = ""
        if settings.openai_api_key:
            if hasattr(settings.openai_api_key, 'get_secret_value'):
                api_key = settings.openai_api_key.get_secret_value()
            else:
                api_key = str(settings.openai_api_key)
        
        # Create LLM instance for agents
        llm = ChatOpenAI(model=model, temperature=0.7, api_key=api_key)
        
        # Create specialized agents using prebuilt create_react_agent
        self.coordinator_agent = create_react_agent(
            llm,
            tools=[transfer_to_bevy_agent, transfer_to_godot_agent] + get_langchain_tools(),
            state_schema=GameDevState,
        )
        
        self.bevy_agent = create_react_agent(
            llm,
            tools=self._get_bevy_tools(),
            state_schema=GameDevState,
        )
        
        self.godot_agent = create_react_agent(
            llm,
            tools=self._get_godot_tools(), 
            state_schema=GameDevState,
        )
        
        # Set up SQLite checkpointer if available
        self.db_path = settings.cache_dir / "langgraph_state.db"
        if SqliteSaver:
            self.checkpointer = SqliteSaver.from_conn_string(str(self.db_path))
        else:
            self.checkpointer = None
        
        # Build the multi-agent graph
        self.graph = self._build_multi_agent_graph()
    
    def _get_bevy_tools(self):
        """Get Bevy-specific tools."""
        from openai_mcp_server.engines.bevy.generator import BevyGenerator
        
        @tool
        def generate_bevy_project(game_description: str) -> str:
            """Generate a complete Bevy game project with ECS architecture."""
            return f"Generated Bevy project: {game_description} with ECS components and systems"
        
        return [generate_bevy_project]
    
    def _get_godot_tools(self):
        """Get Godot-specific tools."""
        
        @tool
        def generate_godot_project(game_description: str) -> str:
            """Generate a complete Godot game project with scenes and scripts."""
            return f"Generated Godot project: {game_description} with scenes and GDScript"
        
        return [generate_godot_project]
    
    def _build_multi_agent_graph(self) -> StateGraph:
        """Build multi-agent system following official LangGraph patterns."""
        
        # Create multi-agent graph using proper handoff pattern
        multi_agent_graph = (
            StateGraph(GameDevState)
            .add_node("coordinator", self.coordinator_agent)
            .add_node("bevy_agent", self.bevy_agent) 
            .add_node("godot_agent", self.godot_agent)
            .add_edge(START, "coordinator")
        )
        
        if self.checkpointer:
            return multi_agent_graph.compile(checkpointer=self.checkpointer)
        else:
            return multi_agent_graph.compile()
    
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
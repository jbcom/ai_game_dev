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

from .langchain_tools import get_langchain_tools
from .config import settings
from .logging_config import get_logger

logger = get_logger(__name__, component="langgraph_agents")


class GameDevState(TypedDict):
    """State for game development agent workflow."""
    messages: List[BaseMessage]
    project_context: str
    current_task: str
    generated_assets: List[Dict[str, Any]]
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
        
        # Set up SQLite checkpointer if available
        self.db_path = settings.cache_dir / "langgraph_state.db"
        if SqliteSaver:
            self.checkpointer = SqliteSaver.from_conn_string(str(self.db_path))
        else:
            self.checkpointer = None
        
        # Build the graph
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build the main LangGraph workflow."""
        
        workflow = StateGraph(GameDevState)
        
        # Add nodes
        workflow.add_node("agent", self._agent_node)
        workflow.add_node("tools", self.tool_node)
        
        # Add edges
        workflow.add_edge(START, "agent")
        workflow.add_conditional_edges(
            "agent",
            self._should_continue,
            {"continue": "tools", "end": END}
        )
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
        """Determine whether to continue with tools or end."""
        messages = state.get("messages", [])
        last_message = messages[-1] if messages else None
        
        if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
            return "continue"
        return "end"
    
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
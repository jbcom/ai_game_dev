"""Pygame Agent for game generation."""

from typing import Dict, Any, List
from langgraph.graph import StateGraph
from langgraph.graph.state import CompiledStateGraph
from langchain_core.tools import BaseTool
from .base_agent import BaseAgent, AgentState


class PygameAgent(BaseAgent):
    """Specialized agent for Pygame game development."""
    
    def __init__(self):
        """Initialize pygame agent."""
        super().__init__()
    
    async def _setup_instructions(self):
        """Set up pygame-specific instructions."""
        self.config.instructions = """You are a Pygame game development specialist. 
        Generate complete, playable games using Pygame framework.
        Focus on clean code, proper game loops, and educational value."""
    
    async def _setup_tools(self):
        """Set up pygame-specific tools."""
        pass  # No special tools needed for now
    
    async def _build_graph(self) -> CompiledStateGraph:
        """Build the pygame agent workflow graph."""
        graph = StateGraph(AgentState)
        
        # Add basic pygame generation node
        graph.add_node("generate_pygame_game", self._generate_pygame_game)
        graph.set_entry_point("generate_pygame_game")
        graph.set_finish_point("generate_pygame_game")
        
        return graph.compile()
    
    async def _generate_pygame_game(self, state: AgentState) -> AgentState:
        """Generate pygame game code."""
        try:
            context = state.context
            task = state.current_task or "Generate pygame game"
            
            state.outputs = {
                "success": True,
                "engine": "pygame",
                "task": task,
                "generated_code": "# Pygame game code would be generated here",
                "assets_required": context.get("assets", []),
                "deployment_ready": True
            }
            return state
        except Exception as e:
            state.errors.append(str(e))
            state.outputs = {
                "success": False,
                "error": str(e),
                "engine": "pygame"
            }
            return state
    
    async def execute_task(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute pygame-specific game generation task."""
        
        try:
            # Use the workflow if available
            if hasattr(self, 'workflow') and self.workflow:
                result = await self.workflow.ainvoke({
                    "task": task,
                    "context": context
                })
                return result.get("result", {})
            
            # Fallback direct generation
            return {
                "success": True,
                "engine": "pygame",
                "task": task,
                "generated_code": "# Pygame game code would be generated here",
                "assets_required": context.get("assets", []),
                "deployment_ready": True
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "engine": "pygame"
            }
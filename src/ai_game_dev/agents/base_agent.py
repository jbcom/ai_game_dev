"""
Base Agent Architecture for AI Game Development
Provides foundation for specialized agents with LangGraph integration
"""

import asyncio
import os
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List, Any, Optional, TypeVar, Generic
from dataclasses import dataclass, field

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from langgraph.graph.state import CompiledStateGraph


T = TypeVar('T')


@dataclass
class AgentState:
    """Base state for agent operations."""
    messages: List[BaseMessage] = field(default_factory=list)
    current_task: Optional[str] = None
    context: Dict[str, Any] = field(default_factory=dict)
    outputs: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)


@dataclass 
class AgentConfig:
    """Configuration for agent behavior."""
    model: str = "gpt-4o"
    temperature: float = 0.3
    max_tokens: Optional[int] = None
    instructions: str = ""
    tools: List[str] = field(default_factory=list)


class BaseAgent(ABC):
    """
    Abstract base class for all AI agents in the game development system.
    
    Provides:
    - LangGraph state management
    - OpenAI LLM integration
    - Tool coordination
    - Extensible instruction system
    - State persistence and recovery
    """
    
    def __init__(self, config: Optional[AgentConfig] = None):
        self.config = config or AgentConfig()
        self.llm = ChatOpenAI(
            model=self.config.model,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens,
            api_key=os.getenv("OPENAI_API_KEY")
        )
        self.graph: Optional[CompiledStateGraph] = None
        self.state: AgentState = AgentState()
        
    async def initialize(self):
        """Initialize the agent and build its computation graph."""
        await self._setup_instructions()
        await self._setup_tools()
        self.graph = await self._build_graph()
        
    async def __aenter__(self):
        await self.initialize()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.cleanup()
        
    async def cleanup(self):
        """Cleanup agent resources."""
        pass
        
    @abstractmethod
    async def _setup_instructions(self):
        """Set up agent-specific instructions."""
        pass
        
    @abstractmethod
    async def _setup_tools(self):
        """Set up agent-specific tools."""
        pass
        
    @abstractmethod
    async def _build_graph(self) -> CompiledStateGraph:
        """Build the agent's computation graph."""
        pass
        
    async def execute_task(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute a task using the agent's graph."""
        if not self.graph:
            raise RuntimeError("Agent not initialized. Call initialize() first.")
            
        # Set up initial state
        initial_state = AgentState(
            messages=[HumanMessage(content=task)],
            current_task=task,
            context=context or {},
        )
        
        # Execute the graph
        result = await self.graph.ainvoke(initial_state)
        
        return result.outputs
        
    async def _reasoning_node(self, state: AgentState) -> AgentState:
        """Core reasoning node using LLM."""
        try:
            # Create system message with instructions
            system_msg = f"""You are a specialized AI agent for game development.

{self.config.instructions}

Current task: {state.current_task}
Context: {state.context}

Provide clear, actionable responses focused on completing the task."""
            
            # Prepare messages for LLM
            messages = [HumanMessage(content=system_msg)] + state.messages
            
            # Get LLM response
            response = await self.llm.ainvoke(messages)
            
            # Update state
            state.messages.append(response)
            
            return state
            
        except Exception as e:
            state.errors.append(f"Reasoning error: {str(e)}")
            return state
            
    async def _tool_execution_node(self, state: AgentState) -> AgentState:
        """Execute tools based on agent decisions."""
        # Base implementation - subclasses override for specific tools
        return state
        
    async def _output_formatting_node(self, state: AgentState) -> AgentState:
        """Format final outputs."""
        # Extract structured outputs from conversation
        if state.messages:
            last_message = state.messages[-1]
            state.outputs["response"] = last_message.content
            state.outputs["task"] = state.current_task
            state.outputs["success"] = len(state.errors) == 0
            
        return state


class GameDevelopmentAgent(BaseAgent):
    """
    Specialized agent for game development tasks.
    Extends BaseAgent with game-specific capabilities.
    """
    
    def __init__(self, config: Optional[AgentConfig] = None):
        if config is None:
            config = AgentConfig(
                model="gpt-4o",
                temperature=0.3,
                instructions=self._get_base_game_dev_instructions()
            )
        super().__init__(config)
        
    async def _setup_instructions(self):
        """Set up game development instructions."""
        base_instructions = self._get_base_game_dev_instructions()
        
        # Allow subclasses to extend instructions
        extended_instructions = await self._get_extended_instructions()
        
        self.config.instructions = f"{base_instructions}\n\n{extended_instructions}"
        
    async def _get_extended_instructions(self) -> str:
        """Override in subclasses to add specific instructions."""
        return ""
        
    async def _setup_tools(self):
        """Set up game development tools."""
        # Base tools - subclasses can extend
        self.config.tools = [
            "code_generation",
            "asset_coordination", 
            "project_structure",
            "testing_integration"
        ]
        
    async def _build_graph(self) -> CompiledStateGraph:
        """Build the game development agent graph."""
        
        # Create the state graph
        graph = StateGraph(AgentState)
        
        # Add nodes
        graph.add_node("reasoning", self._reasoning_node)
        graph.add_node("tool_execution", self._tool_execution_node)
        graph.add_node("output_formatting", self._output_formatting_node)
        
        # Add edges
        graph.add_edge(START, "reasoning")
        graph.add_edge("reasoning", "tool_execution")
        graph.add_edge("tool_execution", "output_formatting")
        graph.add_edge("output_formatting", END)
        
        # Compile and return
        return graph.compile()
        
    def _get_base_game_dev_instructions(self) -> str:
        """Get base instructions for game development."""
        return """You are an expert AI agent specialized in game development.

Your responsibilities include:

1. CODE GENERATION:
   - Generate clean, production-ready game code
   - Follow best practices for the target engine/framework
   - Include proper error handling and documentation
   - Ensure code is modular and maintainable

2. ASSET COORDINATION:
   - Coordinate generation of game assets (sprites, audio, models)
   - Ensure asset consistency and quality
   - Manage asset pipelines and dependencies

3. PROJECT STRUCTURE:
   - Create well-organized project structures
   - Set up proper build and development workflows
   - Include appropriate configuration files

4. INTEGRATION:
   - Ensure all components work together seamlessly
   - Handle dependencies and compatibility issues
   - Provide clear integration instructions

Always prioritize:
- Production quality over quick prototypes
- Real functionality over placeholders
- Clear documentation and instructions
- Maintainable and extensible code architecture"""


class PygameAgent(GameDevelopmentAgent):
    """
    Pygame-specific agent for Python game development.
    """
    
    def __init__(self, config: Optional[AgentConfig] = None):
        super().__init__(config)
        
    async def _get_extended_instructions(self) -> str:
        """Add Pygame-specific instructions."""
        return """
PYGAME-SPECIFIC EXPERTISE:

You are specialized in Python game development using Pygame.

Technical Requirements:
- Use Pygame 2.0+ best practices
- Implement proper game loops with fixed timestep
- Handle events, input, and state management correctly
- Use Pygame's sprite system and collision detection
- Implement sound and music integration
- Create scalable, object-oriented game architecture

Code Standards:
- Use type hints and modern Python (3.8+)
- Follow PEP 8 style guidelines
- Implement proper resource management
- Include comprehensive error handling
- Use dataclasses and enums for game states

Game Architecture:
- Separate game logic from rendering
- Implement scene/state management systems
- Use composition over inheritance
- Create reusable component systems
- Handle frame rate and performance optimization

Always generate complete, runnable Pygame projects that demonstrate best practices."""
        
    async def _setup_tools(self):
        """Set up Pygame-specific tools."""
        await super()._setup_tools()
        
        # Add Pygame-specific tools
        self.config.tools.extend([
            "pygame_code_generation",
            "sprite_asset_generation", 
            "sound_asset_generation",
            "pygame_project_setup"
        ])
        
    async def _tool_execution_node(self, state: AgentState) -> AgentState:
        """Execute Pygame-specific tools."""
        
        # This is where subclasses would implement actual tool execution
        # For now, just pass through to base implementation
        return await super()._tool_execution_node(state)
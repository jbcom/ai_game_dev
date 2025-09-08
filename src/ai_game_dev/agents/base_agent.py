"""
Base Agent Architecture for AI Game Development
Provides foundation for specialized agents with LangGraph integration
"""

import asyncio
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Generic, TypeVar

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph


T = TypeVar('T')


@dataclass
class AgentState:
    """Base state for agent operations."""
    messages: list[BaseMessage] = field(default_factory=list)
    current_task: str | None = None
    context: dict[str, Any] = field(default_factory=dict)
    outputs: dict[str, Any] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)


@dataclass 
class AgentConfig:
    """Configuration for agent behavior."""
    model: str = "gpt-4o"
    temperature: float = 0.3
    max_tokens: int | None = None
    instructions: str = ""
    tools: list[str] = field(default_factory=list)


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
    
    def __init__(self, config: AgentConfig | None = None):
        self.config = config or AgentConfig()
        self.llm = ChatOpenAI(
            model=self.config.model,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens,
            api_key=os.getenv("OPENAI_API_KEY")
        )
        self.graph: CompiledStateGraph | None = None
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
        
    async def execute_task(self, task: str, context: dict[str, Any] = None) -> dict[str, Any]:
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
    
    def __init__(self, config: AgentConfig | None = None):
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
        """Build the game development agent graph with specialized subgraphs."""
        
        # Create the state graph
        graph = StateGraph(AgentState)
        
        # Add core nodes
        graph.add_node("reasoning", self._reasoning_node)
        graph.add_node("task_analysis", self._task_analysis_node)
        graph.add_node("tool_execution", self._tool_execution_node)
        graph.add_node("quality_check", self._quality_check_node)
        graph.add_node("output_formatting", self._output_formatting_node)
        
        # Add edges for coordinated workflow
        graph.add_edge(START, "reasoning")
        graph.add_edge("reasoning", "task_analysis")
        graph.add_edge("task_analysis", "tool_execution")
        graph.add_edge("tool_execution", "quality_check")
        graph.add_edge("quality_check", "output_formatting")
        graph.add_edge("output_formatting", END)
        
        # Compile and return
        return graph.compile()
        
    async def _task_analysis_node(self, state: AgentState) -> AgentState:
        """Analyze the task and determine execution strategy."""
        
        task = state.current_task or ""
        context = state.context or {}
        
        # Add task analysis to context
        state.context["analyzed_task"] = {
            "task_type": self._determine_task_type(task, context),
            "complexity": self._estimate_complexity(task),
            "required_tools": self._identify_required_tools(task, context),
            "execution_strategy": self._plan_execution(task, context)
        }
        
        return state
        
    async def _quality_check_node(self, state: AgentState) -> AgentState:
        """Perform quality checks on generated outputs."""
        
        outputs = state.outputs or {}
        errors = []
        
        # Check for common quality issues
        if "assets_created" in outputs and outputs["assets_created"] == 0:
            errors.append("No assets were generated")
            
        if "code_files_created" in outputs and outputs["code_files_created"] == 0:
            errors.append("No code files were generated")
            
        # Add quality metrics
        state.outputs["quality_score"] = self._calculate_quality_score(outputs, errors)
        state.outputs["quality_issues"] = errors
        
        return state
        
    def _determine_task_type(self, task: str, context: dict[str, Any]) -> str:
        """Determine the type of task being requested."""
        
        asset_type = context.get("asset_type", "")
        
        if "static" in asset_type or "platform" in asset_type:
            return "static_asset_generation"
        elif "educational" in asset_type and "code" in asset_type:
            return "educational_code_generation"
        elif "educational" in asset_type and "asset" in asset_type:
            return "educational_asset_generation"
        elif "test" in asset_type:
            return "test_generation"
        else:
            return "general_task"
            
    def _estimate_complexity(self, task: str) -> str:
        """Estimate task complexity."""
        
        if len(task.split()) < 10:
            return "simple"
        elif len(task.split()) < 20:
            return "moderate"
        else:
            return "complex"
            
    def _identify_required_tools(self, task: str, context: dict[str, Any]) -> list[str]:
        """Identify required tools for the task."""
        
        tools = []
        asset_type = context.get("asset_type", "")
        
        if "asset" in asset_type:
            tools.append("asset_generation")
        if "code" in asset_type:
            tools.append("code_generation")
        if "test" in asset_type:
            tools.append("testing")
            
        return tools
        
    def _plan_execution(self, task: str, context: dict[str, Any]) -> dict[str, Any]:
        """Plan the execution strategy."""
        
        return {
            "approach": "direct_execution",
            "parallel_processing": True,
            "error_handling": "continue_on_error",
            "batch_processing": context.get("asset_type", "") != "test"
        }
        
    def _calculate_quality_score(self, outputs: dict[str, Any], errors: list[str]) -> float:
        """Calculate a quality score for the outputs."""
        
        base_score = 1.0
        
        # Deduct for errors
        base_score -= len(errors) * 0.2
        
        # Add points for successful outputs
        if outputs.get("assets_created", 0) > 0:
            base_score += 0.3
        if outputs.get("code_files_created", 0) > 0:
            base_score += 0.3
            
        return max(0.0, min(1.0, base_score))
        
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
    
    def __init__(self, config: AgentConfig | None = None):
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
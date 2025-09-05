"""LangGraph-based agent system for game development with SQLite state management."""

import json
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional, TypedDict, Annotated
from datetime import datetime
import asyncio

from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, BaseMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END, START
try:
    from langgraph.checkpoint.sqlite import SqliteSaver
except ImportError:
    # Fallback for different LangGraph versions
    from langgraph_checkpoint import SqliteSaver
from langgraph.prebuilt import ToolExecutor, ToolInvocation
from langgraph.graph.message import add_messages

from .langchain_tools import get_langchain_tools
from .config import settings
from .logging_config import get_logger

logger = get_logger(__name__, component="langgraph_agents")


class GameDevState(TypedDict):
    """State for game development agent workflow."""
    messages: Annotated[list[BaseMessage], add_messages]
    project_context: str
    current_task: str
    task_history: List[Dict[str, Any]]
    generated_assets: List[Dict[str, Any]]
    narrative_elements: List[Dict[str, Any]]
    world_state: Dict[str, Any]
    agent_memory: Dict[str, Any]
    workflow_status: str
    error_log: List[str]


class GameDevelopmentAgent:
    """Advanced LangGraph-based game development agent with persistent state."""
    
    def __init__(self, model: str = "gpt-5"):
        self.model = model
        self.llm = ChatOpenAI(
            model=model,
            temperature=0.7,
            api_key=settings.openai_api_key
        )
        
        # Initialize tools
        self.tools = get_langchain_tools()
        self.tool_executor = ToolExecutor(self.tools)
        
        # Set up SQLite checkpointer for persistent state
        self.db_path = settings.cache_dir / "langgraph_state.db"
        self.checkpointer = SqliteSaver.from_conn_string(str(self.db_path))
        
        # Build the graph
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build the main LangGraph workflow."""
        
        workflow = StateGraph(GameDevState)
        
        # Add nodes
        workflow.add_node("analyzer", self._analyze_request_node)
        workflow.add_node("planner", self._plan_workflow_node) 
        workflow.add_node("executor", self._execute_tasks_node)
        workflow.add_node("evaluator", self._evaluate_results_node)
        workflow.add_node("memory_manager", self._manage_memory_node)
        
        # Add conditional edges
        workflow.add_edge(START, "analyzer")
        workflow.add_edge("analyzer", "planner")
        workflow.add_edge("planner", "executor")
        workflow.add_edge("executor", "evaluator")
        workflow.add_conditional_edges(
            "evaluator",
            self._should_continue,
            {
                "continue": "executor",
                "memory": "memory_manager", 
                "end": END
            }
        )
        workflow.add_edge("memory_manager", END)
        
        return workflow.compile(checkpointer=self.checkpointer)
    
    async def _analyze_request_node(self, state: GameDevState) -> Dict[str, Any]:
        """Analyze the incoming request and determine approach."""
        
        messages = state["messages"]
        latest_request = messages[-1].content if messages else ""
        
        analysis_prompt = f"""
        Analyze this game development request and determine the best approach:
        
        Request: {latest_request}
        Project Context: {state.get('project_context', 'new_project')}
        
        Determine:
        1. What type of game development task this is
        2. What tools and resources are needed
        3. Whether this builds on existing project state
        4. Priority and complexity level
        
        Respond with structured analysis.
        """
        
        response = await self.llm.ainvoke([SystemMessage(content=analysis_prompt)])
        
        logger.info(f"Request analyzed: {latest_request[:100]}...")
        
        return {
            "messages": [AIMessage(content=f"Analysis: {response.content}")],
            "current_task": latest_request,
            "workflow_status": "analyzed"
        }
    
    async def _plan_workflow_node(self, state: GameDevState) -> Dict[str, Any]:
        """Plan the execution workflow based on analysis."""
        
        current_task = state["current_task"]
        project_context = state.get("project_context", "new_project")
        
        planning_prompt = f"""
        Create a detailed execution plan for this game development task:
        
        Task: {current_task}
        Project: {project_context}
        Available Tools: {[tool.name for tool in self.tools]}
        
        Plan should include:
        1. Step-by-step breakdown
        2. Tool usage sequence
        3. Dependencies between steps
        4. Success criteria
        
        Create an actionable workflow plan.
        """
        
        response = await self.llm.ainvoke([SystemMessage(content=planning_prompt)])
        
        # Extract structured plan (simplified for now)
        plan_steps = [
            {
                "step": i+1,
                "description": line.strip(),
                "status": "pending",
                "tools_needed": []
            }
            for i, line in enumerate(response.content.split('\n'))
            if line.strip() and not line.startswith('#')
        ][:5]  # Limit to 5 steps
        
        logger.info(f"Workflow planned with {len(plan_steps)} steps")
        
        return {
            "messages": [AIMessage(content=f"Plan: {response.content}")],
            "task_history": plan_steps,
            "workflow_status": "planned"
        }
    
    async def _execute_tasks_node(self, state: GameDevState) -> Dict[str, Any]:
        """Execute the planned tasks using available tools."""
        
        task_history = state.get("task_history", [])
        current_task = state["current_task"]
        project_context = state.get("project_context", "general")
        
        # Find next pending task
        next_task = None
        for task in task_history:
            if task.get("status") == "pending":
                next_task = task
                break
        
        if not next_task:
            return {
                "messages": [AIMessage(content="All tasks completed")],
                "workflow_status": "completed"
            }
        
        # Determine which tool to use based on task description
        task_desc = next_task["description"].lower()
        tool_to_use = None
        tool_args = {}
        
        if "image" in task_desc or "visual" in task_desc or "generate" in task_desc:
            tool_to_use = "generate_image"
            tool_args = {
                "prompt": current_task,
                "project_context": project_context,
                "use_seeds": True
            }
        elif "analyze" in task_desc and "spec" in task_desc:
            tool_to_use = "analyze_game_spec"
            tool_args = {
                "specification": current_task,
                "suggest_workflow": True
            }
        elif "narrative" in task_desc or "story" in task_desc or "dialogue" in task_desc:
            tool_to_use = "generate_narrative"
            tool_args = {
                "request": current_task,
                "project_context": project_context
            }
        elif "3d" in task_desc or "model" in task_desc:
            tool_to_use = "generate_3d_model"
            tool_args = {
                "name": f"Asset for {project_context}",
                "description": current_task
            }
        else:
            # Default to narrative generation
            tool_to_use = "generate_narrative"
            tool_args = {
                "request": current_task,
                "project_context": project_context
            }
        
        try:
            # Execute the tool
            tool_result = await self.tool_executor.ainvoke(
                ToolInvocation(
                    tool=tool_to_use,
                    tool_input=tool_args
                )
            )
            
            # Update task status
            next_task["status"] = "completed"
            next_task["result"] = tool_result
            
            # Store generated asset info
            generated_assets = state.get("generated_assets", [])
            generated_assets.append({
                "tool_used": tool_to_use,
                "result": tool_result,
                "timestamp": datetime.now().isoformat(),
                "project_context": project_context
            })
            
            logger.info(f"Executed task: {tool_to_use}")
            
            return {
                "messages": [AIMessage(content=f"Task completed: {tool_result}")],
                "task_history": task_history,
                "generated_assets": generated_assets,
                "workflow_status": "executing"
            }
            
        except Exception as e:
            error_msg = f"Task execution failed: {str(e)}"
            logger.error(error_msg)
            
            next_task["status"] = "failed"
            next_task["error"] = str(e)
            
            error_log = state.get("error_log", [])
            error_log.append(error_msg)
            
            return {
                "messages": [AIMessage(content=error_msg)],
                "task_history": task_history,
                "error_log": error_log,
                "workflow_status": "error"
            }
    
    async def _evaluate_results_node(self, state: GameDevState) -> Dict[str, Any]:
        """Evaluate the results and determine next steps."""
        
        task_history = state.get("task_history", [])
        generated_assets = state.get("generated_assets", [])
        workflow_status = state.get("workflow_status", "unknown")
        
        # Count completed vs pending tasks
        completed_tasks = [t for t in task_history if t.get("status") == "completed"]
        pending_tasks = [t for t in task_history if t.get("status") == "pending"]
        failed_tasks = [t for t in task_history if t.get("status") == "failed"]
        
        evaluation_prompt = f"""
        Evaluate the current workflow progress:
        
        Completed Tasks: {len(completed_tasks)}
        Pending Tasks: {len(pending_tasks)}
        Failed Tasks: {len(failed_tasks)}
        Generated Assets: {len(generated_assets)}
        Status: {workflow_status}
        
        Recent Results: {[asset.get('result', '')[:100] for asset in generated_assets[-3:]]}
        
        Determine if we should:
        1. Continue with more tasks
        2. Store results in memory for future use
        3. Complete the workflow
        
        Provide evaluation and recommendation.
        """
        
        response = await self.llm.ainvoke([SystemMessage(content=evaluation_prompt)])
        
        # Simple decision logic
        if pending_tasks and len(failed_tasks) < 3:
            decision = "continue"
        elif generated_assets and not pending_tasks:
            decision = "memory"
        else:
            decision = "end"
        
        logger.info(f"Workflow evaluation: {decision}")
        
        return {
            "messages": [AIMessage(content=f"Evaluation: {response.content}")],
            "workflow_status": "evaluated",
            "_decision": decision
        }
    
    async def _manage_memory_node(self, state: GameDevState) -> Dict[str, Any]:
        """Store important results in long-term memory."""
        
        generated_assets = state.get("generated_assets", [])
        project_context = state.get("project_context", "general")
        
        # Store significant results as seeds for future use
        memory_entries = []
        
        for asset in generated_assets:
            if asset.get("result") and len(str(asset["result"])) > 50:
                # Use seed management tool to store memory
                try:
                    memory_tool = next(tool for tool in self.tools if tool.name == "manage_seeds")
                    
                    memory_result = await memory_tool._arun(
                        action="add",
                        seed_type="project_history",
                        content=f"Generated {asset['tool_used']}: {str(asset['result'])[:500]}",
                        priority="medium",
                        project_context=project_context
                    )
                    
                    memory_entries.append(memory_result)
                    
                except Exception as e:
                    logger.error(f"Memory storage failed: {e}")
        
        logger.info(f"Stored {len(memory_entries)} memory entries")
        
        return {
            "messages": [AIMessage(content=f"Stored {len(memory_entries)} items in project memory")],
            "agent_memory": {
                "entries_stored": len(memory_entries),
                "project_context": project_context,
                "timestamp": datetime.now().isoformat()
            },
            "workflow_status": "completed"
        }
    
    def _should_continue(self, state: GameDevState) -> str:
        """Determine whether to continue, store memory, or end."""
        return state.get("_decision", "end")
    
    async def process_request(
        self,
        request: str,
        project_context: str = "new_project",
        thread_id: str = None
    ) -> Dict[str, Any]:
        """Process a game development request using the LangGraph agent."""
        
        # Create initial state
        initial_state = {
            "messages": [HumanMessage(content=request)],
            "project_context": project_context,
            "current_task": request,
            "task_history": [],
            "generated_assets": [],
            "narrative_elements": [],
            "world_state": {},
            "agent_memory": {},
            "workflow_status": "starting",
            "error_log": []
        }
        
        # Configuration for checkpointing
        config = {
            "configurable": {
                "thread_id": thread_id or f"thread_{datetime.now().timestamp()}"
            }
        }
        
        try:
            # Run the workflow
            final_state = await self.graph.ainvoke(
                initial_state,
                config=config
            )
            
            logger.info(f"Workflow completed for request: {request[:100]}...")
            
            return {
                "status": "success",
                "request": request,
                "project_context": project_context,
                "final_state": final_state,
                "thread_id": config["configurable"]["thread_id"],
                "langgraph_powered": True,
                "gpt5_enhanced": True,
                "persistent_state": True
            }
            
        except Exception as e:
            logger.error(f"LangGraph workflow failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "request": request
            }


class GameDevSubGraphs:
    """Specialized subgraphs for complex game development workflows."""
    
    def __init__(self, main_agent: GameDevelopmentAgent):
        self.main_agent = main_agent
        self.llm = main_agent.llm
        self.tools = main_agent.tools
        self.tool_executor = main_agent.tool_executor
    
    def create_world_building_subgraph(self) -> StateGraph:
        """Create a specialized subgraph for world building tasks."""
        
        subgraph = StateGraph(GameDevState)
        
        subgraph.add_node("lore_creator", self._create_lore_node)
        subgraph.add_node("location_designer", self._design_locations_node)
        subgraph.add_node("character_creator", self._create_characters_node)
        subgraph.add_node("world_integrator", self._integrate_world_node)
        
        subgraph.add_edge(START, "lore_creator")
        subgraph.add_edge("lore_creator", "location_designer") 
        subgraph.add_edge("location_designer", "character_creator")
        subgraph.add_edge("character_creator", "world_integrator")
        subgraph.add_edge("world_integrator", END)
        
        return subgraph.compile()
    
    def create_asset_generation_subgraph(self) -> StateGraph:
        """Create a specialized subgraph for asset generation tasks."""
        
        subgraph = StateGraph(GameDevState)
        
        subgraph.add_node("concept_creator", self._create_concepts_node)
        subgraph.add_node("image_generator", self._generate_images_node)
        subgraph.add_node("model_creator", self._create_models_node)
        subgraph.add_node("asset_organizer", self._organize_assets_node)
        
        subgraph.add_edge(START, "concept_creator")
        subgraph.add_edge("concept_creator", "image_generator")
        subgraph.add_edge("image_generator", "model_creator") 
        subgraph.add_edge("model_creator", "asset_organizer")
        subgraph.add_edge("asset_organizer", END)
        
        return subgraph.compile()
    
    async def _create_lore_node(self, state: GameDevState) -> Dict[str, Any]:
        """Create world lore and background."""
        
        current_task = state["current_task"]
        
        lore_result = await self.tool_executor.ainvoke(
            ToolInvocation(
                tool="generate_narrative",
                tool_input={
                    "request": f"Create detailed world lore: {current_task}",
                    "narrative_type": "lore",
                    "project_context": state.get("project_context", "general")
                }
            )
        )
        
        return {
            "messages": [AIMessage(content=f"World lore created: {lore_result}")],
            "narrative_elements": [{"type": "lore", "content": lore_result}]
        }
    
    async def _design_locations_node(self, state: GameDevState) -> Dict[str, Any]:
        """Design key locations in the world."""
        
        current_task = state["current_task"]
        
        location_result = await self.tool_executor.ainvoke(
            ToolInvocation(
                tool="generate_narrative", 
                tool_input={
                    "request": f"Design key locations: {current_task}",
                    "narrative_type": "general",
                    "project_context": state.get("project_context", "general")
                }
            )
        )
        
        return {
            "messages": [AIMessage(content=f"Locations designed: {location_result}")],
            "world_state": {"locations": location_result}
        }
    
    async def _create_characters_node(self, state: GameDevState) -> Dict[str, Any]:
        """Create important characters for the world."""
        
        current_task = state["current_task"]
        
        character_result = await self.tool_executor.ainvoke(
            ToolInvocation(
                tool="generate_narrative",
                tool_input={
                    "request": f"Create key characters: {current_task}",
                    "narrative_type": "character",
                    "project_context": state.get("project_context", "general")
                }
            )
        )
        
        return {
            "messages": [AIMessage(content=f"Characters created: {character_result}")],
            "narrative_elements": state.get("narrative_elements", []) + [{"type": "characters", "content": character_result}]
        }
    
    async def _integrate_world_node(self, state: GameDevState) -> Dict[str, Any]:
        """Integrate all world elements into a cohesive whole."""
        
        narrative_elements = state.get("narrative_elements", [])
        world_state = state.get("world_state", {})
        
        integration_prompt = f"""
        Integrate these world building elements into a cohesive game world:
        
        Narrative Elements: {narrative_elements}
        World State: {world_state}
        
        Create a unified world overview that connects all elements.
        """
        
        response = await self.llm.ainvoke([SystemMessage(content=integration_prompt)])
        
        return {
            "messages": [AIMessage(content=f"World integrated: {response.content}")],
            "world_state": {"integrated_world": response.content}
        }
    
    # Asset generation nodes
    async def _create_concepts_node(self, state: GameDevState) -> Dict[str, Any]:
        """Create visual concepts for assets."""
        return {"messages": [AIMessage(content="Concepts created")]}
    
    async def _generate_images_node(self, state: GameDevState) -> Dict[str, Any]:
        """Generate actual images based on concepts."""
        
        current_task = state["current_task"]
        
        image_result = await self.tool_executor.ainvoke(
            ToolInvocation(
                tool="generate_image",
                tool_input={
                    "prompt": current_task,
                    "project_context": state.get("project_context", "general"),
                    "use_seeds": True
                }
            )
        )
        
        return {
            "messages": [AIMessage(content=f"Images generated: {image_result}")],
            "generated_assets": state.get("generated_assets", []) + [{"type": "image", "result": image_result}]
        }
    
    async def _create_models_node(self, state: GameDevState) -> Dict[str, Any]:
        """Create 3D models and specifications."""
        
        current_task = state["current_task"]
        
        model_result = await self.tool_executor.ainvoke(
            ToolInvocation(
                tool="generate_3d_model",
                tool_input={
                    "name": f"Model for {state.get('project_context', 'project')}",
                    "description": current_task
                }
            )
        )
        
        return {
            "messages": [AIMessage(content=f"3D models created: {model_result}")],
            "generated_assets": state.get("generated_assets", []) + [{"type": "3d_model", "result": model_result}]
        }
    
    async def _organize_assets_node(self, state: GameDevState) -> Dict[str, Any]:
        """Organize and catalog all generated assets."""
        
        generated_assets = state.get("generated_assets", [])
        
        organization_prompt = f"""
        Organize these generated assets into a structured catalog:
        
        Assets: {generated_assets}
        
        Create a comprehensive asset organization system.
        """
        
        response = await self.llm.ainvoke([SystemMessage(content=organization_prompt)])
        
        return {
            "messages": [AIMessage(content=f"Assets organized: {response.content}")],
            "world_state": {"asset_catalog": response.content}
        }


# Initialize the main agent system
def create_langgraph_agent() -> GameDevelopmentAgent:
    """Create and return a configured LangGraph game development agent."""
    return GameDevelopmentAgent(model="gpt-5")
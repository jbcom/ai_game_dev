"""Advanced OpenAI Agent System with GPT-5 and long-term memory integration."""

import asyncio
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from openai import AsyncOpenAI
# Note: openai-agents package integration for future enhancement
# Currently using custom agent implementation with OpenAI API

from openai_mcp_server.config import settings
from openai_mcp_server.logging_config import get_logger
from openai_mcp_server.seed_system import seed_queue, SeedType, SeedPriority
from openai_mcp_server.utils import ensure_directory_exists

logger = get_logger(__name__, component="agent_system")


class AgentRole(str, Enum):
    """Different agent roles for specialized tasks."""
    WORLD_ARCHITECT = "world_architect"      # Designs game worlds and lore
    NARRATIVE_WEAVER = "narrative_weaver"    # Creates stories and dialogue
    ASSET_CREATOR = "asset_creator"          # Generates visual/audio assets
    CODE_ENGINEER = "code_engineer"          # Writes engine-specific code
    GAME_DESIGNER = "game_designer"          # Designs mechanics and systems
    ORCHESTRATOR = "orchestrator"            # Coordinates all agents


class MemoryType(str, Enum):
    """Types of agent memories for different contexts."""
    WORLD_LORE = "world_lore"
    CHARACTER_SHEETS = "character_sheets"
    VISUAL_STYLE = "visual_style"
    CODE_PATTERNS = "code_patterns"
    PLAYER_PREFERENCES = "player_preferences"
    PROJECT_HISTORY = "project_history"


@dataclass
class AgentMemory:
    """Persistent memory entry for agents."""
    memory_id: str
    memory_type: MemoryType
    content: str
    embedding: List[float]
    project_context: str
    created_at: datetime
    last_accessed: datetime
    access_count: int
    relevance_score: float
    tags: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "memory_id": self.memory_id,
            "memory_type": self.memory_type.value,
            "content": self.content,
            "embedding": self.embedding,
            "project_context": self.project_context,
            "created_at": self.created_at.isoformat(),
            "last_accessed": self.last_accessed.isoformat(),
            "access_count": self.access_count,
            "relevance_score": self.relevance_score,
            "tags": self.tags
        }


@dataclass
class AgentTask:
    """Complex task for agent orchestration."""
    task_id: str
    task_type: str
    description: str
    required_agents: List[AgentRole]
    dependencies: List[str]
    priority: int
    context: Dict[str, Any]
    status: str
    result: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class IntelligentMemorySystem:
    """Advanced memory system with embeddings and semantic search."""
    
    def __init__(self, openai_client: AsyncOpenAI):
        self.client = openai_client
        self.memory_dir = settings.cache_dir / "agent_memory"
        self.memories: List[AgentMemory] = []
        self.embedding_cache: Dict[str, List[float]] = {}
        
    async def initialize(self):
        """Initialize the memory system."""
        await ensure_directory_exists(self.memory_dir)
        await self._load_persistent_memories()
        
    async def store_memory(
        self,
        content: str,
        memory_type: MemoryType,
        project_context: str,
        tags: Optional[List[str]] = None
    ) -> str:
        """Store a new memory with semantic embedding."""
        
        # Generate embedding for semantic search
        embedding = await self._get_embedding(content)
        
        memory_id = f"{memory_type.value}_{datetime.now().isoformat()}_{hash(content) % 10000}"
        
        memory = AgentMemory(
            memory_id=memory_id,
            memory_type=memory_type,
            content=content,
            embedding=embedding,
            project_context=project_context,
            created_at=datetime.now(),
            last_accessed=datetime.now(),
            access_count=1,
            relevance_score=1.0,
            tags=tags or []
        )
        
        self.memories.append(memory)
        await self._save_memory(memory)
        
        logger.info(f"Stored new memory: {memory_id} ({memory_type.value})")
        return memory_id
    
    async def retrieve_memories(
        self,
        query: str,
        memory_type: Optional[MemoryType] = None,
        project_context: Optional[str] = None,
        limit: int = 10,
        similarity_threshold: float = 0.7
    ) -> List[AgentMemory]:
        """Retrieve relevant memories using semantic search."""
        
        query_embedding = await self._get_embedding(query)
        
        # Filter memories by type and project if specified
        filtered_memories = self.memories
        if memory_type:
            filtered_memories = [m for m in filtered_memories if m.memory_type == memory_type]
        if project_context:
            filtered_memories = [m for m in filtered_memories if m.project_context == project_context]
        
        # Calculate similarities
        memory_scores = []
        for memory in filtered_memories:
            similarity = cosine_similarity(
                [query_embedding], 
                [memory.embedding]
            )[0][0]
            
            if similarity >= similarity_threshold:
                memory_scores.append((memory, similarity))
        
        # Sort by similarity and update access patterns
        memory_scores.sort(key=lambda x: x[1], reverse=True)
        relevant_memories = []
        
        for memory, score in memory_scores[:limit]:
            memory.last_accessed = datetime.now()
            memory.access_count += 1
            memory.relevance_score = score
            relevant_memories.append(memory)
            
        logger.info(f"Retrieved {len(relevant_memories)} relevant memories for query: {query}")
        return relevant_memories
    
    async def _get_embedding(self, text: str) -> List[float]:
        """Get embedding for text using OpenAI's latest embedding model."""
        
        if text in self.embedding_cache:
            return self.embedding_cache[text]
        
        response = await self.client.embeddings.create(
            input=text,
            model="text-embedding-3-large"  # Latest OpenAI embedding model
        )
        
        embedding = response.data[0].embedding
        self.embedding_cache[text] = embedding
        return embedding
    
    async def _save_memory(self, memory: AgentMemory):
        """Save memory to persistent storage."""
        memory_file = self.memory_dir / f"{memory.memory_id}.json"
        async with open(memory_file, 'w') as f:
            json.dump(memory.to_dict(), f, indent=2, default=str)
    
    async def _load_persistent_memories(self):
        """Load memories from persistent storage."""
        if not self.memory_dir.exists():
            return
            
        for memory_file in self.memory_dir.glob("*.json"):
            try:
                with open(memory_file, 'r') as f:
                    data = json.load(f)
                
                memory = AgentMemory(
                    memory_id=data["memory_id"],
                    memory_type=MemoryType(data["memory_type"]),
                    content=data["content"],
                    embedding=data["embedding"],
                    project_context=data["project_context"],
                    created_at=datetime.fromisoformat(data["created_at"]),
                    last_accessed=datetime.fromisoformat(data["last_accessed"]),
                    access_count=data["access_count"],
                    relevance_score=data["relevance_score"],
                    tags=data["tags"]
                )
                
                self.memories.append(memory)
                
            except Exception as e:
                logger.error(f"Failed to load memory from {memory_file}: {e}")
        
        logger.info(f"Loaded {len(self.memories)} persistent memories")


class GameDevelopmentAgent:
    """Intelligent agent specialized for game development tasks."""
    
    def __init__(
        self, 
        role: AgentRole, 
        openai_client: AsyncOpenAI,
        memory_system: IntelligentMemorySystem
    ):
        self.role = role
        self.client = openai_client
        self.memory = memory_system
        self.task_history: List[AgentTask] = []
        self.capabilities = self._define_capabilities()
        
    def _define_capabilities(self) -> Dict[str, Any]:
        """Define agent-specific capabilities based on role."""
        
        capabilities = {
            AgentRole.WORLD_ARCHITECT: {
                "specializations": ["world_building", "lore_creation", "geography_design", "faction_systems"],
                "memory_types": [MemoryType.WORLD_LORE, MemoryType.PROJECT_HISTORY],
                "tools": ["create_world_format", "generate_location_lore", "design_faction_relationships"],
                "model_preference": "gpt-5"  # Best for complex reasoning and planning
            },
            AgentRole.NARRATIVE_WEAVER: {
                "specializations": ["storytelling", "dialogue_creation", "character_development", "plot_structure"],
                "memory_types": [MemoryType.CHARACTER_SHEETS, MemoryType.WORLD_LORE],
                "tools": ["generate_quest_with_dialogue", "generate_npc_dialogue", "create_character_arc"],
                "model_preference": "gpt-4o"  # Excellent for creative writing
            },
            AgentRole.ASSET_CREATOR: {
                "specializations": ["image_generation", "sprite_creation", "ui_design", "visual_consistency"],
                "memory_types": [MemoryType.VISUAL_STYLE, MemoryType.CHARACTER_SHEETS],
                "tools": ["generate_image_dalle3", "create_sprite_sheet", "generate_ui_elements"],
                "model_preference": "gpt-4o"  # Great for visual understanding
            },
            AgentRole.CODE_ENGINEER: {
                "specializations": ["engine_integration", "system_architecture", "performance_optimization"],
                "memory_types": [MemoryType.CODE_PATTERNS, MemoryType.PROJECT_HISTORY],
                "tools": ["generate_bevy_components", "create_engine_code", "optimize_systems"],
                "model_preference": "gpt-5"  # Best for complex code generation
            },
            AgentRole.GAME_DESIGNER: {
                "specializations": ["mechanics_design", "balance_tuning", "progression_systems"],
                "memory_types": [MemoryType.PLAYER_PREFERENCES, MemoryType.PROJECT_HISTORY],
                "tools": ["design_gameplay_mechanics", "create_progression_system", "balance_game_systems"],
                "model_preference": "gpt-4o"  # Good balance for design thinking
            },
            AgentRole.ORCHESTRATOR: {
                "specializations": ["task_coordination", "workflow_optimization", "quality_assurance"],
                "memory_types": list(MemoryType),  # Access to all memory types
                "tools": ["coordinate_agents", "optimize_workflow", "validate_output"],
                "model_preference": "gpt-5"  # Best for complex orchestration
            }
        }
        
        return capabilities.get(self.role, {})
    
    async def execute_task(self, task: AgentTask) -> Dict[str, Any]:
        """Execute a task using agent's specialized capabilities."""
        
        logger.info(f"{self.role.value} agent executing task: {task.task_id}")
        
        # Retrieve relevant memories
        relevant_memories = await self.memory.retrieve_memories(
            query=task.description,
            project_context=task.context.get("project_context")
        )
        
        # Build context from memories
        memory_context = self._build_memory_context(relevant_memories)
        
        # Execute task with memory-enhanced context
        result = await self._execute_with_memory(task, memory_context)
        
        # Store important results in memory
        if result.get("status") == "success":
            await self._store_task_result(task, result)
        
        # Update task history
        task.result = result
        task.status = "completed" if result.get("status") == "success" else "failed"
        self.task_history.append(task)
        
        return result
    
    def _build_memory_context(self, memories: List[AgentMemory]) -> str:
        """Build context string from relevant memories."""
        
        if not memories:
            return ""
        
        context_parts = ["=== RELEVANT MEMORY CONTEXT ==="]
        
        for memory in memories[:5]:  # Limit to top 5 most relevant
            context_parts.append(f"\n[{memory.memory_type.value}] ({memory.relevance_score:.2f} similarity)")
            context_parts.append(f"Tags: {', '.join(memory.tags)}")
            context_parts.append(f"Content: {memory.content}")
            context_parts.append("---")
        
        return "\n".join(context_parts)
    
    async def _execute_with_memory(self, task: AgentTask, memory_context: str) -> Dict[str, Any]:
        """Execute task with memory-enhanced prompts."""
        
        model = self.capabilities.get("model_preference", "gpt-4o")
        
        # Build enhanced prompt with memory context
        enhanced_prompt = f"""
        You are a {self.role.value} agent specializing in: {', '.join(self.capabilities.get('specializations', []))}
        
        {memory_context}
        
        === CURRENT TASK ===
        Task: {task.description}
        Context: {json.dumps(task.context, indent=2)}
        
        Using your specialization and the relevant memory context above, execute this task with high quality and consistency.
        Ensure your output aligns with previous project decisions and maintains continuity.
        
        Respond with detailed, actionable results in JSON format.
        """
        
        try:
            response = await self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": f"You are an expert {self.role.value} for game development."},
                    {"role": "user", "content": enhanced_prompt}
                ],
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            result["status"] = "success"
            result["agent_role"] = self.role.value
            result["model_used"] = model
            
            return result
            
        except Exception as e:
            logger.error(f"Task execution failed for {self.role.value}: {e}")
            return {
                "status": "error",
                "error": str(e),
                "agent_role": self.role.value
            }
    
    async def _store_task_result(self, task: AgentTask, result: Dict[str, Any]):
        """Store important task results in memory."""
        
        # Determine what to remember based on agent role
        memory_content = self._extract_memorable_content(task, result)
        
        if memory_content:
            memory_type = self._determine_memory_type(task.task_type)
            project_context = task.context.get("project_context", "general")
            
            await self.memory.store_memory(
                content=memory_content,
                memory_type=memory_type,
                project_context=project_context,
                tags=[self.role.value, task.task_type]
            )
    
    def _extract_memorable_content(self, task: AgentTask, result: Dict[str, Any]) -> Optional[str]:
        """Extract important content to remember."""
        
        if self.role == AgentRole.WORLD_ARCHITECT:
            return result.get("world_description") or result.get("lore_content")
        elif self.role == AgentRole.NARRATIVE_WEAVER:
            return result.get("character_description") or result.get("story_outline")
        elif self.role == AgentRole.ASSET_CREATOR:
            return result.get("visual_description") or result.get("style_guide")
        elif self.role == AgentRole.CODE_ENGINEER:
            return result.get("code_pattern") or result.get("architecture_decision")
        elif self.role == AgentRole.GAME_DESIGNER:
            return result.get("design_decision") or result.get("mechanics_explanation")
        
        return None
    
    def _determine_memory_type(self, task_type: str) -> MemoryType:
        """Determine appropriate memory type based on task."""
        
        type_mapping = {
            "world_building": MemoryType.WORLD_LORE,
            "character_creation": MemoryType.CHARACTER_SHEETS,
            "visual_design": MemoryType.VISUAL_STYLE,
            "code_generation": MemoryType.CODE_PATTERNS,
            "mechanics_design": MemoryType.PLAYER_PREFERENCES
        }
        
        return type_mapping.get(task_type, MemoryType.PROJECT_HISTORY)


class AgentOrchestrator:
    """Orchestrates multiple agents for complex game development workflows."""
    
    def __init__(self, openai_client: AsyncOpenAI):
        self.client = openai_client
        self.memory = IntelligentMemorySystem(openai_client)
        self.agents: Dict[AgentRole, GameDevelopmentAgent] = {}
        self.active_workflows: Dict[str, List[AgentTask]] = {}
        
    async def initialize(self):
        """Initialize the orchestrator and all agents."""
        
        await self.memory.initialize()
        
        # Create specialized agents
        for role in AgentRole:
            if role != AgentRole.ORCHESTRATOR:  # Don't create recursive orchestrator
                self.agents[role] = GameDevelopmentAgent(role, self.client, self.memory)
        
        logger.info(f"Initialized {len(self.agents)} specialized agents")
    
    async def execute_complex_workflow(
        self,
        workflow_description: str,
        project_context: str,
        scope: str = "full_game"
    ) -> Dict[str, Any]:
        """Execute a complex multi-agent workflow."""
        
        logger.info(f"Starting complex workflow: {workflow_description}")
        
        # Analyze workflow and create task breakdown
        tasks = await self._analyze_and_plan_workflow(workflow_description, project_context, scope)
        
        # Execute tasks with intelligent coordination
        results = await self._coordinate_task_execution(tasks, project_context)
        
        # Synthesize final output
        final_result = await self._synthesize_results(results, workflow_description, project_context)
        
        return final_result
    
    async def _analyze_and_plan_workflow(
        self, 
        description: str, 
        project_context: str, 
        scope: str
    ) -> List[AgentTask]:
        """Use GPT-5 to intelligently break down workflow into agent tasks."""
        
        planning_prompt = f"""
        You are an expert game development project manager. Analyze this workflow and break it down into specific tasks for specialized agents.
        
        Workflow Description: {description}
        Project Context: {project_context}
        Scope: {scope}
        
        Available Agent Roles:
        - world_architect: Designs worlds, lore, geography, factions
        - narrative_weaver: Creates stories, dialogue, characters, plots
        - asset_creator: Generates visual/audio assets, sprites, UI
        - code_engineer: Writes engine code, systems, architecture
        - game_designer: Designs mechanics, balance, progression
        
        Create a detailed task breakdown with:
        1. Task dependencies (which tasks must complete before others)
        2. Required agent roles for each task
        3. Priority levels (1-10)
        4. Specific context needed for each task
        
        Return JSON with tasks array containing:
        {{
            "task_id": "unique_id",
            "task_type": "category",
            "description": "detailed description",
            "required_agents": ["agent_role1"],
            "dependencies": ["task_id_dependency"],
            "priority": 8,
            "context": {{additional_context}}
        }}
        """
        
        response = await self.client.chat.completions.create(
            model="gpt-5",  # Use GPT-5 for complex planning
            messages=[{"role": "user", "content": planning_prompt}],
            response_format={"type": "json_object"}
        )
        
        plan_data = json.loads(response.choices[0].message.content)
        
        tasks = []
        for task_data in plan_data.get("tasks", []):
            task = AgentTask(
                task_id=task_data["task_id"],
                task_type=task_data["task_type"],
                description=task_data["description"],
                required_agents=[AgentRole(role) for role in task_data["required_agents"]],
                dependencies=task_data["dependencies"],
                priority=task_data["priority"],
                context={**task_data["context"], "project_context": project_context},
                status="pending"
            )
            tasks.append(task)
        
        logger.info(f"Planned {len(tasks)} tasks for workflow execution")
        return tasks
    
    async def _coordinate_task_execution(
        self, 
        tasks: List[AgentTask], 
        project_context: str
    ) -> Dict[str, Any]:
        """Intelligently coordinate task execution across agents."""
        
        results = {}
        completed_tasks = set()
        
        # Sort tasks by priority and dependencies
        remaining_tasks = sorted(tasks, key=lambda t: (-t.priority, len(t.dependencies)))
        
        while remaining_tasks:
            # Find tasks ready to execute (dependencies met)
            ready_tasks = [
                task for task in remaining_tasks 
                if all(dep in completed_tasks for dep in task.dependencies)
            ]
            
            if not ready_tasks:
                logger.error("Circular dependencies detected in task workflow")
                break
            
            # Execute ready tasks (can be parallelized for independent tasks)
            batch_results = await self._execute_task_batch(ready_tasks[:3])  # Limit concurrent tasks
            
            # Process results
            for task_id, result in batch_results.items():
                results[task_id] = result
                completed_tasks.add(task_id)
                
                # Remove completed task from remaining
                remaining_tasks = [t for t in remaining_tasks if t.task_id != task_id]
        
        return results
    
    async def _execute_task_batch(self, tasks: List[AgentTask]) -> Dict[str, Any]:
        """Execute a batch of tasks in parallel."""
        
        task_coroutines = []
        
        for task in tasks:
            # Assign to appropriate agent (use first required agent for now)
            agent_role = task.required_agents[0] if task.required_agents else AgentRole.ORCHESTRATOR
            agent = self.agents.get(agent_role)
            
            if agent:
                task_coroutines.append(agent.execute_task(task))
            else:
                logger.error(f"No agent available for role: {agent_role}")
        
        # Execute tasks in parallel
        if task_coroutines:
            batch_results = await asyncio.gather(*task_coroutines, return_exceptions=True)
            
            # Map results back to task IDs
            result_map = {}
            for i, result in enumerate(batch_results):
                task_id = tasks[i].task_id
                if isinstance(result, Exception):
                    result_map[task_id] = {"status": "error", "error": str(result)}
                else:
                    result_map[task_id] = result
            
            return result_map
        
        return {}
    
    async def _synthesize_results(
        self, 
        task_results: Dict[str, Any], 
        original_description: str, 
        project_context: str
    ) -> Dict[str, Any]:
        """Synthesize all task results into final cohesive output."""
        
        synthesis_prompt = f"""
        You are synthesizing the results of a complex game development workflow.
        
        Original Request: {original_description}
        Project Context: {project_context}
        
        Task Results:
        {json.dumps(task_results, indent=2)}
        
        Create a comprehensive final result that:
        1. Integrates all successful task outputs
        2. Identifies any gaps or failures
        3. Provides next steps or recommendations
        4. Ensures coherent, cohesive game development output
        
        Return a structured JSON response with the synthesized game development assets.
        """
        
        response = await self.client.chat.completions.create(
            model="gpt-5",  # Use GPT-5 for complex synthesis
            messages=[{"role": "user", "content": synthesis_prompt}],
            response_format={"type": "json_object"}
        )
        
        final_result = json.loads(response.choices[0].message.content)
        final_result["orchestration_summary"] = {
            "total_tasks": len(task_results),
            "successful_tasks": len([r for r in task_results.values() if r.get("status") == "success"]),
            "project_context": project_context,
            "agent_coordination": "multi_agent_orchestrated"
        }
        
        return final_result
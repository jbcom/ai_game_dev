"""Advanced seed data system for contextual prompt enhancement."""

import asyncio
import json
import time
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, Literal
from enum import Enum
from dataclasses import dataclass, asdict
from datetime import datetime

import aiofiles

from ai_game_dev.config import settings
from ai_game_dev.logging_config import get_logger
from ai_game_dev.utils import ensure_directory_exists

logger = get_logger(__name__, component="seed_system")


class SeedType(str, Enum):
    """Types of seed data for different purposes."""
    VISUAL_REFERENCE = "visual_reference"
    STYLE_GUIDE = "style_guide"
    CHARACTER_SHEET = "character_sheet"
    WORLD_LORE = "world_lore"
    GAMEPLAY_MECHANIC = "gameplay_mechanic"
    COLOR_PALETTE = "color_palette"
    ASSET_TEMPLATE = "asset_template"
    NARRATIVE_CONTEXT = "narrative_context"
    TECHNICAL_SPEC = "technical_spec"


class SeedPriority(str, Enum):
    """Priority levels for seed consumption."""
    CRITICAL = "critical"    # Always include in prompts
    HIGH = "high"           # Include when relevant
    MEDIUM = "medium"       # Include if space allows
    LOW = "low"             # Background context only


@dataclass
class SeedData:
    """Structured seed data for prompt enhancement."""
    id: str
    seed_type: SeedType
    priority: SeedPriority
    title: str
    content: str
    tags: List[str]
    metadata: Dict[str, Any]
    created_at: float
    expires_at: Optional[float] = None
    usage_count: int = 0
    max_usage: Optional[int] = None
    project_context: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SeedData':
        """Create from dictionary."""
        return cls(**data)
    
    def is_expired(self) -> bool:
        """Check if seed has expired."""
        if self.expires_at is None:
            return False
        return time.time() > self.expires_at
    
    def is_usage_exhausted(self) -> bool:
        """Check if seed usage limit is reached."""
        if self.max_usage is None:
            return False
        return self.usage_count >= self.max_usage
    
    def can_be_consumed(self) -> bool:
        """Check if seed can be consumed."""
        return not (self.is_expired() or self.is_usage_exhausted())


class SeedQueue:
    """Manages queued seed data for consumption."""
    
    def __init__(self):
        self.seeds: Dict[str, SeedData] = {}
        self.seeds_dir = settings.cache_dir / "seeds"
        self.queue_file = self.seeds_dir / "seed_queue.json"
        
    async def initialize(self):
        """Initialize the seed queue."""
        await ensure_directory_exists(self.seeds_dir)
        await self._load_seeds()
    
    async def add_seed(
        self,
        seed_type: SeedType,
        title: str,
        content: str,
        priority: SeedPriority = SeedPriority.MEDIUM,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        expires_in_hours: Optional[int] = None,
        max_usage: Optional[int] = None,
        project_context: Optional[str] = None
    ) -> str:
        """Add seed data to the queue."""
        
        seed_id = str(uuid.uuid4())
        expires_at = None
        
        if expires_in_hours is not None:
            expires_at = time.time() + (expires_in_hours * 3600)
        
        seed = SeedData(
            id=seed_id,
            seed_type=seed_type,
            priority=priority,
            title=title,
            content=content,
            tags=tags or [],
            metadata=metadata or {},
            created_at=time.time(),
            expires_at=expires_at,
            max_usage=max_usage,
            project_context=project_context
        )
        
        self.seeds[seed_id] = seed
        await self._save_seeds()
        
        logger.info(f"Added seed: {title} ({seed_type.value})")
        return seed_id
    
    async def consume_seeds(
        self,
        query_tags: Optional[List[str]] = None,
        project_context: Optional[str] = None,
        max_seeds: int = 10,
        priority_filter: Optional[List[SeedPriority]] = None
    ) -> List[SeedData]:
        """Consume relevant seeds for prompt enhancement."""
        
        # Filter available seeds
        available_seeds = []
        
        for seed in self.seeds.values():
            if not seed.can_be_consumed():
                continue
                
            # Priority filter
            if priority_filter and seed.priority not in priority_filter:
                continue
                
            # Project context filter
            if project_context and seed.project_context:
                if seed.project_context != project_context:
                    continue
            
            # Tag matching
            if query_tags:
                if not any(tag in seed.tags for tag in query_tags):
                    continue
            
            available_seeds.append(seed)
        
        # Sort by priority and relevance
        priority_order = {
            SeedPriority.CRITICAL: 4,
            SeedPriority.HIGH: 3,
            SeedPriority.MEDIUM: 2,
            SeedPriority.LOW: 1
        }
        
        available_seeds.sort(
            key=lambda s: (priority_order.get(s.priority, 0), -s.created_at),
            reverse=True
        )
        
        # Limit to max_seeds
        consumed_seeds = available_seeds[:max_seeds]
        
        # Update usage count
        for seed in consumed_seeds:
            seed.usage_count += 1
        
        if consumed_seeds:
            await self._save_seeds()
            logger.info(f"Consumed {len(consumed_seeds)} seeds for prompt enhancement")
        
        return consumed_seeds
    
    async def get_seed(self, seed_id: str) -> Optional[SeedData]:
        """Get specific seed by ID."""
        return self.seeds.get(seed_id)
    
    async def remove_seed(self, seed_id: str) -> bool:
        """Remove seed from queue."""
        if seed_id in self.seeds:
            del self.seeds[seed_id]
            await self._save_seeds()
            logger.info(f"Removed seed: {seed_id}")
            return True
        return False
    
    async def list_seeds(
        self,
        seed_type: Optional[SeedType] = None,
        project_context: Optional[str] = None,
        active_only: bool = True
    ) -> List[SeedData]:
        """List seeds with optional filtering."""
        
        results = []
        
        for seed in self.seeds.values():
            if active_only and not seed.can_be_consumed():
                continue
                
            if seed_type and seed.seed_type != seed_type:
                continue
                
            if project_context and seed.project_context != project_context:
                continue
                
            results.append(seed)
        
        return results
    
    async def cleanup_expired(self) -> int:
        """Remove expired and exhausted seeds."""
        
        initial_count = len(self.seeds)
        
        # Remove expired/exhausted seeds
        to_remove = []
        for seed_id, seed in self.seeds.items():
            if not seed.can_be_consumed():
                to_remove.append(seed_id)
        
        for seed_id in to_remove:
            del self.seeds[seed_id]
        
        if to_remove:
            await self._save_seeds()
            
        removed_count = len(to_remove)
        if removed_count > 0:
            logger.info(f"Cleaned up {removed_count} expired/exhausted seeds")
        
        return removed_count
    
    async def _load_seeds(self):
        """Load seeds from disk."""
        if not self.queue_file.exists():
            return
            
        try:
            async with aiofiles.open(self.queue_file, 'r') as f:
                content = await f.read()
                data = json.loads(content)
                
                for seed_data in data:
                    seed = SeedData.from_dict(seed_data)
                    self.seeds[seed.id] = seed
                    
            logger.info(f"Loaded {len(self.seeds)} seeds from disk")
            
        except Exception as e:
            logger.error(f"Failed to load seeds: {e}")
    
    async def _save_seeds(self):
        """Save seeds to disk."""
        try:
            data = [seed.to_dict() for seed in self.seeds.values()]
            
            async with aiofiles.open(self.queue_file, 'w') as f:
                await f.write(json.dumps(data, indent=2))
                
        except Exception as e:
            logger.error(f"Failed to save seeds: {e}")


class SeedEnhancedPromptGenerator:
    """Generates enhanced prompts using seed data."""
    
    def __init__(self, seed_queue: SeedQueue):
        self.seed_queue = seed_queue
    
    async def enhance_prompt(
        self,
        base_prompt: str,
        context_tags: Optional[List[str]] = None,
        project_context: Optional[str] = None,
        max_seeds: int = 5,
        include_priority: Optional[List[SeedPriority]] = None
    ) -> Dict[str, Any]:
        """Enhance a prompt with relevant seed data."""
        
        # Consume relevant seeds
        consumed_seeds = await self.seed_queue.consume_seeds(
            query_tags=context_tags,
            project_context=project_context,
            max_seeds=max_seeds,
            priority_filter=include_priority
        )
        
        if not consumed_seeds:
            return {
                "enhanced_prompt": base_prompt,
                "seeds_used": [],
                "enhancement_applied": False
            }
        
        # Build enhanced prompt
        prompt_parts = [base_prompt]
        
        # Group seeds by type for better organization
        seeds_by_type = {}
        for seed in consumed_seeds:
            if seed.seed_type not in seeds_by_type:
                seeds_by_type[seed.seed_type] = []
            seeds_by_type[seed.seed_type].append(seed)
        
        # Add seed context
        if SeedType.STYLE_GUIDE in seeds_by_type:
            style_context = []
            for seed in seeds_by_type[SeedType.STYLE_GUIDE]:
                style_context.append(f"Style: {seed.content}")
            prompt_parts.extend(style_context)
        
        if SeedType.COLOR_PALETTE in seeds_by_type:
            for seed in seeds_by_type[SeedType.COLOR_PALETTE]:
                prompt_parts.append(f"Color palette: {seed.content}")
        
        if SeedType.CHARACTER_SHEET in seeds_by_type:
            for seed in seeds_by_type[SeedType.CHARACTER_SHEET]:
                prompt_parts.append(f"Character reference: {seed.content}")
        
        if SeedType.WORLD_LORE in seeds_by_type:
            for seed in seeds_by_type[SeedType.WORLD_LORE]:
                prompt_parts.append(f"World context: {seed.content}")
        
        if SeedType.TECHNICAL_SPEC in seeds_by_type:
            for seed in seeds_by_type[SeedType.TECHNICAL_SPEC]:
                prompt_parts.append(f"Technical requirement: {seed.content}")
        
        # Add any other seed types as general context
        other_contexts = []
        for seed_type, seeds in seeds_by_type.items():
            if seed_type not in [SeedType.STYLE_GUIDE, SeedType.COLOR_PALETTE, 
                               SeedType.CHARACTER_SHEET, SeedType.WORLD_LORE, 
                               SeedType.TECHNICAL_SPEC]:
                for seed in seeds:
                    other_contexts.append(f"{seed.title}: {seed.content}")
        
        prompt_parts.extend(other_contexts)
        
        enhanced_prompt = ". ".join(prompt_parts)
        
        return {
            "enhanced_prompt": enhanced_prompt,
            "seeds_used": [seed.to_dict() for seed in consumed_seeds],
            "enhancement_applied": True,
            "seed_count": len(consumed_seeds)
        }
    
    async def create_contextual_prompt(
        self,
        task_description: str,
        asset_type: str,
        project_context: Optional[str] = None
    ) -> str:
        """Create a contextual prompt for specific asset generation."""
        
        # Determine relevant tags based on asset type
        context_tags = []
        
        if "sprite" in asset_type.lower():
            context_tags.extend(["character", "sprite", "2d", "game"])
        elif "ui" in asset_type.lower():
            context_tags.extend(["ui", "interface", "button", "panel"])
        elif "tile" in asset_type.lower():
            context_tags.extend(["tilemap", "environment", "world"])
        elif "particle" in asset_type.lower():
            context_tags.extend(["effects", "particles", "vfx"])
        elif "material" in asset_type.lower():
            context_tags.extend(["material", "texture", "3d", "pbr"])
        
        # Enhance with seeds
        enhancement = await self.enhance_prompt(
            base_prompt=task_description,
            context_tags=context_tags,
            project_context=project_context,
            max_seeds=3
        )
        
        return enhancement["enhanced_prompt"]


# Global seed queue instance
seed_queue = SeedQueue()
prompt_enhancer = SeedEnhancedPromptGenerator(seed_queue)


async def initialize_seed_system():
    """Initialize the global seed system."""
    await seed_queue.initialize()
    logger.info("Seed system initialized")
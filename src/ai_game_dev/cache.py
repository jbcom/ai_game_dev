"""Cache initialization for AI Game Dev platform."""
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

def initialize_sqlite_cache_and_memory():
    """Initialize cache directories for the platform.
    
    Creates necessary cache directories for:
    - LLM response caching
    - Generated asset caching
    - Project metadata caching
    """
    # Main cache directory
    cache_dir = Path.home() / ".cache" / "ai-game-dev"
    
    # Create subdirectories
    subdirs = [
        cache_dir / "llm-cache",      # LLM response cache
        cache_dir / "assets",         # Generated assets cache
        cache_dir / "projects",       # Project metadata
        cache_dir / "templates",      # Rendered templates
    ]
    
    for subdir in subdirs:
        subdir.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Ensured cache directory exists: {subdir}")
    
    logger.info(f"Initialized cache system at: {cache_dir}")
    
    return cache_dir
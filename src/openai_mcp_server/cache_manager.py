"""Advanced caching system with TTL, size limits, and cleanup strategies."""

import asyncio
import json
import time
from pathlib import Path
from typing import Any, Optional

import aiofiles

from openai_mcp_server.config import settings
from openai_mcp_server.exceptions import CacheError
from openai_mcp_server.logging_config import get_logger
from openai_mcp_server.metrics import metrics

logger = get_logger(__name__, component="cache", operation="management")


class TTLCache:
    """Time-To-Live cache with automatic cleanup."""
    
    def __init__(self, default_ttl: int = 3600, max_size: int = 1000):
        self.default_ttl = default_ttl
        self.max_size = max_size
        self.cache: dict[str, dict[str, Any]] = {}
        self.access_times: dict[str, float] = {}
        self._cleanup_task: Optional[asyncio.Task] = None
        self._initialized = False
    
    def _start_cleanup_task(self) -> None:
        """Start the automatic cleanup task."""
        try:
            if not self._initialized and (self._cleanup_task is None or self._cleanup_task.done()):
                self._cleanup_task = asyncio.create_task(self._cleanup_loop())
                self._initialized = True
        except RuntimeError:
            # No event loop running, cleanup will be started on first async operation
            pass
    
    async def _cleanup_loop(self) -> None:
        """Periodic cleanup of expired entries."""
        while True:
            try:
                await asyncio.sleep(300)  # Cleanup every 5 minutes
                await self.cleanup_expired()
                await self.cleanup_lru()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Cache cleanup error: {e}")
    
    async def cleanup_expired(self) -> None:
        """Remove expired cache entries."""
        current_time = time.time()
        expired_keys = []
        
        for key, entry in self.cache.items():
            if current_time > entry.get("expires_at", float("inf")):
                expired_keys.append(key)
        
        for key in expired_keys:
            await self.delete(key)
        
        if expired_keys:
            logger.info(f"Cleaned up {len(expired_keys)} expired cache entries")
    
    async def cleanup_lru(self) -> None:
        """Remove least recently used entries if cache is too large."""
        if len(self.cache) <= self.max_size:
            return
        
        # Sort by access time and remove oldest entries
        sorted_keys = sorted(
            self.access_times.items(),
            key=lambda x: x[1]
        )
        
        keys_to_remove = len(self.cache) - self.max_size
        for key, _ in sorted_keys[:keys_to_remove]:
            await self.delete(key)
        
        logger.info(f"Cleaned up {keys_to_remove} LRU cache entries")
    
    async def get(self, key: str) -> Any | None:
        """Get value from cache."""
        # Ensure cleanup task is started
        if not self._initialized:
            self._start_cleanup_task()
        
        if key not in self.cache:
            return None
        
        entry = self.cache[key]
        current_time = time.time()
        
        # Check if expired
        if current_time > entry.get("expires_at", float("inf")):
            await self.delete(key)
            return None
        
        # Update access time
        self.access_times[key] = current_time
        
        return entry["value"]
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache with TTL."""
        ttl = ttl or self.default_ttl
        current_time = time.time()
        
        self.cache[key] = {
            "value": value,
            "created_at": current_time,
            "expires_at": current_time + ttl,
        }
        self.access_times[key] = current_time
    
    async def delete(self, key: str) -> bool:
        """Delete value from cache."""
        if key in self.cache:
            del self.cache[key]
            self.access_times.pop(key, None)
            return True
        return False
    
    async def clear(self) -> None:
        """Clear all cache entries."""
        self.cache.clear()
        self.access_times.clear()
    
    def stats(self) -> dict[str, Any]:
        """Get cache statistics."""
        current_time = time.time()
        expired_count = sum(
            1 for entry in self.cache.values()
            if current_time > entry.get("expires_at", float("inf"))
        )
        
        return {
            "total_entries": len(self.cache),
            "expired_entries": expired_count,
            "max_size": self.max_size,
            "default_ttl": self.default_ttl,
        }


class FileCache:
    """File-based cache with metadata tracking."""
    
    def __init__(self, cache_dir: Path):
        self.cache_dir = cache_dir
        self.metadata_file = cache_dir / ".cache_metadata.json"
        self.metadata: dict[str, dict[str, Any]] = {}
        self._load_metadata()
    
    def _load_metadata(self) -> None:
        """Load cache metadata from disk."""
        try:
            if self.metadata_file.exists():
                with open(self.metadata_file, 'r') as f:
                    self.metadata = json.load(f)
        except Exception as e:
            logger.warning(f"Failed to load cache metadata: {e}")
            self.metadata = {}
    
    async def _save_metadata(self) -> None:
        """Save cache metadata to disk."""
        try:
            async with aiofiles.open(self.metadata_file, 'w') as f:
                await f.write(json.dumps(self.metadata, indent=2))
        except Exception as e:
            logger.error(f"Failed to save cache metadata: {e}")
    
    async def get_file_path(self, key: str) -> Path | None:
        """Get file path for cached content."""
        if key not in self.metadata:
            return None
        
        file_path = self.cache_dir / self.metadata[key]["filename"]
        
        # Check if file exists and is not expired
        if not file_path.exists():
            await self.delete(key)
            return None
        
        # Check TTL
        if "expires_at" in self.metadata[key]:
            if time.time() > self.metadata[key]["expires_at"]:
                await self.delete(key)
                return None
        
        # Update access time
        self.metadata[key]["last_accessed"] = time.time()
        await self._save_metadata()
        
        return file_path
    
    async def store_file(
        self, 
        key: str, 
        file_path: Path, 
        ttl: Optional[int] = None,
        metadata: Optional[dict[str, Any]] = None
    ) -> None:
        """Store file in cache with metadata."""
        current_time = time.time()
        
        entry = {
            "filename": file_path.name,
            "created_at": current_time,
            "last_accessed": current_time,
            "size_bytes": file_path.stat().st_size if file_path.exists() else 0,
            "metadata": metadata or {},
        }
        
        if ttl:
            entry["expires_at"] = current_time + ttl
        
        self.metadata[key] = entry
        await self._save_metadata()
    
    async def delete(self, key: str) -> bool:
        """Delete cached file and metadata."""
        if key not in self.metadata:
            return False
        
        # Remove file
        file_path = self.cache_dir / self.metadata[key]["filename"]
        try:
            if file_path.exists():
                file_path.unlink()
        except Exception as e:
            logger.warning(f"Failed to delete cache file {file_path}: {e}")
        
        # Remove metadata
        del self.metadata[key]
        await self._save_metadata()
        
        return True
    
    async def cleanup_expired(self) -> int:
        """Clean up expired cache files."""
        current_time = time.time()
        expired_keys = []
        
        for key, entry in self.metadata.items():
            if "expires_at" in entry and current_time > entry["expires_at"]:
                expired_keys.append(key)
        
        for key in expired_keys:
            await self.delete(key)
        
        return len(expired_keys)
    
    def stats(self) -> dict[str, Any]:
        """Get cache statistics."""
        total_size = sum(entry.get("size_bytes", 0) for entry in self.metadata.values())
        current_time = time.time()
        expired_count = sum(
            1 for entry in self.metadata.values()
            if "expires_at" in entry and current_time > entry["expires_at"]
        )
        
        return {
            "total_files": len(self.metadata),
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "expired_files": expired_count,
        }


class CacheManager:
    """Unified cache manager for memory and file caches."""
    
    def __init__(self):
        self.memory_cache = TTLCache(default_ttl=3600, max_size=1000)
        self.file_cache = FileCache(settings.cache_dir)
    
    async def get_from_memory(self, key: str) -> Any | None:
        """Get value from memory cache."""
        result = await self.memory_cache.get(key)
        metrics.record_operation("cache_memory_access", 0.001, cache_hit=result is not None)
        return result
    
    async def set_in_memory(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in memory cache."""
        await self.memory_cache.set(key, value, ttl)
    
    async def get_file_path(self, key: str) -> Path | None:
        """Get file path from file cache."""
        result = await self.file_cache.get_file_path(key)
        metrics.record_operation("cache_file_access", 0.001, cache_hit=result is not None)
        return result
    
    async def store_file(self, key: str, file_path: Path, **kwargs) -> None:
        """Store file in file cache."""
        await self.file_cache.store_file(key, file_path, **kwargs)
    
    async def cleanup_all(self) -> dict[str, int]:
        """Clean up all caches."""
        await self.memory_cache.cleanup_expired()
        await self.memory_cache.cleanup_lru()
        
        expired_files = await self.file_cache.cleanup_expired()
        
        return {
            "expired_files_cleaned": expired_files,
        }
    
    def get_stats(self) -> dict[str, Any]:
        """Get comprehensive cache statistics."""
        return {
            "memory_cache": self.memory_cache.stats(),
            "file_cache": self.file_cache.stats(),
        }


# Global cache manager
cache_manager = CacheManager()
import asyncio
import json
import pickle
import hashlib
from pathlib import Path
from typing import Any, Dict, Optional, Union
from datetime import datetime, timedelta
import sqlite3
from contextlib import asynccontextmanager

class CacheManager:
    def __init__(self, cache_dir: Optional[Path] = None):
        self.cache_dir = cache_dir or Path.home() / ".ai-game-dev" / "cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        self.db_path = self.cache_dir / "cache.db"
        self._init_database()
        
        # In-memory cache for frequently accessed items
        self.memory_cache: Dict[str, Any] = {}
        self.memory_cache_ttl: Dict[str, datetime] = {}
        self.max_memory_items = 100

    def _init_database(self):
        """Initialize SQLite database for persistent cache."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS cache_entries (
                    key TEXT PRIMARY KEY,
                    value BLOB,
                    created_at TEXT,
                    expires_at TEXT,
                    access_count INTEGER DEFAULT 0,
                    last_accessed TEXT
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_expires_at ON cache_entries(expires_at)
            """)
            conn.commit()

    def _generate_key(self, *args, **kwargs) -> str:
        """Generate a cache key from arguments."""
        key_data = {
            'args': args,
            'kwargs': sorted(kwargs.items())
        }
        key_str = json.dumps(key_data, sort_keys=True, default=str)
        return hashlib.sha256(key_str.encode()).hexdigest()

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        # Check memory cache first
        if key in self.memory_cache:
            if key in self.memory_cache_ttl:
                if datetime.now() > self.memory_cache_ttl[key]:
                    del self.memory_cache[key]
                    del self.memory_cache_ttl[key]
                else:
                    return self.memory_cache[key]
        
        # Check persistent cache
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT value, expires_at FROM cache_entries 
                    WHERE key = ?
                """, (key,))
                
                row = cursor.fetchone()
                if row:
                    value_blob, expires_at = row
                    
                    # Check if expired
                    if expires_at and datetime.fromisoformat(expires_at) < datetime.now():
                        await self.delete(key)
                        return None
                    
                    # Update access statistics
                    conn.execute("""
                        UPDATE cache_entries 
                        SET access_count = access_count + 1, last_accessed = ?
                        WHERE key = ?
                    """, (datetime.now().isoformat(), key))
                    conn.commit()
                    
                    # Deserialize value
                    value = pickle.loads(value_blob)
                    
                    # Add to memory cache
                    self._add_to_memory_cache(key, value)
                    
                    return value
                    
        except Exception:
            # If there's any error with persistent cache, continue without it
            pass
        
        return None

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache with optional TTL in seconds."""
        expires_at = None
        if ttl:
            expires_at = datetime.now() + timedelta(seconds=ttl)
        
        # Add to memory cache
        self._add_to_memory_cache(key, value, expires_at)
        
        # Add to persistent cache
        try:
            value_blob = pickle.dumps(value)
            
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO cache_entries 
                    (key, value, created_at, expires_at, access_count, last_accessed)
                    VALUES (?, ?, ?, ?, 0, ?)
                """, (
                    key, 
                    value_blob, 
                    datetime.now().isoformat(),
                    expires_at.isoformat() if expires_at else None,
                    datetime.now().isoformat()
                ))
                conn.commit()
                
        except Exception:
            # If there's any error with persistent cache, continue without it
            pass

    async def delete(self, key: str) -> None:
        """Delete value from cache."""
        # Remove from memory cache
        if key in self.memory_cache:
            del self.memory_cache[key]
        if key in self.memory_cache_ttl:
            del self.memory_cache_ttl[key]
        
        # Remove from persistent cache
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("DELETE FROM cache_entries WHERE key = ?", (key,))
                conn.commit()
        except Exception:
            pass

    async def clear(self) -> None:
        """Clear all cache entries."""
        self.memory_cache.clear()
        self.memory_cache_ttl.clear()
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("DELETE FROM cache_entries")
                conn.commit()
        except Exception:
            pass

    async def cleanup_expired(self) -> None:
        """Remove expired entries from cache."""
        now = datetime.now()
        
        # Clean memory cache
        expired_keys = []
        for key, expires_at in self.memory_cache_ttl.items():
            if now > expires_at:
                expired_keys.append(key)
        
        for key in expired_keys:
            del self.memory_cache[key]
            del self.memory_cache_ttl[key]
        
        # Clean persistent cache
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    DELETE FROM cache_entries 
                    WHERE expires_at IS NOT NULL AND expires_at < ?
                """, (now.isoformat(),))
                conn.commit()
        except Exception:
            pass

    def _add_to_memory_cache(self, key: str, value: Any, expires_at: Optional[datetime] = None):
        """Add item to memory cache with LRU eviction."""
        # Remove oldest items if cache is full
        if len(self.memory_cache) >= self.max_memory_items:
            # Remove 10% of oldest items
            items_to_remove = max(1, len(self.memory_cache) // 10)
            # Sort by access time (newest first)
            sorted_items = sorted(
                self.memory_cache_ttl.items(), 
                key=lambda x: x[1], 
                reverse=True
            )
            
            for key_to_remove, _ in sorted_items[-items_to_remove:]:
                if key_to_remove in self.memory_cache:
                    del self.memory_cache[key_to_remove]
                if key_to_remove in self.memory_cache_ttl:
                    del self.memory_cache_ttl[key_to_remove]
        
        self.memory_cache[key] = value
        if expires_at:
            self.memory_cache_ttl[key] = expires_at

    async def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        memory_size = len(self.memory_cache)
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT 
                        COUNT(*) as total_entries,
                        COUNT(CASE WHEN expires_at IS NULL THEN 1 END) as permanent_entries,
                        COUNT(CASE WHEN expires_at IS NOT NULL THEN 1 END) as temporary_entries,
                        AVG(access_count) as avg_access_count
                    FROM cache_entries
                """)
                row = cursor.fetchone()
                
                if row:
                    total, permanent, temporary, avg_access = row
                    persistent_stats = {
                        "total_entries": total or 0,
                        "permanent_entries": permanent or 0,
                        "temporary_entries": temporary or 0,
                        "avg_access_count": float(avg_access or 0)
                    }
                else:
                    persistent_stats = {
                        "total_entries": 0,
                        "permanent_entries": 0,
                        "temporary_entries": 0,
                        "avg_access_count": 0.0
                    }
                    
        except Exception:
            persistent_stats = {
                "total_entries": 0,
                "permanent_entries": 0,
                "temporary_entries": 0,
                "avg_access_count": 0.0
            }
        
        return {
            "memory_cache_size": memory_size,
            "memory_cache_limit": self.max_memory_items,
            "persistent_cache": persistent_stats
        }

def cache_result(ttl: Optional[int] = None, key_prefix: str = ""):
    """Decorator to cache function results."""
    def decorator(func):
        cache_manager = CacheManager()
        
        async def async_wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = key_prefix + cache_manager._generate_key(func.__name__, *args, **kwargs)
            
            # Try to get from cache
            cached_result = await cache_manager.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = await func(*args, **kwargs)
            await cache_manager.set(cache_key, result, ttl)
            return result
        
        def sync_wrapper(*args, **kwargs):
            # For sync functions, run in event loop
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(async_wrapper(*args, **kwargs))
            finally:
                loop.close()
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    
    return decorator

# Global cache manager instance
global_cache = CacheManager()
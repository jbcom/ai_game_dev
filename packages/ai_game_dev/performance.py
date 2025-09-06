"""
Performance optimization utilities for AI game development.
Includes caching, batching, and monitoring capabilities.
"""

import asyncio
import time
import functools
from typing import Any, Dict, List, Callable, Optional
from collections import defaultdict
from dataclasses import dataclass, field
import json
from pathlib import Path

from .logging_config import get_logger
from .cache_manager import CacheManager

logger = get_logger(__name__, component="performance")


@dataclass
class PerformanceMetrics:
    """Performance metrics tracking."""
    
    operation_counts: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    operation_times: Dict[str, List[float]] = field(default_factory=lambda: defaultdict(list))
    cache_hits: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    cache_misses: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    api_calls: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    errors: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    
    def record_operation(self, operation: str, duration: float):
        """Record an operation and its duration."""
        self.operation_counts[operation] += 1
        self.operation_times[operation].append(duration)
    
    def record_cache_hit(self, cache_type: str):
        """Record a cache hit."""
        self.cache_hits[cache_type] += 1
    
    def record_cache_miss(self, cache_type: str):
        """Record a cache miss."""
        self.cache_misses[cache_type] += 1
    
    def record_api_call(self, api: str):
        """Record an API call."""
        self.api_calls[api] += 1
    
    def record_error(self, error_type: str):
        """Record an error."""
        self.errors[error_type] += 1
    
    def get_average_time(self, operation: str) -> float:
        """Get average time for an operation."""
        times = self.operation_times.get(operation, [])
        return sum(times) / len(times) if times else 0.0
    
    def get_cache_hit_rate(self, cache_type: str) -> float:
        """Get cache hit rate for a cache type."""
        hits = self.cache_hits.get(cache_type, 0)
        misses = self.cache_misses.get(cache_type, 0)
        total = hits + misses
        return hits / total if total > 0 else 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary."""
        return {
            'operation_counts': dict(self.operation_counts),
            'average_times': {op: self.get_average_time(op) for op in self.operation_times},
            'cache_hit_rates': {ct: self.get_cache_hit_rate(ct) for ct in self.cache_hits},
            'api_calls': dict(self.api_calls),
            'errors': dict(self.errors),
            'timestamp': time.time()
        }


class PerformanceMonitor:
    """Global performance monitoring system."""
    
    _instance: Optional['PerformanceMonitor'] = None
    
    def __init__(self):
        self.metrics = PerformanceMetrics()
        self.enabled = True
        self._start_time = time.time()
    
    @classmethod
    def get_instance(cls) -> 'PerformanceMonitor':
        """Get singleton instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def time_operation(self, operation_name: str):
        """Decorator to time operations."""
        def decorator(func: Callable):
            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                if not self.enabled:
                    return await func(*args, **kwargs)
                
                start_time = time.time()
                try:
                    result = await func(*args, **kwargs)
                    duration = time.time() - start_time
                    self.metrics.record_operation(operation_name, duration)
                    return result
                except Exception as e:
                    self.metrics.record_error(type(e).__name__)
                    raise
            
            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs):
                if not self.enabled:
                    return func(*args, **kwargs)
                
                start_time = time.time()
                try:
                    result = func(*args, **kwargs)
                    duration = time.time() - start_time
                    self.metrics.record_operation(operation_name, duration)
                    return result
                except Exception as e:
                    self.metrics.record_error(type(e).__name__)
                    raise
            
            return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
        return decorator
    
    def get_report(self) -> Dict[str, Any]:
        """Get comprehensive performance report."""
        uptime = time.time() - self._start_time
        
        report = self.metrics.to_dict()
        report['uptime_seconds'] = uptime
        report['operations_per_second'] = {
            op: count / uptime 
            for op, count in self.metrics.operation_counts.items()
        }
        
        return report
    
    def save_report(self, filepath: Path):
        """Save performance report to file."""
        report = self.get_report()
        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"Performance report saved to {filepath}")


class BatchProcessor:
    """Optimized batch processing for AI operations."""
    
    def __init__(self, batch_size: int = 10, max_concurrent: int = 5):
        self.batch_size = batch_size
        self.max_concurrent = max_concurrent
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.monitor = PerformanceMonitor.get_instance()
    
    @PerformanceMonitor.get_instance().time_operation("batch_process")
    async def process_batch(self, items: List[Any], processor: Callable) -> List[Any]:
        """Process items in optimized batches."""
        results = []
        
        # Split into batches
        batches = [
            items[i:i + self.batch_size] 
            for i in range(0, len(items), self.batch_size)
        ]
        
        # Process batches concurrently
        tasks = [
            self._process_single_batch(batch, processor)
            for batch in batches
        ]
        
        batch_results = await asyncio.gather(*tasks)
        
        # Flatten results
        for batch_result in batch_results:
            results.extend(batch_result)
        
        logger.info(f"Processed {len(items)} items in {len(batches)} batches")
        return results
    
    async def _process_single_batch(self, batch: List[Any], processor: Callable) -> List[Any]:
        """Process a single batch with concurrency control."""
        async with self.semaphore:
            tasks = [processor(item) for item in batch]
            return await asyncio.gather(*tasks)


class ResourcePool:
    """Pool of reusable resources to reduce allocation overhead."""
    
    def __init__(self, factory: Callable, max_size: int = 10):
        self.factory = factory
        self.max_size = max_size
        self.pool = asyncio.Queue(maxsize=max_size)
        self.created_count = 0
        self.monitor = PerformanceMonitor.get_instance()
    
    async def acquire(self) -> Any:
        """Acquire a resource from the pool."""
        try:
            # Try to get from pool first
            resource = self.pool.get_nowait()
            self.monitor.metrics.record_cache_hit("resource_pool")
            return resource
        except asyncio.QueueEmpty:
            # Create new resource if pool is empty
            if self.created_count < self.max_size:
                resource = await self.factory()
                self.created_count += 1
                self.monitor.metrics.record_cache_miss("resource_pool")
                return resource
            else:
                # Wait for resource to become available
                resource = await self.pool.get()
                self.monitor.metrics.record_cache_hit("resource_pool")
                return resource
    
    async def release(self, resource: Any):
        """Release a resource back to the pool."""
        try:
            self.pool.put_nowait(resource)
        except asyncio.QueueFull:
            # Pool is full, resource will be garbage collected
            pass


class APIRateLimiter:
    """Rate limiter for API calls to prevent hitting limits."""
    
    def __init__(self, calls_per_minute: int = 60):
        self.calls_per_minute = calls_per_minute
        self.call_times = []
        self.lock = asyncio.Lock()
    
    async def wait_if_needed(self):
        """Wait if we need to respect rate limits."""
        async with self.lock:
            now = time.time()
            
            # Remove calls older than 1 minute
            self.call_times = [t for t in self.call_times if now - t < 60]
            
            # Check if we need to wait
            if len(self.call_times) >= self.calls_per_minute:
                wait_time = 60 - (now - self.call_times[0])
                if wait_time > 0:
                    logger.info(f"Rate limit reached, waiting {wait_time:.2f} seconds")
                    await asyncio.sleep(wait_time)
            
            # Record this call
            self.call_times.append(now)


def optimize_for_production():
    """Apply production optimizations."""
    
    # Enable performance monitoring
    monitor = PerformanceMonitor.get_instance()
    monitor.enabled = True
    
    # Configure cache for production
    cache = CacheManager.get_instance()
    cache.set_max_memory_usage(1024 * 1024 * 1024)  # 1GB
    cache.set_cleanup_interval(300)  # 5 minutes
    
    # Set up periodic performance reports
    async def save_periodic_reports():
        while True:
            await asyncio.sleep(3600)  # Every hour
            report_path = Path(f"performance_report_{int(time.time())}.json")
            monitor.save_report(report_path)
    
    # Start background task for reports
    asyncio.create_task(save_periodic_reports())
    
    logger.info("Production optimizations applied")


# Global instances
performance_monitor = PerformanceMonitor.get_instance()
batch_processor = BatchProcessor()
api_rate_limiter = APIRateLimiter()


# Decorators for easy use
def monitor_performance(operation_name: str):
    """Decorator to monitor function performance."""
    return performance_monitor.time_operation(operation_name)


def rate_limited(calls_per_minute: int = 60):
    """Decorator to rate limit function calls."""
    limiter = APIRateLimiter(calls_per_minute)
    
    def decorator(func: Callable):
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            await limiter.wait_if_needed()
            return await func(*args, **kwargs)
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            # For sync functions, run the async wait in a new event loop
            import asyncio
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            loop.run_until_complete(limiter.wait_if_needed())
            return func(*args, **kwargs)
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    
    return decorator
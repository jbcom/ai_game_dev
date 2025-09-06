"""Performance metrics and monitoring for the MCP server."""

import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Callable

from openai_mcp_server.logging_config import get_logger

logger = get_logger(__name__, component="metrics", operation="tracking")


@dataclass
class OperationMetrics:
    """Metrics for a specific operation."""
    total_calls: int = 0
    total_duration: float = 0.0
    success_count: int = 0
    error_count: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    recent_durations: deque[float] = field(default_factory=lambda: deque(maxlen=100))
    
    @property
    def average_duration(self) -> float:
        """Average operation duration."""
        return self.total_duration / max(self.total_calls, 1)
    
    @property
    def success_rate(self) -> float:
        """Success rate as percentage."""
        return (self.success_count / max(self.total_calls, 1)) * 100
    
    @property
    def cache_hit_rate(self) -> float:
        """Cache hit rate as percentage."""
        total_cache_ops = self.cache_hits + self.cache_misses
        return (self.cache_hits / max(total_cache_ops, 1)) * 100
    
    @property
    def recent_average_duration(self) -> float:
        """Average duration of recent operations."""
        if not self.recent_durations:
            return 0.0
        return sum(self.recent_durations) / len(self.recent_durations)


class MetricsCollector:
    """Collects and manages performance metrics."""
    
    def __init__(self):
        self.operations: dict[str, OperationMetrics] = defaultdict(OperationMetrics)
        self.start_time = datetime.now()
        self.api_usage = defaultdict(int)
        self.error_counts = defaultdict(int)
    
    def record_operation(
        self, 
        operation: str, 
        duration: float, 
        success: bool = True,
        cache_hit: bool | None = None
    ) -> None:
        """Record metrics for an operation."""
        metrics = self.operations[operation]
        metrics.total_calls += 1
        metrics.total_duration += duration
        metrics.recent_durations.append(duration)
        
        if success:
            metrics.success_count += 1
        else:
            metrics.error_count += 1
        
        if cache_hit is True:
            metrics.cache_hits += 1
        elif cache_hit is False:
            metrics.cache_misses += 1
        
        logger.debug(
            f"Operation recorded: {operation}",
            extra={
                "operation": operation,
                "duration": duration,
                "success": success,
                "cache_hit": cache_hit
            }
        )
    
    def record_api_usage(self, model: str, tokens_used: int = 1) -> None:
        """Record API usage."""
        self.api_usage[model] += tokens_used
    
    def record_error(self, error_type: str) -> None:
        """Record error occurrence."""
        self.error_counts[error_type] += 1
    
    def get_summary(self) -> dict[str, Any]:
        """Get comprehensive metrics summary."""
        uptime = datetime.now() - self.start_time
        
        return {
            "uptime_seconds": uptime.total_seconds(),
            "uptime_human": str(uptime),
            "operations": {
                name: {
                    "total_calls": metrics.total_calls,
                    "average_duration": round(metrics.average_duration, 3),
                    "recent_average_duration": round(metrics.recent_average_duration, 3),
                    "success_rate": round(metrics.success_rate, 2),
                    "cache_hit_rate": round(metrics.cache_hit_rate, 2),
                    "total_duration": round(metrics.total_duration, 3),
                    "error_count": metrics.error_count,
                }
                for name, metrics in self.operations.items()
            },
            "api_usage": dict(self.api_usage),
            "error_counts": dict(self.error_counts),
        }
    
    def reset(self) -> None:
        """Reset all metrics."""
        self.operations.clear()
        self.start_time = datetime.now()
        self.api_usage.clear()
        self.error_counts.clear()


# Global metrics collector
metrics = MetricsCollector()


def track_operation(operation_name: str):
    """Decorator to track operation metrics."""
    def decorator(func: Callable) -> Callable:
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            success = True
            cache_hit = None
            
            try:
                result = await func(*args, **kwargs)
                
                # Extract cache info if available
                if isinstance(result, dict):
                    if result.get("status") == "cached":
                        cache_hit = True
                    elif result.get("status") in ["generated", "analyzed"]:
                        cache_hit = False
                
                return result
            except Exception as e:
                success = False
                metrics.record_error(type(e).__name__)
                raise
            finally:
                duration = time.time() - start_time
                metrics.record_operation(operation_name, duration, success, cache_hit)
        
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            success = True
            
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                success = False
                metrics.record_error(type(e).__name__)
                raise
            finally:
                duration = time.time() - start_time
                metrics.record_operation(operation_name, duration, success)
        
        # Return appropriate wrapper based on whether function is async
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator
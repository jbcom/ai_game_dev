"""Batch processing capabilities for bulk operations."""

import asyncio
from typing import Any, Callable, TypeVar

from openai_mcp_server.logging_config import get_logger
from openai_mcp_server.metrics import track_operation

logger = get_logger(__name__, component="batch", operation="processing")

T = TypeVar('T')
R = TypeVar('R')


class BatchProcessor:
    """Handles batch processing of operations with concurrency control."""
    
    def __init__(self, max_concurrent: int = 5, batch_size: int = 10):
        self.max_concurrent = max_concurrent
        self.batch_size = batch_size
        self.semaphore = asyncio.Semaphore(max_concurrent)
    
    @track_operation("batch_process")
    async def process_batch(
        self,
        items: list[T],
        processor: Callable[[T], Any],
        progress_callback: Callable[[int, int], None] | None = None
    ) -> list[dict[str, Any]]:
        """Process a batch of items with concurrency control."""
        results = []
        total_items = len(items)
        
        # Process items in chunks to control memory usage
        for i in range(0, total_items, self.batch_size):
            chunk = items[i:i + self.batch_size]
            chunk_results = await self._process_chunk(chunk, processor)
            results.extend(chunk_results)
            
            if progress_callback:
                progress_callback(min(i + self.batch_size, total_items), total_items)
        
        return results
    
    async def _process_chunk(
        self,
        chunk: list[T],
        processor: Callable[[T], Any]
    ) -> list[dict[str, Any]]:
        """Process a chunk of items concurrently."""
        async def process_item(item: T) -> dict[str, Any]:
            async with self.semaphore:
                try:
                    if asyncio.iscoroutinefunction(processor):
                        result = await processor(item)
                    else:
                        result = processor(item)
                    
                    return {
                        "status": "success",
                        "item": item,
                        "result": result
                    }
                except Exception as e:
                    logger.error(f"Batch item processing failed: {e}")
                    return {
                        "status": "error",
                        "item": item,
                        "error": str(e)
                    }
        
        tasks = [process_item(item) for item in chunk]
        return await asyncio.gather(*tasks)


class ImageBatchGenerator:
    """Specialized batch processor for image generation."""
    
    def __init__(self, image_generator):
        self.image_generator = image_generator
        self.batch_processor = BatchProcessor(max_concurrent=3, batch_size=5)
    
    @track_operation("batch_image_generation")
    async def generate_images_batch(
        self,
        prompts: list[str],
        size: str = "1024x1024",
        quality: str = "standard",
        progress_callback: Callable[[int, int], None] | None = None
    ) -> dict[str, Any]:
        """Generate multiple images in batch."""
        async def generate_single(prompt: str) -> dict[str, Any]:
            return await self.image_generator.generate_image(
                prompt=prompt,
                size=size,
                quality=quality
            )
        
        results = await self.batch_processor.process_batch(
            prompts, generate_single, progress_callback
        )
        
        successful = [r for r in results if r["status"] == "success"]
        failed = [r for r in results if r["status"] == "error"]
        
        return {
            "total_requested": len(prompts),
            "successful": len(successful),
            "failed": len(failed),
            "success_rate": (len(successful) / len(prompts)) * 100,
            "results": results
        }


class ModelBatchGenerator:
    """Specialized batch processor for 3D model generation."""
    
    def __init__(self, model_generator):
        self.model_generator = model_generator
        self.batch_processor = BatchProcessor(max_concurrent=2, batch_size=3)
    
    @track_operation("batch_model_generation")
    async def generate_models_batch(
        self,
        specifications: list[dict[str, str]],
        progress_callback: Callable[[int, int], None] | None = None
    ) -> dict[str, Any]:
        """Generate multiple 3D models in batch."""
        async def generate_single(spec: dict[str, str]) -> dict[str, Any]:
            return await self.model_generator.generate_3d_model_structured(
                description=spec["description"],
                model_name=spec["model_name"],
                optimization_target=spec.get("optimization_target", "game")
            )
        
        results = await self.batch_processor.process_batch(
            specifications, generate_single, progress_callback
        )
        
        successful = [r for r in results if r["status"] == "success"]
        failed = [r for r in results if r["status"] == "error"]
        
        return {
            "total_requested": len(specifications),
            "successful": len(successful),
            "failed": len(failed),
            "success_rate": (len(successful) / len(specifications)) * 100,
            "results": results
        }
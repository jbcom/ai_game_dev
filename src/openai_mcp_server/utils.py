"""Utility functions for the MCP server."""

import hashlib
import json
from pathlib import Path
from typing import Any

import aiofiles

def generate_content_hash(content: str) -> str:
    """Generate a consistent hash for content-based caching."""
    return hashlib.sha256(content.encode()).hexdigest()[:16]

def get_image_path(images_dir: Path, prompt: str, size: str, quality: str) -> Path:
    """Generate deterministic file path for image based on parameters."""
    content = f"{prompt}|{size}|{quality}"
    hash_id = generate_content_hash(content)
    return images_dir / f"img_{hash_id}.png"

async def load_verification_cache(cache_path: Path) -> dict[str, Any]:
    """Load the verification cache from disk."""
    if cache_path.exists():
        async with aiofiles.open(cache_path, 'r') as f:
            content = await f.read()
            return json.loads(content) if content else {}
    return {}

async def save_verification_cache(cache_path: Path, cache: dict[str, Any]) -> None:
    """Save the verification cache to disk."""
    async with aiofiles.open(cache_path, 'w') as f:
        await f.write(json.dumps(cache, indent=2))

async def ensure_directory_exists(directory: Path) -> None:
    """Ensure directory exists, creating it if necessary."""
    if not directory.exists():
        directory.mkdir(parents=True, exist_ok=True)
"""
Freesound API client for downloading CC-licensed audio assets.
"""

import asyncio
import aiohttp
from pathlib import Path
from typing import Any


class FreesoundClient:
    """Client for accessing Freesound.org API."""
    
    def __init__(self, api_key: str | None = None):
        self.api_key = api_key
        self.base_url = "https://freesound.org/apiv2"
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def search_sounds(
        self,
        query: str,
        license: str = "Creative Commons 0",
        duration_max: float = 10.0,
        limit: int = 10
    ) -> list[dict[str, Any]]:
        """Search for sounds with specified criteria."""
        
        if not self.session:
            raise RuntimeError("Client not initialized. Use 'async with' context manager.")
        
        params = {
            "query": query,
            "license": license,
            "duration": f"[0 TO {duration_max}]",
            "fields": "id,name,url,description,license,duration,download",
            "page_size": limit
        }
        
        if self.api_key:
            params["token"] = self.api_key
        
        async with self.session.get(f"{self.base_url}/search/text/", params=params) as response:
            if response.status == 200:
                data = await response.json()
                return data.get("results", [])
            else:
                return []
    
    async def download_sound(
        self,
        sound_id: int,
        output_path: Path,
        quality: str = "mp3-hq"
    ) -> Path | None:
        """Download a sound file."""
        
        if not self.api_key:
            raise ValueError("API key required for downloading sounds")
        
        if not self.session:
            raise RuntimeError("Client not initialized. Use 'async with' context manager.")
        
        # Get download URL
        params = {"token": self.api_key}
        
        async with self.session.get(
            f"{self.base_url}/sounds/{sound_id}/download/",
            params=params,
            allow_redirects=False
        ) as response:
            if response.status == 302:
                download_url = response.headers.get("Location")
            else:
                return None
        
        # Download the file
        async with self.session.get(download_url) as response:
            if response.status == 200:
                output_path.parent.mkdir(parents=True, exist_ok=True)
                
                with open(output_path, 'wb') as f:
                    async for chunk in response.content.iter_chunked(8192):
                        f.write(chunk)
                
                return output_path
        
        return None
    
    async def get_game_audio_pack(
        self,
        categories: list[str],
        output_dir: Path | None = None
    ) -> dict[str, list[Path]]:
        """Download a curated pack of game audio assets."""
        
        if output_dir is None:
            output_dir = Path("game_audio_pack")
        output_dir.mkdir(exist_ok=True)
        
        audio_pack = {}
        
        category_queries = {
            "ui": ["button click", "menu beep", "notification", "error sound"],
            "ambient": ["forest ambient", "wind", "water", "cave ambient"],
            "effects": ["explosion", "laser", "magic spell", "footstep"],
            "music": ["8bit music", "chiptune", "game music loop"]
        }
        
        for category in categories:
            if category not in category_queries:
                continue
            
            category_dir = output_dir / category
            category_dir.mkdir(exist_ok=True)
            
            category_files = []
            
            for query in category_queries[category]:
                sounds = await self.search_sounds(query, limit=2)
                
                for sound in sounds:
                    sound_id = sound.get("id")
                    if sound_id:
                        filename = f"{sound.get('name', sound_id)}.mp3"
                        # Clean filename
                        filename = "".join(c for c in filename if c.isalnum() or c in "._- ")
                        
                        output_path = category_dir / filename
                        downloaded_path = await self.download_sound(sound_id, output_path)
                        
                        if downloaded_path:
                            category_files.append(downloaded_path)
            
            audio_pack[category] = category_files
        
        return audio_pack
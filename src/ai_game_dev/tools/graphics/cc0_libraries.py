"""
CC0 (Creative Commons Zero) licensed asset libraries integration.
"""

import asyncio
import aiohttp
from pathlib import Path
from typing import Any
import json


class CC0Libraries:
    """Access and manage CC0 licensed asset libraries."""
    
    def __init__(self):
        self.session = None
        self.known_libraries = {
            "kenney": {
                "base_url": "https://www.kenney.nl/assets",
                "description": "High-quality game assets and sprites",
                "categories": ["ui", "sprites", "textures", "audio"]
            },
            "opengameart": {
                "base_url": "https://opengameart.org",
                "description": "Community-driven game art repository",
                "categories": ["sprites", "textures", "audio", "models"]
            },
            "freepik": {
                "base_url": "https://www.freepik.com",
                "description": "Free vectors and graphics",
                "categories": ["vectors", "icons", "illustrations"]
            }
        }
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def search_assets(
        self,
        query: str,
        category: str = "all",
        license_filter: str = "cc0"
    ) -> list[dict[str, Any]]:
        """Search for CC0 assets across multiple libraries."""
        
        results = []
        
        # Simulate search results with curated CC0 assets
        asset_database = {
            "ui": [
                {"name": "Button Pack", "description": "Complete UI button set", "source": "kenney"},
                {"name": "Menu Icons", "description": "Game menu icon collection", "source": "opengameart"},
                {"name": "Progress Bars", "description": "Health and progress bar sprites", "source": "kenney"}
            ],
            "sprites": [
                {"name": "Character Pack", "description": "RPG character sprites", "source": "opengameart"},
                {"name": "Enemy Set", "description": "Fantasy enemy sprites", "source": "kenney"},
                {"name": "Platformer Tiles", "description": "2D platformer tile set", "source": "kenney"}
            ],
            "textures": [
                {"name": "Wood Textures", "description": "Seamless wood patterns", "source": "freepik"},
                {"name": "Stone Patterns", "description": "Rock and stone textures", "source": "opengameart"},
                {"name": "Metal Surfaces", "description": "Metallic texture pack", "source": "kenney"}
            ]
        }
        
        # Filter by category and query
        search_categories = [category] if category != "all" else asset_database.keys()
        
        for cat in search_categories:
            if cat in asset_database:
                for asset in asset_database[cat]:
                    if query.lower() in asset["name"].lower() or query.lower() in asset["description"].lower():
                        asset["category"] = cat
                        asset["license"] = "CC0"
                        asset["download_url"] = f"https://example.com/download/{asset['name'].replace(' ', '_').lower()}.zip"
                        results.append(asset)
        
        return results
    
    async def download_asset_pack(
        self,
        asset_info: dict[str, Any],
        output_dir: Path | None = None
    ) -> Path | None:
        """Download a CC0 asset pack."""
        
        if output_dir is None:
            output_dir = Path("cc0_assets")
        output_dir.mkdir(exist_ok=True)
        
        # Simulate download (in real implementation, would download from actual URLs)
        pack_name = asset_info.get("name", "unknown").replace(" ", "_").lower()
        pack_path = output_dir / f"{pack_name}.zip"
        
        # Create a placeholder file with metadata
        metadata = {
            "name": asset_info.get("name"),
            "description": asset_info.get("description"),
            "source": asset_info.get("source"),
            "license": "CC0",
            "category": asset_info.get("category"),
            "download_date": "2025-01-01"
        }
        
        with open(pack_path.with_suffix('.json'), 'w') as f:
            json.dump(metadata, f, indent=2)
        
        return pack_path
    
    def get_recommended_assets(self, game_type: str) -> list[dict[str, Any]]:
        """Get recommended CC0 assets for specific game types."""
        
        recommendations = {
            "2d_platformer": [
                {"name": "Platformer Character Pack", "category": "sprites", "priority": "high"},
                {"name": "Jump and Run Tiles", "category": "textures", "priority": "high"},
                {"name": "Collectible Icons", "category": "ui", "priority": "medium"},
                {"name": "Background Layers", "category": "textures", "priority": "medium"}
            ],
            "rpg": [
                {"name": "Fantasy Character Set", "category": "sprites", "priority": "high"},
                {"name": "Medieval UI Pack", "category": "ui", "priority": "high"},
                {"name": "Dungeon Tiles", "category": "textures", "priority": "high"},
                {"name": "Equipment Icons", "category": "ui", "priority": "medium"}
            ],
            "puzzle": [
                {"name": "Puzzle Pieces", "category": "sprites", "priority": "high"},
                {"name": "Clean UI Set", "category": "ui", "priority": "high"},
                {"name": "Geometric Patterns", "category": "textures", "priority": "medium"}
            ],
            "arcade": [
                {"name": "Retro Sprites", "category": "sprites", "priority": "high"},
                {"name": "Neon UI Elements", "category": "ui", "priority": "high"},
                {"name": "Space Backgrounds", "category": "textures", "priority": "medium"}
            ]
        }
        
        return recommendations.get(game_type, [])
    
    async def create_asset_collection(
        self,
        game_description: str,
        output_dir: Path | None = None
    ) -> dict[str, list[Path]]:
        """Create a curated collection of CC0 assets for a game."""
        
        if output_dir is None:
            output_dir = Path("game_asset_collection")
        output_dir.mkdir(exist_ok=True)
        
        # Analyze game description to determine asset needs
        game_type = self._analyze_game_type(game_description)
        recommended_assets = self.get_recommended_assets(game_type)
        
        collection = {}
        
        for asset_rec in recommended_assets:
            category = asset_rec["category"]
            if category not in collection:
                collection[category] = []
            
            # Search for assets matching the recommendation
            search_results = await self.search_assets(asset_rec["name"], category)
            
            for result in search_results[:2]:  # Limit to 2 assets per recommendation
                downloaded_path = await self.download_asset_pack(result, output_dir / category)
                if downloaded_path:
                    collection[category].append(downloaded_path)
        
        return collection
    
    def _analyze_game_type(self, description: str) -> str:
        """Analyze game description to determine type."""
        
        description_lower = description.lower()
        
        if any(word in description_lower for word in ["platform", "jump", "run", "mario"]):
            return "2d_platformer"
        elif any(word in description_lower for word in ["rpg", "adventure", "quest", "fantasy"]):
            return "rpg"
        elif any(word in description_lower for word in ["puzzle", "match", "brain", "logic"]):
            return "puzzle"
        elif any(word in description_lower for word in ["arcade", "retro", "classic", "score"]):
            return "arcade"
        else:
            return "generic"
    
    def get_library_info(self, library_name: str) -> dict[str, Any] | None:
        """Get information about a specific CC0 library."""
        return self.known_libraries.get(library_name)
    
    def list_available_libraries(self) -> list[str]:
        """List all available CC0 asset libraries."""
        return list(self.known_libraries.keys())
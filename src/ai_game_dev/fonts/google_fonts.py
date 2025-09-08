"""
Google Fonts integration for game typography.
"""

import asyncio
import aiohttp
from pathlib import Path
from typing import Any
import json


class GoogleFonts:
    """Google Fonts API integration for game typography."""
    
    def __init__(self, api_key: str | None = None):
        self.api_key = api_key
        self.base_url = "https://www.googleapis.com/webfonts/v1/webfonts"
        self.download_base = "https://fonts.googleapis.com/css2"
        self.session = None
        self._font_cache = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def get_available_fonts(self, category: str | None = None) -> list[dict[str, Any]]:
        """Get list of available Google Fonts."""
        
        if self._font_cache is None:
            await self._load_font_cache()
        
        fonts = self._font_cache
        
        if category:
            fonts = [font for font in fonts if font.get("category") == category]
        
        return fonts
    
    async def _load_font_cache(self):
        """Load font information from Google Fonts API or cache."""
        
        if not self.session:
            raise RuntimeError("Client not initialized. Use 'async with' context manager.")
        
        params = {}
        if self.api_key:
            params["key"] = self.api_key
        
        try:
            async with self.session.get(self.base_url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    self._font_cache = data.get("items", [])
                else:
                    # Fallback to popular game fonts
                    self._font_cache = self._get_fallback_fonts()
        except Exception:
            self._font_cache = self._get_fallback_fonts()
    
    def _get_fallback_fonts(self) -> list[dict[str, Any]]:
        """Get fallback list of popular game fonts."""
        
        return [
            {
                "family": "Press Start 2P",
                "category": "display",
                "variants": ["regular"],
                "description": "Perfect for retro arcade games"
            },
            {
                "family": "Orbitron",
                "category": "sans-serif", 
                "variants": ["regular", "bold"],
                "description": "Futuristic sci-fi style"
            },
            {
                "family": "Creepster",
                "category": "display",
                "variants": ["regular"],
                "description": "Horror and spooky games"
            },
            {
                "family": "Bangers",
                "category": "display",
                "variants": ["regular"],
                "description": "Comic book and action games"
            },
            {
                "family": "Fredoka One",
                "category": "display",
                "variants": ["regular"],
                "description": "Friendly and casual games"
            },
            {
                "family": "Black Ops One",
                "category": "display",
                "variants": ["regular"],
                "description": "Military and action games"
            },
            {
                "family": "Permanent Marker",
                "category": "handwriting",
                "variants": ["regular"],
                "description": "Casual and artistic games"
            },
            {
                "family": "Righteous",
                "category": "display",
                "variants": ["regular"],
                "description": "Modern and clean display"
            }
        ]
    
    async def search_fonts(
        self,
        query: str,
        category: str | None = None,
        sort: str = "popularity"
    ) -> list[dict[str, Any]]:
        """Search for fonts matching criteria."""
        
        all_fonts = await self.get_available_fonts(category)
        
        # Filter by query
        matching_fonts = []
        for font in all_fonts:
            family = font.get("family", "").lower()
            if query.lower() in family:
                matching_fonts.append(font)
        
        # Sort results
        if sort == "popularity":
            # Simulate popularity sorting
            matching_fonts.sort(key=lambda x: x.get("family"), reverse=False)
        elif sort == "alpha":
            matching_fonts.sort(key=lambda x: x.get("family"))
        
        return matching_fonts
    
    async def get_fonts_for_game_style(self, game_style: str) -> list[dict[str, Any]]:
        """Get recommended fonts for specific game styles."""
        
        style_recommendations = {
            "retro": ["Press Start 2P", "Orbitron", "VT323"],
            "horror": ["Creepster", "Nosifer", "Butcherman"],
            "fantasy": ["Cinzel", "MedievalSharp", "Uncial Antiqua"],
            "sci-fi": ["Orbitron", "Exo", "Audiowide"],
            "casual": ["Fredoka One", "Comfortaa", "Quicksand"],
            "action": ["Bangers", "Black Ops One", "Bungee"],
            "modern": ["Roboto", "Open Sans", "Lato"],
            "artistic": ["Permanent Marker", "Kalam", "Caveat"]
        }
        
        font_families = style_recommendations.get(game_style, ["Roboto"])
        all_fonts = await self.get_available_fonts()
        
        recommended_fonts = []
        for font in all_fonts:
            if font.get("family") in font_families:
                recommended_fonts.append(font)
        
        return recommended_fonts
    
    async def download_font(
        self,
        font_family: str,
        output_dir: Path | None = None,
        variants: list[str] | None = None
    ) -> Path | None:
        """Download a Google Font."""
        
        if output_dir is None:
            output_dir = Path("fonts")
        output_dir.mkdir(exist_ok=True)
        
        if variants is None:
            variants = ["regular"]
        
        # Build font URL
        font_query = font_family.replace(" ", "+")
        if len(variants) > 1:
            weight_query = ":wght@" + ";".join(variants)
            font_query += weight_query
        
        font_url = f"{self.download_base}?family={font_query}&display=swap"
        
        if not self.session:
            raise RuntimeError("Client not initialized. Use 'async with' context manager.")
        
        try:
            # Get CSS with font URLs
            async with self.session.get(font_url) as response:
                if response.status == 200:
                    css_content = await response.text()
                    
                    # Save CSS file
                    css_path = output_dir / f"{font_family.replace(' ', '_').lower()}.css"
                    with open(css_path, 'w') as f:
                        f.write(css_content)
                    
                    # Create metadata file
                    metadata = {
                        "family": font_family,
                        "variants": variants,
                        "css_url": font_url,
                        "download_date": "2025-01-01"
                    }
                    
                    metadata_path = output_dir / f"{font_family.replace(' ', '_').lower()}_metadata.json"
                    with open(metadata_path, 'w') as f:
                        json.dump(metadata, f, indent=2)
                    
                    return css_path
        
        except Exception as e:
            print(f"Error downloading font {font_family}: {e}")
        
        return None
    
    async def create_font_pack(
        self,
        game_description: str,
        output_dir: Path | None = None
    ) -> dict[str, Path]:
        """Create a curated font pack for a game."""
        
        if output_dir is None:
            output_dir = Path("game_font_pack")
        output_dir.mkdir(exist_ok=True)
        
        # Analyze game description for style
        game_style = self._analyze_game_style(game_description)
        recommended_fonts = await self.get_fonts_for_game_style(game_style)
        
        font_pack = {}
        
        # Download top 3 recommended fonts
        for font in recommended_fonts[:3]:
            font_family = font.get("family")
            if font_family:
                downloaded_path = await self.download_font(
                    font_family,
                    output_dir,
                    font.get("variants", ["regular"])
                )
                if downloaded_path:
                    font_pack[font_family] = downloaded_path
        
        # Always include a fallback system font reference
        system_fonts = {
            "serif": "Times New Roman, serif",
            "sans-serif": "Arial, sans-serif", 
            "monospace": "Courier New, monospace"
        }
        
        for category, font_stack in system_fonts.items():
            fallback_path = output_dir / f"system_{category}.css"
            with open(fallback_path, 'w') as f:
                f.write(f"/* System {category} fallback */\n")
                f.write(f".system-{category} {{ font-family: {font_stack}; }}\n")
            font_pack[f"system_{category}"] = fallback_path
        
        return font_pack
    
    def _analyze_game_style(self, description: str) -> str:
        """Analyze game description to determine typography style."""
        
        description_lower = description.lower()
        
        style_keywords = {
            "retro": ["retro", "8bit", "pixel", "arcade", "classic"],
            "horror": ["horror", "scary", "dark", "spooky", "zombie"],
            "fantasy": ["fantasy", "medieval", "magic", "dragon", "quest"],
            "sci-fi": ["sci-fi", "space", "future", "robot", "alien"],
            "casual": ["casual", "family", "puzzle", "relaxing", "cute"],
            "action": ["action", "fast", "intense", "combat", "shooter"],
            "artistic": ["artistic", "creative", "abstract", "unique", "stylized"]
        }
        
        for style, keywords in style_keywords.items():
            if any(keyword in description_lower for keyword in keywords):
                return style
        
        return "modern"  # Default fallback
    
    def get_font_pairing_suggestions(self, primary_font: str) -> list[str]:
        """Get font pairing suggestions for a primary font."""
        
        pairings = {
            "Press Start 2P": ["Roboto Mono", "Source Code Pro"],
            "Orbitron": ["Roboto", "Open Sans"],
            "Creepster": ["Roboto Slab", "Crimson Text"],
            "Bangers": ["Open Sans", "Lato"],
            "Fredoka One": ["Nunito", "Quicksand"],
            "Black Ops One": ["Roboto Condensed", "Oswald"],
            "Permanent Marker": ["Open Sans", "Roboto"],
            "Righteous": ["Lato", "Source Sans Pro"]
        }
        
        return pairings.get(primary_font, ["Roboto", "Open Sans"])
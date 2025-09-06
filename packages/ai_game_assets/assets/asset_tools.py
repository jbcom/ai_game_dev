"""
Unified asset tools for visual content generation and management.
"""

import asyncio
from pathlib import Path
from typing import Any, Literal
import json
from dataclasses import dataclass

from ai_game_assets.assets.cc0_libraries import CC0Libraries
from ai_game_assets.assets.google_fonts import GoogleFonts
from ai_game_assets.assets.archive_seeder import ArchiveSeeder


@dataclass
class AssetRequest:
    """Request for asset generation/curation."""
    game_description: str
    asset_types: list[str]
    style_preferences: str = ""
    max_assets_per_type: int = 5
    include_cc0: bool = True
    include_fonts: bool = True
    include_archived: bool = False


@dataclass
class AssetPackage:
    """Complete asset package result."""
    graphics_assets: dict[str, list[dict[str, Any]]]
    font_assets: dict[str, Any]
    archived_assets: dict[str, Any]
    metadata: dict[str, Any]
    summary: str


class AssetTools:
    """Unified tools for comprehensive asset management."""
    
    def __init__(self, google_fonts_api_key: str | None = None):
        self.google_fonts_api_key = google_fonts_api_key
        self._cc0_client = None
        self._fonts_client = None
        self._archive_client = None
    
    async def __aenter__(self):
        self._cc0_client = CC0Libraries()
        await self._cc0_client.__aenter__()
        
        self._fonts_client = GoogleFonts(self.google_fonts_api_key)
        await self._fonts_client.__aenter__()
        
        self._archive_client = ArchiveSeeder()
        await self._archive_client.__aenter__()
        
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._cc0_client:
            await self._cc0_client.__aexit__(exc_type, exc_val, exc_tb)
        if self._fonts_client:
            await self._fonts_client.__aexit__(exc_type, exc_val, exc_tb)
        if self._archive_client:
            await self._archive_client.__aexit__(exc_type, exc_val, exc_tb)
    
    async def create_complete_asset_package(
        self,
        game_description: str,
        asset_types: list[str],
        style_preferences: str = "",
        max_assets_per_type: int = 5,
        output_dir: Path | None = None
    ) -> AssetPackage:
        """Create a complete asset package for game development."""
        
        if output_dir is None:
            output_dir = Path("complete_asset_package")
        output_dir.mkdir(exist_ok=True)
        
        # Initialize result structure
        graphics_assets = {}
        font_assets = {}
        archived_assets = {}
        
        # Process graphics assets from CC0 libraries
        if any(asset_type in ["sprites", "textures", "ui", "graphics"] for asset_type in asset_types):
            graphics_assets = await self._gather_graphics_assets(
                game_description, asset_types, style_preferences, max_assets_per_type, output_dir
            )
        
        # Process font assets
        if "fonts" in asset_types or "typography" in asset_types:
            font_assets = await self._gather_font_assets(
                game_description, style_preferences, output_dir
            )
        
        # Process archived assets if requested
        if "archived" in asset_types or "seeded" in asset_types:
            archived_assets = await self._gather_archived_assets(
                game_description, max_assets_per_type, output_dir
            )
        
        # Create comprehensive metadata
        metadata = self._create_package_metadata(
            game_description, asset_types, style_preferences,
            graphics_assets, font_assets, archived_assets
        )
        
        # Generate summary
        summary = self._create_package_summary(graphics_assets, font_assets, archived_assets)
        
        # Save package manifest
        manifest = {
            "game_description": game_description,
            "asset_types": asset_types,
            "style_preferences": style_preferences,
            "graphics_assets": graphics_assets,
            "font_assets": font_assets,
            "archived_assets": archived_assets,
            "metadata": metadata,
            "summary": summary
        }
        
        manifest_path = output_dir / "asset_package_manifest.json"
        with open(manifest_path, 'w') as f:
            json.dump(manifest, f, indent=2, default=str)
        
        return AssetPackage(
            graphics_assets=graphics_assets,
            font_assets=font_assets,
            archived_assets=archived_assets,
            metadata=metadata,
            summary=summary
        )
    
    def _analyze_asset_context(
        self,
        game_description: str,
        art_style: str,
        color_palette: str
    ) -> Dict[str, Any]:
        """Analyze game description to determine asset context."""
        
        desc_lower = game_description.lower()
        
        # Determine game genre for asset selection
        genre = "modern"
        if any(word in desc_lower for word in ["fantasy", "magic", "medieval", "dragon"]):
            genre = "fantasy"
        elif any(word in desc_lower for word in ["sci-fi", "space", "robot", "cyber", "future"]):
            genre = "sci-fi"
        elif any(word in desc_lower for word in ["horror", "scary", "dark", "zombie"]):
            genre = "horror"
        elif any(word in desc_lower for word in ["retro", "pixel", "8bit", "arcade"]):
            genre = "retro"
        elif any(word in desc_lower for word in ["cartoon", "cute", "colorful", "fun"]):
            genre = "cartoon"
        
        # Determine primary game contexts
        contexts = []
        if any(word in desc_lower for word in ["platformer", "jump", "run"]):
            contexts.append("platformer")
        if any(word in desc_lower for word in ["rpg", "role", "character", "quest"]):
            contexts.append("rpg")
        if any(word in desc_lower for word in ["puzzle", "solve", "brain"]):
            contexts.append("puzzle")
        if any(word in desc_lower for word in ["action", "fast", "combat"]):
            contexts.append("action")
        
        # Analyze visual complexity
        complexity = "intermediate"
        if any(word in desc_lower for word in ["simple", "minimal", "basic"]):
            complexity = "simple"
        elif any(word in desc_lower for word in ["complex", "detailed", "rich"]):
            complexity = "complex"
        
        return {
            "genre": genre,
            "contexts": contexts,
            "art_style": art_style,
            "color_palette": color_palette,
            "complexity": complexity
        }
    
    async def _generate_visual_assets(
        self,
        game_description: str,
        asset_context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate visual assets using CC0 libraries."""
        
        genre = asset_context["genre"]
        art_style = asset_context["art_style"]
        
        # Determine needed asset types
        asset_types = self._determine_visual_asset_types(game_description)
        
        all_assets = []
        
        for asset_type in asset_types:
            # Build search query
            search_keywords = f"{genre} {art_style}"
            if asset_context["color_palette"]:
                search_keywords += f" {asset_context['color_palette']}"
            
            # Search CC0 libraries
            assets = await self.cc0_library.search_assets(
                asset_type=asset_type,
                keywords=search_keywords,
                max_results=5,
                style=art_style
            )
            
            # Convert to serializable format
            for asset in assets:
                all_assets.append({
                    "type": asset_type,
                    "name": asset.name,
                    "description": asset.description,
                    "download_url": asset.download_url,
                    "preview_url": asset.preview_url,
                    "license": asset.license,
                    "source": asset.source_library,
                    "tags": asset.tags,
                    "resolution": asset.resolution
                })
        
        return all_assets
    
    def _determine_visual_asset_types(self, game_description: str) -> List[AssetType]:
        """Determine needed visual asset types from game description."""
        
        desc_lower = game_description.lower()
        asset_types = []
        
        # Always include these basics
        asset_types.extend(["sprite", "icon"])
        
        # Add context-specific assets
        if any(word in desc_lower for word in ["background", "environment", "world"]):
            asset_types.append("texture")
        
        if any(word in desc_lower for word in ["character", "player", "hero", "enemy"]):
            asset_types.append("sprite")
        
        if any(word in desc_lower for word in ["ui", "interface", "menu", "button"]):
            asset_types.append("icon")
        
        if any(word in desc_lower for word in ["3d", "model", "object"]):
            asset_types.append("model")
        
        return list(set(asset_types))  # Remove duplicates
    
    async def _generate_font_pack(
        self,
        game_description: str,
        asset_context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate typography pack using Google Fonts."""
        
        genre = asset_context["genre"]
        
        # Map game genres to font contexts
        font_context_map = {
            "fantasy": FontGameContext.FANTASY,
            "sci-fi": FontGameContext.SCI_FI,
            "retro": FontGameContext.RETRO,
            "modern": FontGameContext.MODERN,
            "horror": FontGameContext.MODERN,  # Use modern as fallback
            "cartoon": FontGameContext.MODERN
        }
        
        primary_context = font_context_map.get(genre, FontGameContext.MODERN)
        
        # Get font recommendations for different uses
        ui_fonts = await self.fonts_manager.search_fonts(
            game_context=FontGameContext.UI,
            max_results=3
        )
        
        title_fonts = await self.fonts_manager.search_fonts(
            game_context=FontGameContext.TITLE,
            style_keywords=f"{genre} {asset_context['art_style']}",
            max_results=3
        )
        
        dialogue_fonts = await self.fonts_manager.search_fonts(
            game_context=FontGameContext.DIALOGUE,
            max_results=2
        )
        
        # Combine and format results
        font_pack = []
        
        # Add UI fonts
        for font in ui_fonts:
            font_pack.append({
                "usage": "ui",
                "family": font.family,
                "category": font.category,
                "variants": font.variants,
                "style_tags": font.style_tags,
                "game_contexts": font.game_contexts,
                "download_files": font.files
            })
        
        # Add title fonts
        for font in title_fonts:
            font_pack.append({
                "usage": "title",
                "family": font.family,
                "category": font.category,
                "variants": font.variants,
                "style_tags": font.style_tags,
                "game_contexts": font.game_contexts,
                "download_files": font.files
            })
        
        # Add dialogue fonts
        for font in dialogue_fonts:
            font_pack.append({
                "usage": "dialogue",
                "family": font.family,
                "category": font.category,
                "variants": font.variants,
                "style_tags": font.style_tags,
                "game_contexts": font.game_contexts,
                "download_files": font.files
            })
        
        return font_pack
    
    async def _generate_semantic_seeds(
        self,
        game_description: str,
        theme_keywords: str,
        asset_context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate semantic seeds using Internet Archive."""
        
        if not theme_keywords:
            # Extract keywords from game description
            theme_keywords = asset_context["genre"]
        
        # Generate semantic seed
        seed = await self.archive_seeder.generate_semantic_seed(
            concept=theme_keywords,
            context_description=game_description,
            max_reference_items=10
        )
        
        # Search for related archive items
        archive_items = await self.archive_seeder.search_archive(
            keywords=theme_keywords,
            media_type="image",
            max_results=15
        )
        
        # Format results
        semantic_seeds = [{
            "concept": seed.concept,
            "description": seed.description,
            "keywords": seed.keywords,
            "context_strength": seed.context_strength,
            "reference_items": [
                {
                    "title": item.title,
                    "description": item.description,
                    "download_url": item.download_url,
                    "preview_url": item.preview_url,
                    "subjects": item.subjects,
                    "similarity_score": item.embedding_score
                } for item in archive_items[:5]  # Top 5 most relevant
            ]
        }]
        
        return semantic_seeds
    
    def _create_asset_summary(
        self,
        visual_assets: List[Dict[str, Any]],
        fonts: List[Dict[str, Any]],
        semantic_seeds: List[Dict[str, Any]]
    ) -> str:
        """Create a summary of the generated asset pack."""
        
        summary_parts = []
        
        if visual_assets:
            asset_types = set(asset["type"] for asset in visual_assets)
            summary_parts.append(f"Found {len(visual_assets)} visual assets ({', '.join(asset_types)})")
        
        if fonts:
            font_uses = set(font["usage"] for font in fonts)
            summary_parts.append(f"Selected {len(fonts)} fonts for {', '.join(font_uses)}")
        
        if semantic_seeds:
            total_references = sum(len(seed.get("reference_items", [])) for seed in semantic_seeds)
            summary_parts.append(f"Generated {len(semantic_seeds)} semantic seeds with {total_references} references")
        
        return "Asset pack includes: " + ", ".join(summary_parts) + "."
    
    def create_langraph_tool(self) -> StructuredTool:
        """Create a unified LangGraph tool for complete asset workflow."""
        
        async def _generate_asset_workflow(
            game_description: str,
            asset_needs: List[str],
            art_style: str = "modern",
            color_palette: str = "",
            theme_keywords: str = ""
        ) -> Dict[str, Any]:
            """Generate complete asset pack for game development."""
            
            result = await self.generate_complete_asset_pack(
                game_description=game_description,
                asset_needs=asset_needs,
                art_style=art_style,
                color_palette=color_palette,
                theme_keywords=theme_keywords
            )
            
            return {
                "visual_assets": result.visual_assets,
                "fonts": result.fonts,
                "semantic_seeds": result.semantic_seeds,
                "summary": result.asset_pack_summary,
                "total_assets": (
                    len(result.visual_assets) +
                    len(result.fonts) +
                    len(result.semantic_seeds)
                )
            }
        
        return StructuredTool.from_function(
            func=_generate_asset_workflow,
            name="generate_complete_assets",
            description=(
                "Generate a complete asset pack for game development including "
                "CC0 visual assets, Google Fonts typography, and semantic seeds from "
                "Internet Archive. Provides end-to-end asset production workflow."
            ),
            args_schema=AssetWorkflowRequest
        )
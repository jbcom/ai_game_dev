"""
Unified asset tools integrating CC0 libraries, fonts, and archive seeding.
Provides LangGraph structured tools for complete asset workflow.
"""
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from langchain_core.tools import StructuredTool
from langchain_core.pydantic_v1 import BaseModel, Field

from .cc0_libraries import CC0AssetLibrary, AssetType
from .google_fonts import GoogleFontsManager, GameContext as FontGameContext
from .archive_seeder import InternetArchiveSeeder


class AssetWorkflowRequest(BaseModel):
    """Request for complete asset workflow."""
    game_description: str = Field(description="Description of the game")
    asset_needs: List[str] = Field(description="List of asset needs (sprites, fonts, sounds)")
    art_style: str = Field(default="modern", description="Art style preference")
    color_palette: str = Field(default="", description="Color palette description")
    theme_keywords: str = Field(default="", description="Theme keywords for seeding")


@dataclass
class AssetWorkflowResult:
    """Result of complete asset workflow."""
    visual_assets: List[Dict[str, Any]]
    fonts: List[Dict[str, Any]]
    semantic_seeds: List[Dict[str, Any]]
    asset_pack_summary: str


class AssetTools:
    """Unified asset tools for complete game asset generation."""
    
    def __init__(self):
        self.cc0_library = CC0AssetLibrary()
        self.fonts_manager = GoogleFontsManager()
        self.archive_seeder = InternetArchiveSeeder()
    
    async def generate_complete_asset_pack(
        self,
        game_description: str,
        asset_needs: List[str],
        art_style: str = "modern",
        color_palette: str = "",
        theme_keywords: str = ""
    ) -> AssetWorkflowResult:
        """Generate a complete asset pack for a game."""
        
        # Analyze asset context
        asset_context = self._analyze_asset_context(game_description, art_style, color_palette)
        
        # Generate visual assets
        visual_assets = []
        if any(need in asset_needs for need in ["sprites", "textures", "icons", "visuals"]):
            visual_assets = await self._generate_visual_assets(game_description, asset_context)
        
        # Generate fonts
        fonts = []
        if "fonts" in asset_needs or "typography" in asset_needs:
            fonts = await self._generate_font_pack(game_description, asset_context)
        
        # Generate semantic seeds
        semantic_seeds = []
        if theme_keywords or "seeds" in asset_needs:
            semantic_seeds = await self._generate_semantic_seeds(
                game_description, theme_keywords, asset_context
            )
        
        # Create summary
        summary = self._create_asset_summary(visual_assets, fonts, semantic_seeds)
        
        return AssetWorkflowResult(
            visual_assets=visual_assets,
            fonts=fonts,
            semantic_seeds=semantic_seeds,
            asset_pack_summary=summary
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
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
    
    async def _gather_graphics_assets(
        self,
        game_description: str,
        asset_types: list[str],
        style_preferences: str,
        max_assets: int,
        output_dir: Path
    ) -> dict[str, list[dict[str, Any]]]:
        """Gather graphics assets from CC0 libraries."""
        
        graphics_dir = output_dir / "graphics"
        graphics_dir.mkdir(exist_ok=True)
        
        graphics_assets = {}
        
        # Map asset types to search categories
        type_mapping = {
            "sprites": "sprites",
            "textures": "textures", 
            "ui": "ui",
            "graphics": "all",
            "backgrounds": "textures",
            "characters": "sprites",
            "items": "sprites"
        }
        
        for asset_type in asset_types:
            if asset_type in type_mapping:
                search_category = type_mapping[asset_type]
                
                # Search for assets
                search_query = f"{game_description} {style_preferences} {asset_type}".strip()
                found_assets = await self._cc0_client.search_assets(
                    search_query, search_category, "cc0"
                )
                
                # Limit results and add metadata
                limited_assets = found_assets[:max_assets]
                
                for asset in limited_assets:
                    asset["search_query"] = search_query
                    asset["asset_type"] = asset_type
                    asset["local_category"] = search_category
                
                graphics_assets[asset_type] = limited_assets
        
        # Save graphics manifest
        graphics_manifest = graphics_dir / "graphics_manifest.json"
        with open(graphics_manifest, 'w') as f:
            json.dump(graphics_assets, f, indent=2)
        
        return graphics_assets
    
    async def _gather_font_assets(
        self,
        game_description: str,
        style_preferences: str,
        output_dir: Path
    ) -> dict[str, Any]:
        """Gather font assets from Google Fonts."""
        
        fonts_dir = output_dir / "fonts"
        fonts_dir.mkdir(exist_ok=True)
        
        # Determine game style for font selection
        combined_description = f"{game_description} {style_preferences}".strip()
        
        # Create font pack
        font_pack = await self._fonts_client.create_font_pack(
            combined_description, fonts_dir
        )
        
        # Get font recommendations
        game_style = self._fonts_client._analyze_game_style(combined_description)
        recommended_fonts = await self._fonts_client.get_fonts_for_game_style(game_style)
        
        font_assets = {
            "downloaded_fonts": font_pack,
            "game_style": game_style,
            "recommended_fonts": recommended_fonts,
            "font_pairings": {}
        }
        
        # Add font pairing suggestions
        for font_family in font_pack.keys():
            if not font_family.startswith("system_"):
                pairings = self._fonts_client.get_font_pairing_suggestions(font_family)
                font_assets["font_pairings"][font_family] = pairings
        
        return font_assets
    
    async def _gather_archived_assets(
        self,
        game_description: str,
        max_assets: int,
        output_dir: Path
    ) -> dict[str, Any]:
        """Gather assets from Internet Archive."""
        
        archive_dir = output_dir / "archived"
        archive_dir.mkdir(exist_ok=True)
        
        # Create curated asset seed
        curated_seed = await self._archive_client.create_curated_asset_seed(
            game_description, max_collections=max_assets, max_size_mb=100
        )
        
        # Save seed metadata
        seed_metadata_path = archive_dir / "curated_seed.json"
        with open(seed_metadata_path, 'w') as f:
            json.dump(curated_seed, f, indent=2, default=str)
        
        return {
            "curated_seed": curated_seed,
            "total_collections": len(curated_seed.get("collections", [])),
            "estimated_size_mb": curated_seed.get("total_estimated_size_mb", 0),
            "download_order": curated_seed.get("recommended_download_order", [])
        }
    
    def _create_package_metadata(
        self,
        game_description: str,
        asset_types: list[str],
        style_preferences: str,
        graphics_assets: dict[str, Any],
        font_assets: dict[str, Any],
        archived_assets: dict[str, Any]
    ) -> dict[str, Any]:
        """Create comprehensive metadata for the asset package."""
        
        return {
            "generation_info": {
                "game_description": game_description,
                "requested_asset_types": asset_types,
                "style_preferences": style_preferences,
                "generation_timestamp": "2025-01-01T00:00:00Z"
            },
            "asset_counts": {
                "graphics_categories": len(graphics_assets),
                "total_graphics_assets": sum(len(assets) for assets in graphics_assets.values()),
                "font_families": len(font_assets.get("downloaded_fonts", {})),
                "archived_collections": archived_assets.get("total_collections", 0)
            },
            "estimated_storage": {
                "fonts_mb": 5,  # Estimated
                "archived_mb": archived_assets.get("estimated_size_mb", 0),
                "total_estimated_mb": 5 + archived_assets.get("estimated_size_mb", 0)
            },
            "licenses": {
                "graphics": "CC0 (Creative Commons Zero)",
                "fonts": "Open Font License / Google Fonts",
                "archived": "CC0 (Creative Commons Zero)"
            },
            "usage_recommendations": self._generate_usage_recommendations(
                game_description, graphics_assets, font_assets
            )
        }
    
    def _generate_usage_recommendations(
        self,
        game_description: str,
        graphics_assets: dict[str, Any],
        font_assets: dict[str, Any]
    ) -> list[str]:
        """Generate usage recommendations for the asset package."""
        
        recommendations = []
        
        # Graphics recommendations
        if graphics_assets:
            recommendations.append("Use sprites for character animations and interactive objects")
            if "ui" in graphics_assets:
                recommendations.append("Apply UI assets consistently across all game interfaces")
            if "textures" in graphics_assets:
                recommendations.append("Tile textures seamlessly for background elements")
        
        # Font recommendations
        if font_assets:
            game_style = font_assets.get("game_style", "modern")
            recommendations.append(f"Primary fonts selected for {game_style} style - use consistently")
            recommendations.append("Reserve decorative fonts for titles and special UI elements")
        
        # Game-specific recommendations
        desc_lower = game_description.lower()
        if "mobile" in desc_lower:
            recommendations.append("Optimize all assets for mobile screen sizes and performance")
        if "multiplayer" in desc_lower:
            recommendations.append("Ensure visual consistency for all player-visible assets")
        if "retro" in desc_lower or "pixel" in desc_lower:
            recommendations.append("Maintain pixel-perfect scaling for authentic retro appearance")
        
        return recommendations
    
    def _create_package_summary(
        self,
        graphics_assets: dict[str, Any],
        font_assets: dict[str, Any],
        archived_assets: dict[str, Any]
    ) -> str:
        """Create a human-readable summary of the asset package."""
        
        summary_parts = []
        
        # Graphics summary
        if graphics_assets:
            total_graphics = sum(len(assets) for assets in graphics_assets.values())
            categories = list(graphics_assets.keys())
            summary_parts.append(
                f"Graphics: {total_graphics} assets across {len(categories)} categories "
                f"({', '.join(categories)})"
            )
        
        # Fonts summary
        if font_assets:
            font_count = len(font_assets.get("downloaded_fonts", {}))
            game_style = font_assets.get("game_style", "modern")
            summary_parts.append(f"Fonts: {font_count} font families optimized for {game_style} style")
        
        # Archive summary
        if archived_assets:
            collections = archived_assets.get("total_collections", 0)
            size_mb = archived_assets.get("estimated_size_mb", 0)
            summary_parts.append(f"Archived: {collections} curated collections (~{size_mb:.1f}MB)")
        
        if summary_parts:
            return "Asset package includes: " + "; ".join(summary_parts) + "."
        else:
            return "Asset package created successfully."
    
    def analyze_asset_requirements(
        self,
        game_description: str,
        target_platform: str = "desktop"
    ) -> dict[str, Any]:
        """Analyze game description to determine optimal asset requirements."""
        
        desc_lower = game_description.lower()
        
        # Base requirements
        requirements = {
            "essential_types": ["ui", "sprites"],
            "recommended_types": [],
            "optional_types": [],
            "estimated_count": {},
            "style_suggestions": [],
            "technical_constraints": {}
        }
        
        # Analyze game type for requirements
        if any(word in desc_lower for word in ["platformer", "2d", "side-scrolling"]):
            requirements["essential_types"].extend(["textures", "backgrounds"])
            requirements["recommended_types"].extend(["animations"])
            requirements["style_suggestions"].append("pixel art or hand-drawn")
        
        if any(word in desc_lower for word in ["3d", "first-person", "third-person"]):
            requirements["essential_types"].extend(["textures", "models"])
            requirements["recommended_types"].extend(["materials", "lighting"])
            requirements["style_suggestions"].append("realistic or stylized 3D")
        
        if any(word in desc_lower for word in ["rpg", "adventure", "story"]):
            requirements["recommended_types"].extend(["characters", "environments", "icons"])
            requirements["optional_types"].extend(["portraits", "items"])
        
        # Platform-specific constraints
        if target_platform == "mobile":
            requirements["technical_constraints"] = {
                "max_texture_size": "1024x1024",
                "recommended_formats": ["PNG", "JPG"],
                "performance_priority": "high",
                "file_size_budget": "50MB total"
            }
        elif target_platform == "web":
            requirements["technical_constraints"] = {
                "max_texture_size": "512x512",
                "recommended_formats": ["PNG", "WebP"],
                "performance_priority": "medium",
                "file_size_budget": "20MB total"
            }
        else:  # desktop
            requirements["technical_constraints"] = {
                "max_texture_size": "2048x2048",
                "recommended_formats": ["PNG", "JPG", "TGA"],
                "performance_priority": "low",
                "file_size_budget": "500MB total"
            }
        
        # Estimate asset counts
        base_counts = {"ui": 15, "sprites": 10, "textures": 8, "fonts": 3}
        
        complexity_multiplier = 1.0
        if any(word in desc_lower for word in ["complex", "large", "many", "extensive"]):
            complexity_multiplier = 2.0
        elif any(word in desc_lower for word in ["simple", "minimal", "small"]):
            complexity_multiplier = 0.5
        
        for asset_type in requirements["essential_types"] + requirements["recommended_types"]:
            if asset_type in base_counts:
                requirements["estimated_count"][asset_type] = int(
                    base_counts[asset_type] * complexity_multiplier
                )
        
        return requirements
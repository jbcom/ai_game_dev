"""Specialized Bevy game engine asset generation system."""

import asyncio
import json
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from enum import Enum

import aiofiles
from openai import AsyncOpenAI
from PIL import Image

from .config import settings
from .logging_config import get_logger
from .models import ImageSize, GenerationResult
from .advanced_generators import AdvancedImageGenerator
from .utils import ensure_directory_exists

logger = get_logger(__name__, component="bevy_assets")


class BevyAssetType(str, Enum):
    """Bevy-specific asset types."""
    SPRITE_2D = "sprite_2d"
    TILEMAP = "tilemap"
    UI_ELEMENT = "ui_element"
    PARTICLE_TEXTURE = "particle_texture"
    SKYBOX = "skybox"
    ENVIRONMENT_MAP = "environment_map"
    NORMAL_MAP = "normal_map"
    ROUGHNESS_MAP = "roughness_map"
    METALLIC_MAP = "metallic_map"
    EMISSION_MAP = "emission_map"
    SPRITE_ATLAS = "sprite_atlas"


class BevyMaterialType(str, Enum):
    """Bevy material system types."""
    STANDARD_MATERIAL = "standard"
    UNLIT_MATERIAL = "unlit"
    SPRITE_MATERIAL = "sprite"
    UI_MATERIAL = "ui"
    CUSTOM_MATERIAL = "custom"


class BevyAssetSpec:
    """Specification for Bevy-compatible assets."""
    
    def __init__(
        self,
        asset_type: BevyAssetType,
        name: str,
        description: str,
        size: ImageSize = "1024x1024",
        material_type: BevyMaterialType = BevyMaterialType.STANDARD_MATERIAL,
        tile_size: Optional[Tuple[int, int]] = None,
        atlas_layout: Optional[Tuple[int, int]] = None,
        animation_frames: int = 1,
        seamless: bool = False,
        transparent: bool = False,
        game_style: str = "fantasy",
        bevy_components: Optional[List[str]] = None
    ):
        self.asset_type = asset_type
        self.name = name
        self.description = description
        self.size = size
        self.material_type = material_type
        self.tile_size = tile_size
        self.atlas_layout = atlas_layout
        self.animation_frames = animation_frames
        self.seamless = seamless
        self.transparent = transparent
        self.game_style = game_style
        self.bevy_components = bevy_components or []
        self.id = str(uuid.uuid4())


class BevyAssetGenerator:
    """Specialized generator for Bevy game engine assets."""
    
    def __init__(self, openai_client: AsyncOpenAI):
        self.client = openai_client
        self.advanced_generator = AdvancedImageGenerator(openai_client)
        self.assets_dir = settings.cache_dir / "bevy_assets"
        
    async def generate_sprite_2d(
        self,
        name: str,
        description: str,
        size: ImageSize = "512x512",
        transparent: bool = True,
        style: str = "pixel art",
        animation_frames: int = 1
    ) -> GenerationResult:
        """Generate 2D sprite optimized for Bevy."""
        
        spec = BevyAssetSpec(
            asset_type=BevyAssetType.SPRITE_2D,
            name=name,
            description=description,
            size=size,
            transparent=transparent,
            game_style=style,
            animation_frames=animation_frames,
            bevy_components=["Sprite", "Transform", "Visibility"]
        )
        
        # Create game-optimized prompt
        prompt = self._create_sprite_prompt(spec)
        
        # Generate the sprite
        response = await self.client.images.generate(
            prompt=prompt,
            size=size,
            quality="standard",
            n=1
        )
        
        # Save with Bevy-compatible structure
        asset_path = await self._save_bevy_asset(response.data[0].url, spec)
        
        # Generate animation frames if requested
        if animation_frames > 1:
            frames = await self._generate_animation_frames(spec, asset_path)
            return self._create_animated_sprite_result(spec, asset_path, frames)
        
        return self._create_generation_result(spec, asset_path)
    
    async def generate_tilemap_set(
        self,
        theme: str,
        tile_count: int = 16,
        tile_size: Tuple[int, int] = (64, 64),
        seamless: bool = True
    ) -> Dict[str, Any]:
        """Generate complete tilemap set for Bevy tilemaps."""
        
        tiles = []
        tile_types = [
            "grass", "dirt", "stone", "water", "sand", "rock", "tree", "flower",
            "path", "wall", "door", "window", "roof", "bridge", "fence", "decorative"
        ]
        
        # Generate individual tiles
        for i, tile_type in enumerate(tile_types[:tile_count]):
            spec = BevyAssetSpec(
                asset_type=BevyAssetType.TILEMAP,
                name=f"{theme}_{tile_type}_tile",
                description=f"{tile_type} tile for {theme} themed tilemap",
                size="256x256",
                tile_size=tile_size,
                seamless=seamless,
                game_style=theme,
                bevy_components=["TileMapBundle", "TileStorage"]
            )
            
            prompt = self._create_tile_prompt(spec, tile_type)
            
            response = await self.client.images.generate(
                prompt=prompt,
                size="256x256",
                quality="standard",
                n=1
            )
            
            tile_path = await self._save_bevy_asset(response.data[0].url, spec)
            tiles.append({
                "type": tile_type,
                "path": str(tile_path),
                "id": i,
                "spec": spec.__dict__
            })
        
        # Create tilemap atlas
        atlas_path = await self._create_tile_atlas(tiles, theme)
        
        # Generate Bevy tilemap configuration
        tilemap_config = self._generate_tilemap_config(tiles, atlas_path)
        
        return {
            "tilemap_name": f"{theme}_tilemap",
            "atlas_path": str(atlas_path),
            "tiles": tiles,
            "config": tilemap_config,
            "bevy_setup": self._generate_bevy_tilemap_code(theme, tiles)
        }
    
    async def generate_ui_theme(
        self,
        theme_name: str,
        style: str = "fantasy",
        elements: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Generate complete UI theme for Bevy UI system."""
        
        if elements is None:
            elements = [
                "button_normal", "button_hover", "button_pressed",
                "panel_background", "panel_border", "window_frame",
                "health_bar", "mana_bar", "inventory_slot",
                "icon_frame", "text_background", "progress_bar"
            ]
        
        ui_assets = {}
        
        for element in elements:
            spec = BevyAssetSpec(
                asset_type=BevyAssetType.UI_ELEMENT,
                name=f"{theme_name}_{element}",
                description=f"{element} UI element for {theme_name} theme",
                size="512x512" if "panel" in element else "256x256",
                material_type=BevyMaterialType.UI_MATERIAL,
                transparent=True,
                game_style=style,
                bevy_components=["NodeBundle", "ImageBundle", "ButtonBundle"]
            )
            
            prompt = self._create_ui_prompt(spec, element)
            
            response = await self.client.images.generate(
                prompt=prompt,
                size=spec.size,
                quality="standard", 
                n=1
            )
            
            asset_path = await self._save_bevy_asset(response.data[0].url, spec)
            ui_assets[element] = {
                "path": str(asset_path),
                "spec": spec.__dict__
            }
        
        # Generate Bevy UI theme configuration
        theme_config = self._generate_ui_theme_config(theme_name, ui_assets)
        
        return {
            "theme_name": theme_name,
            "assets": ui_assets,
            "config": theme_config,
            "bevy_setup": self._generate_bevy_ui_code(theme_name, ui_assets)
        }
    
    async def generate_particle_textures(
        self,
        effect_type: str,
        count: int = 8,
        size: ImageSize = "256x256"
    ) -> Dict[str, Any]:
        """Generate particle textures for Bevy particle systems."""
        
        particle_types = {
            "fire": ["flame_core", "flame_outer", "spark", "ember"],
            "magic": ["energy_orb", "magic_trail", "spell_burst", "rune_glow"],
            "explosion": ["blast_center", "shockwave", "debris", "smoke"],
            "water": ["droplet", "splash", "foam", "bubble"],
            "nature": ["leaf", "pollen", "dust", "wind_swirl"]
        }
        
        particles = []
        base_particles = particle_types.get(effect_type, ["particle_1", "particle_2", "particle_3", "particle_4"])
        
        for i, particle_name in enumerate(base_particles[:count]):
            spec = BevyAssetSpec(
                asset_type=BevyAssetType.PARTICLE_TEXTURE,
                name=f"{effect_type}_{particle_name}",
                description=f"{particle_name} texture for {effect_type} particle effect",
                size=size,
                transparent=True,
                game_style="realistic",
                bevy_components=["ParticleSystem", "Material"]
            )
            
            prompt = self._create_particle_prompt(spec, effect_type, particle_name)
            
            response = await self.client.images.generate(
                prompt=prompt,
                size=size,
                quality="standard",
                n=1
            )
            
            particle_path = await self._save_bevy_asset(response.data[0].url, spec)
            particles.append({
                "name": particle_name,
                "path": str(particle_path),
                "id": i,
                "spec": spec.__dict__
            })
        
        return {
            "effect_type": effect_type,
            "particles": particles,
            "bevy_setup": self._generate_bevy_particle_code(effect_type, particles)
        }
    
    async def generate_pbr_material_set(
        self,
        material_name: str,
        description: str,
        size: ImageSize = "1024x1024"
    ) -> Dict[str, Any]:
        """Generate complete PBR material set for Bevy StandardMaterial."""
        
        # Generate all PBR maps
        maps = {}
        
        # Albedo (base color)
        albedo_spec = BevyAssetSpec(
            asset_type=BevyAssetType.SPRITE_2D,
            name=f"{material_name}_albedo",
            description=f"Albedo map for {material_name}: {description}",
            size=size,
            seamless=True,
            material_type=BevyMaterialType.STANDARD_MATERIAL
        )
        
        albedo_prompt = f"Seamless tileable {description} texture, albedo map, diffuse colors only, no lighting, flat lighting, texture pattern"
        
        response = await self.client.images.generate(
            prompt=albedo_prompt,
            size=size,
            quality="hd",
            n=1
        )
        
        maps["albedo"] = await self._save_bevy_asset(response.data[0].url, albedo_spec)
        
        # Normal map
        normal_prompt = f"Normal map for {description} texture, purple/blue normal map, surface details, bumps and grooves, seamless tileable"
        
        response = await self.client.images.generate(
            prompt=normal_prompt,
            size=size,
            quality="hd", 
            n=1
        )
        
        normal_spec = albedo_spec
        normal_spec.name = f"{material_name}_normal"
        normal_spec.asset_type = BevyAssetType.NORMAL_MAP
        maps["normal"] = await self._save_bevy_asset(response.data[0].url, normal_spec)
        
        # Roughness map
        roughness_prompt = f"Roughness map for {description} texture, grayscale, black=smooth white=rough, surface roughness variation, seamless tileable"
        
        response = await self.client.images.generate(
            prompt=roughness_prompt,
            size=size,
            quality="hd",
            n=1
        )
        
        roughness_spec = albedo_spec
        roughness_spec.name = f"{material_name}_roughness" 
        roughness_spec.asset_type = BevyAssetType.ROUGHNESS_MAP
        maps["roughness"] = await self._save_bevy_asset(response.data[0].url, roughness_spec)
        
        # Metallic map (if appropriate)
        if any(word in description.lower() for word in ["metal", "steel", "iron", "gold", "silver", "copper"]):
            metallic_prompt = f"Metallic map for {description} texture, grayscale, white=metallic black=non-metallic, seamless tileable"
            
            response = await self.client.images.generate(
                prompt=metallic_prompt,
                size=size,
                quality="hd",
                n=1
            )
            
            metallic_spec = albedo_spec
            metallic_spec.name = f"{material_name}_metallic"
            metallic_spec.asset_type = BevyAssetType.METALLIC_MAP
            maps["metallic"] = await self._save_bevy_asset(response.data[0].url, metallic_spec)
        
        # Generate Bevy material configuration
        material_config = self._generate_bevy_material_config(material_name, maps)
        
        return {
            "material_name": material_name,
            "maps": {k: str(v) for k, v in maps.items()},
            "config": material_config,
            "bevy_setup": self._generate_bevy_material_code(material_name, maps)
        }
    
    def _create_sprite_prompt(self, spec: BevyAssetSpec) -> str:
        """Create optimized prompt for sprite generation."""
        
        style_modifiers = {
            "pixel art": "pixel art style, crisp pixels, retro gaming aesthetic, clean pixel boundaries",
            "hand drawn": "hand drawn illustration, artistic style, painted look",
            "realistic": "photorealistic, detailed rendering, high quality",
            "cartoon": "cartoon style, cel shaded, vibrant colors, stylized",
            "minimalist": "simple, clean design, minimal details, geometric shapes"
        }
        
        base_prompt = f"Game sprite: {spec.description}"
        style_addon = style_modifiers.get(spec.game_style, "game art style")
        
        prompt_parts = [
            base_prompt,
            style_addon,
            "optimized for game engine",
            "clean composition"
        ]
        
        if spec.transparent:
            prompt_parts.append("transparent background, PNG format")
        
        if spec.animation_frames > 1:
            prompt_parts.append("suitable for sprite animation")
        
        return ", ".join(prompt_parts)
    
    def _create_tile_prompt(self, spec: BevyAssetSpec, tile_type: str) -> str:
        """Create prompt for tilemap tile generation."""
        
        prompt_parts = [
            f"{tile_type} tile for {spec.game_style} game",
            "seamless tileable texture" if spec.seamless else "tile texture",
            "top-down perspective",
            "game tilemap asset",
            "clean edges for tiling",
            f"size {spec.tile_size[0]}x{spec.tile_size[1]} pixels" if spec.tile_size else "",
            "optimized for game engine"
        ]
        
        return ", ".join(filter(None, prompt_parts))
    
    def _create_ui_prompt(self, spec: BevyAssetSpec, element_type: str) -> str:
        """Create prompt for UI element generation."""
        
        ui_styles = {
            "fantasy": "medieval fantasy UI, ornate decorations, stone and wood textures, gold accents",
            "sci-fi": "futuristic UI, metallic surfaces, glowing elements, high-tech design",
            "modern": "clean modern UI, flat design, minimal style, professional look",
            "retro": "retro gaming UI, pixel art style, classic arcade aesthetic"
        }
        
        base_prompt = f"Game UI {element_type.replace('_', ' ')}"
        style_addon = ui_styles.get(spec.game_style, "game UI style")
        
        prompt_parts = [
            base_prompt,
            style_addon,
            "transparent background",
            "game interface element",
            "clean professional design",
            "optimized for game UI system"
        ]
        
        return ", ".join(prompt_parts)
    
    def _create_particle_prompt(self, spec: BevyAssetSpec, effect_type: str, particle_name: str) -> str:
        """Create prompt for particle texture generation."""
        
        prompt_parts = [
            f"{particle_name} texture for {effect_type} particle effect",
            "transparent background",
            "suitable for particle system",
            "game VFX asset",
            "high contrast",
            "optimized for blending"
        ]
        
        return ", ".join(prompt_parts)
    
    async def _save_bevy_asset(self, image_url: str, spec: BevyAssetSpec) -> Path:
        """Save asset with Bevy-compatible structure."""
        
        # Create Bevy asset directory structure
        asset_type_dir = self.assets_dir / spec.asset_type.value
        await ensure_directory_exists(asset_type_dir)
        
        # Save the image
        asset_path = asset_type_dir / f"{spec.name}.png"
        
        # Download and save
        import aiohttp
        async with aiohttp.ClientSession() as session:
            async with session.get(image_url) as response:
                if response.status == 200:
                    async with aiofiles.open(asset_path, 'wb') as f:
                        await f.write(await response.read())
        
        # Save asset metadata
        metadata = {
            "id": spec.id,
            "name": spec.name,
            "asset_type": spec.asset_type.value,
            "material_type": spec.material_type.value,
            "size": spec.size,
            "bevy_components": spec.bevy_components,
            "transparent": spec.transparent,
            "seamless": spec.seamless
        }
        
        metadata_path = asset_type_dir / f"{spec.name}.json"
        async with aiofiles.open(metadata_path, 'w') as f:
            await f.write(json.dumps(metadata, indent=2))
        
        return asset_path
    
    def _create_generation_result(self, spec: BevyAssetSpec, asset_path: Path) -> GenerationResult:
        """Create generation result with Bevy metadata."""
        
        return GenerationResult(
            id=spec.id,
            type="image",
            file_path=str(asset_path),
            metadata={
                "bevy_asset_type": spec.asset_type.value,
                "bevy_material_type": spec.material_type.value,
                "bevy_components": spec.bevy_components,
                "game_style": spec.game_style,
                "transparent": spec.transparent,
                "seamless": spec.seamless,
                "size": spec.size,
                "name": spec.name
            }
        )
    
    async def _generate_animation_frames(self, spec: BevyAssetSpec, base_path: Path) -> List[Path]:
        """Generate animation frames for sprite."""
        # This would generate additional frames for animation
        # For now, return base path as single frame
        return [base_path]
    
    def _create_animated_sprite_result(self, spec: BevyAssetSpec, base_path: Path, frames: List[Path]) -> GenerationResult:
        """Create result for animated sprite."""
        
        result = self._create_generation_result(spec, base_path)
        result.metadata["animation_frames"] = len(frames)
        result.metadata["frame_paths"] = [str(p) for p in frames]
        return result
    
    async def _create_tile_atlas(self, tiles: List[Dict], theme: str) -> Path:
        """Create tile atlas from individual tiles."""
        # This would combine tiles into an atlas texture
        # For now, return placeholder path
        atlas_dir = self.assets_dir / "atlases"
        await ensure_directory_exists(atlas_dir)
        return atlas_dir / f"{theme}_tilemap_atlas.png"
    
    def _generate_tilemap_config(self, tiles: List[Dict], atlas_path: Path) -> Dict[str, Any]:
        """Generate Bevy tilemap configuration."""
        
        return {
            "atlas_path": str(atlas_path),
            "tile_size": {"x": 64, "y": 64},
            "tiles": {tile["type"]: tile["id"] for tile in tiles},
            "bevy_integration": "TiledMap compatible"
        }
    
    def _generate_bevy_tilemap_code(self, theme: str, tiles: List[Dict]) -> str:
        """Generate Bevy tilemap setup code."""
        
        return f'''
// Bevy tilemap setup for {theme}
use bevy::prelude::*;
use bevy_ecs_tilemap::prelude::*;

#[derive(Resource)]
pub struct {theme.title()}TileAssets {{
    pub tilemap_texture: Handle<Image>,
}}

fn setup_{theme}_tilemap(
    mut commands: Commands,
    asset_server: Res<AssetServer>,
) {{
    let tilemap_texture = asset_server.load("{theme}_tilemap_atlas.png");
    
    commands.insert_resource({theme.title()}TileAssets {{
        tilemap_texture: tilemap_texture.clone(),
    }});
    
    let tilemap_entity = commands.spawn_empty().id();
    let mut tile_storage = TileStorage::empty(TilemapSize {{ x: 32, y: 32 }});
    
    commands.entity(tilemap_entity).insert(TilemapBundle {{
        grid_size: TilemapGridSize {{ x: 64.0, y: 64.0 }},
        map_type: TilemapType::default(),
        size: TilemapSize {{ x: 32, y: 32 }},
        storage: tile_storage,
        texture: TilemapTexture::Single(tilemap_texture),
        tile_size: TilemapTileSize {{ x: 64.0, y: 64.0 }},
        transform: get_tilemap_center_transform(&TilemapSize {{ x: 32, y: 32 }}, &TilemapGridSize {{ x: 64.0, y: 64.0 }}, &TilemapType::default(), 0.0),
        ..Default::default()
    }});
}}
'''
    
    def _generate_ui_theme_config(self, theme_name: str, ui_assets: Dict) -> Dict[str, Any]:
        """Generate UI theme configuration."""
        
        return {
            "theme_name": theme_name,
            "assets": ui_assets,
            "bevy_integration": "Compatible with bevy_ui"
        }
    
    def _generate_bevy_ui_code(self, theme_name: str, ui_assets: Dict) -> str:
        """Generate Bevy UI setup code."""
        
        return f'''
// Bevy UI setup for {theme_name} theme
use bevy::prelude::*;

#[derive(Resource)]
pub struct {theme_name.title()}UiAssets {{
{chr(10).join(f'    pub {asset_name}: Handle<Image>,' for asset_name in ui_assets.keys())}
}}

fn setup_{theme_name}_ui_assets(
    mut commands: Commands,
    asset_server: Res<AssetServer>,
) {{
    commands.insert_resource({theme_name.title()}UiAssets {{
{chr(10).join(f'        {asset_name}: asset_server.load("{ui_assets[asset_name]["path"]}"),') for asset_name in ui_assets.keys()}
    }});
}}
'''
    
    def _generate_bevy_material_config(self, material_name: str, maps: Dict[str, Path]) -> Dict[str, Any]:
        """Generate Bevy material configuration."""
        
        return {
            "material_name": material_name,
            "maps": {k: str(v) for k, v in maps.items()},
            "material_type": "StandardMaterial"
        }
    
    def _generate_bevy_material_code(self, material_name: str, maps: Dict[str, Path]) -> str:
        """Generate Bevy material setup code."""
        
        return f'''
// Bevy StandardMaterial setup for {material_name}
use bevy::prelude::*;

#[derive(Resource)]
pub struct {material_name.title()}MaterialAssets {{
{chr(10).join(f'    pub {map_name}: Handle<Image>,' for map_name in maps.keys())}
}}

fn setup_{material_name}_material(
    mut commands: Commands,
    asset_server: Res<AssetServer>,
    mut materials: ResMut<Assets<StandardMaterial>>,
) {{
    let material_assets = {material_name.title()}MaterialAssets {{
{chr(10).join(f'        {map_name}: asset_server.load("{maps[map_name]}"),') for map_name in maps.keys()}
    }};
    
    let material = StandardMaterial {{
        base_color_texture: Some(material_assets.albedo.clone()),
        {'normal_map_texture: Some(material_assets.normal.clone()),' if 'normal' in maps else ''}
        {'metallic_roughness_texture: Some(material_assets.roughness.clone()),' if 'roughness' in maps else ''}
        {'metallic: 1.0,' if 'metallic' in maps else 'metallic: 0.0,'}
        perceptual_roughness: 0.5,
        ..default()
    }};
    
    let material_handle = materials.add(material);
    commands.insert_resource(material_assets);
}}
'''
    
    def _generate_bevy_particle_code(self, effect_type: str, particles: List[Dict]) -> str:
        """Generate Bevy particle system code."""
        
        return f'''
// Bevy particle system for {effect_type} effect
use bevy::prelude::*;

#[derive(Resource)]
pub struct {effect_type.title()}ParticleAssets {{
{chr(10).join(f'    pub {particle["name"]}: Handle<Image>,' for particle in particles)}
}}

fn setup_{effect_type}_particles(
    mut commands: Commands,
    asset_server: Res<AssetServer>,
) {{
    commands.insert_resource({effect_type.title()}ParticleAssets {{
{chr(10).join(f'        {particle["name"]}: asset_server.load("{particle["path"]}"),') for particle in particles)}
    }});
}}
'''
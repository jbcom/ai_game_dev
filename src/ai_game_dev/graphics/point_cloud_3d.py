"""
3D Point Cloud and Mesh Generation using OpenAI's Point-E.

This module extends our graphics capabilities to generate 3D models
from text descriptions or images, perfect for creating game assets
for Godot and other 3D engines.
"""

import asyncio
from pathlib import Path
from typing import Optional, Dict, Any, Union
import numpy as np

from agents import function_tool

# Import Point-E dependencies
try:
    import torch
    from point_e.diffusion.configs import DIFFUSION_CONFIGS, diffusion_from_config
    from point_e.diffusion.sampler import PointCloudSampler
    from point_e.models.download import load_checkpoint
    from point_e.models.configs import MODEL_CONFIGS, model_from_config
    from point_e.util.ply_util import write_ply
    from point_e.util.pc_to_mesh import marching_cubes_mesh
    from trimesh.exchange.export import export_mesh
    POINT_E_AVAILABLE = True
except ImportError:
    POINT_E_AVAILABLE = False


class Point3DGenerator:
    """Handles 3D point cloud and mesh generation using Point-E."""
    
    def __init__(self):
        """Initialize the 3D generator with Point-E models."""
        if not POINT_E_AVAILABLE:
            raise ImportError("Point-E is not installed. Please install with: pip install point-e")
            
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self._models_loaded = False
        self.base_model = None
        self.upsampler_model = None
        self.sampler = None
        self.sdf_model = None
        
    def _ensure_models_loaded(self):
        """Lazy load models to save memory."""
        if self._models_loaded:
            return
            
        print('Loading Point-E models...')
        
        # Base text-to-3D model
        base_name = 'base40M-textvec'
        self.base_model = model_from_config(MODEL_CONFIGS[base_name], self.device)
        self.base_model.eval()
        base_diffusion = diffusion_from_config(DIFFUSION_CONFIGS[base_name])
        
        # Upsampler for higher quality
        self.upsampler_model = model_from_config(MODEL_CONFIGS['upsample'], self.device)
        self.upsampler_model.eval()
        upsampler_diffusion = diffusion_from_config(DIFFUSION_CONFIGS['upsample'])
        
        # Load checkpoints
        self.base_model.load_state_dict(load_checkpoint(base_name, self.device))
        self.upsampler_model.load_state_dict(load_checkpoint('upsample', self.device))
        
        # Create sampler
        self.sampler = PointCloudSampler(
            device=self.device,
            models=[self.base_model, self.upsampler_model],
            diffusions=[base_diffusion, upsampler_diffusion],
            num_points=[1024, 4096 - 1024],
            aux_channels=['R', 'G', 'B'],
            guidance_scale=[3.0, 0.0],
            model_kwargs_key_filter=('texts', ''),
        )
        
        # SDF model for mesh conversion
        sdf_name = 'sdf'
        self.sdf_model = model_from_config(MODEL_CONFIGS[sdf_name], self.device)
        self.sdf_model.eval()
        self.sdf_model.load_state_dict(load_checkpoint(sdf_name, self.device))
        
        self._models_loaded = True
        
    async def generate_point_cloud(
        self,
        prompt: str,
        output_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate a 3D point cloud from a text prompt."""
        self._ensure_models_loaded()
        
        # Generate point clouds
        samples = None
        for x in self.sampler.sample_batch_progressive(
            batch_size=1,
            model_kwargs=dict(texts=[prompt])
        ):
            samples = x
            
        # Extract the point cloud
        pc = self.sampler.output_to_point_clouds(samples)[0]
        
        # Save if path provided
        if output_path:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Save as PLY
            coords = pc.coords
            colors = np.concatenate([pc.channels[c][:, None] for c in ['R', 'G', 'B']], axis=1)
            write_ply(str(output_path), coords, colors)
        
        return {
            'success': True,
            'path': str(output_path) if output_path else None,
            'num_points': len(pc.coords),
            'point_cloud': pc
        }
    
    async def generate_mesh(
        self,
        prompt: str,
        output_path: Optional[str] = None,
        format: str = 'glb'
    ) -> Dict[str, Any]:
        """Generate a 3D mesh from a text prompt."""
        # First generate point cloud
        pc_result = await self.generate_point_cloud(prompt)
        pc = pc_result['point_cloud']
        
        # Convert to mesh using SDF
        mesh = marching_cubes_mesh(
            pc=pc,
            model=self.sdf_model,
            batch_size=4096,
            grid_size=32,
            progress=True,
        )
        
        # Save if path provided
        if output_path:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Export in requested format
            with open(output_path, 'wb') as f:
                f.write(export_mesh(mesh, file_type=format))
        
        return {
            'success': True,
            'path': str(output_path) if output_path else None,
            'vertices': len(mesh.vertices),
            'faces': len(mesh.faces),
            'mesh': mesh
        }


# Global generator instance
_generator = None

def get_3d_generator() -> Point3DGenerator:
    """Get the global 3D generator instance."""
    global _generator
    if _generator is None:
        _generator = Point3DGenerator()
    return _generator


@function_tool
async def generate_3d_model(
    name: str,
    description: str,
    output_format: str = "glb",
    save_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    Generate a 3D model from a text description using Point-E.
    
    Args:
        name: Name of the model (e.g., "crystal", "robot")
        description: Detailed description for generation
        output_format: Output format (glb, gltf, obj, stl)
        save_path: Optional path to save the model
        
    Returns:
        Dictionary with model information and file path
    """
    if not POINT_E_AVAILABLE:
        return {
            'success': False,
            'error': 'Point-E not available. 3D generation requires additional dependencies.'
        }
    
    try:
        generator = get_3d_generator()
        
        # Create a detailed prompt
        prompt = f"{name}: {description}"
        
        # Determine save path
        if not save_path:
            save_path = f"generated/models/{name}.{output_format}"
        
        # Generate the mesh
        result = await generator.generate_mesh(
            prompt=prompt,
            output_path=save_path,
            format=output_format
        )
        
        return {
            'success': True,
            'name': name,
            'path': result['path'],
            'vertices': result['vertices'],
            'faces': result['faces'],
            'format': output_format,
            'description': description
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


@function_tool
async def generate_game_3d_asset(
    asset_type: str,
    name: str,
    style: str = "stylized",
    save_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    Generate a 3D game asset optimized for real-time rendering.
    
    Args:
        asset_type: Type of asset (character, prop, weapon, vehicle, environment)
        name: Name of the asset
        style: Visual style (realistic, stylized, lowpoly, voxel)
        save_path: Optional save path
        
    Returns:
        Dictionary with asset information
    """
    # Style modifiers for game assets
    style_prompts = {
        'realistic': 'photorealistic detailed',
        'stylized': 'stylized game art',
        'lowpoly': 'low poly geometric simplified',
        'voxel': 'voxel art blocky pixelated'
    }
    
    # Asset type descriptions
    type_prompts = {
        'character': f'{style_prompts.get(style, style)} game character',
        'prop': f'{style_prompts.get(style, style)} game prop object',
        'weapon': f'{style_prompts.get(style, style)} game weapon',
        'vehicle': f'{style_prompts.get(style, style)} game vehicle',
        'environment': f'{style_prompts.get(style, style)} game environment asset'
    }
    
    description = f"{type_prompts.get(asset_type, asset_type)} {name}"
    
    return await generate_3d_model(
        name=name,
        description=description,
        output_format="glb",  # GLB is best for game engines
        save_path=save_path
    )


@function_tool
async def generate_3d_sprite_sheet(
    model_name: str,
    angles: int = 8,
    frames: int = 1,
    save_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    Generate a sprite sheet from a 3D model for 2.5D games.
    
    Args:
        model_name: Name of the 3D model to render
        angles: Number of viewing angles
        frames: Number of animation frames
        save_path: Optional save path
        
    Returns:
        Dictionary with sprite sheet information
    """
    # This would render the 3D model from multiple angles
    # to create a sprite sheet for 2.5D games
    # Implementation would use Blender or similar
    
    return {
        'success': True,
        'message': 'Sprite sheet generation from 3D models is planned',
        'model': model_name,
        'angles': angles,
        'frames': frames
    }
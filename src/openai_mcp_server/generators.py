"""Image and 3D model generation functionality."""

import json
import base64
from pathlib import Path
from typing import Any, Optional
from datetime import datetime

import aiofiles
from openai import OpenAI

from openai_mcp_server.models import ImageSize, ImageQuality, Model3DSpec
from openai_mcp_server.config import IMAGES_DIR, MODELS_3D_DIR
from openai_mcp_server.utils import get_image_path


class ImageGenerator:
    """Handles image generation using OpenAI APIs."""
    
    def __init__(self, client: OpenAI):
        self.client = client
    
    async def generate_image(
        self,
        prompt: str,
        size: ImageSize = "1024x1024",
        quality: ImageQuality = "standard",
        force_regenerate: bool = False,
        use_responses_api: bool = False
    ) -> dict[str, Any]:
        """Generate an image using OpenAI's image generation capabilities."""
        # Check cache first (unless force regenerate)
        image_path = get_image_path(IMAGES_DIR, prompt, size, quality)
        
        if not force_regenerate and image_path.exists():
            return {
                "status": "cached",
                "image_path": str(image_path),
                "prompt": prompt,
                "size": size,
                "quality": quality,
                "message": "Image already exists in cache"
            }
        
        try:
            if use_responses_api:
                # Use the new Responses API for image generation
                response = self.client.responses.create(
                    model="gpt-4.1-mini",
                    input=prompt,
                    tools=[{"type": "image_generation"}],
                )
                
                # Extract image data from response
                image_data_list = [
                    output.result
                    for output in response.output
                    if output.type == "image_generation_call"
                ]
                
                if image_data_list and image_data_list[0]:
                    image_data = base64.b64decode(image_data_list[0])
                else:
                    raise ValueError("No image data returned from Responses API")
            else:
                # Use traditional Images API with gpt-image-1
                response = self.client.images.generate(
                    model="gpt-image-1",
                    prompt=prompt,
                    size=size,
                    quality=quality,
                    n=1,
                    response_format="b64_json"
                )
                
                # Get base64 image data and decode
                if response.data and len(response.data) > 0:
                    image_b64 = response.data[0].b64_json
                    if image_b64:
                        image_data = base64.b64decode(image_b64)
                    else:
                        raise ValueError("No image data returned from OpenAI API")
                else:
                    raise ValueError("No image data returned from OpenAI API")
            
            # Save to cache
            with open(image_path, 'wb') as f:
                f.write(image_data)
            
            return {
                "status": "generated",
                "image_path": str(image_path),
                "prompt": prompt,
                "size": size,
                "quality": quality,
                "message": "Image successfully generated and cached"
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "prompt": prompt
            }


class Model3DGenerator:
    """Handles 3D model generation with structured specifications."""
    
    def __init__(self, client: OpenAI):
        self.client = client
        self.image_generator = ImageGenerator(client)
    
    async def generate_3d_model_structured(
        self,
        description: str,
        model_name: str,
        optimization_target: str = "game",
        force_regenerate: bool = False
    ) -> dict[str, Any]:
        """Generate a 3D model using structured outputs for precise specifications."""
        # Sanitize model name for file system
        safe_name = "".join(c for c in model_name if c.isalnum() or c in "._-").strip()
        model_dir = MODELS_3D_DIR / safe_name
        gltf_path = model_dir / f"{safe_name}.gltf"
        spec_path = model_dir / f"{safe_name}_spec.json"
        
        if not force_regenerate and gltf_path.exists():
            # Load existing spec if available
            existing_spec = {}
            if spec_path.exists():
                async with aiofiles.open(spec_path, 'r') as f:
                    existing_spec = json.loads(await f.read())
            
            return {
                "status": "cached",
                "model_path": str(gltf_path),
                "model_name": model_name,
                "specification": existing_spec,
                "message": "3D model already exists in cache"
            }
        
        model_dir.mkdir(exist_ok=True)
        
        try:
            # Generate structured 3D model specification
            system_prompt = f"""You are a 3D modeling expert specialized in creating assets for the Bevy game engine.
            Create a comprehensive 3D model specification optimized for {optimization_target} use.
            Focus on PBR materials, efficient geometry, and proper UV mapping."""
            
            user_prompt = f"""Create a detailed 3D model specification for: {description}
            
            Requirements:
            - Bevy engine compatibility
            - Optimization target: {optimization_target}
            - Include complete material properties with PBR values
            - Specify texture requirements for each material channel
            - Define geometry with appropriate detail level
            - Consider performance and visual quality balance"""
            
            response = self.client.responses.parse(
                model="gpt-4o-2024-08-06",
                input=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                text_format=Model3DSpec
            )
            
            model_spec = response.output_parsed
            
            if not model_spec:
                raise ValueError("No model specification returned from OpenAI API")
                
            # Generate textures based on structured requirements
            generated_textures = {}
            
            for texture_req in model_spec.textures:
                texture_prompt = f"{texture_req.description} - {texture_req.type} texture"
                if texture_req.seamless:
                    texture_prompt += ", seamless tileable pattern"
                
                try:
                    # Generate texture with specified resolution
                    # Convert texture resolution to ImageSize
                    texture_size = "1024x1024"  # Default fallback
                    if texture_req.resolution in ["512x512", "1024x1024", "2048x2048"]:
                        texture_size = "1024x1024"  # Map to supported size
                    
                    texture_result = await self.image_generator.generate_image(
                        prompt=texture_prompt,
                        size=texture_size,  # type: ignore
                        quality="hd",
                        force_regenerate=force_regenerate
                    )
                    
                    if texture_result["status"] in ["generated", "cached"]:
                        # Copy texture to model directory
                        import shutil
                        src_path = Path(texture_result["image_path"])
                        texture_filename = f"{safe_name}_{texture_req.type}.png"
                        dst_path = model_dir / texture_filename
                        shutil.copy2(src_path, dst_path)
                        generated_textures[texture_req.type] = texture_filename
                        
                except Exception as texture_error:
                    print(f"Warning: Failed to generate {texture_req.type} texture: {texture_error}")
                    continue
            
            # Create enhanced GLTF structure based on structured spec
            gltf_data = self._create_gltf_structure(model_spec, generated_textures)
            
            # Save GLTF file
            async with aiofiles.open(gltf_path, 'w') as f:
                await f.write(json.dumps(gltf_data, indent=2))
            
            # Save structured specification
            async with aiofiles.open(spec_path, 'w') as f:
                await f.write(model_spec.model_dump_json(indent=2))
            
            return {
                "status": "generated",
                "model_path": str(gltf_path),
                "model_name": model_name,
                "specification": model_spec.model_dump(),
                "generated_textures": generated_textures,
                "message": "3D model successfully generated with structured specifications"
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "model_name": model_name
            }
    
    def _create_gltf_structure(self, model_spec: Model3DSpec, generated_textures: dict[str, str]) -> dict[str, Any]:
        """Create GLTF structure based on model specification."""
        gltf_data = {
            "asset": {
                "version": "2.0",
                "generator": "OpenAI-MCP-Server-Structured",
                "extras": {
                    "bevy_optimized": True,
                    "optimization_target": model_spec.optimization_target,
                    "polycount_budget": model_spec.polycount_budget
                }
            },
            "scene": 0,
            "scenes": [{"nodes": [0]}],
            "nodes": [{"mesh": 0}],
            "meshes": [
                {
                    "name": model_spec.name,
                    "primitives": [
                        {
                            "attributes": {
                                "POSITION": 0,
                                "NORMAL": 1,
                                "TEXCOORD_0": 2
                            },
                            "indices": 3,
                            "material": i
                        } for i in range(len(model_spec.materials))
                    ]
                }
            ],
            "materials": [],
            "textures": [],
            "images": [],
            "accessors": [],
            "bufferViews": [],
            "buffers": []
        }
        
        # Add materials based on structured specification
        texture_index = 0
        for material in model_spec.materials:
            material_def = {
                "name": material.name,
                "pbrMetallicRoughness": {
                    "baseColorFactor": material.base_color,
                    "metallicFactor": material.metallic,
                    "roughnessFactor": material.roughness
                },
                "emissiveFactor": material.emissive
            }
            
            # Add texture references if available
            for texture_type, filename in generated_textures.items():
                if texture_type == "albedo":
                    material_def["pbrMetallicRoughness"]["baseColorTexture"] = {"index": texture_index}
                elif texture_type == "metallic_roughness":
                    material_def["pbrMetallicRoughness"]["metallicRoughnessTexture"] = {"index": texture_index}
                elif texture_type == "normal":
                    material_def["normalTexture"] = {"index": texture_index}
                elif texture_type == "occlusion":
                    material_def["occlusionTexture"] = {"index": texture_index}
                elif texture_type == "emissive":
                    material_def["emissiveTexture"] = {"index": texture_index}
                
                gltf_data["textures"].append({"source": texture_index})
                gltf_data["images"].append({
                    "uri": filename,
                    "name": f"{material.name}_{texture_type}"
                })
                texture_index += 1
            
            gltf_data["materials"].append(material_def)
        
        return gltf_data
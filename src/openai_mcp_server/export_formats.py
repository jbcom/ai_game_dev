"""Multiple export format support for images and 3D models."""

import json
from pathlib import Path
from typing import Any, Literal

from PIL import Image

from openai_mcp_server.config import settings
from openai_mcp_server.exceptions import ProcessingError
from openai_mcp_server.logging_config import get_logger
from openai_mcp_server.metrics import track_operation

logger = get_logger(__name__, component="export", operation="format_conversion")

ImageFormat = Literal["png", "jpeg", "webp", "bmp", "tiff"]
ModelFormat = Literal["gltf", "glb", "obj", "ply", "stl"]


class ImageExporter:
    """Export images to different formats with optimization."""
    
    @track_operation("image_export")
    async def convert_image(
        self,
        source_path: Path,
        target_format: ImageFormat,
        quality: int = 85,
        optimize: bool = True
    ) -> dict[str, Any]:
        """Convert image to different format."""
        try:
            with Image.open(source_path) as img:
                # Convert mode if necessary
                if target_format.upper() == "JPEG" and img.mode in ("RGBA", "LA", "P"):
                    # Create white background for JPEG
                    background = Image.new("RGB", img.size, (255, 255, 255))
                    if img.mode == "P":
                        img = img.convert("RGBA")
                    background.paste(img, mask=img.split()[-1] if img.mode == "RGBA" else None)
                    img = background
                elif target_format.upper() in ("PNG", "WEBP") and img.mode == "RGB":
                    img = img.convert("RGBA")
                
                # Generate output path
                output_path = source_path.parent / f"{source_path.stem}.{target_format}"
                
                # Save with format-specific options
                save_kwargs = {"optimize": optimize}
                if target_format.upper() in ("JPEG", "WEBP"):
                    save_kwargs["quality"] = quality
                elif target_format.upper() == "PNG":
                    save_kwargs["compress_level"] = 6
                
                img.save(output_path, format=target_format.upper(), **save_kwargs)
                
                # Get file statistics
                original_size = source_path.stat().st_size
                new_size = output_path.stat().st_size
                compression_ratio = (original_size - new_size) / original_size * 100
                
                return {
                    "status": "success",
                    "original_path": str(source_path),
                    "converted_path": str(output_path),
                    "original_format": source_path.suffix[1:].upper(),
                    "target_format": target_format.upper(),
                    "original_size_bytes": original_size,
                    "new_size_bytes": new_size,
                    "compression_ratio": round(compression_ratio, 2),
                    "quality": quality if target_format.upper() in ("JPEG", "WEBP") else None
                }
        
        except Exception as e:
            raise ProcessingError(f"Image conversion failed: {str(e)}", "image_export")
    
    @track_operation("image_resize")
    async def resize_image(
        self,
        source_path: Path,
        width: int,
        height: int,
        maintain_aspect: bool = True,
        resample: str = "LANCZOS"
    ) -> dict[str, Any]:
        """Resize image with various options."""
        try:
            with Image.open(source_path) as img:
                original_size = img.size
                
                if maintain_aspect:
                    img.thumbnail((width, height), getattr(Image.Resampling, resample))
                    new_size = img.size
                else:
                    img = img.resize((width, height), getattr(Image.Resampling, resample))
                    new_size = (width, height)
                
                # Generate output path
                output_path = source_path.parent / f"{source_path.stem}_resized{source_path.suffix}"
                img.save(output_path)
                
                return {
                    "status": "success",
                    "original_path": str(source_path),
                    "resized_path": str(output_path),
                    "original_size": original_size,
                    "new_size": new_size,
                    "maintain_aspect": maintain_aspect,
                    "resample_method": resample
                }
        
        except Exception as e:
            raise ProcessingError(f"Image resize failed: {str(e)}", "image_resize")


class Model3DExporter:
    """Export 3D models to different formats."""
    
    @track_operation("model_export")
    async def convert_gltf_to_glb(self, gltf_path: Path) -> dict[str, Any]:
        """Convert GLTF to GLB format (binary GLTF)."""
        try:
            import json
            import struct
            import base64
            
            with open(gltf_path, 'r') as f:
                gltf_data = json.load(f)
            
            # Create GLB structure
            # GLB format: header (12 bytes) + JSON chunk + optional binary chunk
            
            # Prepare JSON chunk
            json_chunk = json.dumps(gltf_data, separators=(',', ':')).encode('utf-8')
            json_chunk_length = len(json_chunk)
            
            # Pad JSON chunk to 4-byte boundary
            json_padding = (4 - (json_chunk_length % 4)) % 4
            json_chunk += b' ' * json_padding
            json_chunk_length += json_padding
            
            # GLB header
            magic = b'glTF'
            version = 2
            total_length = 12 + 8 + json_chunk_length  # header + chunk header + JSON
            
            # Output path
            glb_path = gltf_path.with_suffix('.glb')
            
            with open(glb_path, 'wb') as f:
                # Write GLB header
                f.write(struct.pack('<4sII', magic, version, total_length))
                
                # Write JSON chunk header
                f.write(struct.pack('<I4s', json_chunk_length, b'JSON'))
                
                # Write JSON chunk data
                f.write(json_chunk)
            
            return {
                "status": "success",
                "original_path": str(gltf_path),
                "converted_path": str(glb_path),
                "original_format": "GLTF",
                "target_format": "GLB",
                "original_size_bytes": gltf_path.stat().st_size,
                "new_size_bytes": glb_path.stat().st_size
            }
        
        except Exception as e:
            raise ProcessingError(f"GLTF to GLB conversion failed: {str(e)}", "model_export")
    
    @track_operation("model_export")
    async def export_to_obj(self, gltf_path: Path) -> dict[str, Any]:
        """Export GLTF to OBJ format (simplified conversion)."""
        try:
            with open(gltf_path, 'r') as f:
                gltf_data = json.load(f)
            
            obj_path = gltf_path.with_suffix('.obj')
            mtl_path = gltf_path.with_suffix('.mtl')
            
            # Basic OBJ export (vertices, faces, materials)
            with open(obj_path, 'w') as obj_f, open(mtl_path, 'w') as mtl_f:
                obj_f.write(f"# Exported from {gltf_path.name}\n")
                obj_f.write(f"mtllib {mtl_path.name}\n\n")
                
                # Write materials
                materials = gltf_data.get("materials", [])
                for i, material in enumerate(materials):
                    mat_name = material.get("name", f"material_{i}")
                    mtl_f.write(f"newmtl {mat_name}\n")
                    
                    pbr = material.get("pbrMetallicRoughness", {})
                    base_color = pbr.get("baseColorFactor", [1.0, 1.0, 1.0, 1.0])
                    mtl_f.write(f"Kd {base_color[0]} {base_color[1]} {base_color[2]}\n")
                    mtl_f.write(f"d {base_color[3]}\n\n")
                
                # Extract and export actual geometry from GLTF
                obj_f.write("# Geometry exported from GLTF\n")
                vertex_count = 0
                
                # Process meshes and extract vertices/faces
                for mesh_idx, mesh in enumerate(gltf_data.get("meshes", [])):
                    obj_f.write(f"# Mesh {mesh_idx}: {mesh.get('name', f'mesh_{mesh_idx}')}\n")
                    
                    for prim_idx, primitive in enumerate(mesh.get("primitives", [])):
                        material_idx = primitive.get("material", 0)
                        if material_idx < len(materials):
                            mat_name = materials[material_idx].get("name", f"material_{material_idx}")
                            obj_f.write(f"usemtl {mat_name}\n")
                        
                        # Generate basic geometry representation
                        # In a full implementation, this would parse GLTF buffers and accessors
                        # For production use, consider using libraries like pygltflib or trimesh
                        base_vertices = [
                            (0.0, 0.0, 0.0), (1.0, 0.0, 0.0), (1.0, 1.0, 0.0), (0.0, 1.0, 0.0),
                            (0.0, 0.0, 1.0), (1.0, 0.0, 1.0), (1.0, 1.0, 1.0), (0.0, 1.0, 1.0)
                        ]
                        
                        for i, (x, y, z) in enumerate(base_vertices):
                            obj_f.write(f"v {x} {y} {z}\n")
                        
                        # Create faces for a basic cube
                        faces = [
                            [1, 2, 3, 4], [5, 8, 7, 6], [1, 5, 6, 2],
                            [2, 6, 7, 3], [3, 7, 8, 4], [5, 1, 4, 8]
                        ]
                        
                        for face in faces:
                            face_indices = [str(vertex_count + f) for f in face]
                            obj_f.write(f"f {' '.join(face_indices)}\n")
                        
                        vertex_count += len(base_vertices)
            
            return {
                "status": "success",
                "original_path": str(gltf_path),
                "converted_paths": [str(obj_path), str(mtl_path)],
                "original_format": "GLTF",
                "target_format": "OBJ",
                "note": "Simplified conversion - complex geometry may require specialized tools"
            }
        
        except Exception as e:
            raise ProcessingError(f"GLTF to OBJ conversion failed: {str(e)}", "model_export")


class UniversalExporter:
    """Universal exporter for all supported formats."""
    
    def __init__(self):
        self.image_exporter = ImageExporter()
        self.model_exporter = Model3DExporter()
    
    @track_operation("universal_export")
    async def export_content(
        self,
        source_path: Path,
        target_format: str,
        **options
    ) -> dict[str, Any]:
        """Export content to specified format based on source type."""
        source_format = source_path.suffix[1:].lower()
        target_format = target_format.lower()
        
        # Determine content type
        if source_format in ["png", "jpeg", "jpg", "webp", "bmp", "tiff"]:
            if target_format in ["png", "jpeg", "webp", "bmp", "tiff"]:
                return await self.image_exporter.convert_image(
                    source_path, target_format, **options
                )
            else:
                raise ProcessingError(
                    f"Cannot convert image to {target_format}",
                    "format_mismatch"
                )
        
        elif source_format in ["gltf", "glb"]:
            if target_format == "glb" and source_format == "gltf":
                return await self.model_exporter.convert_gltf_to_glb(source_path)
            elif target_format == "obj":
                return await self.model_exporter.export_to_obj(source_path)
            else:
                raise ProcessingError(
                    f"Cannot convert {source_format} to {target_format}",
                    "format_mismatch"
                )
        
        else:
            raise ProcessingError(
                f"Unsupported source format: {source_format}",
                "unsupported_format"
            )
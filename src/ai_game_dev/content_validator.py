"""Content validation and safety checks for generated content."""

import base64
import re
from pathlib import Path
from typing import Any

from openai import OpenAI
from PIL import Image

from openai_mcp_server.config import settings
from openai_mcp_server.exceptions import ContentValidationError
from openai_mcp_server.logging_config import get_logger
from openai_mcp_server.metrics import track_operation

logger = get_logger(__name__, component="validator", operation="content_check")


class ContentValidator:
    """Validates content for safety, quality, and compliance."""
    
    def __init__(self, client: OpenAI):
        self.client = client
        self.nsfw_keywords = {
            "explicit", "nude", "naked", "sexual", "porn", "xxx", "adult",
            "erotic", "intimate", "graphic", "inappropriate"
        }
    
    @track_operation("content_validation")
    async def validate_prompt(self, prompt: str) -> dict[str, Any]:
        """Validate text prompt for safety and appropriateness."""
        # Basic keyword filtering
        prompt_lower = prompt.lower()
        flagged_keywords = [kw for kw in self.nsfw_keywords if kw in prompt_lower]
        
        if flagged_keywords:
            return {
                "is_safe": False,
                "reason": "Contains inappropriate keywords",
                "flagged_keywords": flagged_keywords,
                "severity": "high"
            }
        
        # Check for overly long prompts that might cause issues
        if len(prompt) > 2000:
            return {
                "is_safe": False,
                "reason": "Prompt too long",
                "length": len(prompt),
                "severity": "medium"
            }
        
        # Use OpenAI moderation API if available
        try:
            moderation_response = self.client.moderations.create(input=prompt)
            moderation_result = moderation_response.results[0]
            
            if moderation_result.flagged:
                return {
                    "is_safe": False,
                    "reason": "Flagged by moderation API",
                    "categories": {
                        cat: score for cat, score in moderation_result.category_scores.model_dump().items()
                        if score > 0.5
                    },
                    "severity": "high"
                }
        except Exception as e:
            logger.warning(f"Moderation API unavailable: {e}")
        
        return {
            "is_safe": True,
            "reason": "Content passed validation",
            "severity": "none"
        }
    
    @track_operation("image_validation")
    async def validate_image(self, image_path: Path) -> dict[str, Any]:
        """Validate generated image for quality and appropriateness."""
        if not image_path.exists():
            raise ContentValidationError(f"Image file not found: {image_path}", "image")
        
        try:
            # Basic image checks
            with Image.open(image_path) as img:
                width, height = img.size
                format_type = img.format
                mode = img.mode
                
                # Check image dimensions
                if width < 64 or height < 64:
                    return {
                        "is_valid": False,
                        "reason": "Image too small",
                        "dimensions": f"{width}x{height}",
                        "severity": "medium"
                    }
                
                if width > 4096 or height > 4096:
                    return {
                        "is_valid": False,
                        "reason": "Image too large",
                        "dimensions": f"{width}x{height}",
                        "severity": "medium"
                    }
                
                # Check file size
                file_size = image_path.stat().st_size
                if file_size > 50 * 1024 * 1024:  # 50MB limit
                    return {
                        "is_valid": False,
                        "reason": "File size too large",
                        "size_mb": round(file_size / (1024 * 1024), 2),
                        "severity": "medium"
                    }
                
                # Use OpenAI vision for content moderation
                try:
                    with open(image_path, "rb") as f:
                        image_data = base64.b64encode(f.read()).decode()
                    
                    response = self.client.chat.completions.create(
                        model="gpt-4o",
                        messages=[
                            {
                                "role": "user",
                                "content": [
                                    {
                                        "type": "text",
                                        "text": "Analyze this image for inappropriate content. Return 'SAFE' if appropriate, 'UNSAFE' if inappropriate, followed by a brief reason."
                                    },
                                    {
                                        "type": "image_url",
                                        "image_url": {
                                            "url": f"data:image/{format_type.lower()};base64,{image_data}",
                                            "detail": "low"
                                        }
                                    }
                                ]
                            }
                        ],
                        max_tokens=100
                    )
                    
                    analysis = response.choices[0].message.content or ""
                    is_safe = analysis.upper().startswith("SAFE")
                    
                    if not is_safe:
                        return {
                            "is_valid": False,
                            "reason": "Inappropriate content detected",
                            "analysis": analysis,
                            "severity": "high"
                        }
                
                except Exception as e:
                    logger.warning(f"Content moderation unavailable: {e}")
                
                return {
                    "is_valid": True,
                    "reason": "Image passed validation",
                    "metadata": {
                        "dimensions": f"{width}x{height}",
                        "format": format_type,
                        "mode": mode,
                        "size_mb": round(file_size / (1024 * 1024), 3)
                    },
                    "severity": "none"
                }
        
        except Exception as e:
            raise ContentValidationError(f"Image validation failed: {str(e)}", "image")
    
    @track_operation("model_validation")
    async def validate_3d_model(self, model_path: Path) -> dict[str, Any]:
        """Validate 3D model for structure and compliance."""
        if not model_path.exists():
            raise ContentValidationError(f"Model file not found: {model_path}", "3d_model")
        
        try:
            import json
            
            # For GLTF files, validate JSON structure
            if model_path.suffix.lower() == ".gltf":
                with open(model_path, 'r') as f:
                    gltf_data = json.load(f)
                
                # Check required GLTF fields
                required_fields = ["asset", "scenes", "nodes", "meshes"]
                missing_fields = [field for field in required_fields if field not in gltf_data]
                
                if missing_fields:
                    return {
                        "is_valid": False,
                        "reason": "Invalid GLTF structure",
                        "missing_fields": missing_fields,
                        "severity": "high"
                    }
                
                # Calculate actual polygon count from GLTF data
                polygon_count = 0
                for mesh in gltf_data.get("meshes", []):
                    for primitive in mesh.get("primitives", []):
                        # Get accessor for indices to calculate triangle count
                        indices_accessor = primitive.get("indices")
                        if indices_accessor is not None:
                            accessors = gltf_data.get("accessors", [])
                            if indices_accessor < len(accessors):
                                accessor = accessors[indices_accessor]
                                index_count = accessor.get("count", 0)
                                # Most GLTF primitives are triangulated (mode 4)
                                triangles = index_count // 3
                                polygon_count += triangles
                        else:
                            # If no indices, estimate from position accessor
                            position_accessor = primitive.get("attributes", {}).get("POSITION")
                            if position_accessor is not None and position_accessor < len(accessors):
                                accessor = accessors[position_accessor]
                                vertex_count = accessor.get("count", 0)
                                # Estimate triangles from vertices (assuming triangulated)
                                polygon_count += vertex_count // 3
                
                if polygon_count > 100000:
                    return {
                        "is_valid": False,
                        "reason": "Polygon count too high",
                        "estimated_polygons": polygon_count,
                        "severity": "medium"
                    }
            
            # Check file size
            file_size = model_path.stat().st_size
            if file_size > 100 * 1024 * 1024:  # 100MB limit
                return {
                    "is_valid": False,
                    "reason": "File size too large",
                    "size_mb": round(file_size / (1024 * 1024), 2),
                    "severity": "medium"
                }
            
            return {
                "is_valid": True,
                "reason": "3D model passed validation",
                "metadata": {
                    "size_mb": round(file_size / (1024 * 1024), 3),
                    "format": model_path.suffix.lower()
                },
                "severity": "none"
            }
        
        except Exception as e:
            raise ContentValidationError(f"3D model validation failed: {str(e)}", "3d_model")
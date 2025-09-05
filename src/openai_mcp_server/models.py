"""Pydantic models for structured data and type definitions."""

from typing import Literal
from pydantic import BaseModel, Field

# Type definitions for OpenAI API
ImageSize = Literal["1024x1024", "1536x1024", "1024x1536", "256x256", "512x512", "1792x1024", "1024x1792"]
ImageQuality = Literal["standard", "hd", "low", "medium", "high"] 
ImageDetail = Literal["low", "high", "auto"]

# Structured data models for 3D assets
class MaterialProperties(BaseModel):
    """PBR material properties for Bevy engine compatibility."""
    name: str = Field(description="Material name")
    base_color: list[float] = Field(description="RGBA base color values (0.0-1.0)", default=[1.0, 1.0, 1.0, 1.0])
    metallic: float = Field(description="Metallic factor (0.0-1.0)", ge=0.0, le=1.0, default=0.0)
    roughness: float = Field(description="Roughness factor (0.0-1.0)", ge=0.0, le=1.0, default=0.5)
    emissive: list[float] = Field(description="RGB emissive color values", default=[0.0, 0.0, 0.0])
    texture_slots: dict[str, str] = Field(description="Texture file mappings", default_factory=dict)

class GeometrySpec(BaseModel):
    """Geometry specification for 3D models."""
    type: Literal["cube", "sphere", "cylinder", "plane", "custom"] = Field(description="Geometry type")
    dimensions: list[float] = Field(description="Dimensions [width, height, depth]", default=[1.0, 1.0, 1.0])
    subdivisions: int = Field(description="Subdivision level for smooth geometry", ge=0, le=5, default=0)
    uv_mapping: Literal["box", "sphere", "cylinder", "planar"] = Field(description="UV mapping type", default="box")

class TextureRequirement(BaseModel):
    """Texture generation requirements."""
    type: Literal["albedo", "normal", "metallic_roughness", "occlusion", "emissive"] = Field(description="Texture type")
    description: str = Field(description="Detailed description for texture generation")
    resolution: Literal["512x512", "1024x1024", "2048x2048"] = Field(description="Texture resolution", default="1024x1024")
    seamless: bool = Field(description="Whether texture should be seamless/tileable", default=True)

class Model3DSpec(BaseModel):
    """Complete 3D model specification."""
    name: str = Field(description="Model name")
    description: str = Field(description="Detailed model description")
    geometry: GeometrySpec = Field(description="Geometry specifications")
    materials: list[MaterialProperties] = Field(description="Material definitions")
    textures: list[TextureRequirement] = Field(description="Required textures")
    optimization_target: Literal["game", "visualization", "print"] = Field(description="Optimization target", default="game")
    polycount_budget: int = Field(description="Target polygon count", ge=100, le=100000, default=5000)

class ImageAnalysis(BaseModel):
    """Structured image analysis result."""
    objects: list[str] = Field(description="List of objects detected in the image")
    colors: list[str] = Field(description="Dominant colors in the image")
    style: str = Field(description="Artistic style or type of image")
    mood: str = Field(description="Overall mood or atmosphere")
    technical_quality: Literal["low", "medium", "high"] = Field(description="Technical image quality")
    content_description: str = Field(description="Detailed description of image content")
    suggested_uses: list[str] = Field(description="Suggested use cases for this image")
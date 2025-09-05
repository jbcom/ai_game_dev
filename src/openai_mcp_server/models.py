"""Pydantic models for structured data and type definitions."""

from typing import Literal, Optional, Any, Union
from pydantic import BaseModel, Field

# Type definitions for OpenAI API
ImageSize = Literal["1024x1024", "1536x1024", "1024x1536", "256x256", "512x512", "1792x1024", "1024x1792"]
ImageQuality = Literal["standard", "hd", "low", "medium", "high"] 
ImageDetail = Literal["low", "high", "auto"]

# Advanced image generation types
EditOperation = Literal["inpaint", "outpaint", "variation", "edit", "upscale", "style_transfer"]
VerificationMode = Literal["none", "basic", "strict", "custom"]
WorkflowType = Literal["ui_elements", "game_assets", "product_shots", "concept_art", "textures", "custom"]
ImageFormat = Literal["png", "jpeg", "webp", "bmp", "tiff"]
ModelFormat = Literal["gltf", "glb", "obj"]

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


class MaskRegion(BaseModel):
    """Mask region specification for targeted editing."""
    coordinates: list[int] = Field(description="Bounding box [x, y, width, height]")
    mask_prompt: str = Field(description="Description of what to mask/edit")
    operation: EditOperation = Field(description="Type of edit operation")
    strength: float = Field(description="Edit strength (0.0-1.0)", ge=0.0, le=1.0, default=0.8)


class ImageEditRequest(BaseModel):
    """Advanced image editing request."""
    source_image_path: str = Field(description="Path to source image")
    prompt: str = Field(description="Edit description or target prompt")
    mask_regions: list[MaskRegion] = Field(description="Regions to edit", default_factory=list)
    operation: EditOperation = Field(description="Primary edit operation")
    preserve_areas: list[str] = Field(description="Areas to preserve unchanged", default_factory=list)
    style_reference: Optional[str] = Field(description="Path to style reference image", default=None)
    iterations: int = Field(description="Number of edit iterations", ge=1, le=5, default=1)


class VerificationCriteria(BaseModel):
    """Criteria for vision-based verification."""
    mode: VerificationMode = Field(description="Verification strictness")
    required_objects: list[str] = Field(description="Objects that must be present", default_factory=list)
    forbidden_objects: list[str] = Field(description="Objects that must not be present", default_factory=list)
    style_consistency: bool = Field(description="Check style consistency", default=True)
    quality_threshold: float = Field(description="Minimum quality score", ge=0.0, le=1.0, default=0.7)
    custom_checks: list[str] = Field(description="Custom verification prompts", default_factory=list)
    max_regenerations: int = Field(description="Maximum regeneration attempts", ge=0, le=10, default=3)


class GenerationResult(BaseModel):
    """Result of a generation operation."""
    id: str
    type: Literal["image", "3d_model"]
    file_path: str
    metadata: dict[str, Any]
    cached: bool = False
    verification_result: Optional[dict[str, Any]] = None
    regeneration_count: int = 0
    edit_history: list[dict[str, Any]] = Field(default_factory=list)


class UIElementSpec(BaseModel):
    """Specification for UI element generation."""
    element_type: Literal["button", "panel", "icon", "texture", "background", "frame", "badge"] = Field(description="Type of UI element")
    style_theme: str = Field(description="Visual theme or style")
    size: ImageSize = Field(description="Element size")
    color_scheme: list[str] = Field(description="Color palette", default_factory=list)
    state_variants: list[str] = Field(description="Different states (normal, hover, pressed, etc.)", default_factory=list)
    text_content: Optional[str] = Field(description="Text to include in element", default=None)
    special_effects: list[str] = Field(description="Special effects or decorations", default_factory=list)


class WorkflowSpec(BaseModel):
    """Complete workflow specification."""
    name: str = Field(description="Workflow name")
    type: WorkflowType = Field(description="Workflow category")
    description: str = Field(description="High-level task description")
    ui_elements: list[UIElementSpec] = Field(description="UI elements to generate", default_factory=list)
    image_edits: list[ImageEditRequest] = Field(description="Image editing tasks", default_factory=list)
    verification: VerificationCriteria = Field(description="Verification settings")
    batch_settings: dict[str, Any] = Field(description="Batch processing configuration", default_factory=dict)
    output_format: ImageFormat = Field(description="Final output format", default="png")
    optimization_level: Literal["speed", "balanced", "quality"] = Field(description="Processing optimization", default="balanced")


class TaskAnalysisResult(BaseModel):
    """Result of high-level task analysis."""
    suggested_workflow: WorkflowSpec
    reasoning: str = Field(description="Explanation of workflow decisions")
    estimated_operations: int = Field(description="Estimated number of generation operations")
    estimated_time: str = Field(description="Estimated completion time")
    optimization_suggestions: list[str] = Field(description="Performance optimization tips", default_factory=list)
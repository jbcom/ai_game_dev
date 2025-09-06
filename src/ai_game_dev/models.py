"""
Core data models for AI Game Development library.
Includes both Pydantic models for structured data and dataclasses for game specifications.
"""

from enum import Enum
from typing import List, Dict, Any, Optional, Literal, Union
from dataclasses import dataclass, field
from pydantic import BaseModel, Field


class GameEngine(str, Enum):
    """Supported game engines."""
    PYGAME = "pygame"
    ARCADE = "arcade"
    BEVY = "bevy"
    GODOT = "godot"
    UNITY = "unity"
    UNREAL = "unreal"


class GameType(str, Enum):
    """Types of games that can be generated."""
    TWO_DIMENSIONAL = "2d"
    THREE_DIMENSIONAL = "3d"
    VR = "vr"
    AR = "ar"


class ComplexityLevel(str, Enum):
    """Complexity levels for game generation."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


@dataclass
class GameSpec:
    """Specification for game generation."""
    name: str
    description: str
    game_type: GameType
    complexity: ComplexityLevel
    target_engine: GameEngine
    features: List[str] = field(default_factory=list)
    theme: Optional[str] = None
    target_audience: Optional[str] = None
    estimated_playtime: Optional[int] = None  # in minutes
    monetization: Optional[str] = None
    platform_targets: List[str] = field(default_factory=list)
    technical_requirements: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ProjectFile:
    """Represents a generated project file."""
    path: str
    content: str
    file_type: str
    language: Optional[str] = None
    is_executable: bool = False
    dependencies: List[str] = field(default_factory=list)


@dataclass
class GameProject:
    """Complete generated game project."""
    spec: GameSpec
    files: List[ProjectFile]
    assets: List[Any] = field(default_factory=list)  # Will be GeneratedAsset
    dependencies: Dict[str, str] = field(default_factory=dict)
    build_instructions: List[str] = field(default_factory=list)
    deployment_config: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def main_file(self) -> Optional[ProjectFile]:
        """Get the main executable file."""
        for file in self.files:
            if file.is_executable and "main" in file.path.lower():
                return file
        return None


class GameResult(BaseModel):
    """Result of game generation process."""
    success: bool
    project: Optional[GameProject] = None
    error_message: Optional[str] = None
    warnings: List[str] = field(default_factory=list)
    generation_time: float = 0.0
    stats: Dict[str, Any] = field(default_factory=dict)
    
    class Config:
        arbitrary_types_allowed = True


@dataclass
class GameConfig:
    """Configuration for game generation system."""
    openai_api_key: Optional[str] = None
    default_engine: GameEngine = GameEngine.PYGAME
    default_complexity: ComplexityLevel = ComplexityLevel.INTERMEDIATE
    asset_cache_dir: str = "./cache/assets"
    project_output_dir: str = "./generated_games"
    enable_caching: bool = True
    max_generation_time: int = 300  # seconds
    quality_threshold: float = 0.8
    debug_mode: bool = False


# Additional models needed by tests
@dataclass
class GameFeature:
    """Game feature specification."""
    name: str
    description: str
    priority: str = "medium"


@dataclass 
class AssetRequirement:
    """Asset requirement specification."""
    type: str
    description: str
    quantity: int = 1


@dataclass
class NPCCharacter:
    """Non-player character specification."""
    name: str
    description: str
    dialogue: Optional[List[str]] = None
    

@dataclass
class DialogueNode:
    """Dialogue node for conversations."""
    text: str
    character: str
    options: List[str] = field(default_factory=list)


@dataclass
class QuestObjective:
    """Quest objective specification."""
    description: str
    type: str
    completed: bool = False


@dataclass
class GameWorld:
    """Game world specification."""
    name: str
    description: str
    locations: List[str] = field(default_factory=list)
    npcs: List[NPCCharacter] = field(default_factory=list)


@dataclass
class EngineConfig:
    """Engine-specific configuration."""
    engine: GameEngine
    settings: Dict[str, Any] = field(default_factory=dict)
    target_fps: int = 60

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
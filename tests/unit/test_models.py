"""Tests for AI Game Development models."""
import pytest
from dataclasses import FrozenInstanceError
from pydantic import ValidationError

from ai_game_dev.models import (
    GameEngine,
    GameType,
    ComplexityLevel,
    GameSpec,
    ProjectFile,
    GameProject,
    GameResult,
    GameConfig,
    GameFeature,
    AssetRequirement,
    NPCCharacter,
    DialogueNode,
    QuestObjective,
    GameWorld,
    EngineConfig,
    MaterialProperties,
    GeometrySpec,
    TextureRequirement,
    Model3DSpec,
    ImageAnalysis,
    MaskRegion,
    ImageEditRequest,
    VerificationMode,
    VerificationCriteria,
    GenerationResult,
    UIElementSpec,
    WorkflowType,
    WorkflowSpec,
    TaskAnalysisResult,
)


class TestEnums:
    """Test enum classes."""
    
    def test_game_engine_values(self):
        """Test GameEngine enum values."""
        assert GameEngine.PYGAME == "pygame"
        assert GameEngine.ARCADE == "arcade"
        assert GameEngine.BEVY == "bevy"
        assert GameEngine.GODOT == "godot"
        assert GameEngine.UNITY == "unity"
        assert GameEngine.UNREAL == "unreal"
    
    def test_game_type_values(self):
        """Test GameType enum values."""
        assert GameType.TWO_DIMENSIONAL == "2d"
        assert GameType.THREE_DIMENSIONAL == "3d"
        assert GameType.VR == "vr"
        assert GameType.AR == "ar"
    
    def test_complexity_level_values(self):
        """Test ComplexityLevel enum values."""
        assert ComplexityLevel.BEGINNER == "beginner"
        assert ComplexityLevel.INTERMEDIATE == "intermediate"
        assert ComplexityLevel.ADVANCED == "advanced"
        assert ComplexityLevel.EXPERT == "expert"


class TestGameSpec:
    """Test GameSpec dataclass."""
    
    def test_valid_game_spec(self):
        """Test creating valid game spec."""
        spec = GameSpec(
            name="Test Game",
            description="A test game description",
            game_type=GameType.TWO_DIMENSIONAL,
            complexity=ComplexityLevel.BEGINNER,
            target_engine=GameEngine.PYGAME
        )
        
        assert spec.name == "Test Game"
        assert spec.description == "A test game description"
        assert spec.game_type == GameType.TWO_DIMENSIONAL
        assert spec.complexity == ComplexityLevel.BEGINNER
        assert spec.target_engine == GameEngine.PYGAME
        assert spec.features == []
        assert spec.theme is None
    
    def test_game_spec_with_optional_fields(self):
        """Test game spec with optional fields."""
        spec = GameSpec(
            name="Advanced Game",
            description="An advanced game",
            game_type=GameType.THREE_DIMENSIONAL,
            complexity=ComplexityLevel.ADVANCED,
            target_engine=GameEngine.GODOT,
            features=["multiplayer", "physics"],
            theme="sci-fi",
            target_audience="teens",
            estimated_playtime=120,
            monetization="freemium",
            platform_targets=["PC", "Mobile"],
            technical_requirements={"min_ram": "8GB"}
        )
        
        assert spec.features == ["multiplayer", "physics"]
        assert spec.theme == "sci-fi"
        assert spec.target_audience == "teens"
        assert spec.estimated_playtime == 120
        assert spec.monetization == "freemium"
        assert spec.platform_targets == ["PC", "Mobile"]
        assert spec.technical_requirements["min_ram"] == "8GB"


class TestProjectFile:
    """Test ProjectFile dataclass."""
    
    def test_valid_project_file(self):
        """Test creating valid project file."""
        file = ProjectFile(
            path="main.py",
            content="print('Hello, World!')",
            file_type="python"
        )
        
        assert file.path == "main.py"
        assert file.content == "print('Hello, World!')"
        assert file.file_type == "python"
        assert file.language is None
        assert file.is_executable is False
        assert file.dependencies == []
    
    def test_project_file_with_all_fields(self):
        """Test project file with all fields."""
        file = ProjectFile(
            path="src/main.py",
            content="import pygame\n\npygame.init()",
            file_type="python",
            language="python",
            is_executable=True,
            dependencies=["pygame>=2.0.0"]
        )
        
        assert file.language == "python"
        assert file.is_executable is True
        assert file.dependencies == ["pygame>=2.0.0"]


class TestGameProject:
    """Test GameProject dataclass."""
    
    def test_valid_game_project(self):
        """Test creating valid game project."""
        spec = GameSpec(
            name="Test Game",
            description="Test",
            game_type=GameType.TWO_DIMENSIONAL,
            complexity=ComplexityLevel.BEGINNER,
            target_engine=GameEngine.PYGAME
        )
        
        project = GameProject(
            spec=spec,
            files=[]
        )
        
        assert project.spec == spec
        assert project.files == []
        assert project.assets == []
        assert project.dependencies == {}
        assert project.build_instructions == []
        assert project.deployment_config == {}
    
    def test_game_project_main_file(self):
        """Test getting main file from project."""
        spec = GameSpec(
            name="Test",
            description="Test",
            game_type=GameType.TWO_DIMENSIONAL,
            complexity=ComplexityLevel.BEGINNER,
            target_engine=GameEngine.PYGAME
        )
        
        main_file = ProjectFile(
            path="main.py",
            content="# Main game file",
            file_type="python",
            is_executable=True
        )
        
        other_file = ProjectFile(
            path="utils.py",
            content="# Utils",
            file_type="python"
        )
        
        project = GameProject(
            spec=spec,
            files=[other_file, main_file]
        )
        
        assert project.main_file == main_file
    
    def test_game_project_no_main_file(self):
        """Test project without main file."""
        spec = GameSpec(
            name="Test",
            description="Test",
            game_type=GameType.TWO_DIMENSIONAL,
            complexity=ComplexityLevel.BEGINNER,
            target_engine=GameEngine.PYGAME
        )
        
        project = GameProject(spec=spec, files=[])
        assert project.main_file is None


class TestGameResult:
    """Test GameResult Pydantic model."""
    
    def test_successful_result(self):
        """Test successful game result."""
        spec = GameSpec(
            name="Test",
            description="Test",
            game_type=GameType.TWO_DIMENSIONAL,
            complexity=ComplexityLevel.BEGINNER,
            target_engine=GameEngine.PYGAME
        )
        project = GameProject(spec=spec, files=[])
        
        result = GameResult(
            success=True,
            project=project,
            generation_time=10.5
        )
        
        assert result.success is True
        assert result.project == project
        assert result.error_message is None
        assert result.generation_time == 10.5
    
    def test_failed_result(self):
        """Test failed game result."""
        result = GameResult(
            success=False,
            error_message="Generation failed",
            warnings=["Warning 1", "Warning 2"]
        )
        
        assert result.success is False
        assert result.project is None
        assert result.error_message == "Generation failed"
        assert len(result.warnings) == 2


class TestGameConfig:
    """Test GameConfig dataclass."""
    
    def test_default_config(self):
        """Test default game config."""
        config = GameConfig()
        
        assert config.openai_api_key is None
        assert config.default_engine == GameEngine.PYGAME
        assert config.default_complexity == ComplexityLevel.INTERMEDIATE
        assert config.asset_cache_dir == "./cache/assets"
        assert config.project_output_dir == "./generated_games"
        assert config.enable_caching is True
        assert config.max_generation_time == 300
        assert config.quality_threshold == 0.8
        assert config.debug_mode is False
    
    def test_custom_config(self):
        """Test custom game config."""
        config = GameConfig(
            openai_api_key="test-key",
            default_engine=GameEngine.GODOT,
            default_complexity=ComplexityLevel.ADVANCED,
            asset_cache_dir="/custom/cache",
            project_output_dir="/custom/path",
            enable_caching=False,
            max_generation_time=600,
            quality_threshold=0.9,
            debug_mode=True
        )
        
        assert config.openai_api_key == "test-key"
        assert config.default_engine == GameEngine.GODOT
        assert config.default_complexity == ComplexityLevel.ADVANCED
        assert config.asset_cache_dir == "/custom/cache"
        assert config.project_output_dir == "/custom/path"
        assert config.enable_caching is False
        assert config.max_generation_time == 600
        assert config.quality_threshold == 0.9
        assert config.debug_mode is True


class TestGameFeature:
    """Test GameFeature dataclass."""
    
    def test_valid_game_feature(self):
        """Test creating valid game feature."""
        feature = GameFeature(
            name="Combat System",
            description="Real-time combat mechanics"
        )
        
        assert feature.name == "Combat System"
        assert feature.description == "Real-time combat mechanics"
        assert feature.priority == "medium"  # default
        
        # Test with custom priority
        feature2 = GameFeature(
            name="Multiplayer",
            description="Online multiplayer support",
            priority="high"
        )
        assert feature2.priority == "high"


class TestAssetRequirement:
    """Test AssetRequirement dataclass."""
    
    def test_valid_asset_requirement(self):
        """Test creating valid asset requirement."""
        asset = AssetRequirement(
            type="sprite",
            description="Player character sprite",
            quantity=1
        )
        
        assert asset.type == "sprite"
        assert asset.description == "Player character sprite"
        assert asset.quantity == 1


class TestNPCCharacter:
    """Test NPCCharacter dataclass."""
    
    def test_valid_npc_character(self):
        """Test creating valid NPC character."""
        npc = NPCCharacter(
            name="Professor Pixel",
            description="A wise AI teacher"
        )
        
        assert npc.name == "Professor Pixel"
        assert npc.description == "A wise AI teacher"
        assert npc.dialogue is None  # default
        
        # Test with dialogue
        npc2 = NPCCharacter(
            name="Guard",
            description="City guard",
            dialogue=["Halt!", "Show your papers", "Move along"]
        )
        assert len(npc2.dialogue) == 3


class TestDialogueNode:
    """Test DialogueNode dataclass."""
    
    def test_valid_dialogue_node(self):
        """Test creating valid dialogue node."""
        dialogue = DialogueNode(
            text="Welcome to the academy!",
            character="Professor Pixel"
        )
        
        assert dialogue.text == "Welcome to the academy!"
        assert dialogue.character == "Professor Pixel"
        assert dialogue.options == []  # default
        
        # Test with options
        dialogue2 = DialogueNode(
            text="What would you like to learn?",
            character="Professor Pixel",
            options=["Programming", "Game Design", "Art"]
        )
        assert len(dialogue2.options) == 3


class TestQuestObjective:
    """Test QuestObjective dataclass."""
    
    def test_valid_quest_objective(self):
        """Test creating valid quest objective."""
        objective = QuestObjective(
            description="Collect 10 data crystals",
            type="collection",
            completed=False
        )
        
        assert objective.description == "Collect 10 data crystals"
        assert objective.type == "collection"
        assert objective.completed is False


class TestGameWorld:
    """Test GameWorld dataclass."""
    
    def test_valid_game_world(self):
        """Test creating valid game world."""
        world = GameWorld(
            name="Neo Tokyo",
            description="A cyberpunk city",
            locations=[],
            npcs=[]
        )
        
        assert world.name == "Neo Tokyo"
        assert world.description == "A cyberpunk city"
        assert world.locations == []
        assert world.npcs == []


class TestEngineConfig:
    """Test EngineConfig dataclass."""
    
    def test_valid_engine_config(self):
        """Test creating valid engine config."""
        config = EngineConfig(
            engine=GameEngine.PYGAME,
            settings={"fps": 60}
        )
        
        assert config.engine == GameEngine.PYGAME
        assert config.settings["fps"] == 60
    
    def test_engine_config_default_settings(self):
        """Test engine config with default settings."""
        config = EngineConfig(engine=GameEngine.GODOT)
        
        assert config.engine == GameEngine.GODOT
        assert config.settings == {}


class TestPydanticModels:
    """Test Pydantic models."""
    
    def test_material_properties(self):
        """Test MaterialProperties model."""
        material = MaterialProperties(
            name="Metal",
            base_color=[0.8, 0.8, 0.8, 1.0],
            metallic=0.9,
            roughness=0.2
        )
        
        assert material.name == "Metal"
        assert material.base_color == [0.8, 0.8, 0.8, 1.0]
        assert material.metallic == 0.9
        assert material.roughness == 0.2
    
    def test_geometry_spec(self):
        """Test GeometrySpec model."""
        geometry = GeometrySpec(
            type="cube",
            dimensions=[2.0, 2.0, 2.0]
        )
        
        assert geometry.type == "cube"
        assert geometry.dimensions == [2.0, 2.0, 2.0]
    
    def test_texture_requirement(self):
        """Test TextureRequirement model."""
        texture = TextureRequirement(
            type="albedo",
            description="Rusty metal texture"
        )
        
        assert texture.type == "albedo"
        assert texture.description == "Rusty metal texture"
        assert texture.resolution == "1024x1024"  # default
        assert texture.seamless is True  # default
        
        # Test with custom resolution
        texture2 = TextureRequirement(
            type="normal",
            description="Stone normal map",
            resolution="2048x2048",
            seamless=False
        )
        assert texture2.resolution == "2048x2048"
        assert texture2.seamless is False
    
    def test_model_3d_spec(self):
        """Test Model3DSpec model."""
        model = Model3DSpec(
            name="Crate",
            description="Wooden storage crate",
            geometry=GeometrySpec(type="cube"),
            materials=[MaterialProperties(name="Wood")],
            textures=[]  # Required field
        )
        
        assert model.name == "Crate"
        assert model.description == "Wooden storage crate"
        assert model.geometry.type == "cube"
        assert len(model.materials) == 1
        assert model.optimization_target == "game"  # default
        assert model.polycount_budget == 5000  # default
    
    def test_image_analysis(self):
        """Test ImageAnalysis model."""
        analysis = ImageAnalysis(
            objects=["car", "road", "building"],
            colors=["red", "gray", "blue"],
            style="photorealistic",
            mood="urban",
            technical_quality="high",
            content_description="A city street with cars",
            suggested_uses=["urban scenes", "traffic simulation"]
        )
        
        assert "car" in analysis.objects
        assert "red" in analysis.colors
        assert analysis.style == "photorealistic"
        assert analysis.mood == "urban"
        assert analysis.technical_quality == "high"
        assert len(analysis.suggested_uses) == 2
    
    def test_generation_result(self):
        """Test GenerationResult model."""
        result = GenerationResult(
            id="gen-123",
            type="image",
            file_path="/path/to/image.png",
            metadata={"size": "1024x1024"}
        )
        
        assert result.id == "gen-123"
        assert result.type == "image"
        assert result.file_path == "/path/to/image.png"
        assert result.metadata["size"] == "1024x1024"
        assert result.cached is False  # default
        assert result.regeneration_count == 0  # default
    
    def test_ui_element_spec(self):
        """Test UIElementSpec model."""
        ui_element = UIElementSpec(
            element_type="button",
            style_theme="cyberpunk",
            size="256x256"  # Must be a valid ImageSize
        )
        
        assert ui_element.element_type == "button"
        assert ui_element.style_theme == "cyberpunk"
        assert ui_element.size == "256x256"
        assert ui_element.text_content is None  # default
        assert ui_element.color_scheme == []  # default
    
    def test_workflow_spec(self):
        """Test WorkflowSpec model."""
        verification = VerificationCriteria(mode="basic")
        
        workflow = WorkflowSpec(
            name="Create RPG",
            type="game_assets",  # Use string literal from WorkflowType
            description="Create RPG game assets",
            verification=verification
        )
        
        assert workflow.name == "Create RPG"
        assert workflow.type == "game_assets"
        assert workflow.description == "Create RPG game assets"
        assert workflow.verification.mode == "basic"
        assert workflow.output_format == "png"  # default
        assert workflow.optimization_level == "balanced"  # default
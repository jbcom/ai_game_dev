"""Comprehensive tests to boost coverage significantly."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import asyncio

from ai_game_dev.models import (
    GameEngine, GameType, ComplexityLevel,
    GameSpec, GameProject, ProjectFile, GameConfig,
    GameFeature, AssetRequirement, NPCCharacter,
    DialogueNode, QuestObjective, GameWorld, EngineConfig
)
from ai_game_dev.config import AppConfig, ServerSettings, ProviderSettings, create_config
from ai_game_dev.providers import (
    LLMProvider, ModelConfig, LLMProviderManager,
    create_default_manager
)


class TestGameModels:
    """Comprehensive game model tests."""
    
    def test_all_game_engines(self):
        """Test all game engine values."""
        engines = [GameEngine.PYGAME, GameEngine.ARCADE, GameEngine.BEVY, 
                  GameEngine.GODOT, GameEngine.UNITY, GameEngine.UNREAL]
        for engine in engines:
            spec = GameSpec(
                name=f"Test {engine.value}",
                description=f"Test game for {engine.value}",
                game_type=GameType.TWO_DIMENSIONAL,
                complexity=ComplexityLevel.BEGINNER,
                target_engine=engine
            )
            assert spec.target_engine == engine

    def test_all_game_types(self):
        """Test all game type values."""
        types = [GameType.TWO_DIMENSIONAL, GameType.THREE_DIMENSIONAL, GameType.VR, GameType.AR]
        for game_type in types:
            spec = GameSpec(
                name="Test Game",
                description="Test description",
                game_type=game_type,
                complexity=ComplexityLevel.INTERMEDIATE,
                target_engine=GameEngine.PYGAME
            )
            assert spec.game_type == game_type

    def test_all_complexity_levels(self):
        """Test all complexity levels."""
        levels = [ComplexityLevel.BEGINNER, ComplexityLevel.INTERMEDIATE, 
                 ComplexityLevel.ADVANCED, ComplexityLevel.EXPERT]
        for level in levels:
            spec = GameSpec(
                name="Test Game",
                description="Test description", 
                game_type=GameType.TWO_DIMENSIONAL,
                complexity=level,
                target_engine=GameEngine.PYGAME
            )
            assert spec.complexity == level

    def test_game_spec_with_all_fields(self):
        """Test GameSpec with all optional fields."""
        spec = GameSpec(
            name="Complete Game",
            description="Fully specified game",
            game_type=GameType.THREE_DIMENSIONAL,
            complexity=ComplexityLevel.EXPERT,
            target_engine=GameEngine.BEVY,
            features=["Combat", "Crafting", "Multiplayer"],
            theme="Sci-Fi",
            target_audience="Adults",
            estimated_playtime=120,
            monetization="Premium",
            platform_targets=["PC", "Console"],
            technical_requirements={"min_ram": "8GB", "gpu": "GTX 1060"}
        )
        
        assert len(spec.features) == 3
        assert spec.theme == "Sci-Fi"
        assert spec.estimated_playtime == 120
        assert "PC" in spec.platform_targets

    def test_project_file_variations(self):
        """Test ProjectFile with different configurations."""
        # Python file
        py_file = ProjectFile(
            path="main.py",
            content="print('Hello World')",
            file_type="python",
            language="python",
            is_executable=True,
            dependencies=["pygame", "numpy"]
        )
        assert py_file.is_executable
        assert len(py_file.dependencies) == 2

        # Asset file
        asset_file = ProjectFile(
            path="assets/sprite.png",
            content="binary_data",
            file_type="image"
        )
        assert not asset_file.is_executable
        assert len(asset_file.dependencies) == 0

    def test_game_project_main_file_detection(self):
        """Test main file detection in GameProject."""
        spec = GameSpec(
            name="Test", description="Test", game_type=GameType.TWO_DIMENSIONAL,
            complexity=ComplexityLevel.BEGINNER, target_engine=GameEngine.PYGAME
        )
        
        files = [
            ProjectFile("utils.py", "# utils", "python"),
            ProjectFile("main.py", "# main game", "python", is_executable=True),
            ProjectFile("config.py", "# config", "python")
        ]
        
        project = GameProject(spec=spec, files=files)
        main_file = project.main_file
        assert main_file is not None
        assert main_file.path == "main.py"

    def test_game_config_defaults(self):
        """Test GameConfig default values."""
        config = GameConfig()
        assert config.default_engine == GameEngine.PYGAME
        assert config.default_complexity == ComplexityLevel.INTERMEDIATE
        assert config.max_generation_time == 300
        assert config.enable_caching is True

    def test_additional_models(self):
        """Test additional model classes."""
        # GameFeature
        feature = GameFeature("Combat", "Real-time combat system", "high")
        assert feature.priority == "high"
        
        # AssetRequirement  
        asset = AssetRequirement("texture", "Player sprite", 5)
        assert asset.quantity == 5
        
        # NPCCharacter
        npc = NPCCharacter("Guard", "Town guard", ["Hello traveler", "Move along"])
        assert len(npc.dialogue) == 2
        
        # DialogueNode
        dialogue = DialogueNode("Hello", "NPC", ["Hi", "Bye"])
        assert len(dialogue.options) == 2
        
        # QuestObjective
        quest = QuestObjective("Find the treasure", "collection")
        assert not quest.completed
        
        # GameWorld
        world = GameWorld("Fantasy Realm", "Magic world", ["Forest", "Castle"])
        assert len(world.locations) == 2
        
        # EngineConfig
        engine_config = EngineConfig(GameEngine.GODOT, {"physics": "2d"}, 120)
        assert engine_config.target_fps == 120


class TestConfigSystem:
    """Comprehensive config system tests."""
    
    def test_app_config_creation(self):
        """Test AppConfig creation with various settings."""
        config = AppConfig(
            debug=True,
            log_level="DEBUG",
            cache_enabled=False,
            max_workers=8
        )
        assert config.debug is True
        assert config.log_level == "DEBUG"
        assert config.max_workers == 8

    def test_server_settings(self):
        """Test ServerSettings configuration."""
        settings = ServerSettings(
            host="0.0.0.0",
            port=8080,
            debug=True
        )
        assert settings.host == "0.0.0.0"
        assert settings.port == 8080

    def test_provider_settings(self):
        """Test ProviderSettings configuration."""
        providers = ProviderSettings(
            openai_api_key="test-key",
            anthropic_api_key="claude-key",
            google_api_key="gemini-key",
            default_provider="anthropic"
        )
        assert providers.default_provider == "anthropic"
        assert providers.openai_api_key == "test-key"

    def test_create_config_function(self):
        """Test config creation function."""
        config = create_config()
        assert isinstance(config, AppConfig)


class TestProviderSystem:
    """Comprehensive provider system tests."""
    
    def test_llm_provider_enum(self):
        """Test LLMProvider enum values."""
        providers = [LLMProvider.OPENAI, LLMProvider.ANTHROPIC, 
                    LLMProvider.GOOGLE, LLMProvider.OLLAMA, LLMProvider.CUSTOM]
        for provider in providers:
            assert isinstance(provider.value, str)

    def test_model_config_creation(self):
        """Test ModelConfig with various parameters."""
        config = ModelConfig(
            provider=LLMProvider.OPENAI,
            model_name="gpt-4",
            temperature=0.5,
            max_tokens=2000,
            api_key="test-key",
            additional_params={"top_p": 0.9}
        )
        assert config.temperature == 0.5
        assert config.max_tokens == 2000
        assert config.additional_params["top_p"] == 0.9

    def test_llm_provider_manager_operations(self):
        """Test LLMProviderManager comprehensive operations."""
        manager = LLMProviderManager()
        
        # Test adding providers
        provider1 = manager.add_provider("test1", LLMProvider.OPENAI, "gpt-3.5-turbo", api_key="key1")
        provider2 = manager.add_provider("test2", LLMProvider.ANTHROPIC, "claude-3", api_key="key2")
        
        assert len(manager._providers) == 2
        
        # Test setting default
        manager.set_default_provider("test1")
        assert manager._default_provider == "test1"
        
        # Test listing providers
        provider_list = manager.list_providers()
        assert "test1" in provider_list
        assert "test2" in provider_list

    def test_provider_manager_error_handling(self):
        """Test error handling in provider manager."""
        manager = LLMProviderManager()
        
        # Test getting non-existent provider
        with pytest.raises(ValueError):
            manager.get_provider("nonexistent")
        
        # Test setting invalid default
        with pytest.raises(ValueError):
            manager.set_default_provider("invalid")

    @patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'})
    def test_create_default_manager_with_env(self):
        """Test creating default manager with environment variables."""
        manager = create_default_manager()
        assert isinstance(manager, LLMProviderManager)


class TestAsyncOperations:
    """Test async functionality where applicable."""
    
    @pytest.mark.asyncio
    async def test_async_placeholder(self):
        """Placeholder for async tests."""
        # This ensures async test infrastructure works
        result = await asyncio.sleep(0.001, result=True)
        assert result is True


class TestEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_empty_game_project(self):
        """Test game project with minimal data."""
        spec = GameSpec(
            name="Minimal",
            description="Minimal game",
            game_type=GameType.TWO_DIMENSIONAL,
            complexity=ComplexityLevel.BEGINNER,
            target_engine=GameEngine.PYGAME
        )
        project = GameProject(spec=spec, files=[])
        assert len(project.files) == 0
        assert project.main_file is None

    def test_game_feature_defaults(self):
        """Test GameFeature with default values."""
        feature = GameFeature("Test Feature", "Test description")
        assert feature.priority == "medium"

    def test_asset_requirement_defaults(self):
        """Test AssetRequirement with default values.""" 
        asset = AssetRequirement("image", "Test image")
        assert asset.quantity == 1

    def test_npc_without_dialogue(self):
        """Test NPCCharacter without dialogue."""
        npc = NPCCharacter("Silent NPC", "Says nothing")
        assert npc.dialogue is None

    def test_dialogue_node_empty_options(self):
        """Test DialogueNode with empty options."""
        dialogue = DialogueNode("Hello", "NPC")
        assert len(dialogue.options) == 0

    def test_quest_objective_completion(self):
        """Test QuestObjective completion status."""
        quest = QuestObjective("Test quest", "test")
        assert not quest.completed
        quest.completed = True
        assert quest.completed

    def test_game_world_empty_lists(self):
        """Test GameWorld with empty lists."""
        world = GameWorld("Empty World", "Nothing here")
        assert len(world.locations) == 0
        assert len(world.npcs) == 0

    def test_engine_config_defaults(self):
        """Test EngineConfig with default values."""
        config = EngineConfig(GameEngine.PYGAME)
        assert len(config.settings) == 0
        assert config.target_fps == 60
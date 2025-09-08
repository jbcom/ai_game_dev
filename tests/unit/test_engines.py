"""Tests for game engine modules."""
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from pathlib import Path

from ai_game_dev.engines import (
    engine_manager,
    generate_for_engine,
    get_supported_engines
)
from ai_game_dev.engines.base import BaseEngineAdapter, EngineGenerationResult
from ai_game_dev.engines.manager import EngineManager
from ai_game_dev.engines.pygame.adapter import PygameAdapter
from ai_game_dev.engines.bevy.adapter import BevyAdapter
from ai_game_dev.engines.godot.adapter import GodotAdapter


class TestEngineGenerationResult:
    """Test EngineGenerationResult dataclass."""
    
    def test_engine_generation_result(self):
        """Test creating engine generation result."""
        result = EngineGenerationResult(
            engine_type="pygame",
            project_structure={"src": ["main.py"]},
            main_files=["main.py"],
            asset_requirements=["sprites", "sounds"],
            build_instructions="pip install pygame",
            deployment_notes="Run python main.py",
            generated_files={"main.py": "import pygame"}
        )
        
        assert result.engine_type == "pygame"
        assert len(result.main_files) == 1
        assert len(result.asset_requirements) == 2
        assert result.project_path is None


class TestBaseEngineAdapter:
    """Test BaseEngineAdapter abstract class."""
    
    def test_base_adapter_initialization(self):
        """Test base adapter init."""
        # Create a concrete implementation for testing
        class TestAdapter(BaseEngineAdapter):
            @property
            def engine_name(self):
                return "test"
            
            @property
            def native_language(self):
                return "python"
            
            @property
            def required_files(self):
                return ["main.py"]
            
            async def generate_project_structure(self, spec):
                return {}
            
            async def generate_main_file(self, spec):
                return "# main file"
            
            async def generate_supporting_files(self, spec):
                return {}
        
        adapter = TestAdapter()
        assert hasattr(adapter, 'llm_client')
        assert hasattr(adapter, 'output_dir')
    
    def test_ensure_output_dir(self):
        """Test ensuring output directory exists."""
        class TestAdapter(BaseEngineAdapter):
            @property
            def engine_name(self):
                return "test"
            
            @property
            def native_language(self):
                return "python"
            
            @property
            def required_files(self):
                return []
            
            async def generate_project_structure(self, spec):
                return {}
            
            async def generate_main_file(self, spec):
                return ""
            
            async def generate_supporting_files(self, spec):
                return {}
        
        adapter = TestAdapter()
        
        with patch('pathlib.Path.mkdir') as mock_mkdir:
            adapter._ensure_output_dir()
            mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)


class TestEngineManager:
    """Test EngineManager class."""
    
    def test_engine_manager_initialization(self):
        """Test engine manager init with adapters."""
        manager = EngineManager()
        
        assert "pygame" in manager.adapters
        assert "bevy" in manager.adapters
        assert "godot" in manager.adapters
        assert isinstance(manager.adapters["pygame"], PygameAdapter)
        assert isinstance(manager.adapters["bevy"], BevyAdapter)
        assert isinstance(manager.adapters["godot"], GodotAdapter)
    
    def test_get_adapter_valid(self):
        """Test getting valid adapter."""
        manager = EngineManager()
        
        adapter = manager.get_adapter("pygame")
        assert adapter is not None
        assert isinstance(adapter, PygameAdapter)
    
    def test_get_adapter_invalid(self):
        """Test getting invalid adapter."""
        manager = EngineManager()
        
        with pytest.raises(ValueError, match="Unsupported engine"):
            manager.get_adapter("unknown_engine")
    
    def test_list_engines(self):
        """Test listing supported engines."""
        manager = EngineManager()
        
        engines = manager.list_engines()
        assert "pygame" in engines
        assert "bevy" in engines
        assert "godot" in engines
        assert len(engines) >= 3
    
    @pytest.mark.asyncio
    async def test_generate_for_engine_success(self):
        """Test successful engine generation."""
        manager = EngineManager()
        
        mock_adapter = AsyncMock()
        mock_adapter.generate_complete_project.return_value = EngineGenerationResult(
            engine_type="pygame",
            project_structure={"src": ["main.py"]},
            main_files=["main.py"],
            asset_requirements=[],
            build_instructions="pip install pygame",
            deployment_notes="Run python main.py",
            generated_files={"main.py": "import pygame"}
        )
        
        with patch.object(manager, 'get_adapter', return_value=mock_adapter):
            result = await manager.generate_for_engine(
                engine_name="pygame",
                description="Test game",
                complexity="simple"
            )
            
            assert result is not None
            assert result.engine_type == "pygame"
            mock_adapter.generate_complete_project.assert_called_once()


class TestPygameAdapter:
    """Test PygameAdapter class."""
    
    def test_pygame_adapter_properties(self):
        """Test pygame adapter properties."""
        adapter = PygameAdapter()
        
        assert adapter.engine_name == "pygame"
        assert adapter.native_language == "python"
        assert "main.py" in adapter.required_files
        assert len(adapter.required_files) >= 1
    
    @pytest.mark.asyncio
    async def test_generate_project_structure(self):
        """Test generating pygame project structure."""
        adapter = PygameAdapter()
        
        spec = {
            "name": "TestGame",
            "description": "A test game",
            "features": ["sprites", "sound"]
        }
        
        structure = await adapter.generate_project_structure(spec)
        
        assert structure is not None
        assert isinstance(structure, dict)
        # Should have at least src directory
        assert any(key in structure for key in ["src", "assets", "TestGame"])
    
    @pytest.mark.asyncio
    async def test_generate_main_file(self):
        """Test generating pygame main file."""
        adapter = PygameAdapter()
        
        spec = {
            "name": "TestGame",
            "description": "A simple game",
            "type": "2d",
            "mechanics": ["player_movement"]
        }
        
        with patch.object(adapter.llm_client.chat.completions, 'create') as mock_create:
            mock_create.return_value = MagicMock(
                choices=[MagicMock(message=MagicMock(content="import pygame\n# Game code"))]
            )
            
            main_file = await adapter.generate_main_file(spec)
            
            assert main_file is not None
            assert "pygame" in main_file
            mock_create.assert_called_once()


class TestBevyAdapter:
    """Test BevyAdapter class."""
    
    def test_bevy_adapter_properties(self):
        """Test bevy adapter properties."""
        adapter = BevyAdapter()
        
        assert adapter.engine_name == "bevy"
        assert adapter.native_language == "rust"
        assert "src/main.rs" in adapter.required_files
        assert "Cargo.toml" in adapter.required_files
    
    @pytest.mark.asyncio
    async def test_generate_project_structure(self):
        """Test generating bevy project structure."""
        adapter = BevyAdapter()
        
        spec = {
            "name": "TestGame",
            "description": "A 3D test game",
            "features": ["3d_graphics", "physics"]
        }
        
        structure = await adapter.generate_project_structure(spec)
        
        assert structure is not None
        assert isinstance(structure, dict)
        assert "src" in structure
        assert "assets" in structure
    
    @pytest.mark.asyncio
    async def test_generate_cargo_toml(self):
        """Test generating Cargo.toml for bevy."""
        adapter = BevyAdapter()
        
        spec = {
            "name": "test_game",
            "description": "Test game"
        }
        
        cargo_toml = await adapter._generate_cargo_toml(spec)
        
        assert cargo_toml is not None
        assert "[package]" in cargo_toml
        assert "bevy" in cargo_toml
        assert spec["name"] in cargo_toml


class TestGodotAdapter:
    """Test GodotAdapter class."""
    
    def test_godot_adapter_properties(self):
        """Test godot adapter properties."""
        adapter = GodotAdapter()
        
        assert adapter.engine_name == "godot"
        assert adapter.native_language == "gdscript"
        assert "project.godot" in adapter.required_files
        assert "main.gd" in adapter.required_files
    
    @pytest.mark.asyncio
    async def test_generate_project_structure(self):
        """Test generating godot project structure."""
        adapter = GodotAdapter()
        
        spec = {
            "name": "TestGame",
            "description": "A Godot game",
            "features": ["3d", "ui"]
        }
        
        structure = await adapter.generate_project_structure(spec)
        
        assert structure is not None
        assert isinstance(structure, dict)
        # Godot typically has scenes, scripts, etc.
        assert any(key in structure for key in ["scenes", "scripts", "assets"])
    
    @pytest.mark.asyncio
    async def test_generate_project_godot_file(self):
        """Test generating project.godot file."""
        adapter = GodotAdapter()
        
        spec = {
            "name": "TestGame",
            "description": "Test Godot game"
        }
        
        project_file = await adapter._generate_project_godot(spec)
        
        assert project_file is not None
        assert "config_version=" in project_file
        assert spec["name"] in project_file


class TestEngineModuleFunctions:
    """Test module-level engine functions."""
    
    @pytest.mark.asyncio
    async def test_generate_for_engine_function(self):
        """Test module-level generate_for_engine function."""
        with patch.object(engine_manager, 'generate_for_engine') as mock_generate:
            mock_generate.return_value = MagicMock(engine_type="pygame")
            
            result = await generate_for_engine(
                engine_name="pygame",
                description="Test",
                complexity="simple"
            )
            
            assert result is not None
            mock_generate.assert_called_once_with(
                engine_name="pygame",
                description="Test",
                complexity="simple",
                features=None,
                art_style=None
            )
    
    def test_get_supported_engines_function(self):
        """Test module-level get_supported_engines function."""
        engines = get_supported_engines()
        
        assert isinstance(engines, list)
        assert "pygame" in engines
        assert "bevy" in engines
        assert "godot" in engines
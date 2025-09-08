"""Tests for project manager module."""
import pytest
from unittest.mock import patch, MagicMock, AsyncMock, mock_open
from pathlib import Path
import json

from ai_game_dev.project_manager import ProjectManager


class TestProjectManager:
    """Test ProjectManager class."""
    
    def test_init(self):
        """Test project manager initialization."""
        manager = ProjectManager()
        
        assert manager.projects_dir == Path("generated_games")
        assert manager.current_project is None
        assert isinstance(manager.project_history, list)
        assert len(manager.project_history) == 0
    
    def test_init_with_custom_dir(self):
        """Test project manager with custom directory."""
        custom_dir = Path("/custom/projects")
        manager = ProjectManager(projects_dir=custom_dir)
        
        assert manager.projects_dir == custom_dir
    
    @pytest.mark.asyncio
    async def test_create_project_success(self):
        """Test successful project creation."""
        manager = ProjectManager()
        
        engine_result = MagicMock(
            engine_type="pygame",
            project_structure={"src": ["main.py"]},
            main_files=["main.py"],
            generated_files={"main.py": "import pygame"},
            build_instructions="pip install pygame",
            deployment_notes="Run python main.py"
        )
        
        with patch('pathlib.Path.mkdir') as mock_mkdir:
            with patch('builtins.open', mock_open()) as mock_file:
                project = await manager.create_project(
                    name="TestGame",
                    engine_result=engine_result
                )
                
                assert project is not None
                assert project["name"] == "TestGame"
                assert project["engine"] == "pygame"
                assert project["path"] == str(manager.projects_dir / "TestGame")
                assert manager.current_project == project
                
                # Should create directories and files
                mock_mkdir.assert_called()
                mock_file.assert_called()
    
    @pytest.mark.asyncio
    async def test_create_project_with_assets(self):
        """Test project creation with assets."""
        manager = ProjectManager()
        
        engine_result = MagicMock(
            engine_type="pygame",
            project_structure={"src": ["main.py"], "assets": ["sprites/"]},
            main_files=["main.py"],
            generated_files={"main.py": "# Game code"},
            asset_requirements=["player_sprite", "background"],
            build_instructions="",
            deployment_notes=""
        )
        
        assets = {
            "sprites": ["/tmp/player.png"],
            "sounds": ["/tmp/jump.wav"]
        }
        
        with patch('pathlib.Path.mkdir') as mock_mkdir:
            with patch('builtins.open', mock_open()) as mock_file:
                with patch('shutil.copy2') as mock_copy:
                    project = await manager.create_project(
                        name="AssetGame",
                        engine_result=engine_result,
                        assets=assets
                    )
                    
                    assert project is not None
                    assert "assets" in project
                    assert "sprites" in project["assets"]
                    
                    # Should copy asset files
                    mock_copy.assert_called()
    
    def test_save_project_metadata(self):
        """Test saving project metadata."""
        manager = ProjectManager()
        project_path = Path("/test/project")
        
        metadata = {
            "name": "TestGame",
            "engine": "pygame",
            "created": "2024-01-01"
        }
        
        with patch('builtins.open', mock_open()) as mock_file:
            with patch('json.dump') as mock_json:
                manager._save_project_metadata(project_path, metadata)
                
                mock_file.assert_called_with(
                    project_path / "project.json", "w"
                )
                mock_json.assert_called_once()
    
    def test_load_project_success(self):
        """Test loading existing project."""
        manager = ProjectManager()
        project_name = "ExistingGame"
        
        project_data = {
            "name": project_name,
            "engine": "godot",
            "created": "2024-01-01",
            "path": str(manager.projects_dir / project_name)
        }
        
        with patch('pathlib.Path.exists', return_value=True):
            with patch('builtins.open', mock_open(read_data=json.dumps(project_data))):
                project = manager.load_project(project_name)
                
                assert project is not None
                assert project["name"] == project_name
                assert project["engine"] == "godot"
                assert manager.current_project == project
    
    def test_load_project_not_found(self):
        """Test loading non-existent project."""
        manager = ProjectManager()
        
        with patch('pathlib.Path.exists', return_value=False):
            project = manager.load_project("NonExistent")
            
            assert project is None
            assert manager.current_project is None
    
    def test_list_projects(self):
        """Test listing all projects."""
        manager = ProjectManager()
        
        # Mock directory structure
        mock_projects = [
            MagicMock(name="Game1", is_dir=lambda: True),
            MagicMock(name="Game2", is_dir=lambda: True),
            MagicMock(name="file.txt", is_dir=lambda: False)  # Should be ignored
        ]
        
        project1_data = {"name": "Game1", "engine": "pygame"}
        project2_data = {"name": "Game2", "engine": "bevy"}
        
        with patch('pathlib.Path.iterdir', return_value=mock_projects):
            with patch('pathlib.Path.exists', return_value=True):
                with patch('builtins.open', mock_open()) as mock_file:
                    # Mock reading different project.json files
                    mock_file.return_value.read.side_effect = [
                        json.dumps(project1_data),
                        json.dumps(project2_data)
                    ]
                    
                    projects = manager.list_projects()
                    
                    assert len(projects) == 2
                    assert projects[0]["name"] == "Game1"
                    assert projects[1]["name"] == "Game2"
    
    def test_delete_project_success(self):
        """Test deleting a project."""
        manager = ProjectManager()
        project_name = "ToDelete"
        
        with patch('pathlib.Path.exists', return_value=True):
            with patch('shutil.rmtree') as mock_rmtree:
                result = manager.delete_project(project_name)
                
                assert result is True
                mock_rmtree.assert_called_once()
                
                # Should clear current project if it was deleted
                if manager.current_project and manager.current_project["name"] == project_name:
                    assert manager.current_project is None
    
    def test_delete_project_not_found(self):
        """Test deleting non-existent project."""
        manager = ProjectManager()
        
        with patch('pathlib.Path.exists', return_value=False):
            result = manager.delete_project("NonExistent")
            
            assert result is False
    
    @pytest.mark.asyncio
    async def test_update_project_code(self):
        """Test updating project code."""
        manager = ProjectManager()
        manager.current_project = {
            "name": "TestGame",
            "path": "/test/TestGame"
        }
        
        new_code = {
            "main.py": "# Updated game code",
            "player.py": "class Player: pass"
        }
        
        with patch('builtins.open', mock_open()) as mock_file:
            result = await manager.update_project_code(new_code)
            
            assert result is True
            # Should write each code file
            assert mock_file.call_count == len(new_code)
    
    @pytest.mark.asyncio
    async def test_update_project_code_no_current(self):
        """Test updating code without current project."""
        manager = ProjectManager()
        manager.current_project = None
        
        result = await manager.update_project_code({"main.py": "code"})
        
        assert result is False
    
    def test_get_project_info(self):
        """Test getting project info."""
        manager = ProjectManager()
        project_name = "InfoGame"
        
        with patch.object(manager, 'load_project') as mock_load:
            mock_load.return_value = {
                "name": project_name,
                "engine": "pygame",
                "created": "2024-01-01"
            }
            
            info = manager.get_project_info(project_name)
            
            assert info is not None
            assert info["name"] == project_name
            mock_load.assert_called_once_with(project_name)
    
    def test_export_project(self):
        """Test exporting project to zip."""
        manager = ProjectManager()
        project_name = "ExportGame"
        project_path = manager.projects_dir / project_name
        
        with patch('pathlib.Path.exists', return_value=True):
            with patch('zipfile.ZipFile') as mock_zip:
                with patch('pathlib.Path.rglob', return_value=[
                    Path("main.py"),
                    Path("assets/sprite.png")
                ]):
                    export_path = manager.export_project(project_name)
                    
                    assert export_path is not None
                    assert export_path.suffix == ".zip"
                    mock_zip.assert_called_once()
    
    def test_export_project_not_found(self):
        """Test exporting non-existent project."""
        manager = ProjectManager()
        
        with patch('pathlib.Path.exists', return_value=False):
            export_path = manager.export_project("NonExistent")
            
            assert export_path is None
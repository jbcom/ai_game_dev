"""Unit tests for chainlit_app individual functions."""
import pytest
from unittest.mock import patch, MagicMock, AsyncMock

from ai_game_dev.chainlit_app import (
    determine_sprites_needed,
    extract_scene_from_description,
    extract_theme_from_description,
    get_appropriate_lesson,
    save_workshop_project,
    get_lesson_content
)


class TestChainlitFunctions:
    """Test individual chainlit app functions."""
    
    def test_determine_sprites_needed_platformer(self):
        """Test sprite determination for platformer game."""
        sprites = determine_sprites_needed("A platformer game with jumping", "pygame")
        assert "player" in sprites
        assert len(sprites) >= 2  # At least player and platform
    
    def test_determine_sprites_needed_space_shooter(self):
        """Test sprite determination for space shooter."""
        sprites = determine_sprites_needed("Space shooter with asteroids", "pygame")
        assert "player" in sprites
        assert any("enemy" in s or "asteroid" in s for s in sprites)
    
    def test_determine_sprites_needed_rpg(self):
        """Test sprite determination for RPG."""
        sprites = determine_sprites_needed("RPG adventure with monsters", "pygame")
        assert "player" in sprites
        assert any("enemy" in s or "monster" in s for s in sprites)
    
    def test_extract_scene_from_description_space(self):
        """Test scene extraction for space game."""
        scene = extract_scene_from_description("Space adventure on Mars")
        assert scene is not None
        assert "space" in scene or "mars" in scene.lower()
    
    def test_extract_scene_from_description_fantasy(self):
        """Test scene extraction for fantasy game."""
        scene = extract_scene_from_description("Fantasy realm with dragons")
        assert scene is not None
        assert "fantasy" in scene or "dragon" in scene
    
    def test_extract_theme_from_description_scifi(self):
        """Test theme extraction for sci-fi game."""
        theme = extract_theme_from_description("Cyberpunk dystopian future")
        assert theme is not None
        assert isinstance(theme, str)
        assert len(theme) > 0
    
    def test_extract_theme_from_description_retro(self):
        """Test theme extraction for retro game."""
        theme = extract_theme_from_description("Retro 8-bit arcade style")
        assert theme is not None
        assert isinstance(theme, str)
    
    def test_get_appropriate_lesson_beginner(self):
        """Test lesson selection for beginner."""
        assessment = {
            "level": "beginner",
            "experience": "none",
            "language": "python",
            "interests": ["2d_games"]
        }
        
        lesson = get_appropriate_lesson(assessment)
        assert lesson is not None
        assert "intro" in lesson or "basic" in lesson.get("title", "").lower()
    
    def test_get_appropriate_lesson_intermediate(self):
        """Test lesson selection for intermediate."""
        assessment = {
            "level": "intermediate",
            "experience": "some",
            "language": "python",
            "interests": ["3d_games", "physics"]
        }
        
        lesson = get_appropriate_lesson(assessment)
        assert lesson is not None
        assert lesson.get("content") or lesson.get("title")
    
    def test_save_workshop_project_success(self):
        """Test successful project saving."""
        project_data = {
            "code": {"main.py": "print('Hello World')"},
            "assets": {"sprites": ["player.png"]},
            "config": {"name": "Test Game"}
        }
        
        with patch('pathlib.Path.mkdir') as mock_mkdir:
            with patch('builtins.open', create=True) as mock_open:
                with patch('json.dump') as mock_json:
                    path = save_workshop_project(project_data, "test_game")
                    
                    assert path is not None
                    assert "test_game" in str(path)
                    mock_mkdir.assert_called()
    
    def test_save_workshop_project_with_code_files(self):
        """Test saving project with multiple code files."""
        project_data = {
            "code": {
                "main.py": "import game",
                "game.py": "class Game: pass",
                "config.json": '{"title": "Test"}'
            },
            "assets": {},
            "config": {"name": "Multi File Game"}
        }
        
        with patch('pathlib.Path.mkdir') as mock_mkdir:
            with patch('builtins.open', create=True) as mock_open:
                with patch('json.dump') as mock_json:
                    path = save_workshop_project(project_data, "multi_game")
                    
                    # Should create files for each code entry
                    assert mock_open.call_count >= 3
    
    def test_get_lesson_content_intro(self):
        """Test getting intro lesson content."""
        content = get_lesson_content("intro")
        assert content is not None
        assert "variables" in content.lower() or "hello" in content.lower()
    
    def test_get_lesson_content_loops(self):
        """Test getting loops lesson content."""
        content = get_lesson_content("loops")
        assert content is not None
        assert "loop" in content.lower() or "for" in content.lower()
    
    def test_get_lesson_content_objects(self):
        """Test getting objects lesson content."""
        content = get_lesson_content("objects")
        assert content is not None
        assert "class" in content.lower() or "object" in content.lower()
    
    def test_get_lesson_content_invalid(self):
        """Test getting invalid lesson content."""
        content = get_lesson_content("nonexistent_lesson")
        assert content is not None
        assert len(content) > 0  # Should return default content
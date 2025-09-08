"""
Tests for Chainlit-based AI Game Development Platform
"""
import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from pathlib import Path
import chainlit as cl

from ai_game_dev.chainlit_app import (
    start,
    main,
    handle_mode_selection,
    handle_workshop_message,
    generate_game_workshop,
    handle_academy_message,
    handle_skill_assessment,
    start_academy_lesson,
    determine_sprites_needed,
    extract_scene_from_description,
    extract_theme_from_description,
    get_appropriate_lesson,
    save_workshop_project,
    send_progress_update,
    handle_workshop_customization,
    handle_lesson_interaction,
    handle_challenge_submission
)

from contextlib import contextmanager

@contextmanager
def mock_chainlit_context():
    """Mock Chainlit context for testing."""
    with patch('chainlit.context.context') as mock_ctx:
        mock_ctx.session = MagicMock()
        mock_ctx.session.id = "test-session-id"
        mock_ctx.current_task = None
        mock_ctx.current_run = None
        yield mock_ctx


class TestChainlitApp:
    """Test the Chainlit application functions."""
    
    @pytest.mark.asyncio
    async def test_start(self):
        """Test session initialization."""
        with mock_chainlit_context():
            with patch('chainlit.user_session.set') as mock_set:
                await start()
                assert mock_set.called
                mock_set.assert_any_call("mode", None)
                mock_set.assert_any_call("state", {})
    
    @pytest.mark.asyncio
    async def test_main_no_mode(self):
        """Test main handler without mode selected."""
        message = Mock(spec=cl.Message)
        message.content = "Hello"
        
        with mock_chainlit_context():
            with patch('chainlit.user_session') as mock_session:
                mock_session.get = Mock(return_value=None)
                with patch('chainlit.Message.send', new_callable=AsyncMock) as mock_send:
                    await main(message)
                    # Should show welcome message when no mode selected
                assert mock_send.called
    
    @pytest.mark.asyncio
    async def test_handle_mode_selection_workshop(self):
        """Test workshop mode selection."""
        with mock_chainlit_context():
            with patch('chainlit.user_session.set') as mock_set:
                with patch('chainlit.Message', return_value=AsyncMock()) as mock_msg:
                    await handle_mode_selection("workshop")
                    mock_set.assert_called_with("mode", "workshop")
                    assert mock_msg.called
    
    @pytest.mark.asyncio
    async def test_handle_mode_selection_academy(self):
        """Test academy mode selection."""
        with patch('chainlit.user_session.set') as mock_set:
            with patch('chainlit.Message', return_value=AsyncMock()) as mock_msg:
                await handle_mode_selection("academy")
                mock_set.assert_called_with("mode", "academy")
                assert mock_msg.called
    
    def test_determine_sprites_needed(self):
        """Test sprite determination from description."""
        # Test platformer
        sprites = determine_sprites_needed("A platformer game with a hero", "pygame")
        assert "player" in sprites
        assert "platform" in sprites
        
        # Test RPG
        sprites = determine_sprites_needed("An RPG with enemies and NPCs", "pygame")
        assert "player" in sprites
        assert "enemy" in sprites
        assert "npc" in sprites
    
    def test_extract_scene_from_description(self):
        """Test scene extraction."""
        scene = extract_scene_from_description("A space shooter game")
        assert "space" in scene.lower()
        
        scene = extract_scene_from_description("A fantasy RPG in a forest")
        assert "forest" in scene.lower()
    
    def test_extract_theme_from_description(self):
        """Test UI theme extraction."""
        theme = extract_theme_from_description("A dark cyberpunk game")
        assert "cyberpunk" in theme.lower()
        
        theme = extract_theme_from_description("A cute pixel art game")
        assert "pixel" in theme.lower()
    
    def test_get_appropriate_lesson(self):
        """Test lesson selection based on skill level."""
        lesson = get_appropriate_lesson("beginner")
        assert lesson["level"] == "beginner"
        assert "pygame" in lesson["engine"]
        
        lesson = get_appropriate_lesson("intermediate")
        assert lesson["level"] == "intermediate"
        
        lesson = get_appropriate_lesson("advanced")
        assert lesson["level"] == "advanced"
    
    @pytest.mark.asyncio
    async def test_save_workshop_project(self):
        """Test project saving."""
        state = {
            "game_title": "Test Game",
            "engine": "pygame",
            "code": "print('hello')"
        }
        
        with patch('pathlib.Path.mkdir') as mock_mkdir:
            with patch('builtins.open', create=True) as mock_open:
                path = save_workshop_project(state)
                assert "Test_Game" in str(path)
                assert mock_mkdir.called
    
    @pytest.mark.asyncio
    async def test_send_progress_update(self):
        """Test progress update sending."""
        with patch('chainlit.Message', return_value=AsyncMock()) as mock_msg:
            await send_progress_update("Generating sprites...", 50)
            assert mock_msg.called
            call_args = mock_msg.call_args[1]
            assert "Generating sprites..." in call_args["content"]
    
    @pytest.mark.asyncio
    async def test_handle_workshop_message_description(self):
        """Test workshop message handling with game description."""
        message = Mock(spec=cl.Message)
        message.content = "I want to make a space shooter"
        
        with patch('chainlit.user_session.get') as mock_get:
            mock_get.side_effect = lambda key: {
                "mode": "workshop",
                "state": {"step": "description"}
            }.get(key)
            
            with patch('chainlit.user_session.set') as mock_set:
                with patch('chainlit.Message', return_value=AsyncMock()):
                    await handle_workshop_message(message)
                    # Should update state with description
                    calls = mock_set.call_args_list
                    state_call = [c for c in calls if c[0][0] == "state"][0]
                    assert state_call[0][1]["game_description"] == "I want to make a space shooter"
    
    @pytest.mark.asyncio
    async def test_generate_game_workshop(self):
        """Test full game generation workflow."""
        state = {
            "game_title": "Test Game",
            "game_description": "A simple platformer",
            "engine": "pygame",
            "art_style": "pixel",
            "features": ["movement", "jumping"],
            "sprites": ["player", "platform"]
        }
        
        with patch('ai_game_dev.text.tool.generate_code_repository', new_callable=AsyncMock) as mock_gen:
            with patch('ai_game_dev.graphics.tool.generate_sprite', new_callable=AsyncMock) as mock_sprite:
                with patch('ai_game_dev.audio.tool.generate_sound_effect', new_callable=AsyncMock) as mock_audio:
                    with patch('chainlit.Message', return_value=AsyncMock()):
                        mock_gen.return_value = {"files": {"main.py": "print('game')"}}
                        mock_sprite.return_value = Mock(path="sprite.png")
                        mock_audio.return_value = Mock(path="sound.wav")
                        
                        result = await generate_game_workshop(state)
                        assert mock_gen.called
                        assert result is not None


class TestAcademyFlow:
    """Test academy mode functionality."""
    
    @pytest.mark.asyncio
    async def test_handle_academy_message_assessment(self):
        """Test academy assessment handling."""
        message = Mock(spec=cl.Message)
        message.content = "beginner"
        
        with patch('chainlit.user_session.get') as mock_get:
            mock_get.side_effect = lambda key: {
                "mode": "academy",
                "state": {"step": "assessment"}
            }.get(key)
            
            with patch('chainlit.user_session.set'):
                with patch('ai_game_dev.chainlit_app.handle_skill_assessment', new_callable=AsyncMock) as mock_assess:
                    await handle_academy_message(message)
                    mock_assess.assert_called_once_with("beginner", {"step": "assessment"})
    
    @pytest.mark.asyncio
    async def test_handle_skill_assessment(self):
        """Test skill assessment."""
        state = {}
        
        with patch('chainlit.user_session.set') as mock_set:
            with patch('ai_game_dev.chainlit_app.get_appropriate_lesson') as mock_lesson:
                with patch('ai_game_dev.chainlit_app.start_academy_lesson', new_callable=AsyncMock) as mock_start:
                    mock_lesson.return_value = {"title": "Test Lesson"}
                    
                    await handle_skill_assessment("intermediate", state)
                    
                    # Should update state with skill level
                    calls = mock_set.call_args_list
                    state_call = [c for c in calls if c[0][0] == "state"][0]
                    assert state_call[0][1]["skill_level"] == "intermediate"
                    assert mock_start.called
    
    @pytest.mark.asyncio
    async def test_start_academy_lesson(self):
        """Test starting an academy lesson."""
        lesson = {
            "title": "Introduction to Pygame",
            "description": "Learn the basics",
            "objectives": ["Create window", "Draw shapes"]
        }
        state = {}
        
        with patch('chainlit.Message', return_value=AsyncMock()) as mock_msg:
            with patch('chainlit.user_session.set'):
                await start_academy_lesson(lesson, state)
                assert mock_msg.called
                # Should show lesson intro
    
    @pytest.mark.asyncio
    async def test_handle_lesson_interaction(self):
        """Test lesson code interaction."""
        code = "import pygame\npygame.init()"
        state = {
            "lesson": {"validation": "pygame.init"},
            "challenge": None
        }
        
        with patch('chainlit.Message', return_value=AsyncMock()) as mock_msg:
            await handle_lesson_interaction(code, state)
            assert mock_msg.called
    
    @pytest.mark.asyncio
    async def test_handle_challenge_submission(self):
        """Test challenge submission."""
        code = "def move_player(x, y): return x + 1, y"
        state = {
            "challenge": {
                "test": "move_player",
                "expected": "movement"
            }
        }
        
        with patch('chainlit.Message', return_value=AsyncMock()) as mock_msg:
            await handle_challenge_submission(code, state)
            assert mock_msg.called


class TestCustomization:
    """Test customization features."""
    
    @pytest.mark.asyncio
    async def test_handle_workshop_customization(self):
        """Test workshop customization."""
        state = {
            "generated_code": {"main.py": "print('game')"},
            "sprites": {"player": "player.png"}
        }
        
        with patch('chainlit.Message', return_value=AsyncMock()) as mock_msg:
            with patch('ai_game_dev.graphics.tool.generate_sprite', new_callable=AsyncMock) as mock_sprite:
                mock_sprite.return_value = Mock(path="new_sprite.png")
                
                await handle_workshop_customization("Make the player sprite bigger", state)
                assert mock_msg.called
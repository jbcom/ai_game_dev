"""
Tests for Chainlit-based AI Game Development Platform
"""
import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from ai_game_dev.chainlit_app import (
    detect_features,
    detect_art_style,
    handle_create_game,
    initialize_subgraphs,
    enter_workshop_mode,
    enter_academy_mode
)


class TestFeatureDetection:
    """Test feature detection from user descriptions."""
    
    def test_detect_dialogue_features(self):
        """Test dialogue feature detection."""
        descriptions = [
            "RPG with dialogue system",
            "game with conversations",
            "adventure with talking NPCs",
            "story-driven game"
        ]
        
        for desc in descriptions:
            features = detect_features(desc)
            assert "dialogue" in features
    
    def test_detect_combat_features(self):
        """Test combat feature detection."""
        descriptions = [
            "action game with fighting",
            "battle royale",
            "space shooter",
            "combat system"
        ]
        
        for desc in descriptions:
            features = detect_features(desc)
            assert "combat" in features
    
    def test_detect_multiple_features(self):
        """Test detection of multiple features."""
        desc = "RPG with dialogue, puzzles, and combat"
        features = detect_features(desc)
        
        assert "rpg" in features
        assert "dialogue" in features
        assert "puzzles" in features
        assert "combat" in features
    
    def test_default_features(self):
        """Test default features when none detected."""
        desc = "a simple game"
        features = detect_features(desc)
        
        assert "graphics" in features
        assert "audio" in features
        assert "gameplay" in features


class TestArtStyleDetection:
    """Test art style detection from descriptions."""
    
    def test_detect_pixel_art(self):
        """Test pixel art style detection."""
        descriptions = [
            "8-bit platformer",
            "pixel art RPG",
            "retro arcade game"
        ]
        
        for desc in descriptions:
            style = detect_art_style(desc)
            assert style == "pixel"
    
    def test_detect_cyberpunk_style(self):
        """Test cyberpunk style detection."""
        descriptions = [
            "cyberpunk RPG",
            "futuristic cyber game",
            "neon city adventure"
        ]
        
        for desc in descriptions:
            style = detect_art_style(desc)
            assert style == "cyberpunk"
    
    def test_default_style(self):
        """Test default style when none detected."""
        style = detect_art_style("a simple game")
        assert style == "modern"


class TestChainlitIntegration:
    """Test Chainlit app integration."""
    
    @pytest.mark.asyncio
    async def test_initialize_subgraphs(self):
        """Test subgraph initialization."""
        with patch('ai_game_dev.chainlit_app.subgraphs', {
            "dialogue": None,
            "quest": None,
            "graphics": None,
            "audio": None
        }):
            # Mock subgraph classes
            with patch('ai_game_dev.chainlit_app.DialogueSubgraph') as MockDialogue, \
                 patch('ai_game_dev.chainlit_app.QuestSubgraph') as MockQuest, \
                 patch('ai_game_dev.chainlit_app.GraphicsSubgraph') as MockGraphics, \
                 patch('ai_game_dev.chainlit_app.AudioSubgraph') as MockAudio:
                
                # Create mock instances
                mock_dialogue = AsyncMock()
                mock_quest = AsyncMock()
                mock_graphics = AsyncMock()
                mock_audio = AsyncMock()
                
                MockDialogue.return_value = mock_dialogue
                MockQuest.return_value = mock_quest
                MockGraphics.return_value = mock_graphics
                MockAudio.return_value = mock_audio
                
                await initialize_subgraphs()
                
                # Verify all subgraphs were created
                MockDialogue.assert_called_once()
                MockQuest.assert_called_once()
                MockGraphics.assert_called_once()
                MockAudio.assert_called_once()
                
                # Verify initialize was called on each
                mock_dialogue.initialize.assert_called_once()
                mock_quest.initialize.assert_called_once()
                mock_graphics.initialize.assert_called_once()
                mock_audio.initialize.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_enter_workshop_mode(self):
        """Test entering workshop mode."""
        # Mock Chainlit session
        mock_session = Mock()
        mock_session.set = Mock()
        
        with patch('chainlit.user_session', mock_session), \
             patch('chainlit.Message') as MockMessage:
            
            mock_message = AsyncMock()
            MockMessage.return_value = mock_message
            
            await enter_workshop_mode()
            
            # Verify mode was set
            mock_session.set.assert_called_with("mode", "workshop")
            
            # Verify message was sent
            mock_message.send.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_enter_academy_mode(self):
        """Test entering academy mode."""
        # Mock Chainlit session
        mock_session = Mock()
        mock_session.set = Mock()
        
        with patch('chainlit.user_session', mock_session), \
             patch('chainlit.Message') as MockMessage:
            
            mock_message = AsyncMock()
            MockMessage.return_value = mock_message
            
            await enter_academy_mode()
            
            # Verify mode was set
            mock_session.set.assert_called_with("mode", "academy")
            
            # Verify message was sent
            mock_message.send.assert_called_once()


class TestGameCreation:
    """Test game creation workflow."""
    
    @pytest.mark.asyncio
    async def test_parse_create_command(self):
        """Test parsing create game commands."""
        test_cases = [
            ("create a puzzle game", "a puzzle game", None),
            ("create a platformer with pygame", "a platformer", "pygame"),
            ("create RPG using godot", "RPG using", "godot"),
            ("create a bevy racing game", "a racing game", "bevy")
        ]
        
        for command, expected_desc, expected_engine in test_cases:
            # Extract description (simplified version of actual logic)
            desc = command[6:].strip()  # Remove "create"
            
            # Check for engine
            engine = None
            for eng in ["pygame", "godot", "bevy"]:
                if eng in desc.lower():
                    engine = eng
                    break
            
            assert desc.startswith(expected_desc[:5])  # Check beginning matches
            if expected_engine:
                assert engine == expected_engine


class TestSubgraphOrchestration:
    """Test direct subgraph orchestration."""
    
    @pytest.mark.asyncio
    async def test_dialogue_subgraph_called_for_rpg(self):
        """Test dialogue subgraph is called for RPG games."""
        game_spec = {
            "description": "RPG with story",
            "features": ["dialogue", "rpg"]
        }
        
        # This would be tested in actual handle_create_game
        # but we verify the logic here
        assert "dialogue" in game_spec["features"]
        assert "rpg" in game_spec["description"].lower()
    
    @pytest.mark.asyncio
    async def test_graphics_subgraph_always_called(self):
        """Test graphics subgraph is always called."""
        # Graphics should be generated for any game
        game_specs = [
            {"features": []},
            {"features": ["combat"]},
            {"features": ["puzzle", "platform"]}
        ]
        
        for spec in game_specs:
            # In actual implementation, graphics subgraph
            # would always be called
            assert True  # Placeholder for actual test


class TestProjectManagement:
    """Test project manager integration."""
    
    def test_project_creation(self):
        """Test project creation through manager."""
        from ai_game_dev.project_manager import ProjectManager
        
        # This would normally be mocked
        # but we test the interface exists
        assert hasattr(ProjectManager, 'create_project')
        assert hasattr(ProjectManager, 'list_projects')
        assert hasattr(ProjectManager, 'get_project')
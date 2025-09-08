"""Test audio generation and processing tools."""
import pytest
from unittest.mock import MagicMock, patch, AsyncMock
import tempfile
from pathlib import Path

from ai_game_dev.audio.audio_tools import (
    AudioTools,
    AudioWorkflowRequest,
    AudioWorkflowResult
)


class TestAudioWorkflowRequest:
    """Test AudioWorkflowRequest model."""

    def test_valid_audio_request(self):
        """Test creating valid audio workflow request."""
        request = AudioWorkflowRequest(
            game_description="Space adventure game",
            audio_needs=["dialogue", "music", "sfx"],
            style_preferences="Epic orchestral",
            target_duration=180
        )
        
        assert request.game_description == "Space adventure game"
        assert len(request.audio_needs) == 3
        assert request.style_preferences == "Epic orchestral"
        assert request.target_duration == 180

    def test_audio_request_defaults(self):
        """Test audio workflow request with defaults."""
        request = AudioWorkflowRequest(
            game_description="Test game",
            audio_needs=["music"]
        )
        
        assert request.style_preferences == ""
        assert request.target_duration == 120


class TestAudioWorkflowResult:
    """Test AudioWorkflowResult dataclass."""

    def test_audio_workflow_result_creation(self):
        """Test creating audio workflow result."""
        result = AudioWorkflowResult(
            dialogue_audio={"character1": "audio_file_1.wav"},
            background_music={"main_theme": "theme.wav"},
            sound_effects=[{"type": "explosion", "file": "boom.wav"}],
            audio_pack_summary="Complete audio package for space game"
        )
        
        assert "character1" in result.dialogue_audio
        assert "main_theme" in result.background_music
        assert len(result.sound_effects) == 1
        assert "space game" in result.audio_pack_summary


class TestAudioTools:
    """Test AudioTools class."""

    def test_audio_tools_init_with_keys(self):
        """Test AudioTools initialization with API keys."""
        with patch("ai_game_dev.audio.audio_tools.TTSGenerator") as mock_tts, \
             patch("ai_game_dev.audio.audio_tools.MusicGenerator") as mock_music, \
             patch("ai_game_dev.audio.audio_tools.FreesoundClient") as mock_freesound:
            
            mock_tts_instance = MagicMock()
            mock_music_instance = MagicMock()
            mock_freesound_instance = MagicMock()
            
            mock_tts.return_value = mock_tts_instance
            mock_music.return_value = mock_music_instance
            mock_freesound.return_value = mock_freesound_instance
            
            tools = AudioTools(
                openai_api_key="test_openai_key",
                freesound_api_key="test_freesound_key"
            )
            
            mock_tts.assert_called_once_with(api_key="test_openai_key")
            mock_music.assert_called_once()
            mock_freesound.assert_called_once_with(api_key="test_freesound_key")
            
            assert tools.tts_generator == mock_tts_instance
            assert tools.music_generator == mock_music_instance
            assert tools.freesound_client == mock_freesound_instance

    def test_audio_tools_init_no_freesound_key(self):
        """Test AudioTools initialization without Freesound key."""
        with patch("ai_game_dev.audio.audio_tools.TTSGenerator") as mock_tts, \
             patch("ai_game_dev.audio.audio_tools.MusicGenerator") as mock_music:
            
            tools = AudioTools(openai_api_key="test_key")
            
            assert tools.freesound_client is None

    @pytest.mark.asyncio
    async def test_generate_dialogue_audio(self):
        """Test dialogue audio generation."""
        with patch("ai_game_dev.audio.audio_tools.TTSGenerator") as mock_tts_class:
            mock_tts = MagicMock()
            mock_tts.generate_speech = AsyncMock(return_value={"audio_file": "dialogue.wav", "duration": 5.0})
            mock_tts_class.return_value = mock_tts
            
            tools = AudioTools(openai_api_key="test_key")
            
            dialogue_requests = [
                {"character": "Hero", "text": "Hello world!", "voice": "male"},
                {"character": "NPC", "text": "Welcome!", "voice": "female"}
            ]
            
            result = await tools.generate_dialogue_audio(dialogue_requests)
            
            assert len(result) == 2
            assert "Hero" in result
            assert "NPC" in result
            assert mock_tts.generate_speech.call_count == 2

    @pytest.mark.asyncio
    async def test_generate_background_music(self):
        """Test background music generation."""
        with patch("ai_game_dev.audio.audio_tools.MusicGenerator") as mock_music_class:
            mock_music = MagicMock()
            mock_music.generate_adaptive_music = AsyncMock(return_value={
                "main_theme": {"file": "theme.wav", "duration": 120}
            })
            mock_music_class.return_value = mock_music
            
            tools = AudioTools()
            
            music_request = {
                "style": "orchestral",
                "mood": "heroic",
                "duration": 120,
                "themes": ["main_theme"]
            }
            
            result = await tools.generate_background_music(music_request)
            
            assert "main_theme" in result
            mock_music.generate_adaptive_music.assert_called_once_with(music_request)

    @pytest.mark.asyncio
    async def test_search_sound_effects(self):
        """Test sound effects search."""
        with patch("ai_game_dev.audio.audio_tools.FreesoundClient") as mock_freesound_class:
            mock_freesound = MagicMock()
            mock_freesound.search_sounds = AsyncMock(return_value=[
                {"name": "explosion.wav", "url": "http://example.com/explosion.wav"},
                {"name": "laser.wav", "url": "http://example.com/laser.wav"}
            ])
            mock_freesound_class.return_value = mock_freesound
            
            tools = AudioTools(freesound_api_key="test_key")
            
            result = await tools.search_sound_effects(["explosion", "laser"], max_results=2)
            
            assert len(result) == 2
            assert result[0]["name"] == "explosion.wav"
            mock_freesound.search_sounds.assert_called_once()

    @pytest.mark.asyncio
    async def test_generate_complete_audio_pack_no_freesound(self):
        """Test complete audio pack generation without Freesound client."""
        tools = AudioTools()  # No Freesound key
    
        result = await tools.generate_complete_audio_pack(
            game_description="Space shooter game",
            audio_needs=["dialogue", "music", "sfx"],
            style_preferences="retro arcade"
        )
        
        assert result is not None
        assert hasattr(result, 'dialogue_audio')
        assert hasattr(result, 'background_music')
        assert hasattr(result, 'sound_effects')

    @pytest.mark.asyncio
    async def test_complete_audio_workflow(self):
        """Test complete audio workflow."""
        with patch("ai_game_dev.audio.audio_tools.TTSGenerator") as mock_tts_class, \
             patch("ai_game_dev.audio.audio_tools.MusicGenerator") as mock_music_class, \
             patch("ai_game_dev.audio.audio_tools.FreesoundClient") as mock_freesound_class:
            
            # Setup mocks
            mock_tts = MagicMock()
            mock_tts.generate_speech = AsyncMock(return_value={"audio_file": "dialogue.wav"})
            mock_tts_class.return_value = mock_tts
            
            mock_music = MagicMock()
            mock_music.generate_adaptive_music = AsyncMock(return_value={"theme": {"file": "music.wav"}})
            mock_music_class.return_value = mock_music
            
            mock_freesound = MagicMock()
            mock_freesound.search_sounds = AsyncMock(return_value=[{"name": "sfx.wav"}])
            mock_freesound_class.return_value = mock_freesound
            
            tools = AudioTools(
                openai_api_key="test_key",
                freesound_api_key="test_freesound_key"
            )
            
            request = AudioWorkflowRequest(
                game_description="Fantasy RPG",
                audio_needs=["dialogue", "music", "sfx"],
                style_preferences="Medieval orchestral",
                target_duration=180
            )
            
            result = await tools.complete_audio_workflow(request)
            
            assert isinstance(result, AudioWorkflowResult)
            assert result.dialogue_audio is not None
            assert result.background_music is not None
            assert result.sound_effects is not None
            assert "audio package" in result.audio_pack_summary.lower()

    def test_create_langraph_tool(self):
        """Test creating LangGraph structured tool."""
        tools = AudioTools()
        
        structured_tool = tools.create_langraph_tool()
        
        assert structured_tool is not None
        assert hasattr(structured_tool, 'name')
        assert hasattr(structured_tool, 'description')
        assert callable(structured_tool.func)

    @pytest.mark.asyncio
    async def test_generate_dialogue_audio_error_handling(self):
        """Test dialogue audio generation with error handling."""
        with patch("ai_game_dev.audio.audio_tools.TTSGenerator") as mock_tts_class:
            mock_tts = MagicMock()
            mock_tts.generate_speech = AsyncMock(side_effect=Exception("TTS Error"))
            mock_tts_class.return_value = mock_tts
            
            tools = AudioTools(openai_api_key="test_key")
            
            dialogue_requests = [{"character": "Hero", "text": "Hello", "voice": "male"}]
            
            result = await tools.generate_dialogue_audio(dialogue_requests)
            
            # Should return empty dict on error
            assert result == {}

    @pytest.mark.asyncio
    async def test_generate_background_music_error_handling(self):
        """Test background music generation with error handling."""
        with patch("ai_game_dev.audio.audio_tools.MusicGenerator") as mock_music_class:
            mock_music = MagicMock()
            mock_music.generate_adaptive_music = AsyncMock(side_effect=Exception("Music Error"))
            mock_music_class.return_value = mock_music
            
            tools = AudioTools()
            
            music_request = {"style": "orchestral", "duration": 120}
            
            result = await tools.generate_background_music(music_request)
            
            # Should return empty dict on error
            assert result == {}
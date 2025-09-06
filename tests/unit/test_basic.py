"""Basic tests for core modules without heavy dependencies."""
import pytest

def test_basic_import():
    """Test basic package can be imported."""
    import ai_game_dev
    assert hasattr(ai_game_dev, '__version__')
    assert ai_game_dev.__version__ == "1.0.0"

def test_config_module():
    """Test config module can be imported independently."""
    from ai_game_dev.config import ServerSettings
    from unittest.mock import patch
    import os
    
    # Test with environment variable
    with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
        config = ServerSettings()
        assert config.openai_api_key == "test-key"
        assert config.server_name == "openai-multimodal-server"
        assert config.enable_caching is True

def test_models_enum():
    """Test models enums can be imported."""
    from ai_game_dev.models import GameEngine, GameType, ComplexityLevel
    
    assert GameEngine.PYGAME == "pygame"
    assert GameType.TWO_DIMENSIONAL == "2d" 
    assert ComplexityLevel.BEGINNER == "beginner"
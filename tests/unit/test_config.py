"""Test configuration management."""
import pytest
import os
from unittest.mock import patch
from ai_game_dev.config import Config


class TestConfig:
    """Test configuration management."""

    def test_config_defaults(self):
        """Test config with default values."""
        config = Config()
        
        assert config.openai_api_key is None
        assert config.anthropic_api_key is None
        assert config.google_api_key is None
        assert config.debug is False

    @patch.dict(os.environ, {
        "OPENAI_API_KEY": "test_openai",
        "ANTHROPIC_API_KEY": "test_anthropic",
        "GOOGLE_API_KEY": "test_google",
        "DEBUG": "true"
    })
    def test_config_from_env(self):
        """Test config loaded from environment variables."""
        config = Config()
        
        assert config.openai_api_key == "test_openai"
        assert config.anthropic_api_key == "test_anthropic"
        assert config.google_api_key == "test_google"
        assert config.debug is True

    def test_config_explicit_values(self):
        """Test config with explicit values."""
        config = Config(
            openai_api_key="explicit_openai",
            debug=True
        )
        
        assert config.openai_api_key == "explicit_openai"
        assert config.debug is True

    @patch.dict(os.environ, {"DEBUG": "false"})
    def test_config_debug_false(self):
        """Test debug flag with false value."""
        config = Config()
        assert config.debug is False

    @patch.dict(os.environ, {"DEBUG": "0"})
    def test_config_debug_zero(self):
        """Test debug flag with zero value."""
        config = Config()
        assert config.debug is False

    def test_config_missing_required_key(self):
        """Test behavior when required keys are missing."""
        config = Config()
        
        # Should not raise exception, just return None
        assert config.openai_api_key is None
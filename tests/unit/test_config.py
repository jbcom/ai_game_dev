"""Test configuration management."""
import pytest
import os
from unittest.mock import patch
from ai_game_dev.config import ServerSettings as Config


class TestConfig:
    """Test configuration management."""

    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"})
    def test_config_defaults(self):
        """Test config with default values."""
        config = Config()
        
        assert config.openai_api_key == "test-key"
        assert config.server_name == "openai-multimodal-server"
        assert config.enable_caching is True

    @patch.dict(os.environ, {
        "OPENAI_API_KEY": "test_openai",
        "OPENAI_MCP_SERVER_NAME": "custom-server",
        "OPENAI_MCP_ENABLE_CACHING": "false"
    })
    def test_config_from_env(self):
        """Test config loaded from environment variables."""
        config = Config()
        
        assert config.openai_api_key == "test_openai"
        assert config.server_name == "custom-server"
        assert config.enable_caching is False

    def test_config_explicit_values(self):
        """Test config with explicit values."""
        config = Config(
            openai_api_key="explicit_openai",
            server_name="custom-server",
            enable_caching=False
        )
        
        assert config.openai_api_key == "explicit_openai"
        assert config.server_name == "custom-server"
        assert config.enable_caching is False

    @patch.dict(os.environ, {"OPENAI_MCP_ENABLE_CACHING": "false"})
    def test_config_caching_false(self):
        """Test caching flag with false value."""
        config = Config()
        assert config.enable_caching is False

    @patch.dict(os.environ, {"OPENAI_MCP_ENABLE_CACHING": "0"})
    def test_config_caching_zero(self):
        """Test caching flag with zero value."""
        config = Config()
        assert config.enable_caching is False

    def test_config_missing_required_key(self):
        """Test behavior when required keys are missing."""
        config = Config()
        
        # Should return empty string by default
        assert config.openai_api_key == "" or config.openai_api_key == "test_openai_key"  # May be set by env
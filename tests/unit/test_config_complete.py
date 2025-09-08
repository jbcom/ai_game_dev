"""Complete tests for config module."""
import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path
import os

from ai_game_dev.config import ServerSettings, ProviderSettings, settings


class TestServerSettings:
    """Test ServerSettings configuration."""
    
    def test_default_settings(self):
        """Test default server settings."""
        with patch.dict(os.environ, {}, clear=True):
            config = ServerSettings()
            
            assert config.openai_api_key == ""
            assert config.server_name == "openai-multimodal-server"
            assert config.enable_caching is True
            assert isinstance(config.cache_base_dir, Path)
            assert isinstance(config.data_base_dir, Path)
    
    def test_settings_from_env(self):
        """Test loading settings from environment."""
        with patch.dict(os.environ, {
            'OPENAI_API_KEY': 'test-key-123',
            'OPENAI_MCP_SERVER_NAME': 'custom-server',
            'OPENAI_MCP_ENABLE_CACHING': 'false'
        }):
            config = ServerSettings()
            
            assert config.openai_api_key == 'test-key-123'
            assert config.server_name == 'custom-server'
            assert config.enable_caching is False
    
    def test_cache_dir_property(self):
        """Test cache directory property."""
        config = ServerSettings()
        cache_dir = config.cache_dir
        
        assert isinstance(cache_dir, Path)
        assert str(cache_dir).endswith('assets')
    
    def test_images_dir_property(self):
        """Test images directory property."""
        config = ServerSettings()
        images_dir = config.images_dir
        
        assert isinstance(images_dir, Path)
        assert str(images_dir).endswith('images')
    
    def test_models_3d_dir_property(self):
        """Test 3D models directory property."""
        config = ServerSettings()
        models_dir = config.models_3d_dir
        
        assert isinstance(models_dir, Path)
        assert str(models_dir).endswith('3d_models')
    
    def test_verification_cache_path_property(self):
        """Test verification cache path property."""
        config = ServerSettings()
        cache_path = config.verification_cache_path
        
        assert isinstance(cache_path, Path)
        assert str(cache_path).endswith('verification_cache.json')
    
    def test_model_dump(self):
        """Test model serialization."""
        config = ServerSettings(openai_api_key="test-key")
        data = config.model_dump()
        
        assert isinstance(data, dict)
        assert data['openai_api_key'] == "test-key"


class TestProviderSettings:
    """Test ProviderSettings configuration."""
    
    def test_default_provider_settings(self):
        """Test default provider settings."""
        config = ProviderSettings()
        
        assert config.default_model == "gpt-4o"
        assert config.temperature == 0.7
        assert config.max_tokens == 4096
        assert config.enable_streaming is True
        assert config.retry_attempts == 3
        assert config.timeout_seconds == 30
    
    def test_custom_provider_settings(self):
        """Test custom provider settings."""
        config = ProviderSettings(
            default_model="gpt-5",
            temperature=0.9,
            max_tokens=8192,
            enable_streaming=False
        )
        
        assert config.default_model == "gpt-5"
        assert config.temperature == 0.9
        assert config.max_tokens == 8192
        assert config.enable_streaming is False




class TestGlobalSettings:
    """Test global settings instance."""
    
    def test_settings_singleton(self):
        """Test that settings is a singleton instance."""
        assert settings is not None
        assert isinstance(settings, ServerSettings)
    
    def test_settings_properties(self):
        """Test accessing settings properties."""
        assert hasattr(settings, 'openai_api_key')
        assert hasattr(settings, 'cache_dir')
        assert hasattr(settings, 'images_dir')
        assert hasattr(settings, 'models_3d_dir')
    
    def test_settings_env_override(self):
        """Test that settings can be overridden by environment."""
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'override-key'}):
            # Create new instance to pick up env changes
            new_settings = ServerSettings()
            assert new_settings.openai_api_key == 'override-key'
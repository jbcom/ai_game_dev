"""Test LLM provider management."""
import pytest
from unittest.mock import MagicMock, patch, AsyncMock
import os

from ai_game_dev.providers import (
    LLMProvider,
    ModelConfig,
    setup_openai,
    setup_anthropic,
    setup_google,
    setup_ollama,
    create_default_manager
)


class TestLLMManager:
    """Test LLM provider management."""

    def test_init_empty_manager(self):
        """Test creating empty manager."""
        manager = LLMManager()
        assert len(manager.providers) == 0
        assert manager.default_provider is None

    def test_add_provider(self):
        """Test adding a provider."""
        manager = LLMManager()
        mock_provider = MagicMock()
        
        manager.add_provider("test", mock_provider, is_default=True)
        
        assert "test" in manager.providers
        assert manager.providers["test"] == mock_provider
        assert manager.default_provider == "test"

    def test_get_provider_existing(self):
        """Test getting existing provider."""
        manager = LLMManager()
        mock_provider = MagicMock()
        manager.add_provider("test", mock_provider)
        
        result = manager.get_provider("test")
        assert result == mock_provider

    def test_get_provider_nonexistent(self):
        """Test getting non-existent provider."""
        manager = LLMManager()
        
        result = manager.get_provider("nonexistent")
        assert result is None

    def test_get_default_provider(self):
        """Test getting default provider."""
        manager = LLMManager()
        mock_provider = MagicMock()
        manager.add_provider("test", mock_provider, is_default=True)
        
        result = manager.get_provider()
        assert result == mock_provider

    def test_list_providers(self):
        """Test listing all providers."""
        manager = LLMManager()
        manager.add_provider("provider1", MagicMock())
        manager.add_provider("provider2", MagicMock())
        
        providers = manager.list_providers()
        assert "provider1" in providers
        assert "provider2" in providers
        assert len(providers) == 2


class TestProviderSetup:
    """Test provider setup functions."""

    @patch("ai_game_dev.providers.ChatOpenAI")
    def test_setup_openai_with_key(self, mock_openai):
        """Test OpenAI setup with API key."""
        mock_instance = MagicMock()
        mock_openai.return_value = mock_instance
        
        result = setup_openai("test_key")
        
        mock_openai.assert_called_once_with(
            openai_api_key="test_key",
            model="gpt-4o",
            temperature=0.7,
            max_tokens=4000
        )
        assert result == mock_instance

    @patch.dict(os.environ, {"OPENAI_API_KEY": "env_key"})
    @patch("ai_game_dev.providers.ChatOpenAI")
    def test_setup_openai_from_env(self, mock_openai):
        """Test OpenAI setup from environment."""
        mock_instance = MagicMock()
        mock_openai.return_value = mock_instance
        
        result = setup_openai()
        
        mock_openai.assert_called_once_with(
            openai_api_key="env_key",
            model="gpt-4o",
            temperature=0.7,
            max_tokens=4000
        )

    @patch("ai_game_dev.providers.ChatAnthropic")
    def test_setup_anthropic_with_key(self, mock_anthropic):
        """Test Anthropic setup with API key."""
        mock_instance = MagicMock()
        mock_anthropic.return_value = mock_instance
        
        result = setup_anthropic("test_key")
        
        mock_anthropic.assert_called_once_with(
            anthropic_api_key="test_key",
            model="claude-3-5-sonnet-20241022",
            temperature=0.7,
            max_tokens=4000
        )
        assert result == mock_instance

    @patch("ai_game_dev.providers.ChatGoogleGenerativeAI")
    def test_setup_google_with_key(self, mock_google):
        """Test Google AI setup with API key."""
        mock_instance = MagicMock()
        mock_google.return_value = mock_instance
        
        result = setup_google("test_key")
        
        mock_google.assert_called_once_with(
            google_api_key="test_key",
            model="gemini-1.5-pro",
            temperature=0.7,
            max_output_tokens=4000
        )
        assert result == mock_instance

    @patch("ai_game_dev.providers.ChatOllama")
    def test_setup_ollama_with_model(self, mock_ollama):
        """Test Ollama setup with model."""
        mock_instance = MagicMock()
        mock_ollama.return_value = mock_instance
        
        result = setup_ollama("llama2")
        
        mock_ollama.assert_called_once_with(
            model="llama2",
            temperature=0.7
        )
        assert result == mock_instance

    def test_setup_ollama_default_model(self):
        """Test Ollama setup with default model."""
        with patch("ai_game_dev.providers.ChatOllama") as mock_ollama:
            mock_instance = MagicMock()
            mock_ollama.return_value = mock_instance
            
            result = setup_ollama()
            
            mock_ollama.assert_called_once_with(
                model="llama2",
                temperature=0.7
            )

    @patch.dict(os.environ, {"OPENAI_API_KEY": "test_openai_key"})
    @patch("ai_game_dev.providers.setup_openai")
    def test_create_default_manager_with_openai(self, mock_setup_openai):
        """Test creating default manager with OpenAI."""
        mock_provider = MagicMock()
        mock_setup_openai.return_value = mock_provider
        
        manager = create_default_manager()
        
        mock_setup_openai.assert_called_once()
        assert manager.get_provider("openai") == mock_provider
        assert manager.default_provider == "openai"

    @patch.dict(os.environ, {}, clear=True)
    def test_create_default_manager_no_keys(self):
        """Test creating default manager with no API keys."""
        manager = create_default_manager()
        
        assert len(manager.providers) == 0
        assert manager.default_provider is None
"""Comprehensive provider tests to achieve 100% coverage."""

import pytest
from unittest.mock import Mock, patch, MagicMock
import os

from ai_game_dev.providers import (
    LLMProvider, ModelConfig, LLMProviderManager,
    OpenAIProvider, AnthropicProvider, GoogleProvider, OllamaProvider,
    BaseLLMProvider, create_default_manager, setup_openai, setup_anthropic,
    setup_google, setup_ollama
)


class TestModelConfig:
    """Comprehensive ModelConfig tests."""
    
    def test_model_config_post_init(self):
        """Test ModelConfig __post_init__ method."""
        config = ModelConfig(
            provider=LLMProvider.OPENAI,
            model_name="gpt-4"
        )
        assert config.additional_params == {}
        
        config_with_params = ModelConfig(
            provider=LLMProvider.OPENAI,
            model_name="gpt-4",
            additional_params={"top_p": 0.9}
        )
        assert config_with_params.additional_params == {"top_p": 0.9}

    def test_model_config_all_fields(self):
        """Test ModelConfig with all fields."""
        config = ModelConfig(
            provider=LLMProvider.ANTHROPIC,
            model_name="claude-3",
            temperature=0.5,
            max_tokens=1000,
            api_key="test-key",
            base_url="https://api.example.com",
            additional_params={"stream": True}
        )
        
        assert config.provider == LLMProvider.ANTHROPIC
        assert config.model_name == "claude-3"
        assert config.temperature == 0.5
        assert config.max_tokens == 1000
        assert config.api_key == "test-key"
        assert config.base_url == "https://api.example.com"
        assert config.additional_params["stream"] is True


class TestBaseLLMProvider:
    """Test abstract base provider functionality."""
    
    def test_base_provider_abstract(self):
        """Test that BaseLLMProvider is abstract."""
        with pytest.raises(TypeError):
            BaseLLMProvider(ModelConfig(LLMProvider.OPENAI, "test"))

    @patch('ai_game_dev.providers.ChatOpenAI')
    def test_provider_model_property(self, mock_chat):
        """Test model property caching."""
        mock_model = MagicMock()
        mock_chat.return_value = mock_model
        
        provider = OpenAIProvider(ModelConfig(LLMProvider.OPENAI, "gpt-4", api_key="test"))
        
        # First access creates model
        model1 = provider.model
        assert model1 == mock_model
        
        # Second access returns cached model
        model2 = provider.model
        assert model2 == mock_model
        assert model1 is model2

    @patch('ai_game_dev.providers.ChatOpenAI')
    @patch('ai_game_dev.providers.HumanMessage')
    def test_provider_invoke_string(self, mock_human_msg, mock_chat):
        """Test invoke with string input."""
        mock_model = MagicMock()
        mock_response = MagicMock()
        mock_response.content = "Test response"
        mock_model.invoke.return_value = mock_response
        mock_chat.return_value = mock_model
        
        mock_message = MagicMock()
        mock_human_msg.return_value = mock_message
        
        provider = OpenAIProvider(ModelConfig(LLMProvider.OPENAI, "gpt-4", api_key="test"))
        result = provider.invoke("Test prompt")
        
        assert result == "Test response"
        mock_human_msg.assert_called_once_with(content="Test prompt")
        mock_model.invoke.assert_called_once_with([mock_message])

    @patch('ai_game_dev.providers.ChatOpenAI')
    def test_provider_invoke_no_content(self, mock_chat):
        """Test invoke when response has no content attribute."""
        mock_model = MagicMock()
        mock_response = "Raw response"
        mock_model.invoke.return_value = mock_response
        mock_chat.return_value = mock_model
        
        provider = OpenAIProvider(ModelConfig(LLMProvider.OPENAI, "gpt-4", api_key="test"))
        result = provider.invoke("Test prompt")
        
        assert result == "Raw response"

    @patch('ai_game_dev.providers.ChatOpenAI')
    @patch('ai_game_dev.providers.HumanMessage')
    @pytest.mark.asyncio
    async def test_provider_ainvoke_string(self, mock_human_msg, mock_chat):
        """Test async invoke with string input."""
        mock_model = MagicMock()
        mock_response = MagicMock()
        mock_response.content = "Async response"
        mock_model.ainvoke.return_value = mock_response
        mock_chat.return_value = mock_model
        
        mock_message = MagicMock()
        mock_human_msg.return_value = mock_message
        
        provider = OpenAIProvider(ModelConfig(LLMProvider.OPENAI, "gpt-4", api_key="test"))
        result = await provider.ainvoke("Test prompt")
        
        assert result == "Async response"


class TestOpenAIProvider:
    """Comprehensive OpenAI provider tests."""
    
    @patch('ai_game_dev.providers.ChatOpenAI')
    def test_openai_provider_with_api_key(self, mock_chat):
        """Test OpenAI provider with explicit API key."""
        config = ModelConfig(
            provider=LLMProvider.OPENAI,
            model_name="gpt-4",
            api_key="explicit-key",
            temperature=0.8,
            max_tokens=2000,
            additional_params={"top_p": 0.9}
        )
        
        provider = OpenAIProvider(config)
        model = provider.model  # Trigger model creation
        
        mock_chat.assert_called_once_with(
            model="gpt-4",
            temperature=0.8,
            max_tokens=2000,
            api_key="explicit-key",
            top_p=0.9
        )

    @patch.dict(os.environ, {"OPENAI_API_KEY": "env-key"})
    @patch('ai_game_dev.providers.ChatOpenAI')
    def test_openai_provider_env_key(self, mock_chat):
        """Test OpenAI provider with environment API key."""
        config = ModelConfig(LLMProvider.OPENAI, "gpt-3.5-turbo")
        provider = OpenAIProvider(config)
        model = provider.model
        
        mock_chat.assert_called_once_with(
            model="gpt-3.5-turbo",
            temperature=0.7,
            max_tokens=None,
            api_key="env-key"
        )

    @patch.dict(os.environ, {}, clear=True)
    def test_openai_provider_no_key(self):
        """Test OpenAI provider without API key raises error."""
        config = ModelConfig(LLMProvider.OPENAI, "gpt-4")
        provider = OpenAIProvider(config)
        
        with pytest.raises(ValueError, match="OpenAI API key required"):
            model = provider.model


class TestAnthropicProvider:
    """Comprehensive Anthropic provider tests."""
    
    @patch('ai_game_dev.providers.ChatAnthropic')
    def test_anthropic_provider_with_key(self, mock_chat):
        """Test Anthropic provider with API key."""
        config = ModelConfig(
            provider=LLMProvider.ANTHROPIC,
            model_name="claude-3",
            api_key="claude-key",
            temperature=0.3,
            max_tokens=1500
        )
        
        provider = AnthropicProvider(config)
        model = provider.model
        
        mock_chat.assert_called_once_with(
            model="claude-3",
            temperature=0.3,
            max_tokens=1500,
            api_key="claude-key"
        )

    @patch.dict(os.environ, {}, clear=True)
    def test_anthropic_provider_no_key(self):
        """Test Anthropic provider without API key raises error."""
        config = ModelConfig(LLMProvider.ANTHROPIC, "claude-3")
        provider = AnthropicProvider(config)
        
        with pytest.raises(ValueError, match="Anthropic API key required"):
            model = provider.model


class TestGoogleProvider:
    """Comprehensive Google provider tests."""
    
    @patch('ai_game_dev.providers.ChatGoogleGenerativeAI')
    def test_google_provider_with_key(self, mock_chat):
        """Test Google provider with API key."""
        config = ModelConfig(
            provider=LLMProvider.GOOGLE,
            model_name="gemini-pro",
            api_key="google-key",
            temperature=0.6,
            max_tokens=1000
        )
        
        provider = GoogleProvider(config)
        model = provider.model
        
        mock_chat.assert_called_once_with(
            model="gemini-pro",
            temperature=0.6,
            max_output_tokens=1000,
            google_api_key="google-key"
        )

    @patch.dict(os.environ, {}, clear=True)
    def test_google_provider_no_key(self):
        """Test Google provider without API key raises error."""
        config = ModelConfig(LLMProvider.GOOGLE, "gemini-pro")
        provider = GoogleProvider(config)
        
        with pytest.raises(ValueError, match="Google API key required"):
            model = provider.model


class TestOllamaProvider:
    """Comprehensive Ollama provider tests."""
    
    @patch('ai_game_dev.providers.Ollama')
    def test_ollama_provider_default_url(self, mock_ollama):
        """Test Ollama provider with default base URL."""
        config = ModelConfig(
            provider=LLMProvider.OLLAMA,
            model_name="llama3.1:8b",
            temperature=0.4
        )
        
        provider = OllamaProvider(config)
        model = provider.model
        
        mock_ollama.assert_called_once_with(
            model="llama3.1:8b",
            temperature=0.4,
            base_url="http://localhost:11434"
        )

    @patch('ai_game_dev.providers.Ollama')
    def test_ollama_provider_custom_url(self, mock_ollama):
        """Test Ollama provider with custom base URL."""
        config = ModelConfig(
            provider=LLMProvider.OLLAMA,
            model_name="mistral",
            base_url="http://custom:8080",
            additional_params={"num_predict": 100}
        )
        
        provider = OllamaProvider(config)
        model = provider.model
        
        mock_ollama.assert_called_once_with(
            model="mistral",
            temperature=0.7,
            base_url="http://custom:8080",
            num_predict=100
        )


class TestLLMProviderManager:
    """Comprehensive LLMProviderManager tests."""
    
    def test_manager_init(self):
        """Test manager initialization."""
        manager = LLMProviderManager()
        assert len(manager._providers) == 0
        assert manager._default_provider is None

    def test_manager_recommended_models(self):
        """Test recommended models constants."""
        manager = LLMProviderManager()
        
        assert LLMProvider.OPENAI in manager.RECOMMENDED_MODELS
        assert "gpt-4o" in manager.RECOMMENDED_MODELS[LLMProvider.OPENAI]
        assert "claude-3-5-sonnet-20241022" in manager.RECOMMENDED_MODELS[LLMProvider.ANTHROPIC]
        assert "gemini-1.5-pro" in manager.RECOMMENDED_MODELS[LLMProvider.GOOGLE]
        assert "llama3.1:8b" in manager.RECOMMENDED_MODELS[LLMProvider.OLLAMA]

    def test_manager_provider_classes(self):
        """Test provider class mapping."""
        manager = LLMProviderManager()
        
        assert manager.PROVIDER_CLASSES[LLMProvider.OPENAI] == OpenAIProvider
        assert manager.PROVIDER_CLASSES[LLMProvider.ANTHROPIC] == AnthropicProvider
        assert manager.PROVIDER_CLASSES[LLMProvider.GOOGLE] == GoogleProvider
        assert manager.PROVIDER_CLASSES[LLMProvider.OLLAMA] == OllamaProvider

    @patch('ai_game_dev.providers.ChatOpenAI')
    def test_manager_add_provider_success(self, mock_chat):
        """Test successful provider addition."""
        manager = LLMProviderManager()
        
        provider = manager.add_provider(
            "test-openai",
            LLMProvider.OPENAI,
            "gpt-4",
            api_key="test-key",
            temperature=0.5
        )
        
        assert "test-openai" in manager._providers
        assert isinstance(provider, OpenAIProvider)
        assert provider.config.model_name == "gpt-4"
        assert provider.config.temperature == 0.5

    def test_manager_add_provider_unsupported(self):
        """Test adding unsupported provider type."""
        manager = LLMProviderManager()
        
        with pytest.raises(ValueError, match="Unsupported provider"):
            manager.add_provider(
                "test-custom",
                LLMProvider.CUSTOM,
                "custom-model"
            )

    @patch('ai_game_dev.providers.ChatOpenAI')
    def test_manager_get_provider_by_name(self, mock_chat):
        """Test getting provider by name."""
        manager = LLMProviderManager()
        added_provider = manager.add_provider("test", LLMProvider.OPENAI, "gpt-4", api_key="key")
        
        retrieved_provider = manager.get_provider("test")
        assert retrieved_provider == added_provider

    @patch('ai_game_dev.providers.ChatOpenAI')
    def test_manager_get_default_provider(self, mock_chat):
        """Test getting default provider."""
        manager = LLMProviderManager()
        provider = manager.add_provider("default", LLMProvider.OPENAI, "gpt-4", api_key="key")
        manager.set_default_provider("default")
        
        default_provider = manager.get_provider()
        assert default_provider == provider

    def test_manager_get_provider_nonexistent(self):
        """Test getting non-existent provider."""
        manager = LLMProviderManager()
        
        with pytest.raises(ValueError, match="Provider 'missing' not found"):
            manager.get_provider("missing")

    def test_manager_get_default_none(self):
        """Test getting default when none set."""
        manager = LLMProviderManager()
        
        with pytest.raises(ValueError, match="No default provider set"):
            manager.get_provider()

    @patch('ai_game_dev.providers.ChatOpenAI')
    def test_manager_set_default_provider(self, mock_chat):
        """Test setting default provider."""
        manager = LLMProviderManager()
        manager.add_provider("test", LLMProvider.OPENAI, "gpt-4", api_key="key")
        
        manager.set_default_provider("test")
        assert manager._default_provider == "test"

    def test_manager_set_default_nonexistent(self):
        """Test setting non-existent default provider."""
        manager = LLMProviderManager()
        
        with pytest.raises(ValueError, match="Provider 'missing' not found"):
            manager.set_default_provider("missing")

    @patch('ai_game_dev.providers.ChatOpenAI')
    @patch('ai_game_dev.providers.ChatAnthropic')
    def test_manager_list_providers(self, mock_anthropic, mock_openai):
        """Test listing all providers."""
        manager = LLMProviderManager()
        manager.add_provider("openai", LLMProvider.OPENAI, "gpt-4", api_key="key1")
        manager.add_provider("claude", LLMProvider.ANTHROPIC, "claude-3", api_key="key2")
        
        providers = manager.list_providers()
        assert "openai" in providers
        assert "claude" in providers
        assert len(providers) == 2


class TestSetupFunctions:
    """Test provider setup utility functions."""
    
    @patch('ai_game_dev.providers.ChatOpenAI')
    def test_setup_openai_with_key(self, mock_chat):
        """Test OpenAI setup with API key."""
        provider = setup_openai(api_key="test-key", model="gpt-4")
        
        assert isinstance(provider, OpenAIProvider)
        assert provider.config.api_key == "test-key"
        assert provider.config.model_name == "gpt-4"

    @patch('ai_game_dev.providers.ChatAnthropic')
    def test_setup_anthropic_with_key(self, mock_chat):
        """Test Anthropic setup with API key."""
        provider = setup_anthropic(api_key="claude-key", model="claude-3")
        
        assert isinstance(provider, AnthropicProvider)
        assert provider.config.api_key == "claude-key"
        assert provider.config.model_name == "claude-3"

    @patch('ai_game_dev.providers.ChatGoogleGenerativeAI')
    def test_setup_google_with_key(self, mock_chat):
        """Test Google setup with API key."""
        provider = setup_google(api_key="google-key", model="gemini-pro")
        
        assert isinstance(provider, GoogleProvider)
        assert provider.config.api_key == "google-key"
        assert provider.config.model_name == "gemini-pro"

    @patch('ai_game_dev.providers.Ollama')
    def test_setup_ollama_with_model(self, mock_ollama):
        """Test Ollama setup with model."""
        provider = setup_ollama(model="llama3.1:8b")
        
        assert isinstance(provider, OllamaProvider)
        assert provider.config.model_name == "llama3.1:8b"

    @patch.dict(os.environ, {"OPENAI_API_KEY": "env-openai-key"})
    @patch('ai_game_dev.providers.ChatOpenAI')
    def test_create_default_manager_with_openai(self, mock_chat):
        """Test creating default manager with OpenAI from environment."""
        manager = create_default_manager()
        
        assert "openai" in manager._providers
        assert manager._default_provider == "openai"

    @patch.dict(os.environ, {}, clear=True)
    def test_create_default_manager_no_keys(self):
        """Test creating default manager with no API keys."""
        manager = create_default_manager()
        
        assert len(manager._providers) == 0
        assert manager._default_provider is None
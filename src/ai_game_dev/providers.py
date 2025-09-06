"""Multi-LLM provider support for AI Game Development.

Supports OpenAI, Anthropic, Google Gemini, and local LLM providers
with unified interface for game generation workflows.
"""

from typing import Any, Dict, List, Optional, Union, Literal
from dataclasses import dataclass
from enum import Enum
import os
from abc import ABC, abstractmethod

# LLM Provider imports with graceful fallbacks
try:
    from langchain_openai import ChatOpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    ChatOpenAI = None
    OPENAI_AVAILABLE = False

try:
    from langchain_anthropic import ChatAnthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ChatAnthropic = None
    ANTHROPIC_AVAILABLE = False

try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    GOOGLE_AVAILABLE = True
except ImportError:
    ChatGoogleGenerativeAI = None
    GOOGLE_AVAILABLE = False

try:
    from langchain_community.llms import Ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    Ollama = None
    OLLAMA_AVAILABLE = False

try:
    from langchain_core.language_models import BaseLanguageModel
    from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
    LANGCHAIN_CORE_AVAILABLE = True
except ImportError:
    BaseLanguageModel = None
    BaseMessage = None
    HumanMessage = None
    SystemMessage = None
    LANGCHAIN_CORE_AVAILABLE = False


class LLMProvider(Enum):
    """Supported LLM providers."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    OLLAMA = "ollama"
    CUSTOM = "custom"


@dataclass
class ModelConfig:
    """Configuration for a specific LLM model."""
    provider: LLMProvider
    model_name: str
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    additional_params: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.additional_params is None:
            self.additional_params = {}


class BaseLLMProvider(ABC):
    """Abstract base class for LLM providers."""
    
    def __init__(self, config: ModelConfig):
        self.config = config
        self._model: Optional[BaseLanguageModel] = None
    
    @abstractmethod
    def _create_model(self) -> BaseLanguageModel:
        """Create the LangChain model instance."""
        pass
    
    @property
    def model(self) -> BaseLanguageModel:
        """Get or create the model instance."""
        if self._model is None:
            self._model = self._create_model()
        return self._model
    
    def invoke(self, messages: Union[str, List[BaseMessage]], **kwargs) -> str:
        """Invoke the model with messages."""
        if isinstance(messages, str):
            messages = [HumanMessage(content=messages)]
        
        response = self.model.invoke(messages, **kwargs)
        return response.content if hasattr(response, 'content') else str(response)
    
    async def ainvoke(self, messages: Union[str, List[BaseMessage]], **kwargs) -> str:
        """Async invoke the model with messages."""
        if isinstance(messages, str):
            messages = [HumanMessage(content=messages)]
        
        response = await self.model.ainvoke(messages, **kwargs)
        return response.content if hasattr(response, 'content') else str(response)


class OpenAIProvider(BaseLLMProvider):
    """OpenAI provider implementation."""
    
    def _create_model(self) -> BaseLanguageModel:
        api_key = self.config.api_key or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OpenAI API key required")
        
        return ChatOpenAI(
            model=self.config.model_name,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens,
            api_key=api_key,
            **self.config.additional_params
        )


class AnthropicProvider(BaseLLMProvider):
    """Anthropic Claude provider implementation."""
    
    def _create_model(self) -> BaseLanguageModel:
        api_key = self.config.api_key or os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("Anthropic API key required")
        
        return ChatAnthropic(
            model=self.config.model_name,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens,
            api_key=api_key,
            **self.config.additional_params
        )


class GoogleProvider(BaseLLMProvider):
    """Google Gemini provider implementation."""
    
    def _create_model(self) -> BaseLanguageModel:
        api_key = self.config.api_key or os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("Google API key required")
        
        return ChatGoogleGenerativeAI(
            model=self.config.model_name,
            temperature=self.config.temperature,
            max_output_tokens=self.config.max_tokens,
            google_api_key=api_key,
            **self.config.additional_params
        )


class OllamaProvider(BaseLLMProvider):
    """Ollama local LLM provider implementation."""
    
    def _create_model(self) -> BaseLanguageModel:
        base_url = self.config.base_url or "http://localhost:11434"
        
        return Ollama(
            model=self.config.model_name,
            temperature=self.config.temperature,
            base_url=base_url,
            **self.config.additional_params
        )


class LLMProviderManager:
    """Manager for multiple LLM providers with fallback support."""
    
    PROVIDER_CLASSES = {
        LLMProvider.OPENAI: OpenAIProvider,
        LLMProvider.ANTHROPIC: AnthropicProvider,
        LLMProvider.GOOGLE: GoogleProvider,
        LLMProvider.OLLAMA: OllamaProvider,
    }
    
    # Recommended models for each provider
    RECOMMENDED_MODELS = {
        LLMProvider.OPENAI: [
            "gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo"
        ],
        LLMProvider.ANTHROPIC: [
            "claude-3-5-sonnet-20241022", "claude-3-haiku-20240307", "claude-3-opus-20240229"
        ],
        LLMProvider.GOOGLE: [
            "gemini-1.5-pro", "gemini-1.5-flash", "gemini-pro"
        ],
        LLMProvider.OLLAMA: [
            "llama3.1:8b", "llama3.1:70b", "codellama", "mistral", "qwen2.5"
        ]
    }
    
    def __init__(self):
        self._providers: Dict[str, BaseLLMProvider] = {}
        self._default_provider: Optional[str] = None
    
    def add_provider(
        self,
        name: str,
        provider_type: LLMProvider,
        model_name: str,
        **kwargs
    ) -> BaseLLMProvider:
        """Add a new provider configuration."""
        
        config = ModelConfig(
            provider=provider_type,
            model_name=model_name,
            **kwargs
        )
        
        if provider_type not in self.PROVIDER_CLASSES:
            raise ValueError(f"Unsupported provider: {provider_type}")
        
        provider_class = self.PROVIDER_CLASSES[provider_type]
        provider = provider_class(config)
        
        self._providers[name] = provider
        
        # Set as default if it's the first provider
        if self._default_provider is None:
            self._default_provider = name
        
        return provider
    
    def get_provider(self, name: Optional[str] = None) -> BaseLLMProvider:
        """Get a provider by name, or the default provider."""
        if name is None:
            name = self._default_provider
        
        if name is None or name not in self._providers:
            raise ValueError(f"Provider '{name}' not found")
        
        return self._providers[name]
    
    def set_default_provider(self, name: str):
        """Set the default provider."""
        if name not in self._providers:
            raise ValueError(f"Provider '{name}' not found")
        self._default_provider = name
    
    def list_providers(self) -> List[str]:
        """List all configured provider names."""
        return list(self._providers.keys())
    
    def create_quick_setup(
        self,
        preferred_providers: Optional[List[LLMProvider]] = None
    ) -> "LLMProviderManager":
        """Create a quick setup with automatic provider detection."""
        
        if preferred_providers is None:
            preferred_providers = [
                LLMProvider.OPENAI,
                LLMProvider.ANTHROPIC, 
                LLMProvider.GOOGLE,
                LLMProvider.OLLAMA
            ]
        
        for provider_type in preferred_providers:
            try:
                # Try to set up with recommended model
                recommended_models = self.RECOMMENDED_MODELS.get(provider_type, [])
                if not recommended_models:
                    continue
                
                model_name = recommended_models[0]  # Use first recommended model
                
                # Attempt to add provider
                provider_name = f"{provider_type.value}_default"
                self.add_provider(
                    name=provider_name,
                    provider_type=provider_type,
                    model_name=model_name,
                    temperature=0.7
                )
                
                print(f"✅ Successfully configured {provider_type.value} with {model_name}")
                
            except Exception as e:
                print(f"⚠️  Could not configure {provider_type.value}: {e}")
                continue
        
        if not self._providers:
            raise RuntimeError("No LLM providers could be configured")
        
        return self
    
    async def generate_with_fallback(
        self,
        prompt: str,
        provider_names: Optional[List[str]] = None,
        **kwargs
    ) -> str:
        """Generate text with automatic fallback between providers."""
        
        if provider_names is None:
            provider_names = self.list_providers()
        
        last_error = None
        
        for provider_name in provider_names:
            try:
                provider = self.get_provider(provider_name)
                result = await provider.ainvoke(prompt, **kwargs)
                return result
            
            except Exception as e:
                last_error = e
                print(f"Provider {provider_name} failed: {e}")
                continue
        
        raise RuntimeError(f"All providers failed. Last error: {last_error}")


# Convenience functions for quick setup
def setup_openai(
    model: str = "gpt-4o-mini",
    api_key: Optional[str] = None,
    **kwargs
) -> OpenAIProvider:
    """Quick setup for OpenAI provider."""
    config = ModelConfig(
        provider=LLMProvider.OPENAI,
        model_name=model,
        api_key=api_key,
        **kwargs
    )
    return OpenAIProvider(config)


def setup_anthropic(
    model: str = "claude-3-5-sonnet-20241022", 
    api_key: Optional[str] = None,
    **kwargs
) -> AnthropicProvider:
    """Quick setup for Anthropic provider."""
    config = ModelConfig(
        provider=LLMProvider.ANTHROPIC,
        model_name=model,
        api_key=api_key,
        **kwargs
    )
    return AnthropicProvider(config)


def setup_google(
    model: str = "gemini-1.5-flash",
    api_key: Optional[str] = None,
    **kwargs
) -> GoogleProvider:
    """Quick setup for Google provider."""
    config = ModelConfig(
        provider=LLMProvider.GOOGLE,
        model_name=model,
        api_key=api_key,
        **kwargs
    )
    return GoogleProvider(config)


def setup_ollama(
    model: str = "llama3.1:8b",
    base_url: str = "http://localhost:11434",
    **kwargs
) -> OllamaProvider:
    """Quick setup for Ollama provider."""
    config = ModelConfig(
        provider=LLMProvider.OLLAMA,
        model_name=model,
        base_url=base_url,
        **kwargs
    )
    return OllamaProvider(config)


def create_default_manager() -> LLMProviderManager:
    """Create a provider manager with automatic setup."""
    manager = LLMProviderManager()
    return manager.create_quick_setup()
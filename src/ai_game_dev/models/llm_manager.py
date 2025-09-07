"""LLM Manager for coordinating multiple language model providers."""

import os
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum

from langchain_openai import ChatOpenAI
from langchain_core.language_models import BaseChatModel


class LLMProvider(Enum):
    """Supported LLM providers."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    OLLAMA = "ollama"


@dataclass
class LLMConfig:
    """Configuration for LLM provider."""
    provider: LLMProvider
    model_name: str
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    temperature: float = 0.7
    max_tokens: Optional[int] = None


class LLMManager:
    """Manager for multiple LLM providers with automatic fallback."""
    
    def __init__(self):
        """Initialize LLM manager with available providers."""
        self.providers: Dict[LLMProvider, BaseChatModel] = {}
        self.primary_provider: Optional[LLMProvider] = None
        self._initialize_providers()
    
    def _initialize_providers(self):
        """Initialize available LLM providers based on API keys."""
        
        # OpenAI
        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key:
            self.providers[LLMProvider.OPENAI] = ChatOpenAI(
                api_key=openai_key,
                model="gpt-4",
                temperature=0.7
            )
            if not self.primary_provider:
                self.primary_provider = LLMProvider.OPENAI
        
        # Set primary provider to first available
        if not self.primary_provider and self.providers:
            self.primary_provider = list(self.providers.keys())[0]
    
    def get_primary_llm(self) -> BaseChatModel:
        """Get the primary LLM instance."""
        if not self.primary_provider or self.primary_provider not in self.providers:
            raise RuntimeError("No LLM providers available")
        
        return self.providers[self.primary_provider]
    
    def get_llm(self, provider: Optional[LLMProvider] = None) -> BaseChatModel:
        """Get LLM instance for specified provider or primary."""
        if provider is None:
            return self.get_primary_llm()
        
        if provider not in self.providers:
            raise ValueError(f"Provider {provider} not available")
        
        return self.providers[provider]
    
    def list_available_providers(self) -> List[LLMProvider]:
        """List all available providers."""
        return list(self.providers.keys())
    
    def is_provider_available(self, provider: LLMProvider) -> bool:
        """Check if a provider is available."""
        return provider in self.providers
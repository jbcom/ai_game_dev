"""Test configuration for OpenAI MCP Server."""

import os
import pytest
from pathlib import Path
from unittest.mock import Mock, AsyncMock

import pytest_asyncio
from openai import AsyncOpenAI

from openai_mcp_server.config import Settings


@pytest.fixture
def mock_settings():
    """Mock settings for testing."""
    settings = Mock(spec=Settings)
    settings.openai_api_key = "test-api-key"
    settings.cache_dir = Path("/tmp/test_cache")
    settings.data_dir = Path("/tmp/test_data")
    settings.enable_caching = True
    settings.cache_ttl = 3600
    settings.max_cache_size = 100 * 1024 * 1024
    return settings


@pytest.fixture
def mock_openai_client():
    """Mock OpenAI client for testing."""
    client = Mock(spec=AsyncOpenAI)
    
    # Mock image generation
    mock_images = Mock()
    mock_images.generate = AsyncMock(return_value=Mock(
        data=[Mock(url="https://example.com/image.png")]
    ))
    client.images = mock_images
    
    # Mock chat completions
    mock_chat = Mock()
    mock_chat.completions = Mock()
    mock_chat.completions.create = AsyncMock(return_value=Mock(
        choices=[Mock(message=Mock(content="Test response"))]
    ))
    client.chat = mock_chat
    
    return client


@pytest.fixture
def temp_cache_dir(tmp_path):
    """Create temporary cache directory."""
    cache_dir = tmp_path / "cache"
    cache_dir.mkdir(exist_ok=True)
    return cache_dir


@pytest.fixture
def temp_data_dir(tmp_path):
    """Create temporary data directory."""
    data_dir = tmp_path / "data"
    data_dir.mkdir(exist_ok=True)
    return data_dir


@pytest.fixture(autouse=True)
def setup_test_env(monkeypatch, temp_cache_dir, temp_data_dir):
    """Set up test environment."""
    monkeypatch.setenv("OPENAI_API_KEY", "test-api-key")
    monkeypatch.setenv("XDG_CACHE_HOME", str(temp_cache_dir))
    monkeypatch.setenv("XDG_DATA_HOME", str(temp_data_dir))


@pytest.fixture
def sample_game_spec():
    """Sample game specification for testing."""
    return {
        "name": "Test RPG",
        "genre": "fantasy",
        "setting": "medieval world",
        "characters": [
            {"name": "Hero", "class": "warrior"},
            {"name": "Wizard", "class": "mage"}
        ],
        "locations": [
            {"name": "Village", "type": "town"},
            {"name": "Dark Forest", "type": "dungeon"}
        ]
    }
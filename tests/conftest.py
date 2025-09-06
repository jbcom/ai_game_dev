"""Shared test configuration and fixtures."""
import pytest
import asyncio
from unittest.mock import MagicMock, AsyncMock
from pathlib import Path
import tempfile
import shutil
from typing import Generator, AsyncGenerator

# Test data directory
TEST_DATA_DIR = Path(__file__).parent / "fixtures"
TEST_DATA_DIR.mkdir(exist_ok=True)


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield Path(tmp_dir)


@pytest.fixture
def mock_openai_client():
    """Mock OpenAI client for testing."""
    client = MagicMock()
    client.audio = MagicMock()
    client.audio.speech = MagicMock()
    client.audio.speech.create = AsyncMock(return_value=MagicMock(content=b"fake_audio_data"))
    return client


@pytest.fixture
def mock_anthropic_client():
    """Mock Anthropic client for testing."""
    client = MagicMock()
    client.messages = MagicMock()
    client.messages.create = AsyncMock(return_value=MagicMock(content=[MagicMock(text="Mock response")]))
    return client


@pytest.fixture
def mock_google_client():
    """Mock Google AI client for testing."""
    client = MagicMock()
    client.generate_content = AsyncMock(return_value=MagicMock(text="Mock Google response"))
    return client


@pytest.fixture
async def mock_aiohttp_session():
    """Mock aiohttp session for HTTP requests."""
    session = AsyncMock()
    
    # Mock successful JSON response
    response = AsyncMock()
    response.status = 200
    response.json = AsyncMock(return_value={"response": {"docs": []}})
    response.__aenter__ = AsyncMock(return_value=response)
    response.__aexit__ = AsyncMock(return_value=None)
    
    session.get.return_value = response
    session.post.return_value = response
    
    return session


@pytest.fixture
def sample_game_description():
    """Sample game description for testing."""
    return {
        "title": "Space Adventure",
        "genre": "Action/Adventure",
        "description": "A thrilling space exploration game with epic battles",
        "target_audience": "Teen",
        "platform": "PC/Console",
        "art_style": "Sci-fi, futuristic"
    }


@pytest.fixture
def sample_engine_config():
    """Sample engine configuration for testing."""
    return {
        "engine": "pygame",
        "resolution": "1920x1080",
        "fps": 60,
        "audio": True,
        "multiplayer": False
    }


# Mock environment variables for testing
@pytest.fixture(autouse=True)
def mock_env_vars(monkeypatch):
    """Mock environment variables for all tests."""
    monkeypatch.setenv("OPENAI_API_KEY", "test_openai_key")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test_anthropic_key")
    monkeypatch.setenv("GOOGLE_API_KEY", "test_google_key")
    monkeypatch.setenv("FREESOUND_API_KEY", "test_freesound_key")
"""Configuration for end-to-end tests with real OpenAI integration."""
import os
import pytest
import vcr
from pathlib import Path


@pytest.fixture
def vcr_config():
    """Configure VCR for OpenAI API recording/replay."""
    return {
        "filter_headers": [
            ("authorization", "DUMMY"),
            ("openai-organization", "DUMMY"),
        ],
        "filter_query_parameters": ["key", "api_key"],
        "decode_compressed_response": True,
        "record_mode": "once",
    }


@pytest.fixture
def openai_vcr(vcr_config):
    """VCR instance configured for OpenAI API calls."""
    cassette_dir = Path(__file__).parent / "cassettes"
    cassette_dir.mkdir(exist_ok=True)
    
    return vcr.VCR(
        cassette_library_dir=str(cassette_dir),
        **vcr_config
    )


@pytest.fixture
def e2e_output_dir():
    """Directory for E2E test outputs."""
    output_dir = Path(__file__).parent / "outputs"
    output_dir.mkdir(exist_ok=True)
    return output_dir


@pytest.fixture
def real_openai_key():
    """Get real OpenAI API key from environment."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.skip("OPENAI_API_KEY not set - skipping E2E tests")
    return api_key
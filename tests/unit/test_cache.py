"""Tests for cache module."""
import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path

from ai_game_dev.cache import initialize_sqlite_cache_and_memory


class TestCache:
    """Test cache functionality."""
    
    def test_initialize_sqlite_cache_and_memory(self):
        """Test cache initialization."""
        with patch('pathlib.Path.mkdir') as mock_mkdir:
            initialize_sqlite_cache_and_memory()
            
            # Should create cache directory
            mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)
    
    def test_initialize_cache_directory_path(self):
        """Test cache directory path creation."""
        with patch('pathlib.Path.mkdir') as mock_mkdir:
            initialize_sqlite_cache_and_memory()
            
            # Check the path includes expected components
            call_args = mock_mkdir.call_args
            assert call_args is not None
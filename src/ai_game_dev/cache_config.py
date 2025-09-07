"""
LangChain LLM Caching and SQLite Memory Configuration
Implements persistent caching and memory using LangChain with XDG directories
"""

import os
from pathlib import Path
from typing import Optional

from xdg_base_dirs import xdg_cache_home, xdg_data_home
from langchain.globals import set_llm_cache
from langchain_community.cache import SQLiteCache
from langchain_community.memory import SQLChatMessageHistory
from langchain_community.chat_message_histories import StreamlitChatMessageHistory
from langchain.memory import ConversationBufferMemory


def get_cache_directory() -> Path:
    """Get XDG-compliant cache directory for LLM caching."""
    cache_dir = xdg_cache_home() / "ai-game-dev" / "llm-cache"
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir


def get_data_directory() -> Path:
    """Get XDG-compliant data directory for memory persistence."""
    data_dir = xdg_data_home() / "ai-game-dev" / "memory"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


def setup_llm_cache():
    """Set up persistent LLM caching using LangChain SQLiteCache in XDG cache directory."""
    cache_dir = get_cache_directory()
    cache_db_path = cache_dir / "llm_cache.db"
    
    # Initialize LangChain SQLiteCache
    cache = SQLiteCache(database_path=str(cache_db_path))
    set_llm_cache(cache)
    
    print(f"✅ LangChain SQLite caching enabled: {cache_db_path}")
    return cache


def create_persistent_memory(session_id: str) -> ConversationBufferMemory:
    """Create persistent conversation memory using LangChain SQLChatMessageHistory in XDG data directory."""
    data_dir = get_data_directory()
    memory_db_path = data_dir / "conversation_memory.db"
    
    # Create LangChain SQLChatMessageHistory for persistence
    message_history = SQLChatMessageHistory(
        session_id=session_id,
        connection_string=f"sqlite:///{memory_db_path}"
    )
    
    # Create LangChain conversation buffer memory with persistence
    memory = ConversationBufferMemory(
        chat_memory=message_history,
        return_messages=True,
        memory_key="chat_history"
    )
    
    print(f"✅ LangChain SQLite memory enabled for session {session_id}: {memory_db_path}")
    return memory


def get_memory_for_session(session_id: str) -> ConversationBufferMemory:
    """Get or create LangChain persistent memory for a specific session."""
    return create_persistent_memory(session_id)


def initialize_sqlite_cache_and_memory():
    """Initialize both LangChain SQLite caching and memory persistence."""
    print("🚀 Initializing LangChain SQLite caching and memory persistence...")
    
    # Set up LangChain SQLite caching
    cache = setup_llm_cache()
    
    # Verify cache directory exists and is writable
    cache_dir = get_cache_directory()
    test_file = cache_dir / "test_write"
    try:
        test_file.write_text("test")
        test_file.unlink()
        print(f"✅ LangChain cache directory writable: {cache_dir}")
    except Exception as e:
        print(f"❌ LangChain cache directory not writable: {e}")
    
    # Verify data directory exists and is writable
    data_dir = get_data_directory()
    test_file = data_dir / "test_write"
    try:
        test_file.write_text("test")
        test_file.unlink()
        print(f"✅ LangChain data directory writable: {data_dir}")
    except Exception as e:
        print(f"❌ LangChain data directory not writable: {e}")
    
    print("✅ LangChain SQLite cache and memory persistence initialized successfully")
    return cache


def clear_cache():
    """Clear the LangChain SQLite cache database."""
    cache_dir = get_cache_directory()
    cache_db_path = cache_dir / "llm_cache.db"
    
    if cache_db_path.exists():
        cache_db_path.unlink()
        print(f"✅ LangChain cache cleared: {cache_db_path}")
    else:
        print("ℹ️ No LangChain cache to clear")


def clear_memory(session_id: Optional[str] = None):
    """Clear LangChain conversation memory for a specific session or all sessions."""
    data_dir = get_data_directory()
    memory_db_path = data_dir / "conversation_memory.db"
    
    if not memory_db_path.exists():
        print("ℹ️ No LangChain memory database to clear")
        return
    
    if session_id:
        # Clear specific session using LangChain SQLChatMessageHistory
        message_history = SQLChatMessageHistory(
            session_id=session_id,
            connection_string=f"sqlite:///{memory_db_path}"
        )
        message_history.clear()
        print(f"✅ LangChain memory cleared for session: {session_id}")
    else:
        # Clear all memory
        memory_db_path.unlink()
        print("✅ All LangChain conversation memory cleared")


if __name__ == "__main__":
    # Test the LangChain cache and memory setup
    initialize_sqlite_cache_and_memory()
    
    # Test LangChain memory creation
    test_memory = create_persistent_memory("test_session")
    print("✅ Test LangChain memory created successfully")
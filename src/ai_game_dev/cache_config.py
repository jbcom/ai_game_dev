"""
LangChain LLM Caching and SQLite Memory Configuration
Implements persistent caching and memory using SQLite in XDG directories
"""

import os
from pathlib import Path
import sqlite3
from typing import Optional

from xdg_base_dirs import xdg_cache_home, xdg_data_home
from langchain.globals import set_llm_cache
from langchain_community.cache import SQLiteCache
from langchain_community.memory import SQLChatMessageHistory
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
    """Set up persistent LLM caching using SQLite in XDG cache directory."""
    cache_dir = get_cache_directory()
    cache_db_path = cache_dir / "llm_cache.db"
    
    # Initialize SQLite cache for LLM responses
    cache = SQLiteCache(database_path=str(cache_db_path))
    set_llm_cache(cache)
    
    print(f"✅ LLM SQLite caching enabled: {cache_db_path}")
    return cache


def setup_sqlite_memory():
    """Set up SQLite-based conversation memory in XDG data directory."""
    data_dir = get_data_directory()
    memory_db_path = data_dir / "conversation_memory.db"
    
    # Create the SQLite database for memory if it doesn't exist
    conn = sqlite3.connect(memory_db_path)
    
    # Create the message_store table for SQLChatMessageHistory
    conn.execute("""
        CREATE TABLE IF NOT EXISTS message_store (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            message TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create index for faster session queries
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_session_id 
        ON message_store(session_id)
    """)
    
    conn.commit()
    conn.close()
    
    print(f"✅ SQLite memory database initialized: {memory_db_path}")
    return memory_db_path


def create_sqlite_memory(session_id: str) -> ConversationBufferMemory:
    """Create persistent conversation memory using SQLite in XDG data directory."""
    data_dir = get_data_directory()
    memory_db_path = data_dir / "conversation_memory.db"
    
    # Create SQLChatMessageHistory for SQLite persistence
    message_history = SQLChatMessageHistory(
        session_id=session_id,
        connection_string=f"sqlite:///{memory_db_path}"
    )
    
    # Create conversation buffer memory with SQLite persistence
    memory = ConversationBufferMemory(
        chat_memory=message_history,
        return_messages=True,
        memory_key="chat_history"
    )
    
    print(f"✅ SQLite memory enabled for session {session_id}")
    return memory


def get_memory_for_session(session_id: str) -> ConversationBufferMemory:
    """Get or create SQLite persistent memory for a specific session."""
    return create_sqlite_memory(session_id)


def initialize_sqlite_cache_and_memory():
    """Initialize both SQLite LLM caching and SQLite memory persistence."""
    print("🚀 Initializing SQLite caching and memory persistence...")
    
    # Set up SQLite LLM caching
    cache = setup_llm_cache()
    
    # Set up SQLite memory database
    memory_db_path = setup_sqlite_memory()
    
    # Verify cache directory exists and is writable
    cache_dir = get_cache_directory()
    test_file = cache_dir / "test_write"
    try:
        test_file.write_text("test")
        test_file.unlink()
        print(f"✅ SQLite cache directory writable: {cache_dir}")
    except Exception as e:
        print(f"❌ SQLite cache directory not writable: {e}")
    
    # Verify data directory exists and is writable
    data_dir = get_data_directory()
    test_file = data_dir / "test_write"
    try:
        test_file.write_text("test")
        test_file.unlink()
        print(f"✅ SQLite data directory writable: {data_dir}")
    except Exception as e:
        print(f"❌ SQLite data directory not writable: {e}")
    
    print("✅ SQLite cache and memory persistence initialized successfully")
    return cache, memory_db_path


def clear_sqlite_cache():
    """Clear the SQLite LLM cache database."""
    cache_dir = get_cache_directory()
    cache_db_path = cache_dir / "llm_cache.db"
    
    if cache_db_path.exists():
        cache_db_path.unlink()
        print(f"✅ SQLite cache cleared: {cache_db_path}")
    else:
        print("ℹ️ No SQLite cache to clear")


def clear_sqlite_memory(session_id: Optional[str] = None):
    """Clear SQLite conversation memory for a specific session or all sessions."""
    data_dir = get_data_directory()
    memory_db_path = data_dir / "conversation_memory.db"
    
    if not memory_db_path.exists():
        print("ℹ️ No SQLite memory database to clear")
        return
    
    conn = sqlite3.connect(memory_db_path)
    
    if session_id:
        # Clear specific session from SQLite
        conn.execute("DELETE FROM message_store WHERE session_id = ?", (session_id,))
        conn.commit()
        print(f"✅ SQLite memory cleared for session: {session_id}")
    else:
        # Clear all memory from SQLite
        conn.execute("DELETE FROM message_store")
        conn.commit()
        print("✅ All SQLite conversation memory cleared")
    
    conn.close()


if __name__ == "__main__":
    # Test the SQLite cache and memory setup
    initialize_sqlite_cache_and_memory()
    
    # Test SQLite memory creation
    test_memory = create_sqlite_memory("test_session")
    print("✅ Test SQLite memory created successfully")
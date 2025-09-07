#!/usr/bin/env python3
"""
Production-ready entry point for AI Game Development Platform.
Uses proper FastAPI + Jinja2 template architecture.
"""
import sys
import os
import sqlite3
from pathlib import Path

# Add src to path for imports
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

def init_player_db():
    """Initialize player database for user progression tracking."""
    db_path = Path("data/player.db")
    db_path.parent.mkdir(exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create player table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS players (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL DEFAULT 'Developer',
            level INTEGER DEFAULT 1,
            xp INTEGER DEFAULT 0,
            games_created INTEGER DEFAULT 0,
            modules_completed INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Initialize default player if none exists
    cursor.execute('SELECT COUNT(*) FROM players')
    if cursor.fetchone()[0] == 0:
        cursor.execute('''
            INSERT INTO players (name, level, xp, games_created, modules_completed)
            VALUES ('Developer', 1, 0, 0, 0)
        ''')
    
    conn.commit()
    conn.close()
    print(f"📊 Player database initialized at {db_path}")

def main():
    """Main entry point using Chainlit for direct subgraph orchestration."""
    # Initialize player database
    init_player_db()
    
    print("🚀 Starting AI Game Development Platform with Chainlit...")
    print("✅ Direct LangGraph subgraph orchestration")
    print("🎮 Game Workshop | 🎓 Arcade Academy")
    print("📊 SQLite persistence enabled")
    print("🌐 Opening http://localhost:8000")
    
    # Run Chainlit app
    import subprocess
    import sys
    subprocess.run([
        sys.executable, "-m", "chainlit", "run", 
        "src/ai_game_dev/chainlit_app.py",
        "--port", "8000"
    ])

if __name__ == "__main__":
    main()
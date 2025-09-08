#!/usr/bin/env python3
"""
Entry point for AI Game Development Platform.
Uses OpenAI agents with Chainlit UI.
"""
import os
import socket
import sqlite3
import subprocess
import sys
from pathlib import Path

# Add src to path for imports
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))


def init_player_db():
    """Initialize player database for progression tracking."""
    db_path = Path("data/player.db")
    db_path.parent.mkdir(exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS players (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL DEFAULT 'Developer',
            level INTEGER DEFAULT 1,
            xp INTEGER DEFAULT 0,
            games_created INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Initialize default player if none exists
    cursor.execute('SELECT COUNT(*) FROM players')
    if cursor.fetchone()[0] == 0:
        cursor.execute(
            'INSERT INTO players (name) VALUES (?)',
            ('Developer',)
        )
    
    conn.commit()
    conn.close()


def main():
    """Main entry point."""
    # Initialize database
    init_player_db()
    
    print("🚀 AI Game Development Platform")
    print("🤖 Powered by OpenAI Agents")
    print("🎮 Game Workshop | 🎓 Arcade Academy")
    
    # Get port from environment
    port = int(os.environ.get('AI_GAME_DEV_PORT', '8000'))
    
    # Check port availability
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(('127.0.0.1', port))
        except OSError:
            print(f"❌ Port {port} is already in use!")
            print("Set AI_GAME_DEV_PORT environment variable to use a different port")
            sys.exit(1)
    
    print(f"🌐 Starting server on http://localhost:{port}")
    print("")
    
    # Run Chainlit
    try:
        result = subprocess.run([
            sys.executable, "-m", "chainlit", "run",
            "src/ai_game_dev/chainlit_app.py",
            "--port", str(port),
            "--custom-frontend"
        ], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start server: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n👋 Shutting down...")
        sys.exit(0)


if __name__ == "__main__":
    main()
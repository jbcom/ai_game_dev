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
    
    # Run Chainlit app
    import subprocess
    import sys
    
    try:
        # Check if Chainlit is installed
        import chainlit
    except ImportError:
        print("❌ Error: Chainlit is not installed!")
        print("Please install it with: pip install chainlit")
        print("Or run: hatch env create")
        sys.exit(1)
    
    # Check if port is available
    import socket
    port = 8000
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(('127.0.0.1', port))
        except OSError:
            print(f"❌ Error: Port {port} is already in use!")
            print("Please stop any other services running on this port")
            print("Or set a different port with environment variable: AI_GAME_DEV_PORT=8001")
            sys.exit(1)
    
    # Get port from environment or use default
    import os
    port = int(os.environ.get('AI_GAME_DEV_PORT', '8000'))
    
    print(f"🌐 Opening http://localhost:{port}")
    print("")
    
    try:
        result = subprocess.run([
            sys.executable, "-m", "chainlit", "run", 
            "src/ai_game_dev/chainlit_app.py",
            "--port", str(port)
        ], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: Failed to start Chainlit server!")
        print(f"Exit code: {e.returncode}")
        if e.returncode == 1:
            print("This might be due to:")
            print("  - Missing chainlit_app.py file")
            print("  - Syntax errors in the application")
            print("  - Missing dependencies")
        print("\nTry running with debug mode:")
        print(f"  chainlit run src/ai_game_dev/chainlit_app.py --port {port} --debug")
        sys.exit(1)
    except FileNotFoundError:
        print("❌ Error: Python executable not found!")
        print("Please ensure Python is properly installed")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n👋 Shutting down AI Game Development Platform...")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        print("Please report this issue on GitHub")
        sys.exit(1)

if __name__ == "__main__":
    main()
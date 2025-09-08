"""Main entry point for ai-game-dev package."""

import os
import socket
import subprocess
import sys
from pathlib import Path


def check_port_available(port: int) -> bool:
    """Check if a port is available for binding."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(('127.0.0.1', port))
            return True
        except OSError:
            return False


def main():
    """Run the AI Game Development Platform with Chainlit UI."""
    print("🚀 AI Game Development Platform")
    print("🤖 Powered by OpenAI Agents (GPT-5 & GPT-Image-1)")
    print("🎮 Game Workshop | 🎓 Arcade Academy")
    print("")
    
    # Get port from environment or use default
    port = int(os.environ.get('AI_GAME_DEV_PORT', '8000'))
    
    # Check if port is available
    if not check_port_available(port):
        print(f"❌ Port {port} is already in use!")
        print("💡 Set AI_GAME_DEV_PORT environment variable to use a different port")
        sys.exit(1)
    
    print(f"🌐 Starting server on http://localhost:{port}")
    print("")
    
    # Find the chainlit app relative to this file
    chainlit_app = Path(__file__).parent / "chainlit_app.py"
    
    # Run Chainlit with custom frontend enabled
    cmd = [
        sys.executable, "-m", "chainlit", "run",
        str(chainlit_app),
        "--port", str(port),
        "--custom-frontend"
    ]
    
    try:
        result = subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start Chainlit: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n👋 Shutting down gracefully...")
        sys.exit(0)


if __name__ == "__main__":
    main()
"""
Entry point for the unified AI Game Development Server.
Combines FastMCP and Mesop in a single HTTP server.
"""

from ai_game_dev.server import run_server

if __name__ == "__main__":
    # Start the unified server on port 5000
    run_server(host="0.0.0.0", port=5000)
#!/usr/bin/env python3
"""
Main entry point for the AI Game Development FastMCP Server
Run with: python main.py
Or with FastMCP CLI: fastmcp run server.py:mcp
"""

import sys
from pathlib import Path

# Add current directory to path for local imports
sys.path.insert(0, str(Path(__file__).parent))

# Import the server to run it
from server import mcp

if __name__ == "__main__":
    print("🚀 AI Game Development FastMCP Server")
    print("🤖 Available tools:")
    print("  - generate_game: Create complete game projects")
    print("  - generate_assets: Create images, sounds, and music")
    print("  - list_game_engines: Show supported engines")
    print("=" * 50)
    
    # Run the server
    mcp.run()

def main():
    """Main entry point for the MCP server."""
    print("🚀 AI Game Development FastMCP Server")
    print("🤖 Available tools:")
    print("  - generate_game: Create complete game projects")
    print("  - generate_assets: Create images, sounds, and music")
    print("  - list_game_engines: Show supported engines")
    print("=" * 50)
    
    # Import and run the server
    from server import mcp
    mcp.run()
"""
AI Game Development FastMCP Server
Model Context Protocol server providing game development capabilities using FastMCP
"""

__version__ = "1.0.0"
__author__ = "AI Game Dev Team"

from ai_game_dev.mcp_server.server import mcp

__all__ = [
    "mcp",
]
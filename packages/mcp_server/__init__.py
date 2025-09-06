"""
AI Game Development MCP Server
Model Context Protocol server providing game development capabilities
"""

__version__ = "1.0.0"
__author__ = "AI Game Dev Team"

from .server import MCPGameDevServer
from .tools import GameGenerationTool, AssetGenerationTool

__all__ = [
    "MCPGameDevServer",
    "GameGenerationTool", 
    "AssetGenerationTool",
]
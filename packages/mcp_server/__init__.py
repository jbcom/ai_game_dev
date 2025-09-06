"""
AI Game Development FastMCP Server
Model Context Protocol server providing game development capabilities using FastMCP
"""

__version__ = "1.0.0"
__author__ = "AI Game Dev Team"

from .server import create_server, start_server

__all__ = [
    "create_server",
    "start_server",
]
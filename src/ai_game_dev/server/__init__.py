"""
Unified AI Game Development Server
Combines FastMCP protocol endpoints with Mesop web interface in a single HTTP server.
"""

from .unified_server import UnifiedGameDevServer, run_server

__all__ = ["UnifiedGameDevServer", "run_server"]
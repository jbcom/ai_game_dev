"""
MCP Server for AI Game Development
Provides Model Context Protocol interface for game generation
"""

import asyncio
import json
from typing import Any, Dict, List, Optional
from pathlib import Path

from ai_game_dev import AIGameDev, GameSpec, GameType, ComplexityLevel
from ai_game_assets import AssetGenerator

from .tools import GameGenerationTool, AssetGenerationTool


class MCPGameDevServer:
    """Model Context Protocol server for AI game development."""
    
    def __init__(self):
        """Initialize the MCP server."""
        self.game_dev = AIGameDev()
        self.asset_gen = AssetGenerator()
        self.tools = {
            "generate_game": GameGenerationTool(self.game_dev),
            "generate_assets": AssetGenerationTool(self.asset_gen),
        }
        
    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming MCP requests."""
        method = request.get("method")
        params = request.get("params", {})
        
        if method == "tools/list":
            return await self._list_tools()
        elif method == "tools/call":
            return await self._call_tool(params)
        elif method == "initialize":
            return await self._initialize()
        else:
            return {"error": f"Unknown method: {method}"}
    
    async def _initialize(self) -> Dict[str, Any]:
        """Initialize the MCP server."""
        return {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {
                    "listChanged": True
                }
            },
            "serverInfo": {
                "name": "ai-game-dev-mcp-server",
                "version": "1.0.0"
            }
        }
    
    async def _list_tools(self) -> Dict[str, Any]:
        """List available tools."""
        tools = []
        for tool_name, tool in self.tools.items():
            tools.append({
                "name": tool_name,
                "description": tool.description,
                "inputSchema": tool.input_schema
            })
        
        return {"tools": tools}
    
    async def _call_tool(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Call a specific tool."""
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        if tool_name not in self.tools:
            return {"error": f"Unknown tool: {tool_name}"}
        
        try:
            tool = self.tools[tool_name]
            result = await tool.execute(arguments)
            return {"content": [{"type": "text", "text": result}]}
        except Exception as e:
            return {"error": f"Tool execution failed: {str(e)}"}
    
    async def start(self, host: str = "localhost", port: int = 8080):
        """Start the MCP server."""
        print(f"🚀 Starting AI Game Development MCP Server on {host}:{port}")
        print("🤖 Available tools:")
        for tool_name, tool in self.tools.items():
            print(f"  - {tool_name}: {tool.description}")
        
        # In a real implementation, this would start a proper MCP transport
        # For now, we'll just keep the server running
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Server shutdown")


async def create_server() -> MCPGameDevServer:
    """Create and return an MCP server instance."""
    return MCPGameDevServer()
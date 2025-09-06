#!/usr/bin/env python3
"""
Main entry point for the AI Game Development MCP Server
"""

import asyncio
import argparse
import sys
from pathlib import Path

from mcp_server.server import create_server


async def main():
    """Main entry point for the MCP server."""
    parser = argparse.ArgumentParser(description="AI Game Development MCP Server")
    parser.add_argument("--host", default="localhost", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8080, help="Port to bind to")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    
    args = parser.parse_args()
    
    print("🎮 AI Game Development MCP Server")
    print("=" * 40)
    print(f"🌐 Host: {args.host}")
    print(f"📡 Port: {args.port}")
    print(f"🔧 Debug: {args.debug}")
    print("=" * 40)
    
    try:
        # Create and start the server
        server = await create_server()
        await server.start(host=args.host, port=args.port)
        
    except KeyboardInterrupt:
        print("\n🛑 Server shutdown requested")
    except Exception as e:
        print(f"❌ Server error: {e}")
        sys.exit(1)


def cli_main():
    """CLI entry point."""
    asyncio.run(main())


if __name__ == "__main__":
    cli_main()
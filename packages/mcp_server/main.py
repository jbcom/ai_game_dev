#!/usr/bin/env python3
"""
Main entry point for the AI Game Development FastMCP Server
"""

import asyncio
import argparse
import sys
from pathlib import Path

# Add current directory to path for local imports
sys.path.insert(0, str(Path(__file__).parent))

from server import start_server, create_server


async def main():
    """Main entry point for the MCP server."""
    parser = argparse.ArgumentParser(description="AI Game Development FastMCP Server")
    parser.add_argument("--host", default="localhost", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8080, help="Port to bind to")
    parser.add_argument("--transport", default="stdio", help="Transport type (stdio, sse, websocket)")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    
    args = parser.parse_args()
    
    try:
        # Start the FastMCP server
        await start_server(host=args.host, port=args.port)
        
    except KeyboardInterrupt:
        print("\n🛑 Server shutdown requested")
    except Exception as e:
        print(f"❌ Server error: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)


def cli_main():
    """CLI entry point."""
    asyncio.run(main())


if __name__ == "__main__":
    cli_main()
"""
Server-Sent Events (SSE) transport layer for MCP integration.
Based on the FastAPI SSE MCP implementation pattern.
"""
from mcp.server.sse import SseServerTransport
from starlette.applications import Starlette
from starlette.routing import Mount, Route
from mcp.server.fastmcp import FastMCP


def create_sse_server(mcp: FastMCP) -> Starlette:
    """
    Create a Starlette app that handles SSE connections and message handling.
    
    This creates the proper SSE transport layer for MCP clients to connect
    to our unified server using the Server-Sent Events protocol.
    """
    transport = SseServerTransport("/messages/")

    async def handle_sse(request):
        """Handle SSE connections for MCP clients."""
        async with transport.connect_sse(
            request.scope, request.receive, request._send
        ) as streams:
            await mcp._mcp_server.run(
                streams[0], streams[1], mcp._mcp_server.create_initialization_options()
            )

    # Create Starlette routes for SSE and message handling
    routes = [
        Route("/sse/", endpoint=handle_sse),
        Mount("/messages/", app=transport.handle_post_message),
    ]

    # Create a Starlette app
    return Starlette(routes=routes)
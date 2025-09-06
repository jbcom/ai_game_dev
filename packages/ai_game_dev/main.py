"""Main entry point for the OpenAI MCP Server."""

from openai_mcp_server.server import create_server


def main() -> None:
    """Main entry point for the MCP server."""
    mcp = create_server()
    mcp.run()


if __name__ == "__main__":
    main()
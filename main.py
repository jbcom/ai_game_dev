#!/usr/bin/env python3
"""
Clean entry point for the OpenAI MCP Server.
Uses the properly structured library modules.
"""

import sys
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from openai_mcp_server.main import main

if __name__ == "__main__":
    main()
# AI Game Development MCP Server

Model Context Protocol server for AI-powered game development capabilities.

## Features

- **Game Generation**: Create complete game projects from natural language descriptions
- **Asset Generation**: Generate images, sounds, and music for games
- **Multi-Engine Support**: Support for Pygame, Arcade, Bevy, and Godot
- **MCP Protocol**: Standard Model Context Protocol interface

## Installation

```bash
# Install from workspace
uv sync

# Or install as standalone package
pip install ai-game-dev-mcp-server
```

## Usage

### As MCP Server

```bash
# Start the MCP server
ai-game-dev-mcp --host localhost --port 8080

# With debug mode
ai-game-dev-mcp --debug
```

### As Python Module

```python
from mcp_server import create_server
import asyncio

async def main():
    server = await create_server()
    await server.start()

asyncio.run(main())
```

## MCP Tools

### generate_game

Generate a complete game project.

```json
{
  "name": "Space Adventure",
  "description": "A retro space shooter with power-ups",
  "game_type": "2d",
  "complexity": "intermediate",
  "features": ["shooting", "enemies", "power-ups"],
  "engine": "pygame"
}
```

### generate_assets

Generate game assets.

```json
{
  "asset_type": "image",
  "description": "Pixel art spaceship sprite",
  "style": "pixel_art",
  "resolution": "64x64"
}
```

## Configuration

Set up your environment variables:

```bash
export OPENAI_API_KEY=your_api_key_here
```

## Development

```bash
# Run tests
pytest packages/mcp_server/tests/

# Format code
black packages/mcp_server/
ruff check packages/mcp_server/
```
# GitHub Copilot Instructions

## Project Context
You are working on an AI-powered game development platform that uses OpenAI's latest models to generate complete games. The platform has two main modes:
- **Workshop Mode**: Create custom games with Pygame, Godot, or Bevy engines
- **Academy Mode**: Learn game development through AI-guided tutorials

## Key Technical Details
- **UI Framework**: Chainlit with custom React components
- **AI Framework**: OpenAI agents with structured function tools (NOT LangChain/LangGraph)
- **Models**: GPT-5 for text/code, GPT-Image-1 for images, TTS-1-HD for audio
- **Python Version**: 3.11+ with modern type hints

## Code Style Guidelines
```python
# CORRECT: Modern Python style
from ai_game_dev.constants import OPENAI_MODELS
from ai_game_dev.tools.openai_tools import generate_game_image

async def create_character(name: str, description: str) -> dict[str, str]:
    """Create a game character with generated assets."""
    image = await generate_game_image(
        prompt=f"Character portrait: {description}",
        style="pixel art"
    )
    return {"name": name, "image": image.local_path}

# INCORRECT: Old style - avoid these patterns
from typing import Optional, Dict  # Use built-in types
import os  # Use pathlib instead
try:
    import some_module  # No try/except for imports
except ImportError:
    pass
```

## Common Patterns to Suggest

### OpenAI Tool Functions
```python
from agents import function_tool
from openai import AsyncOpenAI

@function_tool
async def my_tool(param: str) -> str:
    """Tool description."""
    client = AsyncOpenAI()
    # Implementation
```

### Chainlit Handlers
```python
import chainlit as cl

@cl.on_message
async def handle_message(message: cl.Message):
    """Handle user messages."""
    # Process message
    await cl.Message(content="Response").send()
```

### File Path Handling
```python
from pathlib import Path
from ai_game_dev.constants import GENERATED_ASSETS_DIR

output_path = GENERATED_ASSETS_DIR / "sprites" / f"{name}.png"
output_path.parent.mkdir(parents=True, exist_ok=True)
```

## PR Review Suggestions
When reviewing PRs, suggest improvements for:

1. **Model Usage**
   - Suggest GPT-5 over GPT-4 for text/code generation
   - Suggest GPT-Image-1 over DALL-E-3 for image generation

2. **Async Patterns**
   - Convert synchronous I/O to async/await
   - Suggest parallel API calls with asyncio.gather()

3. **Error Handling**
   ```python
   # Suggest this pattern
   try:
       result = await api_call()
   except OpenAIError as e:
       logger.error(f"API error: {e}")
       # Fallback logic
   ```

4. **Type Hints**
   - Modern syntax: `list[str]`, `dict[str, Any]`, `str | None`
   - Avoid: `List[str]`, `Dict[str, Any]`, `Optional[str]`

5. **Constants Usage**
   - Import from constants.py instead of hardcoding
   - Suggest moving magic numbers/strings to constants

## Security Considerations
Always flag and suggest fixes for:
- Hardcoded API keys or secrets
- Unsanitized user input in prompts
- File operations outside designated directories
- Missing input validation

## Performance Optimizations
Suggest these patterns:
- Batch API requests when possible
- Cache frequently used assets
- Use streaming for large responses
- Implement progress indicators for long operations

## Testing Patterns
```python
# Suggest async test patterns
import pytest
from unittest.mock import AsyncMock

@pytest.mark.asyncio
async def test_tool_function():
    mock_client = AsyncMock()
    # Test implementation
```

## Documentation Standards
Suggest Google-style docstrings:
```python
def function(param1: str, param2: int = 0) -> bool:
    """Brief description.
    
    Args:
        param1: Description of param1.
        param2: Description of param2. Defaults to 0.
        
    Returns:
        Description of return value.
        
    Raises:
        ValueError: When param1 is empty.
    """
```
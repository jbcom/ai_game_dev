# Cursor AI Assistant Configuration

## Project Overview
This is an AI-powered game development platform that uses OpenAI's latest models (GPT-5 and GPT-Image-1) to generate complete games. The platform features two modes:
- **Workshop Mode**: For creating custom games with any engine (Pygame, Godot, Bevy)
- **Academy Mode**: For learning game development through guided tutorials

## Architecture Guidelines
- We use OpenAI agents with structured function tools, NOT LangChain/LangGraph
- Chainlit provides the web UI with custom React components
- All imports should be absolute (from `ai_game_dev` package root)
- Use modern Python type hints: `T | None` instead of `Optional[T]`
- No try/except blocks around imports - assume all dependencies are installed

## Code Style
- All imports at the top of files
- Use type hints for all function parameters and returns
- Prefer `pathlib.Path` over string paths
- Use async/await for all OpenAI API calls
- Follow PEP 8 with 100-character line limit

## Key Components
1. **OpenAI Tools** (`src/ai_game_dev/tools/openai_tools/`):
   - `image.py`: DALL-E image generation using gpt-image-1
   - `audio.py`: OpenAI TTS + music21 + Freesound API
   - `text.py`: GPT-5 for dialogue, quests, and code generation
   - `template_loader.py`: Jinja2 template management

2. **Constants** (`src/ai_game_dev/constants.py`):
   - Centralized configuration for models, paths, and settings
   - Always import constants instead of hardcoding values

3. **Agent** (`src/ai_game_dev/agent.py`):
   - Main OpenAI agent that orchestrates all tools
   - Handles both workshop and academy modes

4. **Chainlit App** (`src/ai_game_dev/chainlit_app.py`):
   - Web UI entry point
   - Manages wizard flows and user interactions

## Testing Guidelines
- Test all OpenAI tool functions with mock responses
- Verify file paths resolve correctly across platforms
- Check async operations don't block the UI
- Validate generated code compiles/runs

## Common Patterns
```python
# Import pattern
from ai_game_dev.constants import OPENAI_MODELS, GENERATED_ASSETS_DIR
from ai_game_dev.tools.openai_tools import generate_game_image

# Async pattern
async def create_asset(description: str) -> Path:
    result = await generate_game_image(
        prompt=description,
        model=OPENAI_MODELS["image"]["default"]
    )
    return result.local_path

# Path handling
output_path = GENERATED_ASSETS_DIR / "characters" / f"{name}.png"
output_path.parent.mkdir(parents=True, exist_ok=True)
```

## PR Review Focus Areas
1. **Model Usage**: Ensure GPT-5 and GPT-Image-1 are used appropriately
2. **Error Handling**: Graceful fallbacks for API failures
3. **Performance**: Parallel API calls where possible
4. **Security**: No hardcoded API keys, sanitize user inputs
5. **UI/UX**: Maintain cyberpunk theme consistency
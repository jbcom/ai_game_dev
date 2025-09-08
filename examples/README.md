# Game Specification Examples

This directory contains example game specifications that demonstrate how to define games for the AI Game Development Platform.

## What is a Game Spec?

A game specification is a TOML file that defines all aspects of your game, including:
- Basic metadata (title, engine, type)
- Game description and features
- Asset requirements (sprites, audio, backgrounds)
- Game mechanics and rules
- Level structure
- UI styling

## How to Use

### In the Web UI

1. Go to the Game Workshop
2. Choose "Upload Spec" instead of "Describe Game"
3. Upload your `.toml` file
4. The platform will validate your spec and generate the complete game

### Via API

```python
from ai_game_dev.specs.game_spec_loader import load_game_spec
from ai_game_dev.agent import create_game

# Load your spec
spec = load_game_spec("my_game.toml")

# Generate the game
game = await create_game(
    description=spec.description_full,
    engine=spec.engine,
    game_spec=spec.__dict__
)
```

## Spec Format

See the example files in this directory:
- `user_game_spec.toml` - A complete example showing all features
- Platform specs in `src/ai_game_dev/specs/`:
  - `educational_rpg.toml` - Full RPG with educational features
  - `example_platformer.toml` - Simple platformer
  - `example_space_shooter.toml` - Space shooter game

## Asset Mapping

The platform automatically maps your requested assets to:
1. Existing static assets (e.g., UI sounds, character sprites)
2. Generated assets created on demand
3. Engine-specific paths (Pygame, Godot, Bevy)

You don't need to worry about exact paths - just specify logical names and the platform will handle the rest!

## Tips

- Use descriptive names for assets (e.g., "player_hero.png" not "p1.png")
- Include all game mechanics in the `[game.mechanics]` section
- Specify educational features in `[game.educational]` for learning games
- The `save_path` can be relative (to project root) or absolute
- Assets paths are automatically adjusted for each engine
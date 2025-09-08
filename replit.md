# AI Game Development Platform on Replit

## 🚀 Quick Start

Click the **Run** button to start the AI Game Development Platform with Chainlit UI!

The platform will launch on port 8000 with:
- 🎮 **Game Workshop** - Create games with AI assistance
- 🎓 **Arcade Academy** - Learn programming through game development
- 🤖 **Direct LangGraph Integration** - No orchestrator overhead
- ✨ **Custom Cyberpunk UI** - Immersive development experience

## 🔧 Setup

### Environment Variables

Set these in your Replit Secrets:

```bash
OPENAI_API_KEY=your-openai-api-key      # Required for AI features
ANTHROPIC_API_KEY=your-anthropic-key    # Optional, for Claude
```

### First Run

When you first run the platform, it will:
1. Initialize the SQLite database
2. Generate platform assets (UI, audio, characters)
3. Create the NeoTokyo Academy RPG game
4. Start the Chainlit server

This may take a few minutes on first run as assets are generated.

## 🎯 Features

### Game Workshop
- **Natural Language → Game**: Describe your game idea in plain English
- **Multi-Engine Support**: Generate games for Pygame, Godot, or Bevy
- **Parallel Asset Generation**: Graphics, audio, dialogue, and quests
- **Smart Path Management**: Organized output in `generated_games/`

### Arcade Academy
- **Learn by Building**: Master programming through RPG development
- **Professor Pixel**: Your AI guide through coding concepts
- **Interactive Lessons**: Variables, loops, conditionals, functions, classes
- **Teachable Moments**: Code is annotated with educational insights

### Unified Specification
All platform configuration is in `src/ai_game_dev/specs/unified_platform_spec.toml`:
- Platform UI and branding assets
- Complete RPG game specification
- Audio requirements
- Path configurations

## 📁 Project Structure

```
/workspace/
├── src/ai_game_dev/         # Main application code
│   ├── agents/              # AI agents and subgraphs
│   │   └── subgraphs/       # Specialized workflows
│   ├── specs/               # Game and platform specifications
│   └── chainlit_custom_app.py # Main Chainlit application
├── public/                  # Web assets
│   ├── static/              # Static files
│   │   └── assets/          # Images, audio, video
│   └── components/          # React components
├── generated_games/         # Generated game projects
│   ├── workshop/            # User-created games
│   └── academy/             # Educational RPG
└── __main__.py              # Entry point
```

## 🛠️ Development

### Running Locally
```bash
python -m __main__
```

### Using Hatch Scripts
```bash
hatch run server      # Start the server
hatch run test        # Run tests
hatch run lint        # Run linters
```

### Modifying the Platform

1. **Add New Assets**: Edit `unified_platform_spec.toml`
2. **Change UI Theme**: Modify `public/style.css`
3. **Add Game Features**: Update subgraphs in `agents/subgraphs/`
4. **Extend Education**: Edit `academy_subgraph.py`

## 🐛 Troubleshooting

### Port Already in Use
Set a different port in Replit Secrets:
```
AI_GAME_DEV_PORT=8001
```

### Missing Dependencies
The platform uses `uv` for fast dependency installation. If packages are missing:
```bash
hatch env create
```

### Asset Generation Issues
Delete `.asset_manifest.json` to force regeneration:
```bash
rm data/asset_manifest.json
```

## 🚢 Deployment

This Replit is configured for Cloud Run deployment:
- Automatic scaling
- WebSocket support for real-time updates
- Persistent storage for generated content

## 📚 Architecture

### Chainlit Integration
- Custom React frontend with cyberpunk theme
- WebSocket communication for real-time updates
- Direct subgraph execution without orchestrator overhead

### LangGraph Subgraphs
- **GameSpecSubgraph**: Converts descriptions to specs
- **WorkshopSubgraph**: Orchestrates game generation
- **AcademySubgraph**: Adds educational features
- **GraphicsSubgraph**: Generates visual assets
- **AudioSubgraph**: Creates sounds and music
- **DialogueSubgraph**: Builds conversation trees
- **QuestSubgraph**: Designs game objectives

### Asset Management
- Idempotent generation with content hashing
- Organized directory structure
- Relative paths for portability
- Git-ignored generated content

## 🎨 Customization

### Themes
Edit `public/style.css` for visual changes

### Game Engines
Add new engines by:
1. Creating an agent in `agents/`
2. Adding to `engine_agents` in `workshop_subgraph.py`
3. Updating the unified spec with engine-specific templates

### Educational Content
Modify lesson plans in `academy_subgraph.py`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `hatch run test`
5. Submit a pull request

## 📝 License

This project is open source. See LICENSE file for details.

---

**Need Help?** Check the logs in the Replit console or open an issue on GitHub!
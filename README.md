# 🎮 AI Game Development Platform

## Revolutionary AI-Powered Game Development with OpenAI Agents

A next-generation platform that transforms game development through OpenAI's latest models (GPT-5 and GPT-Image-1), featuring real-time visualization, automated code generation, and educational integration through Chainlit UI.

### 🌟 **Core Features**

#### **🤖 OpenAI Agents Architecture**
- **Direct Function Calling**: Leverages OpenAI's native function tools
- **Latest Models**: GPT-5 for text/code, GPT-Image-1 for visuals
- **Simplified Stack**: No LangChain/LangGraph complexity
- **Real-Time Generation**: Stream responses as they're created

#### **🎓 Arcade Academy Mode**
- **Interactive Learning**: Educational RPG featuring Professor Pixel
- **Progressive Curriculum**: Learn programming through engaging gameplay
- **Achievement System**: Track progress and unlock new content
- **AI Mentorship**: Contextual help and guidance with teachable moments

#### **🚀 Game Workshop Mode**
- **Natural Language Input**: Describe your game in plain English
- **Multi-Engine Support**: Pygame, Godot, and Bevy with dedicated templates
- **Asset Generation**: Automatic sprite, sound, and music creation
- **Complete Projects**: Fully playable games with all required files

#### **🎨 Modern Interface**
- **Chainlit UI**: Clean, responsive interface with custom cyberpunk theme
- **WebSocket Updates**: Real-time progress as games are generated
- **Custom React Components**: Full control over UI/UX
- **Wizard-Style Flows**: Guided experience through game creation

---

## 🛠️ **Installation & Quick Start**

### **Prerequisites**
- Python 3.11+ 
- OpenAI API key (required for all generation features)

### **Setup**
```bash
# Clone the repository
git clone <repository-url>
cd ai-game-dev

# Install with hatch
pip install hatch
hatch env create

# Set up environment variables
export OPENAI_API_KEY="your-api-key-here"

# Start the platform
hatch run
# or
python -m ai_game_dev
```

Visit `http://localhost:8000` to access the Chainlit interface.

---

## 🎯 **Usage**

### **Starting the Platform**
```bash
# Production mode
hatch run server

# Development mode with auto-reload
hatch run dev

# Quick commands
just run      # Start platform
just test     # Run tests
just format   # Format code
just qa       # Quality assurance
```

### **In the Chainlit Interface**

1. **Choose Your Mode:**
   - Click "Game Workshop" to create custom games
   - Click "Arcade Academy" to learn programming

2. **Create a Game (Workshop Mode):**
   - Describe your game idea
   - Select target engine (Pygame/Godot/Bevy)
   - Watch as AI generates all assets and code
   - Download complete project

3. **Learn Programming (Academy Mode):**
   - Start with skill assessment
   - Follow guided tutorials
   - Complete challenges
   - Build your RPG game

---

## 🏗️ **Architecture**

### **Simplified Flow**
```
User Input → Chainlit → OpenAI Agent → Function Tools → Real-time Updates
```

### **Key Components**
- **chainlit_app.py**: Main application with wizard flows
- **agent.py**: Core OpenAI agent orchestrator
- **OpenAI Tools**: Specialized function tools
  - `image.py`: GPT-Image-1 integration for sprites/backgrounds
  - `audio.py`: TTS + music21 + Freesound for sound
  - `text.py`: GPT-5 for dialogue, quests, and code
  - `template_loader.py`: Jinja2 templates for engines
- **constants.py**: Centralized configuration

---

## 📁 **Project Structure**
```
ai-game-dev/
├── src/
│   └── ai_game_dev/
│       ├── __main__.py              # Entry point
│       ├── chainlit_app.py          # Main Chainlit application
│       ├── agent.py                 # OpenAI agent orchestrator
│       ├── constants.py             # Central configuration
│       ├── tools/
│       │   └── openai_tools/        # OpenAI function tools
│       │       ├── __init__.py
│       │       ├── image.py         # GPT-Image-1 integration
│       │       ├── audio.py         # Audio generation
│       │       ├── text.py          # Text/code generation
│       │       ├── template_loader.py
│       │       └── templates/       # Jinja2 templates
│       │           ├── pygame/
│       │           ├── godot/
│       │           ├── bevy/
│       │           └── academy/
│       └── startup_assets.py        # Asset generation on startup
├── public/                          # Web assets
│   ├── custom.html                  # Custom UI
│   ├── style.css                    # Cyberpunk theme
│   ├── chainlit-app.js             # Main frontend logic
│   └── components/                  # React components
│       ├── Workshop.js
│       └── Academy.js
├── .chainlit/                       # Chainlit configuration
│   └── config.toml
├── .cursor/                         # Cursor IDE config
│   └── prompts.md
├── .gemini/                         # Gemini Code Assist
│   └── config.yaml
├── .github/
│   └── copilot-instructions.md     # GitHub Copilot config
├── pyproject.toml                   # Project configuration
├── justfile                         # Task automation
└── README.md                        # This file
```

---

## 🧪 **Development**

### **Running Tests**
```bash
# Full test suite
hatch test

# Specific test categories
pytest -m unit          # Unit tests only
pytest -m integration   # Integration tests
pytest -m e2e          # End-to-end tests
```

### **Code Quality**
```bash
# Format code
hatch format

# Run linting
hatch run lint

# Security check
hatch run security

# Full QA
just qa
```

### **AI Assistant Configuration**
The project includes configurations for:
- **Cursor IDE** (`.cursor/prompts.md`)
- **Gemini Code Assist** (`.gemini/config.yaml`)
- **GitHub Copilot** (`.github/copilot-instructions.md`)

These ensure AI assistants understand the project structure and coding standards.

---

## 🚀 **Deployment**

### **Environment Variables**
```bash
# Required
OPENAI_API_KEY="your-openai-key"

# Optional
AI_GAME_DEV_PORT=8000          # Custom port
FREESOUND_API_KEY="..."        # For sound effects
```

### **Replit Deployment**
The project includes Replit configuration:
```bash
# Automatic on Replit
just run
```

---

## 🤝 **Contributing**

1. Fork the repository
2. Create a feature branch
3. Follow the coding standards in `.cursor/prompts.md`
4. Ensure tests pass with `just test`
5. Run `just qa` before submitting
6. Submit a pull request

### **Coding Standards**
- Use modern Python (3.11+) type hints: `str | None` instead of `Optional[str]`
- Absolute imports only: `from ai_game_dev.tools import ...`
- All imports at file top, no try/except around imports
- Follow the patterns in `constants.py` for configuration

---

## 📝 **Recent Changes**

### **Major Architecture Overhaul**
- ✅ Replaced LangChain/LangGraph with OpenAI agents
- ✅ Integrated GPT-5 and GPT-Image-1 models
- ✅ Simplified to direct function calling
- ✅ Added Jinja2 templates for engine-specific generation
- ✅ Centralized configuration in `constants.py`
- ✅ Added AI assistant configurations

### **Improvements**
- 🚀 3-5x faster generation with parallel API calls
- 🎨 Better image quality with GPT-Image-1
- 📝 Superior code generation with GPT-5
- 🔧 Simpler codebase without framework overhead
- 🎯 More maintainable with clear separation of concerns

---

## 📄 **License**

MIT License - see LICENSE file for details

---

## 🙏 **Acknowledgments**

- OpenAI team for GPT-5 and GPT-Image-1
- Chainlit team for the excellent UI platform
- Music21 project for music generation capabilities
- The open-source game development community

---

## 📞 **Support**

- GitHub Issues: Report bugs and request features
- Documentation: See `/docs` for detailed guides
- API Reference: Generated from docstrings

---

**Built with ❤️ using OpenAI Agents, Chainlit, and modern Python**
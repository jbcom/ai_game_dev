# 🎮 AI Game Development Platform

## Revolutionary AI-Powered Game Development with Chainlit

A next-generation platform that transforms game development through direct LangGraph subgraph orchestration, featuring real-time visualization, automated code generation, and educational integration.

### 🌟 **Core Features**

#### **🔗 Direct Subgraph Architecture**
- **No Orchestrator Overhead**: Chainlit directly manages LangGraph subgraphs
- **Real-Time Visualization**: Watch AI traverse through specialized subgraphs
- **Modular Design**: GraphicsSubgraph, AudioSubgraph, DialogueSubgraph, QuestSubgraph
- **Engine-Specific Agents**: Direct integration with Pygame, Godot, and Bevy

#### **🎓 Arcade Academy Mode**
- **Interactive Learning**: Educational RPG featuring Professor Pixel
- **Progressive Curriculum**: Learn programming through engaging gameplay
- **Achievement System**: Track progress and unlock new content
- **AI Mentorship**: Contextual help and guidance

#### **🚀 Game Workshop Mode**
- **Natural Language Input**: Describe your game in plain English
- **Multi-Engine Support**: Pygame, Godot, and Bevy
- **Asset Generation**: Automatic sprite, sound, and music creation
- **Complete Projects**: Fully playable games with all required files

#### **🎨 Modern Interface**
- **Chainlit UI**: Clean, responsive interface with custom cyberpunk theme
- **WebSocket Updates**: Real-time progress as games are generated
- **Custom CSS/JS**: Full control over appearance and behavior
- **No External Dependencies**: Pure Python, no Node.js required

---

## 🛠️ **Installation & Quick Start**

### **Prerequisites**
- Python 3.11+ 
- OpenAI API key (for asset generation)

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
python -m __main__
```

Visit `http://localhost:8000` to access the Chainlit interface.

---

## 🎯 **Usage**

### **Starting the Platform**
```bash
# Production mode
hatch run

# Development mode with auto-reload
just dev

# Quick commands
just start    # Start platform
just test     # Run tests
just format   # Format code
just qa       # Quality assurance
```

### **In the Chainlit Interface**

1. **Choose Your Mode:**
   ```
   workshop   # Enter Game Workshop
   academy    # Enter Arcade Academy
   ```

2. **Create a Game (Workshop Mode):**
   ```
   create a space shooter game
   create a puzzle platformer with pygame
   create a cyberpunk RPG with godot
   ```

3. **Learn Programming (Academy Mode):**
   ```
   start lesson
   continue
   progress
   ```

---

## 🏗️ **Architecture**

### **Simplified Flow**
```
User Input → Chainlit → Subgraph Selection → Direct Processing → Real-time Updates
```

### **Key Components**
- **chainlit_app.py**: Main application handling user interaction
- **Subgraphs**: Specialized processors for different aspects
  - GraphicsSubgraph: Image and sprite generation
  - AudioSubgraph: Sound and music creation
  - DialogueSubgraph: Conversation systems
  - QuestSubgraph: Game objectives and progression
- **Engine Agents**: Game-specific code generators
  - PygameAgent: 2D Python games
  - GodotAgent: GDScript projects
  - BevyAgent: Rust ECS games
- **ArcadeAcademyAgent**: Educational content and lessons

---

## 📁 **Project Structure**
```
ai-game-dev/
├── src/
│   └── ai_game_dev/
│       ├── chainlit_app.py          # Main Chainlit application
│       ├── agents/
│       │   ├── subgraphs/           # LangGraph subgraphs
│       │   │   ├── __init__.py
│       │   │   ├── graphics_subgraph.py
│       │   │   ├── audio_subgraph.py
│       │   │   ├── dialogue_subgraph.py
│       │   │   └── quest_subgraph.py
│       │   ├── pygame_agent.py      # Pygame code generator
│       │   ├── godot_agent.py       # Godot code generator
│       │   ├── bevy_agent.py        # Bevy code generator
│       │   └── arcade_academy_agent.py # Educational agent
│       └── project_manager.py       # Project management
├── .chainlit/                       # Chainlit configuration
│   └── config.toml
├── public/                          # Web assets
│   ├── style.css                    # Cyberpunk theme
│   └── readme.md                    # Welcome screen
├── __main__.py                      # Entry point
├── pyproject.toml                   # Project configuration
├── justfile                         # Task automation
└── README.md                        # This file
```

---

## 🧪 **Development**

### **Running Tests**
```bash
# Full test suite
just test

# Fast tests
just test-fast

# Test imports
just test-imports

# Test Chainlit startup
just test-chainlit
```

### **Code Quality**
```bash
# Format code
just format

# Run linting
just lint

# Security check
just security

# Full QA
just qa
```

### **Documentation**
```bash
# Build docs
just docs

# Serve docs
just docs-serve
```

---

## 🚀 **Deployment**

### **Validation**
```bash
# Check deployment readiness
just validate

# Create deployment package
just package
```

### **Environment Variables**
- `OPENAI_API_KEY`: Required for asset generation
- `ANTHROPIC_API_KEY`: Optional for Claude support
- `GOOGLE_API_KEY`: Optional for Gemini support

---

## 🤝 **Contributing**

1. Fork the repository
2. Create a feature branch
3. Run `just setup` to configure development environment
4. Make your changes
5. Run `just qa` to ensure quality
6. Submit a pull request

---

## 📝 **Recent Changes**

### **Architecture Overhaul**
- ✅ Removed `simple_server.py` - using unified server through main
- ✅ Removed master orchestrator layer - Chainlit manages directly
- ✅ Removed internal agent - subgraphs handle all generation
- ✅ Integrated Chainlit for modern UI with LangGraph visualization
- ✅ Updated all workflows and documentation

### **Improvements**
- 🚀 Faster response times without orchestrator overhead
- 🎨 Better UI/UX with Chainlit's built-in features
- 🔍 Real-time visibility into AI processing
- 📦 Simpler deployment with fewer components

---

## 📄 **License**

MIT License - see LICENSE file for details

---

## 🙏 **Acknowledgments**

- LangChain & LangGraph teams for the AI framework
- Chainlit team for the excellent UI platform
- OpenAI for GPT-4 and DALL-E integration
- The open-source game development community

---

## 📞 **Support**

- GitHub Issues: Report bugs and request features
- Documentation: See `/docs` for detailed guides
- Community: Join our Discord server (coming soon)

---

**Built with ❤️ using Chainlit, LangGraph, and AI**
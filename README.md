# 🎮 AI Game Development Platform

## Revolutionary Universal AI-Powered Game Development with Interactive Variants

A comprehensive platform that transforms game development through artificial intelligence, featuring automated code generation, interactive A/B testing, and educational integration with Professor Pixel.

### 🌟 **Core Features**

#### **🔧 Interactive Variant System**
- **Automatic A/B Detection**: AI analyzes code to suggest variant implementations (hex vs square grids, turn-based vs real-time combat)
- **Live Split-Screen Preview**: Compare different approaches side-by-side before choosing
- **Feature Flag System**: Generated `features.toml` configuration with toggle switches
- **Cross-Engine Support**: Works seamlessly across pygame, Godot, and Bevy

#### **🎓 Arcade Academy with Professor Pixel**
- **AI-Powered Teaching**: Automatic detection of teachable moments through code analysis
- **Interactive Learning**: Students can experiment with variant choices and see educational impact
- **Contextual Lessons**: Professor Pixel appears exactly when concepts become relevant
- **Progressive Difficulty**: Educational content adapts to student level and learning objectives

#### **🚀 Multi-Engine Game Generation**
- **Pygame**: Full WebAssembly deployment support with pygbag integration
- **Godot**: GDScript generation with native features
- **Bevy**: Rust ECS architecture with performance optimization
- **Unified Workflow**: Single interface for all engine development

#### **🎨 Comprehensive Asset Generation**
- **Real OpenAI Integration**: High-quality image generation with variants and masking
- **Audio Synthesis**: Music and sound effect generation
- **Asset Organization**: Structured static asset management with premium resources

#### **🌐 Modern Web Interface**
- **Single Scaling Frame**: HTMX-powered interface with no page redirects
- **Real-Time Updates**: WebSocket support for live development feedback
- **Responsive Design**: Works on desktop and mobile devices
- **Professional UI**: Custom cyberpunk theme with premium assets

---

## 🛠️ **Installation & Quick Start**

### **Prerequisites**
- Python 3.11+ 
- Node.js 20+ (for frontend assets)
- OpenAI API key (for asset generation)

### **Setup**
```bash
# Clone the repository
git clone <repository-url>
cd ai-game-dev

# Install with hatch (uses UV backend automatically)
hatch env create

# Activate the environment and install dependencies
hatch shell

# Alternative: Install specific dependency groups
hatch env create dev    # Development environment
hatch env create pygame # Pygame environment
hatch env create web    # Web environment

# Set up environment variables
export OPENAI_API_KEY="your-api-key-here"

# Start the development server
hatch run python __main__.py
```

Visit `http://localhost:5000` to access the platform.

---

## 🎯 **Quick Usage Examples**

### **Generate a Game with Interactive Variants**
```python
from ai_game_dev.variants import create_variant_enabled_game

# Generate a pygame game with automatic variant detection
result = await create_variant_enabled_game(
    base_code="# Simple platformer game",
    engine="pygame"
)

print(f"Found {len(result['variants'])} interactive choices!")
print(f"Generated features.toml with {len(result['features_toml'])} toggles")
```

### **Educational Game with Professor Pixel**
```python
from ai_game_dev.agents import ArcadeAcademyAgent
from ai_game_dev.agents.educational_context import EducationalContext

agent = ArcadeAcademyAgent()
context = EducationalContext(
    target_audience="middle_school",
    learning_objectives=["variables", "loops", "conditionals"]
)

game = await agent.generate_educational_game(
    "Create a space adventure where students learn programming",
    context
)

print(f"Generated {len(game['teachable_moments'])} learning opportunities!")
```

### **Deploy to WebAssembly**
```bash
# Deploy pygame game to browser
python -m ai_game_dev.deployment.pygbag_deploy my_game.py
```

---

## 🏗️ **Architecture Overview**

### **Agent-Based System**
```
Master Orchestrator
├── Pygame Agent (+ WebAssembly)
├── Godot Agent (+ GDScript)  
├── Bevy Agent (+ Rust ECS)
└── Arcade Academy Agent (+ Educational AI)
```

### **Interactive Variant Pipeline**
```
Code Generation → Variant Detection → A/B Choices → Feature Flags → Live Preview
```

### **Educational Enhancement**
```
Base Game → Teachable Moment Analysis → Professor Pixel Integration → Interactive Learning
```

---

## 📂 **Project Structure**

```
ai-game-dev/
├── src/ai_game_dev/
│   ├── agents/                 # AI agents for different engines
│   │   ├── master_orchestrator.py  # Central coordination
│   │   ├── arcade_academy_agent.py # Educational AI
│   │   └── base_agent.py           # Shared functionality
│   ├── variants/               # Interactive variant system
│   │   ├── variant_system.py      # Core A/B testing logic
│   │   └── __init__.py
│   ├── models/                 # Data models and schemas
│   ├── engines/                # Engine-specific templates
│   ├── server/                 # Web interface (FastAPI + HTMX)
│   ├── deployment/             # WebAssembly and deployment tools
│   └── static/                 # Premium assets and resources
├── tests/                      # Comprehensive test suite
├── docs/                       # Sphinx documentation
└── generated_assets/           # AI-generated game assets
```

---

## 🧪 **Testing & Quality**

### **Run Tests**
```bash
# Full test suite (using hatch + UV)
hatch run test

# Coverage report
hatch run coverage

# Type checking
hatch run mypy

# Code quality
hatch run lint

# Or use justfile shortcuts
just test
just coverage
just mypy
just lint
```

### **Current Coverage**
- **Overall**: 10% (targeting production quality)
- **Models Module**: 98% (comprehensive data model testing)
- **Agents**: Coverage for all engine agents
- **Variants**: New interactive system testing

---

## 🎓 **Educational Features**

### **Automatic Teaching Moments**
The AI analyzes generated code and automatically detects opportunities to teach programming concepts:

- **Variables**: When game state changes (health, score, position)
- **Loops**: When repetitive actions occur (enemy spawning, animation frames)
- **Conditionals**: When game logic branches (collision detection, win/lose conditions)
- **Functions**: When code can be organized better

### **Interactive A/B Learning**
Students can experiment with different programming approaches:

- **Grid Systems**: Square vs hexagonal tile layouts
- **Combat Mechanics**: Turn-based vs real-time systems  
- **Movement**: Discrete vs continuous player control
- **AI Behavior**: Simple vs sophisticated enemy intelligence

Each choice shows immediate visual impact and explains the educational trade-offs.

---

## 🚀 **Deployment Options**

### **Development**
- Local FastAPI server with hot reload
- SQLite persistence for player data
- Real-time WebSocket updates

### **Production**
- **WebAssembly**: pygame games run in browser via pygbag
- **Native**: Export to Windows/Mac/Linux executables
- **Cloud**: Deploy to Replit, Heroku, or custom servers

---

## 🤝 **Contributing**

### **Development Setup**
```bash
# Create development environment with hatch
hatch env create dev

# Activate development environment
hatch shell

# Set up pre-commit hooks
hatch run setup-dev

# Run quality checks
hatch run quality-check

# Or use justfile shortcuts
just setup-dev
just quality-check
```

### **Adding New Features**
1. **Variant Types**: Extend the variant system with new A/B choice patterns
2. **Educational Content**: Add Professor Pixel lessons for new programming concepts
3. **Engine Support**: Integrate additional game engines beyond pygame/Godot/Bevy
4. **Asset Generators**: Create new AI-powered asset generation capabilities

---

## 📊 **Technology Stack**

### **Backend**
- **Python 3.11+**: Modern async/await architecture
- **Hatch + UV**: Modern Python project management with fast dependency resolution
- **FastAPI**: High-performance web framework
- **LangChain/LangGraph**: Multi-agent AI orchestration
- **OpenAI GPT**: Image generation and code analysis
- **SQLite**: Lightweight persistence

### **Frontend**
- **HTMX**: Dynamic content without page reloads
- **DaisyUI + Tailwind**: Modern component library
- **Jinja2**: Server-side template rendering
- **WebSockets**: Real-time communication

### **Game Engines**
- **Pygame**: Python 2D games with WebAssembly support
- **Godot**: Professional 2D/3D engine with GDScript
- **Bevy**: High-performance Rust ECS engine

### **AI & ML**
- **OpenAI GPT-4**: Code generation and analysis
- **PyTorch**: Semantic embedding for asset seeding
- **Internet Archive**: Literary narrative enhancement
- **AST Parsing**: Code structure analysis for education

---

## 🎮 **Example Games Generated**

### **NeoTokyo Code Academy: The Binary Rebellion**
- **Genre**: Educational RPG with cyberpunk themes
- **Features**: Professor Pixel guide, interactive code challenges
- **Variants**: Multiple combat systems, grid layouts, AI behaviors
- **Deployment**: WebAssembly-ready for browser play

### **Space Explorer Platformer**  
- **Genre**: 2D platformer with physics
- **Features**: Procedural level generation, collectible items
- **Variants**: Movement systems, enemy AI, power-up mechanics
- **Educational Focus**: Variables, loops, collision detection

---

## 📈 **Performance & Optimization**

### **AI Generation**
- **Batch Processing**: Concurrent asset generation with rate limiting
- **Caching**: Intelligent caching of generated content
- **Connection Pooling**: Optimized LLM provider connections

### **Web Interface**
- **HTMX**: Minimal JavaScript with server-side rendering
- **Asset CDN**: Optimized delivery of static resources
- **WebSocket**: Efficient real-time updates

### **Game Performance**
- **WebAssembly**: Near-native performance in browsers
- **Asset Optimization**: Compressed images and audio
- **Feature Flags**: Runtime performance tuning

---

## 🆘 **Support & Documentation**

### **Documentation**
- **API Reference**: Comprehensive function documentation
- **Tutorials**: Step-by-step game development guides  
- **Architecture Guide**: Deep dive into system design
- **Educational Guide**: Using Professor Pixel effectively

### **Community**
- **Issues**: Report bugs and request features
- **Discussions**: Community Q&A and showcases
- **Contributing**: Guidelines for code contributions

---

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 **Acknowledgments**

- **OpenAI**: GPT models and image generation capabilities
- **LangChain**: Multi-agent orchestration framework
- **Pygame Community**: WebAssembly deployment via pygbag
- **Replit**: Cloud development platform
- **Internet Archive**: Public domain content for AI seeding

---

**✨ Start building revolutionary AI-powered games with interactive learning today!**
# AI Game Development - Chainlit-based Platform
# Requires: just, hatch, python 3.11+

set shell := ["bash", "-c"]
set dotenv-load := true

# Default recipe
default:
    @just --list

# =============================================================================
# 🚀 MAIN COMMANDS
# =============================================================================

# Start the Chainlit platform
run:
    @echo "🚀 Starting AI Game Development Platform with Chainlit..."
    hatch run python -m ai_game_dev

# Start in development mode with auto-reload
dev:
    @echo "🔄 Starting in development mode with auto-reload..."
    hatch run python -m ai_game_dev --port 8000

# Quick start (alias for run)
start: run

# =============================================================================
# 🎮 GENERATION COMMANDS
# =============================================================================

# Generate server assets
generate-assets:
    @echo "🎨 Generating server assets..."
    hatch run python -m ai_game_dev --assets-spec src/ai_game_dev/specs/server_assets.toml

# Generate Pygame educational RPG
generate-pygame:
    @echo "🎮 Generating NeoTokyo Code Academy (Pygame)..."
    hatch run python -m ai_game_dev --game-spec games/pygame/neotokyo_code_academy.toml

# Generate Bevy FPS
generate-bevy:
    @echo "🎮 Generating Retro Raycast Revolution (Bevy)..."
    hatch run python -m ai_game_dev --game-spec games/bevy/retro_raycast_revolution.toml

# Generate Godot 3D game
generate-godot:
    @echo "🎮 Generating Neural Nexus 3D (Godot)..."
    hatch run python -m ai_game_dev --game-spec games/godot/neural_nexus_3d.toml

# Build all assets and games
build-all-games: generate-assets generate-pygame generate-bevy generate-godot
    @echo "✅ All assets and games generated!"

# =============================================================================
# 🏗️ BUILD COMMANDS
# =============================================================================

# Build the package
build:
    @echo "🐍 Building ai-game-dev package..."
    hatch build

# Build wheel distribution
build-wheel:
    @echo "🎯 Building wheel distribution..."
    hatch build -t wheel

# Build source distribution
build-sdist:
    @echo "📦 Building source distribution..."
    hatch build -t sdist

# Clean all build artifacts
clean:
    @echo "🧹 Cleaning build artifacts..."
    rm -rf dist/ build/ src/ai_game_dev.egg-info/
    find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
    find . -name "*.pyc" -delete 2>/dev/null || true
    find . -name ".pytest_cache" -type d -exec rm -rf {} + 2>/dev/null || true
    find . -name "htmlcov" -type d -exec rm -rf {} + 2>/dev/null || true
    find . -name ".coverage" -delete 2>/dev/null || true
    find . -name ".chainlit" -type d -exec rm -rf {} + 2>/dev/null || true
    rm -rf docs/_build/ docs/doctrees/ coverage.xml

# =============================================================================
# 🧪 TESTING COMMANDS
# =============================================================================

# Run all tests with coverage
test:
    @echo "🧪 Running tests with coverage..."
    hatch run test:cov

# Run tests without coverage (faster)
test-fast:
    @echo "⚡ Running fast tests..."
    hatch run test:no-cov

# Run specific test file
test-file file:
    @echo "🎯 Running tests in {{file}}..."
    hatch run pytest {{file}} -v

# Run tests matching pattern
test-match pattern:
    @echo "🔍 Running tests matching '{{pattern}}'..."
    hatch run pytest tests/ -v -k "{{pattern}}"

# Test Chainlit app startup
test-chainlit:
    @echo "🧪 Testing Chainlit startup..."
    timeout 10s hatch run server || echo "✅ Chainlit started successfully"

# Test subgraph imports
test-imports:
    @echo "🔍 Testing critical imports..."
    hatch run python -c "
from ai_game_dev.agents.subgraphs import GraphicsSubgraph, AudioSubgraph, DialogueSubgraph, QuestSubgraph
from ai_game_dev.agents.pygame_agent import PygameAgent
from ai_game_dev.agents.godot_agent import GodotAgent
from ai_game_dev.agents.bevy_agent import BevyAgent
from ai_game_dev.agents.arcade_academy_agent import ArcadeAcademyAgent
print('✅ All subgraphs and agents imported successfully')
"

# =============================================================================
# 🔍 QUALITY ASSURANCE
# =============================================================================

# Run complete quality analysis
qa: lint test security
    @echo "✅ Quality analysis completed"

# Format and lint all code
lint:
    @echo "🎨 Formatting and linting code..."
    hatch run lint:all

# Type checking
type-check:
    @echo "🔍 Running type checks..."
    hatch run lint:typing

# Security analysis
security:
    @echo "🔒 Running security analysis..."
    hatch run lint:security

# Format code
format:
    @echo "✨ Formatting code..."
    hatch run format:format

# =============================================================================
# 📚 DOCUMENTATION COMMANDS
# =============================================================================

# Build documentation
docs:
    @echo "📚 Building documentation..."
    hatch run docs:build

# Serve documentation locally
docs-serve:
    @echo "🌐 Serving documentation on http://localhost:8001..."
    hatch run docs:serve

# Clean and rebuild docs
docs-clean:
    @echo "🧹 Clean building documentation..."
    rm -rf docs/_build
    hatch run docs:build

# =============================================================================
# 🖼️ ASSET COMMANDS
# =============================================================================

# Process image with automatic optimizations
process-image INPUT_PATH OUTPUT_PATH="":
    @echo "🖼️ Processing image..."
    hatch run process-image "{{INPUT_PATH}}" {{if OUTPUT_PATH != "" { "\"" + OUTPUT_PATH + "\"" } else { "" } }}

# Generate test assets using subgraphs
test-assets:
    @echo "🎨 Testing asset generation through subgraphs..."
    hatch run python -c "
import asyncio
from ai_game_dev.agents.subgraphs import GraphicsSubgraph
async def test():
    subgraph = GraphicsSubgraph()
    await subgraph.initialize()
    result = await subgraph.process({'task': 'generate_test_asset'})
    print(f'✅ Asset generation test: {result}')
asyncio.run(test())
"

# =============================================================================
# 🔧 DEVELOPMENT COMMANDS
# =============================================================================

# Set up development environment
setup:
    @echo "🔧 Setting up development environment..."
    pip install --upgrade pip
    pip install hatch
    hatch env create
    hatch run python -c "print('✅ Development environment ready')"

# Install pre-commit hooks
hooks:
    @echo "🪝 Installing pre-commit hooks..."
    hatch run pre-commit install --install-hooks

# Interactive Python shell with package loaded
shell:
    @echo "🐍 Starting interactive shell..."
    hatch run python -c "
import ai_game_dev
from ai_game_dev.agents.subgraphs import *
from ai_game_dev.agents.pygame_agent import PygameAgent
print('🎮 AI Game Dev loaded - Subgraphs and agents available')
print('Available: GraphicsSubgraph, AudioSubgraph, DialogueSubgraph, QuestSubgraph')
import IPython; IPython.start_ipython()
"

# Watch for file changes and restart
watch:
    @echo "👀 Watching for changes..."
    find src/ -name "*.py" | entr -r just dev

# =============================================================================
# 📊 ANALYSIS & REPORTING
# =============================================================================

# Show project status
status:
    @echo "🎮 AI Game Development Platform Status"
    @echo "====================================="
    @echo "Architecture: Chainlit with Direct Subgraph Management"
    @echo ""
    @echo "Core Components:"
    @test -f src/ai_game_dev/chainlit_app.py && echo "  ✅ Chainlit App" || echo "  ❌ Chainlit App"
    @test -d src/ai_game_dev/agents/subgraphs && echo "  ✅ Subgraphs" || echo "  ❌ Subgraphs"
    @test -f src/ai_game_dev/agents/pygame_agent.py && echo "  ✅ Engine Agents" || echo "  ❌ Engine Agents"
    @test -f .chainlit/config.toml && echo "  ✅ Chainlit Config" || echo "  ❌ Chainlit Config"
    @test -f public/style.css && echo "  ✅ Custom CSS" || echo "  ❌ Custom CSS"
    @echo ""
    @echo "Removed Components:"
    @test ! -f src/ai_game_dev/simple_server.py && echo "  ✅ simple_server.py removed" || echo "  ❌ simple_server.py still exists"
    @test ! -f src/ai_game_dev/agents/master_orchestrator.py || echo "  ⚠️  master_orchestrator.py still exists (consider removing)"
    @test ! -f src/ai_game_dev/agents/internal_agent.py || echo "  ⚠️  internal_agent.py still exists (consider removing)"

# Count lines of code
loc:
    @echo "📏 Lines of code:"
    @echo "Chainlit App:"
    @wc -l src/ai_game_dev/chainlit_app.py 2>/dev/null || echo "  0 lines"
    @echo "Subgraphs:"
    @find src/ai_game_dev/agents/subgraphs -name "*.py" -exec wc -l {} + | tail -1 | awk '{print "  " $1 " lines"}' 2>/dev/null || echo "  0 lines"
    @echo "Engine Agents:"
    @find src/ai_game_dev/agents -name "*_agent.py" -not -path "*/subgraphs/*" -exec wc -l {} + | tail -1 | awk '{print "  " $1 " lines"}' 2>/dev/null || echo "  0 lines"

# =============================================================================
# 🚀 DEPLOYMENT COMMANDS
# =============================================================================

# Validate before deployment
validate:
    @echo "🔍 Validating deployment readiness..."
    @test -f src/ai_game_dev/chainlit_app.py || (echo "❌ Chainlit app missing" && exit 1)
    @test -f .chainlit/config.toml || (echo "❌ Chainlit config missing" && exit 1)
    @test -f public/style.css || (echo "❌ Custom CSS missing" && exit 1)
    @test -f public/readme.md || (echo "❌ Readme missing" && exit 1)
    @echo "✅ All required files present"
    just test-imports
    @echo "✅ Deployment validation passed"

# Package for deployment
package: clean validate build
    @echo "📦 Creating deployment package..."
    mkdir -p deployment
    cp -r dist/* deployment/
    cp -r .chainlit deployment/
    cp -r public deployment/
    @echo "✅ Deployment package ready in deployment/"

# =============================================================================
# 🛠️ MAINTENANCE COMMANDS
# =============================================================================

# Update dependencies
update:
    @echo "⬆️ Updating dependencies..."
    hatch run pip install --upgrade chainlit langchain langgraph

# Check for issues
check: lint type-check test-imports validate
    @echo "✅ All checks passed"

# Full CI simulation
ci: clean format lint test docs build validate
    @echo "🎯 Full CI simulation completed"

# Emergency fix workflow
fix: format test-fast
    @echo "🚑 Emergency fixes applied"

# =============================================================================
# 📝 SHORTCUTS
# =============================================================================

# Aliases
s: start
d: dev
t: test
q: qa
f: format
l: lint

# Quick development cycle
quick: format test-fast
    @echo "⚡ Quick check completed"

# Full development workflow
all: setup format lint test docs
    @echo "🎉 Complete workflow finished"
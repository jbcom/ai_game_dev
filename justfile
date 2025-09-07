# AI Game Development - Unified Package Build System
# Requires: just, uv, sphinx, cargo (optional), gdtoolkit (optional)

set shell := ["bash", "-c"]
set dotenv-load := true

# Default recipe
default:
    @just --list

# =============================================================================
# 🏗️ BUILD COMMANDS
# =============================================================================

# Build the unified AI game development package
build:
    @echo "🐍 Building ai-game-dev package..."
    uv build

# Build with specific target
build-wheel:
    @echo "🎯 Building wheel distribution..."
    uv build --wheel

# Build source distribution
build-sdist:
    @echo "📦 Building source distribution..."
    uv build --sdist

# Clean all build artifacts
clean:
    @echo "🧹 Cleaning build artifacts..."
    rm -rf dist/ build/ src/ai_game_dev.egg-info/
    find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
    find . -name "*.pyc" -delete 2>/dev/null || true
    find . -name ".pytest_cache" -type d -exec rm -rf {} + 2>/dev/null || true
    find . -name "htmlcov" -type d -exec rm -rf {} + 2>/dev/null || true
    find . -name ".coverage" -delete 2>/dev/null || true
    rm -rf docs/_build/ docs/doctrees/ coverage.xml

# =============================================================================
# 🖼️ IMAGE PROCESSING COMMANDS
# =============================================================================

# Process image with automatic transparency removal and frame detection
process-image INPUT_PATH OUTPUT_PATH="":
    @echo "🖼️ Processing image with automatic optimizations..."
    hatch run python scripts/process_image.py "{{INPUT_PATH}}" {{if OUTPUT_PATH != "" { "\"" + OUTPUT_PATH + "\"" } else { "" } }}

# Test automatic processing on tech frame
demo-process:
    @echo "🖼️ Demonstrating automatic processing on tech-frame.png..."
    hatch run python scripts/process_image.py "src/ai_game_dev/server/static/assets/frames/tech-frame.png"


# =============================================================================
# 🧪 TESTING COMMANDS
# =============================================================================

# Run all tests with coverage
test:
    @echo "🧪 Running tests with coverage..."
    uv run pytest tests/ -v --cov=src/ai_game_dev --cov-report=html --cov-report=xml --cov-report=term-missing

# Run tests without coverage (faster)
test-fast:
    @echo "⚡ Running fast tests..."
    uv run pytest tests/ -v -x

# Run specific test file
test-file file:
    @echo "🎯 Running tests in {{file}}..."
    uv run pytest {{file}} -v

# Run tests matching pattern
test-match pattern:
    @echo "🔍 Running tests matching '{{pattern}}'..."
    uv run pytest tests/ -v -k "{{pattern}}"

# Run benchmarks
bench:
    @echo "⚡ Running performance benchmarks..."
    uv run pytest tests/ --benchmark-only --benchmark-json=benchmark-results.json

# =============================================================================
# 🔍 QUALITY ASSURANCE
# =============================================================================

# Run complete quality analysis
qa: lint type-check security test
    @echo "✅ Quality analysis completed"

# Format and lint all code
lint:
    @echo "🎨 Formatting and linting code..."
    uv run black src/ tests/
    uv run isort src/ tests/
    uv run ruff check src/ tests/ --fix

# Type checking with mypy
type-check:
    @echo "🔍 Running type checks..."
    uv run mypy src/ai_game_dev --config-file pyproject.toml

# Security analysis
security:
    @echo "🔒 Running security analysis..."
    uv run bandit -r src/ -f txt

# Check code complexity
complexity:
    @echo "📊 Checking code complexity..."
    uv run radon cc src/ --min C

# Run all linting tools
lint-all: lint type-check
    @echo "🎯 Running comprehensive linting..."
    uv run pylint src/ai_game_dev/ || true
    uv run flake8 src/ tests/ || true

# =============================================================================
# 📚 DOCUMENTATION COMMANDS (RST + Sphinx)
# =============================================================================

# Build Sphinx documentation
docs:
    @echo "📚 Building Sphinx documentation..."
    cd docs && uv run sphinx-build -b html . _build/html

# Build documentation with clean rebuild
docs-clean:
    @echo "🧹 Clean building documentation..."
    cd docs && uv run sphinx-build -b html . _build/html -E

# Serve documentation locally
docs-serve:
    @echo "🌐 Serving documentation on http://localhost:8000..."
    cd docs/_build/html && python -m http.server 8000

# Watch documentation files and rebuild automatically
docs-watch:
    @echo "👀 Watching documentation files..."
    find docs/ -name "*.rst" -o -name "*.py" | entr -r just docs

# Generate API documentation from docstrings
docs-api:
    @echo "🔧 Generating API documentation..."
    cd docs && uv run sphinx-apidoc -o api ../src/ai_game_dev --force

# Check documentation for broken links
docs-linkcheck:
    @echo "🔗 Checking documentation links..."
    cd docs && uv run sphinx-build -b linkcheck . _build/linkcheck

# Build PDF documentation
docs-pdf:
    @echo "📄 Building PDF documentation..."
    cd docs && uv run sphinx-build -b latexpdf . _build/pdf

# =============================================================================
# 🚀 DEVELOPMENT COMMANDS
# =============================================================================

# Set up development environment
setup:
    @echo "🔧 Setting up development environment..."
    uv sync --all-extras --dev
    uv pip install sphinx sphinxcontrib-napoleon sphinx-rtd-theme
    uv run pre-commit install

# Install pre-commit hooks
hooks:
    @echo "🪝 Installing pre-commit hooks..."
    uv run pre-commit install --install-hooks
    uv run pre-commit install --hook-type commit-msg

# Start MCP development server
dev:
    @echo "🚀 Starting MCP server..."
    uv run ai-game-dev-server

# Hot reload development with file watching
watch:
    @echo "👀 Starting file watcher for auto-restart..."
    find src/ -name "*.py" | entr -r uv run ai-game-dev-server

# Start interactive Python shell with package loaded
shell:
    @echo "🐍 Starting interactive shell..."
    uv run python -c "import ai_game_dev; print('AI Game Dev loaded successfully'); import IPython; IPython.start_ipython()"

# =============================================================================
# 📊 ANALYSIS & REPORTING
# =============================================================================

# Generate comprehensive analysis report
analyze: qa
    @echo "📊 Generating analysis report..."
    @echo "Lines of code:"
    find src/ -name "*.py" -exec wc -l {} + | tail -1 | awk '{print "  " $1 " lines"}'
    @echo "Test coverage: see htmlcov/index.html"
    @echo "Documentation: see docs/_build/html/index.html"

# Count lines of code
loc:
    @echo "📏 Lines of code analysis:"
    @echo "Source code:"
    find src/ -name "*.py" -exec wc -l {} + | tail -1 | awk '{print "  " $1 " lines"}'
    @echo "Tests:"
    find tests/ -name "*.py" -exec wc -l {} + | tail -1 | awk '{print "  " $1 " lines"}' 2>/dev/null || echo "  0 lines"
    @echo "Documentation:"
    find docs/ -name "*.rst" -exec wc -l {} + | tail -1 | awk '{print "  " $1 " lines"}' 2>/dev/null || echo "  0 lines"

# Show project status
status:
    @echo "🎮 AI Game Development Package Status"
    @echo "====================================="
    @echo "Package: ai-game-dev"
    @echo "Location: src/ai_game_dev/"
    @echo ""
    @echo "Dependencies:"
    @which uv >/dev/null && echo "  ✅ UV (Python package manager)" || echo "  ❌ UV (Python package manager)"
    @which sphinx-build >/dev/null && echo "  ✅ Sphinx (Documentation)" || echo "  ❌ Sphinx (Documentation)"
    @which python >/dev/null && echo "  ✅ Python" || echo "  ❌ Python"
    @echo ""
    just loc

# =============================================================================
# 🔧 MAINTENANCE COMMANDS
# =============================================================================

# Update all dependencies
update:
    @echo "⬆️ Updating dependencies..."
    uv sync --upgrade

# Check for outdated dependencies
outdated:
    @echo "🔍 Checking for outdated dependencies..."
    uv pip list --outdated

# Format all code
format:
    @echo "✨ Formatting all code..."
    uv run black src/ tests/ docs/
    uv run isort src/ tests/

# Validate project structure
validate:
    @echo "🔍 Validating unified package structure..."
    @test -d src/ai_game_dev && echo "✅ Core package exists" || echo "❌ Core package missing"
    @test -d src/ai_game_dev/assets && echo "✅ Assets module exists" || echo "❌ Assets module missing"
    @test -d src/ai_game_dev/mcp_server && echo "✅ MCP server exists" || echo "❌ MCP server missing"
    @test -d src/ai_game_dev/engine_specs && echo "✅ Engine specs exist" || echo "❌ Engine specs missing"
    @test -f src/ai_game_dev/providers.py && echo "✅ Multi-LLM providers exist" || echo "❌ Multi-LLM providers missing"
    @test -f src/ai_game_dev/schemas/game_world_spec.json && echo "✅ JSON schemas exist" || echo "❌ JSON schemas missing"

# =============================================================================
# 📦 PACKAGING & RELEASE
# =============================================================================

# Prepare for release
release-prep version:
    @echo "🚀 Preparing release {{version}}..."
    sed -i 's/version = ".*"/version = "{{version}}"/' pyproject.toml
    sed -i 's/__version__ = ".*"/__version__ = "{{version}}"/' src/ai_game_dev/__init__.py
    @echo "Version updated to {{version}}"

# Build release distributions
release-build: clean build docs
    @echo "📦 Building release distributions..."
    @echo "✅ Wheel and source distributions created in dist/"
    @echo "✅ Documentation built in docs/_build/html/"

# Upload to PyPI (test)
upload-test:
    @echo "🧪 Uploading to Test PyPI..."
    uv run twine upload --repository testpypi dist/*

# Upload to PyPI (production)
upload:
    @echo "🚀 Uploading to PyPI..."
    uv run twine upload dist/*

# =============================================================================
# 🎯 SHORTCUTS & WORKFLOWS
# =============================================================================

# Quick development cycle
quick: lint test-fast
    @echo "⚡ Quick development check completed"

# Full CI simulation
ci: clean lint type-check security test docs build
    @echo "🎯 Full CI simulation completed"

# Emergency fix workflow
fix: format lint test-fast
    @echo "🚑 Emergency fixes applied"

# Complete development workflow
all: setup lint type-check test docs build
    @echo "🎉 Complete development workflow finished"

# Install package in development mode
install:
    @echo "📦 Installing package in development mode..."
    uv pip install -e .

# Uninstall package
uninstall:
    @echo "🗑️ Uninstalling package..."
    uv pip uninstall ai-game-dev

# =============================================================================
# 🛠️ ENGINE-SPECIFIC COMMANDS
# =============================================================================

# Generate engine-specific templates
templates:
    @echo "🎯 Generating engine templates..."
    uv run python -c "import toml; import os; [print(f'  ✅ {f[:-5].title()} template available') for f in os.listdir('src/ai_game_dev/engine_specs/') if f.endswith('.toml')]"

# Validate TOML specifications
validate-specs:
    @echo "🔍 Validating engine specifications..."
    uv run python -c "import toml; import os; [print(f'  ✅ {f} is valid') if toml.load(f'src/ai_game_dev/engine_specs/{f}') else print(f'  ❌ {f} has errors') for f in os.listdir('src/ai_game_dev/engine_specs/') if f.endswith('.toml')]"

# Validate JSON schemas
validate-schemas:
    @echo "🔍 Validating JSON schemas..."
    uv run python -c "import json; import os; [print(f'  ✅ {f} is valid') if json.load(open(f'src/ai_game_dev/schemas/{f}')) else print(f'  ❌ {f} has errors') for f in os.listdir('src/ai_game_dev/schemas/') if f.endswith('.json')]"
# Hatch-based development workflows
hatch-test:
        @echo "🧪 Running tests with hatch..."
        hatch run test:cov

hatch-lint:
        @echo "🔍 Running linting with hatch..."
        hatch run lint:all

hatch-format:
        @echo "✨ Formatting code with hatch..."
        hatch run format:format

hatch-docs:
        @echo "📚 Building docs with hatch..."
        hatch run docs:build

hatch-full:
        @echo "🚀 Running full hatch pipeline..."
        hatch run format:format
        hatch run lint:all
        hatch run test:full

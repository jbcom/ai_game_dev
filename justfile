# AI Game Development Ecosystem - Cross-Language Build System
# Requires: just, uv, cargo, gdtoolkit

set shell := ["bash", "-c"]
set dotenv-load := true

# Default recipe
default:
    @just --list

# =============================================================================
# 🏗️ BUILD COMMANDS
# =============================================================================

# Build all packages across all languages
build-all: build-python build-rust build-godot
    @echo "✅ All packages built successfully"

# Build Python packages
build-python:
    @echo "🐍 Building Python packages..."
    uv build packages/ai_game_dev/
    uv build packages/ai_game_assets/
    uv build packages/pygame_game_dev/
    uv build packages/arcade_game_dev/
    uv build packages/mcp_server/

# Build Rust packages
build-rust:
    @echo "🦀 Building Rust packages..."
    cd packages/bevy_game_dev && cargo build --release

# Build Godot plugin
build-godot:
    @echo "🎮 Building Godot plugin..."
    cd packages/godot_game_dev && zip -r godot-ai-game-dev.zip . -x "*.git*" "*.md" "target/*"

# Clean all build artifacts
clean:
    @echo "🧹 Cleaning build artifacts..."
    find . -name "dist" -type d -exec rm -rf {} + 2>/dev/null || true
    find . -name "target" -type d -exec rm -rf {} + 2>/dev/null || true
    find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
    find . -name "*.pyc" -delete 2>/dev/null || true
    find . -name ".pytest_cache" -type d -exec rm -rf {} + 2>/dev/null || true
    find . -name "htmlcov" -type d -exec rm -rf {} + 2>/dev/null || true
    rm -f *.zip coverage.xml .coverage 2>/dev/null || true

# =============================================================================
# 🧪 TESTING COMMANDS
# =============================================================================

# Run all tests across all languages
test-all: test-python test-rust test-godot
    @echo "✅ All tests completed"

# Run Python tests with coverage
test-python:
    @echo "🐍 Running Python tests..."
    uv run pytest tests/ -v --cov=packages --cov-report=html --cov-report=xml --cov-report=term-missing

# Run Rust tests
test-rust:
    @echo "🦀 Running Rust tests..."
    cd packages/bevy_game_dev && cargo test --all-features

# Run GDScript tests (validation)
test-godot:
    @echo "🎮 Running GDScript validation..."
    gdlint packages/godot_game_dev/ || true

# Run benchmarks
bench:
    @echo "⚡ Running performance benchmarks..."
    cd packages/bevy_game_dev && cargo bench
    uv run pytest tests/ --benchmark-only --benchmark-json=benchmark-results.json || true

# =============================================================================
# 🔍 QUALITY ASSURANCE
# =============================================================================

# Run complete quality analysis
qa: lint security coverage
    @echo "📊 Generating quality report..."
    python .github/scripts/generate_quality_report.py

# Run all linting across languages
lint: lint-python lint-rust lint-godot
    @echo "✅ All linting completed"

# Lint Python code
lint-python:
    @echo "🐍 Linting Python code..."
    uv run ruff check packages/ --fix
    uv run black packages/
    uv run isort packages/
    uv run mypy packages/ --config-file pyproject.toml || true
    uv run pylint packages/ || true

# Lint Rust code
lint-rust:
    @echo "🦀 Linting Rust code..."
    cd packages/bevy_game_dev && cargo fmt --all
    cd packages/bevy_game_dev && cargo clippy --all-targets --all-features -- -D warnings

# Lint GDScript code
lint-godot:
    @echo "🎮 Linting GDScript code..."
    gdformat packages/godot_game_dev/ || true
    gdlint packages/godot_game_dev/ || true

# Run security analysis
security:
    @echo "🔒 Running security analysis..."
    uv run bandit -r packages/ -f txt || true

# Generate code coverage reports
coverage:
    @echo "📈 Generating coverage reports..."
    uv run pytest tests/ --cov=packages --cov-report=html --cov-report=xml
    cd packages/bevy_game_dev && cargo tarpaulin --out xml --output-dir ../../ || true

# =============================================================================
# 📦 PACKAGING & DISTRIBUTION
# =============================================================================

# Package all distributions
package-all: package-python package-rust package-godot
    @echo "📦 All packages created"

# Package Python distributions
package-python: build-python
    @echo "🐍 Packaging Python distributions..."
    mkdir -p dist/python/
    cp packages/*/dist/* dist/python/ 2>/dev/null || true

# Package Rust distribution
package-rust: build-rust
    @echo "🦀 Packaging Rust distribution..."
    mkdir -p dist/rust/
    cd packages/bevy_game_dev && cargo package
    cp packages/bevy_game_dev/target/package/*.crate dist/rust/ 2>/dev/null || true

# Package Godot plugin
package-godot: build-godot
    @echo "🎮 Packaging Godot plugin..."
    mkdir -p dist/godot/
    cp packages/godot_game_dev/*.zip dist/godot/ 2>/dev/null || true

# =============================================================================
# 🚀 DEVELOPMENT COMMANDS
# =============================================================================

# Set up development environment
setup:
    @echo "🔧 Setting up development environment..."
    curl -LsSf https://astral.sh/uv/install.sh | sh || true
    uv sync --all-extras --dev
    pip install gdtoolkit==4.2.2 || true
    rustup update || true
    rustup component add rustfmt clippy || true

# Install pre-commit hooks
hooks:
    @echo "🪝 Installing pre-commit hooks..."
    uv run pre-commit install
    uv run pre-commit install --hook-type commit-msg

# Start development server (MCP)
dev:
    @echo "🚀 Starting development MCP server..."
    cd packages/mcp_server && uv run python main.py

# Hot reload development with file watching
watch:
    @echo "👀 Starting file watcher..."
    find packages/ -name "*.py" -o -name "*.rs" -o -name "*.gd" | entr -r just dev

# =============================================================================
# 📊 ANALYSIS & REPORTING
# =============================================================================

# Generate comprehensive analysis report
analyze:
    @echo "📊 Running comprehensive analysis..."
    just qa
    @echo "📈 Analysis complete. Check quality-report.html"

# Count lines of code across languages
loc:
    @echo "📏 Lines of code analysis:"
    @echo "Python:"
    find packages/ -name "*.py" -exec wc -l {} + | tail -1 | awk '{print "  " $1 " lines"}'
    @echo "Rust:"
    find packages/ -name "*.rs" -exec wc -l {} + | tail -1 | awk '{print "  " $1 " lines"}' 2>/dev/null || echo "  0 lines"
    @echo "GDScript:"
    find packages/ -name "*.gd" -exec wc -l {} + | tail -1 | awk '{print "  " $1 " lines"}' 2>/dev/null || echo "  0 lines"

# Show project status
status:
    @echo "🎮 AI Game Development Ecosystem Status"
    @echo "========================================"
    @echo "Packages:"
    @ls -1 packages/ | sed 's/^/  /'
    @echo ""
    @echo "Dependencies:"
    @which uv >/dev/null && echo "  ✅ UV (Python)" || echo "  ❌ UV (Python)"
    @which cargo >/dev/null && echo "  ✅ Cargo (Rust)" || echo "  ❌ Cargo (Rust)"
    @which gdformat >/dev/null && echo "  ✅ GDToolkit (GDScript)" || echo "  ❌ GDToolkit (GDScript)"
    @echo ""
    just loc

# =============================================================================
# 🔧 MAINTENANCE COMMANDS
# =============================================================================

# Update all dependencies
update:
    @echo "⬆️ Updating dependencies..."
    uv sync --upgrade
    cd packages/bevy_game_dev && cargo update

# Check for outdated dependencies
outdated:
    @echo "🔍 Checking for outdated dependencies..."
    uv pip list --outdated || true
    cd packages/bevy_game_dev && cargo outdated || echo "Install cargo-outdated for Rust dependency checking"

# Format all code
format: lint-python lint-rust lint-godot
    @echo "✨ All code formatted"

# Validate project structure
validate:
    @echo "🔍 Validating project structure..."
    @test -d packages/ai_game_dev && echo "✅ ai_game_dev package exists" || echo "❌ ai_game_dev package missing"
    @test -d packages/ai_game_assets && echo "✅ ai_game_assets package exists" || echo "❌ ai_game_assets package missing"
    @test -d packages/bevy_game_dev && echo "✅ bevy_game_dev package exists" || echo "❌ bevy_game_dev package missing"
    @test -d packages/godot_game_dev && echo "✅ godot_game_dev package exists" || echo "❌ godot_game_dev package missing"
    @test -d packages/pygame_game_dev && echo "✅ pygame_game_dev package exists" || echo "❌ pygame_game_dev package missing"
    @test -d packages/arcade_game_dev && echo "✅ arcade_game_dev package exists" || echo "❌ arcade_game_dev package missing"
    @test -d packages/mcp_server && echo "✅ mcp_server package exists" || echo "❌ mcp_server package missing"

# =============================================================================
# 🚀 RELEASE COMMANDS
# =============================================================================

# Prepare release (version bump, changelog, etc.)
release-prep version:
    @echo "🚀 Preparing release {{version}}..."
    @echo "Updating version in all packages..."
    sed -i 's/version = ".*"/version = "{{version}}"/' packages/*/pyproject.toml
    sed -i 's/version = ".*"/version = "{{version}}"/' packages/bevy_game_dev/Cargo.toml
    sed -i 's/"version": ".*"/"version": "{{version}}"/' packages/godot_game_dev/plugin.cfg

# Create release artifacts
release-build: clean package-all
    @echo "📦 Creating release artifacts..."
    tar -czf ai-game-dev-ecosystem-$(date +%Y%m%d).tar.gz dist/
    @echo "✅ Release artifacts created"

# =============================================================================
# 📚 DOCUMENTATION
# =============================================================================

# Generate documentation
docs:
    @echo "📚 Generating documentation..."
    cd packages/bevy_game_dev && cargo doc --no-deps --open || true

# Serve documentation locally
docs-serve:
    @echo "🌐 Serving documentation..."
    python -m http.server 8000 -d packages/bevy_game_dev/target/doc/ || true

# =============================================================================
# 🎯 SHORTCUTS
# =============================================================================

# Quick development cycle
quick: lint-python test-python
    @echo "⚡ Quick development check completed"

# Full CI simulation
ci: clean setup lint test-all security coverage package-all
    @echo "🎯 Full CI simulation completed"

# Emergency fix workflow
fix: format lint test-python
    @echo "🚑 Emergency fixes applied"
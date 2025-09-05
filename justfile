# AI Game Dev - Multi-language Monorepo Build System
# Manages Python, Rust, Go, Node.js, and C++ bindings

# Default recipe
default:
    @just --list

# Core library builds
build-core:
    @echo "🔧 Building core AI Game Dev library..."
    cd core/ai-game-dev && cargo build --release
    cd core/ai-game-dev && python -m pip install -e .

# Language-specific builds
build-rust:
    @echo "🦀 Building Rust packages..."
    cd rust/bevy_game_dev && cargo build --release
    cd rust/godot_game_dev && cargo build --release

build-go:
    @echo "🐹 Building Go bindings..."
    cd go/ai-game-dev && go build -buildmode=c-shared -o ../lib/libai_game_dev.so .
    cd go/ai-game-dev && go mod tidy

build-node:
    @echo "📦 Building Node.js bindings..."
    cd nodejs/ai-game-dev && npm install
    cd nodejs/ai-game-dev && npm run build
    cd nodejs/ai-game-dev && node-gyp rebuild

build-python:
    @echo "🐍 Building Python packages..."
    cd python/pygame_game_dev && pip install -e .
    cd python/arcade_game_dev && pip install -e .

build-cpp:
    @echo "⚡ Building C++ bindings..."
    cd cpp/ai-game-dev && mkdir -p build && cd build
    cd cpp/ai-game-dev/build && cmake .. && make -j$(nproc)

# Build everything
build-all: build-core build-rust build-go build-node build-python build-cpp
    @echo "✅ All language bindings built successfully!"

# Testing
test-core:
    cd core/ai-game-dev && cargo test && python -m pytest

test-rust:
    cd rust/bevy_game_dev && cargo test
    cd rust/godot_game_dev && cargo test

test-go:
    cd go/ai-game-dev && go test -v ./...

test-node:
    cd nodejs/ai-game-dev && npm test

test-python:
    cd python/pygame_game_dev && python -m pytest
    cd python/arcade_game_dev && python -m pytest

test-all: test-core test-rust test-go test-node test-python
    @echo "✅ All tests passed!"

# Examples and demos
demo-rust:
    cd rust/bevy_game_dev && cargo run --example ai_generated_rts

demo-go:
    cd go/ai-game-dev/examples && go run main.go

demo-node:
    cd nodejs/ai-game-dev && npm run demo

demo-python:
    cd python/pygame_game_dev && python -m pygame_game_dev.examples.platformer
    cd python/arcade_game_dev && python -m arcade_game_dev.examples.educational

# Distribution and packaging
package-rust:
    cd rust/bevy_game_dev && cargo package
    cd rust/godot_game_dev && cargo package

package-go:
    cd go/ai-game-dev && go mod vendor

package-node:
    cd nodejs/ai-game-dev && npm pack

package-python:
    cd python/pygame_game_dev && python -m build
    cd python/arcade_game_dev && python -m build

package-all: package-rust package-go package-node package-python
    @echo "📦 All packages created!"

# Publish to registries
publish-rust: package-rust
    cd rust/bevy_game_dev && cargo publish
    cd rust/godot_game_dev && cargo publish

publish-go: package-go
    cd go/ai-game-dev && git tag v1.0.0 && git push --tags

publish-node: package-node
    cd nodejs/ai-game-dev && npm publish

publish-python: package-python
    cd python/pygame_game_dev && twine upload dist/*
    cd python/arcade_game_dev && twine upload dist/*

# Development setup
setup-dev:
    @echo "🛠️ Setting up development environment..."
    # Install Rust
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
    # Install Node.js dependencies globally
    npm install -g node-gyp
    # Install Python build tools
    pip install build twine pytest
    # Install Go dependencies
    go install golang.org/x/tools/cmd/goimports@latest

# Clean builds
clean:
    @echo "🧹 Cleaning build artifacts..."
    find . -name "target" -type d -exec rm -rf {} + 2>/dev/null || true
    find . -name "node_modules" -type d -exec rm -rf {} + 2>/dev/null || true
    find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
    find . -name "*.pyc" -delete 2>/dev/null || true
    find . -name "build" -type d -exec rm -rf {} + 2>/dev/null || true
    find . -name "dist" -type d -exec rm -rf {} + 2>/dev/null || true

# Documentation generation
docs:
    @echo "📚 Generating documentation..."
    cd rust/bevy_game_dev && cargo doc --no-deps
    cd go/ai-game-dev && godoc -http=:6060 &
    cd nodejs/ai-game-dev && npm run docs
    cd python/pygame_game_dev && sphinx-build -b html docs docs/_build
    cd python/arcade_game_dev && sphinx-build -b html docs docs/_build

# Performance benchmarks
bench-rust:
    cd rust/bevy_game_dev && cargo bench

bench-go:
    cd go/ai-game-dev && go test -bench=.

bench-node:
    cd nodejs/ai-game-dev && npm run benchmark

bench-all: bench-rust bench-go bench-node
    @echo "⚡ All benchmarks completed!"

# Security audits
audit-rust:
    cd rust/bevy_game_dev && cargo audit
    cd rust/godot_game_dev && cargo audit

audit-node:
    cd nodejs/ai-game-dev && npm audit

audit-go:
    cd go/ai-game-dev && govulncheck ./...

audit-all: audit-rust audit-node audit-go
    @echo "🔒 Security audits completed!"

# Continuous integration helpers
ci-build: build-all test-all
    @echo "🚀 CI build completed successfully!"

ci-package: package-all
    @echo "📦 CI packaging completed!"

# Development workflows
dev-rust:
    cd rust/bevy_game_dev && cargo watch -x "run --example ai_generated_rts"

dev-go:
    cd go/ai-game-dev && find . -name "*.go" | entr -r go run examples/main.go

dev-node:
    cd nodejs/ai-game-dev && npm run dev

dev-python:
    cd python/pygame_game_dev && python -m pygame_game_dev.dev_server

# Repository management
init-submodules:
    git submodule update --init --recursive

update-deps:
    @echo "📦 Updating all dependencies..."
    cd rust/bevy_game_dev && cargo update
    cd go/ai-game-dev && go get -u ./...
    cd nodejs/ai-game-dev && npm update
    cd python/pygame_game_dev && pip-compile --upgrade requirements.in
    cd python/arcade_game_dev && pip-compile --upgrade requirements.in

# Release management
release VERSION:
    @echo "🚀 Creating release {{VERSION}}..."
    git tag v{{VERSION}}
    just package-all
    git push --tags
    @echo "Release v{{VERSION}} created!"

# Matrix build for different platforms
build-matrix:
    @echo "🏗️ Building for multiple platforms..."
    # Linux
    just build-all
    # Additional platform builds would go here
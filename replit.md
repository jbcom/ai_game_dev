# replit.md

## Overview

This is a revolutionary unified AI-powered game development library that provides comprehensive tools for creating games using artificial intelligence. The system is now consolidated into a single Python package (`ai-game-dev`) with multi-LLM provider support, comprehensive asset generation, and engine-specific TOML specifications.

**Production Status**: Fully operational with complete Typer CLI interface, real-time web generation system, project management, code preview/editing, testing integration, and deployment capabilities.

## User Preferences

Preferred communication style: Simple, everyday language.

## Recent Changes

**September 6, 2025**: Completed revolutionary agent-based asset generation system with real OpenAI integration and comprehensive master orchestrator:

- **Master Orchestrator Architecture**: Created comprehensive MasterGameDevOrchestrator with routing logic, spec generation subgraphs, and human-in-the-loop review workflows
- **Multi-Engine Support**: Built specialized agents for Pygame, Godot (GDScript), and Bevy (Rust ECS) with engine-specific instructions and capabilities
- **Intelligent Routing**: Implemented automatic engine detection and routing based on game specifications or natural language prompts
- **Real Seeding System**: Production-ready seeding with PyTorch embeddings, Internet Archive integration, and literary narrative enhancement
- **Spec Generation Pipeline**: Converts natural language descriptions into structured game specifications with thematic analysis
- **InternalAssetAgent**: Production-ready agent that coordinates all static asset generation using real OpenAI GPT Image generation
- **Real Asset Generation**: Eliminated all placeholder functions - now uses actual OpenAI GPT Image generation with variants, masked edits, and batch processing
- **Internal CLI Integration**: Updated all internal CLI commands to use the agent architecture with master orchestrator coordination
- **Production Quality**: Full async/await architecture with proper error handling, resource management, and concurrency control

**Asset Generation Capabilities**:
- OpenAI GPT Image integration for high-quality image generation
- Image variants and masked editing for asset refinement
- Batch processing with rate limiting and concurrent execution
- Cyberpunk-themed asset generation for educational game
- Platform UI element generation for web interface

**Educational Game Pipeline**: Complete agent-driven pipeline for generating "NeoTokyo Code Academy: The Binary Rebellion" with Professor Pixel as cyberpunk guide, including character sprites, environment tilesets, and educational UI elements.

**Master Orchestrator Features**: Complete routing system with spec generation, seeding coordination, engine-specific subgraphs, and human review workflows for production-quality game development across multiple engines.

## Unified Architecture

### Single Package Structure

**Consolidated Package**: All functionality unified under `src/ai_game_dev/` with modular subdirectories for assets, MCP server, and engine specifications.

**Multi-LLM Provider Support**: Unified provider system supporting OpenAI, Anthropic Claude, Google Gemini, and local LLMs via Ollama with automatic fallback capabilities.

**Engine-Specific TOML Templates**: Comprehensive engine specifications with metaprompts for Pygame, Bevy, Godot, and Arcade. Each template includes code generation patterns, asset integration guides, and optimization strategies.

**JSON Schema Integration**: Structured game world specifications enabling AI tools to understand exactly what to generate, including metadata, gameplay mechanics, asset requirements, and narrative elements.

### Core Components

**LangChain/LangGraph Orchestration**: Pure multi-agent workflows for intelligent game generation with support for multiple LLM providers and sophisticated dialogue/quest generation.

**Comprehensive Asset Generation**: Integrated multimedia creation including CC0 graphics libraries, Google Fonts typography, TTS/music generation, and Internet Archive semantic seeding with PyTorch embeddings.

**FastMCP Server**: Model Context Protocol server for external tool integration, providing structured interfaces for Claude, ChatGPT, and other AI assistants.

**Professional Development Tools**: Hatch-based development environment with UV backend, comprehensive static analysis (mypy, ruff, bandit), automated testing with matrix support across Python 3.11/3.12, coverage reporting (currently 10% overall, models module at 98%), comprehensive E2E test suite with real OpenAI integration using pytest-vcr, and modern Python packaging standards.

### Documentation and Quality

**Sphinx with RST**: Professional documentation system using ReStructuredText with sphinx-autodoc2 for automatic API generation from static analysis. No need to install packages for documentation generation.

**Automated Quality Pipeline**: Comprehensive static analysis with MyPy, Pylint, Bandit, Ruff, and support for additional languages. Integrated with pre-commit hooks and CI/CD workflows.

**Justfile Build System**: Streamlined build system with 80+ commands for development, testing, documentation, packaging, and deployment workflows.

## Production Ready Features

**Single pyproject.toml**: Unified dependency management with hatch build backend and UV package manager. Optional dependency groups for different use cases (pygame, audio, web, dev).

**Modern Python Standards**: Python 3.11+ with modern type annotations, async/await patterns, and contemporary import styles. No legacy compatibility layers.

**Performance Optimization**: Intelligent caching, connection pooling, batch processing, and modular loading for optimal performance across different deployment scenarios.

**Enterprise Deployment**: Docker support, PyPI distribution, comprehensive testing suite, and professional documentation ready for production use.
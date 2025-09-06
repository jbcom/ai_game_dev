# replit.md

## Overview

This is a revolutionary unified AI-powered game development library that provides comprehensive tools for creating games using artificial intelligence. The system is now consolidated into a single Python package (`ai-game-dev`) with multi-LLM provider support, comprehensive asset generation, and engine-specific TOML specifications.

## User Preferences

Preferred communication style: Simple, everyday language.

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

**Professional Development Tools**: Async/await performance optimization, intelligent caching systems, batch processing capabilities, and cross-language static analysis.

### Documentation and Quality

**Sphinx with RST**: Professional documentation system using ReStructuredText with sphinx-autodoc2 for automatic API generation from static analysis. No need to install packages for documentation generation.

**Automated Quality Pipeline**: Comprehensive static analysis with MyPy, Pylint, Bandit, Ruff, and support for additional languages. Integrated with pre-commit hooks and CI/CD workflows.

**Justfile Build System**: Streamlined build system with 80+ commands for development, testing, documentation, packaging, and deployment workflows.

## Production Ready Features

**Single pyproject.toml**: Unified dependency management with hatch build backend and UV package manager. Optional dependency groups for different use cases (pygame, audio, web, dev).

**Modern Python Standards**: Python 3.11+ with modern type annotations, async/await patterns, and contemporary import styles. No legacy compatibility layers.

**Performance Optimization**: Intelligent caching, connection pooling, batch processing, and modular loading for optimal performance across different deployment scenarios.

**Enterprise Deployment**: Docker support, PyPI distribution, comprehensive testing suite, and professional documentation ready for production use.
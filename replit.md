# OpenAI Multimodal MCP Server

## Overview

This is an advanced Python MCP (Model Context Protocol) Server that provides image generation, vision analysis, and 3D model creation capabilities. The server integrates with OpenAI's APIs to offer multimodal AI services through a structured server architecture. It's designed as a modern Python 3.11+ application with async capabilities, content caching, and file management systems.

## User Preferences

Preferred communication style: Simple, everyday language.

## Recent Changes

- **September 2025**: Comprehensive feature enhancement and refactoring
- **Module Separation**: Split functionality into logical modules (models, generators, analyzers, server)
- **Advanced Features**: Added comprehensive error handling, structured logging, performance metrics, content validation, batch processing, and multiple export formats
- **Python Version**: Updated to support Python 3.11+ for broader compatibility
- **Type Safety**: Enhanced with modern lowercase type hints (list, dict instead of List, Dict)
- **Production Ready**: Added TTL caching, async optimization, XDG standards compliance

## System Architecture

### Core Framework
- **MCP Server Architecture**: Built using FastMCP framework for handling Model Context Protocol communications
- **Modular Design**: Structured library with separate modules for different concerns
- **Async/Await Pattern**: Leverages Python's asyncio for non-blocking operations and improved performance
- **Type Safety**: Implements comprehensive type hints with modern Python typing features for better code reliability

### Project Structure
```
src/openai_mcp_server/
├── __init__.py          # Package exports and version
├── main.py              # Main entry point
├── server.py            # Enhanced MCP server implementation
├── models.py            # Pydantic models and type definitions
├── generators.py        # Image and 3D model generation
├── analyzers.py         # Image analysis and vision capabilities
├── config.py            # Configuration with pydantic-settings and XDG
├── utils.py             # Utility functions
├── exceptions.py        # Custom exception hierarchy
├── logging_config.py    # Structured logging with Rich
├── metrics.py           # Performance monitoring and tracking
├── cache_manager.py     # Advanced TTL caching system
├── content_validator.py # Safety and quality validation
├── batch_processor.py   # Bulk operations and batch processing
└── export_formats.py    # Multi-format export capabilities
```

### Content Generation System
- **OpenAI Integration**: Uses OpenAI client for image generation and vision analysis capabilities
- **Multi-format Support**: Handles various image sizes and qualities through typed literals
- **3D Model Creation**: Includes infrastructure for 3D model generation and management
- **Structured Outputs**: Leverages OpenAI's structured output features for precise 3D specifications
- **Batch Processing**: Generate multiple images or models simultaneously with concurrency control
- **Content Validation**: AI-powered safety checks and quality validation for all generated content
- **Export Flexibility**: Convert between formats (PNG/JPEG/WebP for images, GLTF/GLB/OBJ for 3D models)

### Caching and Storage
- **Advanced TTL Caching**: Time-based expiration with automatic cleanup and LRU eviction
- **XDG Standards**: Proper system directory usage (~/.cache and ~/.local/share)
- **Content-based Caching**: Hash-based system for generated content to avoid redundant API calls
- **Structured File Organization**: Separates different asset types with metadata tracking
- **Cache Management**: Automatic cleanup, size limits, and performance optimization
- **Idempotent Operations**: Skip existing content unless forced by parameter

### File Management
- **Async File Operations**: Uses aiofiles for non-blocking file I/O operations
- **Path Management**: Leverages pathlib for modern, cross-platform path handling
- **Image Processing**: Integrates PIL (Pillow) for image manipulation capabilities

## Advanced Features

### Performance & Monitoring
- **Structured Logging**: Rich-formatted console output with file logging
- **Performance Metrics**: Detailed operation tracking, cache hit rates, API usage
- **Error Handling**: Comprehensive exception hierarchy with proper error recovery
- **Async Optimization**: Non-blocking operations with connection pooling

### Content Safety & Quality
- **Content Validation**: AI-powered safety checks and NSFW detection
- **Quality Assurance**: Automatic validation of generated images and 3D models
- **Moderation Integration**: OpenAI moderation API for text prompts

### Batch Operations & Export
- **Bulk Processing**: Generate multiple assets simultaneously with progress tracking
- **Format Conversion**: Export to multiple formats with optimization options
- **Streaming Support**: Real-time progress updates for long-running operations

## External Dependencies

### AI Services
- **OpenAI API**: Primary service for image generation and vision analysis
- **API Key Management**: Secure environment variable-based authentication

### Python Libraries
- **FastMCP**: Core MCP server framework
- **OpenAI Python Client**: Official OpenAI API client library
- **aiofiles**: Async file operations
- **Pillow (PIL)**: Image processing and manipulation
- **tiktoken**: Token counting for OpenAI models
- **Rich**: Enhanced terminal output and logging
- **Pydantic Settings**: Configuration management
- **XDG Base Dirs**: System directory standards

### System Requirements
- **Python 3.11+**: Modern Python runtime with latest async features
- **File System**: Local storage for asset caching and management
- **Package Management**: Uses modern UV/Hatch packaging system
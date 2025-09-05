# OpenAI Multimodal MCP Server

## Overview

This is an advanced Python MCP (Model Context Protocol) Server that provides image generation, vision analysis, and 3D model creation capabilities. The server integrates with OpenAI's APIs to offer multimodal AI services through a structured server architecture. It's designed as a modern Python 3.12+ application with async capabilities, content caching, and file management systems.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Core Framework
- **MCP Server Architecture**: Built using FastMCP framework for handling Model Context Protocol communications
- **Async/Await Pattern**: Leverages Python's asyncio for non-blocking operations and improved performance
- **Type Safety**: Implements comprehensive type hints with modern Python typing features for better code reliability

### Content Generation System
- **OpenAI Integration**: Uses OpenAI client for image generation and vision analysis capabilities
- **Multi-format Support**: Handles various image sizes and qualities through typed literals
- **3D Model Creation**: Includes infrastructure for 3D model generation and management

### Caching and Storage
- **Content-based Caching**: Implements hash-based caching system for generated content to avoid redundant API calls
- **Structured File Organization**: Separates different asset types (images, 3D models) into organized directory structures
- **Verification Cache**: Maintains a JSON-based cache for content verification and metadata

### File Management
- **Async File Operations**: Uses aiofiles for non-blocking file I/O operations
- **Path Management**: Leverages pathlib for modern, cross-platform path handling
- **Image Processing**: Integrates PIL (Pillow) for image manipulation capabilities

## External Dependencies

### AI Services
- **OpenAI API**: Primary service for image generation and vision analysis
- **API Key Management**: Environment variable-based authentication system

### Python Libraries
- **FastMCP**: Core MCP server framework
- **OpenAI Python Client**: Official OpenAI API client library
- **aiofiles**: Async file operations
- **Pillow (PIL)**: Image processing and manipulation
- **tiktoken**: Token counting for OpenAI models

### System Requirements
- **Python 3.12+**: Modern Python runtime with latest async features
- **File System**: Local storage for asset caching and management
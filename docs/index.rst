OpenAI MCP Server Documentation
=================================

**OpenAI MCP Server** is a revolutionary AI-powered game development system featuring GPT-5 intelligence, 
multi-agent orchestration, and persistent long-term memory. The system transforms any game specification 
format into complete, deployable games with sophisticated agent coordination and engine-specific optimization.

Key Features
------------

* 🤖 **GPT-5 Powered Intelligence** with 74% coding accuracy and 45% fewer hallucinations
* 🧠 **Multi-Agent Orchestration** with specialized roles (World Architect, Narrative Weaver, Asset Creator, Code Engineer)
* 💾 **Persistent Vector-based Memory** system with semantic search across development sessions
* 🌍 **Universal Format Analysis** for any specification format (natural language, JSON, YAML, TOML, Markdown)
* 🔧 **Engine-specific Sub-packages** with complete Bevy, Arcade, Pygame, Godot, Unity integration
* 🎯 **LangGraph Workflows** with SQLite state persistence and intelligent orchestration
* 🎨 **Structured LangChain Tools** with seamless OpenAI API integration

Quick Start
-----------

Installation::

    pip install openai-mcp-server

Basic Usage::

    from openai_mcp_server import create_server
    
    # Create MCP server
    server = create_server()
    
    # The server provides tools for:
    # - Image generation and analysis
    # - Game world building
    # - Narrative generation
    # - Specification analysis
    # - Agent orchestration

API Reference
-------------

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   modules/server
   modules/agents
   modules/generators
   modules/analyzers
   modules/tools

Architecture
------------

The system is built on several key architectural components:

**Core Framework**
    * MCP Server Architecture using FastMCP framework
    * LangGraph Agent System with SQLite state persistence
    * Structured Tool Integration with LangChain compatibility
    * Async/Await patterns for high performance
    * Comprehensive type safety with modern Python typing

**Agent System**
    * Multi-agent coordination with specialized subgraphs
    * Persistent memory across development sessions
    * Intelligent workflow orchestration
    * State management with SQLite backend

**Tool Integration**
    * OpenAI DALL-E 3 for image generation
    * OpenAI GPT-5 for text and code generation
    * OpenAI Vision for image analysis
    * Custom game development tools

Development
-----------

The project uses modern Python tooling:

* **Hatch** for project management and virtual environments
* **pytest** with asyncio support for testing
* **Black** and **Ruff** for code formatting and linting  
* **mypy** for static type checking
* **Sphinx** for documentation generation

Run tests::

    hatch run test

Format code::

    hatch run format

Build documentation::

    hatch run docs

Contributing
------------

We welcome contributions! Please see our contributing guidelines for more information.

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
AI Game Development Library
============================

.. image:: https://img.shields.io/pypi/v/ai-game-dev.svg
   :target: https://pypi.python.org/pypi/ai-game-dev
   :alt: PyPI Version

.. image:: https://img.shields.io/pypi/pyversions/ai-game-dev.svg
   :target: https://pypi.python.org/pypi/ai-game-dev
   :alt: Python Versions

.. image:: https://github.com/ai-game-dev/ai-game-dev/workflows/CI/badge.svg
   :target: https://github.com/ai-game-dev/ai-game-dev/actions
   :alt: CI Status

.. image:: https://codecov.io/gh/ai-game-dev/ai-game-dev/branch/main/graph/badge.svg
   :target: https://codecov.io/gh/ai-game-dev/ai-game-dev
   :alt: Coverage

A revolutionary unified Python package for AI-powered game development featuring multi-LLM support, 
comprehensive asset generation, and engine-specific TOML specifications.

Key Features
------------

🧠 **Multi-LLM Provider Support**
   - OpenAI (GPT-4, GPT-4o, GPT-3.5-turbo)
   - Anthropic Claude (Claude-3.5-Sonnet, Claude-3-Haiku)
   - Google Gemini (Gemini-1.5-Pro, Gemini-1.5-Flash)
   - Local LLMs via Ollama (Llama, Mistral, CodeLlama)

🎮 **Engine-Specific Templates**
   - Pygame (2D sprite-based games)
   - Bevy (High-performance Rust ECS)
   - Godot (Scene-node tree architecture)
   - Arcade (Modern Python game library)

🎨 **Comprehensive Asset Generation**
   - CC0 graphics libraries integration
   - Google Fonts typography system
   - Audio generation (TTS, music, sound effects)
   - Internet Archive semantic seeding

🔧 **Professional Development Tools**
   - LangChain/LangGraph orchestration
   - JSON schemas for AI integration
   - FastMCP server for tool integration
   - Async/await performance optimization

Quick Start
-----------

Installation
~~~~~~~~~~~~

.. code-block:: bash

   pip install ai-game-dev

Basic Usage
~~~~~~~~~~~

.. code-block:: python

   from ai_game_dev import AIGameDev, create_default_manager

   # Set up multi-LLM provider
   llm_manager = create_default_manager()
   
   # Initialize the game development system
   game_dev = AIGameDev(llm_provider=llm_manager)
   
   # Generate a complete game
   game_spec = {
       "title": "Space Adventure",
       "genre": "platformer", 
       "target_engine": "pygame",
       "complexity": "intermediate"
   }
   
   result = await game_dev.generate_complete_game(game_spec)
   print(f"Game generated: {result.project_path}")

Asset Generation
~~~~~~~~~~~~~~~~

.. code-block:: python

   from ai_game_dev import AssetTools
   
   # Generate comprehensive asset package
   asset_tools = AssetTools()
   
   asset_package = await asset_tools.generate_complete_asset_pack(
       game_description="A retro-style space shooter",
       asset_types=["sprites", "ui", "backgrounds", "sfx"],
       art_style="pixel_art",
       max_assets_per_type=10
   )
   
   print(f"Generated {asset_package.total_assets} assets")

Multi-LLM Configuration
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from ai_game_dev import LLMProviderManager, LLMProvider
   
   # Configure multiple providers with fallback
   manager = LLMProviderManager()
   
   # Add OpenAI provider
   manager.add_provider(
       name="openai_primary",
       provider_type=LLMProvider.OPENAI,
       model_name="gpt-4o"
   )
   
   # Add Anthropic fallback
   manager.add_provider(
       name="anthropic_fallback", 
       provider_type=LLMProvider.ANTHROPIC,
       model_name="claude-3-5-sonnet-20241022"
   )
   
   # Generate with automatic fallback
   result = await manager.generate_with_fallback(
       "Create a puzzle game concept",
       provider_names=["openai_primary", "anthropic_fallback"]
   )

Documentation
-------------

.. toctree::
   :maxdepth: 2
   :caption: User Guide

   installation
   quickstart
   tutorials/index
   examples/index

.. toctree::
   :maxdepth: 2
   :caption: API Reference

   api/ai_game_dev/ai_game_dev

.. toctree::
   :maxdepth: 2
   :caption: Engine Integration

   engines/pygame
   engines/bevy
   engines/godot
   engines/arcade

.. toctree::
   :maxdepth: 2
   :caption: Advanced Topics

   advanced/llm_providers
   advanced/asset_generation
   advanced/mcp_server
   advanced/json_schemas

.. toctree::
   :maxdepth: 1
   :caption: Development

   contributing
   changelog
   license

Architecture Overview
---------------------

The AI Game Development library is built on a unified architecture that combines:

**Core Orchestration**
   Pure LangChain/LangGraph agents for intelligent game generation workflows

**Asset Management**  
   Standalone multimedia generation with TTS, music composition, and visual assets

**Engine Adapters**
   Language-native code generation for Rust (Bevy), Python (Pygame/Arcade), and GDScript (Godot)

**Multi-LLM Support**
   Flexible provider system with automatic fallback and cost optimization

**Structured Specifications**
   TOML templates and JSON schemas for consistent AI-generated content

Performance & Scalability
--------------------------

- **Async/await patterns** for non-blocking operations
- **Intelligent caching** with TTL and content-based invalidation  
- **Batch processing** for multiple asset generation
- **Connection pooling** for LLM provider efficiency
- **Modular architecture** for selective feature loading

Community & Support
--------------------

- **GitHub Repository**: https://github.com/ai-game-dev/ai-game-dev
- **Documentation**: https://ai-game-dev.readthedocs.io
- **PyPI Package**: https://pypi.org/project/ai-game-dev
- **Issues**: https://github.com/ai-game-dev/ai-game-dev/issues

Indices and Tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
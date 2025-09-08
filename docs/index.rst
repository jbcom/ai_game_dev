AI Game Development Platform
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

A revolutionary AI-powered game development platform using OpenAI's latest models (GPT-5 and GPT-Image-1) with a modern Chainlit UI for creating complete games through natural language.

Key Features
------------

🤖 **OpenAI Agents Architecture**
   - Direct function calling with OpenAI's native tools
   - GPT-5 for superior text and code generation
   - GPT-Image-1 for high-quality game assets
   - Simplified architecture without framework overhead

🎮 **Multi-Engine Support**
   - **Pygame**: 2D Python games with sprites and physics
   - **Godot**: Professional 2D/3D games with GDScript
   - **Bevy**: High-performance Rust games with ECS

🎨 **Comprehensive Asset Generation**
   - DALL-E 3 (GPT-Image-1) for sprites and backgrounds
   - OpenAI TTS for voice acting and narration
   - Music21 integration for dynamic soundtracks
   - Freesound API for sound effects

🎓 **Educational Platform**
   - Arcade Academy mode with guided tutorials
   - Progressive learning curriculum
   - Interactive RPG for learning programming
   - Real-time AI mentorship

Quick Start
-----------

Installation
~~~~~~~~~~~~

.. code-block:: bash

   # Clone and setup
   git clone <repository-url>
   cd ai-game-dev
   
   # Install dependencies
   pip install hatch
   hatch env create
   
   # Configure API key
   export OPENAI_API_KEY="sk-..."
   
   # Start the platform
   hatch run server

Visit ``http://localhost:8000`` to access the Chainlit interface.

Basic Usage
~~~~~~~~~~~

**Web Interface (Recommended)**

1. Open ``http://localhost:8000``
2. Choose "Game Workshop" or "Arcade Academy"
3. Follow the wizard-style workflow
4. Download your generated game

**Python API**

.. code-block:: python

   from ai_game_dev.agent import GameDevAgent
   
   # Initialize agent
   agent = GameDevAgent()
   
   # Generate a complete game
   result = await agent.create_game(
       description="A cyberpunk platformer with hacking mechanics",
       engine="pygame",
       art_style="pixel art"
   )
   
   print(f"Game created at: {result.output_path}")

Asset Generation
~~~~~~~~~~~~~~~~

.. code-block:: python

   from ai_game_dev.tools.openai_tools import (
       generate_game_asset,
       generate_character_sprite,
       generate_environment
   )
   
   # Generate a character
   character = await generate_character_sprite(
       character_name="Cyber Ninja",
       character_description="Futuristic ninja with neon accents",
       art_style="cyberpunk pixel art",
       save_path="assets/cyber_ninja.png"
   )
   
   # Generate an environment
   background = await generate_environment(
       environment_name="Neo Tokyo Streets",
       description="Rainy cyberpunk city with neon signs",
       time_of_day="night",
       save_path="assets/neo_tokyo.png"
   )

Documentation
-------------

.. toctree::
   :maxdepth: 2
   :caption: User Guide

   getting-started
   installation
   configuration
   examples

.. toctree::
   :maxdepth: 2
   :caption: Features

   workshop-mode
   academy-mode
   asset-generation
   engine-templates

.. toctree::
   :maxdepth: 2
   :caption: API Reference

   api/agent
   api/tools
   api/constants
   api/startup

.. toctree::
   :maxdepth: 2
   :caption: Development

   contributing
   testing
   architecture
   changelog

Architecture Overview
---------------------

The platform is built on a clean, modern architecture:

**Core Components**
   - **OpenAI Agent**: Orchestrates all AI operations using function tools
   - **Chainlit UI**: Provides interactive web interface with custom React components
   - **Function Tools**: Specialized tools for image, audio, text, and code generation
   - **Template System**: Jinja2 templates for engine-specific code generation

**Key Technologies**
   - **GPT-5**: Latest language model for text and code
   - **GPT-Image-1**: Advanced image generation (DALL-E 3)
   - **OpenAI TTS**: High-quality text-to-speech
   - **Music21**: Algorithmic music composition
   - **Chainlit**: Modern Python UI framework

**Design Principles**
   - Direct API calls over framework abstractions
   - Async-first for performance
   - Type-safe with modern Python
   - Centralized configuration

Performance & Scalability
-------------------------

- **Parallel API Calls**: 3-5x faster generation
- **Streaming Responses**: Real-time progress updates
- **Efficient Caching**: Smart asset reuse
- **WebSocket Communication**: Low-latency UI updates
- **Modular Architecture**: Load only what you need

Educational Features
--------------------

**Arcade Academy**
   - Skill assessment and adaptive learning
   - Step-by-step tutorials with Professor Pixel
   - Interactive challenges and projects
   - Progress tracking and achievements

**Teachable Moments**
   - AI identifies learning opportunities
   - Contextual explanations
   - Best practices guidance
   - Code review and improvement suggestions

Community & Support
-------------------

- **GitHub Repository**: https://github.com/ai-game-dev/ai-game-dev
- **Issue Tracker**: Report bugs and request features
- **Documentation**: Comprehensive guides and API reference
- **Examples**: Complete game projects to learn from

Indices and Tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
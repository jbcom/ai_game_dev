Installation Guide
==================

This guide covers the installation of the AI Game Development library across different platforms and environments.

Requirements
------------

**Python Version**
   - Python 3.11 or higher
   - Python 3.12 recommended for best performance

**System Dependencies**
   - Git (for development installation)
   - Build tools (for some optional dependencies)

Basic Installation
------------------

The simplest way to install the AI Game Development library is via pip:

.. code-block:: bash

   pip install ai-game-dev

This installs the core library with basic functionality including:

- Core AI orchestration (LangChain/LangGraph)
- Multi-LLM provider support
- Basic asset generation
- Engine specifications (TOML templates)

Development Installation
------------------------

For development or to get the latest features:

.. code-block:: bash

   git clone https://github.com/ai-game-dev/ai-game-dev.git
   cd ai-game-dev
   pip install -e ".[dev]"

This installs the library in development mode with additional development tools.

Optional Dependencies
---------------------

The library provides several optional dependency groups for extended functionality:

Game Engine Support
~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # For Pygame integration
   pip install "ai-game-dev[pygame]"
   
   # For Arcade integration  
   pip install "ai-game-dev[arcade]"
   
   # Note: Bevy (Rust) and Godot integrations are template-based
   # and don't require additional Python packages

Advanced Audio Processing
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Enhanced audio generation and processing
   pip install "ai-game-dev[audio]"

This includes:

- ``librosa`` for advanced audio analysis
- ``soundfile`` for audio file I/O
- ``pydub`` for audio manipulation

Web Interface
~~~~~~~~~~~~~

.. code-block:: bash

   # Web-based interfaces and tools
   pip install "ai-game-dev[web]"

This includes:

- ``mesop`` for interactive web interfaces
- ``streamlit`` for rapid prototyping

All Optional Dependencies
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Install everything
   pip install "ai-game-dev[all]"

LLM Provider Setup
------------------

The library supports multiple LLM providers. You'll need API keys for the providers you want to use:

OpenAI
~~~~~~

1. Sign up at https://platform.openai.com/
2. Generate an API key
3. Set the environment variable:

.. code-block:: bash

   export OPENAI_API_KEY="your-api-key-here"

Anthropic Claude
~~~~~~~~~~~~~~~~

1. Sign up at https://console.anthropic.com/
2. Generate an API key  
3. Set the environment variable:

.. code-block:: bash

   export ANTHROPIC_API_KEY="your-api-key-here"

Google Gemini
~~~~~~~~~~~~~

1. Get an API key from https://aistudio.google.com/app/apikey
2. Set the environment variable:

.. code-block:: bash

   export GOOGLE_API_KEY="your-api-key-here"

Local LLMs (Ollama)
~~~~~~~~~~~~~~~~~~~

1. Install Ollama from https://ollama.ai/
2. Pull a model:

.. code-block:: bash

   ollama pull llama3.1:8b

3. The library will automatically detect local Ollama installation

Environment Configuration
--------------------------

Create a ``.env`` file in your project directory:

.. code-block:: bash

   # LLM Provider API Keys
   OPENAI_API_KEY=your-openai-key
   ANTHROPIC_API_KEY=your-anthropic-key
   GOOGLE_API_KEY=your-google-key
   
   # Optional: Ollama configuration
   OLLAMA_BASE_URL=http://localhost:11434
   
   # Optional: Default provider
   DEFAULT_LLM_PROVIDER=openai

Verification
------------

Verify your installation works correctly:

.. code-block:: python

   import ai_game_dev
   
   print(f"AI Game Dev version: {ai_game_dev.get_version()}")
   print(f"Supported engines: {ai_game_dev.get_supported_engines()}")
   print(f"Supported LLM providers: {ai_game_dev.get_supported_llm_providers()}")

You should see output similar to:

.. code-block:: text

   AI Game Dev version: 1.0.0
   Supported engines: ['pygame', 'bevy', 'godot', 'arcade']
   Supported LLM providers: ['openai', 'anthropic', 'google', 'ollama']

Testing LLM Connectivity
-------------------------

Test your LLM provider setup:

.. code-block:: python

   from ai_game_dev import create_default_manager
   
   # This will attempt to configure all available providers
   manager = create_default_manager()
   
   # List successfully configured providers
   print("Configured providers:", manager.list_providers())

Docker Installation
-------------------

A Docker image is available for easy deployment:

.. code-block:: bash

   docker pull aigamedev/ai-game-dev:latest
   
   # Run with environment variables
   docker run -e OPENAI_API_KEY=your-key aigamedev/ai-game-dev:latest

Troubleshooting
---------------

Common Installation Issues
~~~~~~~~~~~~~~~~~~~~~~~~~~

**ModuleNotFoundError: No module named 'ai_game_dev'**

Ensure you've installed the package:

.. code-block:: bash

   pip install ai-game-dev

**Import errors with optional dependencies**

Install the required optional dependency group:

.. code-block:: bash

   pip install "ai-game-dev[audio]"  # for audio features

**LLM provider authentication errors**

Verify your API keys are set correctly:

.. code-block:: bash

   echo $OPENAI_API_KEY

Performance Optimization
~~~~~~~~~~~~~~~~~~~~~~~~

For better performance, consider:

1. **Using uvloop** (Linux/macOS only):

.. code-block:: bash

   pip install uvloop

2. **Installing PyTorch with CUDA** for GPU acceleration:

.. code-block:: bash

   # Check CUDA version first
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

3. **Using faster JSON libraries**:

.. code-block:: bash

   pip install orjson ujson

Getting Help
------------

If you encounter issues:

1. Check the `GitHub Issues <https://github.com/ai-game-dev/ai-game-dev/issues>`_
2. Join our `Discord Community <https://discord.gg/ai-game-dev>`_
3. Read the `FAQ <https://ai-game-dev.readthedocs.io/en/latest/faq.html>`_

Next Steps
----------

Once installed, proceed to the :doc:`quickstart` guide to start creating your first AI-generated game!
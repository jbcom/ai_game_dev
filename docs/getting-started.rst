Getting Started with AI Game Development
========================================

Quick Start
-----------

The AI Game Development platform provides revolutionary tools for creating games with artificial intelligence using OpenAI's latest models (GPT-5 and GPT-Image-1). Get started with our Chainlit-powered interface in minutes.

Installation
~~~~~~~~~~~~

Core Platform
^^^^^^^^^^^^^

.. code-block:: bash

   # Clone the repository
   git clone <repository-url>
   cd ai-game-dev
   
   # Install with hatch
   pip install hatch
   hatch env create
   
   # Set up environment
   export OPENAI_API_KEY="your-api-key-here"
   
   # Start the platform
   hatch run server

The platform will be available at ``http://localhost:8000``

Your First AI-Generated Game
----------------------------

Using the Web Interface
~~~~~~~~~~~~~~~~~~~~~~~

1. **Access the Platform**
   
   Navigate to ``http://localhost:8000`` in your browser

2. **Choose Your Mode**
   
   - **Game Workshop**: Create custom games with any engine
   - **Arcade Academy**: Learn programming through guided tutorials

3. **Create a Game (Workshop Mode)**
   
   .. code-block:: text
   
      Describe your game: "A retro space shooter with power-ups and boss battles"
      Select engine: Pygame
      
   The AI will generate:
   
   - Complete source code
   - Game assets (sprites, sounds, music)
   - Project structure
   - Documentation

Using the Python API
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from ai_game_dev.agent import GameDevAgent
   from ai_game_dev.constants import GAME_ENGINES
   
   # Initialize the agent
   agent = GameDevAgent()
   
   # Generate a complete game
   result = await agent.create_game(
       description="A retro space shooter with power-ups",
       engine="pygame",
       features=["player movement", "enemies", "shooting", "power-ups"],
       art_style="pixel art"
   )
   
   # Access generated files
   print(f"Game created at: {result.output_path}")
   print(f"Assets: {result.assets}")
   print(f"Source files: {result.source_files}")

Key Features
------------

AI-Powered Generation
~~~~~~~~~~~~~~~~~~~~~

- **GPT-5 Code Generation**: State-of-the-art code generation
- **GPT-Image-1 Assets**: High-quality game sprites and backgrounds
- **OpenAI TTS**: Voice acting and sound effects
- **Music Generation**: Dynamic soundtrack creation with music21

Multi-Engine Support
~~~~~~~~~~~~~~~~~~~~

**Pygame (Python 2D)**
   
   - Perfect for learning and prototyping
   - Cross-platform compatibility
   - Extensive community resources

**Godot (GDScript/3D/2D)**
   
   - Professional game engine
   - Visual editor integration
   - Export to multiple platforms

**Bevy (Rust ECS)**
   
   - High-performance games
   - Entity Component System
   - Modern Rust patterns

Wizard-Style Workflows
~~~~~~~~~~~~~~~~~~~~~~

Both Workshop and Academy modes feature guided workflows:

.. code-block:: text

   Workshop Flow:
   1. Game Description → 2. Engine Selection → 3. Feature Detection
   4. Asset Generation → 5. Code Generation → 6. Review & Export
   
   Academy Flow:
   1. Skill Assessment → 2. Lesson Selection → 3. Guided Tutorial
   4. Practice Challenge → 5. Knowledge Check → 6. Project Showcase

Advanced Usage
--------------

Custom Asset Generation
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from ai_game_dev.tools.openai_tools import generate_game_asset
   
   # Generate a character sprite
   character = await generate_game_asset(
       asset_type="sprite",
       description="Pixel art warrior with sword and shield",
       art_style="16-bit pixel art",
       size="1024x1024",
       save_path="assets/warrior.png"
   )
   
   # Generate a background
   background = await generate_game_asset(
       asset_type="background",
       description="Cyberpunk city at night with neon lights",
       art_style="digital art",
       size="1792x1024",
       save_path="assets/city_bg.png"
   )

Audio Generation
~~~~~~~~~~~~~~~~

.. code-block:: python

   from ai_game_dev.tools.openai_tools import generate_game_audio
   
   # Generate background music
   music = await generate_game_audio(
       audio_type="music",
       description="Epic orchestral battle theme",
       duration=120,
       style="orchestral",
       save_path="assets/battle_theme.mp3"
   )
   
   # Generate sound effects
   sfx = await generate_game_audio(
       audio_type="sfx", 
       description="Laser gun shooting sound",
       duration=1,
       save_path="assets/laser.wav"
   )

Template Customization
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from ai_game_dev.tools.openai_tools.template_loader import template_loader
   
   # Load and customize engine templates
   template = template_loader.get_engine_template("pygame", "architecture")
   
   # Render with custom context
   architecture = template.render(
       game_title="Space Defender",
       game_type="arcade shooter",
       features=["multiplayer", "leaderboards", "achievements"]
   )

Examples and Tutorials
----------------------

The platform includes several example projects:

- **Pygame Space Shooter**: Complete 2D arcade game with enemies and power-ups
- **Godot RPG Adventure**: 3D role-playing game with quests and dialogue
- **Bevy Tower Defense**: High-performance strategy game with ECS
- **Educational Pygame**: Learn programming concepts through game development

Run examples with:

.. code-block:: bash

   # Navigate to examples
   cd examples/pygame_space_shooter
   
   # Install dependencies
   pip install -r requirements.txt
   
   # Run the game
   python main.py

Configuration
-------------

Environment Variables
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Required
   OPENAI_API_KEY="sk-..."          # OpenAI API key
   
   # Optional
   AI_GAME_DEV_PORT=8000           # Custom port (default: 8000)
   FREESOUND_API_KEY="..."         # For additional sound effects
   
   # Development
   AI_GAME_DEV_DEBUG=true          # Enable debug logging
   AI_GAME_DEV_CACHE=false         # Disable caching

Project Configuration
~~~~~~~~~~~~~~~~~~~~~

Edit ``pyproject.toml`` to customize:

- Dependencies
- Development tools
- Test configuration
- Build settings

Next Steps
----------

1. **Explore the Interface**: Try both Workshop and Academy modes
2. **Read the API Reference**: Detailed documentation for all modules
3. **Check Examples**: Learn from complete game projects
4. **Join the Community**: Share your creations and get help

Need Help?
----------

- **Documentation**: Full API reference at ``/docs``
- **GitHub Issues**: Report bugs and request features
- **Code Examples**: See ``/examples`` directory
- **Configuration**: Check ``.cursor/``, ``.gemini/``, and ``.github/`` for AI assistant setup
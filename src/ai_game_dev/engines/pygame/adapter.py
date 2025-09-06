"""
Pygame engine adapter for Python game development.
Generates complete, working Pygame projects with professional structure.
"""
from typing import Dict, List
from pathlib import Path

from ai_game_dev.engines.base import BaseEngineAdapter, EngineGenerationResult


class PygameAdapter(BaseEngineAdapter):
    """Adapter for Python Pygame projects."""
    
    @property
    def engine_name(self) -> str:
        return "pygame"
    
    @property
    def native_language(self) -> str:
        return "python"
    
    async def generate_game_project(
        self,
        description: str,
        complexity: str = "intermediate",
        features: List[str] = None,
        art_style: str = "modern"
    ) -> EngineGenerationResult:
        """Generate Pygame Python project with real working code."""
        
        features = features or []
        project_name = description.replace(" ", "_").lower()[:20]
        
        # Generate main.py
        main_prompt = f"""
        Create a complete main.py file for a Pygame game: {description}
        Complexity: {complexity}
        Features: {', '.join(features)}
        Art style: {art_style}
        
        Requirements:
        - Proper pygame initialization and cleanup
        - Professional game loop with event handling
        - Screen setup (800x600) and rendering
        - Import statements for game and player modules
        - Error handling and graceful shutdown
        - FPS control at 60 FPS
        
        Make it production-ready, well-commented, and executable.
        """
        
        # Generate game.py
        game_prompt = f"""
        Create a complete game.py file for a Pygame game: {description}
        
        Requirements:
        - Game class with proper state management
        - Initialize, update, and render methods
        - Asset loading and resource management
        - Game state handling (menu, playing, game over)
        - Collision detection and physics
        - Score/health/inventory systems as needed
        - Sound and music integration
        
        Features to implement: {', '.join(features)}
        Complexity: {complexity}
        Art style: {art_style}
        
        Use pygame best practices and modular design.
        """
        
        # Generate player.py
        player_prompt = f"""
        Create a complete player.py file for a Pygame game: {description}
        
        Requirements:
        - Player class with movement and controls
        - Sprite handling and animation
        - Input processing (keyboard/mouse)
        - Physics and collision boundaries
        - Health, abilities, and state management
        - Smooth movement and responsive controls
        
        Features: {', '.join(features)}
        Style: {art_style}
        Complexity: {complexity}
        
        Make it feel responsive and professional.
        """
        
        # Generate utils.py
        utils_prompt = f"""
        Create a complete utils.py file for a Pygame game: {description}
        
        Include utility functions for:
        - Asset loading (images, sounds, fonts)
        - Math helpers (distance, collision, vectors)
        - Color constants and palettes for {art_style} style
        - Screen utility functions
        - Configuration constants
        - Helper functions for common game tasks
        
        Make it comprehensive and reusable.
        """
        
        # Static files
        requirements_content = """pygame>=2.5.0
numpy>=1.24.0
"""
        
        readme_content = f"""# {description.title()}

A {complexity} complexity Pygame game featuring:
{chr(10).join(f"- {feature}" for feature in features)}

## Installation

1. Install Python 3.8+
2. Install dependencies: `pip install -r requirements.txt`
3. Run the game: `python main.py`

## Controls

- Arrow keys or WASD for movement
- Space for actions
- ESC to quit

## Features

- {art_style.title()} art style
- Professional game architecture
- Modular code structure
- {complexity.title()} difficulty level

## Architecture

- `main.py`: Entry point and game loop
- `game.py`: Core game logic and state management
- `player.py`: Player character implementation
- `utils.py`: Utility functions and constants
"""
        
        # Generate all code files
        generated_files = {
            "main.py": await self.generate_code_with_llm(main_prompt),
            "game.py": await self.generate_code_with_llm(game_prompt),
            "player.py": await self.generate_code_with_llm(player_prompt),
            "utils.py": await self.generate_code_with_llm(utils_prompt),
            "requirements.txt": requirements_content,
            "README.md": readme_content
        }
        
        # Save files to disk
        project_path = await self.save_project_files(project_name, generated_files)
        
        return EngineGenerationResult(
            engine_type="pygame",
            project_structure=self.get_project_template(),
            main_files=list(generated_files.keys()),
            asset_requirements=["player.png", "background.png", "sounds.wav", "music.ogg"],
            build_instructions=self.get_build_instructions(),
            deployment_notes="Use PyInstaller or cx_Freeze for standalone executables",
            generated_files=generated_files,
            project_path=project_path
        )
    
    def get_project_template(self) -> Dict[str, str]:
        """Get Pygame project template structure."""
        return {
            "main.py": "Entry point and game initialization",
            "game.py": "Core game logic and state management", 
            "player.py": "Player character implementation",
            "utils.py": "Utility functions and constants",
            "assets/": "Asset files directory",
            "assets/images/": "Image assets",
            "assets/sounds/": "Audio assets",
            "assets/fonts/": "Font assets"
        }
    
    def get_build_instructions(self) -> str:
        return """Build Instructions for Pygame Project:

1. Install Python 3.8+
2. Create virtual environment: python -m venv venv
3. Activate: source venv/bin/activate (Linux/Mac) or venv\\Scripts\\activate (Windows)
4. Install dependencies: pip install -r requirements.txt
5. Run: python main.py

For distribution:
- PyInstaller: pip install pyinstaller && pyinstaller --onefile main.py
- Auto-py-to-exe: GUI wrapper for PyInstaller
- cx_Freeze: Alternative packaging solution

Development:
- Use pygame.font.Font() for custom fonts
- pygame.mixer for audio
- pygame.sprite.Group() for sprite management
"""
"""
Godot engine adapter for GDScript game development.
Generates complete scene-based Godot projects with professional structure.
"""
from typing import Dict, List
from pathlib import Path

from ai_game_dev.engines.base import BaseEngineAdapter, EngineGenerationResult


class GodotAdapter(BaseEngineAdapter):
    """Adapter for Godot engine projects."""
    
    @property
    def engine_name(self) -> str:
        return "godot"
    
    @property
    def native_language(self) -> str:
        return "gdscript"
    
    async def generate_game_project(
        self,
        description: str,
        complexity: str = "intermediate",
        features: List[str] = None,
        art_style: str = "modern"
    ) -> EngineGenerationResult:
        """Generate Godot project with scene-based architecture."""
        
        features = features or []
        project_name = description.replace(" ", "_").lower()[:20]
        
        # Generate project.godot
        project_prompt = f"""
        Create a complete project.godot configuration file for: {description}
        
        Requirements:
        - Proper Godot 4.x configuration
        - Input map for game controls
        - Display settings for {art_style} style
        - Audio settings
        - Physics configuration
        - Export settings preparation
        
        Features: {', '.join(features)}
        Complexity: {complexity}
        """
        
        # Generate Main.gd
        main_prompt = f"""
        Create a complete Main.gd script for a Godot game: {description}
        Complexity: {complexity}
        Features: {', '.join(features)}
        Art style: {art_style}
        
        Requirements:
        - Extends appropriate node type (Node2D or Node3D)
        - Game initialization in _ready()
        - Game loop management
        - Scene management and transitions
        - Input handling
        - Game state management
        - Audio management
        
        Make it production-ready with proper GDScript patterns.
        """
        
        # Generate Player.gd
        player_prompt = f"""
        Create a complete Player.gd script for a Godot game: {description}
        
        Requirements:
        - Extends CharacterBody2D or CharacterBody3D as appropriate
        - Movement with built-in physics
        - Input processing
        - Animation handling
        - Health and state management
        - Collision detection
        - Signal emissions for game events
        
        Features: {', '.join(features)}
        Style: {art_style}
        Complexity: {complexity}
        
        Use Godot's best practices and node system.
        """
        
        # Generate GameManager.gd
        gamemanager_prompt = f"""
        Create a complete GameManager.gd script for a Godot game: {description}
        
        Requirements:
        - Singleton/autoload pattern
        - Game state management
        - Score and progression tracking
        - Scene transitions
        - Save/load functionality
        - Settings management
        - Audio management
        
        Features: {', '.join(features)}
        Complexity: {complexity}
        
        Make it a robust game management system.
        """
        
        # Generate UI.gd
        ui_prompt = f"""
        Create a complete UI.gd script for a Godot game: {description}
        
        Requirements:
        - Main menu implementation
        - HUD elements
        - Pause menu
        - Settings menu
        - Game over screen
        - Control node management
        - Signal connections
        
        Style: {art_style}
        Features: {', '.join(features)}
        
        Use Godot's UI system effectively.
        """
        
        # Static files
        readme_content = f"""# {description.title()}

A {complexity} complexity Godot game featuring:
{chr(10).join(f"- {feature}" for feature in features)}

## Installation

1. Install Godot Engine 4.x: https://godotengine.org/
2. Open project in Godot Editor
3. Press F5 or click Run button

## Controls

- Arrow keys or WASD for movement
- Space for actions
- ESC for menu/pause

## Features

- {art_style.title()} art style
- Scene-based architecture
- Professional GDScript implementation
- {complexity.title()} complexity level

## Development

- Main scene: `scenes/Main.tscn`
- Player scene: `scenes/Player.tscn`
- UI scenes in `scenes/ui/`
- Scripts in `scripts/`

## Export

1. Go to Project > Export
2. Add export template for target platform
3. Configure export settings
4. Export project

## Architecture

- `Main.gd`: Game initialization and management
- `Player.gd`: Player character controller
- `GameManager.gd`: Game state and progression
- `UI.gd`: User interface management
- `scenes/`: Scene files (.tscn)
- `assets/`: Game assets
"""
        
        gitignore_content = """# Godot-specific ignores
.import/
export.cfg
export_presets.cfg

# Mono-specific ignores
.mono/
data_*/
mono_crash.*.json

# System files
.DS_Store
Thumbs.db
"""
        
        # Generate all code files
        generated_files = {
            "project.godot": await self.generate_code_with_llm(project_prompt),
            "scripts/Main.gd": await self.generate_code_with_llm(main_prompt),
            "scripts/Player.gd": await self.generate_code_with_llm(player_prompt),
            "scripts/GameManager.gd": await self.generate_code_with_llm(gamemanager_prompt),
            "scripts/UI.gd": await self.generate_code_with_llm(ui_prompt),
            "README.md": readme_content,
            ".gitignore": gitignore_content,
            "assets/.gitkeep": "",
            "scenes/.gitkeep": "",
            "scenes/ui/.gitkeep": ""
        }
        
        # Save files to disk
        project_path = await self.save_project_files(project_name, generated_files)
        
        return EngineGenerationResult(
            engine_type="godot",
            project_structure=self.get_project_template(),
            main_files=list(generated_files.keys()),
            asset_requirements=["player.png", "background.png", "sounds.ogg", "music.ogg"],
            build_instructions=self.get_build_instructions(),
            deployment_notes="Export project using Godot editor export templates",
            generated_files=generated_files,
            project_path=project_path
        )
    
    def get_project_template(self) -> Dict[str, str]:
        """Get Godot project template structure."""
        return {
            "project.godot": "Godot project configuration",
            "scripts/Main.gd": "Main game script",
            "scripts/Player.gd": "Player controller script", 
            "scripts/GameManager.gd": "Game management script",
            "scripts/UI.gd": "User interface script",
            "scenes/": "Scene files directory",
            "scenes/ui/": "UI scene files",
            "assets/": "Asset files directory",
            "assets/sprites/": "2D sprites",
            "assets/models/": "3D models",
            "assets/sounds/": "Audio files"
        }
    
    def get_build_instructions(self) -> str:
        return """Build Instructions for Godot Project:

1. Install Godot Engine 4.x: https://godotengine.org/
2. Open project.godot in Godot Editor
3. Test with F5 (Run Project) or F6 (Run Scene)
4. For export: Project > Export

Development Workflow:
- Use scenes for game objects and UI
- Attach scripts to scene nodes
- Use signals for communication between nodes
- Organize assets in the assets/ folder

Export Process:
1. Download export templates: Editor > Manage Export Templates
2. Go to Project > Export
3. Add export preset for target platform
4. Configure settings (icon, permissions, etc.)
5. Export project

Platform Notes:
- Desktop: Windows, macOS, Linux export available
- Mobile: Android APK, iOS (requires macOS)
- Web: HTML5 export for browser games
- Console: Switch to Godot Console editions for console support

Performance:
- Use Godot's profiler for optimization
- Consider 2D vs 3D renderer choice
- Optimize textures and audio for target platform
"""
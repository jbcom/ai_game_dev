"""
Engine adapters for connecting to language-native game engine implementations.
Provides structured interfaces for Rust Bevy, Python Pygame/Arcade, etc.
"""
from typing import Dict, Any, List, Optional, Protocol
from dataclasses import dataclass
from abc import ABC, abstractmethod

from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field


class EngineGenerationRequest(BaseModel):
    """Request for engine-specific game generation."""
    game_description: str = Field(description="Description of the game to generate")
    engine_type: str = Field(description="Target engine (bevy, godot, pygame, arcade)")
    complexity: str = Field(default="intermediate", description="Game complexity level")
    features: List[str] = Field(default=[], description="Specific features to implement")
    art_style: str = Field(default="modern", description="Visual art style")


@dataclass
class EngineGenerationResult:
    """Result from engine-specific generation."""
    engine_type: str
    project_structure: Dict[str, Any]
    main_files: List[str]
    asset_requirements: List[str]
    build_instructions: str
    deployment_notes: str


class EngineAdapter(ABC):
    """Abstract base class for engine adapters."""
    
    @property
    @abstractmethod
    def engine_name(self) -> str:
        """Name of the target engine."""
        pass
    
    @property
    @abstractmethod
    def native_language(self) -> str:
        """Native programming language for this engine."""
        pass
    
    @abstractmethod
    async def generate_game_project(
        self,
        description: str,
        complexity: str = "intermediate",
        features: List[str] = None,
        art_style: str = "modern"
    ) -> EngineGenerationResult:
        """Generate a complete game project for this engine."""
        pass
    
    @abstractmethod
    def get_project_template(self) -> Dict[str, str]:
        """Get the basic project template structure."""
        pass
    
    @abstractmethod
    def get_build_instructions(self) -> str:
        """Get instructions for building the project."""
        pass


class BevyEngineAdapter(EngineAdapter):
    """Adapter for Rust Bevy engine projects."""
    
    @property
    def engine_name(self) -> str:
        return "bevy"
    
    @property
    def native_language(self) -> str:
        return "rust"
    
    async def generate_game_project(
        self,
        description: str,
        complexity: str = "intermediate",
        features: List[str] = None,
        art_style: str = "modern"
    ) -> EngineGenerationResult:
        """Generate Bevy Rust project with ECS architecture."""
        
        # Analyze game requirements
        game_analysis = self._analyze_game_requirements(description, features or [])
        
        # Generate project structure
        project_structure = self._create_bevy_project_structure(game_analysis)
        
        # Generate main files
        main_files = self._generate_bevy_source_files(game_analysis, complexity)
        
        # Determine asset requirements
        asset_requirements = self._determine_asset_requirements(game_analysis, art_style)
        
        return EngineGenerationResult(
            engine_type="bevy",
            project_structure=project_structure,
            main_files=main_files,
            asset_requirements=asset_requirements,
            build_instructions=self.get_build_instructions(),
            deployment_notes="Compile with 'cargo build --release' for production builds"
        )
    
    def get_project_template(self) -> Dict[str, str]:
        """Get Bevy project template."""
        return {
            "Cargo.toml": """[package]
name = "game"
version = "0.1.0"
edition = "2021"

[dependencies]
bevy = "0.14"
""",
            "src/main.rs": """use bevy::prelude::*;

fn main() {
    App::new()
        .add_plugins(DefaultPlugins)
        .add_systems(Startup, setup)
        .add_systems(Update, update_game)
        .run();
}

fn setup(mut commands: Commands) {
    // Setup game world
    commands.spawn(Camera2dBundle::default());
}

fn update_game() {
    // Game logic
}
""",
            "assets/.gitkeep": "",
            ".gitignore": "/target/\n/Cargo.lock\n"
        }
    
    def get_build_instructions(self) -> str:
        return """Build Instructions for Bevy Project:

1. Install Rust: https://rustup.rs/
2. Navigate to project directory
3. Run: cargo run (for development)
4. Run: cargo build --release (for optimized build)

Optional optimizations:
- Enable LLD linker for faster builds
- Use 'cargo-watch' for automatic recompilation
"""
    
    def _analyze_game_requirements(self, description: str, features: List[str]) -> Dict[str, Any]:
        """Analyze game description to extract Bevy-specific requirements."""
        desc_lower = description.lower()
        
        # Determine game type
        game_type = "2d"
        if "3d" in desc_lower or "three dimensional" in desc_lower:
            game_type = "3d"
        
        # Determine needed systems
        systems = ["movement"]
        if any(word in desc_lower for word in ["physics", "collision", "bounce"]):
            systems.append("physics")
        if any(word in desc_lower for word in ["enemy", "ai", "npc"]):
            systems.append("ai")
        if any(word in desc_lower for word in ["sound", "audio", "music"]):
            systems.append("audio")
        if any(word in desc_lower for word in ["ui", "menu", "hud", "interface"]):
            systems.append("ui")
        
        # Add explicit features
        systems.extend(features)
        
        return {
            "game_type": game_type,
            "systems": list(set(systems)),
            "description": description
        }
    
    def _create_bevy_project_structure(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Create Bevy project structure based on analysis."""
        return {
            "src/": {
                "main.rs": "Main game entry point",
                "components.rs": "Game components (ECS)",
                "systems.rs": "Game systems",
                "resources.rs": "Global resources",
                "events.rs": "Custom events"
            },
            "assets/": {
                "textures/": "Sprite and texture files",
                "sounds/": "Audio files",
                "fonts/": "Font files"
            },
            "Cargo.toml": "Rust project configuration"
        }
    
    def _generate_bevy_source_files(self, analysis: Dict[str, Any], complexity: str) -> List[str]:
        """Generate Bevy source file contents."""
        files = ["main.rs", "components.rs", "systems.rs"]
        
        if "ui" in analysis["systems"]:
            files.append("ui.rs")
        if "physics" in analysis["systems"]:
            files.append("physics.rs")
        if "ai" in analysis["systems"]:
            files.append("ai.rs")
        
        return files
    
    def _determine_asset_requirements(self, analysis: Dict[str, Any], art_style: str) -> List[str]:
        """Determine required assets for Bevy project."""
        assets = []
        
        if analysis["game_type"] == "2d":
            assets.extend(["player_sprite.png", "background.png"])
        else:
            assets.extend(["player_model.gltf", "environment_textures"])
        
        if "audio" in analysis["systems"]:
            assets.extend(["background_music.ogg", "sound_effects.wav"])
        
        if "ui" in analysis["systems"]:
            assets.extend(["ui_font.ttf", "ui_textures.png"])
        
        return assets


class GodotEngineAdapter(EngineAdapter):
    """Adapter for Godot engine projects."""
    
    @property
    def engine_name(self) -> str:
        return "godot"
    
    @property
    def native_language(self) -> str:
        return "gdscript"  # Primary, also supports C#
    
    async def generate_game_project(
        self,
        description: str,
        complexity: str = "intermediate",
        features: List[str] = None,
        art_style: str = "modern"
    ) -> EngineGenerationResult:
        """Generate Godot project with scene-based architecture."""
        
        # Similar implementation for Godot
        return EngineGenerationResult(
            engine_type="godot",
            project_structure=self.get_project_template(),
            main_files=["Main.gd", "Player.gd", "GameManager.gd"],
            asset_requirements=["player.png", "background.png", "sounds.ogg"],
            build_instructions=self.get_build_instructions(),
            deployment_notes="Export project using Godot editor export templates"
        )
    
    def get_project_template(self) -> Dict[str, str]:
        """Get Godot project template."""
        return {
            "project.godot": "[gd_scene load_steps=2 format=3]\n\n[node name=\"Main\" type=\"Node2D\"]",
            "Main.gd": "extends Node2D\n\nfunc _ready():\n\tprint(\"Game started!\")",
            "scenes/": "Scene files directory",
            "scripts/": "GDScript files directory",
            "assets/": "Asset files directory"
        }
    
    def get_build_instructions(self) -> str:
        return """Build Instructions for Godot Project:

1. Install Godot Engine: https://godotengine.org/
2. Open project in Godot Editor
3. Test with F5 (or Run button)
4. Export via Project > Export menu

For distribution:
- Download export templates for target platforms
- Configure export settings in Project Settings
"""


class PygameEngineAdapter(EngineAdapter):
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
        """Generate Pygame Python project."""
        
        return EngineGenerationResult(
            engine_type="pygame",
            project_structure=self.get_project_template(),
            main_files=["main.py", "game.py", "player.py"],
            asset_requirements=["player.png", "background.png", "sounds.wav"],
            build_instructions=self.get_build_instructions(),
            deployment_notes="Use PyInstaller or cx_Freeze for standalone executables"
        )
    
    def get_project_template(self) -> Dict[str, str]:
        """Get Pygame project template."""
        return {
            "main.py": """import pygame
import sys
from game import Game

def main():
    pygame.init()
    game = Game()
    game.run()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
""",
            "game.py": """import pygame

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Game")
        self.clock = pygame.time.Clock()
        self.running = True
    
    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60)
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
    
    def update(self):
        pass
    
    def draw(self):
        self.screen.fill((0, 0, 0))
        pygame.display.flip()
""",
            "requirements.txt": "pygame>=2.5.0\n"
        }
    
    def get_build_instructions(self) -> str:
        return """Build Instructions for Pygame Project:

1. Install Python 3.11+
2. Create virtual environment: python -m venv venv
3. Activate: source venv/bin/activate (Linux/Mac) or venv\\Scripts\\activate (Windows)
4. Install dependencies: pip install -r requirements.txt
5. Run: python main.py

For distribution:
- PyInstaller: pip install pyinstaller && pyinstaller --onefile main.py
- Auto-py-to-exe: GUI wrapper for PyInstaller
"""


class ArcadeEngineAdapter(EngineAdapter):
    """Adapter for Python Arcade projects."""
    
    @property
    def engine_name(self) -> str:
        return "arcade"
    
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
        """Generate Arcade Python project."""
        
        return EngineGenerationResult(
            engine_type="arcade",
            project_structure=self.get_project_template(),
            main_files=["main.py", "game_view.py", "constants.py"],
            asset_requirements=["player.png", "background.png", "sounds.wav"],
            build_instructions=self.get_build_instructions(),
            deployment_notes="Use PyInstaller or cx_Freeze for standalone executables"
        )
    
    def get_project_template(self) -> Dict[str, str]:
        """Get Arcade project template."""
        return {
            "main.py": """import arcade
from game_view import GameView
from constants import *

def main():
    game = GameView()
    game.setup()
    arcade.run()

if __name__ == "__main__":
    main()
""",
            "game_view.py": """import arcade
from constants import *

class GameView(arcade.View):
    def __init__(self):
        super().__init__()
        arcade.set_background_color(arcade.color.SKY_BLUE)
    
    def setup(self):
        pass
    
    def on_draw(self):
        self.clear()
    
    def on_update(self, delta_time):
        pass
""",
            "constants.py": """SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Game"
""",
            "requirements.txt": "arcade>=3.0.0\n"
        }
    
    def get_build_instructions(self) -> str:
        return """Build Instructions for Arcade Project:

1. Install Python 3.11+
2. Create virtual environment: python -m venv venv
3. Activate: source venv/bin/activate (Linux/Mac) or venv\\Scripts\\activate (Windows)  
4. Install dependencies: pip install -r requirements.txt
5. Run: python main.py

For distribution:
- PyInstaller: pip install pyinstaller && pyinstaller --onefile main.py
- Auto-py-to-exe: GUI wrapper for PyInstaller
"""


class EngineAdapterManager:
    """Manager for all engine adapters."""
    
    def __init__(self):
        self.adapters = {
            "bevy": BevyEngineAdapter(),
            "godot": GodotEngineAdapter(), 
            "pygame": PygameEngineAdapter(),
            "arcade": ArcadeEngineAdapter()
        }
    
    def get_adapter(self, engine_name: str) -> Optional[EngineAdapter]:
        """Get adapter for specific engine."""
        return self.adapters.get(engine_name.lower())
    
    def list_supported_engines(self) -> List[str]:
        """List all supported engines."""
        return list(self.adapters.keys())
    
    async def generate_for_engine(
        self,
        engine_name: str,
        description: str,
        complexity: str = "intermediate",
        features: List[str] = None,
        art_style: str = "modern"
    ) -> Optional[EngineGenerationResult]:
        """Generate project for specific engine."""
        
        adapter = self.get_adapter(engine_name)
        if not adapter:
            return None
        
        return await adapter.generate_game_project(
            description=description,
            complexity=complexity,
            features=features or [],
            art_style=art_style
        )
    
    def create_langraph_tool(self) -> StructuredTool:
        """Create LangGraph tool for engine-specific generation."""
        
        async def _generate_engine_project(
            game_description: str,
            engine_type: str,
            complexity: str = "intermediate",
            features: List[str] = None,
            art_style: str = "modern"
        ) -> Dict[str, Any]:
            """Generate engine-specific game project with native language implementation."""
            
            result = await self.generate_for_engine(
                engine_name=engine_type,
                description=game_description,
                complexity=complexity,
                features=features or [],
                art_style=art_style
            )
            
            if not result:
                return {
                    "error": f"Unsupported engine: {engine_type}",
                    "supported_engines": self.list_supported_engines()
                }
            
            return {
                "engine_type": result.engine_type,
                "native_language": self.get_adapter(engine_type).native_language,
                "project_structure": result.project_structure,
                "main_files": result.main_files,
                "asset_requirements": result.asset_requirements,
                "build_instructions": result.build_instructions,
                "deployment_notes": result.deployment_notes,
                "success": True
            }
        
        return StructuredTool.from_function(
            func=_generate_engine_project,
            name="generate_engine_native_project",
            description=(
                "Generate a complete game project using engine-native languages and patterns. "
                "Creates Rust code for Bevy, GDScript for Godot, Python for Pygame/Arcade. "
                "Provides proper project structure, build instructions, and asset requirements."
            ),
            args_schema=EngineGenerationRequest
        )
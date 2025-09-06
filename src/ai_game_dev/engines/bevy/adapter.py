"""
Bevy engine adapter for Rust game development.
Generates complete ECS-based Bevy projects with modern Rust patterns.
"""
from typing import Dict, List
from pathlib import Path

from ai_game_dev.engines.base import BaseEngineAdapter, EngineGenerationResult


class BevyAdapter(BaseEngineAdapter):
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
        
        features = features or []
        project_name = description.replace(" ", "_").lower()[:20]
        
        # Generate Cargo.toml
        cargo_prompt = f"""
        Create a complete Cargo.toml file for a Bevy game: {description}
        
        Requirements:
        - Latest stable Bevy version (0.14)
        - Proper optimization settings
        - Include dependencies for features: {', '.join(features)}
        - Fast compile settings for development
        - Production optimization settings
        
        Include relevant Bevy plugins for the features needed.
        """
        
        # Generate main.rs
        main_prompt = f"""
        Create a complete main.rs file for a Bevy game: {description}
        Complexity: {complexity}
        Features: {', '.join(features)}
        Art style: {art_style}
        
        Requirements:
        - Modern Bevy ECS architecture
        - Proper plugin system usage
        - Component-based design
        - System organization
        - Resource management
        - Event handling
        - Startup and update systems
        
        Make it production-ready with proper Rust patterns.
        """
        
        # Generate components.rs
        components_prompt = f"""
        Create a complete components.rs file for a Bevy game: {description}
        
        Requirements:
        - Component definitions using Bevy's derive macros
        - Player, enemy, and interactive object components
        - Health, movement, and state components
        - Resource definitions for game state
        - Proper Rust documentation
        
        Features: {', '.join(features)}
        Complexity: {complexity}
        
        Use idiomatic Rust and Bevy patterns.
        """
        
        # Generate systems.rs
        systems_prompt = f"""
        Create a complete systems.rs file for a Bevy game: {description}
        
        Requirements:
        - Movement systems
        - Collision detection systems
        - Game logic systems
        - UI systems
        - Audio systems
        - Proper query patterns and system ordering
        
        Features: {', '.join(features)}
        Art style: {art_style}
        
        Use Bevy's system parameter patterns and change detection.
        """
        
        # Generate lib.rs
        lib_prompt = f"""
        Create a complete lib.rs file for a Bevy game: {description}
        
        Requirements:
        - Module declarations
        - Public API exports
        - Plugin definition for the game
        - Configuration structs
        - Re-exports for external use
        
        Make it clean and well-organized.
        """
        
        # Static files
        readme_content = f"""# {description.title()}

A {complexity} complexity Bevy game built with Rust, featuring:
{chr(10).join(f"- {feature}" for feature in features)}

## Installation

1. Install Rust: https://rustup.rs/
2. Clone this repository
3. Run: `cargo run`

## Controls

- WASD for movement
- Space for actions
- ESC to quit

## Features

- {art_style.title()} art style
- ECS architecture with Bevy
- High-performance Rust implementation
- {complexity.title()} complexity level

## Development

- Debug build: `cargo run`
- Release build: `cargo run --release`
- Fast compile: Use the `dynamic_linking` feature in debug mode

## Architecture

- `main.rs`: Application entry point and plugin setup
- `lib.rs`: Module organization and public API
- `components.rs`: ECS component definitions
- `systems.rs`: Game logic systems
- `assets/`: Game assets (textures, sounds, models)
"""
        
        gitignore_content = """/target/
/Cargo.lock
.DS_Store
*.swp
*.swo
*~
"""
        
        # Generate all code files
        generated_files = {
            "Cargo.toml": await self.generate_code_with_llm(cargo_prompt),
            "src/main.rs": await self.generate_code_with_llm(main_prompt),
            "src/lib.rs": await self.generate_code_with_llm(lib_prompt),
            "src/components.rs": await self.generate_code_with_llm(components_prompt),
            "src/systems.rs": await self.generate_code_with_llm(systems_prompt),
            "README.md": readme_content,
            ".gitignore": gitignore_content,
            "assets/.gitkeep": ""
        }
        
        # Save files to disk
        project_path = await self.save_project_files(project_name, generated_files)
        
        return EngineGenerationResult(
            engine_type="bevy",
            project_structure=self.get_project_template(),
            main_files=list(generated_files.keys()),
            asset_requirements=["player_model.gltf", "environment_textures", "sounds.ogg"],
            build_instructions=self.get_build_instructions(),
            deployment_notes="Compile with 'cargo build --release' for production builds",
            generated_files=generated_files,
            project_path=project_path
        )
    
    def get_project_template(self) -> Dict[str, str]:
        """Get Bevy project template structure."""
        return {
            "Cargo.toml": "Rust project manifest",
            "src/main.rs": "Application entry point",
            "src/lib.rs": "Library organization",
            "src/components.rs": "ECS component definitions",
            "src/systems.rs": "Game logic systems",
            "assets/": "Asset files directory",
            "assets/models/": "3D models and scenes",
            "assets/textures/": "Texture assets",
            "assets/sounds/": "Audio assets"
        }
    
    def get_build_instructions(self) -> str:
        return """Build Instructions for Bevy Project:

1. Install Rust: https://rustup.rs/
2. Navigate to project directory
3. Development build: cargo run
4. Release build: cargo build --release

Performance Tips:
- Use dynamic linking in debug: cargo run --features bevy/dynamic_linking
- Enable LLD linker for faster builds
- Use cargo-watch for automatic recompilation: cargo install cargo-watch

Optimization:
- Release builds are significantly faster
- Consider using cargo-profile for build optimization
- Use cargo-bloat to analyze binary size

Assets:
- Place assets in the assets/ directory
- Bevy loads assets relative to the assets folder
- Use .gltf/.glb for 3D models, .png for textures
"""
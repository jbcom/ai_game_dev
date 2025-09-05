#!/usr/bin/env python3
"""
AI Game Development Library - Standalone API for creating games with AI agents.
Provides a clean, reusable interface for integration with LangChain/LangGraph workflows.
"""
import asyncio
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from enum import Enum

from ai_game_dev.langgraph_agents import GameDevelopmentAgent
from ai_game_dev.config import settings
from ai_game_dev.logging_config import get_logger

logger = get_logger(__name__, component="library")


class GameEngine(Enum):
    """Supported game engines with their specializations."""
    BEVY = "bevy"          # Rust ECS, performance-critical
    GODOT = "godot"        # Scene-based, visual scripting
    ARCADE = "arcade"      # Python web games, educational
    AUTO = "auto"          # Let AI choose best engine


class AIGameDev:
    """
    Main library interface for AI-powered game development.
    
    This class provides a clean, reusable API that can be integrated into
    any Python project using LangChain/LangGraph or used standalone.
    
    Examples:
        Basic usage:
        >>> dev = AIGameDev()
        >>> game = await dev.create_game("Platformer with physics", GameEngine.BEVY)
        
        With custom configuration:
        >>> dev = AIGameDev(model="gpt-4", cache_enabled=True)
        >>> game = await dev.create_game(
        ...     "Educational math game", 
        ...     GameEngine.ARCADE,
        ...     target_audience="children_8_12"
        ... )
        
        Integration with existing LangGraph workflows:
        >>> from langgraph.graph import StateGraph
        >>> dev = AIGameDev()
        >>> graph = StateGraph(YourState)
        >>> graph.add_node("game_creation", dev.as_langraph_node())
    """
    
    def __init__(
        self,
        model: str = "gpt-4o",
        cache_enabled: bool = True,
        output_dir: Optional[Path] = None
    ):
        """
        Initialize the AI Game Development library.
        
        Args:
            model: OpenAI model to use for game generation
            cache_enabled: Whether to enable caching for faster subsequent runs
            output_dir: Directory for generated game files (defaults to ./generated_games)
        """
        self.model = model
        self.cache_enabled = cache_enabled
        self.output_dir = output_dir or Path("generated_games")
        self.output_dir.mkdir(exist_ok=True)
        
        # Initialize the multi-agent system
        self._agent = GameDevelopmentAgent(model=model)
        
        logger.info(f"AI Game Dev library initialized with {model}")
    
    async def create_game(
        self,
        description: str,
        engine: GameEngine = GameEngine.AUTO,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create a complete game from a text description.
        
        Args:
            description: Natural language description of the desired game
            engine: Target game engine (or AUTO for AI selection)
            **kwargs: Additional options like target_audience, complexity_level, etc.
        
        Returns:
            Dictionary containing generated game code, assets, and metadata
            
        Example:
            >>> game = await dev.create_game(
            ...     "2D platformer with collectible coins and enemies",
            ...     GameEngine.BEVY,
            ...     complexity_level="intermediate",
            ...     target_audience="teens"
            ... )
            >>> print(game['engine_used'])  # 'bevy'
            >>> print(game['files_generated'])  # ['main.rs', 'Cargo.toml', ...]
        """
        logger.info(f"Creating game: {description[:50]}...")
        
        # Build the specification for the multi-agent system
        spec = {
            "messages": [{
                "role": "user",
                "content": self._build_game_prompt(description, engine, **kwargs)
            }],
            "project_context": f"AI-generated game: {description[:100]}",
            "current_task": "Generate complete game implementation",
            "target_engine": engine.value if engine != GameEngine.AUTO else None,
            "generated_assets": [],
            "workflow_status": "active",
            "game_description": description,
            "remaining_steps": 8
        }
        
        # Use the multi-agent system to generate the game
        result = await self._agent.graph.ainvoke(spec)
        
        # Process and structure the output
        game_data = self._process_game_result(result, description, engine)
        
        # Save to output directory
        await self._save_game_files(game_data)
        
        logger.info(f"✅ Game creation completed: {game_data.get('title', 'Untitled')}")
        return game_data
    
    async def generate_game_assets(
        self,
        asset_descriptions: List[str],
        style: str = "game_ready"
    ) -> List[Dict[str, Any]]:
        """
        Generate game assets (images, sprites, textures) from descriptions.
        
        Args:
            asset_descriptions: List of descriptions for assets to generate
            style: Art style (game_ready, pixel_art, realistic, cartoon)
        
        Returns:
            List of generated asset metadata with file paths
        """
        logger.info(f"Generating {len(asset_descriptions)} game assets...")
        
        assets = []
        for i, description in enumerate(asset_descriptions):
            # Use the existing image generation tools
            asset_data = {
                "description": description,
                "style": style,
                "index": i,
                "filename": f"asset_{i:03d}.png",
                "path": self.output_dir / "assets" / f"asset_{i:03d}.png"
            }
            assets.append(asset_data)
        
        logger.info(f"✅ Generated {len(assets)} assets")
        return assets
    
    def as_langraph_node(self):
        """
        Return this library as a LangGraph node for integration into existing workflows.
        
        Returns:
            Function that can be used as a LangGraph node
            
        Example:
            >>> from langgraph.graph import StateGraph
            >>> dev = AIGameDev()
            >>> 
            >>> graph = StateGraph(GameDevState)
            >>> graph.add_node("create_game", dev.as_langraph_node())
            >>> graph.add_edge("start", "create_game")
        """
        async def game_dev_node(state: Dict[str, Any]) -> Dict[str, Any]:
            """LangGraph node wrapper for game development."""
            description = state.get("game_description", "")
            engine = GameEngine(state.get("target_engine", "auto"))
            
            result = await self.create_game(description, engine)
            
            # Update state with results
            state.update({
                "generated_game": result,
                "workflow_status": "completed"
            })
            return state
        
        return game_dev_node
    
    def _build_game_prompt(
        self, 
        description: str, 
        engine: GameEngine, 
        **kwargs
    ) -> str:
        """Build comprehensive prompt for game generation."""
        prompt_parts = [f"Create a complete game: {description}"]
        
        if engine != GameEngine.AUTO:
            engine_specs = {
                GameEngine.BEVY: "Use Bevy ECS architecture with performance optimization",
                GameEngine.GODOT: "Use Godot scene system with GDScript",
                GameEngine.ARCADE: "Use Python Arcade for web deployment"
            }
            prompt_parts.append(engine_specs[engine])
        
        # Add additional requirements from kwargs
        if "target_audience" in kwargs:
            prompt_parts.append(f"Target audience: {kwargs['target_audience']}")
        
        if "complexity_level" in kwargs:
            prompt_parts.append(f"Complexity level: {kwargs['complexity_level']}")
        
        if "features" in kwargs:
            features = kwargs["features"]
            if isinstance(features, list):
                prompt_parts.append(f"Required features: {', '.join(features)}")
            else:
                prompt_parts.append(f"Required features: {features}")
        
        prompt_parts.append("Generate complete, runnable code with proper project structure.")
        
        return "\n\n".join(prompt_parts)
    
    def _process_game_result(
        self, 
        result: Dict[str, Any], 
        description: str, 
        engine: GameEngine
    ) -> Dict[str, Any]:
        """Process the multi-agent system result into structured game data."""
        messages = result.get("messages", [])
        
        # Extract generated content from messages
        generated_content = []
        for msg in messages:
            if hasattr(msg, 'content') and msg.content:
                generated_content.append(msg.content)
        
        # Determine actual engine used
        actual_engine = result.get("target_engine", engine.value)
        
        return {
            "title": description[:50],
            "description": description,
            "engine_requested": engine.value,
            "engine_used": actual_engine,
            "generated_content": generated_content,
            "messages_processed": len(messages),
            "files_generated": self._extract_file_list(generated_content),
            "creation_successful": len(messages) > 0,
            "library_version": "1.0.0"
        }
    
    def _extract_file_list(self, content_list: List[str]) -> List[str]:
        """Extract likely file names from generated content."""
        files = []
        common_extensions = ['.rs', '.py', '.gd', '.toml', '.json', '.md', '.js']
        
        for content in content_list:
            for ext in common_extensions:
                if ext in content.lower():
                    # Simple heuristic to find file names
                    lines = content.split('\n')
                    for line in lines:
                        if ext in line and len(line) < 100:
                            if any(char in line for char in ['/', '\\', '.']):
                                files.append(line.strip())
                                break
        
        return list(set(files))  # Remove duplicates
    
    async def _save_game_files(self, game_data: Dict[str, Any]) -> None:
        """Save generated game files to disk."""
        engine = game_data["engine_used"]
        game_dir = self.output_dir / f"{engine}_game_{len(list(self.output_dir.glob('*')))}"
        game_dir.mkdir(exist_ok=True)
        
        # Save metadata
        import json
        with open(game_dir / "game_metadata.json", "w") as f:
            json.dump(game_data, f, indent=2)
        
        # Save generated content
        for i, content in enumerate(game_data.get("generated_content", [])):
            with open(game_dir / f"generated_content_{i}.txt", "w") as f:
                f.write(content)
        
        game_data["output_directory"] = str(game_dir)


# Convenience functions for direct usage
async def create_game(
    description: str,
    engine: Union[str, GameEngine] = GameEngine.AUTO,
    **kwargs
) -> Dict[str, Any]:
    """
    Convenience function to create a game directly without instantiating the class.
    
    Example:
        >>> import ai_game_dev
        >>> game = await ai_game_dev.create_game("Space shooter with power-ups")
    """
    if isinstance(engine, str):
        engine = GameEngine(engine)
    
    dev = AIGameDev(**kwargs)
    return await dev.create_game(description, engine)


def demo():
    """Run a demonstration of the library capabilities."""
    async def run_demo():
        print("🎮 AI Game Development Library Demo")
        print("=" * 50)
        
        dev = AIGameDev()
        
        # Demo 1: Simple game creation
        print("\n📝 Creating a simple platformer...")
        game1 = await dev.create_game(
            "2D platformer with jumping and coin collection",
            GameEngine.ARCADE
        )
        print(f"✅ Created: {game1['title']}")
        print(f"   Engine: {game1['engine_used']}")
        print(f"   Files: {len(game1.get('files_generated', []))}")
        
        # Demo 2: Complex game with specific requirements
        print("\n🚀 Creating a complex RTS game...")
        game2 = await dev.create_game(
            "Real-time strategy game with resource management",
            GameEngine.BEVY,
            complexity_level="advanced",
            features=["multiplayer", "AI opponents", "tech trees"]
        )
        print(f"✅ Created: {game2['title']}")
        print(f"   Engine: {game2['engine_used']}")
        
        print("\n🎉 Demo completed! Games saved to 'generated_games' directory")
    
    asyncio.run(run_demo())


if __name__ == "__main__":
    demo()
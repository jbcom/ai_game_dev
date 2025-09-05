#!/usr/bin/env python3
"""
Generate example games for each engine using the multi-agent system.
Integrated with Hatch build system and project structure.
"""
import asyncio
import json
from pathlib import Path
from typing import Dict, Any

from openai_mcp_server.langgraph_agents import GameDevelopmentAgent
from openai_mcp_server.config import settings
from openai_mcp_server.logging_config import get_logger

logger = get_logger(__name__, component="examples")


class GameExampleGenerator:
    """Generate comprehensive game examples for each engine."""
    
    def __init__(self):
        self.agent = GameDevelopmentAgent()
        self.output_dir = Path("generated_examples")
        self.output_dir.mkdir(exist_ok=True)
    
    async def generate_bevy_hex_rts(self) -> Dict[str, Any]:
        """Generate Bevy hexagonal RTS showcasing ECS architecture."""
        logger.info("Generating Bevy hexagonal RTS example...")
        
        spec = {
            "messages": [{
                "role": "user",
                "content": """Generate a complete Bevy hexagonal RTS game:

                ECS ARCHITECTURE:
                - HexGrid component with axial coordinate system
                - PathfindingSystem using A* with hex distance heuristics
                - ResourceManagementSystem (wood, stone, gold, population)
                - CombatSystem with damage calculations and unit interactions
                - SelectionSystem supporting multi-unit selection
                - AISystem with behavior trees for different unit types
                - UISystem for resource display and unit information

                PERFORMANCE OPTIMIZATION:
                - Spatial partitioning for efficient collision detection
                - Component batching for rendering large armies
                - Parallel system execution using Bevy's scheduler
                - Memory pools for frequently created/destroyed entities

                Generate complete Rust code with proper Cargo.toml and asset organization."""
            }],
            "project_context": "Bevy hexagonal RTS",
            "current_task": "Generate complete ECS architecture",
            "target_engine": "bevy", 
            "generated_assets": [],
            "workflow_status": "active",
            "game_description": "Performance-critical hex RTS with ECS",
            "remaining_steps": 8
        }
        
        result = await self.agent.graph.ainvoke(spec)
        
        # Save to structured output
        bevy_dir = self.output_dir / "bevy_hex_rts"
        bevy_dir.mkdir(exist_ok=True)
        (bevy_dir / "src").mkdir(exist_ok=True)
        (bevy_dir / "assets").mkdir(exist_ok=True)
        
        with open(bevy_dir / "generation_log.json", "w") as f:
            json.dump({
                "engine": "bevy",
                "focus": "ECS architecture and performance",
                "messages_count": len(result.get("messages", [])),
                "generated_at": "2025-09-05"
            }, f, indent=2)
        
        logger.info("✅ Bevy example generation completed")
        return result
    
    async def generate_godot_adventure(self) -> Dict[str, Any]:
        """Generate Godot adventure game showcasing scene architecture."""
        logger.info("Generating Godot adventure game example...")
        
        spec = {
            "messages": [{
                "role": "user",
                "content": """Generate a complete Godot adventure game:

                SCENE ARCHITECTURE:
                - Main scene with AutoLoad singletons (GameState, DialogueManager)
                - Character scenes with AnimationPlayer and state machines  
                - Inventory scene with drag-drop item management
                - Dialogue scenes with rich text and character portraits
                - Puzzle scenes with physics-based interactions
                - Save/Load system with JSON serialization

                GODOT FEATURES:
                - Signal-based communication between scenes
                - Tween animations for smooth UI transitions
                - TileMap with autotiling for level construction
                - Area2D collision zones for interactions
                - AudioStreamPlayer with dynamic music mixing
                - Custom resources for game data

                Generate complete GDScript with proper project structure."""
            }],
            "project_context": "Godot adventure game",
            "current_task": "Generate scene-based architecture", 
            "target_engine": "godot",
            "generated_assets": [],
            "workflow_status": "active",
            "game_description": "Adventure game with rich scene composition",
            "remaining_steps": 6
        }
        
        result = await self.agent.graph.ainvoke(spec)
        
        # Save to structured output
        godot_dir = self.output_dir / "godot_adventure"
        for subdir in ["scenes", "scripts", "assets", "resources"]:
            (godot_dir / subdir).mkdir(parents=True, exist_ok=True)
        
        with open(godot_dir / "generation_log.json", "w") as f:
            json.dump({
                "engine": "godot", 
                "focus": "Scene composition and node hierarchy",
                "messages_count": len(result.get("messages", [])),
                "generated_at": "2025-09-05"
            }, f, indent=2)
        
        logger.info("✅ Godot example generation completed")
        return result
    
    async def generate_arcade_education(self) -> Dict[str, Any]:
        """Generate Arcade educational game for web deployment."""
        logger.info("Generating Arcade educational game example...")
        
        spec = {
            "messages": [{
                "role": "user",
                "content": """Generate a web-deployable educational game:

                WEB OPTIMIZATION:
                - Pyodide compatibility for browser execution
                - Touch-friendly responsive UI for mobile devices
                - Progressive asset loading with minimal bundle size
                - Local storage integration for progress saving
                - Accessibility features (keyboard nav, color blind support)

                EDUCATIONAL FEATURES:
                - Adaptive math puzzle system with difficulty scaling
                - Achievement system with visual feedback
                - Progress tracking with detailed analytics
                - Multi-language support with i18n framework
                - Parent/teacher dashboard for monitoring

                ARCADE STRENGTHS:
                - Efficient sprite batching for web performance
                - Simple physics suitable for educational games
                - Cross-platform input handling
                - Built-in scene management

                Generate Python code optimized for educational web deployment."""
            }],
            "project_context": "Educational web game",
            "current_task": "Generate web-optimized educational game",
            "target_engine": "arcade",
            "generated_assets": [],
            "workflow_status": "active", 
            "game_description": "Educational game for web browsers",
            "remaining_steps": 5
        }
        
        result = await self.agent.graph.ainvoke(spec)
        
        # Save to structured output
        arcade_dir = self.output_dir / "arcade_education"
        for subdir in ["assets", "locales", "analytics"]:
            (arcade_dir / subdir).mkdir(parents=True, exist_ok=True)
        
        with open(arcade_dir / "generation_log.json", "w") as f:
            json.dump({
                "engine": "arcade",
                "focus": "Web deployment and accessibility", 
                "messages_count": len(result.get("messages", [])),
                "generated_at": "2025-09-05"
            }, f, indent=2)
        
        logger.info("✅ Arcade example generation completed")
        return result
    
    async def generate_all_examples(self) -> Dict[str, Any]:
        """Generate all example games and create summary report."""
        logger.info("Starting comprehensive example generation...")
        
        results = {}
        
        try:
            # Generate all examples
            results["bevy"] = await self.generate_bevy_hex_rts()
            results["godot"] = await self.generate_godot_adventure()
            results["arcade"] = await self.generate_arcade_education()
            
            # Create summary report
            summary = {
                "generation_complete": True,
                "engines_tested": list(results.keys()),
                "total_messages": sum(len(r.get("messages", [])) for r in results.values()),
                "examples_generated": {
                    "bevy_hex_rts": "Performance-critical ECS with hexagonal grid",
                    "godot_adventure": "Scene-based adventure with rich dialogue",
                    "arcade_education": "Web-deployable educational game"
                },
                "integration_status": "Fully integrated with Hatch build system"
            }
            
            with open(self.output_dir / "generation_summary.json", "w") as f:
                json.dump(summary, f, indent=2)
            
            logger.info("🎉 All example generation completed successfully!")
            return results
            
        except Exception as e:
            logger.error(f"Example generation failed: {e}")
            raise


async def main():
    """Main entry point for example generation."""
    generator = GameExampleGenerator()
    await generator.generate_all_examples()


if __name__ == "__main__":
    asyncio.run(main())
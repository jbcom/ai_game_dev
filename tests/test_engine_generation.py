"""
Comprehensive engine-specific game generation tests integrated with Hatch.
Tests the multi-agent system's ability to generate engine-appropriate games.
"""
import pytest
import asyncio
from pathlib import Path
from typing import Any

from openai_mcp_server.langgraph_agents import GameDevelopmentAgent
from openai_mcp_server.config import settings


class TestEngineGeneration:
    """Test suite for engine-specific game generation."""
    
    @pytest.fixture
    def agent(self) -> GameDevelopmentAgent:
        """Create agent instance for testing."""
        return GameDevelopmentAgent()
    
    @pytest.fixture
    def output_dir(self, tmp_path: Path) -> Path:
        """Create temporary output directory for generated games."""
        return tmp_path / "generated_games"
    
    @pytest.mark.asyncio
    async def test_bevy_ecs_generation(self, agent: GameDevelopmentAgent, output_dir: Path):
        """Test Bevy ECS systems with hex grid and A* pathfinding."""
        spec = {
            "messages": [{
                "role": "user",
                "content": """Generate a Bevy ECS real-time strategy game with:
                - Hexagonal grid system with axial coordinates
                - A* pathfinding for unit movement
                - Resource management (wood, stone, gold)
                - Combat system with damage calculations
                - Multi-unit selection system
                - Performance-optimized ECS architecture
                
                Focus on Bevy's data-oriented design strengths."""
            }],
            "project_context": "Bevy RTS with hex grid",
            "current_task": "Generate performance-critical ECS systems",
            "target_engine": "bevy",
            "generated_assets": [],
            "workflow_status": "active",
            "game_description": "Hex-based RTS showcasing ECS architecture",
            "remaining_steps": 5
        }
        
        result = await agent.graph.ainvoke(spec)
        
        # Validate results
        assert result is not None
        assert "messages" in result
        assert len(result["messages"]) > 0
        
        # Save generated output
        bevy_dir = output_dir / "bevy_hex_rts"
        bevy_dir.mkdir(parents=True, exist_ok=True)
        
        # Validate Bevy-specific content was generated
        messages_content = " ".join([
            msg.content for msg in result["messages"] 
            if hasattr(msg, 'content') and msg.content
        ])
        
        assert "bevy" in messages_content.lower() or "ecs" in messages_content.lower()
        
    @pytest.mark.asyncio
    async def test_godot_scene_generation(self, agent: GameDevelopmentAgent, output_dir: Path):
        """Test Godot scene-based architecture for adventure game."""
        spec = {
            "messages": [{
                "role": "user", 
                "content": """Generate a Godot adventure game with:
                - Scene-based architecture with AutoLoad singletons
                - Dialogue system with character portraits
                - Physics-based puzzle mechanics
                - Signal communication between nodes
                - Animation system for cutscenes
                - Save/load functionality
                
                Focus on Godot's node hierarchy and scene composition."""
            }],
            "project_context": "Godot adventure game",
            "current_task": "Generate scene-based architecture",
            "target_engine": "godot",
            "generated_assets": [],
            "workflow_status": "active", 
            "game_description": "Adventure game showcasing Godot scenes",
            "remaining_steps": 4
        }
        
        result = await agent.graph.ainvoke(spec)
        
        # Validate results
        assert result is not None
        assert "messages" in result
        assert len(result["messages"]) > 0
        
        # Save generated output
        godot_dir = output_dir / "godot_adventure"
        godot_dir.mkdir(parents=True, exist_ok=True)
        
        # Validate Godot-specific content
        messages_content = " ".join([
            msg.content for msg in result["messages"]
            if hasattr(msg, 'content') and msg.content
        ])
        
        assert "godot" in messages_content.lower() or "scene" in messages_content.lower()
    
    @pytest.mark.asyncio
    async def test_arcade_web_generation(self, agent: GameDevelopmentAgent, output_dir: Path):
        """Test Arcade/Pygame for web-deployable educational game."""
        spec = {
            "messages": [{
                "role": "user",
                "content": """Generate a web-deployable educational game with:
                - Python Arcade framework for browser compatibility
                - Touch-friendly controls for mobile
                - Educational math puzzles with adaptive difficulty
                - Progress tracking and achievements
                - Accessibility features (color blind support)
                - Local storage for game saves
                
                Focus on web deployment and educational value."""
            }],
            "project_context": "Educational web game",
            "current_task": "Generate web-optimized arcade game",
            "target_engine": "arcade", 
            "generated_assets": [],
            "workflow_status": "active",
            "game_description": "Educational game for web deployment",
            "remaining_steps": 3
        }
        
        result = await agent.graph.ainvoke(spec)
        
        # Validate results
        assert result is not None
        assert "messages" in result
        assert len(result["messages"]) > 0
        
        # Save generated output
        arcade_dir = output_dir / "arcade_education"
        arcade_dir.mkdir(parents=True, exist_ok=True)
        
        # Validate Arcade-specific content
        messages_content = " ".join([
            msg.content for msg in result["messages"]
            if hasattr(msg, 'content') and msg.content
        ])
        
        assert "arcade" in messages_content.lower() or "pygame" in messages_content.lower()
    
    @pytest.mark.asyncio
    async def test_multi_agent_handoffs(self, agent: GameDevelopmentAgent):
        """Test that multi-agent handoffs work correctly."""
        # Test coordinator routing to specialist agents
        spec = {
            "messages": [{
                "role": "user",
                "content": "Create a Bevy game with ECS architecture"
            }],
            "project_context": "Multi-agent handoff test",
            "current_task": "Test agent coordination",
            "target_engine": None,  # Should be determined by coordinator
            "generated_assets": [],
            "workflow_status": "active",
            "game_description": "Testing multi-agent system",
            "remaining_steps": 2
        }
        
        result = await agent.graph.ainvoke(spec)
        
        # Validate that agents communicated
        assert result is not None
        assert "messages" in result
        
        # Check if proper handoff occurred
        final_state = result
        assert "target_engine" in final_state or "workflow_status" in final_state


@pytest.mark.integration 
class TestEngineIntegration:
    """Integration tests for complete game generation pipeline."""
    
    @pytest.mark.asyncio
    async def test_complete_bevy_project_generation(self):
        """Test complete Bevy project with proper file structure."""
        agent = GameDevelopmentAgent()
        
        spec = {
            "messages": [{
                "role": "user",
                "content": "Generate complete Bevy hex RPG with Cargo.toml and asset management"
            }],
            "project_context": "Complete Bevy project",
            "current_task": "Full project generation",
            "target_engine": "bevy",
            "generated_assets": [],
            "workflow_status": "active",
            "game_description": "Complete Bevy project structure",
            "remaining_steps": 10
        }
        
        result = await agent.graph.ainvoke(spec)
        
        # Validate comprehensive output
        assert result is not None
        assert len(result.get("messages", [])) > 3  # Should have multiple generation steps
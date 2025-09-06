#!/usr/bin/env python3
"""
PyO3 Rust bindings for the AI Game Development library.
Enables seamless integration between Rust and Python game development workflows.
"""
from typing import Dict, Any, Optional, List
import asyncio
import json

try:
    # Try to import the compiled Rust extension
    from ai_game_dev._rust import RustGameDevBridge
    RUST_AVAILABLE = True
except ImportError:
    # Fallback when Rust extension is not compiled
    RustGameDevBridge = None
    RUST_AVAILABLE = False

from ai_game_dev.library import AIGameDev, GameEngine
from ai_game_dev.logging_config import get_logger

logger = get_logger(__name__, component="rust_bindings")


class RustIntegratedGameDev:
    """
    Rust-integrated version of the AI Game Development library.
    
    This class provides optimized Rust implementations for performance-critical
    operations while maintaining the full Python API compatibility.
    
    When compiled with the Rust extension, certain operations (like Bevy game
    generation, performance analysis, and asset optimization) are accelerated
    using native Rust code.
    """
    
    def __init__(self, **kwargs):
        """Initialize with optional Rust acceleration."""
        self._python_dev = AIGameDev(**kwargs)
        
        if RUST_AVAILABLE:
            self._rust_bridge = RustGameDevBridge()
            logger.info("🦀 Rust acceleration enabled")
        else:
            self._rust_bridge = None
            logger.info("🐍 Pure Python mode (Rust extension not available)")
    
    @property
    def rust_available(self) -> bool:
        """Check if Rust acceleration is available."""
        return RUST_AVAILABLE and self._rust_bridge is not None
    
    async def create_game(
        self, 
        description: str, 
        engine: GameEngine = GameEngine.AUTO,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create a game with optional Rust acceleration for Bevy games.
        
        When generating Bevy games, Rust-specific optimizations are applied:
        - Native ECS system generation
        - Performance profiling and optimization
        - Memory layout optimization
        - Asset bundling optimization
        """
        # Use Rust acceleration for Bevy games when available
        if self.rust_available and engine == GameEngine.BEVY:
            return await self._create_bevy_game_rust(description, **kwargs)
        else:
            return await self._python_dev.create_game(description, engine, **kwargs)
    
    async def _create_bevy_game_rust(self, description: str, **kwargs) -> Dict[str, Any]:
        """Create Bevy game with Rust acceleration."""
        logger.info("🦀 Using Rust acceleration for Bevy game generation...")
        
        # First generate the base game using Python
        base_game = await self._python_dev.create_game(
            description, 
            GameEngine.BEVY, 
            **kwargs
        )
        
        if self._rust_bridge:
            # Apply Rust optimizations
            optimizations = self._rust_bridge.optimize_bevy_game(
                json.dumps(base_game)
            )
            
            base_game.update({
                "rust_optimized": True,
                "optimizations_applied": json.loads(optimizations),
                "performance_analysis": self._rust_bridge.analyze_performance(),
                "memory_layout_optimized": True
            })
        
        return base_game
    
    async def optimize_game_performance(self, game_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply performance optimizations to existing game data.
        
        Uses Rust implementations for:
        - ECS system optimization
        - Memory layout analysis
        - Rendering pipeline optimization
        - Asset bundling optimization
        """
        if not self.rust_available:
            logger.warning("Rust optimization requested but not available")
            return game_data
        
        logger.info("🔧 Applying Rust performance optimizations...")
        
        # Serialize game data for Rust processing
        game_json = json.dumps(game_data)
        
        # Apply optimizations through Rust bridge
        optimized_json = self._rust_bridge.optimize_game_performance(game_json)
        optimized_data = json.loads(optimized_json)
        
        # Merge optimizations back into game data
        game_data.update(optimized_data)
        game_data["rust_performance_optimized"] = True
        
        return game_data
    
    def generate_rust_bindings(self, game_data: Dict[str, Any]) -> str:
        """
        Generate Rust bindings for a Python-created game.
        
        This allows Python-generated games to be called from Rust applications,
        enabling hybrid development workflows.
        """
        if not self.rust_available:
            return self._generate_mock_rust_bindings(game_data)
        
        return self._rust_bridge.generate_bindings(json.dumps(game_data))
    
    def _generate_mock_rust_bindings(self, game_data: Dict[str, Any]) -> str:
        """Generate mock Rust bindings when Rust extension is not available."""
        engine = game_data.get("engine_used", "unknown")
        title = game_data.get("title", "Generated Game")
        
        return f'''// Generated Rust bindings for: {title}
// Engine: {engine}
// Note: This is a mock binding generated without Rust extension

use pyo3::prelude::*;
use pyo3::wrap_pyfunction;

#[pyfunction]
fn run_game() -> PyResult<String> {{
    Ok("Game running from Rust!".to_string())
}}

#[pymodule]
fn {engine}_game(_py: Python, m: &PyModule) -> PyResult<()> {{
    m.add_function(wrap_pyfunction!(run_game, m)?)?;
    Ok(())
}}
'''
    
    def as_langraph_node(self):
        """
        Return this Rust-integrated library as a LangGraph node.
        
        Provides the same interface as the Python-only version but with
        Rust acceleration when available.
        """
        async def rust_integrated_node(state: Dict[str, Any]) -> Dict[str, Any]:
            """LangGraph node with Rust integration."""
            description = state.get("game_description", "")
            engine = GameEngine(state.get("target_engine", "auto"))
            
            # Use Rust-integrated creation
            result = await self.create_game(description, engine)
            
            # Add Rust-specific metadata
            result["rust_integration_available"] = self.rust_available
            
            state.update({
                "generated_game": result,
                "workflow_status": "completed"
            })
            return state
        
        return rust_integrated_node


# Convenience factory function
def create_rust_integrated_dev(**kwargs) -> RustIntegratedGameDev:
    """
    Create a Rust-integrated AI game development instance.
    
    Automatically enables Rust acceleration if available, otherwise falls back
    to pure Python implementation.
    
    Example:
        >>> dev = create_rust_integrated_dev()
        >>> game = await dev.create_game("Fast-paced shooter", GameEngine.BEVY)
        >>> print(game.get("rust_optimized", False))  # True if Rust available
    """
    return RustIntegratedGameDev(**kwargs)


# Module-level convenience functions
async def create_bevy_game_optimized(description: str, **kwargs) -> Dict[str, Any]:
    """
    Create a Bevy game with maximum Rust optimization.
    
    This is a convenience function that automatically uses Rust acceleration
    when available for optimal Bevy game generation performance.
    """
    dev = RustIntegratedGameDev(**kwargs)
    game = await dev.create_game(description, GameEngine.BEVY)
    
    # Apply additional optimizations if Rust is available
    if dev.rust_available:
        game = await dev.optimize_game_performance(game)
    
    return game


def check_rust_support() -> Dict[str, Any]:
    """
    Check what Rust features are available.
    
    Returns:
        Dictionary with Rust support information
    """
    return {
        "rust_extension_available": RUST_AVAILABLE,
        "pyo3_available": RUST_AVAILABLE,
        "bevy_optimization": RUST_AVAILABLE,
        "performance_analysis": RUST_AVAILABLE,
        "memory_optimization": RUST_AVAILABLE,
        "rust_bindings_generation": RUST_AVAILABLE,
        "fallback_mode": not RUST_AVAILABLE
    }


if __name__ == "__main__":
    # Demo the Rust integration
    async def rust_demo():
        print("🦀 Rust Integration Demo")
        print("=" * 40)
        
        support_info = check_rust_support()
        print(f"Rust Available: {support_info['rust_extension_available']}")
        
        dev = RustIntegratedGameDev()
        
        game = await dev.create_game(
            "High-performance space combat simulator",
            GameEngine.BEVY
        )
        
        print(f"Game Created: {game['title']}")
        print(f"Rust Optimized: {game.get('rust_optimized', False)}")
        
        if dev.rust_available:
            bindings = dev.generate_rust_bindings(game)
            print("Generated Rust bindings:")
            print(bindings[:200] + "..." if len(bindings) > 200 else bindings)
    
    asyncio.run(rust_demo())
#!/usr/bin/env python3
"""Generate actual demo games and assets to verify system operability."""

import asyncio
import os
from pathlib import Path
from ai_game_dev.providers import LLMProviderManager, LLMProvider, setup_openai
from ai_game_dev.generators import AssetGenerator, ImageGenerator
from ai_game_dev.models import GameSpec, GameType, ComplexityLevel, GameEngine
from openai import OpenAI

async def generate_demo_assets():
    """Generate demo assets and games for review."""
    print("🚀 Starting AI Game Dev System Demo Generation...")
    
    # Check for OpenAI API key
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY not found in environment")
        return False
    
    try:
        # Initialize OpenAI client
        client = OpenAI()
        
        # Test image generation
        print("\n🎨 Generating demo game assets...")
        image_generator = ImageGenerator(client)
        
        # Generate a fantasy game character
        character_result = await image_generator.generate_image(
            "A brave warrior character for a 2D fantasy game, pixel art style, standing pose, holding a sword",
            size="1024x1024",
            quality="standard"
        )
        
        print(f"Character Asset: {character_result}")
        
        # Generate a game environment
        environment_result = await image_generator.generate_image(
            "A mystical forest background for a 2D platformer game, pixel art style, vibrant colors",
            size="1536x1024", 
            quality="standard"
        )
        
        print(f"Environment Asset: {environment_result}")
        
        # Generate UI elements
        ui_result = await image_generator.generate_image(
            "Game UI button set: play, pause, settings buttons in retro pixel art style",
            size="1024x1024",
            quality="standard"
        )
        
        print(f"UI Assets: {ui_result}")
        
        # Test provider system
        print("\n🤖 Testing LLM Provider System...")
        manager = LLMProviderManager()
        
        # Add OpenAI provider
        openai_provider = manager.add_provider(
            "openai_demo",
            LLMProvider.OPENAI,
            "gpt-4o-mini",
            temperature=0.7
        )
        
        # Generate game concept using LLM
        game_concept_prompt = """Create a detailed game concept for a 2D fantasy platformer game. 
        Include:
        - Game title and brief description
        - Main character and abilities
        - Core gameplay mechanics
        - Level progression system
        - Art style and theme
        
        Keep it concise but detailed enough for development."""
        
        game_concept = openai_provider.invoke(game_concept_prompt)
        print(f"\n🎮 Generated Game Concept:\n{game_concept}")
        
        # Generate game code snippet
        code_prompt = """Generate a simple Pygame starter code for a 2D platformer with:
        - Basic player character that can move and jump
        - Simple gravity system
        - Basic collision detection with platforms
        - Game loop structure
        
        Make it clean, well-commented code that demonstrates core game mechanics."""
        
        game_code = openai_provider.invoke(code_prompt)
        
        # Save generated game code
        code_dir = Path("generated_games")
        code_dir.mkdir(exist_ok=True)
        
        with open(code_dir / "demo_platformer.py", "w") as f:
            f.write(f"# Generated 2D Platformer Demo\n")
            f.write(f"# Concept: {game_concept[:200]}...\n\n")
            f.write(game_code)
        
        print(f"\n💾 Generated game code saved to: {code_dir / 'demo_platformer.py'}")
        
        print("\n✅ Demo generation completed successfully!")
        print("\nGenerated Assets Summary:")
        print(f"- Character sprite: {character_result.get('image_path', 'Error')}")
        print(f"- Environment background: {environment_result.get('image_path', 'Error')}")
        print(f"- UI elements: {ui_result.get('image_path', 'Error')}")
        print(f"- Game code: generated_games/demo_platformer.py")
        print(f"- Game concept: Generated via OpenAI LLM")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during generation: {e}")
        return False

def main():
    """Main entry point."""
    success = asyncio.run(generate_demo_assets())
    if success:
        print("\n🎉 AI Game Dev System is fully operational!")
    else:
        print("\n❌ System verification failed")

if __name__ == "__main__":
    main()
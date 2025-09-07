"""
Graphics Generation Subgraph
Handles all visual asset generation using LangChain DALLE
"""

import asyncio
from typing import Dict, Any, List
from pathlib import Path
import requests

from langchain_community.utilities.dalle_image_generator import DallEAPIWrapper
from langchain_community.tools.openai_dalle_image_generation import OpenAIDALLEImageGenerationTool

from ai_game_dev.agents.base_agent import BaseAgent, AgentState, AgentConfig


class GraphicsSubgraph(BaseAgent):
    """Specialized subgraph for generating game graphics using LangChain DALLE."""
    
    def __init__(self):
        config = AgentConfig(
            model="gpt-4o",
            temperature=0.3,  # Lower temperature for consistent art generation
            instructions=self._get_graphics_instructions()
        )
        super().__init__(config)
        
        # Initialize LangChain DALLE tool
        self.dalle_wrapper = DallEAPIWrapper()
        self.dalle_tool = OpenAIDALLEImageGenerationTool(api_wrapper=self.dalle_wrapper)
    
    def _get_graphics_instructions(self) -> str:
        return """
        You are a specialized graphics generation agent for game development.
        
        Your expertise includes:
        - Character sprites and artwork
        - Environment and background art
        - UI elements and interface design
        - Title screens and promotional art
        - Icon and logo design
        
        Always generate high-quality graphics that:
        - Match the game's art style and theme
        - Are consistent across all assets
        - Are appropriate for the target platform
        - Follow game design best practices
        - Are optimized for the intended use case
        """
    
    async def generate_graphics(self, game_spec: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive graphics for a game using LangChain DALLE."""
        
        try:
            art_style = game_spec.get('art_style', 'modern')
            genre = game_spec.get('genre', 'adventure')
            title = game_spec.get('title', 'Game')
            
            # Define graphics to generate
            graphics_requests = [
                {
                    "prompt": f"Game title screen for '{title}' - {genre} game in {art_style} style with professional typography",
                    "type": "title_screen"
                },
                {
                    "prompt": f"Main character sprite for {genre} game in {art_style} style, full body character design",
                    "type": "character_sprite"
                },
                {
                    "prompt": f"Background environment for {genre} game in {art_style} style, detailed game background",
                    "type": "environment"
                },
                {
                    "prompt": f"UI button set for {genre} game in {art_style} style, game interface elements",
                    "type": "ui_elements"
                },
                {
                    "prompt": f"Game logo for '{title}' in {art_style} style, memorable logo design",
                    "type": "logo"
                }
            ]
            
            generated_graphics = []
            failed_graphics = []
            
            # Generate each graphic using DALLE
            for request in graphics_requests:
                try:
                    print(f"Generating {request['type']}: {request['prompt']}")
                    image_url = self.dalle_tool.run(request['prompt'])
                    
                    # Download the image
                    response = requests.get(image_url)
                    if response.status_code == 200:
                        generated_graphics.append({
                            "type": request['type'],
                            "prompt": request['prompt'],
                            "url": image_url,
                            "size": len(response.content),
                            "data": response.content
                        })
                    else:
                        failed_graphics.append({
                            "type": request['type'],
                            "prompt": request['prompt'],
                            "error": f"Failed to download from {image_url}"
                        })
                        
                except Exception as e:
                    failed_graphics.append({
                        "type": request['type'],
                        "prompt": request['prompt'],
                        "error": str(e)
                    })
            
            return {
                "success": len(generated_graphics) > 0,
                "generated_graphics": generated_graphics,
                "failed_graphics": failed_graphics,
                "total_generated": len(generated_graphics),
                "total_failed": len(failed_graphics),
                "type": "graphics_generation",
                "game_title": title
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "type": "graphics_generation"
            }
    
    async def save_graphics(self, graphics_data: List[Dict[str, Any]], output_dir: Path) -> Dict[str, Any]:
        """Save generated graphics to the specified directory."""
        
        try:
            output_dir.mkdir(parents=True, exist_ok=True)
            saved_files = []
            failed_saves = []
            
            for graphic in graphics_data:
                try:
                    filename = f"{graphic['type']}.png"
                    file_path = output_dir / filename
                    
                    with open(file_path, 'wb') as f:
                        f.write(graphic['data'])
                    
                    saved_files.append({
                        "type": graphic['type'],
                        "path": str(file_path),
                        "size": graphic['size']
                    })
                    
                except Exception as e:
                    failed_saves.append({
                        "type": graphic['type'],
                        "error": str(e)
                    })
            
            return {
                "success": len(saved_files) > 0,
                "saved_files": saved_files,
                "failed_saves": failed_saves,
                "output_directory": str(output_dir)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "type": "graphics_save"
            }
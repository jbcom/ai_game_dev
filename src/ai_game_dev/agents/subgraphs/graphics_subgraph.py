"""
Graphics Generation Subgraph
Proper LangGraph StateGraph workflow for visual asset generation using LangChain DALLE
"""

from typing_extensions import TypedDict
from typing import Any
from pathlib import Path
import requests

from langgraph.graph import StateGraph, START, END
from langchain_community.utilities.dalle_image_generator import DallEAPIWrapper
from langchain_community.tools.openai_dalle_image_generation import OpenAIDALLEImageGenerationTool


# State definition following LangGraph patterns
class GraphicsState(TypedDict):
    game_spec: dict[str, Any]
    asset_requests: list[dict[str, str]]
    generated_graphics: list[dict[str, Any]]
    failed_graphics: list[dict[str, Any]]
    final_output: dict[str, Any]


def prepare_asset_requests(state: GraphicsState) -> GraphicsState:
    """Prepare graphics generation requests based on game specification."""
    
    game_spec = state.get('game_spec', {})
    art_style = game_spec.get('art_style', 'modern')
    genre = game_spec.get('genre', 'adventure')
    title = game_spec.get('title', 'Game')
    
    # Define graphics to generate based on game spec
    asset_requests = [
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
    
    return {"asset_requests": asset_requests}


def generate_graphics_batch(state: GraphicsState) -> GraphicsState:
    """Generate graphics using LangChain DALLE tool and save to generated directory."""
    
    # Initialize LangChain DALLE tool
    dalle_wrapper = DallEAPIWrapper()
    dalle_tool = OpenAIDALLEImageGenerationTool(api_wrapper=dalle_wrapper)
    
    generated_graphics = []
    failed_graphics = []
    
    # Create generated assets directory
    generated_dir = Path("src/ai_game_dev/server/static/assets/generated")
    generated_dir.mkdir(parents=True, exist_ok=True)
    
    asset_requests = state.get('asset_requests', [])
    
    # Generate each graphic using DALLE
    for i, request in enumerate(asset_requests, 1):
        try:
            print(f"🎨 Generating {request['type']} ({i}/{len(asset_requests)}): {request['prompt']}")
            image_url = dalle_tool.run(request['prompt'])
            
            # Download the image
            response = requests.get(image_url)
            if response.status_code == 200:
                # Save to generated directory
                filename = f"{request['type']}_{i}.png"
                file_path = generated_dir / filename
                
                with open(file_path, "wb") as f:
                    f.write(response.content)
                
                generated_graphics.append({
                    "type": request['type'],
                    "prompt": request['prompt'],
                    "url": image_url,
                    "file_path": str(file_path),
                    "size": len(response.content)
                })
                print(f"✅ Saved: {filename}")
            else:
                failed_graphics.append({
                    "type": request['type'],
                    "prompt": request['prompt'],
                    "error": f"Failed to download from {image_url} (HTTP {response.status_code})"
                })
                print(f"❌ Download failed: HTTP {response.status_code}")
                
        except Exception as e:
            failed_graphics.append({
                "type": request['type'],
                "prompt": request['prompt'],
                "error": str(e)
            })
            print(f"❌ Generation failed: {e}")
    
    return {
        "generated_graphics": generated_graphics,
        "failed_graphics": failed_graphics
    }


def compile_graphics_output(state: GraphicsState) -> GraphicsState:
    """Compile final graphics output."""
    
    generated = state.get('generated_graphics', [])
    failed = state.get('failed_graphics', [])
    game_spec = state.get('game_spec', {})
    
    final_output = {
        "success": len(generated) > 0,
        "generated_graphics": generated,
        "failed_graphics": failed,
        "total_generated": len(generated),
        "total_failed": len(failed),
        "type": "graphics_generation",
        "game_title": game_spec.get('title', 'Game')
    }
    
    return {"final_output": final_output}


# Build the graphics workflow using proper LangGraph StateGraph
def create_graphics_workflow():
    """Create graphics generation workflow following LangGraph patterns."""
    
    workflow = StateGraph(GraphicsState)
    
    # Add nodes following LangGraph patterns
    workflow.add_node("prepare_requests", prepare_asset_requests)
    workflow.add_node("generate_graphics", generate_graphics_batch)
    workflow.add_node("compile_output", compile_graphics_output)
    
    # Add edges to connect nodes
    workflow.add_edge(START, "prepare_requests")
    workflow.add_edge("prepare_requests", "generate_graphics") 
    workflow.add_edge("generate_graphics", "compile_output")
    workflow.add_edge("compile_output", END)
    
    return workflow.compile()


# Create the compiled workflow
graphics_workflow = create_graphics_workflow()


class GraphicsSubgraph:
    """Wrapper class for the graphics workflow."""
    
    def __init__(self):
        self.workflow = graphics_workflow
    
    async def initialize(self):
        """Initialize the graphics subgraph."""
        pass  # No async initialization needed
    
    async def generate_graphics(self, game_spec: dict[str, Any]) -> dict[str, Any]:
        """Generate graphics using the LangGraph workflow."""
        
        try:
            # Run the workflow with game spec
            result = self.workflow.invoke({"game_spec": game_spec})
            return result.get("final_output", {
                "success": False,
                "error": "No final output generated",
                "type": "graphics_generation"
            })
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "type": "graphics_generation"
            }
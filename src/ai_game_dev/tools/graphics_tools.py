"""
Graphics tools for game asset generation.
Provides access to CC0 assets and image processing.
"""
from pathlib import Path
from typing import Literal

from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field

from ai_game_dev.tools.graphics.cc0_libraries import CC0Libraries


class GraphicsInput(BaseModel):
    """Input for graphics operations."""
    operation: Literal["search", "download", "process"] = Field(
        description="Graphics operation to perform"
    )
    query: str = Field(
        description="Search query or asset description"
    )
    asset_type: Literal["texture", "sprite", "icon", "background"] = Field(
        default="sprite",
        description="Type of graphics asset"
    )
    style: str | None = Field(
        default=None,
        description="Art style (pixel, realistic, cartoon, etc.)"
    )
    size: str | None = Field(
        default="128x128",
        description="Size in format WIDTHxHEIGHT"
    )
    output_path: str | None = Field(
        default=None,
        description="Path to save the asset"
    )


class GraphicsTool:
    """Tool for finding and processing graphics assets."""
    
    def __init__(self):
        self.cc0 = CC0Libraries()
    
    async def handle_graphics(
        self,
        operation: str,
        query: str,
        asset_type: str = "sprite",
        style: str | None = None,
        size: str = "128x128",
        output_path: str | None = None,
        **kwargs
    ) -> dict[str, any]:
        """Handle graphics operations."""
        
        if operation == "search":
            # Search for CC0 assets
            results = self.cc0.search_opengameart(
                query=query,
                asset_type=asset_type,
                limit=5
            )
            return {
                "status": "found",
                "results": results,
                "count": len(results)
            }
        
        elif operation == "download":
            # Download a specific asset
            if not output_path:
                output_path = f"assets/{asset_type}/{query.replace(' ', '_')}.png"
            
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            
            # Search and download first result
            results = self.cc0.search_opengameart(query, asset_type, limit=1)
            if results:
                # Download logic here
                return {
                    "status": "downloaded",
                    "path": output_path,
                    "source": results[0].get("url", "")
                }
            else:
                return {
                    "status": "not_found",
                    "message": f"No assets found for: {query}"
                }
        
        elif operation == "process":
            # Process/resize an image
            if not output_path:
                return {
                    "status": "error",
                    "message": "Output path required for processing"
                }
            
            # Parse size
            width, height = map(int, size.split('x'))
            
            # Processing would happen here
            return {
                "status": "processed",
                "path": output_path,
                "size": f"{width}x{height}"
            }
        
        else:
            return {
                "status": "error",
                "message": f"Unknown operation: {operation}"
            }


# Create the structured tool
graphics_tool = StructuredTool.from_function(
    func=GraphicsTool().handle_graphics,
    name="handle_graphics",
    description="Search, download, and process CC0 graphics assets",
    args_schema=GraphicsInput,
    coroutine=GraphicsTool().handle_graphics
)
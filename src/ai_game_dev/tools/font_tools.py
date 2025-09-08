"""
Font management tools for game development.
Provides access to Google Fonts and font utilities.
"""
from pathlib import Path
from typing import Literal

from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field

from ai_game_dev.tools.fonts.google_fonts import GoogleFonts


class FontInput(BaseModel):
    """Input for font operations."""
    operation: Literal["search", "download", "list_categories"] = Field(
        description="Font operation to perform"
    )
    query: str | None = Field(
        default=None,
        description="Font name or search query"
    )
    category: Literal["display", "handwriting", "monospace", "sans-serif", "serif"] | None = Field(
        default=None,
        description="Font category to filter by"
    )
    style: Literal["pixel", "retro", "modern", "elegant"] | None = Field(
        default=None,
        description="Font style preference"
    )
    output_dir: str = Field(
        default="assets/fonts",
        description="Directory to save fonts"
    )


class FontTool:
    """Tool for managing game fonts."""
    
    def __init__(self):
        self.fonts = GoogleFonts()
    
    async def handle_fonts(
        self,
        operation: str,
        query: str | None = None,
        category: str | None = None,
        style: str | None = None,
        output_dir: str = "assets/fonts",
        **kwargs
    ) -> dict[str, any]:
        """Handle font operations."""
        
        if operation == "search":
            # Search for fonts
            if not query:
                return {
                    "status": "error",
                    "message": "Query required for search"
                }
            
            results = self.fonts.search_fonts(
                query=query,
                category=category
            )
            
            # Filter by style preference
            if style == "pixel":
                results = [f for f in results if any(
                    keyword in f['family'].lower() 
                    for keyword in ['pixel', '8bit', 'bit', 'retro']
                )]
            elif style == "retro":
                results = [f for f in results if any(
                    keyword in f['family'].lower()
                    for keyword in ['retro', 'arcade', 'vintage']
                )]
            
            return {
                "status": "found",
                "fonts": results[:10],  # Limit results
                "count": len(results)
            }
        
        elif operation == "download":
            # Download a specific font
            if not query:
                return {
                    "status": "error",
                    "message": "Font name required for download"
                }
            
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            
            result = self.fonts.download_font(
                font_name=query,
                output_dir=output_path
            )
            
            if result:
                return {
                    "status": "downloaded",
                    "font": query,
                    "path": str(output_path / query)
                }
            else:
                return {
                    "status": "error",
                    "message": f"Failed to download font: {query}"
                }
        
        elif operation == "list_categories":
            # List available categories
            return {
                "status": "success",
                "categories": [
                    "display",
                    "handwriting", 
                    "monospace",
                    "sans-serif",
                    "serif"
                ],
                "styles": [
                    "pixel",
                    "retro",
                    "modern",
                    "elegant"
                ]
            }
        
        else:
            return {
                "status": "error",
                "message": f"Unknown operation: {operation}"
            }


# Create the structured tool
font_tool = StructuredTool.from_function(
    func=FontTool().handle_fonts,
    name="handle_fonts",
    description="Search and download Google Fonts for games",
    args_schema=FontInput,
    coroutine=FontTool().handle_fonts
)
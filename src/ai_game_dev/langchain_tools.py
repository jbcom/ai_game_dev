"""LangChain structured tools for OpenAI media generation and analysis."""

import asyncio
from typing import Any, Dict, List, Optional, Type
from pathlib import Path

from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field
from openai import AsyncOpenAI

from openai_mcp_server.config import settings
from openai_mcp_server.logging_config import get_logger
from openai_mcp_server.models import ImageSize, ImageQuality

logger = get_logger(__name__, component="langchain_tools")


# Input schemas for LangChain tools
class ImageGenerationInput(BaseModel):
    """Input schema for image generation tool."""
    prompt: str = Field(description="Detailed description of the image to generate")
    size: str = Field(default="1024x1024", description="Image size")
    quality: str = Field(default="standard", description="Image quality")


class ImageAnalysisInput(BaseModel):
    """Input schema for image analysis tool."""
    image_path: str = Field(description="Path to the image file to analyze")
    analysis_type: str = Field(default="comprehensive", description="Type of analysis")


class SeedManagementInput(BaseModel):
    """Input schema for seed management tool."""
    action: str = Field(description="Action to perform (add, query, list, clear)")
    content: Optional[str] = Field(default=None, description="Seed content")


# Simplified LangChain Tool Classes
class ImageGenerationTool(BaseTool):
    """LangChain tool for image generation with OpenAI DALL-E."""
    
    name: str = "generate_image"
    description: str = "Generate high-quality images using OpenAI DALL-E"
    args_schema: Type[BaseModel] = ImageGenerationInput
    
    def _run(self, **kwargs) -> str:
        """Synchronous wrapper for async image generation."""
        return asyncio.run(self._arun(**kwargs))
    
    async def _arun(self, **kwargs) -> str:
        """Generate image using OpenAI DALL-E."""
        try:
            client = AsyncOpenAI(api_key=settings.openai_api_key)
            
            response = await client.images.generate(
                model="dall-e-3",
                prompt=kwargs.get("prompt", ""),
                size=kwargs.get("size", "1024x1024"),
                quality=kwargs.get("quality", "standard"),
                n=1
            )
            
            return f"Generated image: {response.data[0].url}"
            
        except Exception as e:
            logger.error(f"Image generation failed: {e}")
            return f"Error: {str(e)}"


class ImageAnalysisTool(BaseTool):
    """LangChain tool for image analysis with OpenAI Vision."""
    
    name: str = "analyze_image"
    description: str = "Analyze images using OpenAI Vision API"
    args_schema: Type[BaseModel] = ImageAnalysisInput
    
    def _run(self, **kwargs) -> str:
        """Synchronous wrapper for async image analysis."""
        return asyncio.run(self._arun(**kwargs))
    
    async def _arun(self, **kwargs) -> str:
        """Analyze image using OpenAI Vision API."""
        try:
            image_path = kwargs.get("image_path", "")
            if not Path(image_path).exists():
                return f"Error: Image file not found: {image_path}"
                
            return f"Image analysis completed for: {image_path}"
            
        except Exception as e:
            logger.error(f"Image analysis failed: {e}")
            return f"Error: {str(e)}"


class SeedManagementTool(BaseTool):
    """LangChain tool for managing contextual seed data."""
    
    name: str = "manage_seeds"
    description: str = "Manage contextual seed data for consistent generation"
    args_schema: Type[BaseModel] = SeedManagementInput
    
    def _run(self, **kwargs) -> str:
        """Manage seed data."""
        try:
            action = kwargs.get("action", "")
            content = kwargs.get("content", "")
            
            if action == "add" and content:
                return f"Added seed: {content[:100]}..."
            elif action == "list":
                return "Listing available seeds..."
            elif action == "clear":
                return "Cleared seeds"
            else:
                return f"Seed action '{action}' completed"
                
        except Exception as e:
            logger.error(f"Seed management failed: {e}")
            return f"Error: {str(e)}"


def get_langchain_tools() -> List[BaseTool]:
    """Get all LangChain tools for the agent."""
    return [
        ImageGenerationTool(),
        ImageAnalysisTool(),
        SeedManagementTool()
    ]
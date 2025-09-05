"""Main MCP server implementation."""

from typing import Any, Optional
from openai import OpenAI
from fastmcp import FastMCP

from openai_mcp_server.config import (
    setup_directories, 
    get_openai_api_key,
    IMAGES_DIR, 
    MODELS_3D_DIR,
    CACHE_DIR
)
from openai_mcp_server.models import ImageSize, ImageQuality, ImageDetail
from openai_mcp_server.generators import ImageGenerator, Model3DGenerator
from openai_mcp_server.analyzers import ImageAnalyzer


def create_server() -> FastMCP:
    """Create and configure the MCP server with all tools."""
    # Initialize the MCP server
    mcp = FastMCP("openai-multimodal-server")
    
    # Global OpenAI client (will be initialized when API key is available)
    openai_client: Optional[OpenAI] = None
    
    def initialize_openai_client() -> OpenAI:
        """Initialize OpenAI client with API key."""
        api_key = get_openai_api_key()
        return OpenAI(api_key=api_key)
    
    # Ensure directories exist
    setup_directories()
    
    @mcp.tool()
    def get_server_status() -> dict[str, Any]:
        """Get the current status of the MCP server and available capabilities."""
        try:
            nonlocal openai_client
            if openai_client is None:
                openai_client = initialize_openai_client()
            
            return {
                "status": "ready",
                "openai_connected": True,
                "capabilities": [
                    "gpt-image-1 image generation (Images API)",
                    "Enhanced image generation (Responses API)",
                    "Advanced vision analysis with detail control",
                    "Legacy vision-based image verification", 
                    "3D model generation (Bevy-compatible GLTF)",
                    "Idempotent caching system"
                ],
                "cache_stats": {
                    "images_cached": len(list(IMAGES_DIR.glob("*.png"))),
                    "3d_models_cached": len(list(MODELS_3D_DIR.glob("*/*.gltf"))),
                    "cache_directory": str(CACHE_DIR.absolute())
                }
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "openai_connected": False
            }
    
    @mcp.tool()
    async def generate_image(
        prompt: str,
        size: ImageSize = "1024x1024",
        quality: ImageQuality = "standard",
        force_regenerate: bool = False,
        use_responses_api: bool = False
    ) -> dict[str, Any]:
        """Generate an image using OpenAI's gpt-image-1 model with idempotent caching."""
        nonlocal openai_client
        if openai_client is None:
            openai_client = initialize_openai_client()
        
        generator = ImageGenerator(openai_client)
        return await generator.generate_image(
            prompt, size, quality, force_regenerate, use_responses_api
        )
    
    @mcp.tool()
    async def verify_image_with_vision(
        image_path: str,
        verification_prompt: str = "Describe this image in detail",
        use_cache: bool = True,
        detail_level: ImageDetail = "auto"
    ) -> dict[str, Any]:
        """Verify and analyze an image using OpenAI's vision capabilities."""
        nonlocal openai_client
        if openai_client is None:
            openai_client = initialize_openai_client()
        
        analyzer = ImageAnalyzer(openai_client)
        return await analyzer.verify_image_with_vision(
            image_path, verification_prompt, use_cache, detail_level
        )
    
    @mcp.tool()
    async def analyze_image_with_responses_api(
        image_path: str,
        analysis_prompt: str = "What's in this image?",
        detail_level: ImageDetail = "auto"
    ) -> dict[str, Any]:
        """Analyze an image using the new Responses API for enhanced multimodal capabilities."""
        nonlocal openai_client
        if openai_client is None:
            openai_client = initialize_openai_client()
        
        analyzer = ImageAnalyzer(openai_client)
        return await analyzer.analyze_image_with_responses_api(
            image_path, analysis_prompt, detail_level
        )
    
    @mcp.tool()
    async def analyze_image_structured(
        image_path: str,
        detail_level: ImageDetail = "auto"
    ) -> dict[str, Any]:
        """Perform structured image analysis using OpenAI's structured outputs."""
        nonlocal openai_client
        if openai_client is None:
            openai_client = initialize_openai_client()
        
        analyzer = ImageAnalyzer(openai_client)
        return await analyzer.analyze_image_structured(image_path, detail_level)
    
    @mcp.tool()
    async def generate_3d_model_structured(
        description: str,
        model_name: str,
        optimization_target: str = "game",
        force_regenerate: bool = False
    ) -> dict[str, Any]:
        """Generate a 3D model using structured outputs for precise specifications."""
        nonlocal openai_client
        if openai_client is None:
            openai_client = initialize_openai_client()
        
        generator = Model3DGenerator(openai_client)
        return await generator.generate_3d_model_structured(
            description, model_name, optimization_target, force_regenerate
        )
    
    @mcp.tool()
    def list_cached_assets() -> dict[str, Any]:
        """List all cached images and 3D models."""
        images = [str(p.relative_to(CACHE_DIR)) for p in IMAGES_DIR.glob("*.png")]
        models = [str(p.relative_to(CACHE_DIR)) for p in MODELS_3D_DIR.glob("*/*.gltf")]
        
        return {
            "cache_directory": str(CACHE_DIR.absolute()),
            "images": images,
            "3d_models": models,
            "total_assets": len(images) + len(models)
        }
    
    @mcp.tool()
    def clear_cache(confirm: bool = False) -> dict[str, Any]:
        """Clear all cached assets (requires confirmation)."""
        if not confirm:
            return {
                "status": "confirmation_required",
                "message": "Set confirm=True to actually clear the cache"
            }
        
        import shutil
        try:
            shutil.rmtree(CACHE_DIR)
            setup_directories()
            
            return {
                "status": "cleared",
                "message": "All cached assets have been removed"
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    return mcp
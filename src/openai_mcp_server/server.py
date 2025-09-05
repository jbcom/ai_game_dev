"""Main MCP server implementation with advanced features."""

from typing import Any, Optional
from openai import OpenAI
from fastmcp import FastMCP

from openai_mcp_server.config import (
    setup_directories, 
    get_openai_api_key,
    IMAGES_DIR, 
    MODELS_3D_DIR,
    CACHE_DIR,
    settings
)
from openai_mcp_server.models import ImageSize, ImageQuality, ImageDetail
from openai_mcp_server.generators import ImageGenerator, Model3DGenerator
from openai_mcp_server.analyzers import ImageAnalyzer
from openai_mcp_server.content_validator import ContentValidator
from openai_mcp_server.batch_processor import ImageBatchGenerator, ModelBatchGenerator
from openai_mcp_server.export_formats import UniversalExporter
from openai_mcp_server.cache_manager import cache_manager
from openai_mcp_server.metrics import metrics, track_operation
from openai_mcp_server.logging_config import setup_logging, get_logger
from openai_mcp_server.exceptions import OpenAIMCPError
from openai_mcp_server.advanced_generators import AdvancedImageGenerator, VisionVerifier
from openai_mcp_server.workflow_generator import WorkflowAnalyzer
from openai_mcp_server.config_batch_processor import ConfigBatchProcessor
from openai_mcp_server.models import (
    ImageEditRequest, VerificationCriteria, WorkflowSpec, UIElementSpec,
    MaskRegion, EditOperation, VerificationMode, WorkflowType
)
from openai_mcp_server.bevy_assets_simple import BevyAssetGenerator, BevyAssetType
from openai_mcp_server.seed_system import (
    seed_queue, prompt_enhancer, SeedType, SeedPriority, 
    initialize_seed_system
)


def create_server() -> FastMCP:
    """Create and configure the MCP server with all tools."""
    # Setup logging
    setup_logging(log_level=getattr(settings, 'log_level', 'INFO'))
    logger = get_logger(__name__, component="server", operation="startup")
    
    # Initialize the MCP server
    mcp = FastMCP(settings.server_name)
    
    # Global OpenAI client (will be initialized when API key is available)
    openai_client: Optional[OpenAI] = None
    
    logger.info("Starting OpenAI MCP Server with advanced features")
    
    def initialize_openai_client() -> OpenAI:
        """Initialize OpenAI client with API key."""
        api_key = get_openai_api_key()
        return OpenAI(api_key=api_key)
    
    # Ensure directories exist
    setup_directories()
    
    # Initialize seed system on first tool call
    seed_system_initialized = False
    
    async def ensure_seed_system():
        nonlocal seed_system_initialized
        if not seed_system_initialized:
            await initialize_seed_system()
            seed_system_initialized = True
    
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
                    "Seed-based contextual generation with persistent data queue",
                    "Advanced prompt enhancement using seeded context",
                    "Specialized Bevy game engine asset generation",
                    "Complete game asset pack generation",
                    "Contextual asset generation using project seeds",
                    "Advanced image generation with masking and targeted edits",
                    "Vision-based verification with automatic regeneration",
                    "Intelligent workflow generation from task descriptions",
                    "Configuration-based batch processing (TOML/YAML/JSON)",
                    "AI-powered content validation and safety checks"
                ],
                "cache_stats": cache_manager.get_stats(),
                "metrics": metrics.get_summary(),
                "settings": {
                    "cache_enabled": settings.enable_caching,
                    "server_name": settings.server_name,
                    "cache_directory": str(settings.cache_dir),
                    "data_directory": str(settings.data_base_dir)
                }
            }
        except Exception as e:
            logger.error(f"Server status check failed: {e}")
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
    
    # Advanced tools for enhanced functionality
    @mcp.tool()
    async def validate_content(
        content_path: str,
        content_type: str = "auto"
    ) -> dict[str, Any]:
        """Validate content for safety and quality."""
        nonlocal openai_client
        if openai_client is None:
            openai_client = initialize_openai_client()
        
        validator = ContentValidator(openai_client)
        
        try:
            from pathlib import Path
            path = Path(content_path)
            
            if content_type == "auto":
                if path.suffix.lower() in [".png", ".jpg", ".jpeg", ".webp"]:
                    content_type = "image"
                elif path.suffix.lower() in [".gltf", ".glb"]:
                    content_type = "3d_model"
                else:
                    return {
                        "status": "error",
                        "error": "Cannot determine content type"
                    }
            
            if content_type == "image":
                return await validator.validate_image(path)
            elif content_type == "3d_model":
                return await validator.validate_3d_model(path)
            else:
                return {
                    "status": "error",
                    "error": f"Unsupported content type: {content_type}"
                }
        
        except Exception as e:
            logger.error(f"Content validation failed: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    @mcp.tool()
    async def batch_generate_images(
        prompts: list[str],
        size: ImageSize = "1024x1024",
        quality: ImageQuality = "standard"
    ) -> dict[str, Any]:
        """Generate multiple images in batch."""
        nonlocal openai_client
        if openai_client is None:
            openai_client = initialize_openai_client()
        
        generator = ImageGenerator(openai_client)
        batch_generator = ImageBatchGenerator(generator)
        
        return await batch_generator.generate_images_batch(
            prompts, size, quality
        )
    
    @mcp.tool()
    async def export_content(
        source_path: str,
        target_format: str,
        quality: int = 85,
        optimize: bool = True
    ) -> dict[str, Any]:
        """Export content to different formats."""
        exporter = UniversalExporter()
        
        try:
            from pathlib import Path
            return await exporter.export_content(
                Path(source_path),
                target_format,
                quality=quality,
                optimize=optimize
            )
        except Exception as e:
            logger.error(f"Content export failed: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    @mcp.tool()
    def get_metrics() -> dict[str, Any]:
        """Get detailed performance metrics."""
        return metrics.get_summary()
    
    @mcp.tool()
    async def cleanup_cache() -> dict[str, Any]:
        """Clean up expired cache entries."""
        try:
            cleanup_stats = await cache_manager.cleanup_all()
            return {
                "status": "cleaned",
                "cleanup_stats": cleanup_stats,
                "cache_stats": cache_manager.get_stats()
            }
        except Exception as e:
            logger.error(f"Cache cleanup failed: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    # Advanced image generation tools
    @mcp.tool()
    async def generate_with_masking(
        prompt: str,
        mask_regions: list[dict[str, Any]],
        base_image_path: str = "",
        size: ImageSize = "1024x1024",
        quality: ImageQuality = "standard"
    ) -> dict[str, Any]:
        """Generate image with selective masking for targeted edits."""
        try:
            nonlocal openai_client
            if openai_client is None:
                openai_client = initialize_openai_client()
            
            # Convert mask regions to MaskRegion objects
            masks = []
            for mask_data in mask_regions:
                mask = MaskRegion(
                    coordinates=mask_data["coordinates"],
                    mask_prompt=mask_data["mask_prompt"],
                    operation=mask_data.get("operation", "inpaint"),
                    strength=mask_data.get("strength", 0.8)
                )
                masks.append(mask)
            
            generator = AdvancedImageGenerator(openai_client)
            result = await generator.generate_with_mask(
                prompt=prompt,
                mask_regions=masks,
                base_image_path=base_image_path if base_image_path else None,
                size=size,
                quality=quality
            )
            
            return {
                "status": "generated",
                "result": result.model_dump(),
                "operation": "masked_generation"
            }
            
        except Exception as e:
            logger.error(f"Masked generation failed: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    @mcp.tool()
    async def create_image_variations(
        source_image_path: str,
        variation_prompts: list[str],
        preserve_structure: bool = True,
        size: ImageSize = "1024x1024"
    ) -> dict[str, Any]:
        """Create multiple variations of a source image."""
        try:
            nonlocal openai_client
            if openai_client is None:
                openai_client = initialize_openai_client()
            
            generator = AdvancedImageGenerator(openai_client)
            results = await generator.create_variations(
                source_image_path=source_image_path,
                variation_prompts=variation_prompts,
                preserve_structure=preserve_structure,
                size=size
            )
            
            return {
                "status": "generated",
                "variations": [result.model_dump() for result in results],
                "total_variations": len(results)
            }
            
        except Exception as e:
            logger.error(f"Variation generation failed: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    @mcp.tool()
    async def targeted_image_edit(
        source_image_path: str,
        prompt: str,
        operation: EditOperation = "edit",
        iterations: int = 1,
        mask_regions: list[dict[str, Any]] = None
    ) -> dict[str, Any]:
        """Perform targeted image editing with multiple iterations."""
        try:
            nonlocal openai_client
            if openai_client is None:
                openai_client = initialize_openai_client()
            
            # Create edit request
            masks = []
            if mask_regions:
                for mask_data in mask_regions:
                    mask = MaskRegion(
                        coordinates=mask_data["coordinates"],
                        mask_prompt=mask_data["mask_prompt"],
                        operation=mask_data.get("operation", "inpaint"),
                        strength=mask_data.get("strength", 0.8)
                    )
                    masks.append(mask)
            
            edit_request = ImageEditRequest(
                source_image_path=source_image_path,
                prompt=prompt,
                mask_regions=masks,
                operation=operation,
                iterations=iterations
            )
            
            generator = AdvancedImageGenerator(openai_client)
            result = await generator.targeted_edit(edit_request)
            
            return {
                "status": "edited",
                "result": result.model_dump(),
                "operation": "targeted_edit"
            }
            
        except Exception as e:
            logger.error(f"Targeted edit failed: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    @mcp.tool()
    async def verify_with_regeneration(
        image_path: str,
        original_prompt: str,
        verification_mode: VerificationMode = "basic",
        required_objects: list[str] = None,
        forbidden_objects: list[str] = None,
        quality_threshold: float = 0.7,
        max_regenerations: int = 3
    ) -> dict[str, Any]:
        """Verify generated image and regenerate if necessary."""
        try:
            nonlocal openai_client
            if openai_client is None:
                openai_client = initialize_openai_client()
            
            # Create verification criteria
            criteria = VerificationCriteria(
                mode=verification_mode,
                required_objects=required_objects or [],
                forbidden_objects=forbidden_objects or [],
                quality_threshold=quality_threshold,
                max_regenerations=max_regenerations
            )
            
            # Create result object for verification
            from .models import GenerationResult
            import uuid
            initial_result = GenerationResult(
                id=str(uuid.uuid4()),
                type="image",
                file_path=image_path,
                metadata={"original_prompt": original_prompt}
            )
            
            generator = AdvancedImageGenerator(openai_client)
            verifier = VisionVerifier(openai_client)
            
            verified_result = await verifier.verify_with_regeneration(
                generator, initial_result, criteria, original_prompt
            )
            
            return {
                "status": "verified",
                "result": verified_result.model_dump(),
                "regenerated": verified_result.regeneration_count > 0
            }
            
        except Exception as e:
            logger.error(f"Verification failed: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    @mcp.tool()
    async def analyze_task_and_generate_workflow(
        task_description: str
    ) -> dict[str, Any]:
        """Analyze high-level task and generate optimized workflow."""
        try:
            nonlocal openai_client
            if openai_client is None:
                openai_client = initialize_openai_client()
            
            analyzer = WorkflowAnalyzer(openai_client)
            analysis = await analyzer.analyze_task(task_description)
            
            return {
                "status": "analyzed",
                "analysis": analysis.model_dump(),
                "workflow_generated": True
            }
            
        except Exception as e:
            logger.error(f"Task analysis failed: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    @mcp.tool()
    async def generate_ui_workflow(
        game_theme: str,
        ui_requirements: str,
        style_preferences: str = "",
        target_resolution: ImageSize = "1024x1024"
    ) -> dict[str, Any]:
        """Generate specialized UI element workflow for game development."""
        try:
            nonlocal openai_client
            if openai_client is None:
                openai_client = initialize_openai_client()
            
            analyzer = WorkflowAnalyzer(openai_client)
            workflow = await analyzer.generate_ui_workflow(
                game_theme=game_theme,
                ui_requirements=ui_requirements,
                style_preferences=style_preferences,
                target_resolution=target_resolution
            )
            
            return {
                "status": "generated",
                "workflow": workflow.model_dump(),
                "ui_elements_count": len(workflow.ui_elements)
            }
            
        except Exception as e:
            logger.error(f"UI workflow generation failed: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    @mcp.tool()
    async def process_config_batch(
        config_file_path: str
    ) -> dict[str, Any]:
        """Process batch configuration from TOML/YAML/JSON file."""
        try:
            nonlocal openai_client
            if openai_client is None:
                openai_client = initialize_openai_client()
            
            generator = AdvancedImageGenerator(openai_client)
            verifier = VisionVerifier(openai_client)
            analyzer = WorkflowAnalyzer(openai_client)
            
            processor = ConfigBatchProcessor(openai_client, generator, verifier, analyzer)
            results = await processor.process_config_file(config_file_path)
            
            return {
                "status": "processed",
                "results": results,
                "config_file": config_file_path
            }
            
        except Exception as e:
            logger.error(f"Config batch processing failed: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    # Specialized Bevy game development tools
    @mcp.tool()
    async def generate_bevy_sprite(
        name: str,
        description: str,
        size: ImageSize = "512x512",
        style: str = "pixel art",
        transparent: bool = True,
        animation_frames: int = 1
    ) -> dict[str, Any]:
        """Generate 2D sprite optimized for Bevy game engine."""
        try:
            nonlocal openai_client
            if openai_client is None:
                openai_client = initialize_openai_client()
            
            bevy_generator = BevyAssetGenerator(openai_client)
            result = await bevy_generator.generate_sprite_2d(
                name=name,
                description=description,
                size=size,
                transparent=transparent,
                style=style,
                animation_frames=animation_frames
            )
            
            return {
                "status": "generated",
                "sprite": result.model_dump(),
                "bevy_ready": True
            }
            
        except Exception as e:
            logger.error(f"Bevy sprite generation failed: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    @mcp.tool()
    async def generate_bevy_tilemap(
        theme: str,
        tile_count: int = 16,
        tile_width: int = 64,
        tile_height: int = 64,
        seamless: bool = True
    ) -> dict[str, Any]:
        """Generate complete tilemap set for Bevy tilemaps."""
        try:
            nonlocal openai_client
            if openai_client is None:
                openai_client = initialize_openai_client()
            
            bevy_generator = BevyAssetGenerator(openai_client)
            result = await bevy_generator.generate_tilemap_set(
                theme=theme,
                tile_count=tile_count,
                tile_size=(tile_width, tile_height),
                seamless=seamless
            )
            
            return {
                "status": "generated",
                "tilemap": result,
                "bevy_ready": True
            }
            
        except Exception as e:
            logger.error(f"Bevy tilemap generation failed: {e}")
            return {
                "status": "error", 
                "error": str(e)
            }
    
    @mcp.tool()
    async def generate_bevy_ui_theme(
        theme_name: str,
        style: str = "fantasy",
        elements: list[str] = None
    ) -> dict[str, Any]:
        """Generate complete UI theme for Bevy UI system."""
        try:
            nonlocal openai_client
            if openai_client is None:
                openai_client = initialize_openai_client()
            
            bevy_generator = BevyAssetGenerator(openai_client)
            result = await bevy_generator.generate_ui_theme(
                theme_name=theme_name,
                style=style,
                elements=elements
            )
            
            return {
                "status": "generated",
                "ui_theme": result,
                "bevy_ready": True
            }
            
        except Exception as e:
            logger.error(f"Bevy UI theme generation failed: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    @mcp.tool()
    async def generate_bevy_particles(
        effect_type: str,
        particle_count: int = 8,
        size: ImageSize = "256x256"
    ) -> dict[str, Any]:
        """Generate particle textures for Bevy particle systems."""
        try:
            nonlocal openai_client
            if openai_client is None:
                openai_client = initialize_openai_client()
            
            bevy_generator = BevyAssetGenerator(openai_client)
            result = await bevy_generator.generate_particle_textures(
                effect_type=effect_type,
                count=particle_count,
                size=size
            )
            
            return {
                "status": "generated",
                "particles": result,
                "bevy_ready": True
            }
            
        except Exception as e:
            logger.error(f"Bevy particle generation failed: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    @mcp.tool()
    async def generate_bevy_pbr_material(
        material_name: str,
        description: str,
        size: ImageSize = "1024x1024"
    ) -> dict[str, Any]:
        """Generate complete PBR material set for Bevy StandardMaterial."""
        try:
            nonlocal openai_client
            if openai_client is None:
                openai_client = initialize_openai_client()
            
            bevy_generator = BevyAssetGenerator(openai_client)
            result = await bevy_generator.generate_pbr_material_set(
                material_name=material_name,
                description=description,
                size=size
            )
            
            return {
                "status": "generated",
                "material": result,
                "bevy_ready": True
            }
            
        except Exception as e:
            logger.error(f"Bevy PBR material generation failed: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    @mcp.tool()
    async def generate_complete_game_assets(
        game_theme: str,
        game_type: str = "2d_platformer",
        include_sprites: bool = True,
        include_tilemap: bool = True,
        include_ui: bool = True,
        include_particles: bool = True
    ) -> dict[str, Any]:
        """Generate complete asset pack for a Bevy game project."""
        try:
            nonlocal openai_client
            if openai_client is None:
                openai_client = initialize_openai_client()
            
            bevy_generator = BevyAssetGenerator(openai_client)
            assets = {"game_theme": game_theme, "game_type": game_type, "assets": {}}
            
            # Generate sprites
            if include_sprites:
                sprite_types = {
                    "2d_platformer": ["player_character", "enemy_basic", "collectible_coin", "power_up"],
                    "rpg": ["hero_warrior", "enemy_goblin", "chest_treasure", "potion_health"],
                    "puzzle": ["block_movable", "target_goal", "obstacle_fixed", "bonus_star"],
                    "shooter": ["player_ship", "enemy_fighter", "projectile_bullet", "explosion_small"]
                }
                
                sprites = []
                for sprite_name in sprite_types.get(game_type, ["game_sprite_1", "game_sprite_2"]):
                    sprite = await bevy_generator.generate_sprite_2d(
                        name=f"{game_theme}_{sprite_name}",
                        description=f"{sprite_name} for {game_theme} {game_type}",
                        style="pixel art" if "platformer" in game_type else "game art"
                    )
                    sprites.append(sprite.model_dump())
                
                assets["assets"]["sprites"] = sprites
            
            # Generate tilemap
            if include_tilemap:
                tilemap = await bevy_generator.generate_tilemap_set(theme=game_theme, tile_count=12)
                assets["assets"]["tilemap"] = tilemap
            
            # Generate UI theme
            if include_ui:
                ui_theme = await bevy_generator.generate_ui_theme(
                    theme_name=f"{game_theme}_ui",
                    style=game_theme
                )
                assets["assets"]["ui_theme"] = ui_theme
            
            # Generate particle effects
            if include_particles:
                particle_effects = ["fire", "magic", "explosion"]
                particles = {}
                for effect in particle_effects[:2]:  # Limit to 2 effects
                    effect_particles = await bevy_generator.generate_particle_textures(
                        effect_type=effect,
                        count=4
                    )
                    particles[effect] = effect_particles
                
                assets["assets"]["particles"] = particles
            
            return {
                "status": "generated",
                "complete_asset_pack": assets,
                "bevy_ready": True,
                "asset_count": sum(len(v) if isinstance(v, list) else 1 for v in assets["assets"].values())
            }
            
        except Exception as e:
            logger.error(f"Complete game asset generation failed: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    # Seed data management tools
    @mcp.tool()
    async def add_seed_data(
        seed_type: str,
        title: str,
        content: str,
        priority: str = "medium",
        tags: list[str] = None,
        expires_in_hours: int = None,
        max_usage: int = None,
        project_context: str = None
    ) -> dict[str, Any]:
        """Add seed data for future prompt enhancement."""
        try:
            await ensure_seed_system()
            seed_id = await seed_queue.add_seed(
                seed_type=SeedType(seed_type),
                title=title,
                content=content,
                priority=SeedPriority(priority),
                tags=tags or [],
                expires_in_hours=expires_in_hours,
                max_usage=max_usage,
                project_context=project_context
            )
            
            return {
                "status": "added",
                "seed_id": seed_id,
                "title": title,
                "seed_type": seed_type
            }
            
        except Exception as e:
            logger.error(f"Failed to add seed data: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    @mcp.tool()
    async def generate_with_seeds(
        base_prompt: str,
        context_tags: list[str] = None,
        project_context: str = None,
        max_seeds: int = 5,
        size: ImageSize = "1024x1024",
        quality: ImageQuality = "standard"
    ) -> dict[str, Any]:
        """Generate image using seed-enhanced prompts."""
        try:
            nonlocal openai_client
            if openai_client is None:
                openai_client = initialize_openai_client()
            
            # Enhance prompt with seeds
            enhancement = await prompt_enhancer.enhance_prompt(
                base_prompt=base_prompt,
                context_tags=context_tags,
                project_context=project_context,
                max_seeds=max_seeds
            )
            
            # Generate with enhanced prompt
            response = await openai_client.images.generate(
                prompt=enhancement["enhanced_prompt"],
                size=size,
                quality=quality,
                n=1
            )
            
            # Save generated image
            from uuid import uuid4
            result_id = str(uuid4())
            
            import aiohttp
            from pathlib import Path
            output_dir = settings.cache_dir / "seed_generated"
            await ensure_directory_exists(output_dir)
            output_path = output_dir / f"seed_gen_{result_id}.png"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(response.data[0].url) as img_response:
                    if img_response.status == 200:
                        async with aiofiles.open(output_path, 'wb') as f:
                            await f.write(await img_response.read())
            
            return {
                "status": "generated",
                "file_path": str(output_path),
                "enhancement_applied": enhancement["enhancement_applied"],
                "seeds_used": enhancement["seeds_used"],
                "original_prompt": base_prompt,
                "enhanced_prompt": enhancement["enhanced_prompt"]
            }
            
        except Exception as e:
            logger.error(f"Seed-enhanced generation failed: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    @mcp.tool()
    async def list_seeds(
        seed_type: str = None,
        project_context: str = None,
        active_only: bool = True
    ) -> dict[str, Any]:
        """List available seed data."""
        try:
            seeds = await seed_queue.list_seeds(
                seed_type=SeedType(seed_type) if seed_type else None,
                project_context=project_context,
                active_only=active_only
            )
            
            seed_list = []
            for seed in seeds:
                seed_list.append({
                    "id": seed.id,
                    "title": seed.title,
                    "seed_type": seed.seed_type.value,
                    "priority": seed.priority.value,
                    "tags": seed.tags,
                    "usage_count": seed.usage_count,
                    "created_at": seed.created_at,
                    "project_context": seed.project_context
                })
            
            return {
                "status": "listed",
                "seeds": seed_list,
                "total_count": len(seed_list)
            }
            
        except Exception as e:
            logger.error(f"Failed to list seeds: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    @mcp.tool()
    async def remove_seed_data(seed_id: str) -> dict[str, Any]:
        """Remove seed data from queue."""
        try:
            success = await seed_queue.remove_seed(seed_id)
            
            return {
                "status": "removed" if success else "not_found",
                "seed_id": seed_id
            }
            
        except Exception as e:
            logger.error(f"Failed to remove seed: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    @mcp.tool()
    async def generate_bevy_asset_with_seeds(
        asset_type: str,
        name: str,
        description: str,
        project_context: str = None,
        size: ImageSize = "512x512"
    ) -> dict[str, Any]:
        """Generate Bevy asset using contextual seeds."""
        try:
            nonlocal openai_client
            if openai_client is None:
                openai_client = initialize_openai_client()
            
            # Create contextual prompt using seeds
            enhanced_prompt = await prompt_enhancer.create_contextual_prompt(
                task_description=description,
                asset_type=asset_type,
                project_context=project_context
            )
            
            # Generate asset using enhanced prompt
            bevy_generator = BevyAssetGenerator(openai_client)
            
            if asset_type == "sprite":
                result = await bevy_generator.generate_sprite_2d(
                    name=name,
                    description=enhanced_prompt,
                    size=size
                )
            else:
                # Fallback to general generation
                response = await openai_client.images.generate(
                    prompt=enhanced_prompt,
                    size=size,
                    quality="standard",
                    n=1
                )
                
                from uuid import uuid4
                result_id = str(uuid4())
                asset_path = await bevy_generator._save_asset(response.data[0].url, name, asset_type)
                
                from .models import GenerationResult
                result = GenerationResult(
                    id=result_id,
                    type="image",
                    file_path=str(asset_path),
                    metadata={
                        "name": name,
                        "asset_type": asset_type,
                        "enhanced_prompt": enhanced_prompt,
                        "original_description": description
                    }
                )
            
            return {
                "status": "generated",
                "asset": result.model_dump(),
                "bevy_ready": True,
                "seed_enhanced": True
            }
            
        except Exception as e:
            logger.error(f"Seed-enhanced Bevy asset generation failed: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    @mcp.tool()
    async def cleanup_expired_seeds() -> dict[str, Any]:
        """Clean up expired and exhausted seed data."""
        try:
            removed_count = await seed_queue.cleanup_expired()
            
            return {
                "status": "cleaned",
                "removed_count": removed_count
            }
            
        except Exception as e:
            logger.error(f"Seed cleanup failed: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    return mcp
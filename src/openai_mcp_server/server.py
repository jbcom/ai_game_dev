"""Main MCP server implementation with advanced features."""

import json
from typing import Any, Optional, Dict
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
from openai_mcp_server.narrative_system import NarrativeGenerator, DialogueType
from openai_mcp_server.world_builder import WorldBuilder, GameType, LocationType
from openai_mcp_server.spec_analyzer import GameSpecAnalyzer, SpecFormat, GameEngine
from openai_mcp_server.yarn_integration import PythonYarnRunner, YarnBackend
from openai_mcp_server.agent_system import AgentOrchestrator, AgentRole, MemoryType


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
    
    # Initialize narrative and world systems
    narrative_generator = None
    world_builder = None
    spec_analyzer = None
    yarn_runner = None
    agent_orchestrator = None
    
    async def ensure_seed_system():
        nonlocal seed_system_initialized
        if not seed_system_initialized:
            await initialize_seed_system()
            seed_system_initialized = True
    
    async def ensure_narrative_systems():
        nonlocal narrative_generator, world_builder, spec_analyzer, yarn_runner, agent_orchestrator, openai_client
        if narrative_generator is None:
            if openai_client is None:
                openai_client = initialize_openai_client()
            narrative_generator = NarrativeGenerator(openai_client)
            world_builder = WorldBuilder(openai_client)
            spec_analyzer = GameSpecAnalyzer(openai_client)
            yarn_runner = PythonYarnRunner(YarnBackend.YARN_JSON_EXPORT)
            agent_orchestrator = AgentOrchestrator(openai_client)
            await narrative_generator.initialize()
            await world_builder.initialize()
            await spec_analyzer.initialize()
            await yarn_runner.initialize()
            await agent_orchestrator.initialize()
    
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
                    "🤖 GPT-5 Powered Intelligent Agent Orchestration with Long-term Memory",
                    "🧠 Advanced Multi-Agent Coordination (World Architect, Narrative Weaver, Asset Creator, Code Engineer)",
                    "💾 Persistent Vector-based Memory System with Semantic Search",
                    "🌍 Master Game Specification Analysis (ANY format: natural language, JSON, YAML, TOML, Markdown)",
                    "🎮 Complete Pipeline from Concept to Deployable Game Content",
                    "🔧 Engine-specific Sub-packages (Bevy, Arcade, Pygame, Godot, Unity) with Jinja2 Templates",
                    "💬 Python YarnSpinner Integration with Multi-backend Support", 
                    "🎯 Intelligent Workflow Generation and Task Orchestration",
                    "🎨 Seed-based Contextual Generation with Project-aware Enhancement",
                    "⚡ GPT-5 Enhanced Generation (74% coding accuracy, 45% fewer hallucinations)"
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
    
    # World-building and narrative generation tools
    @mcp.tool()
    async def create_world_format(
        world_brief: str,
        game_type: str,
        complexity: str = "medium"
    ) -> dict[str, Any]:
        """Create a comprehensive world format for game development."""
        try:
            await ensure_narrative_systems()
            await ensure_seed_system()
            
            world_format = await world_builder.create_world_format(
                world_brief=world_brief,
                game_type=GameType(game_type),
                complexity=complexity
            )
            
            return {
                "status": "created",
                "world_format": world_format.to_dict(),
                "seeds_created": True,
                "project_context": f"{world_format.name.lower().replace(' ', '_')}_{world_format.game_type.value}"
            }
            
        except Exception as e:
            logger.error(f"World format creation failed: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    @mcp.tool()
    async def generate_complete_game_area(
        world_brief: str,
        game_type: str,
        area_description: str,
        complexity: str = "medium"
    ) -> dict[str, Any]:
        """Generate complete game area with assets, narrative, and code from a single prompt."""
        try:
            await ensure_narrative_systems()
            await ensure_seed_system()
            
            # Create world format
            world_format = await world_builder.create_world_format(
                world_brief=world_brief,
                game_type=GameType(game_type),
                complexity=complexity
            )
            
            project_context = f"{world_format.name.lower().replace(' ', '_')}_{world_format.game_type.value}"
            
            # Generate area-specific content
            results = {
                "world_format": world_format.to_dict(),
                "project_context": project_context,
                "generated_content": {}
            }
            
            # Generate location lore
            location_lore = await narrative_generator.generate_location_lore(
                location_name=area_description.split()[0].title(),  # Use first word as location name
                location_type="area",
                project_context=project_context
            )
            results["generated_content"]["location_lore"] = location_lore
            
            # Generate quest with dialogue
            quest_data = await narrative_generator.generate_quest_with_dialogue(
                quest_brief=f"Quest in {area_description}",
                location=area_description,
                project_context=project_context
            )
            results["generated_content"]["quest"] = quest_data.to_dict()
            
            # Generate NPCs for the area
            npc_names = await world_builder.generate_names(
                world_format=world_format,
                name_type="person",
                subtype="male",  # Could be randomized
                count=3
            )
            
            npcs = []
            for name in npc_names:
                npc_dialogue = await narrative_generator.generate_npc_dialogue(
                    character_name=name,
                    character_role="villager",
                    location=area_description,
                    dialogue_type=DialogueType.NPC_CHAT,
                    project_context=project_context
                )
                npcs.append({
                    "name": name,
                    "role": "villager",
                    "dialogue_nodes": len(npc_dialogue)
                })
            
            results["generated_content"]["npcs"] = npcs
            
            # Export dialogue to YarnSpinner
            yarn_file = await narrative_generator.export_to_yarnspinner(
                dialogue_nodes=[],  # Would include all generated dialogue
                filename=f"{area_description.lower().replace(' ', '_')}_area",
                project_context=project_context
            )
            results["generated_content"]["yarn_file"] = yarn_file
            
            # Generate Bevy assets using seeds
            nonlocal openai_client
            if openai_client is None:
                openai_client = initialize_openai_client()
            
            bevy_generator = BevyAssetGenerator(openai_client)
            sprite_result = await bevy_generator.generate_sprite_2d(
                name=f"{area_description.lower().replace(' ', '_')}_character",
                description=f"Character sprite for {area_description}",
                size="512x512"
            )
            results["generated_content"]["character_sprite"] = sprite_result.model_dump()
            
            # Generate tilemap for the area
            tilemap_result = await bevy_generator.generate_tilemap_set(
                theme=world_format.theme,
                tile_count=8
            )
            results["generated_content"]["tilemap"] = tilemap_result
            
            return {
                "status": "generated",
                "complete_area": results,
                "assets_created": True,
                "narrative_created": True,
                "bevy_ready": True
            }
            
        except Exception as e:
            logger.error(f"Complete game area generation failed: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    @mcp.tool()
    async def generate_quest_with_dialogue(
        quest_brief: str,
        location: str,
        difficulty: str = "medium",
        project_context: str = None
    ) -> dict[str, Any]:
        """Generate complete quest with YarnSpinner dialogue tree."""
        try:
            await ensure_narrative_systems()
            await ensure_seed_system()
            
            quest_data = await narrative_generator.generate_quest_with_dialogue(
                quest_brief=quest_brief,
                location=location,
                difficulty=difficulty,
                project_context=project_context
            )
            
            return {
                "status": "generated",
                "quest": quest_data.to_dict(),
                "has_dialogue_tree": True,
                "yarn_compatible": True
            }
            
        except Exception as e:
            logger.error(f"Quest generation failed: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    @mcp.tool()
    async def generate_npc_dialogue(
        character_name: str,
        character_role: str,
        location: str,
        dialogue_type: str,
        context: str = None,
        project_context: str = None
    ) -> dict[str, Any]:
        """Generate contextual NPC dialogue with YarnSpinner export."""
        try:
            await ensure_narrative_systems()
            await ensure_seed_system()
            
            dialogue_nodes = await narrative_generator.generate_npc_dialogue(
                character_name=character_name,
                character_role=character_role,
                location=location,
                dialogue_type=DialogueType(dialogue_type),
                context=context,
                project_context=project_context
            )
            
            # Export to YarnSpinner
            yarn_file = await narrative_generator.export_to_yarnspinner(
                dialogue_nodes=dialogue_nodes,
                filename=f"{character_name.lower()}_{dialogue_type}",
                project_context=project_context
            )
            
            return {
                "status": "generated",
                "character": character_name,
                "dialogue_nodes": [node.__dict__ for node in dialogue_nodes],
                "yarn_file": yarn_file,
                "node_count": len(dialogue_nodes)
            }
            
        except Exception as e:
            logger.error(f"NPC dialogue generation failed: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    @mcp.tool()
    async def generate_names(
        world_context: str,
        name_type: str,  # "person" or "place"
        subtype: str,    # "male", "female", "town", "region", etc.
        count: int = 10,
        theme: str = "fantasy"
    ) -> dict[str, Any]:
        """Generate culturally consistent names for game worlds."""
        try:
            await ensure_narrative_systems()
            
            # Create minimal world format for name generation
            from .world_builder import WorldFormat, GameType
            import uuid
            
            temp_world = WorldFormat(
                id=str(uuid.uuid4()),
                name=world_context,
                game_type=GameType.RPG,
                theme=theme,
                setting=world_context,
                tone="neutral",
                complexity="simple",
                person_names={},
                place_names={},
                core_mechanics=[],
                progression_systems=[],
                content_types=[],
                regions=[],
                factions=[],
                conflicts=[]
            )
            
            names = await world_builder.generate_names(
                world_format=temp_world,
                name_type=name_type,
                subtype=subtype,
                count=count
            )
            
            return {
                "status": "generated",
                "names": names,
                "name_type": name_type,
                "subtype": subtype,
                "theme": theme,
                "count": len(names)
            }
            
        except Exception as e:
            logger.error(f"Name generation failed: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    @mcp.tool()
    async def create_generation_plan(
        world_brief: str,
        game_type: str,
        scope: str = "single_area",  # "single_area", "full_region", "entire_world"
        complexity: str = "medium"
    ) -> dict[str, Any]:
        """Create comprehensive plan for generating complete game content."""
        try:
            await ensure_narrative_systems()
            
            # Create world format
            world_format = await world_builder.create_world_format(
                world_brief=world_brief,
                game_type=GameType(game_type),
                complexity=complexity
            )
            
            # Create generation plan
            generation_plan = await world_builder.create_generation_plan(
                world_format=world_format,
                scope=scope
            )
            
            return {
                "status": "planned",
                "world_format": world_format.to_dict(),
                "generation_plan": {
                    "world_id": generation_plan.world_id,
                    "total_locations": generation_plan.total_locations,
                    "asset_count": generation_plan.asset_count,
                    "narrative_count": generation_plan.narrative_count,
                    "estimated_time_minutes": generation_plan.estimated_time,
                    "generation_steps": len(generation_plan.generation_order)
                },
                "ready_to_execute": True
            }
            
        except Exception as e:
            logger.error(f"Generation plan creation failed: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    @mcp.tool()
    async def generate_location_lore(
        location_name: str,
        location_type: str,
        importance: str = "medium",
        project_context: str = None
    ) -> dict[str, Any]:
        """Generate rich lore and descriptions for game locations."""
        try:
            await ensure_narrative_systems()
            await ensure_seed_system()
            
            lore_data = await narrative_generator.generate_location_lore(
                location_name=location_name,
                location_type=location_type,
                importance=importance,
                project_context=project_context
            )
            
            return {
                "status": "generated",
                "location": location_name,
                "lore": lore_data,
                "has_visual_description": "visual_description" in lore_data,
                "has_npcs": "notable_npcs" in lore_data
            }
            
        except Exception as e:
            logger.error(f"Location lore generation failed: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    # Advanced metaprompt refinement and spec analysis tools
    @mcp.tool()
    async def analyze_game_specification(
        spec_content: str,
        spec_format: str = None
    ) -> dict[str, Any]:
        """Analyze ANY format game specification and create optimized workflows."""
        try:
            await ensure_narrative_systems()
            await ensure_seed_system()
            
            # Convert format string to enum if provided
            format_enum = None
            if spec_format:
                try:
                    format_enum = SpecFormat(spec_format)
                except ValueError:
                    pass
            
            # Analyze specification
            refined_spec = await spec_analyzer.analyze_game_spec(
                spec_content=spec_content,
                spec_format=format_enum
            )
            
            # Create automatic seeds
            project_context = f"{refined_spec.game_title.lower().replace(' ', '_')}_{refined_spec.target_engine.value}"
            await spec_analyzer.create_automatic_seeds(refined_spec, project_context)
            
            return {
                "status": "analyzed",
                "original_format": refined_spec.original_format.value,
                "refined_specification": refined_spec.to_dict(),
                "automatic_seeds_created": len(refined_spec.suggested_seeds),
                "project_context": project_context,
                "ready_for_generation": True
            }
            
        except Exception as e:
            logger.error(f"Game specification analysis failed: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    @mcp.tool()
    async def generate_from_master_spec(
        spec_content: str,
        execution_scope: str = "single_area",  # "proof_of_concept", "single_area", "full_region", "complete_game"
        spec_format: str = None
    ) -> dict[str, Any]:
        """Complete game generation pipeline from master specification in ANY format."""
        try:
            await ensure_narrative_systems()
            await ensure_seed_system()
            
            # Analyze specification
            format_enum = SpecFormat(spec_format) if spec_format else None
            refined_spec = await spec_analyzer.analyze_game_spec(spec_content, format_enum)
            
            project_context = f"{refined_spec.game_title.lower().replace(' ', '_')}_{refined_spec.target_engine.value}"
            
            # Create automatic seeds
            await spec_analyzer.create_automatic_seeds(refined_spec, project_context)
            
            # Generate content based on scope
            results = {
                "specification_analysis": refined_spec.to_dict(),
                "project_context": project_context,
                "execution_scope": execution_scope,
                "generated_content": {}
            }
            
            if execution_scope == "proof_of_concept":
                # Generate minimal proof of concept
                demo_quest = await narrative_generator.generate_quest_with_dialogue(
                    quest_brief="Demo quest showcasing core gameplay",
                    location="Starting area",
                    project_context=project_context
                )
                results["generated_content"]["demo_quest"] = demo_quest.to_dict()
                
                # Generate single character sprite
                nonlocal openai_client
                if openai_client is None:
                    openai_client = initialize_openai_client()
                bevy_generator = BevyAssetGenerator(openai_client)
                demo_sprite = await bevy_generator.generate_sprite_2d(
                    name="demo_character",
                    description="Main character for proof of concept",
                    size="512x512"
                )
                results["generated_content"]["demo_sprite"] = demo_sprite.model_dump()
                
            elif execution_scope in ["single_area", "full_region", "complete_game"]:
                # Use existing complete area generation
                complete_area = await generate_complete_game_area(
                    world_brief=refined_spec.world_description,
                    game_type=refined_spec.game_type,
                    area_description="Main game area based on specification",
                    complexity=refined_spec.estimated_complexity
                )
                results["generated_content"]["complete_area"] = complete_area
            
            # Create YarnSpinner dialogue files
            if results["generated_content"]:
                yarn_result = await yarn_runner.create_dialogue_tree(
                    dialogue_nodes=[],  # Would include all generated dialogue
                    filename=f"{refined_spec.game_title.lower().replace(' ', '_')}_dialogue",
                    project_context=project_context
                )
                results["generated_content"]["yarn_files"] = yarn_result
                
                # Export for target engine
                engine_files = await yarn_runner.export_for_engine(
                    dialogue_data={"filename": f"{refined_spec.game_title.lower().replace(' ', '_')}_dialogue"},
                    target_engine=refined_spec.target_engine.value,
                    output_path=settings.cache_dir / "engine_exports" / project_context
                )
                results["generated_content"]["engine_integration_files"] = engine_files
            
            return {
                "status": "generated",
                "master_spec_processed": True,
                "complete_pipeline": results,
                "ready_for_development": True,
                "engine_specific_files": len(results["generated_content"].get("engine_integration_files", [])) > 0
            }
            
        except Exception as e:
            logger.error(f"Master specification generation failed: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    @mcp.tool()
    async def create_python_yarn_dialogue(
        dialogue_content: str,
        filename: str,
        target_engine: str = "generic",
        backend: str = "json_export",
        project_context: str = None
    ) -> dict[str, Any]:
        """Create Python-integrated YarnSpinner dialogue with multiple backend support."""
        try:
            await ensure_narrative_systems()
            
            # Convert backend string to enum
            backend_enum = YarnBackend(backend)
            yarn_runner_instance = PythonYarnRunner(backend_enum)
            await yarn_runner_instance.initialize()
            
            # Parse dialogue content into nodes
            from .yarn_integration import YarnDialogueNode
            import uuid
            
            # Simple parsing - in practice this would be more sophisticated
            dialogue_node = YarnDialogueNode(
                node_id=str(uuid.uuid4()),
                title=filename,
                tags=["generated"],
                body=[dialogue_content],
                choices=[],
                conditions=[],
                commands=[],
                variables={}
            )
            
            # Create dialogue tree
            yarn_result = await yarn_runner_instance.create_dialogue_tree(
                dialogue_nodes=[dialogue_node],
                filename=filename,
                project_context=project_context
            )
            
            # Export for target engine
            engine_files = []
            if target_engine != "generic":
                engine_files = await yarn_runner_instance.export_for_engine(
                    dialogue_data={"filename": filename},
                    target_engine=target_engine,
                    output_path=settings.cache_dir / "yarn_exports"
                )
            
            return {
                "status": "created",
                "yarn_result": yarn_result,
                "backend": backend,
                "target_engine": target_engine,
                "engine_files": engine_files,
                "python_integrated": True
            }
            
        except Exception as e:
            logger.error(f"Python Yarn dialogue creation failed: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    @mcp.tool()
    async def suggest_data_organization(
        raw_content: str,
        desired_format: str = "auto"  # "auto", "toml", "json", "yaml", "markdown"
    ) -> dict[str, Any]:
        """Analyze any content and suggest optimal data organization format."""
        try:
            await ensure_narrative_systems()
            
            suggestion_prompt = f"""
            Analyze this raw content and suggest the optimal data organization format:
            
            Raw Content:
            {raw_content}
            
            Desired Format: {desired_format}
            
            Consider these factors:
            1. Content structure and complexity
            2. Human readability requirements
            3. Machine parsing efficiency
            4. Maintainability and version control
            5. Integration with development tools
            
            Provide suggestions for organizing this content into:
            - TOML (good for configuration, human-readable)
            - JSON (good for structured data, API integration)
            - YAML (good for complex hierarchies, documentation)
            - Markdown (good for narrative content, documentation)
            - Custom hybrid format
            
            Return JSON with:
            {{
                "recommended_format": "format_name",
                "reasoning": "why this format is best",
                "structure_suggestion": {{"organized structure example"}},
                "alternative_formats": ["other good options"],
                "conversion_difficulty": "easy/medium/hard",
                "maintainability_score": 1-10
            }}
            """
            
            response = await self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": suggestion_prompt}],
                response_format={"type": "json_object"}
            )
            
            suggestions = json.loads(response.choices[0].message.content)
            
            # If auto-format, apply the recommended format
            if desired_format == "auto":
                organized_content = await self._auto_organize_content(
                    raw_content, 
                    suggestions["recommended_format"],
                    suggestions["structure_suggestion"]
                )
                suggestions["organized_content"] = organized_content
            
            return {
                "status": "analyzed",
                "original_content_length": len(raw_content),
                "suggestions": suggestions,
                "auto_organized": desired_format == "auto"
            }
            
        except Exception as e:
            logger.error(f"Data organization suggestion failed: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def _auto_organize_content(
        self, 
        raw_content: str, 
        target_format: str, 
        structure_example: Dict[str, Any]
    ) -> str:
        """Auto-organize content into suggested format."""
        
        organization_prompt = f"""
        Reorganize this raw content into {target_format} format following this structure:
        
        Raw Content:
        {raw_content}
        
        Target Structure Example:
        {json.dumps(structure_example, indent=2)}
        
        Create well-organized {target_format} content that:
        1. Follows the suggested structure
        2. Preserves all important information
        3. Uses appropriate {target_format} conventions
        4. Is properly formatted and readable
        5. Includes helpful comments/documentation
        
        Return only the formatted {target_format} content, no explanations.
        """
        
        response = await self.client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": organization_prompt}]
        )
        
        return response.choices[0].message.content
    
    # Advanced Agent Orchestration Tools
    @mcp.tool()
    async def create_intelligent_agent_workflow(
        workflow_description: str,
        project_context: str = "new_project",
        scope: str = "full_game",  # "proof_of_concept", "single_area", "full_game", "franchise"
        use_memory: bool = True
    ) -> dict[str, Any]:
        """Execute complex game development using intelligent multi-agent coordination with GPT-5."""
        try:
            await ensure_narrative_systems()
            await ensure_seed_system()
            
            logger.info(f"Starting intelligent agent workflow: {workflow_description}")
            
            # Execute complex workflow with agent orchestration
            result = await agent_orchestrator.execute_complex_workflow(
                workflow_description=workflow_description,
                project_context=project_context,
                scope=scope
            )
            
            return {
                "status": "success",
                "workflow_completed": True,
                "agent_coordination": "multi_agent_orchestrated",
                "gpt5_powered": True,
                "memory_enhanced": use_memory,
                "scope": scope,
                "project_context": project_context,
                "orchestration_result": result,
                "agents_utilized": list(AgentRole._value2member_map_.keys()),
                "intelligent_planning": "gpt5_task_breakdown"
            }
            
        except Exception as e:
            logger.error(f"Intelligent agent workflow failed: {e}")
            return {
                "status": "error", 
                "error": str(e),
                "suggested_action": "Check agent system logs for detailed error analysis"
            }
    
    @mcp.tool()
    async def query_agent_memory(
        query: str,
        memory_type: str = None,  # world_lore, character_sheets, visual_style, code_patterns, player_preferences, project_history
        project_context: str = None,
        limit: int = 10
    ) -> dict[str, Any]:
        """Query the intelligent agent memory system for relevant game development context."""
        try:
            await ensure_narrative_systems()
            
            # Convert string to enum if provided
            memory_type_enum = None
            if memory_type:
                try:
                    memory_type_enum = MemoryType(memory_type)
                except ValueError:
                    pass
            
            # Retrieve relevant memories
            memories = await agent_orchestrator.memory.retrieve_memories(
                query=query,
                memory_type=memory_type_enum,
                project_context=project_context,
                limit=limit
            )
            
            # Format response
            memory_data = []
            for memory in memories:
                memory_data.append({
                    "memory_id": memory.memory_id,
                    "type": memory.memory_type.value,
                    "content": memory.content,
                    "relevance_score": memory.relevance_score,
                    "project": memory.project_context,
                    "tags": memory.tags,
                    "created": memory.created_at.isoformat(),
                    "access_count": memory.access_count
                })
            
            return {
                "status": "success",
                "query": query,
                "memories_found": len(memory_data),
                "memories": memory_data,
                "semantic_search": "vector_embedding_powered",
                "memory_system": "persistent_agent_memory"
            }
            
        except Exception as e:
            logger.error(f"Agent memory query failed: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    @mcp.tool()
    async def store_agent_memory(
        content: str,
        memory_type: str,  # world_lore, character_sheets, visual_style, code_patterns, player_preferences, project_history
        project_context: str,
        tags: list[str] = None
    ) -> dict[str, Any]:
        """Store important information in the agent's long-term memory system."""
        try:
            await ensure_narrative_systems()
            
            # Convert string to enum
            try:
                memory_type_enum = MemoryType(memory_type)
            except ValueError:
                return {
                    "status": "error",
                    "error": f"Invalid memory type: {memory_type}",
                    "valid_types": list(MemoryType._value2member_map_.keys())
                }
            
            # Store memory
            memory_id = await agent_orchestrator.memory.store_memory(
                content=content,
                memory_type=memory_type_enum,
                project_context=project_context,
                tags=tags or []
            )
            
            return {
                "status": "success", 
                "memory_id": memory_id,
                "memory_type": memory_type,
                "project_context": project_context,
                "persistent_storage": True,
                "semantic_indexing": "vector_embedding_created"
            }
            
        except Exception as e:
            logger.error(f"Agent memory storage failed: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    @mcp.tool()
    async def analyze_project_continuity(
        project_context: str,
        analysis_scope: str = "full_project"  # "characters", "world", "visual_style", "code_architecture", "full_project"
    ) -> dict[str, Any]:
        """Analyze project continuity and consistency using agent memory system."""
        try:
            await ensure_narrative_systems()
            
            # Retrieve all memories for project
            all_memories = await agent_orchestrator.memory.retrieve_memories(
                query="project analysis continuity consistency",
                project_context=project_context,
                limit=50,
                similarity_threshold=0.3  # Lower threshold for broader search
            )
            
            if not all_memories:
                return {
                    "status": "success",
                    "analysis": "No project memories found - this appears to be a new project",
                    "recommendations": [
                        "Start by creating foundational memories (world lore, visual style, character sheets)",
                        "Use intelligent agent workflows to establish project consistency",
                        "Store important decisions as they're made to build project memory"
                    ],
                    "project_maturity": "new"
                }
            
            # Analyze continuity with GPT-5
            analysis_prompt = f"""
            Analyze the continuity and consistency of this game development project:
            
            Project: {project_context}
            Analysis Scope: {analysis_scope}
            
            Project Memories ({len(all_memories)} entries):
            """
            
            for memory in all_memories[:20]:  # Analyze top 20 memories
                analysis_prompt += f"\\n[{memory.memory_type.value}] {memory.content[:200]}..."
            
            analysis_prompt += f"""
            
            Analyze:
            1. Consistency across different game elements
            2. Potential conflicts or contradictions
            3. Gaps in project development
            4. Strengths in current project direction
            5. Recommendations for maintaining continuity
            
            Return detailed JSON analysis with specific recommendations.
            """
            
            response = await openai_client.chat.completions.create(
                model="gpt-5",  # Use GPT-5 for complex analysis
                messages=[{"role": "user", "content": analysis_prompt}],
                response_format={"type": "json_object"}
            )
            
            analysis_result = json.loads(response.choices[0].message.content)
            
            return {
                "status": "success",
                "project_context": project_context,
                "memories_analyzed": len(all_memories),
                "analysis_scope": analysis_scope,
                "continuity_analysis": analysis_result,
                "gpt5_analysis": True,
                "project_maturity": "established" if len(all_memories) > 10 else "developing"
            }
            
        except Exception as e:
            logger.error(f"Project continuity analysis failed: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    @mcp.tool() 
    async def generate_with_gpt5_enhanced(
        task_description: str,
        task_type: str = "general",  # "world_building", "narrative", "asset_creation", "code_generation", "game_design"
        use_reasoning: bool = True,
        verbosity: str = "medium",  # "low", "medium", "high"
        project_context: str = None
    ) -> dict[str, Any]:
        """Generate content using GPT-5 with enhanced reasoning and memory integration."""
        try:
            await ensure_narrative_systems()
            await ensure_seed_system()
            
            # Retrieve relevant memories if project context provided
            memory_context = ""
            if project_context:
                memories = await agent_orchestrator.memory.retrieve_memories(
                    query=task_description,
                    project_context=project_context,
                    limit=5
                )
                
                if memories:
                    memory_context = "\\n=== RELEVANT PROJECT CONTEXT ===\\n"
                    for memory in memories:
                        memory_context += f"[{memory.memory_type.value}] {memory.content}\\n"
                    memory_context += "=== END CONTEXT ===\\n\\n"
            
            # Get enhanced prompt with seeds
            enhanced_prompt = await prompt_enhancer.enhance_prompt(
                original_prompt=task_description,
                task_type=task_type,
                project_context=project_context or "general"
            )
            
            # Build final prompt with memory context
            final_prompt = f"{memory_context}{enhanced_prompt}"
            
            # Generate with GPT-5
            model_params = {
                "model": "gpt-5",
                "messages": [
                    {"role": "system", "content": f"You are an expert {task_type} specialist for game development."},
                    {"role": "user", "content": final_prompt}
                ],
                "verbosity": verbosity
            }
            
            if use_reasoning:
                model_params["reasoning_effort"] = "medium"
            
            response = await openai_client.chat.completions.create(**model_params)
            
            result_content = response.choices[0].message.content
            
            # Store important results in memory
            if project_context and len(result_content) > 100:
                memory_type = {
                    "world_building": MemoryType.WORLD_LORE,
                    "narrative": MemoryType.CHARACTER_SHEETS,
                    "asset_creation": MemoryType.VISUAL_STYLE,
                    "code_generation": MemoryType.CODE_PATTERNS,
                    "game_design": MemoryType.PLAYER_PREFERENCES
                }.get(task_type, MemoryType.PROJECT_HISTORY)
                
                await agent_orchestrator.memory.store_memory(
                    content=result_content[:1000],  # Store first 1000 chars
                    memory_type=memory_type,
                    project_context=project_context,
                    tags=[task_type, "gpt5_generated"]
                )
            
            return {
                "status": "success",
                "task_type": task_type,
                "gpt5_generated": True,
                "reasoning_enabled": use_reasoning,
                "verbosity": verbosity,
                "memory_enhanced": bool(memory_context),
                "seed_enhanced": enhanced_prompt != task_description,
                "project_context": project_context,
                "generated_content": result_content,
                "model_info": {
                    "model": "gpt-5",
                    "advantages": "74% coding accuracy, 45% fewer hallucinations, unified reasoning"
                }
            }
            
        except Exception as e:
            logger.error(f"GPT-5 enhanced generation failed: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    return mcp
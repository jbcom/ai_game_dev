"""Configuration-based batch processing with TOML/YAML/JSON support."""

import asyncio
import json
from pathlib import Path
from typing import Any, Dict, List, Union

import aiofiles
try:
    import tomllib
except ImportError:
    import tomli as tomllib
try:
    import yaml
except ImportError:
    yaml = None

from .advanced_generators import AdvancedImageGenerator, VisionVerifier
from .workflow_generator import WorkflowAnalyzer
from .config import settings
from .logging_config import get_logger
from .models import (
    WorkflowSpec, UIElementSpec, ImageEditRequest, VerificationCriteria,
    GenerationResult, TaskAnalysisResult
)

logger = get_logger(__name__, component="config_batch")


class ConfigBatchProcessor:
    """Process batch specifications from configuration files."""
    
    def __init__(self, openai_client, generator: AdvancedImageGenerator, verifier: VisionVerifier, analyzer: WorkflowAnalyzer):
        self.client = openai_client
        self.generator = generator
        self.verifier = verifier
        self.analyzer = analyzer
    
    async def process_config_file(self, config_path: str) -> Dict[str, Any]:
        """Process batch configuration from file."""
        
        config_file = Path(config_path)
        if not config_file.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        logger.info(f"Processing configuration file: {config_path}")
        
        # Load configuration based on file extension
        if config_file.suffix.lower() == '.toml':
            config_data = await self._load_toml_config(config_file)
        elif config_file.suffix.lower() in ['.yaml', '.yml']:
            config_data = await self._load_yaml_config(config_file)
        elif config_file.suffix.lower() == '.json':
            config_data = await self._load_json_config(config_file)
        else:
            raise ValueError(f"Unsupported config format: {config_file.suffix}")
        
        # Process the configuration
        return await self._process_config_data(config_data)
    
    async def process_workflow_config(self, workflow_spec: WorkflowSpec) -> Dict[str, Any]:
        """Process a workflow specification."""
        
        logger.info(f"Processing workflow: {workflow_spec.name}")
        
        results = {
            "workflow_name": workflow_spec.name,
            "type": workflow_spec.type,
            "ui_elements": [],
            "image_edits": [],
            "verification_results": [],
            "summary": {
                "total_operations": 0,
                "successful": 0,
                "failed": 0,
                "cached": 0
            }
        }
        
        try:
            # Process UI elements
            if workflow_spec.ui_elements:
                ui_results = await self._process_ui_elements(workflow_spec.ui_elements, workflow_spec.verification)
                results["ui_elements"] = ui_results
                results["summary"]["total_operations"] += len(ui_results)
                results["summary"]["successful"] += sum(1 for r in ui_results if "error" not in r)
            
            # Process image edits
            if workflow_spec.image_edits:
                edit_results = await self._process_image_edits(workflow_spec.image_edits, workflow_spec.verification)
                results["image_edits"] = edit_results
                results["summary"]["total_operations"] += len(edit_results)
                results["summary"]["successful"] += sum(1 for r in edit_results if "error" not in r)
            
            logger.info(f"Workflow completed: {results['summary']['successful']}/{results['summary']['total_operations']} successful")
            return results
            
        except Exception as e:
            logger.error(f"Workflow processing failed: {e}")
            results["error"] = str(e)
            return results
    
    async def _load_toml_config(self, config_file: Path) -> Dict[str, Any]:
        """Load TOML configuration file."""
        async with aiofiles.open(config_file, 'rb') as f:
            content = await f.read()
            return tomllib.load(content)
    
    async def _load_yaml_config(self, config_file: Path) -> Dict[str, Any]:
        """Load YAML configuration file."""
        if yaml is None:
            raise ImportError("PyYAML is required for YAML config support. Install with: pip install pyyaml")
        
        async with aiofiles.open(config_file, 'r') as f:
            content = await f.read()
            return yaml.safe_load(content)
    
    async def _load_json_config(self, config_file: Path) -> Dict[str, Any]:
        """Load JSON configuration file."""
        async with aiofiles.open(config_file, 'r') as f:
            content = await f.read()
            return json.loads(content)
    
    async def _process_config_data(self, config_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process loaded configuration data."""
        
        results = {"config_processed": True, "workflows": [], "high_level_tasks": []}
        
        # Check for high-level task descriptions
        if "task" in config_data or "description" in config_data:
            task_description = config_data.get("task", config_data.get("description", ""))
            
            logger.info(f"Analyzing high-level task: {task_description[:100]}...")
            analysis = await self.analyzer.analyze_task(task_description)
            
            # Execute the suggested workflow
            workflow_result = await self.process_workflow_config(analysis.suggested_workflow)
            
            results["high_level_tasks"].append({
                "task": task_description,
                "analysis": analysis.model_dump(),
                "execution_result": workflow_result
            })
        
        # Check for explicit workflow specifications
        if "workflows" in config_data:
            for workflow_config in config_data["workflows"]:
                try:
                    workflow_spec = self._parse_workflow_config(workflow_config)
                    workflow_result = await self.process_workflow_config(workflow_spec)
                    results["workflows"].append(workflow_result)
                except Exception as e:
                    logger.error(f"Failed to process workflow: {e}")
                    results["workflows"].append({"error": str(e), "config": workflow_config})
        
        # Check for batch image generation
        if "batch_images" in config_data:
            batch_result = await self._process_batch_images(config_data["batch_images"])
            results["batch_images"] = batch_result
        
        # Check for UI element specifications
        if "ui_elements" in config_data:
            ui_result = await self._process_ui_config(config_data["ui_elements"])
            results["ui_elements"] = ui_result
        
        return results
    
    def _parse_workflow_config(self, workflow_config: Dict[str, Any]) -> WorkflowSpec:
        """Parse workflow configuration into WorkflowSpec."""
        
        # Parse UI elements
        ui_elements = []
        if "ui_elements" in workflow_config:
            for ui_config in workflow_config["ui_elements"]:
                ui_element = UIElementSpec(
                    element_type=ui_config.get("type", "button"),
                    style_theme=ui_config.get("style", "modern"),
                    size=ui_config.get("size", "1024x1024"),
                    color_scheme=ui_config.get("colors", []),
                    state_variants=ui_config.get("states", []),
                    text_content=ui_config.get("text"),
                    special_effects=ui_config.get("effects", [])
                )
                ui_elements.append(ui_element)
        
        # Parse image edits
        image_edits = []
        if "image_edits" in workflow_config:
            for edit_config in workflow_config["image_edits"]:
                # This would need to be more sophisticated in practice
                image_edit = ImageEditRequest(
                    source_image_path=edit_config["source"],
                    prompt=edit_config["prompt"],
                    operation=edit_config.get("operation", "edit"),
                    iterations=edit_config.get("iterations", 1)
                )
                image_edits.append(image_edit)
        
        # Parse verification criteria
        verification_config = workflow_config.get("verification", {})
        verification = VerificationCriteria(
            mode=verification_config.get("mode", "basic"),
            required_objects=verification_config.get("required_objects", []),
            forbidden_objects=verification_config.get("forbidden_objects", []),
            style_consistency=verification_config.get("style_consistency", True),
            quality_threshold=verification_config.get("quality_threshold", 0.7),
            max_regenerations=verification_config.get("max_regenerations", 2)
        )
        
        # Create workflow spec
        return WorkflowSpec(
            name=workflow_config.get("name", "Generated Workflow"),
            type=workflow_config.get("type", "custom"),
            description=workflow_config.get("description", ""),
            ui_elements=ui_elements,
            image_edits=image_edits,
            verification=verification,
            batch_settings=workflow_config.get("batch_settings", {}),
            output_format=workflow_config.get("output_format", "png"),
            optimization_level=workflow_config.get("optimization", "balanced")
        )
    
    async def _process_ui_elements(
        self, 
        ui_elements: List[UIElementSpec], 
        verification: VerificationCriteria
    ) -> List[Dict[str, Any]]:
        """Process UI element generation."""
        
        results = []
        concurrent_limit = 3  # Configurable
        
        # Process elements in batches
        semaphore = asyncio.Semaphore(concurrent_limit)
        
        async def process_single_element(element: UIElementSpec) -> Dict[str, Any]:
            async with semaphore:
                try:
                    # Generate base element
                    prompt = self._create_ui_prompt(element)
                    
                    # Simple generation for now - could be enhanced with specific techniques
                    response = await self.client.images.generate(
                        prompt=prompt,
                        size=element.size,
                        quality="standard",
                        n=1
                    )
                    
                    # Save image
                    from uuid import uuid4
                    element_id = str(uuid4())
                    result_path = await self.generator._save_generated_image(
                        response.data[0].url,
                        f"ui_{element.element_type}_{element_id}",
                        "png"
                    )
                    
                    result = {
                        "element_type": element.element_type,
                        "style_theme": element.style_theme,
                        "file_path": str(result_path),
                        "element_id": element_id,
                        "metadata": element.model_dump()
                    }
                    
                    # Generate state variants if specified
                    if element.state_variants:
                        variants = await self._generate_element_variants(element, str(result_path))
                        result["variants"] = variants
                    
                    # Verify if enabled
                    if verification.mode != "none":
                        verification_result = await self.verifier.verify_generation(
                            str(result_path), verification, prompt
                        )
                        result["verification"] = verification_result
                    
                    return result
                    
                except Exception as e:
                    logger.error(f"UI element generation failed: {e}")
                    return {
                        "element_type": element.element_type,
                        "error": str(e),
                        "metadata": element.model_dump()
                    }
        
        # Process all elements concurrently
        tasks = [process_single_element(element) for element in ui_elements]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle exceptions
        processed_results = []
        for result in results:
            if isinstance(result, Exception):
                processed_results.append({"error": str(result)})
            else:
                processed_results.append(result)
        
        return processed_results
    
    async def _process_image_edits(
        self,
        image_edits: List[ImageEditRequest],
        verification: VerificationCriteria
    ) -> List[Dict[str, Any]]:
        """Process image editing requests."""
        
        results = []
        
        for edit_request in image_edits:
            try:
                logger.info(f"Processing image edit: {edit_request.prompt[:50]}...")
                
                # Perform targeted edit
                edit_result = await self.generator.targeted_edit(edit_request)
                
                result = {
                    "source_image": edit_request.source_image_path,
                    "prompt": edit_request.prompt,
                    "operation": edit_request.operation,
                    "result_path": edit_result.file_path,
                    "edit_id": edit_result.id,
                    "iterations": len(edit_result.edit_history),
                    "metadata": edit_result.metadata
                }
                
                # Verify with regeneration if enabled
                if verification.mode != "none":
                    verified_result = await self.verifier.verify_with_regeneration(
                        self.generator, edit_result, verification, edit_request.prompt
                    )
                    result["verification"] = verified_result.verification_result
                    result["regeneration_count"] = verified_result.regeneration_count
                    result["final_path"] = verified_result.file_path
                
                results.append(result)
                
            except Exception as e:
                logger.error(f"Image edit failed: {e}")
                results.append({
                    "source_image": edit_request.source_image_path,
                    "prompt": edit_request.prompt,
                    "error": str(e)
                })
        
        return results
    
    async def _process_batch_images(self, batch_config: Dict[str, Any]) -> Dict[str, Any]:
        """Process batch image generation configuration."""
        
        prompts = batch_config.get("prompts", [])
        size = batch_config.get("size", "1024x1024")
        quality = batch_config.get("quality", "standard")
        
        if not prompts:
            return {"error": "No prompts specified for batch generation"}
        
        try:
            # Use existing batch processor
            from .batch_processor import BatchProcessor
            batch_processor = BatchProcessor(self.client)
            
            results = await batch_processor.batch_generate_images(prompts, size, quality)
            return {"batch_results": results, "total_images": len(results)}
            
        except Exception as e:
            logger.error(f"Batch image generation failed: {e}")
            return {"error": str(e)}
    
    async def _process_ui_config(self, ui_config: Dict[str, Any]) -> Dict[str, Any]:
        """Process UI-specific configuration."""
        
        theme = ui_config.get("theme", "modern")
        elements = ui_config.get("elements", [])
        
        if not elements:
            return {"error": "No UI elements specified"}
        
        # Convert to UIElementSpec objects
        ui_elements = []
        for element_config in elements:
            element = UIElementSpec(
                element_type=element_config.get("type", "button"),
                style_theme=theme,
                size=element_config.get("size", "512x512"),
                color_scheme=element_config.get("colors", []),
                state_variants=element_config.get("states", []),
                text_content=element_config.get("text"),
                special_effects=element_config.get("effects", [])
            )
            ui_elements.append(element)
        
        # Process elements
        verification = VerificationCriteria(mode="basic")
        results = await self._process_ui_elements(ui_elements, verification)
        
        return {"ui_results": results, "theme": theme}
    
    def _create_ui_prompt(self, element: UIElementSpec) -> str:
        """Create generation prompt for UI element."""
        
        prompt_parts = [
            f"Create a {element.element_type} UI element",
            f"Style: {element.style_theme}",
        ]
        
        if element.color_scheme:
            prompt_parts.append(f"Colors: {', '.join(element.color_scheme)}")
        
        if element.text_content:
            prompt_parts.append(f"Text: '{element.text_content}'")
        
        if element.special_effects:
            prompt_parts.append(f"Effects: {', '.join(element.special_effects)}")
        
        prompt_parts.extend([
            "Clean design, professional quality",
            "PNG format with transparent background",
            "Modern UI/UX design principles"
        ])
        
        return ", ".join(prompt_parts)
    
    async def _generate_element_variants(
        self, 
        element: UIElementSpec, 
        base_path: str
    ) -> List[Dict[str, Any]]:
        """Generate state variants for UI element."""
        
        variants = []
        
        for state in element.state_variants:
            try:
                state_prompt = f"UI {element.element_type} in {state} state, {element.style_theme} style"
                
                # Generate variant
                response = await self.client.images.generate(
                    prompt=state_prompt,
                    size=element.size,
                    quality="standard",
                    n=1
                )
                
                # Save variant
                from uuid import uuid4
                variant_id = str(uuid4())
                variant_path = await self.generator._save_generated_image(
                    response.data[0].url,
                    f"ui_{element.element_type}_{state}_{variant_id}",
                    "png"
                )
                
                variants.append({
                    "state": state,
                    "file_path": str(variant_path),
                    "variant_id": variant_id
                })
                
            except Exception as e:
                logger.error(f"Variant generation failed for {state}: {e}")
                variants.append({
                    "state": state,
                    "error": str(e)
                })
        
        return variants
"""Advanced image generation with masking, variations, targeted edits and vision verification."""

import asyncio
import base64
import hashlib
import time
import uuid
from pathlib import Path
from typing import Any, Optional

import aiofiles
from openai import AsyncOpenAI
from PIL import Image, ImageDraw

from .config import settings
from .logging_config import get_logger
from .models import (
    EditOperation, GenerationResult, ImageEditRequest, ImageSize, ImageQuality,
    MaskRegion, VerificationCriteria, VerificationMode
)
from .cache_manager import CacheManager
from .utils import ensure_directory_exists


logger = get_logger(__name__, component="advanced_generators")
cache_manager = CacheManager()


class AdvancedImageGenerator:
    """Advanced image generation with masking, variations, and targeted edits."""
    
    def __init__(self, openai_client: AsyncOpenAI):
        self.client = openai_client
        self.generation_cache = cache_manager.memory_cache
    
    async def generate_with_mask(
        self,
        prompt: str,
        mask_regions: list[MaskRegion],
        base_image_path: Optional[str] = None,
        size: ImageSize = "1024x1024",
        quality: ImageQuality = "standard"
    ) -> GenerationResult:
        """Generate image with selective masking for targeted edits."""
        
        operation_id = str(uuid.uuid4())
        cache_key = self._generate_cache_key("mask_generation", {
            "prompt": prompt,
            "mask_regions": [r.model_dump() for r in mask_regions],
            "base_image": base_image_path,
            "size": size,
            "quality": quality
        })
        
        # Check cache first
        cached_result = await self.generation_cache.get(cache_key)
        if cached_result:
            logger.info(f"Using cached masked generation result for {operation_id}")
            return GenerationResult(**cached_result)
        
        try:
            # Create composite mask from all regions
            mask_image = await self._create_composite_mask(mask_regions, size)
            mask_path = await self._save_temp_image(mask_image, f"mask_{operation_id}")
            
            # Prepare image data
            image_data = None
            if base_image_path and Path(base_image_path).exists():
                image_data = await self._load_image_data(base_image_path)
            
            mask_data = await self._load_image_data(mask_path)
            
            # Generate with OpenAI
            if base_image_path:
                # Edit existing image
                response = await self.client.images.edit(
                    image=image_data,
                    mask=mask_data,
                    prompt=prompt,
                    size=size,
                    n=1
                )
            else:
                # Generate new image with inpainting
                response = await self.client.images.generate(
                    prompt=f"Create image: {prompt}",
                    size=size,
                    quality=quality,
                    n=1
                )
            
            # Save result
            result_path = await self._save_generated_image(
                response.data[0].url, f"masked_{operation_id}", "png"
            )
            
            result = GenerationResult(
                id=operation_id,
                type="image",
                file_path=str(result_path),
                metadata={
                    "prompt": prompt,
                    "mask_regions": [r.model_dump() for r in mask_regions],
                    "size": size,
                    "quality": quality,
                    "operation": "masked_generation",
                    "base_image": base_image_path
                },
                cached=False
            )
            
            # Cache result
            await self.generation_cache.set(cache_key, result.model_dump())
            
            return result
            
        except Exception as e:
            logger.error(f"Mask generation failed for {operation_id}: {e}")
            raise
    
    async def create_variations(
        self,
        source_image_path: str,
        variation_prompts: list[str],
        preserve_structure: bool = True,
        size: ImageSize = "1024x1024"
    ) -> list[GenerationResult]:
        """Create multiple variations of a source image."""
        
        if not Path(source_image_path).exists():
            raise FileNotFoundError(f"Source image not found: {source_image_path}")
        
        results = []
        base_id = str(uuid.uuid4())
        
        # Load source image
        image_data = await self._load_image_data(source_image_path)
        
        for i, prompt in enumerate(variation_prompts):
            operation_id = f"{base_id}_var_{i}"
            
            try:
                if preserve_structure:
                    # Use image editing to preserve structure
                    response = await self.client.images.edit(
                        image=image_data,
                        prompt=f"Modify this image: {prompt}",
                        size=size,
                        n=1
                    )
                else:
                    # Create variation using variations endpoint
                    response = await self.client.images.create_variation(
                        image=image_data,
                        size=size,
                        n=1
                    )
                
                # Save variation
                result_path = await self._save_generated_image(
                    response.data[0].url, f"variation_{operation_id}", "png"
                )
                
                result = GenerationResult(
                    id=operation_id,
                    type="image",
                    file_path=str(result_path),
                    metadata={
                        "source_image": source_image_path,
                        "variation_prompt": prompt,
                        "preserve_structure": preserve_structure,
                        "size": size,
                        "operation": "variation"
                    },
                    cached=False
                )
                
                results.append(result)
                logger.info(f"Generated variation {i+1}/{len(variation_prompts)}")
                
            except Exception as e:
                logger.error(f"Variation {i} failed: {e}")
                continue
        
        return results
    
    async def targeted_edit(
        self,
        edit_request: ImageEditRequest
    ) -> GenerationResult:
        """Perform targeted editing with multiple iterations."""
        
        operation_id = str(uuid.uuid4())
        current_image_path = edit_request.source_image_path
        edit_history = []
        
        for iteration in range(edit_request.iterations):
            try:
                logger.info(f"Performing edit iteration {iteration + 1}/{edit_request.iterations}")
                
                if edit_request.mask_regions:
                    # Use masking for targeted edits
                    result = await self.generate_with_mask(
                        prompt=edit_request.prompt,
                        mask_regions=edit_request.mask_regions,
                        base_image_path=current_image_path
                    )
                else:
                    # General image edit
                    image_data = await self._load_image_data(current_image_path)
                    
                    response = await self.client.images.edit(
                        image=image_data,
                        prompt=edit_request.prompt,
                        n=1
                    )
                    
                    result_path = await self._save_generated_image(
                        response.data[0].url, f"edit_{operation_id}_iter_{iteration}", "png"
                    )
                    
                    result = GenerationResult(
                        id=f"{operation_id}_iter_{iteration}",
                        type="image",
                        file_path=str(result_path),
                        metadata={
                            "edit_request": edit_request.model_dump(),
                            "iteration": iteration,
                            "operation": "targeted_edit"
                        },
                        cached=False
                    )
                
                edit_history.append({
                    "iteration": iteration,
                    "prompt": edit_request.prompt,
                    "result_path": result.file_path,
                    "timestamp": time.time()
                })
                
                # Use current result as input for next iteration
                current_image_path = result.file_path
                
            except Exception as e:
                logger.error(f"Edit iteration {iteration} failed: {e}")
                break
        
        # Return final result with complete edit history
        final_result = GenerationResult(
            id=operation_id,
            type="image",
            file_path=current_image_path,
            metadata={
                "edit_request": edit_request.model_dump(),
                "total_iterations": len(edit_history),
                "operation": "targeted_edit_complete"
            },
            cached=False,
            edit_history=edit_history
        )
        
        return final_result
    
    async def _create_composite_mask(
        self,
        mask_regions: list[MaskRegion],
        size: ImageSize
    ) -> Image.Image:
        """Create composite mask from multiple regions."""
        
        width, height = map(int, size.split('x'))
        mask = Image.new('L', (width, height), 0)
        draw = ImageDraw.Draw(mask)
        
        for region in mask_regions:
            x, y, w, h = region.coordinates
            # Apply strength as opacity
            fill_value = int(255 * region.strength)
            draw.rectangle([x, y, x + w, y + h], fill=fill_value)
        
        return mask
    
    async def _load_image_data(self, image_path: str) -> bytes:
        """Load image data for OpenAI API."""
        async with aiofiles.open(image_path, 'rb') as f:
            return await f.read()
    
    async def _save_temp_image(self, image: Image.Image, filename: str) -> Path:
        """Save temporary image file."""
        temp_dir = settings.cache_dir / "temp"
        await ensure_directory_exists(temp_dir)
        
        temp_path = temp_dir / f"{filename}.png"
        image.save(temp_path, "PNG")
        return temp_path
    
    async def _save_generated_image(
        self,
        image_url: str,
        filename: str,
        format: str = "png"
    ) -> Path:
        """Save generated image from URL."""
        import aiohttp
        
        output_dir = settings.cache_dir / "generated"
        await ensure_directory_exists(output_dir)
        
        output_path = output_dir / f"{filename}.{format}"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(image_url) as response:
                if response.status == 200:
                    async with aiofiles.open(output_path, 'wb') as f:
                        await f.write(await response.read())
        
        return output_path
    
    def _generate_cache_key(self, operation: str, params: dict[str, Any]) -> str:
        """Generate cache key for operation."""
        content = f"{operation}:{str(sorted(params.items()))}"
        return hashlib.md5(content.encode()).hexdigest()


class VisionVerifier:
    """Vision-based verification system with automatic regeneration."""
    
    def __init__(self, openai_client: AsyncOpenAI):
        self.client = openai_client
    
    async def verify_generation(
        self,
        image_path: str,
        criteria: VerificationCriteria,
        original_prompt: str
    ) -> dict[str, Any]:
        """Verify generated image against criteria."""
        
        try:
            # Load image for analysis
            image_data = await self._encode_image(image_path)
            
            # Create verification prompt
            verification_prompt = self._create_verification_prompt(criteria, original_prompt)
            
            # Analyze image
            response = await self.client.chat.completions.create(
                model="gpt-4-vision-preview",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": verification_prompt},
                            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_data}"}}
                        ]
                    }
                ],
                max_tokens=500
            )
            
            analysis = response.choices[0].message.content
            
            # Parse verification result
            verification_result = await self._parse_verification_result(
                analysis, criteria
            )
            
            return verification_result
            
        except Exception as e:
            logger.error(f"Verification failed for {image_path}: {e}")
            return {
                "passed": False,
                "score": 0.0,
                "issues": [f"Verification error: {str(e)}"],
                "analysis": "",
                "needs_regeneration": True
            }
    
    async def verify_with_regeneration(
        self,
        generator: AdvancedImageGenerator,
        initial_result: GenerationResult,
        criteria: VerificationCriteria,
        original_prompt: str
    ) -> GenerationResult:
        """Verify and regenerate if necessary."""
        
        current_result = initial_result
        regeneration_count = 0
        
        while regeneration_count < criteria.max_regenerations:
            # Verify current result
            verification = await self.verify_generation(
                current_result.file_path,
                criteria,
                original_prompt
            )
            
            current_result.verification_result = verification
            current_result.regeneration_count = regeneration_count
            
            if verification["passed"] or verification["score"] >= criteria.quality_threshold:
                logger.info(f"Verification passed after {regeneration_count} regenerations")
                break
            
            if not verification.get("needs_regeneration", True):
                logger.info("Verification suggests no regeneration needed")
                break
            
            # Regenerate with improved prompt
            regeneration_count += 1
            logger.info(f"Regeneration attempt {regeneration_count}/{criteria.max_regenerations}")
            
            try:
                improved_prompt = await self._create_improved_prompt(
                    original_prompt, verification["issues"]
                )
                
                # Simple regeneration - could be enhanced with specific techniques
                response = await generator.client.images.generate(
                    prompt=improved_prompt,
                    size=current_result.metadata.get("size", "1024x1024"),
                    quality=current_result.metadata.get("quality", "standard"),
                    n=1
                )
                
                # Save regenerated image
                new_path = await generator._save_generated_image(
                    response.data[0].url,
                    f"regen_{current_result.id}_{regeneration_count}",
                    "png"
                )
                
                current_result.file_path = str(new_path)
                current_result.metadata["regenerated"] = True
                current_result.metadata["improved_prompt"] = improved_prompt
                
            except Exception as e:
                logger.error(f"Regeneration {regeneration_count} failed: {e}")
                break
        
        return current_result
    
    async def _encode_image(self, image_path: str) -> str:
        """Encode image to base64 for vision API."""
        async with aiofiles.open(image_path, 'rb') as f:
            image_data = await f.read()
            return base64.b64encode(image_data).decode('utf-8')
    
    def _create_verification_prompt(
        self,
        criteria: VerificationCriteria,
        original_prompt: str
    ) -> str:
        """Create verification prompt based on criteria."""
        
        prompt_parts = [
            f"Please analyze this image that was generated from the prompt: '{original_prompt}'",
            "",
            "Evaluate the image based on these criteria:"
        ]
        
        if criteria.required_objects:
            prompt_parts.append(f"- Required objects: {', '.join(criteria.required_objects)}")
        
        if criteria.forbidden_objects:
            prompt_parts.append(f"- Objects that should NOT be present: {', '.join(criteria.forbidden_objects)}")
        
        if criteria.style_consistency:
            prompt_parts.append("- Check if the style is consistent throughout the image")
        
        if criteria.custom_checks:
            prompt_parts.extend([f"- {check}" for check in criteria.custom_checks])
        
        prompt_parts.extend([
            "",
            "Please provide:",
            "1. A score from 0.0 to 1.0 for overall quality",
            "2. List any issues or problems",
            "3. Whether the image meets the requirements (YES/NO)",
            "4. Brief analysis of what you see",
            "",
            "Format your response as a structured analysis."
        ])
        
        return "\n".join(prompt_parts)
    
    async def _parse_verification_result(
        self,
        analysis: str,
        criteria: VerificationCriteria
    ) -> dict[str, Any]:
        """Parse verification analysis into structured result."""
        
        # Simple parsing - could be enhanced with structured outputs
        analysis_lower = analysis.lower()
        
        # Extract score
        score = 0.5  # default
        if "score" in analysis_lower:
            # Try to extract numerical score
            import re
            score_match = re.search(r'score.*?(\d+\.?\d*)', analysis_lower)
            if score_match:
                try:
                    score = float(score_match.group(1))
                    if score > 1.0:
                        score = score / 10.0  # Handle scores out of 10
                except ValueError:
                    pass
        
        # Check if requirements met
        passed = (
            ("yes" in analysis_lower and "meets" in analysis_lower) or
            ("requirements" in analysis_lower and "satisfied" in analysis_lower) or
            score >= criteria.quality_threshold
        )
        
        # Extract issues
        issues = []
        if "issue" in analysis_lower or "problem" in analysis_lower:
            # Simple issue extraction
            lines = analysis.split('\n')
            for line in lines:
                if any(word in line.lower() for word in ["issue", "problem", "missing", "incorrect"]):
                    issues.append(line.strip())
        
        return {
            "passed": passed,
            "score": score,
            "issues": issues,
            "analysis": analysis,
            "needs_regeneration": not passed and score < criteria.quality_threshold
        }
    
    async def _create_improved_prompt(
        self,
        original_prompt: str,
        issues: list[str]
    ) -> str:
        """Create improved prompt based on identified issues."""
        
        if not issues:
            return original_prompt
        
        try:
            response = await self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "user",
                        "content": f"""
                        Original prompt: "{original_prompt}"
                        
                        Issues identified in the generated image:
                        {chr(10).join(f"- {issue}" for issue in issues)}
                        
                        Please create an improved prompt that addresses these issues while maintaining the original intent.
                        Make the prompt more specific and detailed to avoid the identified problems.
                        
                        Improved prompt:
                        """
                    }
                ],
                max_tokens=200
            )
            
            improved_prompt = response.choices[0].message.content.strip()
            logger.info(f"Generated improved prompt: {improved_prompt}")
            return improved_prompt
            
        except Exception as e:
            logger.error(f"Failed to create improved prompt: {e}")
            return f"{original_prompt} (enhanced with fixes for: {', '.join(issues[:2])})"
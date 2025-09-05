"""Image analysis and vision capabilities."""

import base64
import json
from pathlib import Path
from typing import Any
from datetime import datetime

from openai import OpenAI

from openai_mcp_server.models import ImageDetail, ImageAnalysis
from openai_mcp_server.utils import generate_content_hash, load_verification_cache, save_verification_cache
from openai_mcp_server.config import VERIFICATION_CACHE


class ImageAnalyzer:
    """Handles image analysis using OpenAI's vision capabilities."""
    
    def __init__(self, client: OpenAI):
        self.client = client
    
    async def verify_image_with_vision(
        self,
        image_path: str,
        verification_prompt: str = "Describe this image in detail",
        use_cache: bool = True,
        detail_level: ImageDetail = "auto"
    ) -> dict[str, Any]:
        """Verify and analyze an image using OpenAI's vision capabilities."""
        image_file = Path(image_path)
        if not image_file.exists():
            return {
                "status": "error",
                "error": f"Image file not found: {image_path}"
            }
        
        # Check verification cache
        cache_key = f"{image_path}|{verification_prompt}"
        cache_hash = generate_content_hash(cache_key)
        
        if use_cache:
            verification_cache = await load_verification_cache(VERIFICATION_CACHE)
            if cache_hash in verification_cache:
                return {
                    "status": "cached",
                    **verification_cache[cache_hash],
                    "message": "Verification result retrieved from cache"
                }
        
        try:
            # Encode image to base64
            with open(image_file, "rb") as f:
                image_data = base64.b64encode(f.read()).decode()
            
            # Analyze with vision model
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": verification_prompt},
                            {
                                "type": "image_url", 
                                "image_url": {
                                    "url": f"data:image/png;base64,{image_data}",
                                    "detail": detail_level
                                }
                            }
                        ]
                    }
                ],
                max_tokens=1000
            )
            
            analysis_content = response.choices[0].message.content or "No analysis available"
            result = {
                "status": "analyzed",
                "image_path": image_path,
                "verification_prompt": verification_prompt,
                "analysis": analysis_content,
                "model_used": "gpt-4o",
                "timestamp": datetime.now().isoformat()
            }
            
            # Cache the result
            if use_cache:
                verification_cache = await load_verification_cache(VERIFICATION_CACHE)
                verification_cache[cache_hash] = result
                await save_verification_cache(VERIFICATION_CACHE, verification_cache)
            
            return result
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "image_path": image_path
            }
    
    async def analyze_image_with_responses_api(
        self,
        image_path: str,
        analysis_prompt: str = "What's in this image?",
        detail_level: ImageDetail = "auto"
    ) -> dict[str, Any]:
        """Analyze an image using the new Responses API for enhanced multimodal capabilities."""
        image_file = Path(image_path)
        if not image_file.exists():
            return {
                "status": "error",
                "error": f"Image file not found: {image_path}"
            }
        
        try:
            # Encode image to base64
            with open(image_file, "rb") as f:
                image_data = base64.b64encode(f.read()).decode()
            
            # Use Responses API for image analysis
            response = self.client.responses.create(
                model="gpt-4.1-mini",
                input=[{
                    "role": "user", 
                    "content": [
                        {"type": "input_text", "text": analysis_prompt},
                        {
                            "type": "input_image",
                            "image_url": f"data:image/png;base64,{image_data}",
                            "detail": detail_level
                        }
                    ]
                }]
            )
            
            return {
                "status": "analyzed",
                "image_path": image_path,
                "analysis_prompt": analysis_prompt,
                "analysis": response.output_text,
                "detail_level": detail_level,
                "model_used": "gpt-4.1-mini (Responses API)",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "image_path": image_path
            }
    
    async def analyze_image_structured(
        self,
        image_path: str,
        detail_level: ImageDetail = "auto"
    ) -> dict[str, Any]:
        """Perform structured image analysis using OpenAI's structured outputs."""
        image_file = Path(image_path)
        if not image_file.exists():
            return {
                "status": "error",
                "error": f"Image file not found: {image_path}"
            }
        
        try:
            # Encode image to base64
            with open(image_file, "rb") as f:
                image_data = base64.b64encode(f.read()).decode()
            
            # Use structured outputs for comprehensive image analysis
            response = self.client.responses.parse(
                model="gpt-4o-2024-08-06",
                input=[
                    {
                        "role": "system", 
                        "content": "Analyze the image comprehensively, identifying objects, colors, style, mood, and technical quality. Provide structured, detailed analysis."
                    },
                    {
                        "role": "user",
                        "content": [
                            {"type": "input_text", "text": "Please analyze this image in detail"},
                            {
                                "type": "input_image",
                                "image_url": f"data:image/png;base64,{image_data}",
                                "detail": detail_level
                            }
                        ]
                    }
                ],
                text_format=ImageAnalysis
            )
            
            analysis = response.output_parsed
            
            return {
                "status": "analyzed",
                "image_path": image_path,
                "analysis": analysis.model_dump(),
                "detail_level": detail_level,
                "model_used": "gpt-4o-2024-08-06 (Structured Outputs)",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "image_path": image_path
            }
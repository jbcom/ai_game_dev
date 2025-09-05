"""LangChain structured tools for OpenAI media generation and analysis."""

import asyncio
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Type, Union
from datetime import datetime

from langchain_core.tools import BaseTool
from langchain_core.callbacks import CallbackManagerForToolRun
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_openai import ChatOpenAI
from openai import AsyncOpenAI

from .generators import ImageGenerator, Model3DGenerator
from .analyzers import ImageAnalyzer, VisionAnalyzer
from .config import settings
from .logging_config import get_logger
from .seed_system import seed_queue, SeedType, SeedPriority
from .cache_manager import cache_manager
from .models import ImageSize, ImageQuality, ModelFormat

logger = get_logger(__name__, component="langchain_tools")


# Input schemas for LangChain tools
class ImageGenerationInput(BaseModel):
    """Input schema for image generation tool."""
    prompt: str = Field(description="Detailed description of the image to generate")
    size: str = Field(default="1024x1024", description="Image size (1024x1024, 1536x1024, 1024x1536, etc.)")
    quality: str = Field(default="standard", description="Image quality (standard, hd)")
    style: str = Field(default="natural", description="Image style (natural, vivid)")
    project_context: Optional[str] = Field(default=None, description="Project context for seed enhancement")
    use_seeds: bool = Field(default=True, description="Whether to enhance with contextual seeds")


class ImageAnalysisInput(BaseModel):
    """Input schema for image analysis tool."""
    image_path: str = Field(description="Path to the image file to analyze")
    analysis_type: str = Field(default="comprehensive", description="Type of analysis (comprehensive, objects, colors, style)")
    detailed: bool = Field(default=True, description="Whether to provide detailed analysis")


class Model3DGenerationInput(BaseModel):
    """Input schema for 3D model generation tool."""
    name: str = Field(description="Name of the 3D model")
    description: str = Field(description="Detailed description of the 3D model")
    geometry_type: str = Field(default="custom", description="Type of geometry (cube, sphere, cylinder, plane, custom)")
    optimization_target: str = Field(default="game", description="Optimization target (game, visualization, print)")
    polycount_budget: int = Field(default=5000, description="Target polygon count")


class SeedManagementInput(BaseModel):
    """Input schema for seed management tool."""
    action: str = Field(description="Action to perform (add, query, list, clear)")
    seed_type: Optional[str] = Field(default=None, description="Type of seed data")
    content: Optional[str] = Field(default=None, description="Seed content to add")
    priority: str = Field(default="medium", description="Seed priority (critical, high, medium, low)")
    project_context: Optional[str] = Field(default=None, description="Project context")


class GameSpecAnalysisInput(BaseModel):
    """Input schema for game specification analysis."""
    specification: str = Field(description="Game specification in any format (natural language, JSON, YAML, etc.)")
    analysis_depth: str = Field(default="comprehensive", description="Analysis depth (basic, comprehensive, detailed)")
    suggest_workflow: bool = Field(default=True, description="Whether to suggest implementation workflow")


class NarrativeGenerationInput(BaseModel):
    """Input schema for narrative generation."""
    request: str = Field(description="Narrative generation request")
    narrative_type: str = Field(default="general", description="Type of narrative (dialogue, quest, character, lore)")
    project_context: Optional[str] = Field(default=None, description="Project context for consistency")
    use_yarn: bool = Field(default=False, description="Whether to use YarnSpinner format")


# LangChain Tool Classes
class ImageGenerationTool(BaseTool):
    """LangChain tool for advanced image generation with OpenAI DALL-E."""
    
    name: str = "generate_image"
    description: str = """Generate high-quality images using OpenAI DALL-E with contextual enhancement.
    Perfect for creating game assets, concept art, characters, environments, UI elements, and more.
    Automatically enhances prompts with relevant seed data for project consistency."""
    
    args_schema: Type[BaseModel] = ImageGenerationInput
    
    def __init__(self):
        super().__init__()
        self.openai_client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.image_generator = None
    
    async def _get_generator(self):
        """Lazy initialization of image generator."""
        if self.image_generator is None:
            self.image_generator = ImageGenerator(self.openai_client)
            await self.image_generator.initialize()
        return self.image_generator
    
    def _run(
        self, 
        prompt: str,
        size: str = "1024x1024",
        quality: str = "standard", 
        style: str = "natural",
        project_context: Optional[str] = None,
        use_seeds: bool = True,
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """Synchronous wrapper for async image generation."""
        return asyncio.run(self._arun(prompt, size, quality, style, project_context, use_seeds, run_manager))
    
    async def _arun(
        self,
        prompt: str,
        size: str = "1024x1024", 
        quality: str = "standard",
        style: str = "natural",
        project_context: Optional[str] = None,
        use_seeds: bool = True,
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """Generate image using OpenAI DALL-E with contextual enhancement."""
        try:
            generator = await self._get_generator()
            
            # Generate image with all enhancements
            result = await generator.generate_image(
                prompt=prompt,
                size=size,
                quality=quality, 
                style=style,
                project_context=project_context or "general",
                use_seeds=use_seeds
            )
            
            if result["status"] == "success":
                logger.info(f"Generated image: {result['local_path']}")
                return f"Successfully generated image: {result['local_path']}. Enhanced prompt: {result.get('enhanced_prompt', prompt)}"
            else:
                return f"Image generation failed: {result.get('error', 'Unknown error')}"
                
        except Exception as e:
            logger.error(f"Image generation tool failed: {e}")
            return f"Error generating image: {str(e)}"


class ImageAnalysisTool(BaseTool):
    """LangChain tool for comprehensive image analysis with OpenAI Vision."""
    
    name: str = "analyze_image"
    description: str = """Analyze images comprehensively using OpenAI Vision API.
    Detects objects, colors, style, mood, and provides detailed descriptions.
    Perfect for understanding visual content, verifying generated assets, and extracting creative insights."""
    
    args_schema: Type[BaseModel] = ImageAnalysisInput
    
    def __init__(self):
        super().__init__()
        self.openai_client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.image_analyzer = None
    
    async def _get_analyzer(self):
        """Lazy initialization of image analyzer."""
        if self.image_analyzer is None:
            self.image_analyzer = ImageAnalyzer(self.openai_client)
            await self.image_analyzer.initialize()
        return self.image_analyzer
    
    def _run(
        self,
        image_path: str,
        analysis_type: str = "comprehensive",
        detailed: bool = True,
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """Synchronous wrapper for async image analysis."""
        return asyncio.run(self._arun(image_path, analysis_type, detailed, run_manager))
    
    async def _arun(
        self,
        image_path: str,
        analysis_type: str = "comprehensive", 
        detailed: bool = True,
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """Analyze image using OpenAI Vision API."""
        try:
            analyzer = await self._get_analyzer()
            
            # Perform analysis
            result = await analyzer.analyze_image(
                image_path=image_path,
                analysis_type=analysis_type,
                detailed=detailed
            )
            
            if result["status"] == "success":
                analysis = result["analysis"]
                logger.info(f"Analyzed image: {image_path}")
                
                # Format analysis for LangChain agent consumption
                formatted_result = f"""Image Analysis Results for {image_path}:

Objects Detected: {', '.join(analysis.get('objects', []))}
Dominant Colors: {', '.join(analysis.get('colors', []))}
Style: {analysis.get('style', 'Unknown')}
Mood: {analysis.get('mood', 'Neutral')}
Technical Quality: {analysis.get('technical_quality', 'Unknown')}

Description: {analysis.get('content_description', 'No description available')}

Suggested Uses: {', '.join(analysis.get('suggested_uses', []))}"""
                
                return formatted_result
            else:
                return f"Image analysis failed: {result.get('error', 'Unknown error')}"
                
        except Exception as e:
            logger.error(f"Image analysis tool failed: {e}")
            return f"Error analyzing image: {str(e)}"


class Model3DGenerationTool(BaseTool):
    """LangChain tool for 3D model generation and specification."""
    
    name: str = "generate_3d_model"
    description: str = """Generate detailed 3D model specifications with materials and textures.
    Creates complete model definitions optimized for game engines like Bevy, Unity, and Godot.
    Includes PBR materials, UV mapping, and optimization parameters."""
    
    args_schema: Type[BaseModel] = Model3DGenerationInput
    
    def __init__(self):
        super().__init__()
        self.openai_client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.model_generator = None
    
    async def _get_generator(self):
        """Lazy initialization of 3D model generator."""
        if self.model_generator is None:
            self.model_generator = Model3DGenerator(self.openai_client)
            await self.model_generator.initialize()
        return self.model_generator
    
    def _run(
        self,
        name: str,
        description: str,
        geometry_type: str = "custom",
        optimization_target: str = "game",
        polycount_budget: int = 5000,
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """Synchronous wrapper for async 3D model generation."""
        return asyncio.run(self._arun(name, description, geometry_type, optimization_target, polycount_budget, run_manager))
    
    async def _arun(
        self,
        name: str,
        description: str, 
        geometry_type: str = "custom",
        optimization_target: str = "game",
        polycount_budget: int = 5000,
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """Generate 3D model specification."""
        try:
            generator = await self._get_generator()
            
            # Generate 3D model spec
            result = await generator.generate_model_spec(
                name=name,
                description=description,
                geometry_type=geometry_type,
                optimization_target=optimization_target,
                polycount_budget=polycount_budget
            )
            
            if result["status"] == "success":
                spec = result["model_spec"]
                logger.info(f"Generated 3D model spec: {name}")
                
                # Format spec for agent consumption
                formatted_result = f"""3D Model Specification: {name}

Description: {description}
Geometry Type: {geometry_type}
Optimization: {optimization_target}
Polygon Budget: {polycount_budget}

Materials: {len(spec.get('materials', []))} defined
Textures: {len(spec.get('textures', []))} required
File Format: {spec.get('format', 'GLTF')}

Specification saved to: {result.get('spec_path', 'memory')}"""
                
                return formatted_result
            else:
                return f"3D model generation failed: {result.get('error', 'Unknown error')}"
                
        except Exception as e:
            logger.error(f"3D model generation tool failed: {e}")
            return f"Error generating 3D model: {str(e)}"


class SeedManagementTool(BaseTool):
    """LangChain tool for managing contextual seed data."""
    
    name: str = "manage_seeds"
    description: str = """Manage contextual seed data for consistent game development.
    Add, query, list, or clear seed data that enhances prompts with project-specific context.
    Seeds maintain visual consistency, character details, and world lore across generation tasks."""
    
    args_schema: Type[BaseModel] = SeedManagementInput
    
    def _run(
        self,
        action: str,
        seed_type: Optional[str] = None,
        content: Optional[str] = None,
        priority: str = "medium",
        project_context: Optional[str] = None,
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """Manage seed data synchronously."""
        try:
            if action == "add" and content:
                # Add new seed
                seed_type_enum = SeedType(seed_type) if seed_type else SeedType.CONTEXT
                priority_enum = SeedPriority(priority)
                
                seed_id = seed_queue.add_seed(
                    content=content,
                    seed_type=seed_type_enum,
                    priority=priority_enum,
                    project_context=project_context or "general"
                )
                
                return f"Added seed {seed_id}: {content[:100]}..."
            
            elif action == "query":
                # Query seeds
                seeds = seed_queue.get_relevant_seeds(
                    query_context=content or "",
                    project_context=project_context or "general"
                )
                
                if seeds:
                    seed_list = "\n".join([f"- [{s.seed_type.value}] {s.content[:100]}..." for s in seeds])
                    return f"Found {len(seeds)} relevant seeds:\n{seed_list}"
                else:
                    return "No relevant seeds found."
            
            elif action == "list":
                # List all seeds
                all_seeds = seed_queue.list_seeds()
                if all_seeds:
                    seed_list = "\n".join([f"- {s.seed_id}: [{s.seed_type.value}] {s.content[:100]}..." for s in all_seeds])
                    return f"All seeds ({len(all_seeds)}):\n{seed_list}"
                else:
                    return "No seeds stored."
            
            elif action == "clear":
                # Clear seeds
                if project_context:
                    cleared = seed_queue.clear_project_seeds(project_context)
                    return f"Cleared {cleared} seeds for project: {project_context}"
                else:
                    seed_queue.clear_all_seeds()
                    return "Cleared all seeds."
            
            else:
                return f"Unknown seed action: {action}. Use add, query, list, or clear."
                
        except Exception as e:
            logger.error(f"Seed management tool failed: {e}")
            return f"Error managing seeds: {str(e)}"


class GameSpecAnalysisTool(BaseTool):
    """LangChain tool for analyzing game specifications in any format."""
    
    name: str = "analyze_game_spec"
    description: str = """Analyze game specifications in any format (natural language, JSON, YAML, TOML, Markdown).
    Provides intelligent analysis, format recommendations, and suggests optimal implementation workflows.
    Perfect for understanding project requirements and planning development approach."""
    
    args_schema: Type[BaseModel] = GameSpecAnalysisInput
    
    def __init__(self):
        super().__init__()
        self.openai_client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.spec_analyzer = None
    
    async def _get_analyzer(self):
        """Lazy initialization of spec analyzer."""
        if self.spec_analyzer is None:
            from .spec_analyzer import GameSpecAnalyzer
            self.spec_analyzer = GameSpecAnalyzer(self.openai_client)
            await self.spec_analyzer.initialize()
        return self.spec_analyzer
    
    def _run(
        self,
        specification: str,
        analysis_depth: str = "comprehensive", 
        suggest_workflow: bool = True,
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """Synchronous wrapper for async spec analysis."""
        return asyncio.run(self._arun(specification, analysis_depth, suggest_workflow, run_manager))
    
    async def _arun(
        self,
        specification: str,
        analysis_depth: str = "comprehensive",
        suggest_workflow: bool = True, 
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """Analyze game specification."""
        try:
            analyzer = await self._get_analyzer()
            
            # Analyze specification
            result = await analyzer.analyze_specification(
                spec_content=specification,
                analysis_depth=analysis_depth
            )
            
            if result["status"] == "success":
                analysis = result["analysis"]
                logger.info(f"Analyzed game specification: {analysis.get('format_detected', 'unknown format')}")
                
                # Format analysis for agent consumption
                formatted_result = f"""Game Specification Analysis:

Format Detected: {analysis.get('format_detected', 'Unknown')}
Confidence: {analysis.get('format_confidence', 0):.2f}
Game Type: {analysis.get('game_type', 'Unknown')}
Engine Recommendation: {analysis.get('recommended_engine', 'Unknown')}

Key Elements Identified:
- Characters: {len(analysis.get('characters', []))}
- Locations: {len(analysis.get('locations', []))}
- Mechanics: {len(analysis.get('mechanics', []))}
- Assets Needed: {len(analysis.get('required_assets', []))}

Analysis Summary:
{analysis.get('summary', 'No summary available')}

Recommended Workflow:
{analysis.get('workflow_recommendation', 'No workflow suggested')}"""
                
                return formatted_result
            else:
                return f"Specification analysis failed: {result.get('error', 'Unknown error')}"
                
        except Exception as e:
            logger.error(f"Game spec analysis tool failed: {e}")
            return f"Error analyzing specification: {str(e)}"


class NarrativeGenerationTool(BaseTool):
    """LangChain tool for narrative and dialogue generation."""
    
    name: str = "generate_narrative"
    description: str = """Generate rich narrative content including dialogue, quests, characters, and lore.
    Supports YarnSpinner format for interactive dialogue trees and maintains consistency across sessions.
    Perfect for creating compelling game stories and character development."""
    
    args_schema: Type[BaseModel] = NarrativeGenerationInput
    
    def __init__(self):
        super().__init__()
        self.openai_client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.narrative_generator = None
    
    async def _get_generator(self):
        """Lazy initialization of narrative generator."""
        if self.narrative_generator is None:
            from .narrative_system import NarrativeGenerator
            self.narrative_generator = NarrativeGenerator(self.openai_client)
            await self.narrative_generator.initialize()
        return self.narrative_generator
    
    def _run(
        self,
        request: str,
        narrative_type: str = "general",
        project_context: Optional[str] = None,
        use_yarn: bool = False,
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """Synchronous wrapper for async narrative generation."""
        return asyncio.run(self._arun(request, narrative_type, project_context, use_yarn, run_manager))
    
    async def _arun(
        self,
        request: str,
        narrative_type: str = "general",
        project_context: Optional[str] = None,
        use_yarn: bool = False,
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """Generate narrative content."""
        try:
            generator = await self._get_generator()
            
            # Generate narrative based on type
            if narrative_type == "dialogue":
                result = await generator.generate_dialogue(
                    character_description="Dynamic character",
                    context=request,
                    dialogue_type="conversation"
                )
            elif narrative_type == "quest":
                result = await generator.generate_quest(
                    quest_description=request,
                    difficulty="medium"
                )
            elif narrative_type == "character":
                result = await generator.generate_character(
                    character_description=request,
                    detail_level="comprehensive"
                )
            else:
                # General narrative generation
                result = await generator.generate_lore(
                    topic=request,
                    lore_type="general",
                    detail_level="comprehensive"
                )
            
            if result["status"] == "success":
                content = result.get("content", result.get("narrative", result.get("dialogue", "")))
                logger.info(f"Generated {narrative_type} narrative")
                
                return f"Generated {narrative_type} narrative:\n\n{content}"
            else:
                return f"Narrative generation failed: {result.get('error', 'Unknown error')}"
                
        except Exception as e:
            logger.error(f"Narrative generation tool failed: {e}")
            return f"Error generating narrative: {str(e)}"


def get_langchain_tools() -> List[BaseTool]:
    """Get all LangChain tools for the game development agent."""
    return [
        ImageGenerationTool(),
        ImageAnalysisTool(), 
        Model3DGenerationTool(),
        SeedManagementTool(),
        GameSpecAnalysisTool(),
        NarrativeGenerationTool()
    ]
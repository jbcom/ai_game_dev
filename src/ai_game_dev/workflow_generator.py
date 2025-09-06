"""Intelligent workflow generation from high-level task descriptions."""

import json
import uuid
from typing import Any, Dict, List

from openai import AsyncOpenAI

from ai_game_dev.config import settings
from ai_game_dev.logging_config import get_logger
from ai_game_dev.models import (
    TaskAnalysisResult, WorkflowSpec, WorkflowType, UIElementSpec, 
    ImageEditRequest, VerificationCriteria, EditOperation, ImageSize
)

logger = get_logger(__name__, component="workflow_generator")


class WorkflowAnalyzer:
    """Analyze high-level tasks and generate optimized workflows."""
    
    def __init__(self, openai_client: AsyncOpenAI):
        self.client = openai_client
    
    async def analyze_task(self, task_description: str) -> TaskAnalysisResult:
        """Analyze high-level task and generate suggested workflow."""
        
        logger.info(f"Analyzing task: {task_description[:100]}...")
        
        try:
            # Use structured output for consistent results
            analysis_prompt = self._create_analysis_prompt(task_description)
            
            response = await self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": self._get_system_prompt()},
                    {"role": "user", "content": analysis_prompt}
                ],
                temperature=0.3,
                max_tokens=2000
            )
            
            analysis_text = response.choices[0].message.content
            
            # Parse the structured response
            workflow_data = await self._parse_analysis_response(analysis_text)
            
            # Create workflow specification
            suggested_workflow = await self._create_workflow_spec(
                task_description, workflow_data
            )
            
            # Generate analysis result
            result = TaskAnalysisResult(
                suggested_workflow=suggested_workflow,
                reasoning=workflow_data.get("reasoning", ""),
                estimated_operations=workflow_data.get("estimated_operations", 1),
                estimated_time=workflow_data.get("estimated_time", "5-10 minutes"),
                optimization_suggestions=workflow_data.get("optimizations", [])
            )
            
            logger.info(f"Generated workflow with {len(suggested_workflow.ui_elements)} UI elements")
            return result
            
        except Exception as e:
            logger.error(f"Task analysis failed: {e}")
            # Return basic fallback workflow
            return await self._create_fallback_workflow(task_description)
    
    async def generate_ui_workflow(
        self,
        game_theme: str,
        ui_requirements: str,
        style_preferences: str = "",
        target_resolution: ImageSize = "1024x1024"
    ) -> WorkflowSpec:
        """Generate specialized UI element workflow for game development."""
        
        logger.info(f"Generating UI workflow for {game_theme}")
        
        try:
            ui_prompt = f"""
            Create a comprehensive UI element generation workflow for:
            
            Game Theme: {game_theme}
            UI Requirements: {ui_requirements}
            Style Preferences: {style_preferences}
            Target Resolution: {target_resolution}
            
            Please identify all necessary UI elements and organize them into an efficient generation workflow.
            Consider element dependencies, visual consistency, and reusability.
            """
            
            response = await self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": self._get_ui_system_prompt()},
                    {"role": "user", "content": ui_prompt}
                ],
                temperature=0.2,
                max_tokens=1500
            )
            
            analysis = response.choices[0].message.content
            ui_data = await self._parse_ui_analysis(analysis)
            
            # Create UI workflow
            workflow = WorkflowSpec(
                name=f"{game_theme.title()} UI Assets",
                type="ui_elements",
                description=f"Complete UI asset generation for {game_theme}",
                ui_elements=ui_data.get("elements", []),
                verification=VerificationCriteria(
                    mode="basic",
                    style_consistency=True,
                    quality_threshold=0.8,
                    max_regenerations=2
                ),
                batch_settings={
                    "concurrent_limit": 3,
                    "retry_failed": True,
                    "group_by_type": True
                },
                output_format="png",
                optimization_level="quality"
            )
            
            return workflow
            
        except Exception as e:
            logger.error(f"UI workflow generation failed: {e}")
            return await self._create_basic_ui_workflow(game_theme, target_resolution)
    
    def _create_analysis_prompt(self, task_description: str) -> str:
        """Create structured analysis prompt."""
        
        return f"""
        Analyze the following task and create an optimized content generation workflow:
        
        TASK: {task_description}
        
        Please provide a structured analysis including:
        
        1. WORKFLOW_TYPE: Classify as one of: ui_elements, game_assets, product_shots, concept_art, textures, custom
        
        2. REQUIRED_ELEMENTS: List specific items that need to be generated
        
        3. GENERATION_STRATEGY: Explain the optimal approach and order
        
        4. STYLE_CONSIDERATIONS: Visual style, themes, consistency requirements
        
        5. TECHNICAL_SPECS: Sizes, formats, quality requirements
        
        6. VERIFICATION_CRITERIA: How to validate results
        
        7. OPTIMIZATIONS: Ways to improve efficiency and quality
        
        8. ESTIMATED_OPERATIONS: Number of generation calls needed
        
        9. ESTIMATED_TIME: Approximate completion time
        
        10. REASONING: Explain your workflow decisions
        
        Structure your response clearly with these sections.
        """
    
    def _get_system_prompt(self) -> str:
        """Get system prompt for task analysis."""
        
        return """
        You are an expert AI workflow designer specializing in content generation optimization.
        
        Your role is to analyze high-level creative tasks and design efficient, high-quality workflows
        for automated content generation using AI image models.
        
        Key principles:
        - Prioritize visual consistency across related assets
        - Minimize redundant operations through smart caching and reuse
        - Consider dependencies between assets (base elements before variants)
        - Design for scalability and maintainability
        - Include quality verification at critical points
        - Optimize for both speed and quality based on use case
        
        Always provide specific, actionable workflow recommendations.
        """
    
    def _get_ui_system_prompt(self) -> str:
        """Get specialized system prompt for UI workflow generation."""
        
        return """
        You are an expert UI/UX designer and game asset specialist.
        
        Your role is to design comprehensive UI asset generation workflows that create
        cohesive, professional game interfaces.
        
        UI Design Principles:
        - Maintain visual hierarchy and consistency
        - Consider different UI states (normal, hover, pressed, disabled)
        - Design for scalability across different screen sizes
        - Ensure accessibility and readability
        - Create modular, reusable components
        - Balance aesthetic appeal with functional clarity
        
        Always consider the complete user experience and interface flow.
        """
    
    async def _parse_analysis_response(self, analysis_text: str) -> Dict[str, Any]:
        """Parse structured analysis response."""
        
        try:
            # Simple parsing - could be enhanced with structured outputs
            data = {}
            
            sections = {
                "WORKFLOW_TYPE": "workflow_type",
                "REQUIRED_ELEMENTS": "elements", 
                "GENERATION_STRATEGY": "strategy",
                "STYLE_CONSIDERATIONS": "style",
                "TECHNICAL_SPECS": "specs",
                "VERIFICATION_CRITERIA": "verification",
                "OPTIMIZATIONS": "optimizations",
                "ESTIMATED_OPERATIONS": "estimated_operations",
                "ESTIMATED_TIME": "estimated_time",
                "REASONING": "reasoning"
            }
            
            current_section = None
            current_content = []
            
            for line in analysis_text.split('\n'):
                line = line.strip()
                
                # Check if this is a section header
                section_found = False
                for section_key, data_key in sections.items():
                    if section_key in line.upper():
                        # Save previous section
                        if current_section and current_content:
                            data[current_section] = '\n'.join(current_content).strip()
                        
                        current_section = data_key
                        current_content = []
                        section_found = True
                        break
                
                if not section_found and current_section and line:
                    current_content.append(line)
            
            # Save final section
            if current_section and current_content:
                data[current_section] = '\n'.join(current_content).strip()
            
            # Parse specific fields
            if 'estimated_operations' in data:
                try:
                    data['estimated_operations'] = int(data['estimated_operations'].split()[0])
                except:
                    data['estimated_operations'] = 5
            
            if 'optimizations' in data and isinstance(data['optimizations'], str):
                data['optimizations'] = [
                    line.strip('- ').strip() 
                    for line in data['optimizations'].split('\n') 
                    if line.strip().startswith('-')
                ]
            
            return data
            
        except Exception as e:
            logger.error(f"Failed to parse analysis response: {e}")
            return {"reasoning": "Analysis parsing failed", "estimated_operations": 1}
    
    async def _parse_ui_analysis(self, analysis: str) -> Dict[str, Any]:
        """Parse UI-specific analysis."""
        
        try:
            # Extract UI elements from analysis
            elements = []
            element_types = ["button", "panel", "icon", "texture", "background", "frame", "badge"]
            
            lines = analysis.split('\n')
            current_element = None
            
            for line in lines:
                line = line.strip().lower()
                
                # Check for element type mentions
                for element_type in element_types:
                    if element_type in line and ("create" in line or "generate" in line):
                        # Extract element details
                        element = UIElementSpec(
                            element_type=element_type,
                            style_theme="game-themed",
                            size="1024x1024",
                            color_scheme=["#2C3E50", "#3498DB", "#E74C3C"],  # Default colors
                            state_variants=["normal", "hover", "pressed"] if element_type == "button" else []
                        )
                        elements.append(element)
                        break
            
            # If no elements found, create basic set
            if not elements:
                elements = [
                    UIElementSpec(
                        element_type="button",
                        style_theme="modern",
                        size="512x512",
                        state_variants=["normal", "hover", "pressed"]
                    ),
                    UIElementSpec(
                        element_type="panel",
                        style_theme="modern",
                        size="1024x1024"
                    )
                ]
            
            return {"elements": elements}
            
        except Exception as e:
            logger.error(f"UI analysis parsing failed: {e}")
            return {"elements": []}
    
    async def _create_workflow_spec(
        self,
        task_description: str,
        workflow_data: Dict[str, Any]
    ) -> WorkflowSpec:
        """Create workflow specification from analysis data."""
        
        # Determine workflow type
        workflow_type = "custom"
        type_mapping = {
            "ui": "ui_elements",
            "game": "game_assets", 
            "product": "product_shots",
            "concept": "concept_art",
            "texture": "textures"
        }
        
        for key, value in type_mapping.items():
            if key in task_description.lower():
                workflow_type = value
                break
        
        # Create verification criteria
        verification = VerificationCriteria(
            mode="basic",
            style_consistency=True,
            quality_threshold=0.7,
            max_regenerations=2
        )
        
        if "strict" in task_description.lower() or "high quality" in task_description.lower():
            verification.mode = "strict"
            verification.quality_threshold = 0.85
            verification.max_regenerations = 3
        
        # Create workflow
        workflow = WorkflowSpec(
            name=f"Generated Workflow - {str(uuid.uuid4())[:8]}",
            type=workflow_type,
            description=task_description,
            ui_elements=[],  # Will be populated based on type
            image_edits=[],
            verification=verification,
            batch_settings={
                "concurrent_limit": 2,
                "retry_failed": True
            },
            output_format="png",
            optimization_level="balanced"
        )
        
        return workflow
    
    async def _create_fallback_workflow(self, task_description: str) -> TaskAnalysisResult:
        """Create basic fallback workflow."""
        
        workflow = WorkflowSpec(
            name="Basic Content Generation",
            type="custom",
            description=task_description,
            ui_elements=[],
            image_edits=[],
            verification=VerificationCriteria(mode="basic"),
            batch_settings={"concurrent_limit": 1},
            output_format="png",
            optimization_level="balanced"
        )
        
        return TaskAnalysisResult(
            suggested_workflow=workflow,
            reasoning="Fallback workflow created due to analysis failure",
            estimated_operations=1,
            estimated_time="5 minutes",
            optimization_suggestions=["Review task description for clarity"]
        )
    
    async def _create_basic_ui_workflow(
        self,
        theme: str,
        size: ImageSize
    ) -> WorkflowSpec:
        """Create basic UI workflow as fallback."""
        
        basic_elements = [
            UIElementSpec(
                element_type="button",
                style_theme=theme,
                size=size,
                state_variants=["normal", "hover", "pressed"]
            ),
            UIElementSpec(
                element_type="panel", 
                style_theme=theme,
                size=size
            ),
            UIElementSpec(
                element_type="icon",
                style_theme=theme,
                size="256x256"
            )
        ]
        
        return WorkflowSpec(
            name=f"Basic {theme} UI",
            type="ui_elements",
            description=f"Basic UI elements for {theme}",
            ui_elements=basic_elements,
            verification=VerificationCriteria(mode="basic"),
            batch_settings={"concurrent_limit": 2},
            output_format="png",
            optimization_level="balanced"
        )
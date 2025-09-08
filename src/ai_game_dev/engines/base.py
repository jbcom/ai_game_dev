"""
Base classes for game engine adapters.
Provides structured interfaces for language-native game engine implementations.
"""
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from abc import ABC, abstractmethod
from pathlib import Path
import os

from openai import AsyncOpenAI
from ai_game_dev.config import settings


@dataclass
class EngineGenerationResult:
    """Result from engine-specific generation."""
    engine_type: str
    project_structure: Dict[str, Any]
    main_files: List[str]
    asset_requirements: List[str]
    build_instructions: str
    deployment_notes: str
    generated_files: Dict[str, str]  # filename -> actual code content
    project_path: Optional[Path] = None


class BaseEngineAdapter(ABC):
    """Abstract base class for game engine adapters."""
    
    def __init__(self):
        self.llm_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.output_dir = settings.cache_dir / "generated_projects"
        # Don't create directories on init - defer until needed
    
    def _ensure_output_dir(self) -> None:
        """Ensure output directory exists."""
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    @property
    @abstractmethod
    def engine_name(self) -> str:
        """Name of the target engine."""
        pass
    
    @property
    @abstractmethod
    def native_language(self) -> str:
        """Native programming language for this engine."""
        pass
    
    @abstractmethod
    async def generate_game_project(
        self,
        description: str,
        complexity: str = "intermediate",
        features: List[str] = None,
        art_style: str = "modern"
    ) -> EngineGenerationResult:
        """Generate a complete game project for this engine."""
        pass
    
    @abstractmethod
    def get_project_template(self) -> Dict[str, str]:
        """Get the basic project template structure."""
        pass
    
    @abstractmethod
    def get_build_instructions(self) -> str:
        """Get instructions for building the project."""
        pass
    
    async def generate_code_with_llm(self, prompt: str, max_tokens: int = 4000) -> str:
        """Generate code using LLM."""
        try:
            response = await self.llm_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": f"You are an expert {self.native_language} developer specializing in {self.engine_name} game development. Generate clean, production-ready code with proper structure and comments."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"// Error generating code: {e}\n// Fallback placeholder code"
    
    async def save_project_files(self, project_name: str, files: Dict[str, str]) -> Path:
        """Save generated files to disk."""
        project_path = self.output_dir / f"{self.engine_name}_{project_name}"
        project_path.mkdir(exist_ok=True)
        
        for filename, content in files.items():
            file_path = project_path / filename
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
        
        return project_path
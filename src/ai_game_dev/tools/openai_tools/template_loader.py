"""Template loader for OpenAI tools.

This module provides Jinja2 template loading functionality for engine-specific
prompts and educational content.
"""

from pathlib import Path
from jinja2 import Environment, FileSystemLoader, Template


class TemplateLoader:
    """Loads and manages Jinja2 templates for game generation."""
    
    def __init__(self):
        """Initialize template loader with the templates directory."""
        self.templates_dir = Path(__file__).parent / "templates"
        self.env = Environment(
            loader=FileSystemLoader(str(self.templates_dir)),
            trim_blocks=True,
            lstrip_blocks=True
        )
    
    def get_engine_template(self, engine: str, template_type: str) -> Template:
        """Get a template for a specific engine.
        
        Args:
            engine: The game engine (bevy, pygame, godot)
            template_type: Type of template (architecture, code_structure, assets, etc.)
            
        Returns:
            Loaded Jinja2 template
        """
        template_path = f"{engine}/{template_type}.jinja2"
        return self.env.get_template(template_path)
    
    def get_academy_template(self, template_type: str) -> Template:
        """Get a template for academy educational content.
        
        Args:
            template_type: Type of template (lesson, challenge, teachable_moment, etc.)
            
        Returns:
            Loaded Jinja2 template
        """
        template_path = f"academy/{template_type}.jinja2"
        return self.env.get_template(template_path)
    
    def render_engine_prompt(self, engine: str, template_type: str, **context) -> str:
        """Render an engine-specific prompt with context.
        
        Args:
            engine: The game engine
            template_type: Type of template
            **context: Variables to pass to template
            
        Returns:
            Rendered prompt string
        """
        template = self.get_engine_template(engine, template_type)
        return template.render(**context)
    
    def render_academy_prompt(self, template_type: str, **context) -> str:
        """Render an academy educational prompt with context.
        
        Args:
            template_type: Type of template
            **context: Variables to pass to template
            
        Returns:
            Rendered prompt string
        """
        template = self.get_academy_template(template_type)
        return template.render(**context)


# Global instance
template_loader = TemplateLoader()
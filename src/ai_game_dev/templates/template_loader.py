"""
Template loader for engine-specific prompts and code structures.
"""
from pathlib import Path
from typing import Any, Dict, Literal

from jinja2 import Environment, FileSystemLoader, Template


class TemplateLoader:
    """Loads and renders Jinja2 templates for different game engines."""
    
    def __init__(self):
        # Get the templates directory
        self.templates_dir = Path(__file__).parent / "prompts"
        self.templates_dir.mkdir(exist_ok=True)
        
        # Initialize Jinja2 environment
        self.env = Environment(
            loader=FileSystemLoader(str(self.templates_dir)),
            trim_blocks=True,
            lstrip_blocks=True
        )
        
    def render_engine_prompt(
        self,
        engine: Literal["pygame", "godot", "bevy"],
        template_name: str,
        **context: Any
    ) -> str:
        """
        Render an engine-specific template.
        
        Args:
            engine: Game engine name
            template_name: Template file name (without extension)
            **context: Variables to pass to the template
            
        Returns:
            Rendered template string
        """
        try:
            template = self.env.get_template(f"{engine}/{template_name}.jinja2")
            return template.render(**context)
        except Exception:
            # Fallback to default template if engine-specific not found
            try:
                template = self.env.get_template(f"default/{template_name}.jinja2")
                return template.render(engine=engine, **context)
            except Exception:
                # Return a basic template if file not found
                return self._get_fallback_template(engine, template_name, context)
    
    def render_academy_prompt(
        self,
        template_name: str,
        **context: Any
    ) -> str:
        """
        Render an Academy-specific educational template.
        
        Args:
            template_name: Template file name (without extension)
            **context: Variables to pass to the template
            
        Returns:
            Rendered template string
        """
        try:
            template = self.env.get_template(f"academy/{template_name}.jinja2")
            return template.render(**context)
        except Exception:
            return self._get_fallback_academy_template(template_name, context)
    
    def _get_fallback_template(
        self,
        engine: str,
        template_name: str,
        context: Dict[str, Any]
    ) -> str:
        """Provide fallback templates when files don't exist."""
        
        if template_name == "architecture":
            return f"""You are creating a {engine} game with the following architecture principles:

1. Clear separation of concerns
2. Modular component design
3. Efficient resource management
4. Responsive controls and UI
5. Proper error handling

Focus on creating clean, maintainable code that follows {engine} best practices."""

        elif template_name == "code_structure":
            return f"""Create a complete {engine} game with:

- Main game loop
- Entity/component system
- Input handling
- Rendering pipeline
- Audio management
- State management
- Asset loading
- Configuration

Ensure all code is production-ready and follows {engine} conventions."""

        else:
            return f"Create {template_name} for {engine} game development."
    
    def _get_fallback_academy_template(
        self,
        template_name: str,
        context: Dict[str, Any]
    ) -> str:
        """Provide fallback templates for Academy mode."""
        
        if template_name == "teachable_moment":
            return """Identify a teachable moment in this code:

1. What programming concept is demonstrated?
2. Why is this important for game development?
3. What are common mistakes to avoid?
4. How can this be practiced?

Make it engaging and appropriate for the student's level."""

        elif template_name == "lesson_plan":
            return """Create a lesson plan that:

1. Introduces the concept clearly
2. Shows practical game examples
3. Provides hands-on exercises
4. Builds on previous knowledge
5. Includes fun challenges

Keep it encouraging and game-focused!"""

        else:
            return f"Create educational {template_name} for game programming."
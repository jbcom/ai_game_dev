"""Jinja2 templates for engine-specific code generation."""

from jinja2 import Environment, FileSystemLoader
from pathlib import Path

def get_template_environment(engine: str):
    """Get Jinja2 environment for specific engine."""
    template_dir = Path(__file__).parent / engine
    if template_dir.exists():
        return Environment(loader=FileSystemLoader(str(template_dir)))
    return None
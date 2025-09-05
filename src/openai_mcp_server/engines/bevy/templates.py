"""Bevy Jinja2 template manager."""

from jinja2 import Environment, DictLoader

class BevyTemplateManager:
    """Template manager for Bevy code generation."""
    
    def __init__(self):
        self.templates = {}
        
    async def initialize(self):
        pass
"""
WebAssembly deployment tools for AI Game Development.
Specialized support for pygame WebAssembly compilation via pygbag.
"""

from .pygbag_deploy import deploy_pygame_to_web, PygbagConfig

__all__ = ["deploy_pygame_to_web", "PygbagConfig"]
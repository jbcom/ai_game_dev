"""
AI Game Development Education Module
Interactive learning platform for game development with Professor Pixel
"""

try:
    from .run_education import main
except ImportError:
    # Handle import during development
    main = None

__all__ = ["main"]
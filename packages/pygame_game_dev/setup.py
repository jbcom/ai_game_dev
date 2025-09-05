#!/usr/bin/env python3
"""
pygame_game_dev - Specialized Python library for 2D game development
Built on top of ai_game_dev with PyGame-specific optimizations.
"""
from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_path = Path(__file__).parent / "README.md"
long_description = readme_path.read_text() if readme_path.exists() else ""

setup(
    name="pygame_game_dev",
    version="1.0.0",
    description="AI-powered 2D game development with PyGame integration",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="AI Game Dev Team",
    author_email="team@ai-game-dev.com",
    url="https://github.com/ai-game-dev/pygame-game-dev",
    packages=find_packages(),
    python_requires=">=3.11",
    install_requires=[
        "ai-game-dev>=1.0.0",
        "pygame>=2.5.0",
        "numpy>=1.24.0",
        "pillow>=10.0.0",
        "pymunk>=6.5.0",  # 2D physics
        "pytmx>=3.32.0",  # Tiled map support
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "ruff>=0.1.0",
        ],
        "physics": ["pymunk>=6.5.0"],
        "tiles": ["pytmx>=3.32.0"],
        "audio": ["pygame>=2.5.0"],
    },
    entry_points={
        "console_scripts": [
            "pygame-game-dev=pygame_game_dev.cli:main",
            "pg-create-game=pygame_game_dev.generator:create_game_cli",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Games/Entertainment",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Multimedia :: Graphics",
    ],
    keywords="pygame 2d games ai generation development sprites physics",
)
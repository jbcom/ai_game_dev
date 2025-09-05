#!/usr/bin/env python3
"""
arcade_game_dev - Educational and web-deployable game development
Built on top of ai_game_dev with Arcade-specific features for learning and web deployment.
"""
from setuptools import setup, find_packages
from pathlib import Path

readme_path = Path(__file__).parent / "README.md"
long_description = readme_path.read_text() if readme_path.exists() else ""

setup(
    name="arcade_game_dev",
    version="1.0.0", 
    description="AI-powered educational game development with web deployment support",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="AI Game Dev Team",
    author_email="team@ai-game-dev.com",
    url="https://github.com/ai-game-dev/arcade-game-dev",
    packages=find_packages(),
    python_requires=">=3.11",
    install_requires=[
        "ai-game-dev>=1.0.0",
        "arcade>=2.6.0",
        "numpy>=1.24.0",
        "pillow>=10.0.0",
        "pyglet>=2.0.0",
        "pymunk>=6.5.0",
    ],
    extras_require={
        "web": [
            "pyodide-build>=0.25.0",
            "micropip>=0.5.0",
        ],
        "education": [
            "matplotlib>=3.7.0",
            "pandas>=2.0.0",
        ],
        "accessibility": [
            "pygame>=2.5.0",  # For audio fallbacks
            "speech-recognition>=3.10.0",
        ],
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0", 
            "black>=23.0.0",
            "ruff>=0.1.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "arcade-game-dev=arcade_game_dev.cli:main",
            "arcade-create=arcade_game_dev.generator:create_game_cli",
            "arcade-deploy-web=arcade_game_dev.web:deploy_cli",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta", 
        "Intended Audience :: Education",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12", 
        "Topic :: Education",
        "Topic :: Games/Entertainment",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords="arcade games education web deployment pyodide learning accessibility",
)
"""Centralized constants and configuration for AI Game Dev platform."""

from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
PUBLIC_DIR = PROJECT_ROOT / "public"
ASSETS_DIR = PUBLIC_DIR / "static" / "assets"
GENERATED_ASSETS_DIR = ASSETS_DIR / "generated"
GENERATED_GAMES_DIR = PROJECT_ROOT / "generated_games"

# OpenAI Model Configuration
OPENAI_MODELS = {
    "text": {
        "default": "gpt-5",  # Latest GPT-5 model
        "fallback": "gpt-4-turbo-preview",
        "educational": "gpt-5",  # Best for educational content
        "code_generation": "gpt-5",  # Best for code generation
    },
    "image": {
        "default": "gpt-image-1",  # Latest DALL-E model
        "fallback": "dall-e-3",
    },
    "audio": {
        "tts": "tts-1-hd",  # High quality text-to-speech
        "tts_voices": ["alloy", "echo", "fable", "onyx", "nova", "shimmer"],
    }
}

# Image Generation Settings
IMAGE_SETTINGS = {
    "sizes": {
        "square": "1024x1024",
        "landscape": "1792x1024", 
        "portrait": "1024x1792",
    },
    "quality": {
        "standard": "standard",
        "hd": "hd",
    },
    "styles": {
        "natural": "natural",
        "vivid": "vivid",
    }
}

# Game Engine Configurations
GAME_ENGINES = {
    "pygame": {
        "name": "Pygame",
        "language": "python",
        "file_extension": ".py",
        "main_file": "main.py",
        "package_manager": "pip",
        "dependencies": ["pygame>=2.5.0"],
    },
    "godot": {
        "name": "Godot",
        "language": "gdscript", 
        "file_extension": ".gd",
        "main_file": "Main.gd",
        "project_file": "project.godot",
        "version": "4.2",
    },
    "bevy": {
        "name": "Bevy",
        "language": "rust",
        "file_extension": ".rs",
        "main_file": "src/main.rs",
        "package_manager": "cargo",
        "version": "0.12",
        "dependencies": ["bevy = \"0.12\""],
    }
}

# Educational Settings
EDUCATIONAL_LEVELS = {
    "beginner": {
        "concepts": ["variables", "loops", "conditionals", "functions"],
        "max_complexity": 3,
        "comment_density": "high",
    },
    "intermediate": {
        "concepts": ["classes", "inheritance", "data structures", "algorithms"],
        "max_complexity": 6,
        "comment_density": "medium",
    },
    "advanced": {
        "concepts": ["design patterns", "optimization", "concurrency", "architecture"],
        "max_complexity": 10,
        "comment_density": "low",
    }
}

# Asset Generation Settings
ASSET_SETTINGS = {
    "art_styles": [
        "pixel art",
        "digital art",
        "concept art",
        "cartoon",
        "realistic",
        "minimalist",
        "retro",
        "cyberpunk",
        "fantasy",
        "sci-fi"
    ],
    "audio": {
        "music": {
            "tempo_range": (60, 180),
            "genres": ["electronic", "orchestral", "chiptune", "ambient"],
        },
        "sfx": {
            "categories": ["ui", "movement", "combat", "environment", "feedback"],
        }
    }
}

# Chainlit UI Settings
CHAINLIT_CONFIG = {
    "port": 8000,
    "host": "127.0.0.1",
    "theme": "cyberpunk",
    "modes": ["workshop", "academy"],
    "wizard_steps": {
        "workshop": [
            "game_description",
            "engine_selection", 
            "feature_detection",
            "asset_generation",
            "code_generation",
            "review_export"
        ],
        "academy": [
            "skill_assessment",
            "lesson_selection",
            "guided_tutorial",
            "practice_challenge",
            "knowledge_check",
            "project_showcase"
        ]
    }
}

# API Keys and External Services
EXTERNAL_SERVICES = {
    "freesound": {
        "api_url": "https://freesound.org/apiv2",
        "rate_limit": 60,  # requests per minute
    },
    "openai": {
        "api_timeout": 60,  # seconds
        "max_retries": 3,
    }
}

# File Size Limits
FILE_LIMITS = {
    "max_image_size_mb": 10,
    "max_audio_size_mb": 20,
    "max_code_file_kb": 500,
    "max_project_size_mb": 100,
}

# Unified Platform Spec Path
PLATFORM_SPEC_PATH = PROJECT_ROOT / "src" / "ai_game_dev" / "specs" / "unified_platform_spec.toml"
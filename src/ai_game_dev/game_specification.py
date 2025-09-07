"""
Game Specification Parser
Parses TOML game specifications for comprehensive AI asset generation
"""

import toml
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum


class AssetCategory(Enum):
    """Asset categories for comprehensive game generation."""
    CHARACTERS = "characters"
    ENVIRONMENTS = "environments"
    UI_ELEMENTS = "ui_elements"
    AUDIO = "audio"
    CODE = "code"
    YARN_SPINNER = "yarn_spinner"
    EDUCATIONAL = "educational"


@dataclass
class GameAssetSpec:
    """Specification for a game asset to be generated."""
    name: str
    category: AssetCategory
    prompts: List[str]
    size: str = "512x512"
    quality: str = "hd"
    style: str = "cyberpunk"
    additional_params: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)


@dataclass
class GameSpecification:
    """Complete game specification parsed from TOML."""
    name: str
    description: str
    generation_method: str
    assets: Dict[str, List[GameAssetSpec]] = field(default_factory=dict)
    audio_specs: Dict[str, Any] = field(default_factory=dict)
    batch_config: Dict[str, Any] = field(default_factory=dict)
    educational_config: Dict[str, Any] = field(default_factory=dict)


class GameSpecificationParser:
    """Parser for TOML game specifications."""
    
    def __init__(self, specs_directory: str = "src/ai_game_dev/specs"):
        self.specs_directory = Path(specs_directory)
    
    def parse_platform_assets_spec(self) -> GameSpecification:
        """Parse the comprehensive platform assets specification."""
        spec_file = self.specs_directory / "web_platform_assets.toml"
        
        if not spec_file.exists():
            raise FileNotFoundError(f"Game specification file not found: {spec_file}")
        
        with open(spec_file, 'r') as f:
            toml_data = toml.load(f)
        
        # Extract platform info
        platform_info = toml_data.get("platform_info", {})
        
        game_spec = GameSpecification(
            name=platform_info.get("name", "AI Game Dev Platform"),
            description=platform_info.get("description", ""),
            generation_method=platform_info.get("generation_method", "internal_batch_tooling")
        )
        
        # Parse asset specifications
        assets_data = toml_data.get("assets", {})
        
        # Character assets (Professor Pixel, RPG characters)
        character_assets = []
        
        # Professor Pixel educational character
        if "professor_pixel" in assets_data:
            prof_pixel = assets_data["professor_pixel"]
            character_assets.append(GameAssetSpec(
                name="professor_pixel",
                category=AssetCategory.CHARACTERS,
                prompts=prof_pixel.get("prompts", []),
                size=prof_pixel.get("size", "512x512"),
                quality=prof_pixel.get("quality", "hd"),
                style="cyberpunk_educational"
            ))
        
        # RPG Character Classes
        if "rpg_characters" in assets_data:
            rpg_chars = assets_data["rpg_characters"]
            character_assets.append(GameAssetSpec(
                name="rpg_character_classes",
                category=AssetCategory.CHARACTERS,
                prompts=rpg_chars.get("prompts", []),
                size=rpg_chars.get("size", "64x64"),
                quality=rpg_chars.get("quality", "hd"),
                style="pixel_art_rpg"
            ))
        
        game_spec.assets[AssetCategory.CHARACTERS.value] = character_assets
        
        # Environment assets (NeoTokyo environments)
        environment_assets = []
        
        if "neotokyo_environments" in assets_data:
            environments = assets_data["neotokyo_environments"]
            environment_assets.append(GameAssetSpec(
                name="neotokyo_environments",
                category=AssetCategory.ENVIRONMENTS,
                prompts=environments.get("prompts", []),
                size=environments.get("size", "512x512"),
                quality=environments.get("quality", "hd"),
                style="cyberpunk_pixel_art"
            ))
        
        game_spec.assets[AssetCategory.ENVIRONMENTS.value] = environment_assets
        
        # Educational UI elements
        ui_assets = []
        
        if "educational_ui" in assets_data:
            edu_ui = assets_data["educational_ui"]
            ui_assets.append(GameAssetSpec(
                name="educational_ui_elements",
                category=AssetCategory.UI_ELEMENTS,
                prompts=edu_ui.get("prompts", []),
                size=edu_ui.get("size", "256x256"),
                quality=edu_ui.get("quality", "hd"),
                style="cyberpunk_educational_ui"
            ))
        
        game_spec.assets[AssetCategory.UI_ELEMENTS.value] = ui_assets
        
        # Audio specifications
        audio_data = toml_data.get("audio", {})
        game_spec.audio_specs = {
            "ui_sounds": audio_data.get("ui_sounds", {}),
            "game_effects": audio_data.get("game_effects", {}),
            "ambient": audio_data.get("ambient", {}),
            "generation_config": toml_data.get("audio_generation", {})
        }
        
        # Batch configuration
        game_spec.batch_config = toml_data.get("batch_config", {})
        
        # Educational configuration
        game_spec.educational_config = {
            "rpg_theme": "NeoTokyo Code Academy: The Binary Rebellion",
            "mentor_character": "Professor Pixel",
            "learning_system": "interactive_variant_system",
            "character_classes": ["Code Knight", "Data Sage", "Bug Hunter", "Web Weaver"],
            "environments": ["Code Academy", "Underground Labs", "Algorithm Towers", "Digital Marketplace"]
        }
        
        return game_spec
    
    def get_comprehensive_asset_requirements(self, game_spec: GameSpecification) -> Dict[str, List[str]]:
        """Convert game specification to asset requirements for verification."""
        
        requirements = {
            "rpg_characters": [],
            "educational_environments": [], 
            "educational_ui": [],
            "professor_pixel": [],
            "game_code": [],
            "yarn_spinner": []
        }
        
        # Character asset requirements
        for asset_spec in game_spec.assets.get(AssetCategory.CHARACTERS.value, []):
            if asset_spec.name == "professor_pixel":
                requirements["professor_pixel"].extend([
                    "src/ai_game_dev/server/static/assets/characters/professor_pixel_portrait.png",
                    "src/ai_game_dev/server/static/assets/characters/professor_pixel_sprite.png",
                    "src/ai_game_dev/server/static/assets/characters/professor_pixel_avatar.png"
                ])
            elif asset_spec.name == "rpg_character_classes":
                requirements["rpg_characters"].extend([
                    "src/ai_game_dev/server/static/assets/characters/code_knight.png",
                    "src/ai_game_dev/server/static/assets/characters/data_sage.png", 
                    "src/ai_game_dev/server/static/assets/characters/bug_hunter.png",
                    "src/ai_game_dev/server/static/assets/characters/web_weaver.png"
                ])
        
        # Environment asset requirements
        for asset_spec in game_spec.assets.get(AssetCategory.ENVIRONMENTS.value, []):
            if asset_spec.name == "neotokyo_environments":
                requirements["educational_environments"].extend([
                    "src/ai_game_dev/server/static/assets/environments/code_academy_exterior.png",
                    "src/ai_game_dev/server/static/assets/environments/underground_lab.png",
                    "src/ai_game_dev/server/static/assets/environments/algorithm_tower.png",
                    "src/ai_game_dev/server/static/assets/environments/digital_marketplace.png"
                ])
        
        # UI asset requirements
        for asset_spec in game_spec.assets.get(AssetCategory.UI_ELEMENTS.value, []):
            if asset_spec.name == "educational_ui_elements":
                requirements["educational_ui"].extend([
                    "src/ai_game_dev/server/static/assets/ui/progress_bar_learning.png",
                    "src/ai_game_dev/server/static/assets/ui/xp_notification.png",
                    "src/ai_game_dev/server/static/assets/ui/skill_tree_background.png",
                    "src/ai_game_dev/server/static/assets/ui/lesson_complete_badge.png"
                ])
        
        # Code generation requirements
        requirements["game_code"].extend([
            "src/ai_game_dev/generated/neotokyo_rpg/game.py",
            "src/ai_game_dev/generated/neotokyo_rpg/player.py",
            "src/ai_game_dev/generated/neotokyo_rpg/professor_pixel.py",
            "src/ai_game_dev/generated/neotokyo_rpg/character_classes.py",
            "src/ai_game_dev/generated/neotokyo_rpg/educational_system.py"
        ])
        
        # YarnSpinner content requirements
        requirements["yarn_spinner"].extend([
            "src/ai_game_dev/generated/dialogue/professor_pixel_intro.yarn",
            "src/ai_game_dev/generated/dialogue/character_selection.yarn",
            "src/ai_game_dev/generated/dialogue/educational_challenges.yarn",
            "src/ai_game_dev/generated/dialogue/skill_advancement.yarn"
        ])
        
        return requirements
    
    def get_asset_generation_specs(self, game_spec: GameSpecification) -> Dict[str, Any]:
        """Get detailed specifications for asset generation."""
        
        return {
            "character_generation": {
                "professor_pixel": {
                    "prompts": game_spec.assets.get(AssetCategory.CHARACTERS.value, [{}])[0].prompts if game_spec.assets.get(AssetCategory.CHARACTERS.value) else [],
                    "style": "cyberpunk_educational_mentor",
                    "variants": ["portrait", "sprite", "avatar", "teaching_pose"]
                },
                "rpg_classes": {
                    "prompts": game_spec.assets.get(AssetCategory.CHARACTERS.value, [{}])[-1].prompts if game_spec.assets.get(AssetCategory.CHARACTERS.value) else [],
                    "style": "pixel_art_cyberpunk_rpg",
                    "classes": ["Code Knight", "Data Sage", "Bug Hunter", "Web Weaver", "System Admin"]
                }
            },
            "environment_generation": {
                "neotokyo_locations": {
                    "prompts": game_spec.assets.get(AssetCategory.ENVIRONMENTS.value, [{}])[0].prompts if game_spec.assets.get(AssetCategory.ENVIRONMENTS.value) else [],
                    "style": "cyberpunk_pixel_art_educational",
                    "locations": ["Code Academy", "Underground Labs", "Algorithm Towers", "Digital Marketplace", "Virus Sectors"]
                }
            },
            "code_generation": {
                "educational_rpg": {
                    "game_title": "NeoTokyo Code Academy: The Binary Rebellion",
                    "engine": "pygame",
                    "features": ["educational_progression", "character_classes", "professor_pixel_mentor", "interactive_coding_challenges"],
                    "files": ["game.py", "player.py", "professor_pixel.py", "character_classes.py", "educational_system.py"]
                }
            },
            "yarn_spinner_generation": {
                "educational_dialogue": {
                    "characters": ["Professor Pixel", "Code Knight", "Data Sage", "Bug Hunter", "Web Weaver"],
                    "topics": ["intro_to_programming", "character_selection", "skill_challenges", "advancement_system"],
                    "style": "cyberpunk_educational_friendly"
                }
            },
            "batch_config": game_spec.batch_config
        }


def load_game_specification() -> GameSpecification:
    """Load the comprehensive game specification."""
    parser = GameSpecificationParser()
    return parser.parse_platform_assets_spec()


def get_comprehensive_asset_requirements() -> Dict[str, List[str]]:
    """Get comprehensive asset requirements for verification."""
    parser = GameSpecificationParser()
    game_spec = parser.parse_platform_assets_spec()
    return parser.get_comprehensive_asset_requirements(game_spec)


def get_asset_generation_specifications() -> Dict[str, Any]:
    """Get detailed asset generation specifications."""
    parser = GameSpecificationParser()
    game_spec = parser.parse_platform_assets_spec()
    return parser.get_asset_generation_specs(game_spec)
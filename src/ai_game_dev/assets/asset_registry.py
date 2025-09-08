"""
Centralized asset registry for tracking and coordinating generated assets.

This module provides a registry that:
1. Tracks all generated assets (sprites, audio, backgrounds, etc.)
2. Provides asset paths and metadata to code generation tools
3. Ensures consistency between asset generation and code generation
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict

from ai_game_dev.constants import ASSETS_DIR, GENERATED_ASSETS_DIR


@dataclass
class AssetInfo:
    """Information about a generated asset."""
    name: str
    path: str
    asset_type: str  # sprite, audio, background, font, etc.
    category: str    # game_elements, ui, effects, etc.
    generated: bool
    metadata: Dict[str, Any] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {k: v for k, v in asdict(self).items() if v is not None}


class AssetRegistry:
    """Central registry for all game assets."""
    
    def __init__(self):
        self.registry_path = GENERATED_ASSETS_DIR / "asset_registry.json"
        self.assets: Dict[str, List[AssetInfo]] = {
            "sprites": [],
            "audio": [],
            "backgrounds": [],
            "fonts": [],
            "ui": []
        }
        self._load_registry()
        self._scan_static_assets()
    
    def _load_registry(self):
        """Load existing registry from disk."""
        if self.registry_path.exists():
            with open(self.registry_path, 'r') as f:
                data = json.load(f)
                for asset_type, items in data.items():
                    self.assets[asset_type] = [
                        AssetInfo(**item) for item in items
                    ]
    
    def _scan_static_assets(self):
        """Scan and register existing static assets."""
        static_mappings = {
            "audio": {
                "ui": ["button_click_futuristic", "hover_beep_cyberpunk", "error_buzz_warning", 
                       "success_ding_pleasant", "notification_chime_tech"],
                "ambient": ["typing_mechanical_keyboard"],
                "menu": ["menu_open_whoosh", "menu_close_whoosh_reverse"]
            },
            "sprites": {
                "characters": ["professor_pixel"],
                "mascots": ["ai-orb-mascot", "professor-pixel-mascot", 
                           "ai-orb-transparent", "professor-pixel-transparent"],
                "panels": ["arcade-academy-panel", "game-workshop-panel", 
                          "bevy-panel", "godot-panel", "pygame-panel"]
            },
            "ui": {
                "buttons": ["play-button", "pause-button", "stop-button", 
                           "skip-button", "volume-slider"],
                "frames": ["tech-frame"],
                "logos": ["arcade-academy-condensed", "game-workshop-condensed", 
                         "main-logo", "platform-logo"]
            }
        }
        
        # Register static audio assets
        for category, sounds in static_mappings.get("audio", {}).items():
            for sound in sounds:
                asset_path = f"/public/static/assets/audio/{sound}.wav"
                if not self._asset_exists("audio", sound):
                    self.register_asset(
                        name=sound,
                        path=asset_path,
                        asset_type="audio",
                        category=category,
                        generated=False
                    )
        
        # Register static sprite assets
        for category, sprites in static_mappings.get("sprites", {}).items():
            for sprite in sprites:
                asset_path = f"/public/static/assets/{category}/{sprite}.png"
                if not self._asset_exists("sprites", sprite):
                    self.register_asset(
                        name=sprite,
                        path=asset_path,
                        asset_type="sprites",
                        category=category,
                        generated=False
                    )
        
        # Register static UI assets
        for category, items in static_mappings.get("ui", {}).items():
            for item in items:
                ext = ".svg" if item == "main-logo" else ".png"
                asset_path = f"/public/static/assets/{category}/{item}{ext}"
                if not self._asset_exists("ui", item):
                    self.register_asset(
                        name=item,
                        path=asset_path,
                        asset_type="ui",
                        category=category,
                        generated=False
                    )
    
    def _asset_exists(self, asset_type: str, name: str) -> bool:
        """Check if an asset is already registered."""
        return any(asset.name == name for asset in self.assets.get(asset_type, []))
    
    def register_asset(self, name: str, path: str, asset_type: str, 
                      category: str, generated: bool = True, 
                      metadata: Optional[Dict[str, Any]] = None) -> AssetInfo:
        """Register a new asset."""
        asset = AssetInfo(
            name=name,
            path=path,
            asset_type=asset_type,
            category=category,
            generated=generated,
            metadata=metadata or {}
        )
        
        if asset_type not in self.assets:
            self.assets[asset_type] = []
        
        # Update existing or add new
        existing_idx = next(
            (i for i, a in enumerate(self.assets[asset_type]) 
             if a.name == name and a.category == category), 
            None
        )
        
        if existing_idx is not None:
            self.assets[asset_type][existing_idx] = asset
        else:
            self.assets[asset_type].append(asset)
        
        self._save_registry()
        return asset
    
    def get_assets_for_game(self, game_type: str, engine: str) -> Dict[str, Any]:
        """Get all assets formatted for a specific game type and engine."""
        assets_config = {
            "sprites": {},
            "audio": {},
            "backgrounds": [],
            "ui": {},
            "fonts": []
        }
        
        # Map asset categories to game use cases
        if game_type == "platformer":
            assets_config["sprites"] = {
                "player": self._get_asset_path("sprites", "professor_pixel", "characters"),
                "enemies": [self._get_asset_path("sprites", name, "game_elements")
                           for name in ["enemy_slime"] if self._has_asset("sprites", name)],
                "items": [self._get_asset_path("sprites", name, "game_elements")
                         for name in ["collectible_gem", "powerup_star"] if self._has_asset("sprites", name)],
                "tiles": [self._get_asset_path("sprites", "platform_tile", "game_elements")]
                         if self._has_asset("sprites", "platform_tile") else []
            }
            assets_config["audio"]["effects"] = {
                "jump": self._get_asset_path("audio", "jump", "gameplay"),
                "collect": self._get_asset_path("audio", "collect", "gameplay"),
                "damage": self._get_asset_path("audio", "damage", "gameplay")
            }
            
        elif game_type == "space_shooter":
            assets_config["sprites"] = {
                "player": self._get_asset_path("sprites", "spaceship", "vehicles")
                         if self._has_asset("sprites", "spaceship") else None,
                "enemies": [self._get_asset_path("sprites", name, "vehicles")
                           for name in ["enemy_fighter", "boss_ship"] if self._has_asset("sprites", name)],
                "projectiles": [self._get_asset_path("sprites", name, "weapons")
                               for name in ["laser_beam", "missile"] if self._has_asset("sprites", name)],
                "effects": [self._get_asset_path("sprites", name, "effects")
                           for name in ["explosion", "shield_hit"] if self._has_asset("sprites", name)]
            }
            assets_config["audio"]["effects"] = {
                "shoot": self._get_asset_path("audio", "shoot", "combat"),
                "explosion": self._get_asset_path("audio", "explosion", "combat"),
                "shield": self._get_asset_path("audio", "shield_activate", "combat")
            }
            
        elif game_type == "educational_rpg":
            # Use the full asset config from startup.py
            assets_config = self.get_educational_rpg_assets()
        
        # Add common UI sounds (these are static)
        assets_config["audio"]["ui"] = {
            "click": "/public/static/assets/audio/button_click_futuristic.wav",
            "hover": "/public/static/assets/audio/hover_beep_cyberpunk.wav",
            "success": "/public/static/assets/audio/success_ding_pleasant.wav",
            "error": "/public/static/assets/audio/error_buzz_warning.wav"
        }
        
        # Add backgrounds if available
        bg_category = "environments"
        backgrounds = [asset for asset in self.assets.get("backgrounds", [])
                      if asset.category == bg_category]
        assets_config["backgrounds"] = [asset.path for asset in backgrounds]
        
        # Format for specific engine
        return self._format_for_engine(assets_config, engine)
    
    def get_educational_rpg_assets(self) -> Dict[str, Any]:
        """Get the full asset configuration for the educational RPG."""
        return {
            "sprites": {
                "player": "/public/static/assets/characters/professor_pixel.png",
                "enemies": [f"/public/static/assets/generated/sprites/game_elements/{name}.png" 
                           for name in ["enemy_slime", "bug_creature", "error_demon"]],
                "items": [f"/public/static/assets/generated/sprites/game_elements/{name}.png"
                         for name in ["collectible_gem", "powerup_star", "health_potion"]],
                "weapons": [f"/public/static/assets/generated/sprites/weapons/{name}.png"
                           for name in ["laser_beam", "plasma_sword", "shield_bubble"]],
                "effects": [f"/public/static/assets/generated/sprites/effects/{name}.png"
                           for name in ["explosion", "sparkle", "damage_flash"]],
                "npcs": [f"/public/static/assets/generated/sprites/characters/{name}.png"
                        for name in ["mentor_ai", "student_coder", "bug_boss"]]
            },
            "backgrounds": [f"/public/static/assets/generated/backgrounds/environments/{name}.png"
                           for name in ["academy_classroom", "digital_realm", "cyberpunk_city", "boss_arena"]],
            "audio": {
                "effects": {
                    "jump": "/public/static/assets/generated/audio/gameplay/jump.wav",
                    "collect": "/public/static/assets/generated/audio/gameplay/collect.wav",
                    "damage": "/public/static/assets/generated/audio/gameplay/damage.wav",
                    "levelup": "/public/static/assets/generated/audio/gameplay/levelup.wav",
                    "shoot": "/public/static/assets/generated/audio/combat/shoot.wav",
                    "explosion": "/public/static/assets/generated/audio/combat/explosion.wav",
                    "dialogue": "/public/static/assets/generated/audio/ui/dialogue_beep.wav"
                },
                "ui": {
                    "click": "/public/static/assets/audio/button_click_futuristic.wav",
                    "hover": "/public/static/assets/audio/hover_beep_cyberpunk.wav",
                    "success": "/public/static/assets/audio/success_ding_pleasant.wav",
                    "error": "/public/static/assets/audio/error_buzz_warning.wav",
                    "notification": "/public/static/assets/audio/notification_chime_tech.wav"
                },
                "music": {
                    "menu": "/public/static/assets/generated/audio/music/menu_theme.mp3",
                    "gameplay": "/public/static/assets/generated/audio/music/exploration_theme.mp3",
                    "battle": "/public/static/assets/generated/audio/music/battle_theme.mp3",
                    "victory": "/public/static/assets/generated/audio/music/victory_theme.mp3"
                }
            },
            "fonts": [
                "/public/static/assets/fonts/inter-400.woff2",
                "/public/static/assets/fonts/inter-600.woff2",
                "/public/static/assets/fonts/jetbrains-mono-400.woff2"
            ],
            "ui": {
                "frames": ["/public/static/assets/frames/tech-frame.png"],
                "panels": ["/public/static/assets/textures/glass-panel.png"],
                "overlays": ["/public/static/assets/textures/hexagon-overlay.png"]
            }
        }
    
    def _get_asset_path(self, asset_type: str, name: str, category: str) -> Optional[str]:
        """Get the path for a specific asset."""
        for asset in self.assets.get(asset_type, []):
            if asset.name == name and (not category or asset.category == category):
                return asset.path
        return None
    
    def _has_asset(self, asset_type: str, name: str) -> bool:
        """Check if we have a specific asset."""
        return any(asset.name == name for asset in self.assets.get(asset_type, []))
    
    def _format_for_engine(self, assets: Dict[str, Any], engine: str) -> Dict[str, Any]:
        """Format asset paths for specific game engine requirements."""
        if engine == "pygame":
            # Pygame uses relative paths from the game directory
            formatted = {}
            for key, value in assets.items():
                if isinstance(value, dict):
                    formatted[key] = {
                        k: v.replace("/public/static/", "../../public/static/") if isinstance(v, str) else v
                        for k, v in value.items()
                    }
                elif isinstance(value, list):
                    formatted[key] = [
                        item.replace("/public/static/", "../../public/static/") if isinstance(item, str) else item
                        for item in value
                    ]
                else:
                    formatted[key] = value
            return formatted
            
        elif engine == "godot":
            # Godot uses res:// paths
            formatted = {}
            for key, value in assets.items():
                if isinstance(value, dict):
                    formatted[key] = {
                        k: f"res://assets/{v.split('/')[-1]}" if isinstance(v, str) else v
                        for k, v in value.items()
                    }
                elif isinstance(value, list):
                    formatted[key] = [
                        f"res://assets/{item.split('/')[-1]}" if isinstance(item, str) else item
                        for item in value
                    ]
                else:
                    formatted[key] = value
            return formatted
            
        elif engine == "bevy":
            # Bevy uses relative paths from assets/ directory
            formatted = {}
            for key, value in assets.items():
                if isinstance(value, dict):
                    formatted[key] = {
                        k: f"assets/{v.split('/')[-1]}" if isinstance(v, str) else v
                        for k, v in value.items()
                    }
                elif isinstance(value, list):
                    formatted[key] = [
                        f"assets/{item.split('/')[-1]}" if isinstance(item, str) else item
                        for item in value
                    ]
                else:
                    formatted[key] = value
            return formatted
            
        return assets
    
    def _save_registry(self):
        """Save registry to disk."""
        self.registry_path.parent.mkdir(parents=True, exist_ok=True)
        
        data = {}
        for asset_type, assets in self.assets.items():
            data[asset_type] = [asset.to_dict() for asset in assets]
        
        with open(self.registry_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def get_registry_for_code_generation(self) -> Dict[str, Any]:
        """Get a simplified registry for code generation tools."""
        return {
            "available_assets": {
                asset_type: [
                    {
                        "name": asset.name,
                        "path": asset.path,
                        "category": asset.category
                    }
                    for asset in assets
                ]
                for asset_type, assets in self.assets.items()
            },
            "asset_mappings": {
                "ui_sounds": {
                    "click": self._get_asset_path("audio", "button_click_futuristic", "ui"),
                    "hover": self._get_asset_path("audio", "hover_beep_cyberpunk", "ui"),
                    "success": self._get_asset_path("audio", "success_ding_pleasant", "ui"),
                    "error": self._get_asset_path("audio", "error_buzz_warning", "ui")
                },
                "common_sprites": {
                    "player_default": self._get_asset_path("sprites", "professor_pixel", "characters"),
                    "collectible": self._get_asset_path("sprites", "collectible_gem", "game_elements"),
                    "enemy_basic": self._get_asset_path("sprites", "enemy_slime", "game_elements")
                }
            }
        }


# Global registry instance
_registry = None

def get_asset_registry() -> AssetRegistry:
    """Get the global asset registry instance."""
    global _registry
    if _registry is None:
        _registry = AssetRegistry()
    return _registry
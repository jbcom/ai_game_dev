"""
Game specification loader for both internal and external use.

This module provides a unified way to load and validate game specifications
from TOML files, ensuring consistency between internal platform needs and
external user specifications.
"""

import tomllib
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field

from ai_game_dev.constants import PROJECT_ROOT, ASSETS_DIR


@dataclass
class GameSpec:
    """Standardized game specification."""
    # Core metadata
    title: str
    engine: str
    type: str
    version: str = "1.0.0"
    save_path: str = ""
    
    # Description
    description_short: str = ""
    description_full: str = ""
    
    # Features
    features: Dict[str, Any] = field(default_factory=dict)
    
    # Assets with resolved paths
    assets: Dict[str, Any] = field(default_factory=dict)
    
    # Game-specific data
    characters: Dict[str, Any] = field(default_factory=dict)
    levels: Dict[str, Any] = field(default_factory=dict)
    mechanics: Dict[str, Any] = field(default_factory=dict)
    dialogue: Dict[str, Any] = field(default_factory=dict)
    ui: Dict[str, Any] = field(default_factory=dict)
    
    # Educational features (optional)
    educational: Optional[Dict[str, Any]] = None
    
    def get_absolute_save_path(self) -> Path:
        """Get absolute path for saving the game."""
        if self.save_path.startswith("/"):
            return Path(self.save_path)
        return PROJECT_ROOT / self.save_path
    
    def resolve_asset_paths(self, base_path: Path = ASSETS_DIR) -> Dict[str, Any]:
        """Resolve all asset paths to absolute paths."""
        resolved = {}
        
        for asset_type, assets in self.assets.items():
            if isinstance(assets, dict):
                resolved[asset_type] = {}
                for key, path in assets.items():
                    if isinstance(path, str):
                        resolved[asset_type][key] = self._resolve_path(path, base_path)
                    elif isinstance(path, list):
                        resolved[asset_type][key] = [
                            self._resolve_path(p, base_path) for p in path
                        ]
                    else:
                        resolved[asset_type][key] = path
            elif isinstance(assets, list):
                resolved[asset_type] = [
                    self._resolve_path(path, base_path) if isinstance(path, str) else path
                    for path in assets
                ]
            elif isinstance(assets, str):
                resolved[asset_type] = self._resolve_path(assets, base_path)
            else:
                resolved[asset_type] = assets
                
        return resolved
    
    def _resolve_path(self, path: str, base_path: Path) -> str:
        """Resolve a single asset path."""
        if path.startswith("/"):
            # Absolute path
            return path
        elif path.startswith("generated/"):
            # Generated asset
            return f"/public/static/assets/{path}"
        else:
            # Static asset
            return f"/public/static/assets/{path}"
    
    def get_engine_specific_paths(self) -> Dict[str, Any]:
        """Get asset paths formatted for the specific engine."""
        assets = self.resolve_asset_paths()
        
        if self.engine == "pygame":
            # Pygame uses relative paths from game directory
            return self._convert_paths_relative(assets, "../../public/static/assets")
        elif self.engine == "godot":
            # Godot uses res:// paths
            return self._convert_paths_godot(assets)
        elif self.engine == "bevy":
            # Bevy uses paths relative to assets/ directory
            return self._convert_paths_bevy(assets)
        
        return assets
    
    def _convert_paths_relative(self, assets: Dict[str, Any], base: str) -> Dict[str, Any]:
        """Convert paths to relative format."""
        converted = {}
        for key, value in assets.items():
            if isinstance(value, dict):
                converted[key] = self._convert_paths_relative(value, base)
            elif isinstance(value, list):
                converted[key] = [
                    v.replace("/public/static/assets", base) if isinstance(v, str) else v
                    for v in value
                ]
            elif isinstance(value, str):
                converted[key] = value.replace("/public/static/assets", base)
            else:
                converted[key] = value
        return converted
    
    def _convert_paths_godot(self, assets: Dict[str, Any]) -> Dict[str, Any]:
        """Convert paths to Godot res:// format."""
        converted = {}
        for key, value in assets.items():
            if isinstance(value, dict):
                converted[key] = self._convert_paths_godot(value)
            elif isinstance(value, list):
                converted[key] = [
                    f"res://assets/{Path(v).name}" if isinstance(v, str) else v
                    for v in value
                ]
            elif isinstance(value, str):
                converted[key] = f"res://assets/{Path(value).name}"
            else:
                converted[key] = value
        return converted
    
    def _convert_paths_bevy(self, assets: Dict[str, Any]) -> Dict[str, Any]:
        """Convert paths to Bevy assets/ format."""
        converted = {}
        for key, value in assets.items():
            if isinstance(value, dict):
                converted[key] = self._convert_paths_bevy(value)
            elif isinstance(value, list):
                converted[key] = [
                    f"assets/{Path(v).name}" if isinstance(v, str) else v
                    for v in value
                ]
            elif isinstance(value, str):
                converted[key] = f"assets/{Path(value).name}"
            else:
                converted[key] = value
        return converted


class GameSpecLoader:
    """Loader for game specifications."""
    
    def __init__(self, specs_dir: Optional[Path] = None):
        self.specs_dir = specs_dir or (PROJECT_ROOT / "src" / "ai_game_dev" / "specs")
    
    def load_spec(self, spec_path: str | Path) -> GameSpec:
        """Load a game specification from a TOML file."""
        if isinstance(spec_path, str):
            # Check if it's a filename in the specs directory
            if not spec_path.startswith("/") and not Path(spec_path).exists():
                spec_path = self.specs_dir / spec_path
            spec_path = Path(spec_path)
        
        with open(spec_path, 'rb') as f:
            data = tomllib.load(f)
        
        return self._parse_spec(data)
    
    def _parse_spec(self, data: Dict[str, Any]) -> GameSpec:
        """Parse TOML data into a GameSpec object."""
        game_data = data.get('game', {})
        
        # Extract description
        desc = game_data.get('description', {})
        if isinstance(desc, dict):
            desc_short = desc.get('short', '')
            desc_full = desc.get('full', '')
        else:
            desc_short = str(desc)
            desc_full = str(desc)
        
        spec = GameSpec(
            title=game_data.get('title', 'Untitled Game'),
            engine=game_data.get('engine', 'pygame'),
            type=game_data.get('type', 'general'),
            version=game_data.get('version', '1.0.0'),
            save_path=game_data.get('save_path', ''),
            description_short=desc_short,
            description_full=desc_full,
            features=game_data.get('features', {}),
            assets=game_data.get('assets', {}),
            characters=game_data.get('characters', {}),
            levels=game_data.get('levels', {}),
            mechanics=game_data.get('mechanics', {}),
            dialogue=game_data.get('dialogue', {}),
            ui=game_data.get('ui', {}),
            educational=game_data.get('educational')
        )
        
        return spec
    
    def load_platform_specs(self) -> Dict[str, GameSpec]:
        """Load all platform game specifications."""
        platform_spec_path = self.specs_dir / "unified_platform_spec.toml"
        
        with open(platform_spec_path, 'rb') as f:
            platform_data = tomllib.load(f)
        
        specs = {}
        game_specs = platform_data.get('game_specs', {})
        
        for name, spec_file in game_specs.items():
            try:
                spec = self.load_spec(spec_file)
                specs[name] = spec
            except Exception as e:
                print(f"Error loading spec {spec_file}: {e}")
        
        return specs
    
    def validate_spec(self, spec: GameSpec) -> List[str]:
        """Validate a game specification and return any errors."""
        errors = []
        
        # Required fields
        if not spec.title:
            errors.append("Missing required field: title")
        if not spec.engine:
            errors.append("Missing required field: engine")
        elif spec.engine not in ["pygame", "godot", "bevy"]:
            errors.append(f"Invalid engine: {spec.engine}")
        if not spec.type:
            errors.append("Missing required field: type")
        
        # Validate asset paths exist or will be generated
        for asset_type, assets in spec.assets.items():
            errors.extend(self._validate_assets(assets, asset_type))
        
        return errors
    
    def _validate_assets(self, assets: Any, asset_type: str, path: str = "") -> List[str]:
        """Recursively validate asset paths."""
        errors = []
        
        if isinstance(assets, dict):
            for key, value in assets.items():
                new_path = f"{path}.{key}" if path else key
                errors.extend(self._validate_assets(value, asset_type, new_path))
        elif isinstance(assets, list):
            for i, item in enumerate(assets):
                new_path = f"{path}[{i}]" if path else f"[{i}]"
                errors.extend(self._validate_assets(item, asset_type, new_path))
        elif isinstance(assets, str):
            # Basic path validation
            if not assets:
                errors.append(f"Empty asset path at {asset_type}.{path}")
        
        return errors


# Convenience functions
def load_game_spec(spec_path: str | Path) -> GameSpec:
    """Load a game specification from a file."""
    loader = GameSpecLoader()
    return loader.load_spec(spec_path)


def load_platform_specs() -> Dict[str, GameSpec]:
    """Load all platform game specifications."""
    loader = GameSpecLoader()
    return loader.load_platform_specs()
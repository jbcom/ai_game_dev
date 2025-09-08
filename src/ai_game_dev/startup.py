"""
Startup generation system for AI Game Development Platform.
Idempotently generates all example games and assets on server startup.
"""
import asyncio
import json
import tomllib
from pathlib import Path
from typing import Dict, Any, List

from ai_game_dev.agent import create_game, create_educational_game
from ai_game_dev.graphics import generate_game_sprite, generate_ui_pack, generate_game_background
try:
    from ai_game_dev.graphics import generate_3d_model, generate_game_3d_asset
    HAS_3D = True
except ImportError:
    HAS_3D = False
from ai_game_dev.audio import generate_sound_effect, generate_background_music
from ai_game_dev.constants import GENERATED_ASSETS_DIR, GAMES_DIR, PLATFORM_SPEC_PATH, ASSETS_DIR
from ai_game_dev.text import get_rpg_specification
from ai_game_dev.assets.asset_registry import get_asset_registry
from ai_game_dev.specs.game_spec_loader import load_platform_specs


# Example game specifications
EXAMPLE_GAMES = {
    "platformer": {
        "title": "Pixel Quest Adventures",
        "description": "A classic 2D platformer with pixel art style, featuring a brave hero collecting gems while avoiding enemies",
        "engine": "pygame",
        "genre": "platformer",
        "features": ["player_movement", "jumping", "double_jump", "enemy_ai", "collectibles", "score_system"],
        "educational": False
    },
    "space_shooter": {
        "title": "Galactic Defender", 
        "description": "A fast-paced space shooter where you defend Earth from alien invaders with upgradeable weapons",
        "engine": "pygame",
        "genre": "shooter",
        "features": ["shooting", "enemy_waves", "power_ups", "boss_battles", "high_score"],
        "educational": False
    },
    "puzzle_game": {
        "title": "Crystal Match Quest",
        "description": "A match-3 puzzle game with fantasy theme and spell-casting mechanics",
        "engine": "pygame", 
        "genre": "puzzle",
        "features": ["match_mechanics", "combos", "special_powers", "level_progression"],
        "educational": False
    },
    "bevy_adventure": {
        "title": "Rust Realms",
        "description": "A 3D adventure game showcasing Bevy engine capabilities with exploration and combat",
        "engine": "bevy",
        "genre": "adventure",
        "features": ["3d_movement", "combat_system", "inventory", "quest_system"],
        "educational": False
    },
    "godot_rpg": {
        "title": "Forest of Shadows",
        "description": "A 2D RPG with dialogue trees and turn-based combat built in Godot",
        "engine": "godot",
        "genre": "rpg",
        "features": ["dialogue_system", "turn_based_combat", "inventory", "save_system"],
        "educational": False
    },
    "educational_rpg": {
        "title": "NeoTokyo Code Academy",
        "description": "An educational RPG where students learn programming through cyberpunk adventures",
        "engine": "pygame",
        "genre": "rpg",
        "features": ["interactive_lessons", "code_challenges", "progress_tracking", "achievements"],
        "educational": True,
        "concepts": ["variables", "loops", "functions", "classes", "debugging"]
    }
}

# Static assets that already exist - don't regenerate these
EXISTING_ASSETS = {
    "audio": {
        "ui": ["button_click_futuristic", "hover_beep_cyberpunk", "error_buzz_warning", 
                "success_ding_pleasant", "notification_chime_tech"],
        "menu": ["menu_open_whoosh", "menu_close_whoosh_reverse"],
        "ambient": ["typing_mechanical_keyboard"]
    },
    "sprites": {
        "characters": ["professor_pixel"],
        "mascots": ["ai-orb-mascot", "professor-pixel-mascot"],
        "ui": ["play-button", "pause-button", "stop-button", "skip-button", "volume-slider"]
    },
    "panels": ["arcade-academy-panel", "game-workshop-panel", "bevy-panel", "godot-panel", "pygame-panel"]
}

# Assets to generate that don't exist yet
ASSETS_TO_GENERATE = {
    "sprites": {
        "game_elements": ["collectible_gem", "enemy_slime", "platform_tile", "powerup_star", 
                         "health_potion", "bug_creature", "error_demon"],
        "weapons": ["laser_beam", "plasma_sword", "shield_bubble", "missile"],
        "effects": ["explosion", "sparkle", "damage_flash", "shield_hit"],
        "characters": ["mentor_ai", "student_coder", "bug_boss", "pixel_hero"],
        "vehicles": ["spaceship", "enemy_fighter", "boss_ship"]
    },
    "audio": {
        "gameplay": ["jump", "collect", "damage", "levelup"],
        "combat": ["shoot", "explosion", "shield_activate"],
        "ui": ["dialogue_beep"],
        "music": ["menu_theme", "exploration_theme", "battle_theme", "victory_theme"]
    },
    "backgrounds": {
        "environments": ["cyberpunk_city", "digital_realm", "academy_classroom", "boss_arena",
                        "colorful_hills", "space_nebula"]
    }
}


class StartupGenerator:
    """Handles idempotent generation of example games and assets."""
    
    def __init__(self):
        self.assets_dir = Path(GENERATED_ASSETS_DIR)
        self.games_dir = Path(GAMES_DIR)
        self.specs_dir = Path("src/ai_game_dev/specs")
        self.manifest_path = self.assets_dir / "manifest.json"
        self.platform_spec = self._load_platform_spec()
        
    async def generate_all(self):
        """Generate all startup assets and example games."""
        print("🚀 Starting asset and example generation...")
        
        # Create directories
        self.assets_dir.mkdir(parents=True, exist_ok=True)
        self.games_dir.mkdir(parents=True, exist_ok=True)
        
        # Load existing manifest
        manifest = self._load_manifest()
        
        # Generate common assets
        await self._generate_common_assets(manifest)
        
        # Generate all games and server assets from specs
        await self._generate_example_games(manifest)
        
        # Save updated manifest
        self._save_manifest(manifest)
        
        print("✅ Startup generation complete!")
        
    def _load_platform_spec(self) -> Dict[str, Any]:
        """Load the unified platform specification."""
        if PLATFORM_SPEC_PATH.exists():
            with open(PLATFORM_SPEC_PATH, 'rb') as f:
                return tomllib.load(f)
        return {}
        
    def _load_manifest(self) -> Dict[str, Any]:
        """Load generation manifest to track what's already been created."""
        if self.manifest_path.exists():
            with open(self.manifest_path, 'r') as f:
                return json.load(f)
        return {"assets": {}, "games": {}}
        
    def _save_manifest(self, manifest: Dict[str, Any]):
        """Save generation manifest."""
        with open(self.manifest_path, 'w') as f:
            json.dump(manifest, f, indent=2)
            
    async def _generate_common_assets(self, manifest: Dict[str, Any]):
        """Generate common assets that don't already exist as static files."""
        print("🎨 Generating missing assets...")
        
        # Get asset registry
        registry = get_asset_registry()
        
        # Sprites
        for category, items in ASSETS_TO_GENERATE.get("sprites", {}).items():
            sprite_dir = self.assets_dir / "sprites" / category
            sprite_dir.mkdir(parents=True, exist_ok=True)
            
            for item in items:
                asset_key = f"sprite_{category}_{item}"
                
                if asset_key not in manifest.get("assets", {}):
                    print(f"  Creating sprite: {category}/{item}")
                    
                    # Generate sprite with appropriate style
                    style = "pixel" if category == "game_elements" else "digital"
                    result = await generate_game_sprite(
                        name=item,
                        description=f"{item.replace('_', ' ')} sprite for games",
                        style=style,
                        save_path=str(sprite_dir / f"{item}.png")
                    )
                    
                    # Register in asset registry
                    asset_path = f"/public/static/assets/generated/sprites/{category}/{item}.png"
                    registry.register_asset(
                        name=item,
                        path=asset_path,
                        asset_type="sprites",
                        category=category,
                        generated=True
                    )
                    
                    manifest["assets"][asset_key] = {
                        "type": "sprite",
                        "category": category,
                        "name": item,
                        "path": str(sprite_dir / f"{item}.png"),
                        "generated": True
                    }
        
        # Audio
        for category, sounds in ASSETS_TO_GENERATE.get("audio", {}).items():
            audio_dir = self.assets_dir / "audio" / category
            audio_dir.mkdir(parents=True, exist_ok=True)
            
            for sound in sounds:
                asset_key = f"audio_{category}_{sound}"
                
                if asset_key not in manifest.get("assets", {}):
                    print(f"  Creating sound: {category}/{sound}")
                    
                    result = await generate_sound_effect(
                        effect_name=sound,
                        style="retro" if category == "gameplay" else "modern",
                        save_path=str(audio_dir / f"{sound}.wav")
                    )
                    
                    # Register in asset registry
                    asset_path = f"/public/static/assets/generated/audio/{category}/{sound}.wav"
                    registry.register_asset(
                        name=sound,
                        path=asset_path,
                        asset_type="audio",
                        category=category,
                        generated=True
                    )
                    
                    manifest["assets"][asset_key] = {
                        "type": "audio",
                        "category": category,
                        "name": sound,
                        "path": result.path if hasattr(result, 'path') else str(audio_dir / f"{sound}.wav"),
                        "generated": True
                    }
        
        # Music tracks
        music_tracks = ASSETS_TO_GENERATE.get("audio", {}).get("music", [])
        if music_tracks:
            music_dir = self.assets_dir / "audio" / "music"
            music_dir.mkdir(parents=True, exist_ok=True)
            
            for track in music_tracks:
                asset_key = f"audio_music_{track}"
                
                if asset_key not in manifest.get("assets", {}):
                    print(f"  Creating music: {track}")
                    
                    # Determine music style based on track name
                    style = "electronic"
                    if "battle" in track:
                        style = "orchestral"
                    elif "menu" in track:
                        style = "ambient"
                    elif "victory" in track:
                        style = "chiptune"
                    
                    result = await generate_background_music(
                        name=track.replace('_', ' '),
                        style=style,
                        duration=120,  # 2 minutes
                        save_path=str(music_dir / f"{track}.mp3")
                    )
                    
                    # Register in asset registry
                    asset_path = f"/public/static/assets/generated/audio/music/{track}.mp3"
                    registry.register_asset(
                        name=track,
                        path=asset_path,
                        asset_type="audio",
                        category="music",
                        generated=True
                    )
                    
                    manifest["assets"][asset_key] = {
                        "type": "audio",
                        "category": "music",
                        "name": track,
                        "path": result.path if hasattr(result, 'path') else str(music_dir / f"{track}.mp3"),
                        "generated": True
                    }
        
        # Backgrounds
        for category, items in ASSETS_TO_GENERATE.get("backgrounds", {}).items():
            bg_dir = self.assets_dir / "backgrounds" / category
            bg_dir.mkdir(parents=True, exist_ok=True)
            
            for item in items:
                asset_key = f"background_{category}_{item}"
                
                if asset_key not in manifest.get("assets", {}):
                    print(f"  Creating background: {category}/{item}")
                    
                    result = await generate_game_background(
                        scene=item.replace('_', ' '),
                        style="cyberpunk" if "cyberpunk" in item else "digital",
                        save_path=str(bg_dir / f"{item}.png")
                    )
                    
                    # Register in asset registry
                    asset_path = f"/public/static/assets/generated/backgrounds/{category}/{item}.png"
                    registry.register_asset(
                        name=item,
                        path=asset_path,
                        asset_type="backgrounds",
                        category=category,
                        generated=True
                    )
                    
                    manifest["assets"][asset_key] = {
                        "type": "background",
                        "category": category,
                        "name": item,
                        "path": str(bg_dir / f"{item}.png"),
                        "generated": True
                    }
                    
    async def _generate_example_games(self, manifest: Dict[str, Any]):
        """Generate example games from platform specs."""
        print("🎮 Generating example games...")
        
        # Load all platform game specs
        platform_specs = load_platform_specs()
        
        for spec_name, spec_data in platform_specs.items():
            # Handle server assets separately
            if spec_name == "server_assets":
                await self._generate_server_assets(manifest, spec_data)
                continue
                
            # Skip if not a game spec
            if not hasattr(spec_data, 'title'):
                continue
                
            game_spec = spec_data
            game_key = spec_name
            if game_key not in manifest.get("games", {}):
                print(f"\n  Creating {game_spec.title} ({game_spec.engine})...")
                
                try:
                    # Get asset paths for this engine
                    asset_paths = game_spec.get_engine_specific_paths()
                    
                    # Generate the game using the spec
                    output_dir = game_spec.get_absolute_save_path()
                    output_dir.mkdir(parents=True, exist_ok=True)
                    
                    # Check if this game needs 3D models
                    if game_spec.engine == "godot" and HAS_3D and "model_specs" in game_spec.assets:
                        await self._generate_3d_models_for_game(manifest, game_spec)
                    
                    # Create full game specification
                    full_spec = {
                        "title": game_spec.title,
                        "type": game_spec.type,
                        "engine": game_spec.engine,
                        "description": game_spec.description_full or game_spec.description_short,
                        "assets": asset_paths,
                        "mechanics": game_spec.mechanics,
                        "levels": game_spec.levels,
                        "features": game_spec.features
                    }
                    
                    # Generate the game
                    project = await create_game(
                        description=game_spec.description_full or game_spec.description_short,
                        engine=game_spec.engine,
                        game_spec=full_spec
                    )
                    
                    # Write game files
                    for filename, content in project.code_files.items():
                        (output_dir / filename).write_text(content)
                    
                    # Copy the original spec file
                    spec_path = output_dir / "game_spec.toml"
                    import shutil
                    shutil.copy(
                        self.specs_dir / f"{spec_name}.toml",
                        spec_path
                    )
                    
                    manifest["games"][game_key] = {
                        "title": game_spec.title,
                        "engine": game_spec.engine,
                        "path": str(output_dir),
                        "type": game_spec.type,
                        "spec_file": f"{spec_name}.toml",
                        "generated": True
                    }
                    
                    print(f"    ✅ {game_spec.title} generated successfully!")
                    
                except Exception as e:
                    print(f"    ❌ Error generating {game_spec.title}: {e}")
                    manifest["games"][game_key] = {
                        "title": game_spec.title,
                        "engine": game_spec.engine,
                        "error": str(e),
                        "generated": False
                    }
            else:
                print(f"  ✓ {game_spec.title} already exists")
                
    async def _generate_server_assets(self, manifest: Dict[str, Any], assets_spec: Dict[str, Any]):
        """Generate platform-wide server assets."""
        print("🎨 Generating server assets...")
        
        # Get asset registry
        registry = get_asset_registry()
        
        # Generate UI sprites
        if "sprites" in assets_spec.get("generated", {}):
            for category, items_data in assets_spec["generated"]["sprites"].items():
                sprite_dir = self.assets_dir / "sprites" / category
                sprite_dir.mkdir(parents=True, exist_ok=True)
                
                for item_spec in items_data.get("items", []):
                    name = item_spec["name"]
                    asset_key = f"server_sprite_{category}_{name}"
                    
                    if asset_key not in manifest.get("assets", {}):
                        print(f"  Creating server sprite: {category}/{name}")
                        
                        result = await generate_game_sprite(
                            name=name,
                            description=f"{name} for platform UI",
                            style=item_spec.get("style", "cyberpunk"),
                            save_path=str(sprite_dir / f"{name}.png")
                        )
                        
                        # Register in asset registry
                        asset_path = f"/public/static/assets/generated/sprites/{category}/{name}.png"
                        registry.register_asset(
                            name=name,
                            path=asset_path,
                            asset_type="sprites",
                            category=category,
                            generated=True,
                            metadata={"platform_asset": True}
                        )
                        
                        manifest["assets"][asset_key] = {
                            "type": "sprite",
                            "category": category,
                            "name": name,
                            "path": str(sprite_dir / f"{name}.png"),
                            "generated": True,
                            "platform_asset": True
                        }
        
        # Generate platform sounds
        if "audio" in assets_spec.get("generated", {}):
            for category, sounds_data in assets_spec["generated"]["audio"].items():
                audio_dir = self.assets_dir / "audio" / category
                audio_dir.mkdir(parents=True, exist_ok=True)
                
                for sound_spec in sounds_data.get("sounds", []):
                    name = sound_spec["name"]
                    asset_key = f"server_audio_{category}_{name}"
                    
                    if asset_key not in manifest.get("assets", {}):
                        print(f"  Creating server sound: {category}/{name}")
                        
                        result = await generate_sound_effect(
                            effect_name=name,
                            style=sound_spec.get("style", "digital"),
                            save_path=str(audio_dir / f"{name}.wav")
                        )
                        
                        # Register in asset registry
                        asset_path = f"/public/static/assets/generated/audio/{category}/{name}.wav"
                        registry.register_asset(
                            name=name,
                            path=asset_path,
                            asset_type="audio",
                            category=category,
                            generated=True,
                            metadata={"platform_asset": True}
                        )
                        
                        manifest["assets"][asset_key] = {
                            "type": "audio",
                            "category": category,
                            "name": name,
                            "path": str(audio_dir / f"{name}.wav"),
                            "generated": True,
                            "platform_asset": True
                        }
    
    async def _generate_3d_models_for_game(self, manifest: Dict[str, Any], game_spec):
        """Generate 3D models for games that need them."""
        print("🎨 Generating 3D models...")
        
        # Get asset registry
        registry = get_asset_registry()
        
        models_dir = self.assets_dir / "models"
        models_dir.mkdir(parents=True, exist_ok=True)
        
        for model_name, model_info in game_spec.assets.get("model_specs", {}).items():
            asset_key = f"3d_model_{model_name}"
            
            if asset_key not in manifest.get("assets", {}):
                print(f"  Creating 3D model: {model_name}")
                
                try:
                    result = await generate_game_3d_asset(
                        asset_type="prop",  # Default type
                        name=model_name,
                        style=model_info.get("style", "stylized"),
                        save_path=str(models_dir / f"{model_name}.glb")
                    )
                    
                    if result['success']:
                        # Register in asset registry
                        asset_path = f"/public/static/assets/generated/models/{model_name}.glb"
                        registry.register_asset(
                            name=model_name,
                            path=asset_path,
                            asset_type="models",
                            category="3d",
                            generated=True,
                            metadata={
                                "vertices": result.get("vertices"),
                                "faces": result.get("faces"),
                                "engine": game_spec.engine
                            }
                        )
                        
                        manifest["assets"][asset_key] = {
                            "type": "3d_model",
                            "name": model_name,
                            "path": str(models_dir / f"{model_name}.glb"),
                            "generated": True,
                            "vertices": result.get("vertices"),
                            "faces": result.get("faces")
                        }
                    else:
                        print(f"    ⚠️  Failed to generate 3D model {model_name}: {result.get('error')}")
                        
                except Exception as e:
                    print(f"    ❌ Error generating 3D model {model_name}: {e}")


async def run_startup_generation():
    """Run the startup generation process."""
    generator = StartupGenerator()
    await generator.generate_all()


if __name__ == "__main__":
    # Test the startup generation
    asyncio.run(run_startup_generation())
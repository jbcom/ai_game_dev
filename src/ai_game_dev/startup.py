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
from ai_game_dev.graphics import generate_game_sprite, generate_ui_pack
from ai_game_dev.audio import generate_sound_effect, generate_background_music
from ai_game_dev.constants import GENERATED_ASSETS_DIR, GENERATED_GAMES_DIR, PLATFORM_SPEC_PATH, ASSETS_DIR
from ai_game_dev.text import get_rpg_specification


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
        "game_elements": ["collectible_gem", "enemy_slime", "platform_tile", "powerup_star"],
        "weapons": ["laser_beam", "plasma_sword", "shield_bubble"],
        "effects": ["explosion", "sparkle", "damage_flash"]
    },
    "audio": {
        "gameplay": ["jump", "collect", "damage", "levelup"],
        "combat": ["shoot", "explosion", "shield_activate"]
    },
    "backgrounds": {
        "environments": ["cyberpunk_city", "digital_realm", "academy_classroom", "boss_arena"]
    }
}


class StartupGenerator:
    """Handles idempotent generation of example games and assets."""
    
    def __init__(self):
        self.assets_dir = Path(GENERATED_ASSETS_DIR)
        self.games_dir = Path(GENERATED_GAMES_DIR)
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
        
        # Generate example games
        await self._generate_example_games(manifest)
        
        # Generate the educational RPG from spec
        await self._generate_educational_rpg(manifest)
        
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
                    
                    manifest["assets"][asset_key] = {
                        "type": "audio",
                        "category": category,
                        "name": sound,
                        "path": result.path if hasattr(result, 'path') else str(audio_dir / f"{sound}.wav"),
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
                    
                    manifest["assets"][asset_key] = {
                        "type": "background",
                        "category": category,
                        "name": item,
                        "path": str(bg_dir / f"{item}.png"),
                        "generated": True
                    }
                    
    async def _generate_example_games(self, manifest: Dict[str, Any]):
        """Generate example games for each engine."""
        print("🎮 Generating example games...")
        
        for game_id, spec in EXAMPLE_GAMES.items():
            if game_id not in manifest.get("games", {}):
                print(f"\n  Creating {spec['title']} ({spec['engine']})...")
                
                try:
                    if spec.get("educational"):
                        # Generate educational game
                        project = await create_educational_game(
                            topic="Programming Fundamentals",
                            concepts=spec.get("concepts", ["variables", "loops"]),
                            level="beginner"
                        )
                    else:
                        # Generate regular game
                        project = await create_game(
                            description=spec["description"],
                            engine=spec["engine"]
                        )
                    
                    # Save project info
                    game_dir = self.games_dir / game_id
                    game_dir.mkdir(exist_ok=True)
                    
                    # Write game files
                    for filename, content in project.code_files.items():
                        (game_dir / filename).write_text(content)
                    
                    # Write game spec
                    spec_path = game_dir / "game_spec.json"
                    spec_path.write_text(json.dumps({
                        **spec,
                        "generated_at": str(asyncio.get_event_loop().time())
                    }, indent=2))
                    
                    manifest["games"][game_id] = {
                        "title": spec["title"],
                        "engine": spec["engine"],
                        "path": str(game_dir),
                        "generated": True
                    }
                    
                    print(f"    ✅ {spec['title']} generated successfully!")
                    
                except Exception as e:
                    print(f"    ❌ Error generating {spec['title']}: {e}")
                    manifest["games"][game_id] = {
                        "title": spec["title"],
                        "engine": spec["engine"],
                        "error": str(e),
                        "generated": False
                    }
            else:
                print(f"  ✓ {spec['title']} already exists")
                
    async def _generate_educational_rpg(self, manifest: Dict[str, Any]):
        """Generate the full educational RPG from specification."""
        print("🎓 Generating NeoTokyo Code Academy RPG...")
        
        rpg_key = "educational_rpg_full"
        if rpg_key not in manifest.get("games", {}):
            try:
                # Get the full RPG specification
                rpg_spec = get_rpg_specification()
                
                # Generate the complete educational RPG
                project = await create_educational_game(
                    topic="Programming through Cyberpunk Adventure",
                    concepts=["variables", "loops", "functions", "classes", "algorithms"],
                    level="progressive"  # Adapts from beginner to advanced
                )
                
                # Save to special directory
                rpg_dir = self.games_dir / "neotokyo_code_academy"
                rpg_dir.mkdir(exist_ok=True)
                
                # Write all game files
                for filename, content in project.code_files.items():
                    (rpg_dir / filename).write_text(content)
                
                # Save the full RPG specification
                spec_path = rpg_dir / "full_game_spec.json"
                spec_path.write_text(json.dumps(rpg_spec, indent=2))
                
                manifest["games"][rpg_key] = {
                    "title": "NeoTokyo Code Academy: The Binary Rebellion",
                    "engine": "pygame",
                    "path": str(rpg_dir),
                    "type": "educational_rpg",
                    "generated": True
                }
                
                print("    ✅ Educational RPG generated successfully!")
                
            except Exception as e:
                print(f"    ❌ Error generating RPG: {e}")
                manifest["games"][rpg_key] = {
                    "title": "NeoTokyo Code Academy",
                    "error": str(e),
                    "generated": False
                }
        else:
            print("  ✓ Educational RPG already exists")


async def run_startup_generation():
    """Run the startup generation process."""
    generator = StartupGenerator()
    await generator.generate_all()


if __name__ == "__main__":
    # Test the startup generation
    asyncio.run(run_startup_generation())
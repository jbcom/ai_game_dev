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
from ai_game_dev.constants import GENERATED_ASSETS_DIR, GENERATED_GAMES_DIR, PLATFORM_SPEC_PATH
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

# Common UI assets needed for all games
UI_ASSETS = {
    "buttons": ["play", "pause", "menu", "quit", "restart"],
    "panels": ["dialog", "inventory", "settings", "score"],
    "icons": ["health", "mana", "coin", "star", "key"]
}

# Common sound effects
SOUND_EFFECTS = {
    "ui": ["click", "hover", "confirm", "cancel"],
    "gameplay": ["jump", "collect", "hit", "powerup", "gameover"],
    "combat": ["shoot", "explosion", "shield", "damage"]
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
        """Generate common UI assets and sounds."""
        print("🎨 Generating common assets...")
        
        # UI Elements
        ui_dir = self.assets_dir / "ui"
        ui_dir.mkdir(exist_ok=True)
        
        for category, items in UI_ASSETS.items():
            for item in items:
                asset_key = f"ui_{category}_{item}"
                
                if asset_key not in manifest.get("assets", {}):
                    print(f"  Creating {category}: {item}")
                    
                    if category in ["buttons", "panels"]:
                        # Generate UI element
                        result = await generate_ui_pack(
                            theme="cyberpunk",
                            style="modern",
                            save_dir=str(ui_dir / category)
                        )
                        manifest["assets"][asset_key] = {
                            "type": category,
                            "name": item,
                            "path": str(ui_dir / category),
                            "generated": True
                        }
                        
        # Sound Effects
        audio_dir = self.assets_dir / "audio"
        audio_dir.mkdir(exist_ok=True)
        
        for category, sounds in SOUND_EFFECTS.items():
            for sound in sounds:
                asset_key = f"audio_{category}_{sound}"
                
                if asset_key not in manifest.get("assets", {}):
                    print(f"  Creating sound: {sound}")
                    
                    result = await generate_sound_effect(
                        effect_name=sound,
                        style="retro",
                        save_path=str(audio_dir / f"{sound}.wav")
                    )
                    
                    manifest["assets"][asset_key] = {
                        "type": "sound",
                        "category": category,
                        "name": sound,
                        "path": result.path if hasattr(result, 'path') else str(audio_dir / f"{sound}.wav"),
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
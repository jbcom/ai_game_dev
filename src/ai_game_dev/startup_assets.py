"""
Startup asset generation system
Ensures all required internal assets are generated idempotently on server start
"""
import asyncio
import json
from pathlib import Path
from typing import Dict, List, Any
import hashlib

from ai_game_dev.agents.subgraphs import GraphicsSubgraph, AudioSubgraph
from ai_game_dev.agents.arcade_academy_agent import ArcadeAcademyAgent
from ai_game_dev.variants import InteractiveVariantSystem
from ai_game_dev.game_specification import GameSpecificationParser


class StartupAssetGenerator:
    """Handles idempotent generation of all required assets on startup."""
    
    def __init__(self):
        self.assets_dir = Path("public/static/assets")
        self.generated_dir = Path("generated_assets")
        self.examples_dir = Path("generated_examples")
        self.manifest_file = Path("data/asset_manifest.json")
        
        # Ensure directories exist
        self.assets_dir.mkdir(parents=True, exist_ok=True)
        self.generated_dir.mkdir(parents=True, exist_ok=True)
        self.examples_dir.mkdir(parents=True, exist_ok=True)
        Path("data").mkdir(exist_ok=True)
        
        # Load or create manifest
        self.manifest = self._load_manifest()
        
        # Initialize subgraphs
        self.graphics_subgraph = None
        self.audio_subgraph = None
        self.arcade_agent = None
        self.variant_system = None
    
    def _load_manifest(self) -> Dict[str, Any]:
        """Load asset generation manifest for idempotency."""
        if self.manifest_file.exists():
            with open(self.manifest_file, 'r') as f:
                return json.load(f)
        return {
            "version": "1.0",
            "generated_assets": {},
            "generated_examples": {}
        }
    
    def _save_manifest(self):
        """Save manifest to track what's been generated."""
        with open(self.manifest_file, 'w') as f:
            json.dump(self.manifest, f, indent=2)
    
    def _get_asset_hash(self, spec: Dict[str, Any]) -> str:
        """Generate hash for asset specification."""
        spec_str = json.dumps(spec, sort_keys=True)
        return hashlib.md5(spec_str.encode()).hexdigest()
    
    async def initialize(self):
        """Initialize all subgraphs and agents."""
        print("🔧 Initializing asset generation systems...")
        
        self.graphics_subgraph = GraphicsSubgraph()
        self.audio_subgraph = AudioSubgraph()
        self.arcade_agent = ArcadeAcademyAgent()
        self.variant_system = InteractiveVariantSystem()
        
        await self.graphics_subgraph.initialize()
        await self.audio_subgraph.initialize()
        await self.arcade_agent.initialize()
        
        print("✅ Asset generation systems initialized")
    
    async def generate_all_assets(self):
        """Generate all required assets idempotently."""
        print("🎨 Starting comprehensive asset generation...")
        
        # 1. Core UI Assets
        await self._generate_ui_assets()
        
        # 2. Character Assets
        await self._generate_character_assets()
        
        # 3. Game Icons and Logos
        await self._generate_game_icons()
        
        # 4. Audio Assets
        await self._generate_audio_assets()
        
        # 5. Arcade Academy RPG Assets
        await self._generate_academy_game_assets()
        
        # 6. Example Games with Variants
        await self._generate_example_games()
        
        # Save manifest
        self._save_manifest()
        
        print("✅ All asset generation complete!")
    
    async def _generate_ui_assets(self):
        """Generate UI components and frames."""
        ui_assets = [
            {
                "name": "tech-frame",
                "type": "ui_frame",
                "description": "Cyberpunk tech frame with circuit patterns and neon glow",
                "style": "cyberpunk",
                "variants": ["basic", "with_lightning", "with_circuit_pattern"]
            },
            {
                "name": "glass-panel",
                "type": "ui_panel",
                "description": "Frosted glass panel with subtle glow",
                "style": "glassmorphism"
            },
            {
                "name": "audio-controls",
                "type": "ui_controls",
                "description": "Futuristic audio player controls",
                "style": "neon_cyberpunk",
                "components": ["play", "pause", "stop", "volume_slider"]
            }
        ]
        
        for asset_spec in ui_assets:
            await self._generate_asset_if_needed(asset_spec, "ui")
    
    async def _generate_character_assets(self):
        """Generate character sprites and avatars."""
        characters = [
            {
                "name": "professor-pixel",
                "type": "character",
                "description": "Wise AI professor with pixelated aesthetic, cyberpunk teacher outfit",
                "style": "pixel_art_cyberpunk",
                "variants": ["idle", "teaching", "excited", "thinking"]
            },
            {
                "name": "ai-orb",
                "type": "mascot",
                "description": "Floating AI orb assistant with holographic effects",
                "style": "futuristic_hologram"
            }
        ]
        
        for char_spec in characters:
            await self._generate_asset_if_needed(char_spec, "characters")
    
    async def _generate_game_icons(self):
        """Generate game engine icons and logos."""
        icons = [
            {
                "name": "pygame-icon",
                "type": "engine_icon",
                "description": "Python snake forming a game controller",
                "style": "modern_flat"
            },
            {
                "name": "godot-icon", 
                "type": "engine_icon",
                "description": "Godot robot mascot in cyberpunk style",
                "style": "cyberpunk"
            },
            {
                "name": "bevy-icon",
                "type": "engine_icon", 
                "description": "Hexagonal bee with rust-colored circuit patterns",
                "style": "technical"
            }
        ]
        
        for icon_spec in icons:
            await self._generate_asset_if_needed(icon_spec, "icons")
    
    async def _generate_audio_assets(self):
        """Generate sound effects and music."""
        audio_assets = [
            {
                "name": "button_click_futuristic",
                "type": "sound_effect",
                "description": "Futuristic button click with digital beep",
                "duration": 0.2
            },
            {
                "name": "hover_beep_cyberpunk",
                "type": "sound_effect",
                "description": "Subtle cyberpunk hover sound",
                "duration": 0.1
            },
            {
                "name": "success_ding_pleasant",
                "type": "sound_effect",
                "description": "Pleasant success chime",
                "duration": 0.5
            },
            {
                "name": "arcade_academy_theme",
                "type": "music",
                "description": "Chiptune educational theme music",
                "duration": 120,
                "loop": True
            }
        ]
        
        for audio_spec in audio_assets:
            await self._generate_audio_if_needed(audio_spec)
    
    async def _generate_academy_game_assets(self):
        """Generate all assets for the Arcade Academy RPG."""
        print("🎓 Generating Arcade Academy RPG assets...")
        
        # Get the full game specification
        academy_spec = {
            "title": "NeoTokyo Code Academy: The Binary Rebellion",
            "type": "educational_rpg",
            "description": "Learn programming through an epic cyberpunk adventure",
            "assets_needed": [
                # Environments
                {
                    "name": "academy_entrance",
                    "type": "environment",
                    "description": "Futuristic academy entrance with holographic displays"
                },
                {
                    "name": "code_classroom",
                    "type": "environment",
                    "description": "High-tech classroom with floating code displays"
                },
                {
                    "name": "binary_dungeon",
                    "type": "environment",
                    "description": "Digital dungeon made of binary code"
                },
                # Characters
                {
                    "name": "student_avatar",
                    "type": "character_sprite",
                    "description": "Customizable student character in cyberpunk attire"
                },
                {
                    "name": "code_enemies",
                    "type": "enemy_sprites",
                    "description": "Bug enemies, syntax errors as creatures"
                },
                # UI Elements
                {
                    "name": "dialogue_box",
                    "type": "ui_element",
                    "description": "Futuristic dialogue interface"
                },
                {
                    "name": "code_editor_ui",
                    "type": "ui_element",
                    "description": "In-game code editor with syntax highlighting"
                }
            ]
        }
        
        # Generate each asset
        for asset in academy_spec["assets_needed"]:
            asset["game"] = "arcade_academy"
            await self._generate_asset_if_needed(asset, f"academy/{asset['type']}")
        
        # Generate the game code itself
        await self._generate_academy_game_code()
    
    async def _generate_academy_game_code(self):
        """Generate the actual Academy game code."""
        output_path = self.examples_dir / "arcade_academy_rpg"
        
        if not output_path.exists():
            print("📝 Generating Arcade Academy game code...")
            
            # Use arcade agent to generate the full game
            result = await self.arcade_agent.generate_educational_game({
                "title": "NeoTokyo Code Academy",
                "lessons": ["variables", "loops", "conditionals", "functions"],
                "game_type": "rpg_adventure"
            })
            
            # Save the generated code
            output_path.mkdir(parents=True, exist_ok=True)
            
            # Main game file
            main_file = output_path / "main.py"
            main_file.write_text(result.get("main_code", ""))
            
            # Game modules
            for module_name, module_code in result.get("modules", {}).items():
                module_file = output_path / f"{module_name}.py"
                module_file.write_text(module_code)
            
            print(f"✅ Academy game code generated at {output_path}")
    
    async def _generate_example_games(self):
        """Generate example games with variants."""
        print("🎮 Generating example games with variants...")
        
        example_games = [
            {
                "name": "space_shooter",
                "description": "Classic space shooter with power-ups",
                "engine": "pygame",
                "variants": {
                    "enemy_patterns": ["waves", "random"],
                    "weapon_system": ["single_shot", "spread_shot"],
                    "difficulty": ["casual", "hardcore"]
                }
            },
            {
                "name": "puzzle_platformer",
                "description": "Puzzle platformer with physics",
                "engine": "godot",
                "variants": {
                    "movement": ["grid_based", "free_movement"],
                    "puzzle_type": ["sokoban", "switches"],
                    "art_style": ["pixel", "vector"]
                }
            },
            {
                "name": "tower_defense",
                "description": "Strategic tower defense game",
                "engine": "bevy",
                "variants": {
                    "grid_type": ["hexagonal", "square"],
                    "economy": ["fixed_income", "interest_based"],
                    "tower_targeting": ["nearest", "strongest", "random"]
                }
            }
        ]
        
        for game_spec in example_games:
            await self._generate_game_with_variants(game_spec)
    
    async def _generate_game_with_variants(self, game_spec: Dict[str, Any]):
        """Generate a game with all its variants."""
        game_name = game_spec["name"]
        output_dir = self.examples_dir / game_name
        
        # Check if already generated
        spec_hash = self._get_asset_hash(game_spec)
        if self.manifest["generated_examples"].get(game_name) == spec_hash:
            print(f"✓ {game_name} already generated")
            return
        
        print(f"🎯 Generating {game_name} with variants...")
        
        # Generate base game
        base_code = await self._generate_base_game_code(game_spec)
        
        # Generate variants using variant system
        variants = await self.variant_system.generate_variants(
            base_code=base_code,
            variant_specs=game_spec["variants"],
            engine=game_spec["engine"]
        )
        
        # Save everything
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Base game
        (output_dir / "main.py").write_text(base_code)
        
        # Features configuration
        features_toml = self.variant_system.generate_features_toml(game_spec["variants"])
        (output_dir / "features.toml").write_text(features_toml)
        
        # Variant implementations
        for variant_name, variant_code in variants.items():
            variant_file = output_dir / f"variants/{variant_name}.py"
            variant_file.parent.mkdir(exist_ok=True)
            variant_file.write_text(variant_code)
        
        # Update manifest
        self.manifest["generated_examples"][game_name] = spec_hash
        
        print(f"✅ {game_name} generated with {len(variants)} variants")
    
    async def _generate_base_game_code(self, game_spec: Dict[str, Any]) -> str:
        """Generate base game code for a specification."""
        # This would use the appropriate engine agent
        # For now, return a template
        return f"""
# {game_spec['name']} - {game_spec['description']}
# Engine: {game_spec['engine']}
# Auto-generated with variant support

import {game_spec['engine']}
from variants import load_variant_config

# Load feature flags
config = load_variant_config('features.toml')

class {game_spec['name'].title().replace('_', '')}Game:
    def __init__(self):
        self.config = config
        # Initialize based on variants
        
    def run(self):
        # Main game loop
        pass

if __name__ == "__main__":
    game = {game_spec['name'].title().replace('_', '')}Game()
    game.run()
"""
    
    async def _generate_asset_if_needed(self, asset_spec: Dict[str, Any], category: str):
        """Generate an asset if it hasn't been generated yet."""
        asset_name = asset_spec["name"]
        asset_path = self.assets_dir / category / f"{asset_name}.png"
        
        # Check if already generated
        spec_hash = self._get_asset_hash(asset_spec)
        manifest_key = f"{category}/{asset_name}"
        
        if self.manifest["generated_assets"].get(manifest_key) == spec_hash and asset_path.exists():
            print(f"✓ {asset_name} already exists")
            return
        
        print(f"🎨 Generating {asset_name}...")
        
        # Ensure directory exists
        asset_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Generate using graphics subgraph
        result = await self.graphics_subgraph.process({
            "task": "generate_asset",
            "asset_type": asset_spec["type"],
            "description": asset_spec["description"],
            "style": asset_spec.get("style", "modern"),
            "output_path": str(asset_path)
        })
        
        # Generate variants if specified
        if "variants" in asset_spec:
            for variant in asset_spec["variants"]:
                variant_path = asset_path.parent / f"{asset_name}_{variant}.png"
                await self.graphics_subgraph.process({
                    "task": "generate_asset",
                    "asset_type": asset_spec["type"],
                    "description": f"{asset_spec['description']} - {variant} variant",
                    "style": asset_spec.get("style", "modern"),
                    "output_path": str(variant_path)
                })
        
        # Update manifest
        self.manifest["generated_assets"][manifest_key] = spec_hash
        
        print(f"✅ {asset_name} generated")
    
    async def _generate_audio_if_needed(self, audio_spec: Dict[str, Any]):
        """Generate audio asset if needed."""
        audio_name = audio_spec["name"]
        audio_path = self.assets_dir / "audio" / f"{audio_name}.wav"
        
        # Check if already generated
        spec_hash = self._get_asset_hash(audio_spec)
        manifest_key = f"audio/{audio_name}"
        
        if self.manifest["generated_assets"].get(manifest_key) == spec_hash and audio_path.exists():
            print(f"✓ {audio_name} already exists")
            return
        
        print(f"🎵 Generating {audio_name}...")
        
        # Ensure directory exists
        audio_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Generate using audio subgraph
        result = await self.audio_subgraph.process({
            "task": "generate_audio",
            "audio_type": audio_spec["type"],
            "description": audio_spec["description"],
            "duration": audio_spec.get("duration", 1.0),
            "output_path": str(audio_path)
        })
        
        # Update manifest
        self.manifest["generated_assets"][manifest_key] = spec_hash
        
        print(f"✅ {audio_name} generated")


async def run_startup_generation():
    """Run the startup asset generation process."""
    generator = StartupAssetGenerator()
    await generator.initialize()
    await generator.generate_all_assets()
    print("🎉 All startup assets generated successfully!")


if __name__ == "__main__":
    # Can be run standalone for testing
    asyncio.run(run_startup_generation())
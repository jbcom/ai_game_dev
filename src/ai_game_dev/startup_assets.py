"""
Startup asset generation system
Ensures all required internal assets are generated idempotently on server start
"""
import asyncio
import hashlib
import json
from pathlib import Path
from typing import Any

import toml

from ai_game_dev.agents.arcade_academy_agent import ArcadeAcademyAgent
from ai_game_dev.agents.subgraphs import AudioSubgraph, GraphicsSubgraph


class StartupAssetGenerator:
    """Handles idempotent generation of all required assets on startup."""
    
    def __init__(self):
        self.workspace_root = self._find_workspace_root()
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
    
    def _find_workspace_root(self) -> Path:
        """Find the workspace root directory."""
        # Look for pyproject.toml to identify root
        current = Path.cwd()
        while current != current.parent:
            if (current / "pyproject.toml").exists():
                return current
            current = current.parent
        return Path.cwd()  # Fallback to current directory
    
    def _load_manifest(self) -> dict[str, Any]:
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
    
    def _get_asset_hash(self, spec: dict[str, Any]) -> str:
        """Generate hash for asset specification."""
        spec_str = json.dumps(spec, sort_keys=True)
        return hashlib.md5(spec_str.encode()).hexdigest()
    
    async def initialize(self):
        """Initialize all subgraphs and agents."""
        print("🔧 Initializing asset generation systems...")
        
        self.graphics_subgraph = GraphicsSubgraph()
        self.audio_subgraph = AudioSubgraph()
        self.arcade_agent = ArcadeAcademyAgent()
        self.variant_system = None  # Will be initialized if needed
        
        await self.graphics_subgraph.initialize()
        await self.audio_subgraph.initialize()
        await self.arcade_agent.initialize()
        
        print("✅ Asset generation systems initialized")
    
    async def generate_all_assets(self):
        """Generate all required assets idempotently."""
        print("🎨 Starting comprehensive asset generation...")
        
        # Load the unified platform specification
        unified_spec_path = self.workspace_root / "src/ai_game_dev/specs/unified_platform_spec.toml"
        with open(unified_spec_path, 'r') as f:
            unified_spec = toml.load(f)
        
        # 1. Generate platform UI and branding assets
        await self._generate_platform_assets_from_unified(unified_spec)
        
        # 2. Generate platform audio assets
        await self._generate_platform_audio_from_unified(unified_spec)
        
        # 3. Generate the complete Academy RPG using the unified spec
        await self._generate_academy_rpg_from_unified(unified_spec)
        
        # 4. Generate example games with variants
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
    
    async def _generate_platform_assets_from_unified(self, unified_spec: dict[str, Any]):
        """Generate all platform visual assets from unified specification."""
        print("🎨 Generating platform visual assets...")
        
        platform_assets = unified_spec.get("platform_assets", {})
        
        for category_name, category_data in platform_assets.items():
            if category_name in ["ui", "characters", "environments"]:
                prompts = category_data.get("prompts", [])
                size = category_data.get("size", "512x512")
                quality = category_data.get("quality", "hd")
                category_path = category_data.get("category", category_name)
                
                print(f"📦 Processing {category_name} ({len(prompts)} assets)...")
                
                for i, prompt in enumerate(prompts):
                    asset_name = f"{category_name}_{i}"
                    output_path = self.assets_dir / category_path / f"{asset_name}.png"
                    
                    # Generate hash for idempotency
                    spec_hash = self._get_asset_hash({
                        "prompt": prompt,
                        "size": size,
                        "quality": quality
                    })
                    
                    manifest_key = f"{category_path}/{asset_name}"
                    
                    # Check if already generated
                    if self.manifest["generated_assets"].get(manifest_key) == spec_hash and output_path.exists():
                        print(f"  ✓ {asset_name} already exists")
                        continue
                    
                    print(f"  🎨 Generating {asset_name}...")
                    
                    # Ensure directory exists
                    output_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Generate using graphics subgraph
                    result = await self.graphics_subgraph.process({
                        "task": "generate_asset",
                        "prompt": prompt,
                        "size": size,
                        "quality": quality,
                        "output_path": str(output_path)
                    })
                    
                    # Update manifest
                    self.manifest["generated_assets"][manifest_key] = spec_hash
    
    async def _generate_platform_audio_from_unified(self, unified_spec: dict[str, Any]):
        """Generate all platform audio assets from unified specification."""
        print("🎵 Generating platform audio assets...")
        
        platform_audio = unified_spec.get("platform_audio", {})
        
        for category_name, category_data in platform_audio.items():
            if category_name in ["ui_sounds", "ambient"]:
                effects = category_data.get("effects", [])
                durations = category_data.get("duration_ms", [])
                format = category_data.get("format", "wav")
                
                print(f"🎵 Processing {category_name} ({len(effects)} sounds)...")
                
                for i, effect_name in enumerate(effects):
                    duration_ms = durations[i] if i < len(durations) else 1000
                    output_path = self.assets_dir / "audio" / f"{effect_name}.{format}"
                    
                    # Generate hash for idempotency
                    spec_hash = self._get_asset_hash({
                        "effect": effect_name,
                        "duration": duration_ms,
                        "format": format
                    })
                    
                    manifest_key = f"audio/{effect_name}"
                    
                    # Check if already generated
                    if self.manifest["generated_assets"].get(manifest_key) == spec_hash and output_path.exists():
                        print(f"  ✓ {effect_name} already exists")
                        continue
                    
                    print(f"  🎵 Generating {effect_name}...")
                    
                    # Ensure directory exists
                    output_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Generate using audio subgraph
                    result = await self.audio_subgraph.process({
                        "task": "generate_sound_effect",
                        "effect_name": effect_name,
                        "duration_ms": duration_ms,
                        "category": category_name,
                        "output_path": str(output_path)
                    })
                    
                    # Update manifest
                    self.manifest["generated_assets"][manifest_key] = spec_hash
    
    async def _generate_platform_audio(self, audio_spec: dict[str, Any]):
        """Generate all platform audio assets."""
        print("🎵 Generating platform audio assets...")
        
        # Process each audio category
        for category_name, category_data in audio_spec.items():
            if category_name == "generation_config":
                continue
                
            effects = category_data.get("effects", [])
            durations = category_data.get("duration_ms", [])
            format = category_data.get("format", "wav")
            
            for i, effect_name in enumerate(effects):
                duration_ms = durations[i] if i < len(durations) else 1000
                audio_path = self.assets_dir / "audio" / f"{effect_name}.{format}"
                
                # Check if already exists
                spec_hash = self._get_asset_hash({
                    "effect": effect_name, 
                    "duration": duration_ms,
                    "category": category_name
                })
                manifest_key = f"audio/{effect_name}"
                
                if self.manifest["generated_assets"].get(manifest_key) == spec_hash and audio_path.exists():
                    print(f"  ✓ {effect_name} already exists")
                    continue
                
                print(f"  🎵 Generating {effect_name}...")
                audio_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Generate using audio subgraph
                result = await self.audio_subgraph.process({
                    "task": "generate_sound_effect",
                    "effect_name": effect_name,
                    "duration_ms": duration_ms,
                    "category": category_name,
                    "output_path": str(audio_path)
                })
                
                # Update manifest
                self.manifest["generated_assets"][manifest_key] = spec_hash
    
    async def _generate_academy_rpg_from_unified(self, unified_spec: dict[str, Any]):
        """Generate the complete Academy RPG from unified specification."""
        print("🎓 Generating NeoTokyo Code Academy RPG from unified spec...")
        
        # Extract the RPG game specification
        rpg_spec = unified_spec.get("rpg_game", {})
        
        # Add metadata required by the workshop
        rpg_spec["title"] = rpg_spec.get("name", "NeoTokyo Code Academy")
        rpg_spec["features"] = rpg_spec.get("features", {}).get("main", [])
        
        # Use the academy subgraph which inherits from workshop
        from ai_game_dev.agents.subgraphs import ArcadeAcademySubgraph
        
        # Get paths from the RPG spec
        paths_config = rpg_spec.get("paths", {})
        code_base = Path(paths_config.get("code_base", "generated_games/academy"))
        project_name = paths_config.get("project_name", "neotokyo_code_academy")
        
        # Create full path (relative to workspace root)
        rpg_dir = self.workspace_root / code_base / project_name
        spec_hash = self._get_asset_hash(rpg_spec)
        
        if self.manifest["generated_examples"].get("academy_rpg_unified") == spec_hash and rpg_dir.exists():
            print("✓ NeoTokyo Academy RPG already generated")
            return
        
        print("📝 Generating complete RPG code and assets...")
        
        # Initialize and use the academy subgraph
        academy_subgraph = ArcadeAcademySubgraph()
        await academy_subgraph.initialize()
        
        # Process the RPG spec as an uploaded spec
        result = await academy_subgraph.process({
            "uploaded_spec": rpg_spec,
            "educational_mode": True
        })
        
        if result["success"]:
            # Extract generated code
            project_data = result["project"]
            rpg_dir.mkdir(parents=True, exist_ok=True)
            
            # Save all generated files
            for filename, content in project_data["code"].items():
                file_path = rpg_dir / filename
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_text(content)
            
            print(f"✅ RPG code saved to: {rpg_dir}")
            print(f"✅ Assets will be in: {paths_config.get('assets_base', '')}")
        else:
            print(f"❌ Failed to generate RPG: {result.get('errors', [])}")
            return
        
        # Update manifest
        self.manifest["generated_examples"]["academy_rpg_unified"] = spec_hash
        
        print("✅ NeoTokyo Academy RPG generated successfully!")
    
    async def _generate_academy_rpg_complete(self):
        """Generate the complete Arcade Academy RPG."""
        print("🎓 Generating NeoTokyo Code Academy RPG...")
        
        # Import the complete RPG specification
        from ai_game_dev.education.rpg_specification import RPG_GAME_SPEC
        from ai_game_dev.agents.subgraphs import ArcadeAcademySubgraph
        
        # Use the paths from the spec
        paths_config = RPG_GAME_SPEC.get("paths", {})
        code_base = Path(paths_config.get("code_base", "generated_games/academy"))
        project_name = paths_config.get("project_name", "neotokyo_code_academy")
        
        # Create full path (relative to workspace root)
        rpg_dir = self.workspace_root / code_base / project_name
        spec_hash = self._get_asset_hash(RPG_GAME_SPEC)
        
        if self.manifest["generated_examples"].get("neotokyo_academy_rpg") == spec_hash and rpg_dir.exists():
            print("✓ NeoTokyo Academy RPG already generated")
            return
        
        print("📝 Generating complete RPG code and assets...")
        
        # Initialize and use the academy subgraph
        academy_subgraph = ArcadeAcademySubgraph()
        await academy_subgraph.initialize()
        
        # Process the RPG spec
        result = await academy_subgraph.process_with_education({
            "uploaded_spec": RPG_GAME_SPEC,
            "educational_mode": True,
            "lesson_focus": "variables"  # Start with variables lesson
        })
        
        if result["success"]:
            # Extract generated code
            project_data = result["project"]
            rpg_dir.mkdir(parents=True, exist_ok=True)
            
            # Save all generated files
            for filename, content in project_data["code"].items():
                file_path = rpg_dir / filename
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_text(content)
            
            # Assets are generated separately by the workshop subgraph
            print(f"✅ Code saved to: {rpg_dir}")
        else:
            print(f"❌ Failed to generate RPG: {result.get('errors', [])}")
            return
        
        # Update manifest
        self.manifest["generated_examples"]["neotokyo_academy_rpg"] = spec_hash
        
        print("✅ NeoTokyo Academy RPG generated successfully!")
    
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
    
    async def _generate_game_with_variants(self, game_spec: dict[str, Any]):
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
    
    async def _generate_base_game_code(self, game_spec: dict[str, Any]) -> str:
        """Generate base game code for a specification."""
        # This would use the appropriate engine agent
        # For now, return a template
        return f"""
# {game_spec['name']} - {game_spec['description']}
# Engine: {game_spec['engine']}
# Auto-generated with variant support

import {game_spec['engine']}
        from ai_game_dev.tools.variants import load_variant_config

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
    
    async def _generate_asset_if_needed(self, asset_spec: dict[str, Any], category: str):
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
    
    async def _generate_audio_if_needed(self, audio_spec: dict[str, Any]):
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
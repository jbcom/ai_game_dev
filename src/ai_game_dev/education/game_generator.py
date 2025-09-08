"""
Pre-generate the complete NeoTokyo Code Academy RPG using our own AI tools
This makes us the first customer of our own game generation system
"""

import asyncio
import json
from pathlib import Path
from typing import Dict, Any

from ai_game_dev.engines import generate_for_engine
from ai_game_dev.project_manager import ProjectManager
from ai_game_dev.education.rpg_specification import RPG_GAME_SPEC
from ai_game_dev.education.characters_and_story import MAIN_STORYLINE, MAIN_CHARACTERS


async def generate_neotokyo_rpg() -> Dict[str, Any]:
    """
    Generate the complete NeoTokyo Code Academy RPG using our AI generation system.
    This serves as both the educational game and a showcase of our capabilities.
    """
    
    # Create comprehensive game description for AI generation
    game_description = f"""
    Create '{RPG_GAME_SPEC["name"]}' - {RPG_GAME_SPEC["description"]}
    
    SETTING: {MAIN_STORYLINE["setting"]}
    
    PREMISE: {MAIN_STORYLINE["premise"]}
    
    MAIN CHARACTER CLASSES:
    {json.dumps([cls for cls in RPG_GAME_SPEC["core_systems"]["character_classes"]], indent=2)}
    
    WORLD DESIGN:
    - Overworld: {RPG_GAME_SPEC["world_design"]["overworld_map"]["name"]}
    - Biomes: {', '.join(RPG_GAME_SPEC["world_design"]["overworld_map"]["biomes"])}
    - Key Locations: {', '.join(RPG_GAME_SPEC["world_design"]["overworld_map"]["landmarks"])}
    
    TECHNICAL REQUIREMENTS:
    - Engine: pygame (educational Python game development)
    - Combat: {RPG_GAME_SPEC["core_systems"]["combat_system"]["style"]}
    - Progression: Level 1-{RPG_GAME_SPEC["core_systems"]["leveling_system"]["max_level"]}
    - View: {RPG_GAME_SPEC["view_perspective"]}
    - Art Style: {RPG_GAME_SPEC["art_style"]}
    
    EDUCATIONAL INTEGRATION:
    This game must demonstrate every Python concept students will learn:
    {json.dumps(RPG_GAME_SPEC["educational_objectives"]["python_concepts"], indent=2)}
    
    The generated code should be production-quality, well-documented, and serve as
    the perfect example for students learning game development with Python.
    """
    
    print("🎮 Generating NeoTokyo Code Academy RPG...")
    print("📝 Using our own AI tools to create the educational game")
    
    try:
        # Generate the complete game using our engine
        result = await generate_for_engine(
            engine_name="pygame",
            description=game_description,
            complexity="advanced",
            features=[
                "turn_based_combat",
                "character_progression", 
                "inventory_system",
                "dialogue_system",
                "procedural_dungeons",
                "party_management",
                "save_system",
                "educational_integration"
            ],
            art_style="16-bit cyberpunk pixel art"
        )
        
        print("✅ Game generation complete!")
        print(f"📁 Generated {len(result.generated_files)} files")
        print(f"🎯 Engine: {result.engine_type}")
        
        # Save the generated game for educational use
        education_dir = Path(__file__).parent / "generated_game"
        education_dir.mkdir(exist_ok=True)
        
        # Write the generated files
        for filename, content in result.generated_files.items():
            file_path = education_dir / filename
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content)
        
        # Create educational metadata
        metadata = {
            "game_info": RPG_GAME_SPEC,
            "storyline": MAIN_STORYLINE,
            "characters": MAIN_CHARACTERS,
            "generation_result": {
                "engine": result.engine_type,
                "files": list(result.generated_files.keys()),
                "build_instructions": result.build_instructions,
                "asset_requirements": result.asset_requirements
            }
        }
        
        metadata_file = education_dir / "educational_metadata.json"
        metadata_file.write_text(json.dumps(metadata, indent=2, default=str))
        
        return {
            "success": True,
            "game_path": str(education_dir),
            "files_generated": len(result.generated_files),
            "educational_ready": True
        }
        
    except Exception as e:
        print(f"❌ Game generation failed: {e}")
        return {
            "success": False,
            "error": str(e)
        }


async def setup_educational_assets():
    """Generate all cyberpunk assets needed for the educational RPG."""
    from ai_game_dev.tools.openai_tools import (
        generate_character_sprite,
        generate_environment,
        generate_ui_element,
        generate_sound_effect,
        generate_music
    )
    
    print("🎨 Generating cyberpunk educational assets...")
    
    assets = {}
    
    # Character sprites for all classes
    for class_name in ["Code Knight", "Data Sage", "Bug Hunter", "Web Weaver"]:
        sprite = await generate_character_sprite(
            character_name=class_name,
            character_description=f"Cyberpunk {class_name} with neon accents",
            art_style="cyberpunk pixel art",
            save_path=f"assets/characters/{class_name.lower().replace(' ', '_')}.png"
        )
        assets[f"{class_name}_sprite"] = sprite
    
    # Professor Pixel
    professor = await generate_character_sprite(
        character_name="Professor Pixel",
        character_description="Friendly AI hologram teacher with glowing circuits",
        art_style="cyberpunk pixel art",
        save_path="assets/characters/professor_pixel.png"
    )
    assets["professor_pixel"] = professor
    
    # Neo-Tokyo environments
    for env_name in ["Academy Exterior", "Underground Lab", "Algorithm Tower"]:
        env = await generate_environment(
            environment_name=env_name,
            description=f"Cyberpunk {env_name} with neon lights and holograms",
            time_of_day="night",
            art_style="cyberpunk pixel art",
            save_path=f"assets/environments/{env_name.lower().replace(' ', '_')}.png"
        )
        assets[f"{env_name}_bg"] = env
    
    # UI elements
    for ui_type in ["dialog_box", "health_bar", "menu"]:
        ui = await generate_ui_element(
            element_type=ui_type,
            theme="cyberpunk",
            description="Neon glowing with circuit patterns",
            save_path=f"assets/ui/{ui_type}.png"
        )
        assets[f"{ui_type}_ui"] = ui
    
    # Sound effects
    sfx_list = ["laser_shot", "level_up", "menu_select", "dialogue_beep"]
    for sfx in sfx_list:
        sound = await generate_sound_effect(
            sound_type=sfx.replace('_', ' '),
            style="electronic cyberpunk",
            duration=1,
            save_path=f"assets/sfx/{sfx}.wav"
        )
        assets[f"{sfx}_sound"] = sound
    
    # Background music
    music = await generate_music(
        description="Cyberpunk educational theme with synth and electronic beats",
        style="synthwave",
        duration=180,
        save_path="assets/music/main_theme.mp3"
    )
    assets["main_theme"] = music
    
    return {"assets_generated": True, "assets": assets}


if __name__ == "__main__":
    async def main():
        result = await generate_neotokyo_rpg()
        asset_result = await setup_educational_assets()
        
        print("\n🎓 NeoTokyo Code Academy RPG Generation Complete!")
        print(f"✅ Game Ready: {result.get('success', False)}")
        print(f"📁 Files: {result.get('files_generated', 0)}")
        print(f"🎨 Assets: {asset_result.get('assets_generated', False)}")
        
        if result.get("success"):
            print(f"🎮 Game available at: {result['game_path']}")
            print("🎓 Ready for educational use!")
    
    asyncio.run(main())
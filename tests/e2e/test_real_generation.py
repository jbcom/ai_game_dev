"""Working E2E tests that actually generate games."""
import pytest
import os
from pathlib import Path


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_generate_pygame_game():
    """Generate a real Pygame game using proper engine adapter."""
    from ai_game_dev.engine_adapters import EngineAdapterManager
    
    # Check API key
    if not os.getenv("OPENAI_API_KEY"):
        pytest.skip("OPENAI_API_KEY not available")
    
    # Use proper engine adapter system
    engine_manager = EngineAdapterManager()
    
    # Generate complete pygame project
    result = await engine_manager.generate_for_engine(
        engine_name="pygame",
        description="A 2D space shooter with player ship, enemies, bullets, collision detection, and score system",
        complexity="intermediate",
        features=["player_movement", "shooting", "collision_detection", "score_system"],
        art_style="retro"
    )
    
    assert result is not None
    assert result.engine_type == "pygame"
    assert len(result.project_structure) > 0
    assert len(result.main_files) > 0
    assert "pygame" in result.build_instructions.lower()
    
    # Save generated project
    output_dir = Path("tests/e2e/outputs/pygame_project")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Save project overview
    with open(output_dir / "project_structure.txt", "w") as f:
        f.write(f"Engine: {result.engine_type}\n")
        f.write(f"Main files: {result.main_files}\n")
        f.write(f"Asset requirements: {result.asset_requirements}\n")
        f.write(f"Build instructions: {result.build_instructions}\n")
    
    print(f"✅ Generated complete Pygame project with {len(result.main_files)} main files")
    return True


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_generate_bevy_game():
    """Generate a real Bevy (Rust) game using proper engine adapter."""
    from ai_game_dev.engine_adapters import EngineAdapterManager
    
    if not os.getenv("OPENAI_API_KEY"):
        pytest.skip("OPENAI_API_KEY not available")
    
    # Use proper engine adapter system
    engine_manager = EngineAdapterManager()
    
    # Generate complete Bevy project
    result = await engine_manager.generate_for_engine(
        engine_name="bevy",
        description="A 3D space exploration game with physics, camera controls, and procedural asteroid generation",
        complexity="complex",
        features=["3d_graphics", "physics_simulation", "camera_controls", "procedural_generation"],
        art_style="sci-fi"
    )
    
    assert result is not None
    assert result.engine_type == "bevy"
    assert len(result.project_structure) > 0
    assert len(result.main_files) > 0
    assert "rust" in result.build_instructions.lower() or "cargo" in result.build_instructions.lower()
    
    # Save generated project
    output_dir = Path("tests/e2e/outputs/bevy_project") 
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Save project overview
    with open(output_dir / "project_structure.txt", "w") as f:
        f.write(f"Engine: {result.engine_type}\n")
        f.write(f"Main files: {result.main_files}\n") 
        f.write(f"Asset requirements: {result.asset_requirements}\n")
        f.write(f"Build instructions: {result.build_instructions}\n")
    
    print(f"✅ Generated complete Bevy project with {len(result.main_files)} main files")
    return True


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_generate_godot_game():
    """Generate a real Godot game using proper engine adapter."""
    from ai_game_dev.engine_adapters import EngineAdapterManager
    
    if not os.getenv("OPENAI_API_KEY"):
        pytest.skip("OPENAI_API_KEY not available")
    
    # Use proper engine adapter system
    engine_manager = EngineAdapterManager()
    
    # Generate complete Godot project
    result = await engine_manager.generate_for_engine(
        engine_name="godot",
        description="A 3D platformer adventure with character progression, puzzle mechanics, and dynamic lighting",
        complexity="intermediate", 
        features=["3d_platforming", "character_progression", "puzzle_mechanics", "dynamic_lighting"],
        art_style="stylized"
    )
    
    assert result is not None
    assert result.engine_type == "godot"
    assert len(result.project_structure) > 0
    assert len(result.main_files) > 0
    assert "godot" in result.build_instructions.lower()
    
    # Save generated project
    output_dir = Path("tests/e2e/outputs/godot_project")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Save project overview
    with open(output_dir / "project_structure.txt", "w") as f:
        f.write(f"Engine: {result.engine_type}\n")
        f.write(f"Main files: {result.main_files}\n")
        f.write(f"Asset requirements: {result.asset_requirements}\n") 
        f.write(f"Build instructions: {result.build_instructions}\n")
    
    print(f"✅ Generated complete Godot project with {len(result.main_files)} main files")
    return True


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_yarn_spinner_dialogue_generation():
    """Test Yarn Spinner dialogue and quest generation end-to-end."""
    from ai_game_dev.narrative_system import NarrativeGenerator
    
    if not os.getenv("OPENAI_API_KEY"):
        pytest.skip("OPENAI_API_KEY not available")
    
    # Initialize narrative system
    narrative_gen = NarrativeGenerator()
    
    # Generate quest with dialogue tree
    quest = await narrative_gen.generate_quest_with_dialogue(
        quest_brief="Find the lost magical artifact in the ancient ruins",
        location="Ancient Temple Ruins",
        difficulty="medium",
        quest_type="main_quest",
        project_context="fantasy_rpg_test"
    )
    
    # Verify quest structure
    assert quest is not None
    assert quest.title and len(quest.title) > 0
    assert quest.description and len(quest.description) > 0
    assert quest.objectives and len(quest.objectives) >= 3
    assert quest.dialogue_tree is not None
    assert len(quest.dialogue_tree.nodes) > 0
    
    # Export to Yarn Spinner format
    yarn_file_path = await narrative_gen.export_to_yarnspinner(
        quest.dialogue_tree,
        filename=f"quest_{quest.id}",
        project_context="fantasy_rpg_test"
    )
    
    # Verify Yarn file was created
    yarn_path = Path(yarn_file_path)
    assert yarn_path.exists()
    assert yarn_path.suffix == ".yarn"
    
    # Check Yarn file content
    with open(yarn_path, 'r') as f:
        yarn_content = f.read()
        assert "title:" in yarn_content
        assert "---" in yarn_content  # Yarn format separator
        assert "===" in yarn_content  # End of node marker
    
    # Save test results
    output_dir = Path("tests/e2e/outputs/narrative_test")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    with open(output_dir / "quest_summary.txt", "w") as f:
        f.write(f"Quest Title: {quest.title}\n")
        f.write(f"Description: {quest.description}\n")
        f.write(f"Objectives: {len(quest.objectives)}\n")
        f.write(f"Dialogue Nodes: {len(quest.dialogue_tree.nodes)}\n")
        f.write(f"Yarn File: {yarn_file_path}\n")
    
    print(f"✅ Generated quest '{quest.title}' with {len(quest.dialogue_tree.nodes)} dialogue nodes")
    return True


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_rich_media_asset_generation():
    """Test comprehensive rich media asset generation end-to-end."""
    from ai_game_dev.assets.asset_tools import AssetSpecProcessor
    from ai_game_dev.graphics.cc0_libraries import CC0AssetManager
    from ai_game_dev.fonts.google_fonts import GoogleFontsManager
    from ai_game_dev.audio.audio_tools import AudioAssetManager
    
    if not os.getenv("OPENAI_API_KEY"):
        pytest.skip("OPENAI_API_KEY not available")
    
    # Test CC0 graphics generation
    cc0_manager = CC0AssetManager()
    graphics_assets = await cc0_manager.find_suitable_assets(
        search_query="fantasy character sprite",
        asset_type="image",
        max_results=3
    )
    
    assert graphics_assets is not None
    assert len(graphics_assets) > 0
    
    # Test Google Fonts integration
    fonts_manager = GoogleFontsManager()
    suitable_fonts = await fonts_manager.find_game_fonts(
        game_style="fantasy",
        text_purpose="ui_headers",
        max_results=3
    )
    
    assert suitable_fonts is not None
    assert len(suitable_fonts) > 0
    
    # Test audio asset management
    audio_manager = AudioAssetManager()
    audio_specs = [
        {
            "type": "background_music",
            "style": "fantasy_adventure", 
            "duration": "3min",
            "format": "ogg"
        },
        {
            "type": "sound_effect",
            "purpose": "sword_clash",
            "duration": "short",
            "format": "wav"
        }
    ]
    
    audio_results = []
    for spec in audio_specs:
        result = await audio_manager.process_audio_spec(spec)
        audio_results.append(result)
    
    assert len(audio_results) == 2
    for result in audio_results:
        assert result is not None
        assert result.get("status") != "failed"
    
    # Test comprehensive asset processing
    asset_processor = AssetSpecProcessor()
    
    comprehensive_spec = {
        "graphics": [
            {"name": "player_sprite", "type": "character", "style": "fantasy"},
            {"name": "background", "type": "environment", "style": "ancient_ruins"}
        ],
        "audio": [
            {"name": "theme_music", "type": "background", "style": "epic_fantasy"},
            {"name": "footsteps", "type": "effect", "purpose": "movement"}
        ],
        "fonts": [
            {"name": "ui_font", "purpose": "interface", "style": "readable"},
            {"name": "title_font", "purpose": "headers", "style": "decorative"}
        ]
    }
    
    processed_assets = await asset_processor.process_asset_bundle(
        comprehensive_spec,
        project_context="rich_media_test"
    )
    
    assert processed_assets is not None
    assert "graphics" in processed_assets
    assert "audio" in processed_assets
    assert "fonts" in processed_assets
    
    # Save test results
    output_dir = Path("tests/e2e/outputs/asset_test")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    with open(output_dir / "asset_summary.txt", "w") as f:
        f.write(f"CC0 Graphics Found: {len(graphics_assets)}\n")
        f.write(f"Google Fonts Found: {len(suitable_fonts)}\n")
        f.write(f"Audio Assets Generated: {len(audio_results)}\n")
        f.write(f"Comprehensive Assets: {len(processed_assets)}\n")
        
        # Detail each category
        for category, assets in processed_assets.items():
            f.write(f"\n{category.title()} Assets:\n")
            for asset in assets:
                f.write(f"  - {asset.get('name', 'unnamed')}: {asset.get('status', 'unknown')}\n")
    
    print(f"✅ Generated comprehensive asset bundle with {sum(len(assets) for assets in processed_assets.values())} total assets")
    return True


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_internet_archive_seeding():
    """Test Internet Archive semantic seeding system end-to-end."""
    from ai_game_dev.assets.archive_seeder import InternetArchiveSeeder
    from ai_game_dev.seed_system import SeedQueue
    
    # Initialize systems
    archive_seeder = InternetArchiveSeeder()
    seed_queue = SeedQueue()
    
    # Test semantic search and seeding
    search_queries = [
        "medieval fantasy artwork",
        "retro video game music", 
        "sound effects library"
    ]
    
    seeded_content = []
    for query in search_queries:
        seeds = await archive_seeder.search_and_seed(
            query=query,
            content_types=["image", "audio"],
            max_results=3
        )
        seeded_content.extend(seeds)
    
    assert len(seeded_content) > 0
    
    # Test seed consumption for game generation
    consumed_seeds = await seed_queue.consume_seeds(
        query_tags=["fantasy", "game", "asset"],
        project_context="archive_test",
        max_seeds=5
    )
    
    assert consumed_seeds is not None
    assert len(consumed_seeds) > 0
    
    # Verify seed quality and relevance
    for seed in consumed_seeds:
        assert seed.get("content_type") in ["image", "audio", "text"]
        assert seed.get("relevance_score", 0) > 0.5
        assert seed.get("metadata") is not None
    
    # Save test results
    output_dir = Path("tests/e2e/outputs/seeding_test")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    with open(output_dir / "seeding_summary.txt", "w") as f:
        f.write(f"Total Seeds Generated: {len(seeded_content)}\n")
        f.write(f"Seeds Consumed: {len(consumed_seeds)}\n")
        f.write(f"Search Queries Tested: {len(search_queries)}\n")
        
        f.write("\nSeeded Content Types:\n")
        content_types = {}
        for seed in seeded_content:
            content_type = seed.get("content_type", "unknown")
            content_types[content_type] = content_types.get(content_type, 0) + 1
        
        for content_type, count in content_types.items():
            f.write(f"  - {content_type}: {count}\n")
        
        f.write("\nConsumed Seed Relevance:\n")
        total_relevance = sum(seed.get("relevance_score", 0) for seed in consumed_seeds)
        avg_relevance = total_relevance / len(consumed_seeds) if consumed_seeds else 0
        f.write(f"  - Average relevance: {avg_relevance:.3f}\n")
        f.write(f"  - High quality seeds (>0.7): {sum(1 for seed in consumed_seeds if seed.get('relevance_score', 0) > 0.7)}\n")
    
    print(f"✅ Seeded {len(seeded_content)} items from Internet Archive, consumed {len(consumed_seeds)} for generation")
    return True
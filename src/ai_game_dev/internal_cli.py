"""
Internal CLI Commands for Development
These commands are only available during development and are filtered out for release builds.
"""

import asyncio
import os
import json
from pathlib import Path
from typing import Optional, List
import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich.table import Table

# Internal CLI - separate from main CLI

from ai_game_dev.agents.internal_agent import InternalAssetAgent
from ai_game_dev.agents.master_orchestrator import MasterGameDevOrchestrator

internal_app = typer.Typer(help="Internal Development Commands - Not included in release builds")
console = Console()

def internal_main():
    """Entry point for ai-game-dev-internal hatch script."""
    internal_app()


@internal_app.command(name="build-static-assets")
def build_static_assets(
    force_rebuild: bool = typer.Option(False, help="Force rebuild even if assets exist"),
    dry_run: bool = typer.Option(False, help="Show what would be built without building")
):
    """
    Idempotent command to build static platform assets using the Internal Asset Agent.
    """
    
    console.print(Panel(
        "[bold cyan]Building Static Platform Assets[/bold cyan]\n"
        "UI elements, logos, icons, and audio for the web platform",
        title="🎨 Static Asset Builder"
    ))
    
    if dry_run:
        console.print("[yellow]DRY RUN MODE - No files will be created[/yellow]")
        return
    
    async def run_asset_generation():
        async with InternalAssetAgent() as agent:
            task = "Generate all static platform assets from the unified specification including cyberpunk UI elements, engine panels, and branding assets"
            
            results = await agent.execute_task(task, {
                "force_rebuild": force_rebuild,
                "asset_type": "static_platform"
            })
            
            return results
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Initializing Internal Asset Agent...", total=None)
        
        try:
            results = asyncio.run(run_asset_generation())
            progress.update(task, completed=True, description="✅ Static assets complete")
            
            # Display results - handle dict response properly
            if isinstance(results, dict):
                success = results.get("success", True)
                assets_count = results.get("assets_created", len(results.get("generated", [])))
                message = results.get("response", results.get("message", "Asset generation completed"))
            else:
                success = getattr(results, 'success', True)
                assets_count = getattr(results, 'assets_created', 0)
                message = getattr(results, 'response', 'Asset generation completed')
                
            if success or assets_count > 0:
                console.print(f"✅ Generated {assets_count} static assets")
            else:
                console.print(f"⚠️ Asset generation completed: {message}")
                
        except Exception as e:
            progress.update(task, completed=True, description="❌ Asset generation failed")
            console.print(f"[red]Error: {e}[/red]")


@internal_app.command(name="build-educational-game-code")
def build_educational_game_code(
    force_rebuild: bool = typer.Option(False, help="Force rebuild even if code exists"),
    dry_run: bool = typer.Option(False, help="Show what would be built without building")
):
    """
    Idempotent command to build the educational RPG game code using the Internal Asset Agent.
    """
    
    console.print(Panel(
        "[bold cyan]Building Educational RPG Code[/bold cyan]\n"
        "Complete pygame RPG demonstrating Python concepts",
        title="🎮 Educational Code Builder"
    ))
    
    if dry_run:
        console.print("[yellow]DRY RUN MODE - No files will be created[/yellow]")
        return
    
    async def run_game_generation():
        async with InternalAssetAgent() as agent:
            task = "Generate the complete NeoTokyo Code Academy educational RPG game code with pygame, including all game mechanics, character classes, and educational progression system"
            
            results = await agent.execute_task(task, {
                "force_rebuild": force_rebuild,
                "asset_type": "educational_game_code"
            })
            
            return results
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Generating educational RPG with Internal Agent...", total=None)
        
        try:
            results = asyncio.run(run_game_generation())
            progress.update(task, completed=True, description="✅ Educational RPG code complete")
            
            # Handle dict response properly
            if isinstance(results, dict):
                success = results.get("success", True)
                message = results.get("response", results.get("message", "Educational RPG generated"))
            else:
                success = getattr(results, 'success', True)
                message = getattr(results, 'response', 'Educational RPG generated')
                
            if success:
                console.print(f"✅ Generated educational RPG: {message}")
            else:
                console.print(f"⚠️ Game generation completed: {message}")
                
        except Exception as e:
            progress.update(task, completed=True, description="❌ Game generation failed")
            console.print(f"[red]Error: {e}[/red]")


@internal_app.command(name="build-educational-game-assets")
def build_educational_game_assets(
    force_rebuild: bool = typer.Option(False, help="Force rebuild even if assets exist"),
    dry_run: bool = typer.Option(False, help="Show what would be built without building")
):
    """
    Idempotent command to build cyberpunk assets for the educational RPG using the Internal Asset Agent.
    """
    
    console.print(Panel(
        "[bold cyan]Building Educational RPG Assets[/bold cyan]\n"
        "Cyberpunk sprites, environments, and audio for the educational game",
        title="🏙️ Educational Asset Builder"
    ))
    
    if dry_run:
        console.print("[yellow]DRY RUN MODE - No files will be created[/yellow]")
        return
    
    async def run_educational_assets():
        async with InternalAssetAgent() as agent:
            task = "Generate all cyberpunk educational assets including Professor Pixel character sprites, NeoTokyo environment tilesets, character class sprites (Code Knight, Data Sage, Bug Hunter, Web Weaver), and educational UI elements"
            
            results = await agent.execute_task(task, {
                "force_rebuild": force_rebuild,
                "asset_type": "educational_game_assets"
            })
            
            return results
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Generating cyberpunk assets with Internal Agent...", total=None)
        
        try:
            results = asyncio.run(run_educational_assets())
            progress.update(task, completed=True, description="✅ Educational assets complete")
            
            # Handle dict response properly
            if isinstance(results, dict):
                success = results.get("success", True)
                assets_count = results.get("assets_created", len(results.get("characters", []) + results.get("environments", []) + results.get("ui_elements", [])))
                message = results.get("response", results.get("message", "Educational assets generated"))
            else:
                success = getattr(results, 'success', True)
                assets_count = getattr(results, 'assets_created', 0)
                message = getattr(results, 'response', 'Educational assets generated')
                
            if success or assets_count > 0:
                console.print(f"✅ Generated educational assets: {assets_count} files")
            else:
                console.print(f"⚠️ Asset generation completed: {message}")
                
        except Exception as e:
            progress.update(task, completed=True, description="❌ Educational asset generation failed")
            console.print(f"[red]Error: {e}[/red]")


@internal_app.command(name="build-all")
def build_all_internal_assets(
    force_rebuild: bool = typer.Option(False, help="Force rebuild everything"),
    dry_run: bool = typer.Option(False, help="Show what would be built without building")
):
    """
    Idempotent command to build ALL internal assets and code.
    """
    
    console.print(Panel(
        "[bold cyan]Building ALL Internal Assets[/bold cyan]\n"
        "Complete build of static assets, educational game code, and assets",
        title="🏗️ Complete Internal Builder"
    ))
    
    # Run all build commands in sequence
    console.print("\n[bold]Step 1: Building static platform assets...[/bold]")
    try:
        build_static_assets(force_rebuild=force_rebuild, dry_run=dry_run)
    except Exception as e:
        console.print(f"[red]Step 1 failed: {e}[/red]")
    
    console.print("\n[bold]Step 2: Building educational game code...[/bold]")
    try:
        build_educational_game_code(force_rebuild=force_rebuild, dry_run=dry_run)
    except Exception as e:
        console.print(f"[red]Step 2 failed: {e}[/red]")
    
    console.print("\n[bold]Step 3: Building educational game assets...[/bold]")
    try:
        build_educational_game_assets(force_rebuild=force_rebuild, dry_run=dry_run)
    except Exception as e:
        console.print(f"[red]Step 3 failed: {e}[/red]")
    
    console.print("\n🎉 [bold green]All internal builds complete![/bold green]")


@internal_app.command(name="generate-game")
def generate_game_with_orchestrator(
    description: str = typer.Argument(..., help="Natural language description of the game to generate"),
    engine: Optional[str] = typer.Option(None, help="Preferred engine: pygame, godot, or bevy"),
    use_seeding: bool = typer.Option(True, help="Use literary seeding for narrative enhancement"),
    force_rebuild: bool = typer.Option(False, help="Force rebuild even if project exists")
):
    """
    Generate a complete game using the Master Orchestrator with spec generation and routing.
    """
    
    console.print(Panel(
        f"[bold cyan]Generating Game with Master Orchestrator[/bold cyan]\n"
        f"Description: {description}\n"
        f"Engine preference: {engine or 'auto-detect'}\n"
        f"Literary seeding: {'enabled' if use_seeding else 'disabled'}",
        title="🎮 Master Game Generator"
    ))
    
    async def run_orchestrator():
        async with MasterGameDevOrchestrator() as orchestrator:
            # Build user input with preferences
            user_input = description
            if engine:
                user_input += f" using {engine} engine"
                
            results = await orchestrator.execute_task(user_input, {
                "force_rebuild": force_rebuild,
                "use_seeding": use_seeding,
                "engine_preference": engine
            })
            
            return results
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Initializing Master Orchestrator...", total=None)
        
        try:
            results = asyncio.run(run_orchestrator())
            progress.update(task, completed=True, description="✅ Game generation complete")
            
            # Display comprehensive results
            if results.get("success"):
                spec = results.get("generated_spec", {})
                engine_used = results.get("chosen_engine", "unknown")
                
                console.print(f"\n✅ Successfully generated game: [bold]{spec.get('title', 'Generated Game')}[/bold]")
                console.print(f"Engine: [cyan]{engine_used}[/cyan]")
                console.print(f"Genre: [green]{spec.get('genre', 'adventure')}[/green]")
                
                if results.get("seeding_applied"):
                    console.print("🌱 Literary seeding applied for narrative enhancement")
                    
                if results.get("human_reviewed"):
                    console.print("👤 Specification reviewed and approved")
                    
                artifacts = results.get("artifacts_created", [])
                if artifacts:
                    console.print(f"\n📁 Created {len(artifacts)} project artifacts:")
                    for artifact in artifacts[:5]:  # Show first 5
                        console.print(f"  • {artifact}")
                    if len(artifacts) > 5:
                        console.print(f"  ... and {len(artifacts) - 5} more files")
                        
            else:
                console.print(f"⚠️ Game generation completed with issues: {results.get('response', 'Unknown error')}")
                
        except Exception as e:
            progress.update(task, completed=True, description="❌ Game generation failed")
            console.print(f"[red]Error: {e}[/red]")


@internal_app.command(name="test-seeding")
def test_seeding_system(
    theme: str = typer.Argument("fantasy adventure", help="Theme to test seeding with"),
    max_sources: int = typer.Option(3, help="Maximum sources to gather")
):
    """
    Test the seeding system with PyTorch embeddings and Internet Archive integration.
    """
    
    console.print(Panel(
        f"[bold cyan]Testing Seeding System[/bold cyan]\n"
        f"Theme: {theme}\n"
        f"Max sources: {max_sources}",
        title="🌱 Seeding System Test"
    ))
    
    async def test_seeding():
        from ai_game_dev.seeding.literary_seeder import LiterarySeeder, SeedingRequest
        
        seeder = LiterarySeeder()
        request = SeedingRequest(
            themes=[theme],
            genres=["fantasy", "adventure"],
            character_types=["hero", "mentor"],
            settings=["medieval", "magical"],
            max_sources=max_sources
        )
        
        results = await seeder.seed_from_request(request)
        return results
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Testing seeding system...", total=None)
        
        try:
            results = asyncio.run(test_seeding())
            progress.update(task, completed=True, description="✅ Seeding test complete")
            
            # Display seeding results
            console.print(f"\n🌱 Seeding Results:")
            
            themes_found = results.get("themes_found", [])
            if themes_found:
                console.print(f"Themes discovered: {', '.join(themes_found)}")
                
            character_inspirations = results.get("character_inspirations", [])
            if character_inspirations:
                console.print(f"\n👥 Character inspirations found: {len(character_inspirations)}")
                for char in character_inspirations[:3]:
                    console.print(f"  • {char.get('archetype', 'Unknown')}: {char.get('description', 'No description')}")
                    
            setting_inspirations = results.get("setting_inspirations", [])
            if setting_inspirations:
                console.print(f"\n🏰 Setting inspirations found: {len(setting_inspirations)}")
                for setting in setting_inspirations[:3]:
                    console.print(f"  • {setting.get('type', 'Unknown')}: {setting.get('description', 'No description')}")
                    
            embedding_summary = results.get("embedding_summary", {})
            if embedding_summary and embedding_summary.get("pytorch_available"):
                console.print(f"\n🧠 PyTorch Embeddings:")
                console.print(f"  • Average relevance: {embedding_summary.get('average_relevance', 0):.3f}")
                console.print(f"  • Highest relevance: {embedding_summary.get('highest_relevance', 0):.3f}")
                console.print(f"  • Embedding dimensions: {embedding_summary.get('embedding_dimensions', 0)}")
            else:
                console.print("\n⚠️ PyTorch embeddings not available (install sentence-transformers for full functionality)")
                
        except Exception as e:
            progress.update(task, completed=True, description="❌ Seeding test failed")
            console.print(f"[red]Error: {e}[/red]")


# All asset checking, generation, and management is now handled by InternalAssetAgent
# The agent provides comprehensive functionality including:
# - Idempotent asset generation with proper file checking
# - Real OpenAI DALL-E 3 image generation (no placeholders)
# - Batch processing with rate limiting and error handling
# - Educational game code generation with pygame
# - Static platform asset generation
# - Quality validation and directory management


# LEGACY FUNCTIONS REMOVED
# All asset generation is now handled by InternalAssetAgent with real OpenAI integration


@internal_app.command(name="validate")
def validate_internal_assets():
    """Validate that all internal assets are present and correctly structured."""
    
    console.print(Panel(
        "[bold cyan]Validating Internal Assets[/bold cyan]\n"
        "Checking asset integrity and completeness",
        title="🔍 Asset Validator"
    ))
    
    issues = []
    
    # Check platform assets
    platform_assets_dir = Path("src/ai_game_dev/server/static/assets")
    if not _check_platform_assets_complete(platform_assets_dir):
        issues.append("Platform assets incomplete")
    
    # Check educational RPG
    educational_game_dir = Path("src/ai_game_dev/education/generated_game")
    if not _check_educational_rpg_complete(educational_game_dir):
        issues.append("Educational RPG incomplete")
    
    # Check for orphaned files
    orphaned_files = _find_orphaned_assets()
    if orphaned_files:
        issues.extend([f"Orphaned file: {f}" for f in orphaned_files])
    
    if issues:
        table = Table(title="Asset Issues Found")
        table.add_column("Issue", style="red")
        
        for issue in issues:
            table.add_row(issue)
        
        console.print(table)
        console.print(f"\n[red]Found {len(issues)} issues. Run 'build-internal-assets --force-rebuild' to fix.[/red]")
    else:
        console.print("✅ All internal assets are valid and complete!")


def _find_orphaned_assets() -> List[str]:
    """Find asset files that aren't referenced anywhere."""
    # This would implement logic to scan for unused assets
    # For now, return empty list
    return []


@internal_app.command(name="clean")
def clean_internal_assets():
    """Clean up old or orphaned internal assets."""
    
    console.print(Panel(
        "[bold yellow]Cleaning Internal Assets[/bold yellow]\n"
        "Removing orphaned and outdated assets",
        title="🧹 Asset Cleaner"
    ))
    
    # Find and remove orphaned files
    orphaned_files = _find_orphaned_assets()
    
    if orphaned_files:
        for file_path in orphaned_files:
            try:
                Path(file_path).unlink()
                console.print(f"Removed: {file_path}")
            except Exception as e:
                console.print(f"[red]Error removing {file_path}: {e}[/red]")
    else:
        console.print("✅ No orphaned assets found")


@internal_app.command(name="stats")
def show_asset_stats():
    """Show statistics about internal assets."""
    
    console.print(Panel(
        "[bold cyan]Internal Asset Statistics[/bold cyan]",
        title="📊 Asset Stats"
    ))
    
    stats = _gather_asset_statistics()
    
    table = Table(title="Asset Inventory")
    table.add_column("Category", style="cyan")
    table.add_column("Count", style="green")
    table.add_column("Total Size", style="yellow")
    
    for category, data in stats.items():
        table.add_row(category, str(data["count"]), data["size"])
    
    console.print(table)


def _gather_asset_statistics() -> dict:
    """Gather statistics about all internal assets."""
    
    stats = {}
    
    # Platform assets
    platform_dir = Path("src/ai_game_dev/server/static/assets")
    if platform_dir.exists():
        platform_files = list(platform_dir.rglob("*"))
        platform_size = sum(f.stat().st_size for f in platform_files if f.is_file())
        stats["Platform Assets"] = {
            "count": len([f for f in platform_files if f.is_file()]),
            "size": f"{platform_size / 1024 / 1024:.1f} MB"
        }
    
    # Educational game assets
    edu_dir = Path("src/ai_game_dev/education/generated_game")
    if edu_dir.exists():
        edu_files = list(edu_dir.rglob("*"))
        edu_size = sum(f.stat().st_size for f in edu_files if f.is_file())
        stats["Educational RPG"] = {
            "count": len([f for f in edu_files if f.is_file()]),
            "size": f"{edu_size / 1024 / 1024:.1f} MB"
        }
    
    return stats


if __name__ == "__main__":
    # This allows running internal commands directly during development
    internal_app()
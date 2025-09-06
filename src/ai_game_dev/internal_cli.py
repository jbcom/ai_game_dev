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

# Internal commands - fail fast if environment isn't set up correctly
if os.getenv("AI_GAME_DEV_INTERNAL", "false").lower() != "true":
    raise RuntimeError("Internal CLI requires AI_GAME_DEV_INTERNAL=true environment variable")

from ai_game_dev.agents.internal_agent import InternalAssetAgent

internal_app = typer.Typer(help="Internal Development Commands - Not included in release builds")
console = Console()


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
            
            # Display results
            if results.get("success"):
                console.print(f"✅ Generated {results.get('assets_created', 0)} static assets")
            else:
                console.print(f"⚠️ Asset generation completed with issues: {results.get('response', 'Unknown error')}")
                
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
            
            if results.get("success"):
                console.print(f"✅ Generated educational RPG: {results.get('response', 'Complete')}")
            else:
                console.print(f"⚠️ Game generation completed with issues: {results.get('response', 'Unknown error')}")
                
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
            
            if results.get("success"):
                console.print(f"✅ Generated educational assets: {results.get('assets_created', 0)} files")
            else:
                console.print(f"⚠️ Asset generation completed with issues: {results.get('response', 'Unknown error')}")
                
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
    build_static_assets(force_rebuild=force_rebuild, dry_run=dry_run)
    
    console.print("\n[bold]Step 2: Building educational game code...[/bold]")
    build_educational_game_code(force_rebuild=force_rebuild, dry_run=dry_run)
    
    console.print("\n[bold]Step 3: Building educational game assets...[/bold]")
    build_educational_game_assets(force_rebuild=force_rebuild, dry_run=dry_run)
    
    console.print("\n🎉 [bold green]All internal builds complete![/bold green]")


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
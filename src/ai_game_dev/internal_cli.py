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

from ai_game_dev.education.complete_rpg_generator import create_complete_educational_game
from ai_game_dev.assets.generator import AssetGenerator, AssetRequest
from ai_game_dev.cli import _batch_generate_assets

internal_app = typer.Typer(help="Internal Development Commands - Not included in release builds")
console = Console()


@internal_app.command(name="build-static-assets")
def build_static_assets(
    force_rebuild: bool = typer.Option(False, help="Force rebuild even if assets exist"),
    dry_run: bool = typer.Option(False, help="Show what would be built without building")
):
    """
    Idempotent command to build static platform assets (UI, logos, icons, audio).
    """
    
    console.print(Panel(
        "[bold cyan]Building Static Platform Assets[/bold cyan]\n"
        "UI elements, logos, icons, and audio for the web platform",
        title="🎨 Static Asset Builder"
    ))
    
    if dry_run:
        console.print("[yellow]DRY RUN MODE - No files will be created[/yellow]")
    
    platform_assets_dir = Path("src/ai_game_dev/server/static/assets")
    
    if force_rebuild or not _check_platform_assets_complete(platform_assets_dir):
        if dry_run:
            console.print("[yellow]Would build platform static assets[/yellow]")
            return
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Building static assets...", total=None)
            asyncio.run(_build_platform_assets())
            progress.update(task, completed=True, description="✅ Static assets complete")
    else:
        console.print("✅ Static assets up to date")


@internal_app.command(name="build-educational-game-code")
def build_educational_game_code(
    force_rebuild: bool = typer.Option(False, help="Force rebuild even if code exists"),
    dry_run: bool = typer.Option(False, help="Show what would be built without building")
):
    """
    Idempotent command to build the educational RPG game code.
    """
    
    console.print(Panel(
        "[bold cyan]Building Educational RPG Code[/bold cyan]\n"
        "Complete pygame RPG demonstrating Python concepts",
        title="🎮 Educational Code Builder"
    ))
    
    if dry_run:
        console.print("[yellow]DRY RUN MODE - No files will be created[/yellow]")
    
    educational_game_dir = Path("src/ai_game_dev/education/generated_game")
    
    if force_rebuild or not _check_educational_rpg_complete(educational_game_dir):
        if dry_run:
            console.print("[yellow]Would build educational RPG code[/yellow]")
            return
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Generating educational RPG...", total=None)
            create_complete_educational_game()
            progress.update(task, completed=True, description="✅ Educational RPG code complete")
    else:
        console.print("✅ Educational RPG code up to date")


@internal_app.command(name="build-educational-game-assets")
def build_educational_game_assets(
    force_rebuild: bool = typer.Option(False, help="Force rebuild even if assets exist"),
    dry_run: bool = typer.Option(False, help="Show what would be built without building")
):
    """
    Idempotent command to build cyberpunk assets for the educational RPG.
    """
    
    console.print(Panel(
        "[bold cyan]Building Educational RPG Assets[/bold cyan]\n"
        "Cyberpunk sprites, environments, and audio for the educational game",
        title="🏙️ Educational Asset Builder"
    ))
    
    if dry_run:
        console.print("[yellow]DRY RUN MODE - No files will be created[/yellow]")
    
    educational_game_dir = Path("src/ai_game_dev/education/generated_game")
    assets_dir = educational_game_dir / "assets"
    
    if force_rebuild or not _check_educational_assets_complete(assets_dir):
        if dry_run:
            console.print("[yellow]Would build educational RPG assets[/yellow]")
            return
        
        # Ensure game code exists first
        if not educational_game_dir.exists():
            console.print("[yellow]Educational game code not found. Building code first...[/yellow]")
            create_complete_educational_game()
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Generating cyberpunk assets...", total=None)
            asyncio.run(_generate_educational_assets(educational_game_dir))
            progress.update(task, completed=True, description="✅ Educational assets complete")
    else:
        console.print("✅ Educational RPG assets up to date")


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


def _check_platform_assets_complete(assets_dir: Path) -> bool:
    """Check if platform assets are complete and up to date."""
    required_dirs = [
        "logos", "engine-panels", "audio", "fonts", 
        "textures", "frames", "characters"
    ]
    
    for dir_name in required_dirs:
        dir_path = assets_dir / dir_name
        if not dir_path.exists() or not any(dir_path.iterdir()):
            return False
    
    return True


def _check_educational_rpg_complete(game_dir: Path) -> bool:
    """Check if educational RPG is complete and up to date."""
    required_files = [
        "game.py", "player.py", "educational_metadata.json", "requirements.txt"
    ]
    
    for file_name in required_files:
        if not (game_dir / file_name).exists():
            return False
    
    return True


def _check_educational_assets_complete(assets_dir: Path) -> bool:
    """Check if educational RPG assets are complete."""
    required_dirs = ["sprites", "tilesets"]
    
    for dir_name in required_dirs:
        dir_path = assets_dir / dir_name
        if not dir_path.exists() or not any(dir_path.iterdir()):
            return False
    
    return True


async def _build_platform_assets():
    """Build all platform UI and visual assets."""
    
    # Load our platform asset specification
    spec_file = Path("src/ai_game_dev/specs/web_platform_assets.toml")
    
    if spec_file.exists():
        # Use existing batch processor
        batch_processor = BatchProcessor()
        await batch_processor.process_specification_file(str(spec_file))
    else:
        # Generate core assets manually
        await _generate_core_platform_assets()


async def _generate_core_platform_assets():
    """Generate core platform assets if specification is missing."""
    
    generator = AssetGenerator()
    assets_dir = Path("src/ai_game_dev/server/static/assets")
    
    # Generate essential UI elements
    ui_assets = [
        ("main-logo.svg", "AI Game Dev logo, cyberpunk style, transparent background"),
        ("favicon.ico", "Favicon version of AI Game Dev logo, 32x32 pixels"),
    ]
    
    logos_dir = assets_dir / "logos"
    logos_dir.mkdir(parents=True, exist_ok=True)
    
    for filename, description in ui_assets:
        try:
            request = AssetRequest(
                asset_type="ui_icon",
                description=description,
                style="cyberpunk futuristic",
                dimensions=(512, 512),
                format="PNG"
            )
            asset = await generator.generate_ui_icon(request)
            
            output_path = logos_dir / filename
            if asset.data:
                output_path.write_bytes(asset.data)
                console.print(f"Generated: {filename}")
                
        except Exception as e:
            console.print(f"[yellow]Warning: Could not generate {filename}: {e}[/yellow]")




async def _generate_educational_assets(game_dir: Path):
    """Generate cyberpunk assets for the educational RPG."""
    
    generator = AssetGenerator()
    assets_dir = game_dir / "assets"
    assets_dir.mkdir(exist_ok=True)
    
    # Character sprites
    characters = [
        ("professor_pixel.png", "Professor Pixel: Cyberpunk mentor with neon hair and AR glasses"),
        ("code_knight.png", "Code Knight: Cybernetic warrior with plasma sword"),
        ("data_sage.png", "Data Sage: Mystical hacker with holographic robes"),
        ("bug_hunter.png", "Bug Hunter: Agile cyber-assassin with stealth cloak"),
        ("web_weaver.png", "Web Weaver: Digital architect with quantum tablet")
    ]
    
    sprites_dir = assets_dir / "sprites"
    sprites_dir.mkdir(exist_ok=True)
    
    for filename, description in characters:
        try:
            request = AssetRequest(
                asset_type="sprite",
                description=f"{description}, 16-bit pixel art, transparent background",
                style="cyberpunk pixel art",
                dimensions=(64, 64),
                format="PNG"
            )
            sprite = await generator.generate_sprite(request)
            
            if sprite.data:
                (sprites_dir / filename).write_bytes(sprite.data)
                
        except Exception as e:
            console.print(f"[yellow]Warning: Could not generate {filename}: {e}[/yellow]")
    
    # Environment tilesets
    environments = [
        ("neo_tokyo_streets.png", "Cyberpunk city streets with neon signs"),
        ("underground_academy.png", "Hidden rebel programming school"),
        ("algorithm_tower.png", "Corporate empire data center interior")
    ]
    
    tilesets_dir = assets_dir / "tilesets"
    tilesets_dir.mkdir(exist_ok=True)
    
    for filename, description in environments:
        try:
            request = AssetRequest(
                asset_type="tileset",
                description=f"{description}, 16-bit isometric pixel art",
                style="cyberpunk pixel art",
                format="PNG",
                additional_params={"tile_size": 32, "grid_size": (8, 8)}
            )
            tileset = await generator.generate_tileset(request)
            
            if tileset.data:
                (tilesets_dir / filename).write_bytes(tileset.data)
                
        except Exception as e:
            console.print(f"[yellow]Warning: Could not generate {filename}: {e}[/yellow]")


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
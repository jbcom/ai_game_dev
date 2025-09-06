import asyncio
from pathlib import Path
from typing import Optional, List
import typer
import toml
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.panel import Panel
from rich.table import Table

from ai_game_dev.engines import get_supported_engines, generate_for_engine
from ai_game_dev.server.unified_server import UnifiedGameDevServer

app = typer.Typer(help="AI Game Development CLI - Revolutionary AI-powered game creation")
console = Console()

@app.command()
def generate(
    description: str = typer.Argument(..., help="Description of the game to generate"),
    engine: str = typer.Option("pygame", help="Game engine to use"),
    complexity: str = typer.Option("intermediate", help="Game complexity level"),
    output_dir: Optional[Path] = typer.Option(None, help="Output directory for generated project"),
    art_style: str = typer.Option("modern", help="Art style for the game"),
    features: List[str] = typer.Option([], help="Additional features to include")
):
    """Generate a new game project using AI."""
    
    supported_engines = get_supported_engines()
    if engine not in supported_engines:
        console.print(f"[red]Error: Engine '{engine}' not supported. Available: {', '.join(supported_engines)}[/red]")
        raise typer.Exit(1)
    
    console.print(Panel(f"[bold cyan]Generating {engine} game[/bold cyan]\n{description}", title="AI Game Generation"))
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Generating game project...", total=None)
        
        try:
            result = asyncio.run(generate_for_engine(
                engine_name=engine,
                description=description,
                complexity=complexity,
                features=features,
                art_style=art_style
            ))
            
            progress.update(task, completed=True, description="✅ Generation complete!")
            
            table = Table(title="Generated Project")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="green")
            
            table.add_row("Engine", result.engine_type)
            table.add_row("Main Files", ", ".join(result.main_files))
            table.add_row("Generated Files", str(len(result.generated_files)))
            if result.project_path:
                table.add_row("Output Path", str(result.project_path))
            
            console.print(table)
            
            if result.build_instructions:
                console.print(Panel("\n".join(result.build_instructions), title="Build Instructions", border_style="green"))
                
        except Exception as e:
            progress.update(task, completed=True, description="❌ Generation failed!")
            console.print(f"[red]Error: {e}[/red]")
            raise typer.Exit(1)

@app.command()
def engines():
    """List available game engines."""
    supported_engines = get_supported_engines()
    
    table = Table(title="Supported Game Engines")
    table.add_column("Engine", style="cyan")
    table.add_column("Language", style="green")
    table.add_column("Status", style="yellow")
    
    for engine in supported_engines:
        table.add_row(engine.title(), "Python" if engine == "pygame" else "Rust" if engine == "bevy" else "GDScript", "✅ Ready")
    
    console.print(table)

@app.command()
def server(
    host: str = typer.Option("127.0.0.1", help="Host to bind the server"),
    port: int = typer.Option(5000, help="Port to bind the server"),
    reload: bool = typer.Option(False, help="Enable auto-reload for development")
):
    """Start the AI Game Development server."""
    console.print(Panel(f"[bold green]Starting server at http://{host}:{port}[/bold green]", title="AI Game Dev Server"))
    
    try:
        server_instance = UnifiedGameDevServer(host=host, port=port)
        import uvicorn
        uvicorn.run(server_instance.app, host=host, port=port, log_level="info")
    except KeyboardInterrupt:
        console.print("\n[yellow]Server stopped by user[/yellow]")

@app.command()
def build_assets(
    spec_file: str = typer.Option("src/ai_game_dev/specs/web_platform_assets.toml", help="Asset specification TOML file"),
    output_dir: Optional[str] = typer.Option(None, help="Override output directory"),
    dry_run: bool = typer.Option(False, help="Show what would be generated without actually generating")
):
    """Build all static web assets for our platform using batch generation."""
    
    spec_path = Path(spec_file)
    if not spec_path.exists():
        console.print(f"[red]Error: Specification file not found: {spec_file}[/red]")
        raise typer.Exit(1)
    
    console.print(Panel(f"[bold cyan]Building Platform Assets[/bold cyan]\nSpec: {spec_file}", title="Asset Generation"))
    
    try:
        # Load asset specification
        with open(spec_path, 'r') as f:
            spec = toml.load(f)
        
        # Extract batch config
        batch_config = spec.get('batch_config', {})
        total_assets = batch_config.get('total_assets', 0)
        output_directory = output_dir or batch_config.get('output_directory', 'src/ai_game_dev/server/static/assets/generated/')
        
        # Ensure output directory exists
        Path(output_directory).mkdir(parents=True, exist_ok=True)
        
        if dry_run:
            console.print(f"[yellow]DRY RUN: Would generate {total_assets} assets to {output_directory}[/yellow]")
            _show_asset_summary(spec)
            return
        
        # Run the batch generation
        asyncio.run(_batch_generate_assets(spec, output_directory))
        
    except Exception as e:
        console.print(f"[red]Error loading specification: {e}[/red]")
        raise typer.Exit(1)

@app.command()
def assets(
    asset_type: str = typer.Argument(..., help="Type of asset to generate"),
    description: str = typer.Argument(..., help="Description of the asset"),
    style: str = typer.Option("modern", help="Art style for the asset"),
    output_dir: Optional[Path] = typer.Option(None, help="Output directory for assets")
):
    """Generate single game asset using AI."""
    console.print(Panel(f"[bold magenta]Generating {asset_type} asset[/bold magenta]\n{description}", title="Asset Generation"))
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Generating asset...", total=None)
        
        try:
            console.print("[yellow]Single asset generation feature coming soon![/yellow]")
            progress.update(task, completed=True, description="✅ Asset generation ready!")
            
        except Exception as e:
            progress.update(task, completed=True, description="❌ Asset generation failed!")
            console.print(f"[red]Error: {e}[/red]")
            raise typer.Exit(1)

@app.command()
def version():
    """Show version information."""
    console.print("[bold cyan]AI Game Development Platform[/bold cyan]")
    console.print("Version: 1.0.0")
    console.print("Engines: Pygame, Bevy, Godot")
    console.print("LLM Support: OpenAI, Anthropic, Google, Local")

async def _batch_generate_assets(spec: dict, output_directory: str):
    """Internal function to batch generate assets from specification."""
    
    # Use our generate_image_tool directly for each asset
    assets_config = spec.get('assets', {})
    batch_config = spec.get('batch_config', {})
    
    total_generated = 0
    failed_generations = []
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console,
    ) as progress:
        
        # Process each asset category
        for category_name, category_data in assets_config.items():
            if 'prompts' not in category_data:
                continue
                
            prompts = category_data['prompts']
            category = category_data.get('category', category_name)
            
            task = progress.add_task(f"Generating {category}...", total=len(prompts))
            
            successful = 0
            failed = 0
            
            for i, prompt in enumerate(prompts):
                try:
                    console.print(f"[blue]Generating: {prompt[:50]}...[/blue]")
                    
                    # Create filename
                    filename = f"{category}_{i+1}_{abs(hash(prompt))}.png"
                    output_path = Path(output_directory) / filename
                    output_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Use our internal generate_image_tool
                    import subprocess
                    import json
                    
                    # Call generate_image_tool via function call
                    result = await _generate_image_internal(
                        prompt=prompt,
                        output_path=str(output_path),
                        size="1024x1024"
                    )
                    
                    if result and output_path.exists():
                        successful += 1
                        total_generated += 1
                        console.print(f"[green]✓ Saved: {filename}[/green]")
                    else:
                        failed += 1
                        failed_generations.append(f"{category}_{i+1}: Generation failed")
                    
                    progress.update(task, advance=1)
                    
                except Exception as e:
                    console.print(f"[red]Failed: {prompt[:30]}... - {e}[/red]")
                    failed += 1
                    failed_generations.append(f"{category}_{i+1}: {str(e)}")
                    progress.update(task, advance=1)
            
            console.print(f"[green]✅ {category}: {successful}/{len(prompts)} generated[/green]")
    
    # Final summary
    console.print(Panel(
        f"[bold green]Asset Generation Complete![/bold green]\n"
        f"Total Generated: {total_generated}\n"
        f"Output Directory: {output_directory}\n"
        f"Failed Categories: {len(failed_generations)}",
        title="Summary"
    ))
    
    if failed_generations:
        console.print("[yellow]Failed generations:[/yellow]")
        for failure in failed_generations[:5]:  # Show first 5 failures
            console.print(f"  • {failure}")
        if len(failed_generations) > 5:
            console.print(f"  • ... and {len(failed_generations) - 5} more")

async def _generate_image_internal(prompt: str, output_path: str, size: str = "1024x1024"):
    """Internal function to generate images using our image generation tool."""
    try:
        import openai
        import requests
        
        # Use OpenAI client directly 
        client = openai.OpenAI()
        response = client.images.generate(
            model="gpt-image-1",
            prompt=prompt,
            size=size,
            quality="high",
            n=1
        )
        
        # Download and save
        image_url = response.data[0].url
        img_response = requests.get(image_url)
        
        if img_response.status_code == 200:
            with open(output_path, 'wb') as f:
                f.write(img_response.content)
            return True
        return False
        
    except Exception as e:
        console.print(f"[red]Image generation error: {e}[/red]")
        return False

def _show_asset_summary(spec: dict):
    """Show summary of assets that would be generated."""
    
    table = Table(title="Asset Generation Plan")
    table.add_column("Category", style="cyan")
    table.add_column("Count", style="green")
    table.add_column("Size", style="yellow")
    table.add_column("Quality", style="magenta")
    
    assets_config = spec.get('assets', {})
    total_assets = 0
    
    for category_name, category_data in assets_config.items():
        if 'prompts' in category_data:
            count = len(category_data['prompts'])
            size = category_data.get('size', '512x512')
            quality = category_data.get('quality', 'standard')
            total_assets += count
            
            table.add_row(category_name, str(count), size, quality)
    
    console.print(table)
    console.print(f"[bold]Total Assets: {total_assets}[/bold]")

if __name__ == "__main__":
    app()
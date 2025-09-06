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
def build_audio(
    spec_file: str = typer.Option("src/ai_game_dev/specs/web_platform_assets.toml", help="Unified asset specification TOML file"),
    output_dir: Optional[str] = typer.Option(None, help="Override output directory"),
    category: Optional[str] = typer.Option(None, help="Generate specific category only"),
    dry_run: bool = typer.Option(False, help="Show what would be generated without actually generating")
):
    """Generate procedural audio effects from unified asset spec."""
    
    spec_path = Path(spec_file)
    if not spec_path.exists():
        console.print(f"[red]Error: Asset specification file not found: {spec_file}[/red]")
        raise typer.Exit(1)
    
    console.print(Panel(f"[bold cyan]Generating Game Audio[/bold cyan]\nSpec: {spec_file}", title="Audio Generation"))
    
    try:
        # Load unified specification
        with open(spec_path, 'r') as f:
            spec = toml.load(f)
        
        # Extract config
        config = spec.get('batch_config', {})
        output_directory = output_dir or config.get('audio_output_directory', 'src/ai_game_dev/server/static/assets/audio/')
        
        # Ensure output directory exists
        Path(output_directory).mkdir(parents=True, exist_ok=True)
        
        if dry_run:
            _show_audio_summary(spec, category)
            return
        
        # Run the audio generation
        asyncio.run(_generate_audio_effects(spec, output_directory, category))
        
    except Exception as e:
        console.print(f"[red]Error loading audio specification: {e}[/red]")
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

async def _generate_audio_effects(spec: dict, output_directory: str, category_filter: Optional[str]):
    """Generate procedural audio effects from specification."""
    
    total_generated = 0
    failed_generations = []
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console,
    ) as progress:
        
        # Process audio categories
        audio_config = spec.get('audio', {})
        
        for category_name, category_data in audio_config.items():
            if category_filter and category_name != category_filter:
                continue
                
            effects = category_data.get('effects', category_data.get('tracks', []))
            durations = category_data.get('duration_ms', [1000] * len(effects))
            audio_format = category_data.get('format', 'wav')
            
            task = progress.add_task(f"Generating {category_name}...", total=len(effects))
            
            for i, effect_name in enumerate(effects):
                try:
                    console.print(f"[blue]Synthesizing: {effect_name}[/blue]")
                    
                    # Generate audio file
                    filename = f"{effect_name}.{audio_format}"
                    output_path = Path(output_directory) / filename
                    
                    duration = durations[i] if i < len(durations) else 1000
                    success = await _synthesize_audio_effect(effect_name, output_path, duration)
                    
                    if success:
                        total_generated += 1
                        console.print(f"[green]✓ Generated: {filename}[/green]")
                    else:
                        failed_generations.append(f"{effect_name}: Synthesis failed")
                    
                    progress.update(task, advance=1)
                    
                except Exception as e:
                    console.print(f"[red]Failed: {effect_name} - {e}[/red]")
                    failed_generations.append(f"{effect_name}: {str(e)}")
                    progress.update(task, advance=1)
            
            console.print(f"[green]✅ {category_name}: Generated {len(effects) - len([f for f in failed_generations if category_name in f])}/{len(effects)} files[/green]")
    
    # Final summary
    console.print(Panel(
        f"[bold green]Audio Generation Complete![/bold green]\n"
        f"Total Generated: {total_generated}\n"
        f"Output Directory: {output_directory}\n"
        f"Failed: {len(failed_generations)}",
        title="Summary"
    ))

async def _synthesize_audio_effect(effect_name: str, output_path: Path, duration_ms: int) -> bool:
    """Synthesize a procedural audio effect."""
    try:
        import wave
        import math
        import random
        
        # Basic procedural synthesis based on effect name
        sample_rate = 44100
        duration_sec = duration_ms / 1000.0
        num_samples = int(sample_rate * duration_sec)
        
        # Generate audio samples
        samples = []
        
        for i in range(num_samples):
            t = i / sample_rate
            
            # Generate different waveforms based on effect type
            if "click" in effect_name or "beep" in effect_name:
                # Short click/beep sound
                frequency = 800
                sample = math.sin(2 * math.pi * frequency * t) * math.exp(-t * 10)
            elif "laser" in effect_name or "zap" in effect_name:
                # Laser/zap effect
                frequency = 1000 - (800 * t / duration_sec)  # Sweep down
                sample = math.sin(2 * math.pi * frequency * t) * math.exp(-t * 3)
            elif "explosion" in effect_name or "boom" in effect_name:
                # Explosion effect (noise burst)
                sample = (random.random() - 0.5) * math.exp(-t * 2)
            elif "footstep" in effect_name or "clank" in effect_name:
                # Percussive sound
                sample = (random.random() - 0.5) * 0.3 * math.exp(-t * 20)
            elif "whoosh" in effect_name:
                # Whoosh effect
                frequency = 200 + 300 * math.sin(2 * math.pi * 2 * t)
                sample = math.sin(2 * math.pi * frequency * t) * (1 - t / duration_sec)
            else:
                # Default tone
                frequency = 440
                sample = math.sin(2 * math.pi * frequency * t) * math.exp(-t * 2)
            
            # Normalize and convert to 16-bit
            sample = max(-1, min(1, sample))
            samples.append(int(sample * 32767))
        
        # Save as WAV file
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with wave.open(str(output_path), 'w') as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(b''.join(sample.to_bytes(2, 'little', signed=True) for sample in samples))
        
        return True
        
    except Exception as e:
        console.print(f"[red]Audio synthesis error: {e}[/red]")
        return False

def _show_audio_summary(spec: dict, category_filter: Optional[str]):
    """Show summary of audio that would be generated."""
    
    table = Table(title="Audio Generation Plan")
    table.add_column("Category", style="cyan")
    table.add_column("Count", style="green")
    table.add_column("Duration", style="yellow")
    table.add_column("Format", style="magenta")
    
    audio_config = spec.get('audio', {})
    total_files = 0
    
    for category_name, category_data in audio_config.items():
        if category_filter and category_name != category_filter:
            continue
            
        effects = category_data.get('effects', category_data.get('tracks', []))
        count = len(effects)
        duration_ms = category_data.get('duration_ms', [1000])
        avg_duration = sum(duration_ms) / len(duration_ms) if duration_ms else 1000
        audio_format = category_data.get('format', 'wav')
        total_files += count
        
        table.add_row(category_name, str(count), f"{avg_duration:.0f}ms", audio_format.upper())
    
    console.print(table)
    console.print(f"[bold]Total Audio Files: {total_files}[/bold]")

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
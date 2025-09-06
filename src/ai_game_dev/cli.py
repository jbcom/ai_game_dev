import asyncio
from pathlib import Path
from typing import Optional, List
import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
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
def assets(
    asset_type: str = typer.Argument(..., help="Type of asset to generate"),
    description: str = typer.Argument(..., help="Description of the asset"),
    style: str = typer.Option("modern", help="Art style for the asset"),
    output_dir: Optional[Path] = typer.Option(None, help="Output directory for assets")
):
    """Generate game assets using AI."""
    console.print(Panel(f"[bold magenta]Generating {asset_type} asset[/bold magenta]\n{description}", title="Asset Generation"))
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Generating asset...", total=None)
        
        try:
            console.print("[yellow]Asset generation feature coming soon![/yellow]")
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

if __name__ == "__main__":
    app()
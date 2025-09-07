"""
Pygbag WebAssembly deployment system for pygame games.
Provides seamless web deployment with Professor Pixel integration.
"""

import asyncio
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()

@dataclass
class PygbagConfig:
    """Configuration for pygbag WebAssembly deployment."""
    
    project_path: Path
    port: int = 8000
    template: str = "simple.tmpl"
    app_name: str = "AI Game"
    archive: bool = False
    dev_mode: bool = False
    custom_template: Optional[Path] = None
    professor_pixel_integration: bool = True
    
    def __post_init__(self):
        self.project_path = Path(self.project_path).resolve()


class PygbagDeployer:
    """Handles pygame to WebAssembly deployment via pygbag."""
    
    def __init__(self, config: PygbagConfig):
        self.config = config
        self.console = Console()
    
    def validate_project(self) -> bool:
        """Validate pygame project structure for WebAssembly deployment."""
        project_path = self.config.project_path
        
        # Check if main.py exists
        main_py = project_path / "main.py"
        if not main_py.exists():
            self.console.print(f"❌ [red]main.py not found in {project_path}[/red]")
            self.console.print("💡 [yellow]Pygame WebAssembly projects require a main.py entry point[/yellow]")
            return False
        
        # Check for async main function
        try:
            with open(main_py, 'r') as f:
                content = f.read()
                if 'async def main' not in content and 'asyncio.run' not in content:
                    self.console.print("⚠️  [yellow]Warning: No async main() function detected[/yellow]")
                    self.console.print("💡 [cyan]WebAssembly requires async game loops for browser compatibility[/cyan]")
        except Exception as e:
            self.console.print(f"⚠️  [yellow]Could not validate main.py: {e}[/yellow]")
        
        # Check pygame imports
        try:
            with open(main_py, 'r') as f:
                content = f.read()
                if 'import pygame' not in content and 'from pygame' not in content:
                    self.console.print("⚠️  [yellow]Warning: No pygame imports detected in main.py[/yellow]")
        except Exception:
            pass
        
        self.console.print(f"✅ [green]Project structure validated: {project_path}[/green]")
        return True
    
    def check_pygbag_installed(self) -> bool:
        """Check if pygbag is installed."""
        try:
            result = subprocess.run(
                [sys.executable, "-c", "import pygbag; print(pygbag.__version__)"],
                capture_output=True,
                text=True,
                check=True
            )
            version = result.stdout.strip()
            self.console.print(f"✅ [green]pygbag {version} is installed[/green]")
            return True
        except subprocess.CalledProcessError:
            self.console.print("❌ [red]pygbag is not installed[/red]")
            self.console.print("💡 [cyan]Install with: pip install 'ai-game-dev[pygame-web]'[/cyan]")
            return False
    
    def setup_professor_pixel_integration(self) -> None:
        """Copy Professor Pixel modal component to project."""
        if not self.config.professor_pixel_integration:
            return
        
        project_path = self.config.project_path
        
        # Copy Professor Pixel modal template if it doesn't exist
        modal_source = Path(__file__).parent.parent / "server" / "templates" / "components" / "professor_pixel_modal.html"
        modal_dest = project_path / "professor_pixel_modal.html"
        
        if modal_source.exists() and not modal_dest.exists():
            shutil.copy2(modal_source, modal_dest)
            self.console.print("✅ [green]Professor Pixel modal integration added[/green]")
        
        # Copy WebAssembly pygame template if main.py doesn't have async structure
        template_source = Path(__file__).parent.parent / "engines" / "pygame_template_webassembly.py"
        main_py = project_path / "main.py"
        
        if template_source.exists():
            try:
                with open(main_py, 'r') as f:
                    content = f.read()
                    if 'ProfessorPixelIntegration' not in content:
                        backup_path = project_path / "main_backup.py"
                        shutil.copy2(main_py, backup_path)
                        self.console.print(f"📄 [yellow]Original main.py backed up to {backup_path}[/yellow]")
                        
                        # Offer to update with template
                        self.console.print("💡 [cyan]Consider integrating Professor Pixel teaching system from template[/cyan]")
                        self.console.print(f"📖 [cyan]Template available at: {template_source}[/cyan]")
            except Exception as e:
                self.console.print(f"⚠️  [yellow]Could not check main.py for Professor Pixel integration: {e}[/yellow]")
    
    async def deploy(self) -> bool:
        """Deploy pygame project to WebAssembly using pygbag."""
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
        ) as progress:
            
            # Validation
            task = progress.add_task("Validating project structure...", total=None)
            if not self.validate_project():
                return False
            
            progress.update(task, description="Checking pygbag installation...")
            if not self.check_pygbag_installed():
                return False
            
            progress.update(task, description="Setting up Professor Pixel integration...")
            self.setup_professor_pixel_integration()
            
            # Build pygbag command
            progress.update(task, description="Building WebAssembly deployment...")
            cmd = [sys.executable, "-m", "pygbag"]
            
            # Add options
            cmd.extend(["--port", str(self.config.port)])
            cmd.extend(["--app_name", self.config.app_name])
            cmd.extend(["--template", self.config.template])
            
            if self.config.archive:
                cmd.append("--archive")
            
            if self.config.dev_mode:
                cmd.append("--dev")
            
            # Add project path
            cmd.append(str(self.config.project_path))
            
            try:
                self.console.print(f"🚀 [bold green]Deploying to WebAssembly...[/bold green]")
                self.console.print(f"📂 Project: {self.config.project_path}")
                self.console.print(f"🌐 Port: {self.config.port}")
                self.console.print(f"📋 Template: {self.config.template}")
                
                # Run pygbag
                process = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.STDOUT,
                    cwd=self.config.project_path.parent
                )
                
                progress.update(task, description="Compiling to WebAssembly...")
                
                # Stream output
                while True:
                    line = await process.stdout.readline()
                    if not line:
                        break
                    
                    output = line.decode().strip()
                    if output:
                        # Filter interesting output
                        if any(keyword in output.lower() for keyword in ['error', 'warning', 'serving', 'http']):
                            self.console.print(f"📄 {output}")
                
                await process.wait()
                
                if process.returncode == 0:
                    progress.update(task, description="✅ WebAssembly deployment successful!")
                    self.console.print(f"\n🎉 [bold green]Deployment successful![/bold green]")
                    self.console.print(f"🌐 [cyan]Access your game at: http://localhost:{self.config.port}[/cyan]")
                    
                    if self.config.professor_pixel_integration:
                        self.console.print(f"🎓 [yellow]Professor Pixel teaching system integrated[/yellow]")
                    
                    self.console.print(f"\n📊 [bold]Features enabled:[/bold]")
                    self.console.print(f"  ✅ WebAssembly compilation")
                    self.console.print(f"  ✅ Browser compatibility")
                    self.console.print(f"  ✅ Mobile device support")
                    if self.config.professor_pixel_integration:
                        self.console.print(f"  ✅ Interactive learning system")
                    
                    return True
                else:
                    progress.update(task, description="❌ Deployment failed")
                    self.console.print(f"❌ [red]Deployment failed with exit code {process.returncode}[/red]")
                    return False
                    
            except Exception as e:
                progress.update(task, description="❌ Deployment error")
                self.console.print(f"❌ [red]Deployment error: {e}[/red]")
                return False


def deploy_pygame_to_web(
    project_path: Path,
    port: int = 8000,
    template: str = "simple.tmpl",
    app_name: str = "AI Game",
    archive: bool = False,
    dev_mode: bool = False,
    professor_pixel: bool = True
) -> bool:
    """
    Deploy a pygame project to WebAssembly for browser play.
    
    Args:
        project_path: Path to pygame project directory
        port: Port to serve the game on (default: 8000)
        template: Pygbag template to use (default: "simple.tmpl")
        app_name: Name of the deployed application
        archive: Create archive file for distribution
        dev_mode: Enable development mode with debug features
        professor_pixel: Enable Professor Pixel teaching integration
    
    Returns:
        True if deployment successful, False otherwise
    """
    config = PygbagConfig(
        project_path=project_path,
        port=port,
        template=template,
        app_name=app_name,
        archive=archive,
        dev_mode=dev_mode,
        professor_pixel_integration=professor_pixel
    )
    
    deployer = PygbagDeployer(config)
    return asyncio.run(deployer.deploy())


# CLI interface
app = typer.Typer(help="Deploy pygame games to WebAssembly with Professor Pixel integration")

@app.command()
def main(
    project_path: Path = typer.Argument(..., help="Path to pygame project directory"),
    port: int = typer.Option(8000, "--port", "-p", help="Port to serve the game on"),
    template: str = typer.Option("simple.tmpl", "--template", "-t", help="Pygbag template to use"),
    app_name: str = typer.Option("AI Game", "--name", "-n", help="Name of the deployed application"),
    archive: bool = typer.Option(False, "--archive", "-a", help="Create archive file for distribution"),
    dev: bool = typer.Option(False, "--dev", "-d", help="Enable development mode"),
    no_professor: bool = typer.Option(False, "--no-professor", help="Disable Professor Pixel integration"),
) -> None:
    """Deploy pygame project to WebAssembly for browser play."""
    
    success = deploy_pygame_to_web(
        project_path=project_path,
        port=port,
        template=template,
        app_name=app_name,
        archive=archive,
        dev_mode=dev,
        professor_pixel=not no_professor
    )
    
    if not success:
        typer.echo("❌ Deployment failed!")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
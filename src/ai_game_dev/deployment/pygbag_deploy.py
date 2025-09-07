"""
Advanced Pygbag WebAssembly deployment system for pygame games.
Provides seamless web deployment with Professor Pixel integration.
Features rich console output, progress tracking, and comprehensive CLI.
"""

import asyncio
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional, Dict, Any, List
from dataclasses import dataclass

try:
    import typer
    from rich.console import Console
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.panel import Panel
    from rich.table import Table
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    typer = None
    Console = None
    Progress = None
    SpinnerColumn = None
    TextColumn = None
    Panel = None
    Table = None

console = Console() if RICH_AVAILABLE else None

@dataclass
class PygbagConfig:
    """Advanced configuration for pygbag WebAssembly deployment."""
    
    project_path: Path
    port: int = 8000
    template: str = "simple.tmpl"
    app_name: str = "AI Game"
    archive: bool = False
    dev_mode: bool = False
    professor_pixel_integration: bool = True
    optimization_level: str = "O2"
    memory_size: int = 512
    stack_size: int = 32
    enable_threading: bool = False
    enable_audio: bool = True
    
    def __post_init__(self):
        self.project_path = Path(self.project_path).resolve()


class PygbagDeployer:
    """Advanced pygame to WebAssembly deployment system with rich UI."""
    
    def __init__(self, config: PygbagConfig):
        self.config = config
        self.console = Console() if RICH_AVAILABLE else None
    
    def validate_project(self) -> bool:
        """Validate pygame project structure for WebAssembly deployment."""
        project_path = self.config.project_path
        
        if self.console:
            self.console.print(f"🔍 Validating project: {project_path}")
        
        # Check main.py exists
        main_py = project_path / "main.py"
        if not main_py.exists():
            if self.console:
                self.console.print(f"❌ main.py not found in {project_path}", style="red")
            return False
        
        # Check for pygame imports
        try:
            with open(main_py, 'r') as f:
                content = f.read()
                if 'import pygame' not in content and 'from pygame' not in content:
                    if self.console:
                        self.console.print("⚠️  No pygame imports found in main.py", style="yellow")
        except Exception as e:
            if self.console:
                self.console.print(f"⚠️  Could not read main.py: {e}", style="yellow")
        
        if self.console:
            self.console.print("✅ Project validation passed", style="green")
        return True
    
    def check_dependencies(self) -> bool:
        """Check if pygbag and dependencies are installed."""
        if self.console:
            self.console.print("🔧 Checking dependencies...")
        
        try:
            result = subprocess.run(
                [sys.executable, "-c", "import pygbag"],
                check=True,
                capture_output=True,
                text=True
            )
            if self.console:
                self.console.print("✅ pygbag is available", style="green")
            return True
        except subprocess.CalledProcessError:
            if self.console:
                self.console.print("❌ pygbag not installed", style="red")
                self.console.print("Install with: pip install 'ai-game-dev[pygame-web]'", style="blue")
            return False
        except Exception as e:
            if self.console:
                self.console.print(f"❌ Error checking dependencies: {e}", style="red")
            return False
    
    def build_command(self) -> List[str]:
        """Build the pygbag deployment command with all options."""
        cmd = [
            sys.executable, "-m", "pygbag",
            "--port", str(self.config.port),
            "--app_name", self.config.app_name,
            "--template", self.config.template
        ]
        
        if self.config.archive:
            cmd.append("--archive")
        if self.config.dev_mode:
            cmd.append("--dev")
        if self.config.enable_audio:
            cmd.append("--audio")
        if self.config.enable_threading:
            cmd.append("--threading")
        
        cmd.extend([
            "--memory", str(self.config.memory_size),
            "--stack", str(self.config.stack_size),
            "--optimization", self.config.optimization_level
        ])
        
        cmd.append(str(self.config.project_path))
        return cmd
    
    async def deploy_async(self) -> bool:
        """Deploy the pygame project to WebAssembly asynchronously."""
        if not self.validate_project():
            return False
        
        if not self.check_dependencies():
            return False
        
        cmd = self.build_command()
        
        if self.console:
            # Create deployment info table
            table = Table(title="🚀 WebAssembly Deployment Configuration")
            table.add_column("Setting", style="cyan")
            table.add_column("Value", style="green")
            
            table.add_row("Project Path", str(self.config.project_path))
            table.add_row("Port", str(self.config.port))
            table.add_row("App Name", self.config.app_name)
            table.add_row("Template", self.config.template)
            table.add_row("Memory Size", f"{self.config.memory_size}MB")
            table.add_row("Optimization", self.config.optimization_level)
            table.add_row("Professor Pixel", "✅" if self.config.professor_pixel_integration else "❌")
            
            self.console.print(table)
            self.console.print(f"🌐 Will be available at: http://localhost:{self.config.port}")
        
        try:
            if RICH_AVAILABLE and self.console:
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=self.console
                ) as progress:
                    task = progress.add_task("Compiling to WebAssembly...", total=None)
                    
                    process = await asyncio.create_subprocess_exec(
                        *cmd,
                        cwd=self.config.project_path.parent,
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE
                    )
                    
                    stdout, stderr = await process.communicate()
                    
                    if process.returncode == 0:
                        progress.update(task, description="✅ Deployment successful!")
                        if self.config.professor_pixel_integration:
                            self.console.print(Panel(
                                "🎓 Professor Pixel integration enabled!\n"
                                "Your game now supports interactive learning breakpoints.",
                                title="Educational Features Ready",
                                style="green"
                            ))
                        return True
                    else:
                        progress.update(task, description="❌ Deployment failed")
                        self.console.print(f"Error: {stderr.decode()}", style="red")
                        return False
            else:
                # Fallback without Rich
                print("🚀 Deploying to WebAssembly...")
                result = subprocess.run(cmd, cwd=self.config.project_path.parent)
                return result.returncode == 0
                
        except Exception as e:
            if self.console:
                self.console.print(f"❌ Deployment failed: {e}", style="red")
            else:
                print(f"❌ Deployment failed: {e}")
            return False
    
    def deploy(self) -> bool:
        """Synchronous wrapper for async deployment."""
        return asyncio.run(self.deploy_async())


def deploy_pygame_to_web(
    project_path: Path,
    port: int = 8000,
    template: str = "simple.tmpl",
    app_name: str = "AI Game",
    archive: bool = False,
    dev_mode: bool = False,
    professor_pixel: bool = True,
    optimization: str = "O2",
    memory_size: int = 512
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
        optimization: Optimization level (O0, O1, O2, O3)
        memory_size: Memory size in MB (default: 512)
    
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
        professor_pixel_integration=professor_pixel,
        optimization_level=optimization,
        memory_size=memory_size
    )
    
    deployer = PygbagDeployer(config)
    return deployer.deploy()


# CLI Application
if RICH_AVAILABLE and typer:
    app = typer.Typer(
        name="pygbag-deploy",
        help="Advanced WebAssembly deployment for pygame games with Professor Pixel integration"
    )
    
    @app.command()
    def deploy(
        project_path: Path = typer.Argument(..., help="Path to pygame project directory"),
        port: int = typer.Option(8000, "--port", "-p", help="Port to serve the game on"),
        template: str = typer.Option("simple.tmpl", "--template", "-t", help="Pygbag template to use"),
        app_name: str = typer.Option("AI Game", "--name", "-n", help="Name of the deployed application"),
        archive: bool = typer.Option(False, "--archive", "-a", help="Create archive file for distribution"),
        dev_mode: bool = typer.Option(False, "--dev", "-d", help="Enable development mode"),
        professor_pixel: bool = typer.Option(True, "--professor-pixel/--no-professor-pixel", help="Enable Professor Pixel integration"),
        optimization: str = typer.Option("O2", "--optimization", "-O", help="Optimization level (O0, O1, O2, O3)"),
        memory_size: int = typer.Option(512, "--memory", "-m", help="Memory size in MB")
    ):
        """Deploy a pygame project to WebAssembly for browser play."""
        success = deploy_pygame_to_web(
            project_path=project_path,
            port=port,
            template=template,
            app_name=app_name,
            archive=archive,
            dev_mode=dev_mode,
            professor_pixel=professor_pixel,
            optimization=optimization,
            memory_size=memory_size
        )
        
        if not success:
            raise typer.Exit(1)
    
    def main():
        """CLI entry point."""
        app()

else:
    def main():
        """Fallback CLI when Rich/Typer not available."""
        import sys
        
        if len(sys.argv) < 2:
            print("Usage: pygbag-deploy <project_path> [--port 8000]")
            return
        
        project_path = Path(sys.argv[1])
        port = 8000
        
        if "--port" in sys.argv and len(sys.argv) > sys.argv.index("--port") + 1:
            port = int(sys.argv[sys.argv.index("--port") + 1])
        
        success = deploy_pygame_to_web(project_path, port=port)
        if not success:
            sys.exit(1)


if __name__ == "__main__":
    main()
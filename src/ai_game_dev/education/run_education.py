"""
Educational Server for AI Game Development
Runs a separate educational web interface with Professor Pixel
"""

import typer
import uvicorn
from pathlib import Path

from ai_game_dev.education.education_server import create_education_app


def main(
    host: str = typer.Option("0.0.0.0", help="Host to bind to"),
    port: int = typer.Option(5001, help="Port to bind to"),
    reload: bool = typer.Option(True, help="Enable auto-reload"),
):
    """Start the AI Game Development Education Server."""
    
    typer.echo("🎓 Starting AI Game Development Education Server...")
    typer.echo(f"📚 Professor Pixel's Learning Platform")
    typer.echo(f"🌐 Server will be available at http://{host}:{port}")
    typer.echo(f"🎮 Learn Python game development with real examples!")
    
    app = create_education_app()
    
    uvicorn.run(
        app,
        host=host,
        port=port,
        reload=reload,
        reload_dirs=["src/ai_game_dev/education"] if reload else None
    )


if __name__ == "__main__":
    typer.run(main)
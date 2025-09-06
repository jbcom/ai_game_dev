"""Main CLI interface using Textual for interactive game development."""

from typing import Any, Optional
import asyncio
from pathlib import Path

try:
    from textual.app import App, ComposeResult
    from textual.containers import Container, Horizontal, Vertical
    from textual.widgets import (
        Header, Footer, Button, Input, Select, TextArea, 
        Static, TabbedContent, TabPane, Tree, Log
    )
    from textual.binding import Binding
    from textual.screen import Screen
    from rich.console import Console
    from rich.syntax import Syntax
    from rich.table import Table
    TEXTUAL_AVAILABLE = True
except ImportError:
    TEXTUAL_AVAILABLE = False
    # Fallback classes
    class App: pass
    class ComposeResult: pass
    class Container: pass


class GameProjectCreator(Screen):
    """Screen for creating new game projects."""
    
    BINDINGS = [
        Binding("escape", "app.pop_screen", "Back"),
        Binding("ctrl+s", "create_project", "Create Project"),
    ]
    
    def compose(self) -> ComposeResult:
        """Create the UI layout."""
        yield Header()
        
        with Container(id="main"):
            with Vertical(id="form"):
                yield Static("🎮 Create New Game Project", classes="title")
                
                yield Input(placeholder="Game Title", id="title")
                yield Select([
                    ("platformer", "2D Platformer"),
                    ("rpg", "Role-Playing Game"),
                    ("puzzle", "Puzzle Game"),
                    ("shooter", "Space Shooter"),
                    ("adventure", "Adventure Game"),
                ], prompt="Select Genre", id="genre")
                
                yield Select([
                    ("pygame", "Pygame (Python)"),
                    ("bevy", "Bevy (Rust)"),
                    ("godot", "Godot (GDScript)"),
                    ("arcade", "Arcade (Python)"),
                ], prompt="Select Engine", id="engine")
                
                yield Select([
                    ("simple", "Simple"),
                    ("intermediate", "Intermediate"),
                    ("complex", "Complex"),
                ], prompt="Complexity Level", id="complexity")
                
                yield TextArea(
                    placeholder="Describe your game concept...",
                    id="description"
                )
                
                with Horizontal(id="buttons"):
                    yield Button("Create Project", variant="primary", id="create")
                    yield Button("Cancel", variant="default", id="cancel")
        
        yield Footer()
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "create":
            self.action_create_project()
        elif event.button.id == "cancel":
            self.app.pop_screen()
    
    def action_create_project(self) -> None:
        """Create a new game project."""
        # Get form values
        title = self.query_one("#title", Input).value
        genre = self.query_one("#genre", Select).value
        engine = self.query_one("#engine", Select).value
        complexity = self.query_one("#complexity", Select).value
        description = self.query_one("#description", TextArea).text
        
        if not title:
            self.notify("Please enter a game title", severity="error")
            return
        
        # Create project specification
        project_spec = {
            "title": title,
            "genre": genre,
            "engine": engine,
            "complexity": complexity,
            "description": description
        }
        
        # Notify parent app
        self.app.project_created(project_spec)
        self.app.pop_screen()


class AssetGenerator(Screen):
    """Screen for generating game assets."""
    
    BINDINGS = [
        Binding("escape", "app.pop_screen", "Back"),
        Binding("ctrl+g", "generate_assets", "Generate Assets"),
    ]
    
    def compose(self) -> ComposeResult:
        """Create the UI layout.""" 
        yield Header()
        
        with Container(id="main"):
            with Vertical(id="form"):
                yield Static("🎨 Generate Game Assets", classes="title")
                
                yield Input(placeholder="Game Description", id="description")
                
                yield Select([
                    ("sprites", "Sprites & Characters"),
                    ("ui", "User Interface"),
                    ("backgrounds", "Backgrounds"),
                    ("sfx", "Sound Effects"),
                    ("music", "Background Music"),
                ], prompt="Asset Types", id="asset_types", allow_blank=False)
                
                yield Select([
                    ("pixel_art", "Pixel Art"),
                    ("hand_drawn", "Hand Drawn"),
                    ("realistic", "Realistic"),
                    ("stylized", "Stylized"),
                    ("minimalist", "Minimalist"),
                ], prompt="Art Style", id="art_style")
                
                with Horizontal(id="buttons"):
                    yield Button("Generate Assets", variant="primary", id="generate")
                    yield Button("Cancel", variant="default", id="cancel")
        
        yield Footer()
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "generate":
            self.action_generate_assets()
        elif event.button.id == "cancel":
            self.app.pop_screen()
    
    def action_generate_assets(self) -> None:
        """Generate game assets."""
        description = self.query_one("#description", Input).value
        asset_types = self.query_one("#asset_types", Select).value
        art_style = self.query_one("#art_style", Select).value
        
        if not description:
            self.notify("Please enter a game description", severity="error")
            return
        
        asset_spec = {
            "description": description,
            "asset_types": [asset_types] if asset_types else [],
            "art_style": art_style
        }
        
        # Notify parent app
        self.app.assets_requested(asset_spec)
        self.app.pop_screen()


class GameDevCLI(App):
    """Main CLI application for AI Game Development."""
    
    CSS = """
    .title {
        text-align: center;
        margin: 1 0;
        text-style: bold;
        color: $primary;
    }
    
    #main {
        height: 100%;
        padding: 1;
    }
    
    #form {
        width: 80%;
        margin: 0 auto;
        padding: 2;
        border: solid $primary;
        border-title-color: $primary;
        border-title-align: center;
    }
    
    #buttons {
        align: center;
        margin-top: 1;
    }
    
    Button {
        margin: 0 1;
    }
    
    .status-panel {
        height: 30%;
        border: solid $accent;
        margin-top: 1;
    }
    """
    
    TITLE = "AI Game Development CLI"
    SUB_TITLE = "Revolutionary AI-powered game creation"
    
    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("n", "new_project", "New Project"),
        Binding("a", "generate_assets", "Generate Assets"),
        Binding("h", "help", "Help"),
    ]
    
    def __init__(self):
        super().__init__()
        self.console = Console()
        self.current_project: Optional[dict[str, Any]] = None
    
    def compose(self) -> ComposeResult:
        """Create the main UI layout."""
        yield Header()
        
        with Container(id="main"):
            with TabbedContent():
                with TabPane("Dashboard", id="dashboard"):
                    yield Static("🚀 Welcome to AI Game Development", classes="title")
                    
                    with Vertical():
                        yield Static("Choose an action to get started:")
                        
                        with Horizontal(id="main-buttons"):
                            yield Button("🎮 New Project", id="new_project")
                            yield Button("🎨 Generate Assets", id="generate_assets") 
                            yield Button("🔧 Settings", id="settings")
                        
                        with Container(classes="status-panel"):
                            yield Log(id="status_log")
                
                with TabPane("Projects", id="projects"):
                    yield Tree("Projects", id="project_tree")
                
                with TabPane("Assets", id="assets"):
                    yield Static("Asset management coming soon...")
        
        yield Footer()
    
    def on_mount(self) -> None:
        """Initialize the application."""
        self.log_status("AI Game Development CLI ready")
        self.log_status("Press 'n' for new project, 'a' for assets, 'q' to quit")
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "new_project":
            self.action_new_project()
        elif event.button.id == "generate_assets":
            self.action_generate_assets()
        elif event.button.id == "settings":
            self.notify("Settings panel coming soon!")
    
    def action_new_project(self) -> None:
        """Launch new project creation screen."""
        self.push_screen(GameProjectCreator())
    
    def action_generate_assets(self) -> None:
        """Launch asset generation screen.""" 
        self.push_screen(AssetGenerator())
    
    def action_help(self) -> None:
        """Show help information."""
        help_text = """
🎮 AI Game Development CLI Help

Keyboard Shortcuts:
• n - Create new project
• a - Generate assets
• h - Show this help
• q - Quit application

Navigation:
• Tab/Shift+Tab - Navigate between elements
• Enter - Activate buttons
• Escape - Go back/cancel

Getting Started:
1. Press 'n' to create a new game project
2. Fill in the game details and select engine
3. Use 'a' to generate assets for your game

For more information, visit: https://ai-game-dev.readthedocs.io
        """
        
        self.notify(help_text, title="Help", timeout=10)
    
    def project_created(self, project_spec: dict[str, Any]) -> None:
        """Handle project creation."""
        self.current_project = project_spec
        self.log_status(f"📝 Project '{project_spec['title']}' created")
        self.log_status(f"🎯 Engine: {project_spec['engine']}")
        self.log_status(f"📊 Complexity: {project_spec['complexity']}")
        
        # In a real implementation, this would trigger the AI game generation
        self.notify(f"Project '{project_spec['title']}' created successfully!", severity="success")
    
    def assets_requested(self, asset_spec: dict[str, Any]) -> None:
        """Handle asset generation request."""
        self.log_status(f"🎨 Generating assets: {asset_spec['asset_types']}")
        self.log_status(f"🖌️ Style: {asset_spec['art_style']}")
        
        # In a real implementation, this would trigger the AI asset generation
        self.notify("Asset generation started! Check status log for progress.", severity="info")
    
    def log_status(self, message: str) -> None:
        """Add a message to the status log."""
        try:
            log_widget = self.query_one("#status_log", Log)
            log_widget.write_line(message)
        except:
            # Fallback if log widget not available
            pass


def launch_cli() -> None:
    """Launch the CLI interface."""
    if not TEXTUAL_AVAILABLE:
        print("❌ CLI interface requires textual. Install with: pip install 'ai-game-dev[ui]'")
        return
    
    app = GameDevCLI()
    app.run()


if __name__ == "__main__":
    launch_cli()
"""Web portal interface using Mesop for interactive game development."""

from typing import Any, Optional
import json
from dataclasses import dataclass, field

try:
    import mesop as me
    import mesop.labs as mel
    MESOP_AVAILABLE = True
except ImportError:
    MESOP_AVAILABLE = False
    # Create dummy decorators for when mesop is not available
    def page(path: str, title: str = ""):
        def decorator(func):
            return func
        return decorator
    me = type('me', (), {'page': page})()


@dataclass
class GameProject:
    """Represents a game project."""
    title: str = ""
    genre: str = ""
    engine: str = ""
    complexity: str = ""
    description: str = ""
    status: str = "draft"
    assets: list[str] = field(default_factory=list)


@dataclass
class AppState:
    """Application state for the web portal."""
    current_page: str = "dashboard"
    projects: list[GameProject] = field(default_factory=list)
    current_project: Optional[GameProject] = None
    generation_status: str = ""
    llm_providers: list[str] = field(default_factory=lambda: ["openai", "anthropic", "google"])
    selected_provider: str = "openai"


if MESOP_AVAILABLE:
    @me.page(path="/", title="AI Game Development Portal")
    def home():
        """Main dashboard page."""
        state = me.state(AppState)
        
        with me.box(style=me.Style(
            background="#1a1a2e",
            color="white",
            padding=me.Padding.all(20),
            min_height="100vh"
        )):
            # Header
            with me.box(style=me.Style(
                display="flex",
                justify_content="space-between",
                align_items="center",
                margin=me.Margin(bottom=30),
                border_bottom="2px solid #16213e",
                padding=me.Padding(bottom=20)
            )):
                me.text(
                    "🎮 AI Game Development Portal",
                    style=me.Style(
                        font_size=32,
                        font_weight="bold",
                        color="#64ffda"
                    )
                )
                
                with me.box(style=me.Style(display="flex", gap=10)):
                    me.button(
                        "Dashboard",
                        on_click=lambda e: navigate_to("dashboard"),
                        style=button_style(state.current_page == "dashboard")
                    )
                    me.button(
                        "New Project",
                        on_click=lambda e: navigate_to("new_project"),
                        style=button_style(state.current_page == "new_project")
                    )
                    me.button(
                        "Generate Assets",
                        on_click=lambda e: navigate_to("assets"),
                        style=button_style(state.current_page == "assets")
                    )
                    me.button(
                        "Settings",
                        on_click=lambda e: navigate_to("settings"),
                        style=button_style(state.current_page == "settings")
                    )
            
            # Content area
            if state.current_page == "dashboard":
                render_dashboard(state)
            elif state.current_page == "new_project":
                render_new_project(state)
            elif state.current_page == "assets":
                render_asset_generator(state)
            elif state.current_page == "settings":
                render_settings(state)


    def render_dashboard(state: AppState):
        """Render the main dashboard."""
        me.text(
            "🚀 Welcome to AI-Powered Game Development",
            style=me.Style(font_size=24, margin=me.Margin(bottom=20))
        )
        
        # Quick stats
        with me.box(style=me.Style(
            display="grid",
            grid_template_columns="repeat(auto-fit, minmax(250px, 1fr))",
            gap=20,
            margin=me.Margin(bottom=30)
        )):
            create_stat_card("Projects Created", str(len(state.projects)), "🎮")
            create_stat_card("Active Provider", state.selected_provider.title(), "🤖")
            create_stat_card("Engine Support", "4 Engines", "⚙️")
            create_stat_card("Status", "Ready", "✅")
        
        # Recent projects
        me.text(
            "📁 Recent Projects",
            style=me.Style(font_size=20, margin=me.Margin(bottom=15))
        )
        
        if state.projects:
            for project in state.projects[-5:]:  # Show last 5 projects
                create_project_card(project)
        else:
            with me.box(style=card_style()):
                me.text(
                    "No projects yet. Create your first AI-generated game!",
                    style=me.Style(text_align="center", color="#888")
                )
                me.button(
                    "🎮 Create New Project",
                    on_click=lambda e: navigate_to("new_project"),
                    style=me.Style(
                        margin=me.Margin(top=15),
                        background="#64ffda",
                        color="black",
                        padding=me.Padding.all(10),
                        border_radius=5,
                        border="none"
                    )
                )


    def render_new_project(state: AppState):
        """Render the new project creation form."""
        me.text(
            "🎮 Create New Game Project",
            style=me.Style(font_size=24, margin=me.Margin(bottom=20))
        )
        
        with me.box(style=card_style()):
            me.text("Project Details", style=me.Style(font_size=18, margin=me.Margin(bottom=15)))
            
            me.input(
                label="Game Title",
                placeholder="Enter your game title",
                on_blur=lambda e: update_project_field("title", e.value)
            )
            
            me.select(
                label="Genre",
                options=[
                    me.SelectOption(label="2D Platformer", value="platformer"),
                    me.SelectOption(label="RPG", value="rpg"),
                    me.SelectOption(label="Puzzle Game", value="puzzle"),
                    me.SelectOption(label="Space Shooter", value="shooter"),
                    me.SelectOption(label="Adventure", value="adventure"),
                ],
                on_selection_change=lambda e: update_project_field("genre", e.value)
            )
            
            me.select(
                label="Game Engine",
                options=[
                    me.SelectOption(label="Pygame (Python)", value="pygame"),
                    me.SelectOption(label="Bevy (Rust)", value="bevy"),
                    me.SelectOption(label="Godot (GDScript)", value="godot"),
                    me.SelectOption(label="Arcade (Python)", value="arcade"),
                ],
                on_selection_change=lambda e: update_project_field("engine", e.value)
            )
            
            me.select(
                label="Complexity",
                options=[
                    me.SelectOption(label="Simple", value="simple"),
                    me.SelectOption(label="Intermediate", value="intermediate"),
                    me.SelectOption(label="Complex", value="complex"),
                ],
                on_selection_change=lambda e: update_project_field("complexity", e.value)
            )
            
            me.textarea(
                label="Game Description",
                placeholder="Describe your game concept, mechanics, and vision...",
                rows=4,
                on_blur=lambda e: update_project_field("description", e.value)
            )
            
            with me.box(style=me.Style(margin=me.Margin(top=20))):
                me.button(
                    "🚀 Generate Game",
                    on_click=create_project,
                    style=me.Style(
                        background="#64ffda",
                        color="black",
                        padding=me.Padding.all(12),
                        border_radius=5,
                        border="none",
                        margin=me.Margin(right=10)
                    )
                )
                me.button(
                    "Cancel",
                    on_click=lambda e: navigate_to("dashboard"),
                    style=me.Style(
                        background="#444",
                        color="white",
                        padding=me.Padding.all(12),
                        border_radius=5,
                        border="none"
                    )
                )


    def render_asset_generator(state: AppState):
        """Render the asset generation interface."""
        me.text(
            "🎨 Generate Game Assets",
            style=me.Style(font_size=24, margin=me.Margin(bottom=20))
        )
        
        with me.box(style=card_style()):
            me.text("Asset Generation", style=me.Style(font_size=18, margin=me.Margin(bottom=15)))
            
            me.input(
                label="Game Description",
                placeholder="Describe the game for which you need assets",
            )
            
            mel.checkbox(
                label="Asset Types",
                options=[
                    mel.CheckboxOption(label="🎭 Sprites & Characters", value="sprites"),
                    mel.CheckboxOption(label="🖼️ Backgrounds", value="backgrounds"),
                    mel.CheckboxOption(label="🎨 UI Elements", value="ui"),
                    mel.CheckboxOption(label="🔊 Sound Effects", value="sfx"),
                    mel.CheckboxOption(label="🎵 Background Music", value="music"),
                ]
            )
            
            me.select(
                label="Art Style",
                options=[
                    me.SelectOption(label="Pixel Art", value="pixel_art"),
                    me.SelectOption(label="Hand Drawn", value="hand_drawn"),
                    me.SelectOption(label="Realistic", value="realistic"),
                    me.SelectOption(label="Stylized", value="stylized"),
                    me.SelectOption(label="Minimalist", value="minimalist"),
                ]
            )
            
            me.button(
                "🎨 Generate Assets",
                on_click=generate_assets,
                style=me.Style(
                    background="#64ffda",
                    color="black",
                    padding=me.Padding.all(12),
                    border_radius=5,
                    border="none",
                    margin=me.Margin(top=20)
                )
            )


    def render_settings(state: AppState):
        """Render the settings page."""
        me.text(
            "⚙️ Settings",
            style=me.Style(font_size=24, margin=me.Margin(bottom=20))
        )
        
        with me.box(style=card_style()):
            me.text("LLM Provider", style=me.Style(font_size=18, margin=me.Margin(bottom=15)))
            
            me.select(
                label="Primary LLM Provider",
                options=[
                    me.SelectOption(label="OpenAI", value="openai"),
                    me.SelectOption(label="Anthropic Claude", value="anthropic"),
                    me.SelectOption(label="Google Gemini", value="google"),
                    me.SelectOption(label="Local (Ollama)", value="ollama"),
                ],
                value=state.selected_provider,
                on_selection_change=lambda e: update_provider(e.value)
            )
            
            me.text(
                "💡 Configure your API keys in environment variables",
                style=me.Style(color="#888", margin=me.Margin(top=10))
            )


    def create_stat_card(title: str, value: str, icon: str):
        """Create a statistics card."""
        with me.box(style=me.Style(
            background="#16213e",
            padding=me.Padding.all(20),
            border_radius=10,
            border="1px solid #64ffda"
        )):
            me.text(
                f"{icon} {title}",
                style=me.Style(color="#888", font_size=14)
            )
            me.text(
                value,
                style=me.Style(color="#64ffda", font_size=24, font_weight="bold")
            )


    def create_project_card(project: GameProject):
        """Create a project card."""
        with me.box(style=me.Style(
            background="#16213e",
            padding=me.Padding.all(15),
            border_radius=8,
            margin=me.Margin(bottom=10),
            border="1px solid #333"
        )):
            me.text(
                f"🎮 {project.title}",
                style=me.Style(font_weight="bold", margin=me.Margin(bottom=5))
            )
            me.text(
                f"Engine: {project.engine} | Genre: {project.genre} | Status: {project.status}",
                style=me.Style(color="#888", font_size=12)
            )


    def card_style():
        """Standard card styling."""
        return me.Style(
            background="#16213e",
            padding=me.Padding.all(20),
            border_radius=10,
            border="1px solid #333",
            margin=me.Margin(bottom=20)
        )


    def button_style(active: bool = False):
        """Standard button styling."""
        return me.Style(
            background="#64ffda" if active else "#333",
            color="black" if active else "white",
            padding=me.Padding.all(10),
            border_radius=5,
            border="none"
        )


    def navigate_to(page: str):
        """Navigate to a different page."""
        state = me.state(AppState)
        state.current_page = page


    def update_project_field(field: str, value: str):
        """Update a field in the current project."""
        state = me.state(AppState)
        if not state.current_project:
            state.current_project = GameProject()
        setattr(state.current_project, field, value)


    def update_provider(provider: str):
        """Update the selected LLM provider."""
        state = me.state(AppState)
        state.selected_provider = provider


    def create_project(event):
        """Create a new game project."""
        state = me.state(AppState)
        if state.current_project and state.current_project.title:
            state.current_project.status = "generating"
            state.projects.append(state.current_project)
            state.generation_status = f"Generating {state.current_project.title}..."
            state.current_project = None
            navigate_to("dashboard")


    def generate_assets(event):
        """Generate game assets."""
        state = me.state(AppState)
        state.generation_status = "Generating assets..."


class GameDevPortal:
    """Web portal for AI Game Development."""
    
    def __init__(self, host: str = "localhost", port: int = 8080):
        self.host = host
        self.port = port
    
    def run(self):
        """Run the web portal."""
        if not MESOP_AVAILABLE:
            print("❌ Web portal requires mesop. Install with: pip install 'ai-game-dev[web]'")
            return
        
        print(f"🌐 Starting AI Game Dev Portal at http://{self.host}:{self.port}")
        print("Press Ctrl+C to stop the server")
        
        # In a real implementation, this would start the Mesop server
        # me.run(host=self.host, port=self.port)


def launch_web_portal(host: str = "localhost", port: int = 8080) -> None:
    """Launch the web portal interface."""
    portal = GameDevPortal(host, port)
    portal.run()


if __name__ == "__main__":
    launch_web_portal()
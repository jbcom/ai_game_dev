"""
Mesop Web Portal for AI Game Development
Interactive web interface for generating games with AI
"""

import mesop as me
import mesop.labs as mel
from typing import List, Dict, Any
import asyncio
import json
from pathlib import Path
import sys

# Add packages to path for development
sys.path.insert(0, str(Path(__file__).parent.parent / "packages"))

try:
    from ai_game_dev import AIGameDev, GameSpec, GameType, ComplexityLevel
    from ai_game_assets import AssetGenerator
except ImportError as e:
    print(f"Please install packages: {e}")
    sys.exit(1)


@me.stateclass
class AppState:
    """Application state management."""
    
    # Game specification
    game_name: str = ""
    game_description: str = ""
    game_type: str = "2d"
    complexity: str = "beginner"
    features: List[str] = []
    
    # Generation state
    is_generating: bool = False
    generation_progress: str = ""
    generated_project: Dict[str, Any] = {}
    generated_assets: Dict[str, Any] = {}
    
    # UI state
    current_tab: str = "design"
    show_preview: bool = False
    error_message: str = ""


def header():
    """Application header with navigation."""
    with me.box(
        style=me.Style(
            background="linear-gradient(90deg, #667eea 0%, #764ba2 100%)",
            color="white",
            padding=me.Padding.all(20),
            margin=me.Margin(bottom=20)
        )
    ):
        me.text(
            "🤖 AI Game Development Studio", 
            style=me.Style(font_size=24, font_weight="bold")
        )
        me.text(
            "Generate complete games with artificial intelligence",
            style=me.Style(font_size=14, opacity=0.9, margin=me.Margin(top=8))
        )


def game_design_tab(state: AppState):
    """Game design specification interface."""
    
    with me.box(style=me.Style(max_width="800px", margin=me.Margin.symmetric(horizontal="auto"))):
        me.text("🎮 Game Design", style=me.Style(font_size=20, font_weight="bold", margin=me.Margin(bottom=20)))
        
        # Game name input
        with me.box(style=me.Style(margin=me.Margin(bottom=16))):
            me.text("Game Name", style=me.Style(font_weight="bold", margin=me.Margin(bottom=8)))
            me.input(
                value=state.game_name,
                placeholder="Enter your game name",
                on_input=on_game_name_change,
                style=me.Style(width="100%")
            )
        
        # Game description
        with me.box(style=me.Style(margin=me.Margin(bottom=16))):
            me.text("Game Description", style=me.Style(font_weight="bold", margin=me.Margin(bottom=8)))
            me.textarea(
                value=state.game_description,
                placeholder="Describe your game in detail...",
                on_input=on_game_description_change,
                rows=4,
                style=me.Style(width="100%")
            )
        
        # Game type selection
        with me.box(style=me.Style(margin=me.Margin(bottom=16))):
            me.text("Game Type", style=me.Style(font_weight="bold", margin=me.Margin(bottom=8)))
            me.radio(
                options=[
                    me.RadioOption(label="2D Game", value="2d"),
                    me.RadioOption(label="3D Game", value="3d"),
                ],
                value=state.game_type,
                on_change=on_game_type_change
            )
        
        # Complexity level
        with me.box(style=me.Style(margin=me.Margin(bottom=16))):
            me.text("Complexity", style=me.Style(font_weight="bold", margin=me.Margin(bottom=8)))
            me.select(
                options=[
                    me.SelectOption(label="Beginner", value="beginner"),
                    me.SelectOption(label="Intermediate", value="intermediate"),
                    me.SelectOption(label="Advanced", value="advanced"),
                ],
                value=state.complexity,
                on_selection_change=on_complexity_change
            )
        
        # Feature selection
        with me.box(style=me.Style(margin=me.Margin(bottom=24))):
            me.text("Features", style=me.Style(font_weight="bold", margin=me.Margin(bottom=8)))
            
            feature_options = [
                "Player movement", "Enemy AI", "Combat system", "Inventory",
                "Quests", "Multiplayer", "Procedural generation", "Physics",
                "Particle effects", "Sound effects", "Background music", "UI/HUD"
            ]
            
            for feature in feature_options:
                me.checkbox(
                    checked=feature in state.features,
                    label=feature,
                    on_change=lambda e, f=feature: on_feature_toggle(e, f),
                    style=me.Style(margin=me.Margin(bottom=4))
                )
        
        # Generate button
        if not state.is_generating:
            me.button(
                "🚀 Generate Game",
                on_click=on_generate_game,
                disabled=not (state.game_name and state.game_description),
                style=me.Style(
                    background="#4CAF50",
                    color="white",
                    padding=me.Padding.all(16),
                    border_radius=8,
                    font_size=16,
                    font_weight="bold"
                )
            )
        else:
            me.progress_bar(value=50)
            me.text(f"🔄 {state.generation_progress}", style=me.Style(margin=me.Margin(top=8)))


def generation_results_tab(state: AppState):
    """Display generation results."""
    
    if not state.generated_project:
        with me.box(style=me.Style(text_align="center", padding=me.Padding.all(40))):
            me.text("No game generated yet", style=me.Style(color="gray", font_size=18))
            me.text("Use the Design tab to create your game", style=me.Style(color="gray", margin=me.Margin(top=8)))
        return
    
    with me.box(style=me.Style(max_width="800px", margin=me.Margin.symmetric(horizontal="auto"))):
        me.text("🎉 Generated Game", style=me.Style(font_size=20, font_weight="bold", margin=me.Margin(bottom=20)))
        
        # Project summary
        with me.box(style=me.Style(
            background="#f5f5f5",
            padding=me.Padding.all(16),
            border_radius=8,
            margin=me.Margin(bottom=20)
        )):
            me.text(f"Game: {state.game_name}", style=me.Style(font_weight="bold", font_size=16))
            me.text(f"Type: {state.game_type.upper()}", style=me.Style(margin=me.Margin(top=4)))
            me.text(f"Complexity: {state.complexity.title()}", style=me.Style(margin=me.Margin(top=4)))
            me.text(f"Features: {', '.join(state.features)}", style=me.Style(margin=me.Margin(top=4)))
        
        # Generated files
        me.text("📁 Generated Files", style=me.Style(font_weight="bold", font_size=16, margin=me.Margin(bottom=12)))
        
        project = state.generated_project
        files = [
            ("main.py", project.get("main_py", "")),
            ("game.py", project.get("game_py", "")),
            ("player.py", project.get("player_py", "")),
            ("constants.py", project.get("constants_py", "")),
            ("requirements.txt", project.get("requirements_txt", ""))
        ]
        
        for filename, content in files:
            if content:
                with me.box(style=me.Style(margin=me.Margin(bottom=16))):
                    me.text(filename, style=me.Style(font_weight="bold", margin=me.Margin(bottom=4)))
                    me.code(
                        content[:500] + ("..." if len(content) > 500 else ""),
                        language="python"
                    )
        
        # Download button
        me.button(
            "📥 Download Project",
            on_click=on_download_project,
            style=me.Style(
                background="#2196F3",
                color="white",
                padding=me.Padding.all(12),
                border_radius=8
            )
        )


def assets_tab(state: AppState):
    """Asset generation and management."""
    
    with me.box(style=me.Style(max_width="800px", margin=me.Margin.symmetric(horizontal="auto"))):
        me.text("🎨 Game Assets", style=me.Style(font_size=20, font_weight="bold", margin=me.Margin(bottom=20)))
        
        if not state.generated_assets:
            me.text("Generate a game first to create assets", style=me.Style(color="gray"))
            return
        
        # Asset grid
        assets = state.generated_assets
        
        for asset_name, asset_data in assets.items():
            with me.box(style=me.Style(
                border="1px solid #ddd",
                border_radius=8,
                padding=me.Padding.all(16),
                margin=me.Margin(bottom=16)
            )):
                me.text(asset_name.replace("_", " ").title(), style=me.Style(font_weight="bold"))
                me.text(f"Type: {asset_data.get('type', 'Unknown')}")
                
                if asset_data.get("preview_url"):
                    me.image(
                        src=asset_data["preview_url"],
                        style=me.Style(max_width="200px", border_radius=4, margin=me.Margin(top=8))
                    )


def navigation_tabs(state: AppState):
    """Navigation tab interface."""
    
    tabs = [
        ("design", "🎮 Design"),
        ("results", "🎉 Results"),
        ("assets", "🎨 Assets"),
    ]
    
    with me.box(style=me.Style(
        display="flex",
        border_bottom="1px solid #ddd",
        margin=me.Margin(bottom=20)
    )):
        for tab_id, tab_label in tabs:
            me.button(
                tab_label,
                on_click=lambda e, t=tab_id: on_tab_change(e, t),
                style=me.Style(
                    background="transparent" if state.current_tab != tab_id else "#f0f0f0",
                    border="none",
                    padding=me.Padding.symmetric(horizontal=20, vertical=12),
                    cursor="pointer"
                )
            )


@me.page(path="/")
def main_page():
    """Main application page."""
    
    state = me.state(AppState)
    
    header()
    navigation_tabs(state)
    
    # Error display
    if state.error_message:
        with me.box(style=me.Style(
            background="#ffebee",
            color="#c62828",
            padding=me.Padding.all(12),
            border_radius=4,
            margin=me.Margin(bottom=20)
        )):
            me.text(f"❌ {state.error_message}")
    
    # Tab content
    if state.current_tab == "design":
        game_design_tab(state)
    elif state.current_tab == "results":
        generation_results_tab(state)
    elif state.current_tab == "assets":
        assets_tab(state)


# Event handlers
def on_game_name_change(e: me.InputEvent):
    state = me.state(AppState)
    state.game_name = e.value


def on_game_description_change(e: me.InputEvent):
    state = me.state(AppState)
    state.game_description = e.value


def on_game_type_change(e: me.RadioChangeEvent):
    state = me.state(AppState)
    state.game_type = e.value


def on_complexity_change(e: me.SelectChangeEvent):
    state = me.state(AppState)
    state.complexity = e.value


def on_feature_toggle(e: me.CheckboxChangeEvent, feature: str):
    state = me.state(AppState)
    if e.checked and feature not in state.features:
        state.features.append(feature)
    elif not e.checked and feature in state.features:
        state.features.remove(feature)


def on_tab_change(e: me.ClickEvent, tab_id: str):
    state = me.state(AppState)
    state.current_tab = tab_id


def on_generate_game(e: me.ClickEvent):
    """Generate game using AI."""
    state = me.state(AppState)
    
    state.is_generating = True
    state.error_message = ""
    state.generation_progress = "Initializing AI systems..."
    
    try:
        # Create game specification
        game_type = GameType.TWO_DIMENSIONAL if state.game_type == "2d" else GameType.THREE_DIMENSIONAL
        complexity = getattr(ComplexityLevel, state.complexity.upper())
        
        spec = GameSpec(
            name=state.game_name,
            description=state.game_description,
            game_type=game_type,
            features=state.features,
            complexity=complexity
        )
        
        # Initialize AI systems
        state.generation_progress = "Generating game project..."
        game_dev = AIGameDev()
        
        # Generate project (this would be async in real implementation)
        state.generation_progress = "Creating game files..."
        project = game_dev.generate_project(spec)
        
        # Generate assets
        state.generation_progress = "Generating game assets..."
        asset_gen = AssetGenerator()
        assets = asset_gen.generate_game_assets(spec)
        
        # Store results
        state.generated_project = project.__dict__ if hasattr(project, '__dict__') else {}
        state.generated_assets = assets
        
        # Switch to results tab
        state.current_tab = "results"
        state.generation_progress = "✅ Generation complete!"
        
    except Exception as e:
        state.error_message = f"Generation failed: {str(e)}"
    
    finally:
        state.is_generating = False


def on_download_project(e: me.ClickEvent):
    """Download the generated project."""
    state = me.state(AppState)
    
    if state.generated_project:
        # In a real implementation, this would create a downloadable zip file
        # For now, we'll just show the JSON representation
        project_json = json.dumps(state.generated_project, indent=2)
        print("Project would be downloaded:")
        print(project_json)


if __name__ == "__main__":
    me.run(
        main_page,
        host="0.0.0.0",
        port=5000,
        debug=True
    )
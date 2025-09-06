"""
HTMY web interface for AI Game Development.
Modern web UI using HTMX, TailwindCSS, and DaisyUI.
"""
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Annotated, Optional, List

from fastapi import Depends, FastAPI, Request, Form
from fastapi.responses import HTMLResponse

from htmy import Component, ComponentType, Context, Renderer, component, html, is_component_sequence

# Import our core functionality
from ai_game_dev.engines import engine_manager, generate_for_engine, get_supported_engines


@dataclass
class GameDevUser:
    """User data model for the game development interface."""
    name: str = "Game Developer"
    preferred_theme: str = "dark"


@dataclass
class AppState:
    """Application state for game development."""
    current_project: Optional[str] = None
    last_generation_result: Optional[str] = None
    is_generating: bool = False


def make_htmy_context(request: Request) -> Context:
    """Creates the base htmy context for rendering."""
    return {
        Request: request, 
        GameDevUser: GameDevUser(),
        AppState: AppState()
    }


RendererFunction = Callable[[Component], Awaitable[HTMLResponse]]


def render(request: Request) -> RendererFunction:
    """FastAPI dependency that returns an htmy renderer function."""

    async def exec(component: Component) -> HTMLResponse:
        renderer = Renderer(make_htmy_context(request))
        return HTMLResponse(await renderer.render(component))

    return exec


DependsRenderFunc = Annotated[RendererFunction, Depends(render)]


@component
def page(content: ComponentType, context: Context) -> Component:
    """
    Main page layout component with game development styling.
    """
    user: GameDevUser = context[GameDevUser]
    return (
        html.DOCTYPE.html,
        html.html(
            html.head(
                html.title("AI Game Development Portal"),
                html.meta.charset(),
                html.meta.viewport(),
                # TailwindCSS and DaisyUI
                html.script(src="https://cdn.tailwindcss.com"),
                html.link.css("https://cdn.jsdelivr.net/npm/daisyui@4.12.11/dist/full.min.css"),
                # HTMX for interactivity
                html.script(src="https://unpkg.com/htmx.org@2.0.2"),
                # Custom styles
                html.style("""
                    .game-dev-bg { background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); }
                    .glow { box-shadow: 0 0 20px rgba(100, 255, 218, 0.3); }
                """),
            ),
            html.body(
                content,
                data_theme=user.preferred_theme,
                class_="min-h-screen game-dev-bg text-white",
            ),
            lang="en",
        ),
    )


@component
def header(context: Context) -> Component:
    """Header component with navigation."""
    return html.header(
        html.div(
            html.div(
                html.h1(
                    "🎮 AI Game Development Portal",
                    class_="text-3xl font-bold text-cyan-400"
                ),
                html.div(
                    html.div(
                        html.div(class_="w-2 h-2 bg-green-400 rounded-full animate-pulse"),
                        html.span("Server Online", class_="text-sm text-green-400"),
                        class_="flex items-center gap-2"
                    ),
                    class_="text-right"
                ),
                class_="flex justify-between items-center"
            ),
            class_="container mx-auto px-6 py-4"
        ),
        class_="border-b border-cyan-600/30 backdrop-blur-sm"
    )


@component
def navigation_tabs(current_tab: str, context: Context) -> Component:
    """Navigation tabs component."""
    tabs = [
        ("dashboard", "📊 Dashboard"),
        ("new_project", "🚀 New Project"),
        ("assets", "🎨 Generate Assets"),
        ("engines", "⚙️ Engines")
    ]
    
    return html.div(
        html.div(
            *[
                html.button(
                    label,
                    hx_get=f"/web/{tab_id}",
                    hx_target="#main-content",
                    hx_push_url="true",
                    class_=f"tab tab-lg {'tab-active text-cyan-400 border-cyan-400' if tab_id == current_tab else 'text-gray-300 hover:text-white'}"
                )
                for tab_id, label in tabs
            ],
            class_="tabs tabs-boxed bg-gray-800/50 backdrop-blur-sm"
        ),
        class_="container mx-auto px-6 py-4"
    )


@component
def dashboard_content(context: Context) -> Component:
    """Dashboard page content."""
    engines = get_supported_engines()
    
    return html.div(
        html.div(
            html.h2("Welcome to AI Game Development", class_="text-2xl font-bold mb-6"),
            
            # Stats cards
            html.div(
                html.div(
                    html.div(
                        html.div("🎮", class_="text-4xl mb-2"),
                        html.div("Supported Engines", class_="text-sm text-gray-400"),
                        html.div(str(len(engines)), class_="text-2xl font-bold text-cyan-400"),
                        class_="stat-title"
                    ),
                    class_="stat bg-gray-800/50 backdrop-blur-sm rounded-lg border border-gray-700"
                ),
                html.div(
                    html.div(
                        html.div("🚀", class_="text-4xl mb-2"),
                        html.div("Projects Generated", class_="text-sm text-gray-400"),
                        html.div("0", class_="text-2xl font-bold text-green-400"),
                        class_="stat-title"
                    ),
                    class_="stat bg-gray-800/50 backdrop-blur-sm rounded-lg border border-gray-700"
                ),
                html.div(
                    html.div(
                        html.div("🎨", class_="text-4xl mb-2"),
                        html.div("Assets Created", class_="text-sm text-gray-400"),
                        html.div("0", class_="text-2xl font-bold text-purple-400"),
                        class_="stat-title"
                    ),
                    class_="stat bg-gray-800/50 backdrop-blur-sm rounded-lg border border-gray-700"
                ),
                class_="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8"
            ),
            
            # Quick start
            html.div(
                html.h3("Quick Start", class_="text-xl font-bold mb-4"),
                html.div(
                    "Create your first AI-generated game project:",
                    class_="text-gray-300 mb-4"
                ),
                html.div(
                    *[
                        html.div(
                            html.div(f"{i+1}.", class_="w-8 h-8 bg-cyan-600 rounded-full flex items-center justify-center text-sm font-bold"),
                            html.span(step, class_="text-gray-300"),
                            class_="flex items-center gap-3 mb-3"
                        )
                        for i, step in enumerate([
                            "Navigate to 'New Project' tab",
                            "Describe your game idea",
                            "Select your preferred engine",
                            "Click 'Generate Project' and watch the magic happen!"
                        ])
                    ],
                ),
                class_="bg-gray-800/30 rounded-lg p-6 border border-gray-700"
            ),
            
            class_="container mx-auto px-6 py-8"
        )
    )


@component
def project_form(context: Context) -> Component:
    """New project creation form."""
    engines = get_supported_engines()
    
    return html.div(
        html.div(
            html.h2("Create New Game Project", class_="text-2xl font-bold mb-6"),
            
            html.form(
                html.div(
                    html.label("Project Description", class_="label text-gray-300"),
                    html.textarea(
                        placeholder="Describe your game idea... (e.g., A 2D platformer with pixel art graphics)",
                        name="description",
                        class_="textarea textarea-bordered w-full bg-gray-800 border-gray-600 text-white",
                        rows="3",
                        required=True
                    ),
                    class_="form-control mb-4"
                ),
                
                html.div(
                    html.div(
                        html.label("Engine", class_="label text-gray-300"),
                        html.select(
                            html.option("Select an engine...", value="", disabled=True, selected=True),
                            *[
                                html.option(f"{engine.title()} ({engine_manager.get_engine_info(engine)['language'].title()})", value=engine)
                                for engine in engines
                            ],
                            name="engine",
                            class_="select select-bordered w-full bg-gray-800 border-gray-600 text-white",
                            required=True
                        ),
                        class_="form-control"
                    ),
                    html.div(
                        html.label("Complexity", class_="label text-gray-300"),
                        html.select(
                            html.option("Beginner", value="beginner"),
                            html.option("Intermediate", value="intermediate", selected=True),
                            html.option("Advanced", value="advanced"),
                            name="complexity",
                            class_="select select-bordered w-full bg-gray-800 border-gray-600 text-white"
                        ),
                        class_="form-control"
                    ),
                    class_="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6"
                ),
                
                html.div(
                    html.label("Art Style", class_="label text-gray-300"),
                    html.select(
                        html.option("Modern", value="modern", selected=True),
                        html.option("Pixel Art", value="pixel"),
                        html.option("Minimalist", value="minimalist"),
                        html.option("Cartoonish", value="cartoon"),
                        html.option("Realistic", value="realistic"),
                        name="art_style",
                        class_="select select-bordered w-full bg-gray-800 border-gray-600 text-white"
                    ),
                    class_="form-control mb-6"
                ),
                
                html.button(
                    "🚀 Generate Project",
                    type="submit",
                    hx_post="/web/generate-project",
                    hx_target="#generation-result",
                    hx_indicator="#loading",
                    class_="btn btn-primary btn-lg w-full glow"
                ),
                
                # Loading indicator
                html.div(
                    html.div(
                        html.span(class_="loading loading-spinner loading-lg"),
                        html.span("Generating your game project...", class_="ml-4"),
                        class_="flex items-center justify-center"
                    ),
                    id="loading",
                    class_="htmx-indicator mt-6 p-4 bg-blue-900/30 rounded-lg border border-blue-600"
                ),
                
                # Result area
                html.div(id="generation-result", class_="mt-6"),
                
                class_="bg-gray-800/30 rounded-lg p-6 border border-gray-700"
            ),
            
            class_="container mx-auto px-6 py-8"
        )
    )


@component
def generation_result(success: bool, result_data: dict, context: Context) -> Component:
    """Display generation result."""
    if success:
        return html.div(
            html.div(
                html.div("✅", class_="text-4xl mb-4"),
                html.h3("Project Generated Successfully!", class_="text-xl font-bold text-green-400 mb-4"),
                html.div(
                    html.p(f"Engine: {result_data.get('engine_type', 'Unknown')}", class_="mb-2"),
                    html.p(f"Files: {', '.join(result_data.get('main_files', []))}", class_="mb-2"),
                    html.p(f"Project Path: {result_data.get('project_path', 'Not specified')}", class_="text-sm text-gray-400"),
                    class_="text-gray-300"
                ),
                class_="text-center"
            ),
            class_="bg-green-900/30 rounded-lg p-6 border border-green-600"
        )
    else:
        return html.div(
            html.div(
                html.div("❌", class_="text-4xl mb-4"),
                html.h3("Generation Failed", class_="text-xl font-bold text-red-400 mb-4"),
                html.p(f"Error: {result_data.get('error', 'Unknown error')}", class_="text-gray-300"),
                class_="text-center"
            ),
            class_="bg-red-900/30 rounded-lg p-6 border border-red-600"
        )


@component
def engines_list(context: Context) -> Component:
    """Display available engines."""
    engines = get_supported_engines()
    
    return html.div(
        html.div(
            html.h2("Available Game Engines", class_="text-2xl font-bold mb-6"),
            
            html.div(
                *[
                    html.div(
                        html.div(
                            html.div(
                                html.h3(engine.title(), class_="text-xl font-bold text-cyan-400"),
                                html.p(f"Language: {engine_manager.get_engine_info(engine)['language'].title()}", class_="text-gray-400"),
                                class_="mb-4"
                            ),
                            html.div(
                                "Ready for game development",
                                class_="badge badge-success"
                            ),
                            class_="flex justify-between items-start"
                        ),
                        class_="bg-gray-800/50 rounded-lg p-6 border border-gray-600"
                    )
                    for engine in engines
                ],
                class_="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
            ),
            
            class_="container mx-auto px-6 py-8"
        )
    )


def setup_htmy_routes(app: FastAPI):
    """Setup HTMY web interface routes."""
    
    @app.get("/web")
    @app.get("/web/")
    @app.get("/web/dashboard")
    async def web_dashboard(render: DependsRenderFunc) -> HTMLResponse:
        """Dashboard page."""
        return await render(
            page((
                header,
                navigation_tabs("dashboard"),
                dashboard_content
            ))
        )
    
    @app.get("/web/new_project")
    async def web_new_project(render: DependsRenderFunc) -> HTMLResponse:
        """New project page."""
        return await render(
            page((
                header,
                navigation_tabs("new_project"),
                project_form
            ))
        )
    
    @app.get("/web/engines")
    async def web_engines(render: DependsRenderFunc) -> HTMLResponse:
        """Engines page."""
        return await render(
            page((
                header,
                navigation_tabs("engines"),
                engines_list
            ))
        )
    
    @app.post("/web/generate-project")
    async def web_generate_project(
        render: DependsRenderFunc,
        description: str = Form(...),
        engine: str = Form(...),
        complexity: str = Form("intermediate"),
        art_style: str = Form("modern")
    ) -> HTMLResponse:
        """Handle project generation via HTMX."""
        try:
            result = await generate_for_engine(
                engine_name=engine,
                description=description,
                complexity=complexity,
                features=[],
                art_style=art_style
            )
            
            return await render(
                generation_result(True, {
                    "engine_type": result.engine_type,
                    "main_files": result.main_files,
                    "project_path": str(result.project_path) if result.project_path else None
                })
            )
        except Exception as e:
            return await render(
                generation_result(False, {"error": str(e)})
            )
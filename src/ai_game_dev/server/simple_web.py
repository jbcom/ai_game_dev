"""
Simple HTML web interface for AI Game Development.
Clean, working interface without HTMY complexity.
"""
from typing import List
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from ai_game_dev.engines import get_supported_engines, generate_for_engine


def get_base_template() -> str:
    """Get the base HTML template with TailwindCSS and DaisyUI."""
    return """
<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Game Development Portal</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://cdn.jsdelivr.net/npm/daisyui@4.12.11/dist/full.min.css" rel="stylesheet">
    <script src="https://unpkg.com/htmx.org@2.0.2"></script>
    <style>
        .game-dev-gradient { 
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%); 
        }
        .glow { box-shadow: 0 0 20px rgba(100, 255, 218, 0.3); }
        .card-glass { backdrop-filter: blur(10px); background: rgba(255,255,255,0.1); }
    </style>
</head>
<body class="min-h-screen game-dev-gradient text-white">
    <div class="navbar bg-base-100/20 backdrop-blur-sm">
        <div class="navbar-start">
            <div class="text-2xl font-bold text-primary">🎮 AI Game Dev</div>
        </div>
        <div class="navbar-center">
            <div class="tabs tabs-boxed bg-base-100/30">
                <a href="/web/dashboard" class="tab {dashboard_active}">📊 Dashboard</a>
                <a href="/web/new_project" class="tab {project_active}">🚀 New Project</a>
                <a href="/web/engines" class="tab {engines_active}">⚙️ Engines</a>
            </div>
        </div>
        <div class="navbar-end">
            <div class="flex items-center gap-2">
                <div class="w-2 h-2 bg-success rounded-full animate-pulse"></div>
                <span class="text-sm">Server Online</span>
            </div>
        </div>
    </div>
    
    <div class="container mx-auto p-6">
        {content}
    </div>
</body>
</html>"""


def get_dashboard_content() -> str:
    """Get dashboard page content."""
    engines = get_supported_engines()
    return f"""
        <div class="hero min-h-96 bg-base-200/20 rounded-box mb-8">
            <div class="hero-content text-center">
                <div class="max-w-md">
                    <h1 class="text-5xl font-bold mb-6">Welcome to AI Game Development</h1>
                    <p class="py-6 text-lg">Create games with AI assistance across multiple engines using cutting-edge language models.</p>
                    <a href="/web/new_project" class="btn btn-primary btn-lg glow">Start Creating 🚀</a>
                </div>
            </div>
        </div>
        
        <div class="stats shadow w-full bg-base-100/20 backdrop-blur-sm">
            <div class="stat place-items-center">
                <div class="stat-figure text-primary">
                    <svg class="w-8 h-8" fill="currentColor" viewBox="0 0 20 20">
                        <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
                    </svg>
                </div>
                <div class="stat-title">Supported Engines</div>
                <div class="stat-value text-primary">{len(engines)}</div>
                <div class="stat-desc">Pygame, Bevy, Godot</div>
            </div>
            
            <div class="stat place-items-center">
                <div class="stat-figure text-secondary">
                    <svg class="w-8 h-8" fill="currentColor" viewBox="0 0 20 20">
                        <path d="M13 6a3 3 0 11-6 0 3 3 0 016 0zM18 8a2 2 0 11-4 0 2 2 0 014 0zM14 15a4 4 0 00-8 0v3h8v-3z"/>
                    </svg>
                </div>
                <div class="stat-title">Projects Generated</div>
                <div class="stat-value text-secondary">0</div>
                <div class="stat-desc">Start your first project!</div>
            </div>
            
            <div class="stat place-items-center">
                <div class="stat-figure text-accent">
                    <svg class="w-8 h-8" fill="currentColor" viewBox="0 0 20 20">
                        <path d="M4 3a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V5a2 2 0 00-2-2H4z"/>
                    </svg>
                </div>
                <div class="stat-title">Assets Created</div>
                <div class="stat-value text-accent">0</div>
                <div class="stat-desc">Ready to generate</div>
            </div>
        </div>
        
        <div class="card bg-base-100/20 backdrop-blur-sm shadow-xl mt-8">
            <div class="card-body">
                <h2 class="card-title text-2xl mb-4">🚀 Quick Start Guide</h2>
                <div class="steps steps-vertical lg:steps-horizontal">
                    <div class="step step-primary">Describe your game idea</div>
                    <div class="step">Choose your engine</div>
                    <div class="step">Generate project</div>
                    <div class="step">Build and play!</div>
                </div>
            </div>
        </div>
    """


def get_project_form() -> str:
    """Get new project form."""
    engines = get_supported_engines()
    engine_map = {"pygame": "Python", "bevy": "Rust", "godot": "GDScript"}
    engine_options = "".join([
        f'<option value="{engine}">{engine.title()} ({engine_map.get(engine, "Unknown")})</option>'
        for engine in engines
    ])
    
    return f"""
        <div class="card bg-base-100/20 backdrop-blur-sm shadow-xl max-w-2xl mx-auto">
            <div class="card-body">
                <h2 class="card-title text-3xl mb-6 text-center">🚀 Create New Game Project</h2>
                
                <form hx-post="/web/generate-project" hx-target="#result" hx-indicator="#loading" class="space-y-6">
                    <div class="form-control">
                        <label class="label">
                            <span class="label-text text-lg">Project Description</span>
                        </label>
                        <textarea 
                            name="description" 
                            class="textarea textarea-bordered textarea-lg bg-base-100/50" 
                            placeholder="Describe your game idea... (e.g., A 2D platformer with pixel art graphics and retro soundtrack)"
                            rows="3" 
                            required>
                        </textarea>
                    </div>
                    
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div class="form-control">
                            <label class="label">
                                <span class="label-text">Engine</span>
                            </label>
                            <select name="engine" class="select select-bordered bg-base-100/50" required>
                                <option disabled selected>Choose an engine...</option>
                                {engine_options}
                            </select>
                        </div>
                        
                        <div class="form-control">
                            <label class="label">
                                <span class="label-text">Complexity</span>
                            </label>
                            <select name="complexity" class="select select-bordered bg-base-100/50">
                                <option value="beginner">Beginner</option>
                                <option value="intermediate" selected>Intermediate</option>
                                <option value="advanced">Advanced</option>
                            </select>
                        </div>
                    </div>
                    
                    <div class="form-control">
                        <label class="label">
                            <span class="label-text">Art Style</span>
                        </label>
                        <select name="art_style" class="select select-bordered bg-base-100/50">
                            <option value="modern" selected>Modern</option>
                            <option value="pixel">Pixel Art</option>
                            <option value="minimalist">Minimalist</option>
                            <option value="cartoon">Cartoonish</option>
                            <option value="realistic">Realistic</option>
                        </select>
                    </div>
                    
                    <div class="form-control mt-8">
                        <button type="submit" class="btn btn-primary btn-lg glow">
                            🚀 Generate Project
                        </button>
                    </div>
                </form>
                
                <div id="loading" class="htmx-indicator mt-6">
                    <div class="alert alert-info">
                        <span class="loading loading-spinner"></span>
                        Generating your game project... This may take a moment.
                    </div>
                </div>
                
                <div id="result" class="mt-6"></div>
            </div>
        </div>
    """


def get_engines_list() -> str:
    """Get engines list page."""
    engines = get_supported_engines()
    
    engine_cards = ""
    for engine in engines:
        engine_info = {
            "pygame": {"lang": "Python", "desc": "2D game development with Python", "icon": "🐍"},
            "bevy": {"lang": "Rust", "desc": "Modern ECS-based game engine", "icon": "🦀"},
            "godot": {"lang": "GDScript", "desc": "Scene-based game development", "icon": "🎯"}
        }
        
        info = engine_info.get(engine, {"lang": "Unknown", "desc": "Game engine", "icon": "🎮"})
        
        engine_cards += f"""
            <div class="card bg-base-100/20 backdrop-blur-sm shadow-xl">
                <div class="card-body">
                    <h2 class="card-title text-2xl">
                        {info['icon']} {engine.title()}
                        <div class="badge badge-primary">{info['lang']}</div>
                    </h2>
                    <p>{info['desc']}</p>
                    <div class="card-actions justify-end">
                        <div class="badge badge-success">Ready</div>
                    </div>
                </div>
            </div>
        """
    
    return f"""
        <div class="text-center mb-8">
            <h1 class="text-4xl font-bold mb-4">⚙️ Available Game Engines</h1>
            <p class="text-lg opacity-80">Choose from our supported engines to create your next game</p>
        </div>
        
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {engine_cards}
        </div>
        
        <div class="card bg-base-100/20 backdrop-blur-sm shadow-xl mt-8">
            <div class="card-body">
                <h2 class="card-title">💡 Engine Recommendations</h2>
                <div class="space-y-4">
                    <div class="flex items-start gap-4">
                        <div class="w-8 h-8 bg-primary rounded-full flex items-center justify-center text-primary-content font-bold">P</div>
                        <div>
                            <h3 class="font-bold">Pygame - Best for Beginners</h3>
                            <p class="opacity-80">Easy to learn Python-based engine perfect for 2D games and prototypes.</p>
                        </div>
                    </div>
                    <div class="flex items-start gap-4">
                        <div class="w-8 h-8 bg-secondary rounded-full flex items-center justify-center text-secondary-content font-bold">B</div>
                        <div>
                            <h3 class="font-bold">Bevy - Performance Focused</h3>
                            <p class="opacity-80">Modern Rust engine with ECS architecture for high-performance games.</p>
                        </div>
                    </div>
                    <div class="flex items-start gap-4">
                        <div class="w-8 h-8 bg-accent rounded-full flex items-center justify-center text-accent-content font-bold">G</div>
                        <div>
                            <h3 class="font-bold">Godot - Versatile & Visual</h3>
                            <p class="opacity-80">Scene-based engine with visual scripting and GDScript for rapid development.</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    """


def setup_simple_web_routes(app: FastAPI):
    """Setup simple HTML web interface routes."""
    
    @app.get("/web", response_class=HTMLResponse)
    @app.get("/web/", response_class=HTMLResponse) 
    @app.get("/web/dashboard", response_class=HTMLResponse)
    async def web_dashboard():
        """Dashboard page."""
        template = get_base_template()
        content = get_dashboard_content()
        return template.format(
            content=content,
            dashboard_active="tab-active",
            project_active="",
            engines_active=""
        )
    
    @app.get("/web/new_project", response_class=HTMLResponse)
    async def web_new_project():
        """New project page."""
        template = get_base_template()
        content = get_project_form()
        return template.format(
            content=content,
            dashboard_active="",
            project_active="tab-active",
            engines_active=""
        )
    
    @app.get("/web/engines", response_class=HTMLResponse)
    async def web_engines():
        """Engines page."""
        template = get_base_template()
        content = get_engines_list()
        return template.format(
            content=content,
            dashboard_active="",
            project_active="",
            engines_active="tab-active"
        )
    
    @app.post("/web/generate-project", response_class=HTMLResponse)
    async def web_generate_project(
        description: str = Form(...),
        engine: str = Form(...),
        complexity: str = Form("intermediate"),
        art_style: str = Form("modern")
    ):
        """Handle project generation via HTMX."""
        try:
            result = await generate_for_engine(
                engine_name=engine,
                description=description,
                complexity=complexity,
                features=[],
                art_style=art_style
            )
            
            return f"""
                <div class="alert alert-success">
                    <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
                    </svg>
                    <div>
                        <h3 class="font-bold">Project Generated Successfully! 🎉</h3>
                        <div class="text-sm opacity-80 mt-2">
                            <p><strong>Engine:</strong> {result.engine_type}</p>
                            <p><strong>Files:</strong> {', '.join(result.main_files)}</p>
                            <p><strong>Project Path:</strong> {result.project_path or 'Generated in memory'}</p>
                        </div>
                    </div>
                </div>
            """
        except Exception as e:
            return f"""
                <div class="alert alert-error">
                    <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
                    </svg>
                    <div>
                        <h3 class="font-bold">Generation Failed ❌</h3>
                        <div class="text-sm opacity-80">Error: {str(e)}</div>
                    </div>
                </div>
            """
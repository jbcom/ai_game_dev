"""
Production-quality Jinja2-based web interface for AI Game Development.
Proper template separation, inheritance, and component architecture.
"""
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from ai_game_dev.engines import get_supported_engines, generate_for_engine, engine_manager


# Template directory setup
TEMPLATE_DIR = Path(__file__).parent / "templates"
STATIC_DIR = Path(__file__).parent / "static"

# Initialize Jinja2 templates
templates = Jinja2Templates(directory=str(TEMPLATE_DIR))


def get_engine_info() -> Dict[str, Dict[str, Any]]:
    """Get comprehensive engine information for templates."""
    return {
        "pygame": {
            "icon": "🐍",
            "language": "Python",
            "description": "2D game development with Python - perfect for beginners and prototypes",
            "complexity": "beginner",
            "best_for": "2D Games, Prototypes",
            "platforms": "Cross-platform",
            "features": ["2D Graphics", "Sound", "Input", "Physics"],
            "learning_curve": 2,  # 1-5 scale
            "performance": 3,
            "support_2d": True,
            "support_3d": False,
            "community": 4
        },
        "bevy": {
            "icon": "🦀",
            "language": "Rust",
            "description": "Modern ECS-based game engine with high performance and safety",
            "complexity": "advanced",
            "best_for": "Performance Games, Complex Systems",
            "platforms": "Cross-platform",
            "features": ["ECS", "3D/2D", "Multithreading", "Hot Reload"],
            "learning_curve": 4,
            "performance": 5,
            "support_2d": True,
            "support_3d": True,
            "community": 3
        },
        "godot": {
            "icon": "🎯",
            "language": "GDScript",
            "description": "Scene-based game development with visual scripting support",
            "complexity": "intermediate",
            "best_for": "Indie Games, Rapid Prototyping",
            "platforms": "Cross-platform",
            "features": ["Visual Script", "3D/2D", "Animation", "Physics"],
            "learning_curve": 3,
            "performance": 4,
            "support_2d": True,
            "support_3d": True,
            "community": 4
        }
    }


def get_template_context(request: Request, current_page: str = "") -> Dict[str, Any]:
    """Get common template context for all pages."""
    engines = get_supported_engines()
    
    return {
        "request": request,
        "current_page": current_page,
        "current_year": datetime.now().year,
        "engines": engines,
        "engine_info": get_engine_info(),
        "theme": "dark",  # Default theme
        "stats": {
            "projects_generated": 0,  # TODO: Implement project tracking
            "assets_created": 0,      # TODO: Implement asset tracking
        },
        "recent_projects": [],  # TODO: Implement project history
    }


def setup_jinja_routes(app: FastAPI) -> None:
    """Setup Jinja2-based web interface routes."""
    
    # Mount static files
    if STATIC_DIR.exists():
        app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
    
    @app.get("/web", response_class=HTMLResponse)
    @app.get("/web/", response_class=HTMLResponse) 
    @app.get("/web/dashboard", response_class=HTMLResponse)
    async def web_dashboard(request: Request):
        """Dashboard page with overview and statistics."""
        context = get_template_context(request, "dashboard")
        return templates.TemplateResponse("pages/dashboard.html", context)
    
    @app.get("/web/new_project", response_class=HTMLResponse)
    async def web_new_project(request: Request, engine: Optional[str] = None):
        """New project creation page with form."""
        context = get_template_context(request, "new_project")
        
        # Pre-select engine if provided in query params
        if engine and engine in context["engines"]:
            context["selected_engine"] = engine
            
        return templates.TemplateResponse("pages/new_project.html", context)
    
    @app.get("/web/engines", response_class=HTMLResponse)
    async def web_engines(request: Request):
        """Engines overview and comparison page."""
        context = get_template_context(request, "engines")
        return templates.TemplateResponse("pages/engines.html", context)
    
    @app.post("/web/generate-project", response_class=HTMLResponse)
    async def web_generate_project(
        request: Request,
        description: str = Form(...),
        engine: str = Form(...),
        complexity: str = Form("intermediate"),
        art_style: str = Form("modern"),
        platform: str = Form("desktop"),
        project_name: Optional[str] = Form(None),
        include_assets: bool = Form(False)
    ):
        """Handle project generation via HTMX form submission."""
        try:
            # Generate the project
            result = await generate_for_engine(
                engine_name=engine,
                description=description,
                complexity=complexity,
                features=[],
                art_style=art_style
            )
            
            # Prepare success response data
            context = {
                "request": request,
                "success": True,
                "result": {
                    "engine_type": result.engine_type,
                    "main_files": result.main_files,
                    "project_path": str(result.project_path) if result.project_path else "Generated in memory",
                    "asset_requirements": result.asset_requirements,
                    "build_instructions": result.build_instructions,
                    "generated_files_count": len(result.generated_files)
                },
                "project_name": project_name or f"{engine}_{int(datetime.now().timestamp())}",
                "description": description
            }
            
            return templates.TemplateResponse("components/generation_result.html", context)
            
        except Exception as e:
            # Prepare error response data
            context = {
                "request": request,
                "success": False,
                "error": str(e),
                "engine": engine,
                "description": description
            }
            
            return templates.TemplateResponse("components/generation_result.html", context)


# Additional template filters and functions
def setup_template_globals(templates_instance: Jinja2Templates) -> None:
    """Setup custom template filters and global functions."""
    
    def format_file_size(size_bytes: int) -> str:
        """Format file size in human readable format."""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB"]
        i = 0
        while size_bytes >= 1024.0 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        
        return f"{size_bytes:.1f} {size_names[i]}"
    
    def truncate_text(text: str, length: int = 100) -> str:
        """Truncate text to specified length with ellipsis."""
        if len(text) <= length:
            return text
        return text[:length-3] + "..."
    
    def format_datetime(dt: datetime, format_str: str = "%Y-%m-%d %H:%M") -> str:
        """Format datetime object."""
        return dt.strftime(format_str)
    
    # Add filters to Jinja2 environment
    templates_instance.env.filters["file_size"] = format_file_size
    templates_instance.env.filters["truncate"] = truncate_text
    templates_instance.env.filters["datetime"] = format_datetime
    
    # Add global functions
    templates_instance.env.globals["range"] = range
    templates_instance.env.globals["len"] = len
    templates_instance.env.globals["enumerate"] = enumerate


# Initialize template globals when module is imported
setup_template_globals(templates)
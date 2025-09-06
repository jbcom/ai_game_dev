"""
Production-quality Jinja2-based web interface for AI Game Development.
Proper template separation, inheritance, and component architecture.
"""
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse, Response
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from ai_game_dev.engines import get_supported_engines, generate_for_engine
from ai_game_dev.project_manager import ProjectManager


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
    
    # Get project statistics
    project_manager = ProjectManager()
    stats = project_manager.get_stats()
    recent_projects = project_manager.get_recent_projects(limit=5)
    
    return {
        "request": request,
        "current_page": current_page,
        "current_year": datetime.now().year,
        "engines": engines,
        "engine_info": get_engine_info(),
        "theme": "dark",
        "stats": {
            "projects_generated": stats.get("total_projects", 0),
            "assets_created": 0,  # TODO: Implement asset tracking
        },
        "recent_projects": [
            {"name": p.name, "engine": p.engine, "created_at": p.created_at}
            for p in recent_projects
        ],
    }


def setup_jinja_routes(app: FastAPI) -> None:
    """Setup Jinja2-based web interface routes."""
    
    # Mount static files
    if STATIC_DIR.exists():
        app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
    
    @app.get("/favicon.ico")
    async def favicon():
        """Serve favicon."""
        favicon_path = STATIC_DIR / "favicon.svg"
        if favicon_path.exists():
            return FileResponse(favicon_path)
        return Response(status_code=204)
    
    @app.get("/web")
    @app.get("/web/") 
    @app.get("/web/dashboard")
    async def web_root(request: Request):
        """Root web route redirects to new project page."""
        return RedirectResponse(url="/web/new_project", status_code=307)
    
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
    
    
    @app.get("/web/projects", response_class=HTMLResponse)
    async def web_projects(request: Request, page: int = 1, limit: int = 12):
        """Projects management page."""
        project_manager = ProjectManager()
        
        offset = (page - 1) * limit
        projects = project_manager.list_projects(limit=limit, offset=offset)
        stats = project_manager.get_stats()
        
        total_projects = stats.get("total_projects", 0)
        total_pages = (total_projects + limit - 1) // limit
        
        # Get most popular engine
        engine_counts = stats.get("projects_by_engine", {})
        most_popular_engine = max(engine_counts.keys(), key=engine_counts.get) if engine_counts else "None"
        
        context = get_template_context(request, "projects")
        context.update({
            "projects": projects,
            "project_stats": stats,
            "most_popular_engine": most_popular_engine,
            "current_page": page,
            "total_pages": total_pages,
            "total_projects": total_projects
        })
        
        return templates.TemplateResponse("pages/projects.html", context)
    
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
        project_manager = ProjectManager()
        
        try:
            # Create project record
            name = project_name or f"{engine.title()} Game - {datetime.now().strftime('%Y%m%d_%H%M%S')}"
            project = project_manager.create_project(
                name=name,
                description=description,
                engine=engine,
                complexity=complexity,
                art_style=art_style
            )
            
            # Generate the project
            result = await generate_for_engine(
                engine_name=engine,
                description=description,
                complexity=complexity,
                features=[],
                art_style=art_style
            )
            
            # Update project with results
            updated_project = project_manager.update_project_with_result(project.id, result)
            
            # Prepare success response data
            context = {
                "request": request,
                "success": True,
                "result": {
                    "project_id": updated_project.id,
                    "engine_type": result.engine_type,
                    "main_files": result.main_files,
                    "project_path": str(result.project_path) if result.project_path else "Generated in memory",
                    "asset_requirements": result.asset_requirements,
                    "build_instructions": result.build_instructions,
                    "generated_files_count": len(result.generated_files)
                },
                "project_name": name,
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
        size_float = float(size_bytes)
        while size_float >= 1024.0 and i < len(size_names) - 1:
            size_float /= 1024.0
            i += 1
        
        return f"{size_float:.1f} {size_names[i]}"
    
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
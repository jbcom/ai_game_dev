"""
Educational Web Server for AI Game Development
Professor Pixel's Interactive Learning Platform
"""

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path

def create_education_app() -> FastAPI:
    """Create the educational FastAPI application."""
    
    app = FastAPI(
        title="AI Game Development Education",
        description="Professor Pixel's Interactive Learning Platform",
        version="1.0.0"
    )
    
    # Static files - reuse the main server's assets
    main_static_dir = Path(__file__).parent.parent / "server" / "static"
    app.mount("/static", StaticFiles(directory=str(main_static_dir)), name="static")
    
    # Templates
    template_dir = Path(__file__).parent / "templates"
    template_dir.mkdir(exist_ok=True)
    templates = Jinja2Templates(directory=str(template_dir))
    
    @app.get("/", response_class=HTMLResponse)
    async def education_home(request: Request):
        """Educational platform home page with Professor Pixel."""
        return templates.TemplateResponse("education_home.html", {
            "request": request,
            "title": "Welcome to Code Valley Academy!"
        })
    
    @app.get("/chapter/{chapter_id}", response_class=HTMLResponse)
    async def education_chapter(request: Request, chapter_id: int):
        """Individual educational chapters."""
        return templates.TemplateResponse("education_chapter.html", {
            "request": request,
            "chapter_id": chapter_id,
            "title": f"Chapter {chapter_id} - Code Valley Academy"
        })
    
    return app
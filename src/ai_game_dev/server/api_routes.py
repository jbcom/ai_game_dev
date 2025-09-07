from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel
import json
import zipfile
import io

from ai_game_dev.project_manager import ProjectManager, ProjectInfo
# Asset generation now handled by LangGraph subgraphs

router = APIRouter(prefix="/api", tags=["api"])

class ProjectCreateRequest(BaseModel):
    name: str
    description: str
    engine: str
    complexity: str = "intermediate"
    art_style: str = "modern"

class AssetGenerationRequest(BaseModel):
    asset_type: str
    description: str
    style: str = "modern"
    dimensions: Optional[tuple[int, int]] = None
    additional_params: Dict[str, Any] = {}

def get_project_manager() -> ProjectManager:
    return ProjectManager()

def get_graphics_subgraph():
    """Get graphics subgraph for asset generation."""
    from ai_game_dev.agents.subgraphs import GraphicsSubgraph
    return GraphicsSubgraph()

@router.get("/projects", response_model=List[Dict[str, Any]])
async def list_projects(
    limit: int = 50, 
    offset: int = 0,
    project_manager: ProjectManager = Depends(get_project_manager)
):
    """List all projects with pagination."""
    projects = project_manager.list_projects(limit=limit, offset=offset)
    return [
        {
            "id": p.id,
            "name": p.name,
            "description": p.description,
            "engine": p.engine,
            "complexity": p.complexity,
            "art_style": p.art_style,
            "status": p.status,
            "created_at": p.created_at.isoformat(),
            "updated_at": p.updated_at.isoformat()
        }
        for p in projects
    ]

@router.get("/projects/{project_id}")
async def get_project(
    project_id: str,
    project_manager: ProjectManager = Depends(get_project_manager)
):
    """Get detailed project information."""
    project = project_manager.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    return {
        "id": project.id,
        "name": project.name,
        "description": project.description,
        "engine": project.engine,
        "complexity": project.complexity,
        "art_style": project.art_style,
        "status": project.status,
        "created_at": project.created_at.isoformat(),
        "updated_at": project.updated_at.isoformat(),
        "project_path": project.project_path,
        "generated_files": project.generated_files,
        "build_instructions": project.build_instructions,
        "asset_requirements": project.asset_requirements
    }

@router.post("/projects")
async def create_project(
    request: ProjectCreateRequest,
    project_manager: ProjectManager = Depends(get_project_manager)
):
    """Create a new project."""
    project = project_manager.create_project(
        name=request.name,
        description=request.description,
        engine=request.engine,
        complexity=request.complexity,
        art_style=request.art_style
    )
    
    return {
        "success": True,
        "project_id": project.id,
        "message": "Project created successfully"
    }

@router.delete("/projects/{project_id}")
async def delete_project(
    project_id: str,
    project_manager: ProjectManager = Depends(get_project_manager)
):
    """Delete a project."""
    success = project_manager.delete_project(project_id)
    if not success:
        raise HTTPException(status_code=404, detail="Project not found")
    
    return {"success": True, "message": "Project deleted successfully"}

@router.post("/projects/{project_id}/duplicate")
async def duplicate_project(
    project_id: str,
    project_manager: ProjectManager = Depends(get_project_manager)
):
    """Duplicate an existing project."""
    original = project_manager.get_project(project_id)
    if not original:
        raise HTTPException(status_code=404, detail="Project not found")
    
    duplicate = project_manager.create_project(
        name=f"{original.name} (Copy)",
        description=original.description,
        engine=original.engine,
        complexity=original.complexity,
        art_style=original.art_style
    )
    
    return {
        "success": True,
        "project_id": duplicate.id,
        "message": "Project duplicated successfully"
    }

@router.get("/projects/{project_id}/export")
async def export_project(
    project_id: str,
    project_manager: ProjectManager = Depends(get_project_manager)
):
    """Export project as ZIP file."""
    project = project_manager.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Create ZIP file in memory
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        # Add project metadata
        project_info = {
            "name": project.name,
            "description": project.description,
            "engine": project.engine,
            "complexity": project.complexity,
            "art_style": project.art_style,
            "created_at": project.created_at.isoformat(),
            "build_instructions": project.build_instructions,
            "asset_requirements": project.asset_requirements
        }
        zip_file.writestr("project.json", json.dumps(project_info, indent=2))
        
        # Add generated files
        for filename, content in project.generated_files.items():
            zip_file.writestr(f"src/{filename}", content)
        
        # Add README
        readme_content = f"""# {project.name}

{project.description}

## Engine
{project.engine.title()}

## Build Instructions
{chr(10).join(f"{i+1}. {instruction}" for i, instruction in enumerate(project.build_instructions))}

## Generated Files
{chr(10).join(f"- {filename}" for filename in project.generated_files.keys())}

Generated by AI Game Development Platform
"""
        zip_file.writestr("README.md", readme_content)
    
    zip_buffer.seek(0)
    
    return StreamingResponse(
        io.BytesIO(zip_buffer.read()),
        media_type="application/zip",
        headers={"Content-Disposition": f"attachment; filename={project.name.replace(' ', '_')}.zip"}
    )

@router.get("/projects/stats")
async def get_project_stats(
    project_manager: ProjectManager = Depends(get_project_manager)
):
    """Get project statistics."""
    return project_manager.get_stats()

@router.post("/assets/generate")
async def generate_asset(
    request: AssetGenerationRequest,
    graphics_subgraph = Depends(get_graphics_subgraph)
):
    """Generate a game asset using LangGraph graphics subgraph."""
    
    # Convert request to game spec format for subgraph
    game_spec = {
        "title": f"Asset: {request.asset_type}",
        "art_style": request.style,
        "genre": "game",
        "description": request.description,
        "features": [request.asset_type]
    }
    
    try:
        # Use the graphics subgraph to generate assets
        result = await graphics_subgraph.generate_graphics(game_spec)
        
        if result["success"]:
            return {
                "success": True,
                "asset_type": request.asset_type,
                "description": request.description,
                "generated_assets": result["generated_graphics"],
                "total_generated": result["total_generated"]
            }
        else:
            raise HTTPException(status_code=500, detail=f"Asset generation failed: {result.get('error', 'Unknown error')}")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Asset generation failed: {str(e)}")

@router.get("/assets/types")
async def get_asset_types():
    """Get supported asset types."""
    return {
        "asset_types": ["sprite", "tileset", "sound", "music"],
        "styles": ["modern", "pixel", "minimalist", "cartoon", "realistic"],
        "sprite_dimensions": [(32, 32), (64, 64), (128, 128), (256, 256)],
        "tileset_sizes": [16, 32, 64],
        "audio_formats": ["WAV", "MP3", "OGG"]
    }
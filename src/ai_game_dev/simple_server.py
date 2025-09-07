"""
Simple AI Game Development Server
Fallback server when Streamlit is not available.
"""

import asyncio
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import uvicorn

# Our components
from ai_game_dev.cache_config import initialize_sqlite_cache_and_memory
from ai_game_dev.agents.master_orchestrator import MasterGameDevOrchestrator
from ai_game_dev.project_manager import ProjectManager


app = FastAPI(title="AI Game Development Platform")

# Global state
orchestrator = None
project_manager = None


@app.on_event("startup")
async def startup_event():
    """Initialize the application on startup."""
    global orchestrator, project_manager
    
    print("🚀 Starting AI Game Development Platform...")
    
    # Initialize caching and memory
    try:
        initialize_sqlite_cache_and_memory()
        print("✅ LangChain SQLite caching initialized")
    except Exception as e:
        print(f"⚠️ Cache initialization failed: {e}")
    
    # Initialize orchestrator
    try:
        orchestrator = MasterGameDevOrchestrator()
        await orchestrator.initialize()
        print("✅ Master orchestrator initialized")
    except Exception as e:
        print(f"⚠️ Orchestrator initialization failed: {e}")
    
    # Initialize project manager
    try:
        project_manager = ProjectManager()
        print("✅ Project manager initialized")
    except Exception as e:
        print(f"⚠️ Project manager initialization failed: {e}")
    
    print("🎮 AI Game Development Platform ready!")


@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main dashboard."""
    
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>🎮 AI Game Development Platform</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-gray-100 min-h-screen">
        <div class="container mx-auto px-4 py-8">
            <!-- Header -->
            <div class="text-center mb-8">
                <h1 class="text-5xl font-bold text-blue-600 mb-4">🎮 AI Game Development Platform</h1>
                <p class="text-xl text-gray-600">Create revolutionary games with AI-powered tools</p>
            </div>
            
            <!-- Status -->
            <div class="bg-white rounded-lg shadow-md p-6 mb-8">
                <h2 class="text-2xl font-semibold mb-4">🔧 System Status</h2>
                <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div class="text-center">
                        <div class="text-3xl font-bold text-green-600">✅</div>
                        <div class="text-sm text-gray-600">SQLite Cache</div>
                    </div>
                    <div class="text-center">
                        <div class="text-3xl font-bold text-green-600">🤖</div>
                        <div class="text-sm text-gray-600">AI Agents</div>
                    </div>
                    <div class="text-center">
                        <div class="text-3xl font-bold text-blue-600">3</div>
                        <div class="text-sm text-gray-600">Game Engines</div>
                    </div>
                    <div class="text-center">
                        <div class="text-3xl font-bold text-purple-600">🎓</div>
                        <div class="text-sm text-gray-600">Education Ready</div>
                    </div>
                </div>
            </div>
            
            <!-- Quick Actions -->
            <div class="grid md:grid-cols-2 gap-8">
                <div class="bg-white rounded-lg shadow-md p-6">
                    <h3 class="text-xl font-semibold mb-4">🚀 Game Creation</h3>
                    <div class="space-y-3">
                        <button onclick="createGame()" class="w-full bg-blue-600 text-white py-2 px-4 rounded hover:bg-blue-700">
                            🆕 Create New Game
                        </button>
                        <button onclick="viewProjects()" class="w-full bg-gray-600 text-white py-2 px-4 rounded hover:bg-gray-700">
                            📚 View Projects
                        </button>
                    </div>
                </div>
                
                <div class="bg-white rounded-lg shadow-md p-6">
                    <h3 class="text-xl font-semibold mb-4">🎓 Education</h3>
                    <div class="space-y-3">
                        <button onclick="startEducation()" class="w-full bg-purple-600 text-white py-2 px-4 rounded hover:bg-purple-700">
                            🌃 NeoTokyo Code Academy
                        </button>
                        <button onclick="viewLessons()" class="w-full bg-gray-600 text-white py-2 px-4 rounded hover:bg-gray-700">
                            📖 Browse Lessons
                        </button>
                    </div>
                </div>
            </div>
            
            <!-- API Info -->
            <div class="bg-white rounded-lg shadow-md p-6 mt-8">
                <h3 class="text-xl font-semibold mb-4">⚡ API Endpoints</h3>
                <div class="space-y-2 text-sm text-gray-600">
                    <div><strong>POST</strong> /api/generate-game - Generate a complete game</div>
                    <div><strong>GET</strong> /api/projects - List all projects</div>
                    <div><strong>GET</strong> /api/education - Educational content</div>
                    <div><strong>POST</strong> /api/chat - Chat with AI assistant</div>
                </div>
            </div>
        </div>
        
        <script>
            function createGame() {
                alert('🎮 Game creation interface - TODO: Build form');
            }
            
            function viewProjects() {
                window.location.href = '/projects';
            }
            
            function startEducation() {
                alert('🎓 NeoTokyo Code Academy starting soon!');
            }
            
            function viewLessons() {
                alert('📖 Educational content interface - TODO');
            }
        </script>
    </body>
    </html>
    """
    
    return HTMLResponse(content=html_content)


@app.get("/projects", response_class=HTMLResponse)
async def projects_page():
    """Projects management page."""
    
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>📚 Projects - AI Game Dev</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-gray-100 min-h-screen">
        <div class="container mx-auto px-4 py-8">
            <div class="mb-6">
                <a href="/" class="text-blue-600 hover:underline">← Back to Dashboard</a>
            </div>
            
            <h1 class="text-3xl font-bold mb-6">📚 Game Projects</h1>
            
            <div class="bg-white rounded-lg shadow-md p-6">
                <p class="text-gray-600 mb-4">Project management interface coming soon!</p>
                <p class="text-sm text-gray-500">This will show your generated games, allow editing, and provide project management tools.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return HTMLResponse(content=html_content)


@app.post("/api/generate-game")
async def generate_game(request: Request):
    """Generate a complete game using the orchestrator."""
    
    global orchestrator
    
    if not orchestrator:
        return JSONResponse({"error": "Orchestrator not initialized"}, status_code=500)
    
    try:
        data = await request.json()
        
        game_spec = {
            "title": data.get("title", "My Game"),
            "description": data.get("description", "A fun game"),
            "engine": data.get("engine", "pygame"),
            "complexity": data.get("complexity", "intermediate"),
            "art_style": data.get("art_style", "modern"),
            "target_audience": data.get("target_audience", "general"),
            "features": data.get("features", ["graphics", "audio"])
        }
        
        # Generate game using orchestrator
        result = await orchestrator.generate_complete_game(game_spec)
        
        return JSONResponse(result)
        
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@app.get("/api/projects")
async def get_projects():
    """Get all projects."""
    
    global project_manager
    
    if not project_manager:
        return JSONResponse({"error": "Project manager not initialized"}, status_code=500)
    
    try:
        projects = project_manager.list_projects()
        
        return JSONResponse({
            "projects": [
                {
                    "id": p.id,
                    "name": p.name,
                    "description": p.description,
                    "engine": p.engine,
                    "status": p.status,
                    "created_at": p.created_at.isoformat()
                }
                for p in projects
            ]
        })
        
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@app.get("/api/education")
async def get_education():
    """Get educational content."""
    
    return JSONResponse({
        "game": {
            "title": "NeoTokyo Code Academy: The Binary Rebellion",
            "description": "Educational RPG featuring Professor Pixel",
            "lessons": [
                "Variables and Data Types",
                "Loops and Conditions", 
                "Functions and Classes",
                "Data Structures",
                "Game Programming Basics"
            ],
            "status": "ready"
        }
    })


@app.post("/api/chat")
async def chat_with_ai(request: Request):
    """Chat with AI assistant."""
    
    try:
        data = await request.json()
        message = data.get("message", "")
        
        # Simple response for now
        response = f"🤖 AI Assistant: I received your message '{message}'. Full chat integration coming soon!"
        
        return JSONResponse({"response": response})
        
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


def run_simple_server():
    """Run the simple FastAPI server."""
    
    print("🚀 Starting simple AI Game Development server...")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=5000,
        log_level="info"
    )


if __name__ == "__main__":
    run_simple_server()
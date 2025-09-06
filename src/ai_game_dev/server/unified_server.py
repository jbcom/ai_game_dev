"""
Unified server combining FastMCP and Mesop web interface.
Serves both MCP protocol endpoints and web UI from a single HTTP server.
"""
import json
import asyncio
from typing import Optional, List, Dict, Any
from pathlib import Path
import uvicorn
from fastapi import FastAPI, Request, Response
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

# Import our core functionality
from ai_game_dev.engines import engine_manager, generate_for_engine, get_supported_engines
from ai_game_dev.assets import AssetTools
from ai_game_dev.providers import get_provider

# Try to import mesop for web UI
try:
    import mesop as me
    from ai_game_dev.ui.web.portal import AppState, render_dashboard, render_new_project, render_asset_generator, render_settings
    MESOP_AVAILABLE = True
except ImportError:
    MESOP_AVAILABLE = False


class UnifiedGameDevServer:
    """
    Unified server combining MCP protocol and web interface.
    Provides both HTTP endpoints for MCP clients and web UI for browser access.
    """
    
    def __init__(self, host: str = "0.0.0.0", port: int = 5000):
        self.host = host
        self.port = port
        self.app = FastAPI(
            title="AI Game Development Server",
            description="Unified server for game development with MCP protocol and web interface",
            version="1.0.0"
        )
        self.setup_middleware()
        self.setup_routes()
    
    def setup_middleware(self):
        """Setup CORS and other middleware."""
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    
    def setup_routes(self):
        """Setup all routes for both MCP and web interface."""
        self.setup_mcp_routes()
        self.setup_web_routes()
        self.setup_api_routes()
    
    def setup_mcp_routes(self):
        """Setup Model Context Protocol endpoints."""
        
        @self.app.post("/mcp/tools/generate_game")
        async def mcp_generate_game(request: Request):
            """MCP endpoint for game generation."""
            data = await request.json()
            
            try:
                result = await generate_for_engine(
                    engine_name=data.get("engine", "pygame"),
                    description=data.get("description", ""),
                    complexity=data.get("complexity", "intermediate"),
                    features=data.get("features", []),
                    art_style=data.get("art_style", "modern")
                )
                
                return JSONResponse({
                    "success": True,
                    "result": {
                        "engine_type": result.engine_type,
                        "main_files": result.main_files,
                        "asset_requirements": result.asset_requirements,
                        "build_instructions": result.build_instructions,
                        "project_path": str(result.project_path) if result.project_path else None,
                        "generated_files_count": len(result.generated_files)
                    }
                })
            except Exception as e:
                return JSONResponse({
                    "success": False,
                    "error": str(e)
                }, status_code=500)
        
        @self.app.post("/mcp/tools/generate_assets")
        async def mcp_generate_assets(request: Request):
            """MCP endpoint for asset generation."""
            data = await request.json()
            
            try:
                # Use asset generation tools
                asset_tools = AssetTools()
                
                result = {
                    "success": True,
                    "asset_type": data.get("asset_type", "image"),
                    "description": data.get("description", ""),
                    "style": data.get("style", "modern"),
                    "message": "Asset generation initiated"
                }
                
                return JSONResponse(result)
            except Exception as e:
                return JSONResponse({
                    "success": False,
                    "error": str(e)
                }, status_code=500)
        
        @self.app.get("/mcp/tools/list_engines")
        async def mcp_list_engines():
            """MCP endpoint to list available engines."""
            try:
                engines = get_supported_engines()
                engine_info = {
                    engine: engine_manager.get_engine_info(engine)
                    for engine in engines
                }
                
                return JSONResponse({
                    "success": True,
                    "engines": engines,
                    "engine_info": engine_info
                })
            except Exception as e:
                return JSONResponse({
                    "success": False,
                    "error": str(e)
                }, status_code=500)
    
    def setup_web_routes(self):
        """Setup web interface routes."""
        
        @self.app.get("/", response_class=HTMLResponse)
        async def web_home():
            """Main web interface page."""
            if not MESOP_AVAILABLE:
                return HTMLResponse("""
                    <html>
                        <head><title>AI Game Development Server</title></head>
                        <body style="font-family: Arial, sans-serif; padding: 20px; background: #1a1a2e; color: white;">
                            <h1>🎮 AI Game Development Server</h1>
                            <p>MCP protocol is available at the following endpoints:</p>
                            <ul>
                                <li><code>POST /mcp/tools/generate_game</code> - Generate game projects</li>
                                <li><code>POST /mcp/tools/generate_assets</code> - Generate game assets</li>
                                <li><code>GET /mcp/tools/list_engines</code> - List available engines</li>
                            </ul>
                            <p><strong>Note:</strong> Web UI requires Mesop to be installed.</p>
                            <p>Install with: <code>pip install mesop</code></p>
                        </body>
                    </html>
                """)
            
            # If Mesop is available, render the full web interface
            return HTMLResponse(self.render_mesop_app())
        
        @self.app.get("/health")
        async def health_check():
            """Health check endpoint."""
            return JSONResponse({
                "status": "healthy",
                "services": {
                    "mcp": True,
                    "web_ui": MESOP_AVAILABLE,
                    "engines": len(get_supported_engines())
                }
            })
    
    def setup_api_routes(self):
        """Setup REST API routes for web interface."""
        
        @self.app.get("/api/engines")
        async def api_list_engines():
            """REST API to list engines."""
            return JSONResponse({
                "engines": get_supported_engines(),
                "count": len(get_supported_engines())
            })
        
        @self.app.post("/api/generate")
        async def api_generate_game(request: Request):
            """REST API for game generation."""
            data = await request.json()
            
            try:
                result = await generate_for_engine(
                    engine_name=data.get("engine", "pygame"),
                    description=data.get("description", ""),
                    complexity=data.get("complexity", "intermediate"),
                    features=data.get("features", []),
                    art_style=data.get("art_style", "modern")
                )
                
                return JSONResponse({
                    "success": True,
                    "project_info": {
                        "engine": result.engine_type,
                        "files": result.main_files,
                        "assets_needed": result.asset_requirements,
                        "project_path": str(result.project_path) if result.project_path else None
                    }
                })
            except Exception as e:
                return JSONResponse({
                    "success": False,
                    "error": str(e)
                }, status_code=500)
    
    def render_mesop_app(self) -> str:
        """Render the Mesop web application as HTML."""
        # This is a simplified version - in practice, Mesop would handle routing
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>AI Game Development Portal</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #1a1a2e; color: white; }
                .header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px; }
                .title { font-size: 32px; font-weight: bold; color: #64ffda; }
                .nav-buttons { display: flex; gap: 10px; }
                .nav-button { background: #16213e; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; }
                .nav-button:hover { background: #0f3460; }
                .content { background: #16213e; padding: 20px; border-radius: 10px; }
            </style>
        </head>
        <body>
            <div class="header">
                <div class="title">🎮 AI Game Development Portal</div>
                <div class="nav-buttons">
                    <button class="nav-button" onclick="showDashboard()">Dashboard</button>
                    <button class="nav-button" onclick="showNewProject()">New Project</button>
                    <button class="nav-button" onclick="showAssets()">Generate Assets</button>
                    <button class="nav-button" onclick="showSettings()">Settings</button>
                </div>
            </div>
            
            <div class="content" id="content">
                <h2>Welcome to AI Game Development</h2>
                <p>Create games with AI assistance across multiple engines:</p>
                <ul>
                    <li><strong>Pygame</strong> - Python 2D games</li>
                    <li><strong>Bevy</strong> - Rust ECS engine</li>
                    <li><strong>Godot</strong> - GDScript scene-based</li>
                </ul>
                <p>Use the navigation buttons above to get started.</p>
            </div>
            
            <script>
                function showDashboard() {
                    document.getElementById('content').innerHTML = `
                        <h2>Dashboard</h2>
                        <p>Recent projects and system status would appear here.</p>
                    `;
                }
                
                function showNewProject() {
                    document.getElementById('content').innerHTML = `
                        <h2>Create New Project</h2>
                        <form onsubmit="generateProject(event)">
                            <p><label>Description: <input type="text" id="description" placeholder="A simple platformer game" style="width: 300px;"></label></p>
                            <p><label>Engine: 
                                <select id="engine">
                                    <option value="pygame">Pygame (Python)</option>
                                    <option value="bevy">Bevy (Rust)</option>
                                    <option value="godot">Godot (GDScript)</option>
                                </select>
                            </label></p>
                            <p><label>Complexity: 
                                <select id="complexity">
                                    <option value="beginner">Beginner</option>
                                    <option value="intermediate">Intermediate</option>
                                    <option value="advanced">Advanced</option>
                                </select>
                            </label></p>
                            <button type="submit" style="background: #64ffda; color: #1a1a2e; border: none; padding: 10px 20px; border-radius: 5px;">Generate Project</button>
                        </form>
                        <div id="result"></div>
                    `;
                }
                
                function showAssets() {
                    document.getElementById('content').innerHTML = `
                        <h2>Generate Assets</h2>
                        <p>Asset generation tools would appear here.</p>
                    `;
                }
                
                function showSettings() {
                    document.getElementById('content').innerHTML = `
                        <h2>Settings</h2>
                        <p>Configuration options would appear here.</p>
                    `;
                }
                
                async function generateProject(event) {
                    event.preventDefault();
                    const description = document.getElementById('description').value;
                    const engine = document.getElementById('engine').value;
                    const complexity = document.getElementById('complexity').value;
                    
                    const result = document.getElementById('result');
                    result.innerHTML = '<p>Generating project...</p>';
                    
                    try {
                        const response = await fetch('/api/generate', {
                            method: 'POST',
                            headers: {'Content-Type': 'application/json'},
                            body: JSON.stringify({description, engine, complexity})
                        });
                        
                        const data = await response.json();
                        
                        if (data.success) {
                            result.innerHTML = `
                                <h3>✅ Project Generated Successfully!</h3>
                                <p><strong>Engine:</strong> ${data.project_info.engine}</p>
                                <p><strong>Files:</strong> ${data.project_info.files.join(', ')}</p>
                                <p><strong>Project Path:</strong> ${data.project_info.project_path}</p>
                            `;
                        } else {
                            result.innerHTML = `<p style="color: #ff6b6b;">❌ Error: ${data.error}</p>`;
                        }
                    } catch (error) {
                        result.innerHTML = `<p style="color: #ff6b6b;">❌ Network Error: ${error.message}</p>`;
                    }
                }
            </script>
        </body>
        </html>
        """
    
    async def start(self):
        """Start the unified server."""
        print(f"🚀 Starting Unified AI Game Development Server")
        print(f"🌐 Web Interface: http://{self.host}:{self.port}")
        print(f"🔧 MCP Endpoints: http://{self.host}:{self.port}/mcp/")
        print(f"📡 API Endpoints: http://{self.host}:{self.port}/api/")
        print(f"💾 Mesop Available: {MESOP_AVAILABLE}")
        print(f"🎮 Supported Engines: {', '.join(get_supported_engines())}")
        print("Press Ctrl+C to stop the server")
        
        config = uvicorn.Config(
            self.app,
            host=self.host,
            port=self.port,
            log_level="info"
        )
        server = uvicorn.Server(config)
        await server.serve()
    
    def run(self):
        """Run the server (synchronous wrapper)."""
        try:
            asyncio.run(self.start())
        except KeyboardInterrupt:
            print("\n👋 Server stopped by user")


def run_server(host: str = "0.0.0.0", port: int = 5000):
    """Start the unified game development server."""
    server = UnifiedGameDevServer(host, port)
    server.run()


if __name__ == "__main__":
    run_server()
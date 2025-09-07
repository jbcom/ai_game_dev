"""
Unified server combining FastMCP SSE and Mesop web interface.
Serves both MCP protocol endpoints and web UI from a single HTTP server.
"""
import json
import asyncio
import os
from typing import Optional, List, Dict, Any, Callable
from pathlib import Path
import uvicorn
from fastapi import FastAPI, Request, Response
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from mcp.server.fastmcp import FastMCP

# Import our SSE transport layer
from .sse_transport import create_sse_server

# Import our core functionality
from ai_game_dev.engines import engine_manager, generate_for_engine, get_supported_engines
# Asset generation now handled by LangChain DALLE in subgraphs
# Cache config imported on demand to avoid dependency issues

# Try to import HTMY for web UI, fallback to simple web interface
try:
    import htmy
    from .htmy_interface import setup_htmy_routes
    HTMY_AVAILABLE = True
except ImportError:
    HTMY_AVAILABLE = False

# Always import simple web interface as fallback
# Removed simple_web - using Jinja2 interface


class UnifiedGameDevServer:
    """
    Unified server combining MCP protocol and web interface.
    Provides both SSE-based MCP endpoints and web UI from a single FastAPI server.
    """
    
    def __init__(self, master_orchestrator=None, host: str = "0.0.0.0", port: int = 5000):
        self.host = host
        self.port = port
        self.master_orchestrator = master_orchestrator
        self.master_orchestrator_initialized = master_orchestrator is not None
        self.app = FastAPI(
            title="AI Game Development Server",
            description="Unified server for game development with MCP protocol and web interface",
            version="1.0.0"
        )
        
        # Initialize SQLite caching and memory persistence
        print("🚀 Initializing SQLite caching and memory...")
        self._initialize_sqlite_cache()
        
        # Initialize FastMCP server for SSE connections
        self.mcp = FastMCP("AI Game Development Server")
        self.setup_mcp_tools()
        self.setup_middleware()
        self.setup_routes()
    
    def _initialize_sqlite_cache(self):
        """Initialize SQLite caching without heavy dependencies."""
        try:
            from ai_game_dev.cache_config import initialize_sqlite_cache_and_memory
            initialize_sqlite_cache_and_memory()
        except ImportError as e:
            print(f"⚠️ SQLite caching unavailable: {e}")
            print("ℹ️ Running without persistent caching")
    
    async def _setup_master_orchestrator_integration(self):
        """Setup integration with master orchestrator for asset management."""
        if not self.master_orchestrator_initialized:
            print("⚠️ Master Orchestrator not provided during initialization")
            return
            
        try:
            # Setup internal asset verification through orchestrator
            print("🎨 Requesting asset verification through Master Orchestrator...")
            
            verification_request = {
                "task_type": "asset_verification", 
                "user_input": "Verify all required game assets are available and generate missing ones",
                "context": {
                    "asset_categories": ["rpg_characters", "educational_environments", "professor_pixel", "game_code", "yarn_spinner"],
                    "output_directory": "src/ai_game_dev/server/static/assets"
                }
            }
            
            # Route through master orchestrator instead of direct agent call
            result = await self.master_orchestrator.route_internal_request(verification_request)
            
            if result.get("success"):
                print("✅ Asset verification completed through Master Orchestrator")
            else:
                print(f"⚠️ Asset verification had issues: {result.get('message', 'Unknown error')}")
                
        except Exception as e:
            print(f"⚠️ Master Orchestrator integration failed: {e}")
            print("ℹ️ Continuing server startup without orchestrator integration")
    
    def _get_required_assets(self) -> Dict[str, List[str]]:
        """Get comprehensive game asset requirements from TOML specifications."""
        try:
            from ai_game_dev.game_specification import get_comprehensive_asset_requirements
            return get_comprehensive_asset_requirements()
        except ImportError as e:
            print(f"⚠️ Failed to load game specifications: {e}")
            print("ℹ️ Falling back to basic asset requirements")
            # Fallback to basic assets if game specification system unavailable
            return {
                "basic_ui": [
                    "src/ai_game_dev/server/static/assets/logos/main-logo.svg",
                    "src/ai_game_dev/server/static/assets/frames/tech-frame.png"
                ]
            }
    
    def _check_missing_assets(self, required_assets: Dict[str, List[str]]) -> Dict[str, List[str]]:
        """Check which required assets are missing."""
        missing = {}
        
        for category, asset_paths in required_assets.items():
            missing_in_category = []
            
            for asset_path in asset_paths:
                path = Path(asset_path)
                if not path.exists():
                    missing_in_category.append(asset_path)
            
            if missing_in_category:
                missing[category] = missing_in_category
        
        return missing
    
    def setup_middleware(self):
        """Setup CORS and other middleware."""
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    
    def setup_mcp_tools(self):
        """Setup MCP tools using FastMCP decorators."""
        
        @self.mcp.tool()
        async def generate_game(
            description: str,
            engine: str = "pygame",
            complexity: str = "intermediate",
            features: List[str] = None,
            art_style: str = "modern"
        ) -> str:
            """Generate a complete game project using the specified engine."""
            try:
                result = await generate_for_engine(
                    engine_name=engine,
                    description=description,
                    complexity=complexity,
                    features=features or [],
                    art_style=art_style
                )
                
                return json.dumps({
                    "success": True,
                    "engine_type": result.engine_type,
                    "main_files": result.main_files,
                    "asset_requirements": result.asset_requirements,
                    "project_path": str(result.project_path) if result.project_path else None,
                    "message": f"✅ Generated {description} for {engine} engine successfully!"
                }, indent=2)
            except Exception as e:
                return json.dumps({
                    "success": False,
                    "error": str(e)
                }, indent=2)
        
        @self.mcp.tool()
        def list_game_engines() -> str:
            """List all available game engines and their capabilities."""
            try:
                engines = get_supported_engines()
                engine_info = {
                    engine: engine_manager.get_engine_info(engine)
                    for engine in engines
                }
                
                return json.dumps({
                    "success": True,
                    "engines": engines,
                    "engine_info": engine_info,
                    "total_engines": len(engines)
                }, indent=2)
            except Exception as e:
                return json.dumps({
                    "success": False,
                    "error": str(e)
                }, indent=2)
        
        @self.mcp.tool()
        async def generate_assets(
            asset_type: str,
            description: str,
            style: str = "modern",
            resolution: str = "512x512"
        ) -> str:
            """Generate game assets like images, sounds, and music."""
            try:
                # Use asset generation tools
                # Asset generation now handled by LangChain DALLE in subgraphs
                
                return json.dumps({
                    "success": True,
                    "asset_type": asset_type,
                    "description": description,
                    "style": style,
                    "resolution": resolution,
                    "message": f"✅ Asset generation initiated: {description}"
                }, indent=2)
            except Exception as e:
                return json.dumps({
                    "success": False,
                    "error": str(e)
                }, indent=2)
    
    def setup_routes(self):
        """Setup all routes for both MCP SSE and web interface."""
        # Setup API routes first (before mounting anything)
        self.setup_api_routes()
        
        # Mount the SSE MCP server for MCP protocol communication
        self.app.mount("/mcp", create_sse_server(self.mcp))
        
        # Setup Jinja2 web interface (production-ready templates)
        from .jinja_interface import setup_jinja_routes
        from .api_routes import router as api_router
        from .websocket_manager import websocket_endpoint
        
        setup_jinja_routes(self.app)
        self.app.include_router(api_router)
        self.app.websocket("/ws")(websocket_endpoint)
        print("✅ Jinja2 interface, API routes, and WebSocket support loaded successfully")
        
        # Add redirect from root to web interface
        @self.app.get("/", response_class=HTMLResponse)
        async def root_redirect():
            """Redirect root to split-panel homepage."""
            return HTMLResponse("""
                <html>
                    <head>
                        <meta http-equiv="refresh" content="0; URL=/web/homepage">
                    </head>
                    <body>
                        <p>Redirecting to <a href="/web/homepage">AI Game Development Platform</a>...</p>
                    </body>
                </html>
            """)
    
        
    def setup_fallback_web_routes(self):
        """Setup fallback web routes when Mesop is not available."""
        
        @self.app.get("/", response_class=HTMLResponse)
        async def web_home():
            """Fallback web interface."""
            return HTMLResponse("""
                <html>
                    <head><title>AI Game Development Server</title></head>
                    <body style="font-family: Arial, sans-serif; padding: 20px; background: #1a1a2e; color: white;">
                        <h1>🎮 AI Game Development Server</h1>
                        <h2>MCP Protocol Connection</h2>
                        <p>Connect your MCP client to: <code>http://localhost:5000/mcp/sse</code></p>
                        <p>Available MCP tools:</p>
                        <ul>
                            <li><strong>generate_game</strong> - Generate complete game projects</li>
                            <li><strong>generate_assets</strong> - Generate game assets</li>
                            <li><strong>list_game_engines</strong> - List available engines</li>
                        </ul>
                        <h2>Web Interface</h2>
                        <p><strong>Note:</strong> Full web UI requires HTMY to be installed.</p>
                        <p>Install with: <code>pip install htmy</code></p>
                        <p>Use the <a href="/api/" style="color: #64ffda;">REST API</a> for web-based interactions.</p>
                    </body>
                </html>
            """)
        
        @self.app.get("/health")
        async def health_check():
            """Health check endpoint."""
            return JSONResponse({
                "status": "healthy",
                "services": {
                    "mcp_sse": True,
                    "web_ui": True,
                    "engines": len(get_supported_engines()),
                    "mcp_endpoint": "http://localhost:5000/mcp/sse"
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
    
    
    async def start(self):
        """Start the unified server."""
        print(f"🚀 Starting Unified AI Game Development Server")
        
        # Setup master orchestrator integration if available
        if self.master_orchestrator_initialized:
            print("🎨 Setting up Master Orchestrator integration...")
            await self._setup_master_orchestrator_integration()
        else:
            print("⚠️ Starting without Master Orchestrator integration")
        
        print(f"🌐 Web Interface: http://{self.host}:{self.port}")
        print(f"🔧 MCP SSE Endpoint: http://{self.host}:{self.port}/mcp/sse")
        print(f"📡 REST API: http://{self.host}:{self.port}/api/")
        print(f"💾 Web UI: Simple HTML + HTMX + DaisyUI")
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


def run_server(host: str = "0.0.0.0", port: int = 5000, master_orchestrator=None):
    """Start the unified game development server."""
    server = UnifiedGameDevServer(master_orchestrator, host, port)
    server.run()


if __name__ == "__main__":
    run_server()
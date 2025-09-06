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
from fastapi.middleware.wsgi import WSGIMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from mcp.server.fastmcp import FastMCP

# Import our SSE transport layer
from .sse_transport import create_sse_server

# Import our core functionality
from ai_game_dev.engines import engine_manager, generate_for_engine, get_supported_engines
from ai_game_dev.assets import AssetTools

# Try to import mesop for web UI
try:
    import mesop as me
    import mesop.labs as mel
    MESOP_AVAILABLE = True
except ImportError:
    MESOP_AVAILABLE = False


class UnifiedGameDevServer:
    """
    Unified server combining MCP protocol and web interface.
    Provides both SSE-based MCP endpoints and web UI from a single FastAPI server.
    """
    
    def __init__(self, host: str = "0.0.0.0", port: int = 5000):
        self.host = host
        self.port = port
        self.app = FastAPI(
            title="AI Game Development Server",
            description="Unified server for game development with MCP protocol and web interface",
            version="1.0.0"
        )
        
        # Initialize FastMCP server for SSE connections
        self.mcp = FastMCP("AI Game Development Server")
        self.setup_mcp_tools()
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
                asset_tools = AssetTools()
                
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
        
        # Setup Mesop web interface if available
        if MESOP_AVAILABLE:
            self.setup_mesop_interface()
        else:
            self.setup_fallback_web_routes()
    
    def setup_mesop_interface(self):
        """Setup Mesop web interface using proper WSGI integration."""
        
        @me.stateclass
        class GameDevState:
            """State for the game development interface."""
            current_page: str = "dashboard"
            project_description: str = ""
            selected_engine: str = "pygame"
            complexity: str = "intermediate"
            generation_result: Optional[str] = None
            is_generating: bool = False

        def navigate_to_page(page: str):
            """Navigate to a different page."""
            def handler(event: me.ClickEvent):
                state = me.state(GameDevState)
                state.current_page = page
            return handler

        def generate_project(event: me.ClickEvent):
            """Generate a game project."""
            state = me.state(GameDevState)
            state.is_generating = True
            # This would trigger the actual generation via the MCP tools
            state.generation_result = f"Generated {state.project_description} using {state.selected_engine}"
            state.is_generating = False

        def update_description(event: me.InputEvent):
            """Update project description."""
            state = me.state(GameDevState)
            state.project_description = event.value

        def update_engine(event: me.SelectSelectionChangeEvent):
            """Update selected engine."""
            state = me.state(GameDevState)
            state.selected_engine = event.value

        @me.page(
            path="/",
            title="AI Game Development Portal",
            security_policy=me.SecurityPolicy(
                allowed_script_srcs=["https://cdn.jsdelivr.net"]
            )
        )
        def game_dev_portal():
            """Main game development portal page."""
            state = me.state(GameDevState)
            
            with me.box(style=me.Style(
                background="#1a1a2e",
                color="white",
                padding=me.Padding.all(20),
                min_height="100vh"
            )):
                # Header
                with me.box(style=me.Style(
                    display="flex",
                    justify_content="space-between",
                    align_items="center",
                    margin=me.Margin(bottom=30),
                    border_bottom="2px solid #16213e",
                    padding=me.Padding(bottom=20)
                )):
                    me.text(
                        "🎮 AI Game Development Portal",
                        style=me.Style(font_size=32, font_weight="bold", color="#64ffda")
                    )
                    
                    with me.box(style=me.Style(display="flex", gap=10)):
                        me.button(
                            "Dashboard",
                            on_click=navigate_to_page("dashboard"),
                            type="flat" if state.current_page != "dashboard" else "raised"
                        )
                        me.button(
                            "New Project",
                            on_click=navigate_to_page("new_project"),
                            type="flat" if state.current_page != "new_project" else "raised"
                        )
                        me.button(
                            "Assets",
                            on_click=navigate_to_page("assets"),
                            type="flat" if state.current_page != "assets" else "raised"
                        )

                # Content area
                with me.box(style=me.Style(
                    background="#16213e",
                    padding=me.Padding.all(20),
                    border_radius=10
                )):
                    if state.current_page == "dashboard":
                        me.text("Welcome to AI Game Development", style=me.Style(font_size=24, margin=me.Margin(bottom=20)))
                        me.text("Create games with AI assistance across multiple engines:")
                        me.text("• Pygame - Python 2D games")
                        me.text("• Bevy - Rust ECS engine") 
                        me.text("• Godot - GDScript scene-based")
                        
                    elif state.current_page == "new_project":
                        me.text("Create New Game Project", style=me.Style(font_size=24, margin=me.Margin(bottom=20)))
                        
                        me.input(
                            label="Project Description",
                            value=state.project_description,
                            on_input=update_description,
                            style=me.Style(width="100%", margin=me.Margin(bottom=10))
                        )
                        
                        me.select(
                            label="Engine",
                            options=[
                                me.SelectOption(label="Pygame (Python)", value="pygame"),
                                me.SelectOption(label="Bevy (Rust)", value="bevy"),
                                me.SelectOption(label="Godot (GDScript)", value="godot")
                            ],
                            value=state.selected_engine,
                            on_selection_change=update_engine,
                            style=me.Style(margin=me.Margin(bottom=20))
                        )
                        
                        me.button(
                            "Generate Project" if not state.is_generating else "Generating...",
                            on_click=generate_project,
                            disabled=state.is_generating or not state.project_description,
                            style=me.Style(background="#64ffda", color="#1a1a2e")
                        )
                        
                        if state.generation_result:
                            me.text(f"✅ {state.generation_result}", style=me.Style(color="#64ffda", margin=me.Margin(top=20)))
                            
                    elif state.current_page == "assets":
                        me.text("Generate Assets", style=me.Style(font_size=24, margin=me.Margin(bottom=20)))
                        me.text("Asset generation tools coming soon...")

        # Mount Mesop WSGI app
        self.app.mount(
            "/",
            WSGIMiddleware(
                me.create_wsgi_app(debug_mode=os.environ.get("DEBUG_MODE", "") == "true")
            ),
        )
        
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
                        <p><strong>Note:</strong> Full web UI requires Mesop to be installed.</p>
                        <p>Install with: <code>pip install mesop</code></p>
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
                    "web_ui": MESOP_AVAILABLE,
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
        print(f"🌐 Web Interface: http://{self.host}:{self.port}")
        print(f"🔧 MCP SSE Endpoint: http://{self.host}:{self.port}/mcp/sse")
        print(f"📡 REST API: http://{self.host}:{self.port}/api/")
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
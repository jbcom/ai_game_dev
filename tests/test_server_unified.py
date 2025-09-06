"""
Comprehensive tests for the unified server architecture.
Tests both MCP SSE and web interface functionality.
"""
import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient
from httpx import AsyncClient

from ai_game_dev.server.unified_server import UnifiedGameDevServer
from ai_game_dev.engines.base import GameGenerationResult


class TestUnifiedServer:
    """Test the unified server functionality."""
    
    @pytest.fixture
    def server(self):
        """Create a test server instance."""
        return UnifiedGameDevServer(host="127.0.0.1", port=8000)
    
    @pytest.fixture
    def client(self, server):
        """Create a test client."""
        return TestClient(server.app)
    
    def test_server_initialization(self, server):
        """Test server initializes correctly."""
        assert server.host == "127.0.0.1"
        assert server.port == 8000
        assert server.app is not None
        assert server.mcp is not None
    
    def test_health_endpoint(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert "services" in data
        assert data["services"]["mcp_sse"] is True
        assert data["services"]["web_ui"] is True
        assert "engines" in data["services"]
        assert "mcp_endpoint" in data["services"]
    
    def test_root_redirect(self, client):
        """Test root redirects to web interface."""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 200
        assert "web/dashboard" in response.text
    
    def test_web_dashboard_route(self, client):
        """Test web dashboard route."""
        response = client.get("/web/dashboard")
        assert response.status_code == 200
        assert "AI Game Development" in response.text or "AI Game Dev" in response.text
    
    def test_web_new_project_route(self, client):
        """Test new project route."""
        response = client.get("/web/new_project")
        assert response.status_code == 200
        assert "Create" in response.text or "Generate" in response.text
    
    def test_web_engines_route(self, client):
        """Test engines list route."""
        response = client.get("/web/engines")
        assert response.status_code == 200
        assert "Engine" in response.text
    
    @patch('ai_game_dev.server.unified_server.generate_for_engine')
    def test_web_generate_project_success(self, mock_generate, client):
        """Test successful project generation via web interface."""
        # Mock successful generation
        mock_result = GameGenerationResult(
            engine_type="pygame",
            main_files=["main.py", "game.py"],
            asset_requirements={"sprites": ["player.png"]},
            build_instructions=["python main.py"],
            project_path="/tmp/test_game",
            generated_files={"main.py": "import pygame"}
        )
        mock_generate.return_value = asyncio.Future()
        mock_generate.return_value.set_result(mock_result)
        
        response = client.post("/web/generate-project", data={
            "description": "A simple platformer game",
            "engine": "pygame",
            "complexity": "intermediate",
            "art_style": "modern"
        })
        
        assert response.status_code == 200
        assert "success" in response.text.lower() or "generated" in response.text.lower()
        mock_generate.assert_called_once()
    
    @patch('ai_game_dev.server.unified_server.generate_for_engine')
    def test_web_generate_project_failure(self, mock_generate, client):
        """Test failed project generation via web interface."""
        # Mock generation failure
        mock_generate.side_effect = Exception("Generation failed")
        
        response = client.post("/web/generate-project", data={
            "description": "A simple platformer game",
            "engine": "pygame"
        })
        
        assert response.status_code == 200
        assert "error" in response.text.lower() or "failed" in response.text.lower()
    
    def test_api_generate_endpoint_get(self, client):
        """Test API generate endpoint GET request."""
        response = client.get("/api/generate")
        assert response.status_code == 200
        data = response.json()
        assert "supported_engines" in data
        assert "complexity_levels" in data
        assert "art_styles" in data
    
    @patch('ai_game_dev.server.unified_server.generate_for_engine')
    def test_api_generate_endpoint_post(self, mock_generate, client):
        """Test API generate endpoint POST request."""
        # Mock successful generation
        mock_result = GameGenerationResult(
            engine_type="pygame",
            main_files=["main.py"],
            asset_requirements={},
            build_instructions=["python main.py"],
            project_path="/tmp/test",
            generated_files={"main.py": "print('Hello, Game!')"}
        )
        mock_generate.return_value = asyncio.Future()
        mock_generate.return_value.set_result(mock_result)
        
        response = client.post("/api/generate", json={
            "description": "Test game",
            "engine": "pygame",
            "complexity": "beginner"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "project_info" in data
        assert data["project_info"]["engine"] == "pygame"
    
    def test_api_engines_endpoint(self, client):
        """Test API engines endpoint."""
        response = client.get("/api/engines")
        assert response.status_code == 200
        data = response.json()
        assert "engines" in data
        assert len(data["engines"]) > 0
        
        # Check engine structure
        for engine_name, engine_info in data["engines"].items():
            assert "language" in engine_info
            assert "description" in engine_info
            assert "complexity" in engine_info
    
    def test_api_assets_endpoint_get(self, client):
        """Test API assets endpoint GET request."""
        response = client.get("/api/assets")
        assert response.status_code == 200
        data = response.json()
        assert "asset_types" in data
        assert "art_styles" in data
    
    @patch('ai_game_dev.server.unified_server.AssetTools')
    def test_api_assets_endpoint_post(self, mock_asset_tools, client):
        """Test API assets endpoint POST request."""
        # Mock asset tools
        mock_instance = Mock()
        mock_asset_tools.return_value = mock_instance
        
        response = client.post("/api/assets", json={
            "asset_type": "sprite",
            "description": "Player character",
            "style": "pixel"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "asset_type" in data


class TestMCPIntegration:
    """Test MCP server integration."""
    
    @pytest.fixture
    def server(self):
        """Create a test server instance."""
        return UnifiedGameDevServer()
    
    def test_mcp_tools_registration(self, server):
        """Test that MCP tools are properly registered."""
        # Check that MCP tools are registered
        tools = server.mcp.list_tools()
        tool_names = [tool.name for tool in tools]
        
        assert "generate_game" in tool_names
        assert "generate_assets" in tool_names
        assert "list_game_engines" in tool_names
    
    @patch('ai_game_dev.server.sse_transport.create_sse_server')
    def test_sse_server_mounting(self, mock_create_sse, server):
        """Test that SSE server is properly mounted."""
        # The SSE server should be mounted during setup
        server.setup_routes()
        mock_create_sse.assert_called_once_with(server.mcp)
    
    @pytest.mark.asyncio
    @patch('ai_game_dev.server.unified_server.generate_for_engine')
    async def test_mcp_generate_game_tool(self, mock_generate, server):
        """Test MCP generate_game tool."""
        # Mock successful generation
        mock_result = GameGenerationResult(
            engine_type="pygame",
            main_files=["main.py"],
            asset_requirements={},
            build_instructions=["python main.py"],
            project_path="/tmp/test",
            generated_files={"main.py": "import pygame"}
        )
        mock_generate.return_value = mock_result
        
        # Get the generate_game tool
        tools = {tool.name: tool for tool in server.mcp.list_tools()}
        generate_tool = tools["generate_game"]
        
        # Call the tool
        result = await generate_tool.fn(
            engine_name="pygame",
            description="Test game",
            complexity="beginner",
            features=[],
            art_style="modern"
        )
        
        assert result["success"] is True
        assert result["engine_type"] == "pygame"
        assert "main_files" in result
        mock_generate.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_mcp_list_engines_tool(self, server):
        """Test MCP list_game_engines tool."""
        # Get the list_game_engines tool
        tools = {tool.name: tool for tool in server.mcp.list_tools()}
        list_engines_tool = tools["list_game_engines"]
        
        # Call the tool
        result = await list_engines_tool.fn()
        
        assert "engines" in result
        assert len(result["engines"]) > 0
        assert "pygame" in result["engines"]
    
    @pytest.mark.asyncio
    @patch('ai_game_dev.server.unified_server.AssetTools')
    async def test_mcp_generate_assets_tool(self, mock_asset_tools, server):
        """Test MCP generate_assets tool."""
        # Mock asset tools
        mock_instance = Mock()
        mock_asset_tools.return_value = mock_instance
        
        # Get the generate_assets tool
        tools = {tool.name: tool for tool in server.mcp.list_tools()}
        assets_tool = tools["generate_assets"]
        
        # Call the tool
        result = await assets_tool.fn(
            asset_type="sprite",
            description="Player character",
            style="pixel",
            requirements={}
        )
        
        assert "success" in result
        assert result["asset_type"] == "sprite"


class TestServerConfiguration:
    """Test server configuration and environment handling."""
    
    def test_server_with_custom_config(self):
        """Test server with custom configuration."""
        server = UnifiedGameDevServer(host="0.0.0.0", port=9000)
        assert server.host == "0.0.0.0"
        assert server.port == 9000
    
    @patch.dict('os.environ', {'DEBUG_MODE': 'true'})
    def test_debug_mode_configuration(self):
        """Test server configuration in debug mode."""
        server = UnifiedGameDevServer()
        # Should handle debug mode without errors
        assert server.app is not None
    
    def test_cors_middleware_configuration(self):
        """Test CORS middleware is properly configured."""
        server = UnifiedGameDevServer()
        
        # Check that CORS middleware is added
        middleware_types = [type(middleware) for middleware in server.app.user_middleware]
        from starlette.middleware.cors import CORSMiddleware
        assert any(issubclass(mw_type, CORSMiddleware) for mw_type in middleware_types)


@pytest.mark.asyncio
class TestAsyncServerOperations:
    """Test async server operations."""
    
    async def test_async_server_startup(self):
        """Test async server startup process."""
        server = UnifiedGameDevServer()
        
        # Should be able to access app without errors
        assert server.app is not None
        
        # Test async client
        async with AsyncClient(app=server.app, base_url="http://test") as client:
            response = await client.get("/health")
            assert response.status_code == 200
    
    @patch('ai_game_dev.server.unified_server.generate_for_engine')
    async def test_concurrent_project_generation(self, mock_generate):
        """Test handling concurrent project generation requests."""
        server = UnifiedGameDevServer()
        
        # Mock generation with delay
        async def mock_gen(*args, **kwargs):
            await asyncio.sleep(0.1)  # Simulate work
            return GameGenerationResult(
                engine_type="pygame",
                main_files=["main.py"],
                asset_requirements={},
                build_instructions=["python main.py"],
                project_path="/tmp/test",
                generated_files={"main.py": "import pygame"}
            )
        
        mock_generate.side_effect = mock_gen
        
        # Make concurrent requests
        async with AsyncClient(app=server.app, base_url="http://test") as client:
            tasks = []
            for i in range(3):
                task = client.post("/api/generate", json={
                    "description": f"Test game {i}",
                    "engine": "pygame",
                    "complexity": "beginner"
                })
                tasks.append(task)
            
            responses = await asyncio.gather(*tasks)
            
            # All requests should succeed
            for response in responses:
                assert response.status_code == 200
                data = response.json()
                assert data["success"] is True


# Test file - no main execution needed
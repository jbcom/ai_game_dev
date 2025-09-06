"""
Comprehensive tests for HTMY web interface components.
Tests component rendering, state management, and interactions.
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient

# Try to import HTMY components
try:
    from ai_game_dev.server.htmy_interface import (
        setup_htmy_routes, 
        GameDevUser, 
        AppState,
        make_htmy_context,
        render
    )
    HTMY_AVAILABLE = True
except ImportError:
    HTMY_AVAILABLE = False


@pytest.mark.skipif(not HTMY_AVAILABLE, reason="HTMY not available")
class TestHTMYInterface:
    """Test HTMY web interface functionality."""
    
    @pytest.fixture
    def app_with_htmy(self):
        """Create FastAPI app with HTMY routes."""
        from fastapi import FastAPI
        app = FastAPI()
        setup_htmy_routes(app)
        return app
    
    @pytest.fixture
    def client(self, app_with_htmy):
        """Create test client with HTMY interface."""
        return TestClient(app_with_htmy)
    
    def test_htmy_context_creation(self):
        """Test HTMY context creation."""
        from fastapi import Request
        
        # Mock request
        mock_request = Mock(spec=Request)
        mock_request.url = Mock()
        mock_request.url.path = "/test"
        
        context = make_htmy_context(mock_request)
        
        assert Request in context
        assert GameDevUser in context
        assert AppState in context
        assert context[Request] == mock_request
        assert isinstance(context[GameDevUser], GameDevUser)
        assert isinstance(context[AppState], AppState)
    
    def test_gamedev_user_model(self):
        """Test GameDevUser data model."""
        user = GameDevUser()
        assert user.name == "Game Developer"
        assert user.preferred_theme == "dark"
        
        custom_user = GameDevUser(name="Test User", preferred_theme="light")
        assert custom_user.name == "Test User"
        assert custom_user.preferred_theme == "light"
    
    def test_app_state_model(self):
        """Test AppState data model."""
        state = AppState()
        assert state.current_project is None
        assert state.last_generation_result is None
        assert state.is_generating is False
        
        custom_state = AppState(
            current_project="test_game",
            last_generation_result="Success",
            is_generating=True
        )
        assert custom_state.current_project == "test_game"
        assert custom_state.last_generation_result == "Success"
        assert custom_state.is_generating is True
    
    def test_dashboard_route(self, client):
        """Test dashboard route renders correctly."""
        response = client.get("/web/dashboard")
        assert response.status_code == 200
        
        content = response.text
        assert "AI Game Development" in content
        assert "Dashboard" in content
        assert "dark" in content  # Theme should be applied
    
    def test_new_project_route(self, client):
        """Test new project route renders correctly."""
        response = client.get("/web/new_project")
        assert response.status_code == 200
        
        content = response.text
        assert "Create New Game Project" in content
        assert "form" in content.lower()
        assert "engine" in content.lower()
        assert "description" in content.lower()
    
    def test_engines_route(self, client):
        """Test engines route renders correctly."""
        response = client.get("/web/engines")
        assert response.status_code == 200
        
        content = response.text
        assert "Engine" in content
        assert "pygame" in content.lower() or "Pygame" in content
    
    @patch('ai_game_dev.server.htmy_interface.generate_for_engine')
    def test_project_generation_success(self, mock_generate, client):
        """Test successful project generation through HTMY interface."""
        from ai_game_dev.engines.base import GameGenerationResult
        import asyncio
        
        # Mock successful generation
        mock_result = GameGenerationResult(
            engine_type="pygame",
            main_files=["main.py", "game.py"],
            asset_requirements={"sprites": ["player.png"]},
            build_instructions=["python main.py"],
            project_path="/tmp/test_game",
            generated_files={"main.py": "import pygame"}
        )
        
        # Create a future that resolves to our mock result
        future = asyncio.Future()
        future.set_result(mock_result)
        mock_generate.return_value = future
        
        response = client.post("/web/generate-project", data={
            "description": "A test platformer game",
            "engine": "pygame",
            "complexity": "intermediate",
            "art_style": "modern"
        })
        
        assert response.status_code == 200
        content = response.text
        assert "success" in content.lower()
        assert "pygame" in content.lower()
        
        mock_generate.assert_called_once_with(
            engine_name="pygame",
            description="A test platformer game",
            complexity="intermediate",
            features=[],
            art_style="modern"
        )
    
    @patch('ai_game_dev.server.htmy_interface.generate_for_engine')
    def test_project_generation_failure(self, mock_generate, client):
        """Test failed project generation through HTMY interface."""
        # Mock generation failure
        mock_generate.side_effect = Exception("Generation failed for test")
        
        response = client.post("/web/generate-project", data={
            "description": "A test game",
            "engine": "pygame"
        })
        
        assert response.status_code == 200
        content = response.text
        assert "error" in content.lower() or "failed" in content.lower()
        assert "Generation failed for test" in content
    
    def test_navigation_consistency(self, client):
        """Test navigation is consistent across pages."""
        pages = ["/web/dashboard", "/web/new_project", "/web/engines"]
        
        for page in pages:
            response = client.get(page)
            assert response.status_code == 200
            
            content = response.text
            # Each page should have navigation elements
            assert "Dashboard" in content
            assert "New Project" in content
            assert "Engines" in content
    
    def test_responsive_design_elements(self, client):
        """Test that responsive design elements are present."""
        response = client.get("/web/dashboard")
        assert response.status_code == 200
        
        content = response.text
        # Check for TailwindCSS and DaisyUI classes
        assert "tailwindcss" in content
        assert "daisyui" in content
        assert "min-h-screen" in content
        assert "game-dev-bg" in content
    
    def test_accessibility_features(self, client):
        """Test accessibility features in the interface."""
        response = client.get("/web/new_project")
        assert response.status_code == 200
        
        content = response.text
        # Check for proper HTML structure
        assert "<!DOCTYPE html>" in content
        assert 'lang="en"' in content
        assert "<title>" in content
        assert "label" in content  # Form labels
    
    def test_security_headers(self, client):
        """Test security-related headers and features."""
        response = client.get("/web/dashboard")
        assert response.status_code == 200
        
        content = response.text
        # Check for security policy configuration
        assert "SecurityPolicy" in content or "security" in content.lower()
    
    @patch('ai_game_dev.server.htmy_interface.get_supported_engines')
    def test_dynamic_engine_loading(self, mock_engines, client):
        """Test dynamic loading of available engines."""
        # Mock available engines
        mock_engines.return_value = ["pygame", "bevy", "godot", "test_engine"]
        
        response = client.get("/web/new_project")
        assert response.status_code == 200
        
        content = response.text
        # Should include all mocked engines
        assert "pygame" in content.lower()
        assert "bevy" in content.lower()
        assert "godot" in content.lower()
        assert "test_engine" in content.lower()
    
    def test_form_validation_attributes(self, client):
        """Test that forms have proper validation attributes."""
        response = client.get("/web/new_project")
        assert response.status_code == 200
        
        content = response.text
        # Check for HTML5 validation attributes
        assert "required" in content
        assert "placeholder" in content
        assert 'type="submit"' in content
    
    def test_htmx_integration(self, client):
        """Test HTMX integration for dynamic interactions."""
        response = client.get("/web/new_project")
        assert response.status_code == 200
        
        content = response.text
        # Check for HTMX attributes
        assert "hx-post" in content
        assert "hx-target" in content
        assert "hx-indicator" in content
        assert "htmx.org" in content  # HTMX script inclusion
    
    def test_loading_indicators(self, client):
        """Test loading indicators are properly configured."""
        response = client.get("/web/new_project")
        assert response.status_code == 200
        
        content = response.text
        # Check for loading indicator elements
        assert "loading" in content
        assert "htmx-indicator" in content
    
    def test_error_handling_display(self, client):
        """Test error handling and display mechanisms."""
        # Test with invalid form data
        response = client.post("/web/generate-project", data={
            "description": "",  # Empty description should cause validation issues
            "engine": "invalid_engine"
        })
        
        # Should handle gracefully
        assert response.status_code in [200, 400, 422]  # Various acceptable error responses
    
    def test_theme_consistency(self, client):
        """Test theme consistency across all pages."""
        pages = ["/web/dashboard", "/web/new_project", "/web/engines"]
        
        for page in pages:
            response = client.get(page)
            assert response.status_code == 200
            
            content = response.text
            # All pages should use dark theme consistently
            assert 'data-theme="dark"' in content
            assert "game-dev-bg" in content
    
    @patch('ai_game_dev.server.htmy_interface.engine_manager')
    def test_engine_info_display(self, mock_manager, client):
        """Test engine information display."""
        # Mock engine manager
        mock_manager.get_engine_info.return_value = {
            "language": "Python",
            "description": "2D game development",
            "complexity": "beginner"
        }
        
        response = client.get("/web/engines")
        assert response.status_code == 200
        
        content = response.text
        # Should display engine information
        assert "Python" in content or "python" in content.lower()


@pytest.mark.skipif(HTMY_AVAILABLE, reason="Testing fallback when HTMY not available")
class TestHTMYFallback:
    """Test behavior when HTMY is not available."""
    
    def test_import_fallback(self):
        """Test that the system handles missing HTMY gracefully."""
        # When HTMY is not available, should fall back to simple interface
        from ai_game_dev.server.unified_server import UnifiedGameDevServer
        
        server = UnifiedGameDevServer()
        client = TestClient(server.app)
        
        # Should still serve web interface using fallback
        response = client.get("/web/dashboard")
        assert response.status_code == 200
        
        # Should contain basic web interface elements
        content = response.text
        assert "AI Game Dev" in content or "Game Development" in content


# Test file - no main execution needed
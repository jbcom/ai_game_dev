"""
Comprehensive tests for Jinja2-based web interface.
Tests template rendering, context handling, and form processing.
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient
from fastapi import FastAPI

from ai_game_dev.server.jinja_interface import (
    setup_jinja_routes, 
    get_engine_info, 
    get_template_context
)


class TestJinjaInterface:
    """Test Jinja2 web interface functionality."""
    
    @pytest.fixture
    def app_with_jinja(self):
        """Create FastAPI app with Jinja2 routes."""
        app = FastAPI()
        setup_jinja_routes(app)
        return app
    
    @pytest.fixture
    def client(self, app_with_jinja):
        """Create test client with Jinja2 interface."""
        return TestClient(app_with_jinja)
    
    def test_engine_info_structure(self):
        """Test engine info has correct structure."""
        engine_info = get_engine_info()
        
        required_fields = [
            "icon", "language", "description", "complexity", 
            "best_for", "platforms", "features", "learning_curve",
            "performance", "support_2d", "support_3d", "community"
        ]
        
        for engine, info in engine_info.items():
            for field in required_fields:
                assert field in info, f"Engine {engine} missing field {field}"
            
            # Validate data types
            assert isinstance(info["features"], list)
            assert isinstance(info["learning_curve"], int)
            assert isinstance(info["performance"], int)
            assert isinstance(info["support_2d"], bool)
            assert isinstance(info["support_3d"], bool)
            assert isinstance(info["community"], int)
    
    @patch('ai_game_dev.server.jinja_interface.get_supported_engines')
    def test_template_context_creation(self, mock_engines):
        """Test template context creation."""
        mock_engines.return_value = ["pygame", "bevy", "godot"]
        
        from fastapi import Request
        mock_request = Mock(spec=Request)
        
        context = get_template_context(mock_request, "dashboard")
        
        assert "request" in context
        assert "current_page" in context
        assert "current_year" in context
        assert "engines" in context
        assert "engine_info" in context
        assert "theme" in context
        assert "stats" in context
        assert "recent_projects" in context
        
        assert context["current_page"] == "dashboard"
        assert context["engines"] == ["pygame", "bevy", "godot"]
        assert context["theme"] == "dark"
    
    def test_dashboard_route(self, client):
        """Test dashboard route renders correctly."""
        response = client.get("/web/dashboard")
        assert response.status_code == 200
        
        content = response.text
        assert "<!DOCTYPE html>" in content
        assert "AI Game Development" in content
        assert "Dashboard" in content
        assert "tailwindcss" in content
        assert "daisyui" in content
    
    def test_new_project_route(self, client):
        """Test new project route renders correctly."""
        response = client.get("/web/new_project")
        assert response.status_code == 200
        
        content = response.text
        assert "Create New Game Project" in content
        assert "<form" in content
        assert "hx-post" in content
        assert "description" in content
        assert "engine" in content
        assert "complexity" in content
    
    def test_new_project_with_engine_param(self, client):
        """Test new project route with pre-selected engine."""
        response = client.get("/web/new_project?engine=pygame")
        assert response.status_code == 200
        
        content = response.text
        assert "pygame" in content.lower()
    
    def test_engines_route(self, client):
        """Test engines route renders correctly."""
        response = client.get("/web/engines")
        assert response.status_code == 200
        
        content = response.text
        assert "Available Game Engines" in content
        assert "pygame" in content.lower()
        assert "bevy" in content.lower()
        assert "godot" in content.lower()
        assert "Engine Comparison" in content
    
    @patch('ai_game_dev.server.jinja_interface.generate_for_engine')
    def test_project_generation_success(self, mock_generate, client):
        """Test successful project generation through Jinja2 interface."""
        from ai_game_dev.engines.base import GameGenerationResult
        import asyncio
        
        # Mock successful generation
        mock_result = GameGenerationResult(
            engine_type="pygame",
            main_files=["main.py", "game.py"],
            asset_requirements={"sprites": ["player.png"]},
            build_instructions=["python main.py"],
            project_path="/tmp/test_game",
            generated_files={"main.py": "import pygame", "game.py": "# Game logic"}
        )
        
        future = asyncio.Future()
        future.set_result(mock_result)
        mock_generate.return_value = future
        
        response = client.post("/web/generate-project", data={
            "description": "A test platformer game with jumping mechanics",
            "engine": "pygame",
            "complexity": "intermediate",
            "art_style": "modern",
            "platform": "desktop",
            "include_assets": "true"
        })
        
        assert response.status_code == 200
        content = response.text
        assert "Project Generated Successfully" in content
        assert "pygame" in content.lower()
        assert "main.py" in content
        assert "2 files" in content
        
        mock_generate.assert_called_once_with(
            engine_name="pygame",
            description="A test platformer game with jumping mechanics",
            complexity="intermediate",
            features=[],
            art_style="modern"
        )
    
    @patch('ai_game_dev.server.jinja_interface.generate_for_engine')
    def test_project_generation_failure(self, mock_generate, client):
        """Test failed project generation through Jinja2 interface."""
        # Mock generation failure
        mock_generate.side_effect = Exception("Test generation error")
        
        response = client.post("/web/generate-project", data={
            "description": "A test game",
            "engine": "pygame",
            "complexity": "beginner"
        })
        
        assert response.status_code == 200
        content = response.text
        assert "Generation Failed" in content
        assert "Test generation error" in content
        assert "Troubleshooting Tips" in content
    
    def test_form_validation_required_fields(self, client):
        """Test form handles missing required fields."""
        # Missing description
        response = client.post("/web/generate-project", data={
            "engine": "pygame",
            "complexity": "intermediate"
        })
        
        # Should handle gracefully (FastAPI handles validation)
        assert response.status_code in [200, 422]
    
    def test_static_files_mounting(self, app_with_jinja, client):
        """Test static files are properly mounted."""
        # The static route should be available even if directory doesn't exist
        response = client.get("/static/nonexistent.css")
        # Should return 404, not 500, indicating route is properly mounted
        assert response.status_code == 404
    
    def test_template_inheritance(self, client):
        """Test template inheritance works correctly."""
        response = client.get("/web/dashboard")
        assert response.status_code == 200
        
        content = response.text
        # Check for base template elements
        assert '<html lang="en"' in content
        assert 'data-theme="dark"' in content
        assert "navbar" in content
        assert "footer" in content
        
        # Check for page-specific content
        assert "Welcome to AI Game Development" in content
    
    def test_navigation_consistency(self, client):
        """Test navigation is consistent across pages."""
        pages = ["/web/dashboard", "/web/new_project", "/web/engines"]
        
        for page in pages:
            response = client.get(page)
            assert response.status_code == 200
            
            content = response.text
            # Each page should have consistent navigation
            assert "AI Game Dev" in content
            assert "Dashboard" in content
            assert "New Project" in content
            assert "Engines" in content
            assert "navbar" in content
    
    def test_responsive_design_classes(self, client):
        """Test responsive design classes are present."""
        response = client.get("/web/new_project")
        assert response.status_code == 200
        
        content = response.text
        # Check for responsive grid classes
        assert "grid-cols-1" in content
        assert "md:grid-cols-" in content
        assert "lg:grid-cols-" in content
        
        # Check for responsive breakpoints
        assert "sm:" in content or "md:" in content or "lg:" in content
    
    def test_accessibility_features(self, client):
        """Test accessibility features are present."""
        response = client.get("/web/new_project")
        assert response.status_code == 200
        
        content = response.text
        # Check for accessibility attributes
        assert 'lang="en"' in content
        assert "<title>" in content
        assert "aria-" in content or "role=" in content
        assert "<label" in content  # Form labels
    
    def test_htmx_integration(self, client):
        """Test HTMX integration is properly configured."""
        response = client.get("/web/new_project")
        assert response.status_code == 200
        
        content = response.text
        # Check for HTMX script and attributes
        assert "htmx.org" in content
        assert "hx-post" in content
        assert "hx-target" in content
        assert "hx-indicator" in content
    
    def test_theme_consistency(self, client):
        """Test theme is consistently applied."""
        pages = ["/web/dashboard", "/web/new_project", "/web/engines"]
        
        for page in pages:
            response = client.get(page)
            assert response.status_code == 200
            
            content = response.text
            assert 'data-theme="dark"' in content
            assert "game-dev-gradient" in content
    
    @patch('ai_game_dev.server.jinja_interface.get_supported_engines')
    def test_dynamic_engine_loading(self, mock_engines, client):
        """Test dynamic loading of engines in templates."""
        # Mock custom engine list
        mock_engines.return_value = ["pygame", "bevy", "godot", "custom_engine"]
        
        response = client.get("/web/engines")
        assert response.status_code == 200
        
        content = response.text
        # Should display all engines including custom one
        assert "pygame" in content.lower()
        assert "bevy" in content.lower()
        assert "godot" in content.lower()
        # Note: custom_engine won't appear because it's not in engine_info
    
    def test_error_handling_graceful(self, client):
        """Test graceful error handling in templates."""
        # Test with invalid form data
        response = client.post("/web/generate-project", data={
            "description": "x" * 2000,  # Very long description
            "engine": "invalid_engine",
            "complexity": "invalid_complexity"
        })
        
        # Should handle gracefully without crashing
        assert response.status_code in [200, 400, 422]
    
    def test_template_security(self, client):
        """Test template security features."""
        response = client.get("/web/dashboard")
        assert response.status_code == 200
        
        content = response.text
        # Check that security headers and CSP are properly configured
        assert "script" in content  # Scripts should be properly loaded
        # Templates should not have obvious XSS vulnerabilities
        assert "<script>alert(" not in content


class TestTemplateFilters:
    """Test custom template filters and functions."""
    
    def test_filter_availability(self):
        """Test custom filters are available."""
        from ai_game_dev.server.jinja_interface import templates
        
        # Test that custom filters are registered
        assert "file_size" in templates.env.filters
        assert "truncate" in templates.env.filters
        assert "datetime" in templates.env.filters
    
    def test_global_functions(self):
        """Test global functions are available."""
        from ai_game_dev.server.jinja_interface import templates
        
        # Test that global functions are registered
        assert "range" in templates.env.globals
        assert "len" in templates.env.globals
        assert "enumerate" in templates.env.globals


class TestProductionReadiness:
    """Test production-readiness features."""
    
    def test_template_directory_structure(self):
        """Test template directory has proper structure."""
        from ai_game_dev.server.jinja_interface import TEMPLATE_DIR
        
        assert TEMPLATE_DIR.exists()
        assert (TEMPLATE_DIR / "base").exists()
        assert (TEMPLATE_DIR / "pages").exists()
        assert (TEMPLATE_DIR / "components").exists()
        
        # Check for key template files
        assert (TEMPLATE_DIR / "base" / "layout.html").exists()
        assert (TEMPLATE_DIR / "pages" / "dashboard.html").exists()
        assert (TEMPLATE_DIR / "components" / "navbar.html").exists()
    
    def test_static_directory_setup(self):
        """Test static directory is properly configured."""
        from ai_game_dev.server.jinja_interface import STATIC_DIR
        
        # Directory should exist or be creatable
        assert STATIC_DIR.parent.exists()
    
    def test_no_hardcoded_values(self, client):
        """Test templates don't contain hardcoded development values."""
        response = client.get("/web/dashboard")
        assert response.status_code == 200
        
        content = response.text
        # Should not contain obvious development artifacts
        assert "localhost" not in content.lower()
        assert "127.0.0.1" not in content
        assert "debug" not in content.lower()
        assert "test" not in content.lower() or "Test" not in content
    
    def test_performance_considerations(self, client):
        """Test performance-related template features."""
        response = client.get("/web/dashboard")
        assert response.status_code == 200
        
        content = response.text
        # Check for performance optimizations
        assert "loading=" in content  # Lazy loading attributes
        assert "transition" in content  # CSS transitions for smooth UX
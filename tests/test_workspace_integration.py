"""Integration tests for the AI Game Development workspace."""

import pytest
import subprocess
import sys
from pathlib import Path


class TestWorkspaceIntegration:
    """Test workspace-level functionality and cross-package compatibility."""
    
    def test_package_imports(self):
        """Test that all packages can be imported successfully."""
        try:
            import ai_game_dev
            import ai_game_assets
            assert ai_game_dev.__version__
            assert ai_game_assets.__version__
        except ImportError as e:
            pytest.fail(f"Failed to import core packages: {e}")
    
    def test_engine_package_imports(self):
        """Test engine-specific packages import correctly."""
        try:
            # These may fail if pygame/arcade aren't installed, which is expected
            import pygame_game_dev
            import arcade_game_dev
            assert hasattr(pygame_game_dev, 'generate_pygame_project')
            assert hasattr(arcade_game_dev, 'generate_arcade_project')
        except ImportError:
            # Expected in CI environments without game engines
            pytest.skip("Engine packages not available in test environment")
    
    def test_workspace_dependency_resolution(self):
        """Test that workspace dependencies resolve correctly."""
        result = subprocess.run(
            [sys.executable, "-c", "import ai_game_dev; print('OK')"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0
        assert "OK" in result.stdout
    
    def test_cross_package_functionality(self):
        """Test that packages can work together."""
        from ai_game_dev import AIGameDev
        from ai_game_assets import AssetGenerator
        
        # Test basic instantiation
        game_dev = AIGameDev()
        asset_gen = AssetGenerator()
        
        assert game_dev is not None
        assert asset_gen is not None
    
    def test_package_metadata(self):
        """Test that all packages have proper metadata."""
        packages = ['ai_game_dev', 'ai_game_assets']
        
        for pkg_name in packages:
            try:
                pkg = __import__(pkg_name)
                assert hasattr(pkg, '__version__')
                assert hasattr(pkg, '__author__') or hasattr(pkg, '__author_email__')
            except ImportError:
                pytest.fail(f"Package {pkg_name} not found")


class TestPackageBuilds:
    """Test that packages can be built successfully."""
    
    def test_python_package_builds(self):
        """Test that Python packages build without errors."""
        packages = [
            'packages/ai_game_dev',
            'packages/ai_game_assets', 
            'packages/pygame_game_dev',
            'packages/arcade_game_dev'
        ]
        
        for pkg_dir in packages:
            if Path(pkg_dir).exists():
                result = subprocess.run(
                    ['uv', 'build', '--wheel'],
                    cwd=pkg_dir,
                    capture_output=True,
                    text=True
                )
                assert result.returncode == 0, f"Failed to build {pkg_dir}: {result.stderr}"
    
    def test_rust_package_builds(self):
        """Test that Rust packages build without errors."""
        rust_pkg = Path('packages/bevy_game_dev')
        if rust_pkg.exists():
            result = subprocess.run(
                ['cargo', 'check'],
                cwd=rust_pkg,
                capture_output=True,
                text=True
            )
            assert result.returncode == 0, f"Rust package check failed: {result.stderr}"


class TestAPICompatibility:
    """Test API compatibility across packages."""
    
    def test_engine_adapter_interface(self):
        """Test that engine adapters follow consistent interface."""
        try:
            from ai_game_dev.engine_adapters import EngineAdapter
            
            # Test that base interface exists
            assert hasattr(EngineAdapter, 'generate_project')
            assert hasattr(EngineAdapter, 'validate_spec')
            
        except ImportError:
            pytest.skip("Engine adapters not available")
    
    def test_asset_generation_interface(self):
        """Test asset generation API consistency."""
        try:
            from ai_game_assets import AssetGenerator
            
            generator = AssetGenerator()
            assert hasattr(generator, 'generate_image')
            assert hasattr(generator, 'generate_audio')
            
        except ImportError:
            pytest.skip("Asset generator not available")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
"""Tests for deployment modules."""
import pytest
from unittest.mock import patch, MagicMock, AsyncMock, mock_open
from pathlib import Path
import json

from ai_game_dev.deployment.deploy_manager import DeploymentManager, DeploymentConfig
from ai_game_dev.deployment.pygbag_deploy import PygbagDeployer


class TestDeploymentConfig:
    """Test DeploymentConfig class."""
    
    def test_deployment_config_default(self):
        """Test default deployment config."""
        config = DeploymentConfig()
        assert config.target_platform == "web"
        assert config.output_format == "html5"
        assert config.optimization_level == "balanced"
        assert config.include_assets is True
        assert config.minify_code is False
        assert config.enable_pwa is False
    
    def test_deployment_config_custom(self):
        """Test custom deployment config."""
        config = DeploymentConfig(
            project_path=Path("/test/project"),
            target_platform="mobile",
            output_format="apk",
            optimization_level="high",
            minify_code=True,
            enable_pwa=True
        )
        assert config.project_path == Path("/test/project")
        assert config.target_platform == "mobile"
        assert config.output_format == "apk"
        assert config.optimization_level == "high"
        assert config.minify_code is True
        assert config.enable_pwa is True


class TestDeploymentManager:
    """Test DeploymentManager class."""
    
    def test_init(self):
        """Test deployment manager initialization."""
        manager = DeploymentManager()
        assert manager.deployers == {}
        assert manager.current_deployment is None
    
    def test_register_deployer(self):
        """Test registering a deployer."""
        manager = DeploymentManager()
        deployer = MagicMock()
        
        manager.register_deployer("test", deployer)
        assert "test" in manager.deployers
        assert manager.deployers["test"] == deployer
    
    @pytest.mark.asyncio
    async def test_deploy_pygame_to_web(self):
        """Test deploying pygame to web."""
        manager = DeploymentManager()
        
        with patch.object(manager, '_deploy_pygame_web') as mock_deploy:
            mock_deploy.return_value = {
                "success": True,
                "url": "http://localhost:8080"
            }
            
            config = DeploymentConfig(
                project_path=Path("/test/game"),
                target_platform="web"
            )
            
            result = await manager.deploy("pygame", config)
            
            assert result["success"] is True
            assert "url" in result
            mock_deploy.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_deploy_unsupported_engine(self):
        """Test deploying unsupported engine."""
        manager = DeploymentManager()
        config = DeploymentConfig()
        
        with pytest.raises(ValueError, match="Unsupported engine"):
            await manager.deploy("unknown_engine", config)
    
    @pytest.mark.asyncio
    async def test_deploy_pygame_web_implementation(self):
        """Test pygame web deployment implementation."""
        manager = DeploymentManager()
        config = DeploymentConfig(
            project_path=Path("/test/game"),
            optimization_level="high"
        )
        
        with patch('ai_game_dev.deployment.deploy_manager.PygbagDeployer') as MockDeployer:
            mock_deployer = AsyncMock()
            mock_deployer.deploy.return_value = {
                "success": True,
                "build_path": "/test/build"
            }
            MockDeployer.return_value = mock_deployer
            
            result = await manager._deploy_pygame_web(config)
            
            assert result["success"] is True
            MockDeployer.assert_called_once()
            mock_deployer.deploy.assert_called_once_with(config)
    
    def test_get_deployment_status_none(self):
        """Test getting deployment status when none exists."""
        manager = DeploymentManager()
        status = manager.get_deployment_status()
        
        assert status["status"] == "none"
        assert status["message"] == "No deployment in progress"
    
    def test_get_deployment_status_active(self):
        """Test getting deployment status when active."""
        manager = DeploymentManager()
        manager.current_deployment = {
            "engine": "pygame",
            "platform": "web",
            "status": "building",
            "progress": 50
        }
        
        status = manager.get_deployment_status()
        
        assert status["status"] == "building"
        assert status["progress"] == 50


class TestPygbagDeployer:
    """Test PygbagDeployer class."""
    
    def test_init(self):
        """Test pygbag deployer initialization."""
        deployer = PygbagDeployer()
        assert deployer.pygbag_version == "0.8.0"
        assert deployer.python_version == "3.11"
    
    @pytest.mark.asyncio
    async def test_deploy_success(self):
        """Test successful pygbag deployment."""
        deployer = PygbagDeployer()
        config = DeploymentConfig(
            project_path=Path("/test/game"),
            output_dir=Path("/test/output")
        )
        
        with patch.object(deployer, '_check_requirements', return_value=True):
            with patch.object(deployer, '_prepare_project') as mock_prepare:
                with patch.object(deployer, '_run_pygbag') as mock_run:
                    with patch.object(deployer, '_create_index_html') as mock_index:
                        mock_run.return_value = True
                        
                        result = await deployer.deploy(config)
                        
                        assert result["success"] is True
                        assert "build_path" in result
                        mock_prepare.assert_called_once()
                        mock_run.assert_called_once()
                        mock_index.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_deploy_requirements_fail(self):
        """Test deployment when requirements check fails."""
        deployer = PygbagDeployer()
        config = DeploymentConfig(project_path=Path("/test/game"))
        
        with patch.object(deployer, '_check_requirements', return_value=False):
            result = await deployer.deploy(config)
            
            assert result["success"] is False
            assert "pygbag not installed" in result["error"]
    
    @pytest.mark.asyncio
    async def test_check_requirements(self):
        """Test checking pygbag requirements."""
        deployer = PygbagDeployer()
        
        with patch('subprocess.run') as mock_run:
            # Simulate pygbag installed
            mock_run.return_value = MagicMock(returncode=0)
            
            result = await deployer._check_requirements()
            
            assert result is True
            mock_run.assert_called()
    
    @pytest.mark.asyncio
    async def test_prepare_project(self):
        """Test project preparation."""
        deployer = PygbagDeployer()
        config = DeploymentConfig(
            project_path=Path("/test/game"),
            output_dir=Path("/test/output")
        )
        
        with patch('shutil.copytree') as mock_copy:
            with patch('pathlib.Path.mkdir') as mock_mkdir:
                with patch.object(deployer, '_modify_for_web') as mock_modify:
                    await deployer._prepare_project(config)
                    
                    mock_mkdir.assert_called()
                    mock_copy.assert_called_once()
                    mock_modify.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_modify_for_web(self):
        """Test modifying project for web."""
        deployer = PygbagDeployer()
        project_path = Path("/test/game")
        
        main_content = '''
import pygame

def main():
    pygame.init()
    # Game code here
    
if __name__ == "__main__":
    main()
'''
        
        expected_content = '''
import pygame
import asyncio

async def main():
    pygame.init()
    # Game code here
    
if __name__ == "__main__":
    asyncio.run(main())
'''
        
        with patch('builtins.open', mock_open(read_data=main_content)) as mock_file:
            await deployer._modify_for_web(project_path)
            
            # Check file was read and written
            mock_file.assert_called()
            handle = mock_file()
            handle.write.assert_called()
    
    @pytest.mark.asyncio
    async def test_create_index_html(self):
        """Test creating index.html."""
        deployer = PygbagDeployer()
        output_dir = Path("/test/output")
        game_title = "Test Game"
        
        with patch('builtins.open', mock_open()) as mock_file:
            await deployer._create_index_html(output_dir, game_title)
            
            mock_file.assert_called_with(output_dir / "index.html", "w")
            handle = mock_file()
            handle.write.assert_called()
            
            # Check HTML content includes game title
            written_content = "".join(call[0][0] for call in handle.write.call_args_list)
            assert game_title in written_content
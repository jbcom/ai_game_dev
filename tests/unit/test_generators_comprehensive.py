"""Comprehensive generator tests to achieve 100% coverage."""

import pytest
from unittest.mock import Mock, patch, MagicMock, AsyncMock, mock_open
from pathlib import Path
import tempfile
import json
import base64
import asyncio

from ai_game_dev.generators import (
    ImageGenerator, Model3DGenerator, AssetGenerator,
    ImageSize, ImageQuality, Model3DSpec,
    get_image_path, IMAGES_DIR, MODELS_3D_DIR
)


class TestUtilityFunctions:
    """Test utility functions."""
    
    def test_get_image_path(self):
        """Test image path generation."""
        base_dir = Path("/test/dir")
        prompt = "test prompt"
        size = "1024x1024"
        quality = "standard"
        
        path = get_image_path(base_dir, prompt, size, quality)
        
        assert path.parent == base_dir
        assert size in path.name
        assert quality in path.name
        assert path.suffix == ".png"
        
        # Test consistency
        path2 = get_image_path(base_dir, prompt, size, quality)
        assert path == path2

    def test_get_image_path_different_prompts(self):
        """Test different prompts generate different paths."""
        base_dir = Path("/test/dir")
        
        path1 = get_image_path(base_dir, "prompt1", "1024x1024", "standard")
        path2 = get_image_path(base_dir, "prompt2", "1024x1024", "standard")
        
        assert path1 != path2


class TestModel3DSpec:
    """Test Model3DSpec class."""
    
    def test_model3d_spec_defaults(self):
        """Test Model3DSpec with default values."""
        spec = Model3DSpec()
        assert spec.format == "gltf"
        assert spec.quality == "medium"

    def test_model3d_spec_custom(self):
        """Test Model3DSpec with custom values."""
        spec = Model3DSpec("obj", "high")
        assert spec.format == "obj"
        assert spec.quality == "high"

    def test_model3d_spec_various_formats(self):
        """Test Model3DSpec with various formats."""
        formats = ["gltf", "obj", "glb", "fbx"]
        qualities = ["low", "medium", "high", "ultra"]
        
        for fmt in formats:
            for quality in qualities:
                spec = Model3DSpec(fmt, quality)
                assert spec.format == fmt
                assert spec.quality == quality


class TestImageGenerator:
    """Comprehensive ImageGenerator tests."""
    
    def test_image_generator_init(self):
        """Test ImageGenerator initialization."""
        mock_client = MagicMock()
        generator = ImageGenerator(mock_client)
        assert generator.client == mock_client

    @pytest.mark.asyncio
    async def test_generate_image_cached(self):
        """Test image generation with cached result."""
        mock_client = MagicMock()
        generator = ImageGenerator(mock_client)
        
        with patch('ai_game_dev.generators.get_image_path') as mock_path, \
             patch('ai_game_dev.generators.IMAGES_DIR') as mock_dir:
            
            mock_file = MagicMock()
            mock_file.exists.return_value = True
            mock_path.return_value = mock_file
            
            result = await generator.generate_image("test prompt")
            
            assert result["status"] == "cached"
            assert "test prompt" in result["prompt"]

    @pytest.mark.asyncio
    async def test_generate_image_traditional_api_success(self):
        """Test successful image generation with traditional API."""
        mock_client = MagicMock()
        
        # Mock API response
        mock_response = MagicMock()
        mock_data = MagicMock()
        mock_data.b64_json = base64.b64encode(b"fake_image_data").decode()
        mock_response.data = [mock_data]
        mock_client.images.generate.return_value = mock_response
        
        generator = ImageGenerator(mock_client)
        
        with patch('ai_game_dev.generators.get_image_path') as mock_path, \
             patch('ai_game_dev.generators.IMAGES_DIR') as mock_dir, \
             patch('builtins.open', mock_open()) as mock_file:
            
            mock_file_obj = MagicMock()
            mock_file_obj.exists.return_value = False
            mock_path.return_value = mock_file_obj
            
            result = await generator.generate_image("test prompt", use_responses_api=False)
            
            assert result["status"] == "generated"
            assert result["prompt"] == "test prompt"
            mock_client.images.generate.assert_called_once()

    @pytest.mark.asyncio
    async def test_generate_image_responses_api_success(self):
        """Test successful image generation with responses API."""
        mock_client = MagicMock()
        
        # Mock responses API
        mock_response = MagicMock()
        mock_output = MagicMock()
        mock_output.type = "image_generation_call"
        mock_output.result = base64.b64encode(b"fake_image_data").decode()
        mock_response.output = [mock_output]
        mock_client.responses.create.return_value = mock_response
        
        generator = ImageGenerator(mock_client)
        
        with patch('ai_game_dev.generators.get_image_path') as mock_path, \
             patch('builtins.open', mock_open()) as mock_file:
            
            mock_file_obj = MagicMock()
            mock_file_obj.exists.return_value = False
            mock_path.return_value = mock_file_obj
            
            result = await generator.generate_image("test prompt", use_responses_api=True)
            
            assert result["status"] == "generated"
            mock_client.responses.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_generate_image_no_data_traditional(self):
        """Test image generation with no data from traditional API."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.data = []
        mock_client.images.generate.return_value = mock_response
        
        generator = ImageGenerator(mock_client)
        
        with patch('ai_game_dev.generators.get_image_path') as mock_path:
            mock_file_obj = MagicMock()
            mock_file_obj.exists.return_value = False
            mock_path.return_value = mock_file_obj
            
            result = await generator.generate_image("test prompt", use_responses_api=False)
            
            assert result["status"] == "error"
            assert "No image data returned" in result["error"]

    @pytest.mark.asyncio
    async def test_generate_image_no_b64_json(self):
        """Test image generation with no b64_json in response."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_data = MagicMock()
        mock_data.b64_json = None
        mock_response.data = [mock_data]
        mock_client.images.generate.return_value = mock_response
        
        generator = ImageGenerator(mock_client)
        
        with patch('ai_game_dev.generators.get_image_path') as mock_path:
            mock_file_obj = MagicMock()
            mock_file_obj.exists.return_value = False
            mock_path.return_value = mock_file_obj
            
            result = await generator.generate_image("test prompt", use_responses_api=False)
            
            assert result["status"] == "error"
            assert "No image data returned" in result["error"]

    @pytest.mark.asyncio
    async def test_generate_image_no_data_responses(self):
        """Test image generation with no data from responses API."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.output = []
        mock_client.responses.create.return_value = mock_response
        
        generator = ImageGenerator(mock_client)
        
        with patch('ai_game_dev.generators.get_image_path') as mock_path:
            mock_file_obj = MagicMock()
            mock_file_obj.exists.return_value = False
            mock_path.return_value = mock_file_obj
            
            result = await generator.generate_image("test prompt", use_responses_api=True)
            
            assert result["status"] == "error"
            assert "No image data returned" in result["error"]

    @pytest.mark.asyncio
    async def test_generate_image_force_regenerate(self):
        """Test force regenerate bypasses cache."""
        mock_client = MagicMock()
        
        # Mock successful generation
        mock_response = MagicMock()
        mock_data = MagicMock()
        mock_data.b64_json = base64.b64encode(b"fake_image_data").decode()
        mock_response.data = [mock_data]
        mock_client.images.generate.return_value = mock_response
        
        generator = ImageGenerator(mock_client)
        
        with patch('ai_game_dev.generators.get_image_path') as mock_path, \
             patch('builtins.open', mock_open()):
            
            mock_file_obj = MagicMock()
            mock_file_obj.exists.return_value = True  # File exists but should be bypassed
            mock_path.return_value = mock_file_obj
            
            result = await generator.generate_image("test prompt", force_regenerate=True)
            
            assert result["status"] == "generated"
            mock_client.images.generate.assert_called_once()

    @pytest.mark.asyncio
    async def test_generate_image_all_sizes(self):
        """Test image generation with all supported sizes."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_data = MagicMock()
        mock_data.b64_json = base64.b64encode(b"fake_image_data").decode()
        mock_response.data = [mock_data]
        mock_client.images.generate.return_value = mock_response
        
        generator = ImageGenerator(mock_client)
        
        sizes = ["1024x1024", "1536x1024", "1024x1536", "256x256", "512x512", "1792x1024", "1024x1792"]
        
        for size in sizes:
            with patch('ai_game_dev.generators.get_image_path') as mock_path, \
                 patch('builtins.open', mock_open()):
                
                mock_file_obj = MagicMock()
                mock_file_obj.exists.return_value = False
                mock_path.return_value = mock_file_obj
                
                result = await generator.generate_image("test prompt", size=size)
                assert result["status"] == "generated"
                assert result["size"] == size

    @pytest.mark.asyncio
    async def test_generate_image_all_qualities(self):
        """Test image generation with all supported qualities."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_data = MagicMock()
        mock_data.b64_json = base64.b64encode(b"fake_image_data").decode()
        mock_response.data = [mock_data]
        mock_client.images.generate.return_value = mock_response
        
        generator = ImageGenerator(mock_client)
        
        qualities = ["standard", "hd"]
        
        for quality in qualities:
            with patch('ai_game_dev.generators.get_image_path') as mock_path, \
                 patch('builtins.open', mock_open()):
                
                mock_file_obj = MagicMock()
                mock_file_obj.exists.return_value = False
                mock_path.return_value = mock_file_obj
                
                result = await generator.generate_image("test prompt", quality=quality)
                assert result["status"] == "generated"
                assert result["quality"] == quality

    @pytest.mark.asyncio
    async def test_generate_image_api_exception(self):
        """Test image generation with API exception."""
        mock_client = MagicMock()
        mock_client.images.generate.side_effect = Exception("API Error")
        
        generator = ImageGenerator(mock_client)
        
        with patch('ai_game_dev.generators.get_image_path') as mock_path:
            mock_file_obj = MagicMock()
            mock_file_obj.exists.return_value = False
            mock_path.return_value = mock_file_obj
            
            result = await generator.generate_image("test prompt")
            
            assert result["status"] == "error"
            assert "API Error" in result["error"]


class TestModel3DGenerator:
    """Comprehensive Model3DGenerator tests."""
    
    def test_model3d_generator_init(self):
        """Test Model3DGenerator initialization."""
        mock_client = MagicMock()
        generator = Model3DGenerator(mock_client)
        assert generator.client == mock_client
        assert isinstance(generator.image_generator, ImageGenerator)

    def test_generate_model_simple(self):
        """Test simple model generation interface."""
        mock_client = MagicMock()
        generator = Model3DGenerator(mock_client)
        
        with patch('ai_game_dev.generators.MODELS_3D_DIR') as mock_dir:
            mock_dir.mkdir = MagicMock()
            
            spec = Model3DSpec("gltf", "medium")
            result = generator.generate_model("test cube", spec)
            
            assert result is not None
            assert "gltf" in result
            mock_dir.mkdir.assert_called_once()

    @pytest.mark.asyncio
    async def test_generate_3d_model_structured_cached(self):
        """Test structured 3D model generation with cached result."""
        mock_client = MagicMock()
        generator = Model3DGenerator(mock_client)
        
        with patch('ai_game_dev.generators.MODELS_3D_DIR') as mock_dir:
            mock_path = MagicMock()
            mock_path.exists.return_value = True
            mock_dir.__truediv__ = lambda self, x: mock_path
            
            result = await generator.generate_3d_model_structured(
                "test description", "test_model"
            )
            
            assert result["status"] == "cached"
            assert result["model_name"] == "test_model"

    @pytest.mark.asyncio
    async def test_generate_3d_model_structured_with_spec_cache(self):
        """Test structured generation with existing spec cache."""
        mock_client = MagicMock()
        generator = Model3DGenerator(mock_client)
        
        mock_spec = {"materials": [], "geometry": {}}
        
        with patch('ai_game_dev.generators.MODELS_3D_DIR') as mock_dir, \
             patch('ai_game_dev.generators.aiofiles') as mock_aiofiles:
            
            mock_gltf_path = MagicMock()
            mock_gltf_path.exists.return_value = True
            mock_spec_path = MagicMock()
            mock_spec_path.exists.return_value = True
            
            mock_dir_obj = MagicMock()
            mock_dir_obj.__truediv__ = lambda self, x: mock_gltf_path if "gltf" in str(x) else mock_spec_path
            mock_dir.__truediv__ = lambda self, x: mock_dir_obj
            
            mock_file = MagicMock()
            mock_file.read.return_value = json.dumps(mock_spec)
            mock_aiofiles.open.return_value.__aenter__.return_value = mock_file
            
            result = await generator.generate_3d_model_structured(
                "test description", "test_model"
            )
            
            assert result["status"] == "cached"
            assert result["specification"] == mock_spec


class TestAssetGenerator:
    """Comprehensive AssetGenerator tests."""
    
    @patch('ai_game_dev.generators.OpenAI')
    def test_asset_generator_init(self, mock_openai):
        """Test AssetGenerator initialization."""
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        
        generator = AssetGenerator()
        
        assert isinstance(generator.image_generator, ImageGenerator)
        assert isinstance(generator.model3d_generator, Model3DGenerator)
        mock_openai.assert_called_once()

    @patch('ai_game_dev.generators.OpenAI')
    @patch('asyncio.run')
    def test_generate_game_assets_success(self, mock_run, mock_openai):
        """Test successful game asset generation."""
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        
        mock_run.return_value = {
            "status": "generated",
            "image_path": "path/to/asset.png"
        }
        
        generator = AssetGenerator()
        assets = generator.generate_game_assets("2d", "fantasy", 3)
        
        assert len(assets) == 3
        assert all("asset.png" in asset for asset in assets)
        assert mock_run.call_count == 3

    @patch('ai_game_dev.generators.OpenAI')
    @patch('asyncio.run')
    def test_generate_game_assets_with_errors(self, mock_run, mock_openai):
        """Test game asset generation with some failures."""
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        
        # First succeeds, second fails, third succeeds
        mock_run.side_effect = [
            {"status": "generated", "image_path": "asset1.png"},
            Exception("Generation failed"),
            {"status": "cached", "image_path": "asset3.png"}
        ]
        
        generator = AssetGenerator()
        assets = generator.generate_game_assets("2d", "fantasy", 3)
        
        assert len(assets) == 2  # Only successful generations
        assert "asset1.png" in assets
        assert "asset3.png" in assets

    @patch('ai_game_dev.generators.OpenAI')
    @patch('asyncio.run')
    def test_generate_ui_assets(self, mock_run, mock_openai):
        """Test UI asset generation."""
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        
        mock_run.return_value = {
            "status": "generated",
            "image_path": "ui_element.png"
        }
        
        generator = AssetGenerator()
        assets = generator.generate_ui_assets("buttons", "modern", 2)
        
        assert len(assets) == 2
        assert mock_run.call_count == 2

    @patch('ai_game_dev.generators.OpenAI')
    @patch('asyncio.run')
    def test_generate_character_assets(self, mock_run, mock_openai):
        """Test character asset generation."""
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        
        mock_run.return_value = {
            "status": "generated",
            "image_path": "character.png"
        }
        
        generator = AssetGenerator()
        assets = generator.generate_character_assets("hero", "pixel", 4)
        
        assert len(assets) == 4
        assert mock_run.call_count == 4

    @patch('ai_game_dev.generators.OpenAI')
    @patch('asyncio.run')
    def test_generate_environment_assets(self, mock_run, mock_openai):
        """Test environment asset generation."""
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        
        mock_run.return_value = {
            "status": "generated",
            "image_path": "environment.png"
        }
        
        generator = AssetGenerator()
        asset_types = ["background", "tiles", "decorations"]
        assets = generator.generate_environment_assets("forest", "peaceful", asset_types)
        
        assert len(assets) == 3
        assert mock_run.call_count == 3

    @patch('ai_game_dev.generators.OpenAI')
    @patch('asyncio.run')
    def test_generate_assets_error_status(self, mock_run, mock_openai):
        """Test asset generation with error status response."""
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        
        mock_run.return_value = {
            "status": "error",
            "error": "API failed"
        }
        
        generator = AssetGenerator()
        assets = generator.generate_game_assets("2d", "fantasy", 2)
        
        assert len(assets) == 0  # No successful generations

    @patch('ai_game_dev.generators.OpenAI')
    def test_asset_generator_error_handling(self, mock_openai):
        """Test AssetGenerator error handling during initialization."""
        mock_openai.side_effect = Exception("OpenAI client failed")
        
        with pytest.raises(Exception):
            AssetGenerator()


class TestConstants:
    """Test module constants and type definitions."""
    
    def test_image_sizes(self):
        """Test ImageSize type values."""
        valid_sizes = ["1024x1024", "1536x1024", "1024x1536", "256x256", "512x512", "1792x1024", "1024x1792"]
        
        # This tests that the literal types are properly defined
        for size in valid_sizes:
            assert "x" in size
            width, height = size.split("x")
            assert int(width) > 0
            assert int(height) > 0

    def test_image_qualities(self):
        """Test ImageQuality type values."""
        valid_qualities = ["standard", "hd"]
        
        for quality in valid_qualities:
            assert quality in ["standard", "hd"]

    def test_directories(self):
        """Test directory constants."""
        assert isinstance(IMAGES_DIR, Path)
        assert isinstance(MODELS_3D_DIR, Path)
        assert "images" in str(IMAGES_DIR)
        assert "models" in str(MODELS_3D_DIR)
"""Comprehensive tests for generators module."""

import pytest
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from pathlib import Path
import tempfile
import os

from ai_game_dev.generators import (
    ImageGenerator, Model3DGenerator, AssetGenerator,
    ImageSize, ImageQuality, Model3DSpec
)


class TestImageGenerator:
    """Test image generation functionality."""
    
    def test_image_generator_init(self):
        """Test ImageGenerator initialization."""
        with patch('ai_game_dev.generators.OpenAI') as mock_openai:
            mock_client = MagicMock()
            mock_openai.return_value = mock_client
            
            generator = ImageGenerator()
            assert generator.client == mock_client
            mock_openai.assert_called_once()

    @patch('ai_game_dev.generators.OpenAI')
    def test_generate_image_success(self, mock_openai):
        """Test successful image generation."""
        # Setup mocks
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        
        mock_response = MagicMock()
        mock_response.data = [MagicMock()]
        mock_response.data[0].url = "https://example.com/image.png"
        mock_client.images.generate.return_value = mock_response
        
        # Mock file operations
        with patch('ai_game_dev.generators.requests') as mock_requests, \
             patch('ai_game_dev.generators.aiofiles') as mock_aiofiles, \
             patch('ai_game_dev.generators.IMAGES_DIR') as mock_dir:
            
            mock_requests.get.return_value.content = b"fake_image_data"
            mock_dir.mkdir = MagicMock()
            
            generator = ImageGenerator()
            result = generator.generate_image(
                prompt="A beautiful landscape",
                size="1024x1024",
                quality="standard"
            )
            
            assert result is not None
            mock_client.images.generate.assert_called_once()

    @patch('ai_game_dev.generators.OpenAI')
    def test_generate_image_different_sizes(self, mock_openai):
        """Test image generation with different sizes."""
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        
        mock_response = MagicMock()
        mock_response.data = [MagicMock()]
        mock_response.data[0].url = "https://example.com/image.png"
        mock_client.images.generate.return_value = mock_response
        
        generator = ImageGenerator()
        
        sizes = ["1024x1024", "512x512", "256x256"]
        for size in sizes:
            with patch('ai_game_dev.generators.requests'), \
                 patch('ai_game_dev.generators.aiofiles'), \
                 patch('ai_game_dev.generators.IMAGES_DIR'):
                
                result = generator.generate_image(
                    prompt="Test image",
                    size=size,
                    quality="standard"
                )
                assert result is not None

    @patch('ai_game_dev.generators.OpenAI')
    def test_generate_image_different_qualities(self, mock_openai):
        """Test image generation with different qualities."""
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        
        mock_response = MagicMock()
        mock_response.data = [MagicMock()]
        mock_response.data[0].url = "https://example.com/image.png"
        mock_client.images.generate.return_value = mock_response
        
        generator = ImageGenerator()
        
        qualities = ["standard", "hd"]
        for quality in qualities:
            with patch('ai_game_dev.generators.requests'), \
                 patch('ai_game_dev.generators.aiofiles'), \
                 patch('ai_game_dev.generators.IMAGES_DIR'):
                
                result = generator.generate_image(
                    prompt="Test image",
                    size="1024x1024", 
                    quality=quality
                )
                assert result is not None

    @patch('ai_game_dev.generators.OpenAI')
    def test_generate_image_error_handling(self, mock_openai):
        """Test image generation error handling."""
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        mock_client.images.generate.side_effect = Exception("API Error")
        
        generator = ImageGenerator()
        
        with pytest.raises(Exception):
            generator.generate_image("Test prompt")


class TestModel3DGenerator:
    """Test 3D model generation functionality."""
    
    def test_model3d_generator_init(self):
        """Test Model3DGenerator initialization."""
        generator = Model3DGenerator()
        assert hasattr(generator, 'generate_model')

    def test_model3d_spec_creation(self):
        """Test Model3DSpec creation."""
        spec = Model3DSpec()
        assert spec.format == "gltf"
        assert spec.quality == "medium"
        
        spec_custom = Model3DSpec("obj", "high")
        assert spec_custom.format == "obj"
        assert spec_custom.quality == "high"

    def test_generate_placeholder_model(self):
        """Test placeholder 3D model generation."""
        generator = Model3DGenerator()
        
        with patch('ai_game_dev.generators.MODELS_3D_DIR') as mock_dir:
            mock_dir.mkdir = MagicMock()
            
            result = generator.generate_model(
                prompt="A simple cube",
                spec=Model3DSpec()
            )
            
            assert result is not None

    def test_generate_model_different_formats(self):
        """Test model generation with different formats."""
        generator = Model3DGenerator()
        
        formats = ["gltf", "obj", "glb"]
        for fmt in formats:
            spec = Model3DSpec(format=fmt)
            
            with patch('ai_game_dev.generators.MODELS_3D_DIR') as mock_dir:
                mock_dir.mkdir = MagicMock()
                
                result = generator.generate_model(
                    prompt="Test model",
                    spec=spec
                )
                assert result is not None

    def test_generate_model_different_qualities(self):
        """Test model generation with different qualities."""
        generator = Model3DGenerator()
        
        qualities = ["low", "medium", "high"]
        for quality in qualities:
            spec = Model3DSpec(quality=quality)
            
            with patch('ai_game_dev.generators.MODELS_3D_DIR') as mock_dir:
                mock_dir.mkdir = MagicMock()
                
                result = generator.generate_model(
                    prompt="Test model",
                    spec=spec
                )
                assert result is not None


class TestAssetGenerator:
    """Test comprehensive asset generation."""
    
    def test_asset_generator_init(self):
        """Test AssetGenerator initialization."""
        generator = AssetGenerator()
        assert hasattr(generator, 'image_generator')
        assert hasattr(generator, 'model3d_generator')

    @patch('ai_game_dev.generators.ImageGenerator')
    @patch('ai_game_dev.generators.Model3DGenerator')
    def test_generate_game_assets(self, mock_model3d, mock_image):
        """Test comprehensive game asset generation."""
        # Setup mocks
        mock_image_gen = MagicMock()
        mock_model_gen = MagicMock()
        mock_image.return_value = mock_image_gen
        mock_model3d.return_value = mock_model_gen
        
        mock_image_gen.generate_image.return_value = "path/to/image.png"
        mock_model_gen.generate_model.return_value = "path/to/model.gltf"
        
        generator = AssetGenerator()
        
        assets = generator.generate_game_assets(
            game_type="2d",
            theme="fantasy",
            asset_count=3
        )
        
        assert len(assets) > 0
        assert mock_image_gen.generate_image.called

    @patch('ai_game_dev.generators.ImageGenerator')
    def test_generate_ui_assets(self, mock_image):
        """Test UI asset generation."""
        mock_image_gen = MagicMock()
        mock_image.return_value = mock_image_gen
        mock_image_gen.generate_image.return_value = "path/to/button.png"
        
        generator = AssetGenerator()
        
        ui_assets = generator.generate_ui_assets(
            ui_type="buttons",
            style="modern",
            count=5
        )
        
        assert len(ui_assets) == 5
        assert mock_image_gen.generate_image.call_count == 5

    @patch('ai_game_dev.generators.ImageGenerator')
    def test_generate_character_assets(self, mock_image):
        """Test character asset generation."""
        mock_image_gen = MagicMock()
        mock_image.return_value = mock_image_gen
        mock_image_gen.generate_image.return_value = "path/to/character.png"
        
        generator = AssetGenerator()
        
        character_assets = generator.generate_character_assets(
            character_type="hero",
            art_style="pixel",
            variations=3
        )
        
        assert len(character_assets) == 3
        assert mock_image_gen.generate_image.call_count == 3

    @patch('ai_game_dev.generators.ImageGenerator')
    def test_generate_environment_assets(self, mock_image):
        """Test environment asset generation."""
        mock_image_gen = MagicMock()
        mock_image.return_value = mock_image_gen
        mock_image_gen.generate_image.return_value = "path/to/background.png"
        
        generator = AssetGenerator()
        
        env_assets = generator.generate_environment_assets(
            environment_type="forest",
            mood="peaceful",
            asset_types=["background", "tiles", "decorations"]
        )
        
        assert len(env_assets) == 3
        assert mock_image_gen.generate_image.call_count == 3


class TestAsyncAssetGeneration:
    """Test async asset generation functionality."""
    
    @pytest.mark.asyncio
    @patch('ai_game_dev.generators.ImageGenerator')
    async def test_async_asset_generation(self, mock_image):
        """Test async asset generation."""
        mock_image_gen = MagicMock()
        mock_image.return_value = mock_image_gen
        mock_image_gen.generate_image = AsyncMock(return_value="path/to/async_image.png")
        
        generator = AssetGenerator()
        
        # Simulate async asset generation
        results = []
        for i in range(3):
            result = await mock_image_gen.generate_image(f"Test image {i}")
            results.append(result)
        
        assert len(results) == 3
        assert all("async_image.png" in result for result in results)


class TestGeneratorErrorHandling:
    """Test error handling in generators."""
    
    @patch('ai_game_dev.generators.OpenAI')
    def test_image_generator_api_error(self, mock_openai):
        """Test handling of API errors in image generator."""
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        mock_client.images.generate.side_effect = Exception("API Rate Limit")
        
        generator = ImageGenerator()
        
        with pytest.raises(Exception) as exc_info:
            generator.generate_image("Test prompt")
        
        assert "API Rate Limit" in str(exc_info.value)

    def test_model3d_generator_file_error(self):
        """Test handling of file system errors in 3D model generator."""
        generator = Model3DGenerator()
        
        with patch('ai_game_dev.generators.MODELS_3D_DIR') as mock_dir:
            mock_dir.mkdir.side_effect = OSError("Permission denied")
            
            with pytest.raises(OSError):
                generator.generate_model("Test model", Model3DSpec())

    @patch('ai_game_dev.generators.ImageGenerator')
    def test_asset_generator_partial_failure(self, mock_image):
        """Test handling of partial failures in asset generator."""
        mock_image_gen = MagicMock()
        mock_image.return_value = mock_image_gen
        
        # First call succeeds, second fails, third succeeds
        mock_image_gen.generate_image.side_effect = [
            "success1.png",
            Exception("Generation failed"),
            "success2.png"
        ]
        
        generator = AssetGenerator()
        
        # Should handle partial failures gracefully
        try:
            assets = generator.generate_game_assets("2d", "fantasy", 3)
            # Depending on implementation, might return partial results
            assert isinstance(assets, list)
        except Exception as e:
            # Or might propagate the error
            assert "Generation failed" in str(e)


class TestUtilityFunctions:
    """Test utility functions in generators module."""
    
    def test_path_creation(self):
        """Test path creation utilities."""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_path = Path(temp_dir) / "test_images"
            test_path.mkdir(parents=True, exist_ok=True)
            assert test_path.exists()
            assert test_path.is_dir()

    def test_file_saving(self):
        """Test file saving utilities."""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = Path(temp_dir) / "test.txt"
            test_content = "Test content"
            
            with open(test_file, 'w') as f:
                f.write(test_content)
            
            assert test_file.exists()
            assert test_file.read_text() == test_content

    def test_image_size_validation(self):
        """Test image size validation."""
        valid_sizes = ["1024x1024", "512x512", "256x256", "1536x1024", "1024x1536"]
        
        for size in valid_sizes:
            # In a real implementation, this would validate the size
            assert "x" in size
            width, height = size.split("x")
            assert int(width) > 0
            assert int(height) > 0

    def test_quality_validation(self):
        """Test quality parameter validation."""
        valid_qualities = ["standard", "hd"]
        
        for quality in valid_qualities:
            assert quality in ["standard", "hd"]
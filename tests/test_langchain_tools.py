"""Tests for LangChain tools integration."""

import pytest
from unittest.mock import Mock, AsyncMock, patch

from openai_mcp_server.langchain_tools import (
    ImageGenerationTool,
    ImageAnalysisTool,
    SeedManagementTool,
    get_langchain_tools
)


class TestImageGenerationTool:
    """Test image generation tool."""
    
    @pytest.mark.asyncio
    async def test_image_generation_success(self, mock_openai_client):
        """Test successful image generation."""
        tool = ImageGenerationTool()
        
        with patch('openai_mcp_server.langchain_tools.AsyncOpenAI', return_value=mock_openai_client):
            result = await tool._arun(
                prompt="A fantasy castle",
                size="1024x1024",
                quality="standard"
            )
        
        assert "Generated image:" in result
        assert "https://example.com/image.png" in result
        mock_openai_client.images.generate.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_image_generation_error(self):
        """Test image generation error handling."""
        tool = ImageGenerationTool()
        
        mock_client = Mock()
        mock_client.images.generate = AsyncMock(side_effect=Exception("API Error"))
        
        with patch('openai_mcp_server.langchain_tools.AsyncOpenAI', return_value=mock_client):
            result = await tool._arun(prompt="test")
        
        assert "Error:" in result
        assert "API Error" in result


class TestImageAnalysisTool:
    """Test image analysis tool."""
    
    @pytest.mark.asyncio
    async def test_image_analysis_file_not_found(self, tmp_path):
        """Test image analysis with non-existent file."""
        tool = ImageAnalysisTool()
        
        result = await tool._arun(image_path=str(tmp_path / "nonexistent.jpg"))
        
        assert "Error:" in result
        assert "Image file not found" in result
    
    @pytest.mark.asyncio
    async def test_image_analysis_success(self, tmp_path):
        """Test successful image analysis."""
        tool = ImageAnalysisTool()
        
        # Create a dummy image file
        image_file = tmp_path / "test.jpg"
        image_file.write_text("dummy image data")
        
        result = await tool._arun(image_path=str(image_file))
        
        assert "Image analysis completed" in result


class TestSeedManagementTool:
    """Test seed management tool."""
    
    def test_seed_add(self):
        """Test adding a seed."""
        tool = SeedManagementTool()
        
        result = tool._run(action="add", content="Test seed content")
        
        assert "Added seed:" in result
        assert "Test seed content" in result
    
    def test_seed_list(self):
        """Test listing seeds."""
        tool = SeedManagementTool()
        
        result = tool._run(action="list")
        
        assert "Listing available seeds" in result
    
    def test_seed_clear(self):
        """Test clearing seeds."""
        tool = SeedManagementTool()
        
        result = tool._run(action="clear")
        
        assert "Cleared seeds" in result


def test_get_langchain_tools():
    """Test getting all LangChain tools."""
    tools = get_langchain_tools()
    
    assert len(tools) == 3
    assert any(isinstance(tool, ImageGenerationTool) for tool in tools)
    assert any(isinstance(tool, ImageAnalysisTool) for tool in tools)
    assert any(isinstance(tool, SeedManagementTool) for tool in tools)
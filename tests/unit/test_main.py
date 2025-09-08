"""Tests for __main__ module."""
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
import sys
import subprocess
from pathlib import Path

from ai_game_dev.__main__ import (
    check_port_available,
    run_server,
    generate_game,
    generate_assets,
    main
)


class TestMainModule:
    """Test the main module functions."""
    
    def test_check_port_available_free(self):
        """Test checking if port is available when free."""
        with patch('socket.socket') as mock_socket:
            mock_sock_instance = MagicMock()
            mock_socket.return_value.__enter__.return_value = mock_sock_instance
            
            result = check_port_available(8080)
            
            assert result is True
            mock_sock_instance.bind.assert_called_once_with(('127.0.0.1', 8080))
    
    def test_check_port_available_in_use(self):
        """Test checking if port is available when in use."""
        with patch('socket.socket') as mock_socket:
            mock_sock_instance = MagicMock()
            mock_sock_instance.bind.side_effect = OSError("Address in use")
            mock_socket.return_value.__enter__.return_value = mock_sock_instance
            
            result = check_port_available(8080)
            
            assert result is False
    
    def test_run_server_success(self):
        """Test successful server startup."""
        with patch('subprocess.run') as mock_run:
            with patch('os.path.exists', return_value=True):
                with patch('sys.executable', 'python'):
                    run_server(8080)
                    
                    mock_run.assert_called_once()
                    args = mock_run.call_args[0][0]
                    assert 'chainlit' in args
                    assert 'run' in args
                    assert '--port' in args
                    assert '8080' in args
    
    def test_run_server_chainlit_not_installed(self):
        """Test server startup when Chainlit is not installed."""
        with patch('subprocess.run') as mock_run:
            mock_run.side_effect = subprocess.CalledProcessError(
                1, ['chainlit'], stderr="No module named 'chainlit'"
            )
            
            with pytest.raises(SystemExit) as exc_info:
                run_server(8080)
            
            assert exc_info.value.code == 1
    
    def test_run_server_port_in_use_subprocess(self):
        """Test server startup when port is in use (detected by subprocess)."""
        with patch('ai_game_dev.__main__.check_port_available', return_value=True):
            with patch('subprocess.run') as mock_run:
                mock_run.side_effect = subprocess.CalledProcessError(
                    1, ['chainlit'], stderr="Address already in use"
                )
                
                with pytest.raises(SystemExit) as exc_info:
                    run_server(8080)
                
                assert exc_info.value.code == 1
    
    def test_run_server_python_not_found(self):
        """Test server startup when Python is not found."""
        with patch('subprocess.run') as mock_run:
            mock_run.side_effect = FileNotFoundError()
            
            with pytest.raises(SystemExit) as exc_info:
                run_server(8080)
            
            assert exc_info.value.code == 1
    
    def test_run_server_unexpected_error(self):
        """Test server startup with unexpected error."""
        with patch('subprocess.run') as mock_run:
            mock_run.side_effect = RuntimeError("Unexpected error")
            
            with pytest.raises(SystemExit) as exc_info:
                run_server(8080)
            
            assert exc_info.value.code == 1
    
    @pytest.mark.asyncio
    async def test_generate_game_success(self):
        """Test successful game generation."""
        mock_spec = {
            'title': 'Test Game',
            'engine': 'pygame',
            'description': 'A test game'
        }
        
        with patch('ai_game_dev.__main__.load_toml', return_value=mock_spec):
            with patch('ai_game_dev.__main__.GameSpecLoader') as MockLoader:
                mock_loader = MagicMock()
                mock_loader.load_and_resolve.return_value = mock_spec
                MockLoader.return_value = mock_loader
                
                with patch('ai_game_dev.__main__.generate_for_engine') as mock_gen:
                    mock_gen.return_value = MagicMock(project_path='/path/to/game')
                    
                    await generate_game(Path('spec.toml'), Path('output'))
                    
                    MockLoader.assert_called_once_with('.')
                    mock_loader.load_and_resolve.assert_called_once()
                    mock_gen.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_generate_game_file_not_found(self):
        """Test game generation with missing spec file."""
        with patch('ai_game_dev.__main__.load_toml', side_effect=FileNotFoundError()):
            with pytest.raises(SystemExit):
                await generate_game(Path('missing.toml'), Path('output'))
    
    @pytest.mark.asyncio
    async def test_generate_assets_success(self):
        """Test successful asset generation."""
        mock_spec = {
            'assets': {
                'sprites': [{'name': 'player'}],
                'backgrounds': [{'scene': 'space'}]
            }
        }
        
        with patch('ai_game_dev.__main__.load_toml', return_value=mock_spec):
            with patch('ai_game_dev.graphics.generate_sprite', new_callable=AsyncMock) as mock_sprite:
                with patch('ai_game_dev.graphics.generate_background', new_callable=AsyncMock) as mock_bg:
                    mock_sprite.return_value = '/path/to/sprite.png'
                    mock_bg.return_value = '/path/to/bg.png'
                    
                    await generate_assets(Path('spec.toml'), Path('output'))
                    
                    mock_sprite.assert_called_once()
                    mock_bg.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_generate_assets_file_not_found(self):
        """Test asset generation with missing spec file."""
        with patch('ai_game_dev.__main__.load_toml', side_effect=FileNotFoundError()):
            with pytest.raises(SystemExit):
                await generate_assets(Path('missing.toml'), Path('output'))
    
    
    def test_main_server_mode(self):
        """Test main entry point in server mode."""
        with patch('sys.argv', ['ai-game-dev']):
            with patch('ai_game_dev.__main__.run_server') as mock_run:
                main()
                mock_run.assert_called_once_with(8000)
    
    def test_main_game_mode(self):
        """Test main entry point in game mode."""
        with patch('sys.argv', ['ai-game-dev', '--game-spec', 'test.toml']):
            with patch('asyncio.run') as mock_run:
                main()
                mock_run.assert_called_once()
    
    def test_main_assets_mode(self):
        """Test main entry point in assets mode."""
        with patch('sys.argv', ['ai-game-dev', '--assets-spec', 'test.toml']):
            with patch('asyncio.run') as mock_run:
                main()
                mock_run.assert_called_once()
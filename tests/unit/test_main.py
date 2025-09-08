"""Tests for __main__ module."""
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
import sys
from pathlib import Path

from ai_game_dev.__main__ import (
    parse_args,
    run_server,
    generate_game,
    generate_assets,
    async_main,
    main
)


class TestMainModule:
    """Test the main module functions."""
    
    def test_parse_args_server_mode(self):
        """Test parsing args for server mode."""
        with patch('sys.argv', ['ai-game-dev']):
            args = parse_args()
            assert args.mode == 'server'
            assert args.port == 8000
    
    def test_parse_args_server_with_port(self):
        """Test parsing args for server with custom port."""
        with patch('sys.argv', ['ai-game-dev', '--port', '9000']):
            args = parse_args()
            assert args.mode == 'server'
            assert args.port == 9000
    
    def test_parse_args_game_mode(self):
        """Test parsing args for game generation."""
        with patch('sys.argv', ['ai-game-dev', '--game-spec', 'game.toml']):
            args = parse_args()
            assert args.mode == 'game'
            assert args.game_spec == 'game.toml'
            assert args.game_dir == 'games'
    
    def test_parse_args_game_mode_with_dir(self):
        """Test parsing args for game with custom dir."""
        with patch('sys.argv', ['ai-game-dev', '--game-spec', 'game.toml', '--game-dir', 'output']):
            args = parse_args()
            assert args.mode == 'game'
            assert args.game_spec == 'game.toml'
            assert args.game_dir == 'output'
    
    def test_parse_args_assets_mode(self):
        """Test parsing args for asset generation."""
        with patch('sys.argv', ['ai-game-dev', '--assets-spec', 'assets.toml']):
            args = parse_args()
            assert args.mode == 'assets'
            assert args.assets_spec == 'assets.toml'
            assert args.assets_dir == 'public/static/assets/generated'
    
    def test_parse_args_assets_mode_with_dir(self):
        """Test parsing args for assets with custom dir."""
        with patch('sys.argv', ['ai-game-dev', '--assets-spec', 'assets.toml', '--assets-dir', 'output']):
            args = parse_args()
            assert args.mode == 'assets'
            assert args.assets_spec == 'assets.toml'
            assert args.assets_dir == 'output'
    
    def test_run_server(self):
        """Test server startup."""
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
                    
                    await generate_game('spec.toml', 'output')
                    
                    MockLoader.assert_called_once_with('.')
                    mock_loader.load_and_resolve.assert_called_once()
                    mock_gen.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_generate_game_file_not_found(self):
        """Test game generation with missing spec file."""
        with patch('ai_game_dev.__main__.load_toml', side_effect=FileNotFoundError()):
            with pytest.raises(SystemExit):
                await generate_game('missing.toml', 'output')
    
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
                    
                    await generate_assets('spec.toml', 'output')
                    
                    mock_sprite.assert_called_once()
                    mock_bg.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_generate_assets_file_not_found(self):
        """Test asset generation with missing spec file."""
        with patch('ai_game_dev.__main__.load_toml', side_effect=FileNotFoundError()):
            with pytest.raises(SystemExit):
                await generate_assets('missing.toml', 'output')
    
    @pytest.mark.asyncio
    async def test_async_main_server_mode(self):
        """Test async main in server mode."""
        args = MagicMock(mode='server', port=8000)
        
        with patch('ai_game_dev.__main__.run_server') as mock_run:
            await async_main(args)
            mock_run.assert_called_once_with(8000)
    
    @pytest.mark.asyncio
    async def test_async_main_game_mode(self):
        """Test async main in game mode."""
        args = MagicMock(mode='game', game_spec='spec.toml', game_dir='output')
        
        with patch('ai_game_dev.__main__.generate_game', new_callable=AsyncMock) as mock_gen:
            await async_main(args)
            mock_gen.assert_called_once_with('spec.toml', 'output')
    
    @pytest.mark.asyncio
    async def test_async_main_assets_mode(self):
        """Test async main in assets mode."""
        args = MagicMock(mode='assets', assets_spec='spec.toml', assets_dir='output')
        
        with patch('ai_game_dev.__main__.generate_assets', new_callable=AsyncMock) as mock_gen:
            await async_main(args)
            mock_gen.assert_called_once_with('spec.toml', 'output')
    
    def test_main(self):
        """Test main entry point."""
        with patch('ai_game_dev.__main__.parse_args') as mock_parse:
            with patch('ai_game_dev.__main__.asyncio.run') as mock_run:
                args = MagicMock(mode='server')
                mock_parse.return_value = args
                
                main()
                
                mock_parse.assert_called_once()
                mock_run.assert_called_once()
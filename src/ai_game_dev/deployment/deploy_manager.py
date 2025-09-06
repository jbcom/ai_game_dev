import asyncio
import zipfile
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import subprocess
import tempfile
import shutil

@dataclass
class DeploymentConfig:
    platform: str  # "web", "desktop", "mobile"
    engine: str
    build_mode: str = "release"  # "debug" or "release"
    target_dir: Optional[Path] = None
    extra_files: List[str] = None

    def __post_init__(self):
        if self.extra_files is None:
            self.extra_files = []

@dataclass
class DeploymentResult:
    success: bool
    platform: str
    build_path: Optional[Path] = None
    package_path: Optional[Path] = None
    size_mb: float = 0.0
    build_time: float = 0.0
    logs: List[str] = None
    error: Optional[str] = None

    def __post_init__(self):
        if self.logs is None:
            self.logs = []

class DeploymentManager:
    def __init__(self):
        self.temp_dir = Path(tempfile.mkdtemp(prefix="ai_game_deploy_"))

    async def deploy_pygame_web(self, project_path: Path, config: DeploymentConfig) -> DeploymentResult:
        """Deploy Pygame project for web using Pygbag."""
        start_time = asyncio.get_event_loop().time()
        logs = []
        
        try:
            # Check if pygbag is available
            try:
                proc = await asyncio.create_subprocess_exec(
                    'python', '-m', 'pygbag', '--help',
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                await proc.communicate()
                
                if proc.returncode != 0:
                    return DeploymentResult(
                        success=False,
                        platform="web",
                        error="Pygbag not installed. Install with: pip install pygbag"
                    )
            except Exception:
                return DeploymentResult(
                    success=False,
                    platform="web",
                    error="Pygbag not available. Install with: pip install pygbag"
                )
            
            # Find main Python file
            main_files = list(project_path.glob("main.py")) or list(project_path.glob("game.py"))
            if not main_files:
                return DeploymentResult(
                    success=False,
                    platform="web",
                    error="No main.py or game.py found"
                )
            
            main_file = main_files[0]
            
            # Create web build directory
            web_dir = self.temp_dir / "web_build"
            web_dir.mkdir(exist_ok=True)
            
            # Copy project files
            for file_path in project_path.rglob("*"):
                if file_path.is_file() and not file_path.name.startswith('.'):
                    rel_path = file_path.relative_to(project_path)
                    target_path = web_dir / rel_path
                    target_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(file_path, target_path)
            
            logs.append("Copied project files to build directory")
            
            # Run pygbag
            cmd = [
                'python', '-m', 'pygbag',
                '--build-dir', str(web_dir / 'dist'),
                '--archive-name', project_path.name,
                str(web_dir / main_file.name)
            ]
            
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=web_dir
            )
            
            stdout, stderr = await proc.communicate()
            logs.extend(stdout.decode().split('\n'))
            
            if proc.returncode == 0:
                build_path = web_dir / 'dist'
                package_path = None
                
                # Create ZIP package
                if build_path.exists():
                    package_path = self.temp_dir / f"{project_path.name}_web.zip"
                    with zipfile.ZipFile(package_path, 'w') as zf:
                        for file_path in build_path.rglob("*"):
                            if file_path.is_file():
                                arc_name = file_path.relative_to(build_path)
                                zf.write(file_path, arc_name)
                    
                    size_mb = package_path.stat().st_size / (1024 * 1024)
                else:
                    size_mb = 0
                
                end_time = asyncio.get_event_loop().time()
                
                return DeploymentResult(
                    success=True,
                    platform="web",
                    build_path=build_path,
                    package_path=package_path,
                    size_mb=size_mb,
                    build_time=end_time - start_time,
                    logs=logs
                )
            else:
                return DeploymentResult(
                    success=False,
                    platform="web",
                    error=stderr.decode(),
                    logs=logs
                )
                
        except Exception as e:
            return DeploymentResult(
                success=False,
                platform="web",
                error=str(e),
                logs=logs
            )

    async def deploy_pygame_desktop(self, project_path: Path, config: DeploymentConfig) -> DeploymentResult:
        """Deploy Pygame project for desktop using PyInstaller."""
        start_time = asyncio.get_event_loop().time()
        logs = []
        
        try:
            # Check if PyInstaller is available
            try:
                proc = await asyncio.create_subprocess_exec(
                    'pyinstaller', '--version',
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                await proc.communicate()
                
                if proc.returncode != 0:
                    return DeploymentResult(
                        success=False,
                        platform="desktop",
                        error="PyInstaller not installed. Install with: pip install pyinstaller"
                    )
            except Exception:
                return DeploymentResult(
                    success=False,
                    platform="desktop",
                    error="PyInstaller not available. Install with: pip install pyinstaller"
                )
            
            # Find main Python file
            main_files = list(project_path.glob("main.py")) or list(project_path.glob("game.py"))
            if not main_files:
                return DeploymentResult(
                    success=False,
                    platform="desktop",
                    error="No main.py or game.py found"
                )
            
            main_file = main_files[0]
            
            # Create desktop build directory
            desktop_dir = self.temp_dir / "desktop_build"
            desktop_dir.mkdir(exist_ok=True)
            
            # PyInstaller command
            cmd = [
                'pyinstaller',
                '--onefile' if config.build_mode == 'release' else '--onedir',
                '--windowed',
                '--name', project_path.name,
                '--distpath', str(desktop_dir / 'dist'),
                '--workpath', str(desktop_dir / 'build'),
                '--specpath', str(desktop_dir),
                str(main_file)
            ]
            
            # Add data files
            for file_path in project_path.rglob("*"):
                if file_path.is_file() and file_path.suffix in ['.png', '.jpg', '.wav', '.mp3', '.ogg']:
                    rel_path = file_path.relative_to(project_path)
                    cmd.extend(['--add-data', f"{file_path};{rel_path.parent}"])
            
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=project_path
            )
            
            stdout, stderr = await proc.communicate()
            logs.extend(stdout.decode().split('\n'))
            
            if proc.returncode == 0:
                build_path = desktop_dir / 'dist'
                
                # Create ZIP package
                package_path = self.temp_dir / f"{project_path.name}_desktop.zip"
                with zipfile.ZipFile(package_path, 'w') as zf:
                    for file_path in build_path.rglob("*"):
                        if file_path.is_file():
                            arc_name = file_path.relative_to(build_path)
                            zf.write(file_path, arc_name)
                
                size_mb = package_path.stat().st_size / (1024 * 1024)
                end_time = asyncio.get_event_loop().time()
                
                return DeploymentResult(
                    success=True,
                    platform="desktop",
                    build_path=build_path,
                    package_path=package_path,
                    size_mb=size_mb,
                    build_time=end_time - start_time,
                    logs=logs
                )
            else:
                return DeploymentResult(
                    success=False,
                    platform="desktop",
                    error=stderr.decode(),
                    logs=logs
                )
                
        except Exception as e:
            return DeploymentResult(
                success=False,
                platform="desktop",
                error=str(e),
                logs=logs
            )

    async def deploy_bevy_web(self, project_path: Path, config: DeploymentConfig) -> DeploymentResult:
        """Deploy Bevy project for web using wasm-pack."""
        start_time = asyncio.get_event_loop().time()
        logs = []
        
        try:
            # Check if wasm-pack is available
            try:
                proc = await asyncio.create_subprocess_exec(
                    'wasm-pack', '--version',
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                await proc.communicate()
                
                if proc.returncode != 0:
                    return DeploymentResult(
                        success=False,
                        platform="web",
                        error="wasm-pack not installed. Install from: https://rustwasm.github.io/wasm-pack/"
                    )
            except Exception:
                return DeploymentResult(
                    success=False,
                    platform="web",
                    error="wasm-pack not available. Install from: https://rustwasm.github.io/wasm-pack/"
                )
            
            # Build for web
            web_dir = self.temp_dir / "bevy_web"
            web_dir.mkdir(exist_ok=True)
            
            cmd = [
                'wasm-pack', 'build',
                '--target', 'web',
                '--out-dir', str(web_dir),
                str(project_path)
            ]
            
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await proc.communicate()
            logs.extend(stdout.decode().split('\n'))
            
            if proc.returncode == 0:
                # Create basic HTML wrapper
                html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{project_path.name}</title>
    <style>
        body {{ margin: 0; background: #000; display: flex; justify-content: center; align-items: center; height: 100vh; }}
        canvas {{ border: 1px solid #333; }}
    </style>
</head>
<body>
    <script type="module">
        import init from './{project_path.name}.js';
        init();
    </script>
</body>
</html>"""
                
                (web_dir / "index.html").write_text(html_content)
                
                # Create ZIP package
                package_path = self.temp_dir / f"{project_path.name}_bevy_web.zip"
                with zipfile.ZipFile(package_path, 'w') as zf:
                    for file_path in web_dir.rglob("*"):
                        if file_path.is_file():
                            arc_name = file_path.relative_to(web_dir)
                            zf.write(file_path, arc_name)
                
                size_mb = package_path.stat().st_size / (1024 * 1024)
                end_time = asyncio.get_event_loop().time()
                
                return DeploymentResult(
                    success=True,
                    platform="web",
                    build_path=web_dir,
                    package_path=package_path,
                    size_mb=size_mb,
                    build_time=end_time - start_time,
                    logs=logs
                )
            else:
                return DeploymentResult(
                    success=False,
                    platform="web",
                    error=stderr.decode(),
                    logs=logs
                )
                
        except Exception as e:
            return DeploymentResult(
                success=False,
                platform="web",
                error=str(e),
                logs=logs
            )

    async def deploy_project(self, project_path: Path, config: DeploymentConfig) -> DeploymentResult:
        """Deploy project based on engine and platform."""
        if config.engine.lower() == "pygame":
            if config.platform == "web":
                return await self.deploy_pygame_web(project_path, config)
            elif config.platform == "desktop":
                return await self.deploy_pygame_desktop(project_path, config)
        elif config.engine.lower() == "bevy":
            if config.platform == "web":
                return await self.deploy_bevy_web(project_path, config)
        
        return DeploymentResult(
            success=False,
            platform=config.platform,
            error=f"Deployment not supported for {config.engine} on {config.platform}"
        )

    def cleanup(self):
        """Clean up temporary files."""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def __del__(self):
        self.cleanup()
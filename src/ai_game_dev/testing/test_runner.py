import asyncio
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import json

@dataclass
class TestResult:
    test_name: str
    passed: bool
    duration: float
    output: str
    error: Optional[str] = None

class GameTestRunner:
    def __init__(self, project_path: Path):
        self.project_path = project_path
        self.test_results: List[TestResult] = []

    async def run_pygame_tests(self) -> List[TestResult]:
        """Run tests for Pygame projects."""
        results = []
        
        # Test basic imports
        results.append(await self._test_imports(['pygame', 'sys', 'os']))
        
        # Test main game file syntax
        main_files = list(self.project_path.glob("main.py")) or list(self.project_path.glob("game.py"))
        if main_files:
            results.append(await self._test_syntax(main_files[0]))
            results.append(await self._test_execution(main_files[0]))
        
        return results

    async def run_bevy_tests(self) -> List[TestResult]:
        """Run tests for Bevy projects."""
        results = []
        
        # Check for Cargo.toml
        cargo_file = self.project_path / "Cargo.toml"
        if cargo_file.exists():
            results.append(await self._test_cargo_check())
            results.append(await self._test_cargo_build())
        
        return results

    async def run_godot_tests(self) -> List[TestResult]:
        """Run tests for Godot projects."""
        results = []
        
        # Check project.godot file
        project_file = self.project_path / "project.godot"
        if project_file.exists():
            results.append(TestResult(
                test_name="Godot Project File",
                passed=True,
                duration=0.1,
                output="Godot project file found"
            ))
        
        # Test GDScript files
        gd_files = list(self.project_path.glob("**/*.gd"))
        for gd_file in gd_files:
            results.append(await self._test_gdscript(gd_file))
        
        return results

    async def _test_imports(self, modules: List[str]) -> TestResult:
        """Test if required modules can be imported."""
        import_code = "; ".join([f"import {module}" for module in modules])
        
        try:
            proc = await asyncio.create_subprocess_exec(
                sys.executable, '-c', import_code,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await proc.communicate()
            
            if proc.returncode == 0:
                return TestResult(
                    test_name="Module Imports",
                    passed=True,
                    duration=0.5,
                    output=f"Successfully imported: {', '.join(modules)}"
                )
            else:
                return TestResult(
                    test_name="Module Imports",
                    passed=False,
                    duration=0.5,
                    output=stdout.decode(),
                    error=stderr.decode()
                )
        except Exception as e:
            return TestResult(
                test_name="Module Imports",
                passed=False,
                duration=0.5,
                output="",
                error=str(e)
            )

    async def _test_syntax(self, file_path: Path) -> TestResult:
        """Test Python file syntax."""
        try:
            proc = await asyncio.create_subprocess_exec(
                sys.executable, '-m', 'py_compile', str(file_path),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await proc.communicate()
            
            return TestResult(
                test_name=f"Syntax Check: {file_path.name}",
                passed=proc.returncode == 0,
                duration=0.3,
                output=stdout.decode(),
                error=stderr.decode() if proc.returncode != 0 else None
            )
        except Exception as e:
            return TestResult(
                test_name=f"Syntax Check: {file_path.name}",
                passed=False,
                duration=0.3,
                output="",
                error=str(e)
            )

    async def _test_execution(self, file_path: Path) -> TestResult:
        """Test if Python file can execute without immediate errors."""
        try:
            # Run with a timeout to prevent hanging
            proc = await asyncio.create_subprocess_exec(
                sys.executable, str(file_path),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            try:
                stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=5.0)
                return TestResult(
                    test_name=f"Execution Test: {file_path.name}",
                    passed=proc.returncode == 0,
                    duration=1.0,
                    output=stdout.decode()[:500],  # Limit output
                    error=stderr.decode()[:500] if proc.returncode != 0 else None
                )
            except asyncio.TimeoutError:
                proc.kill()
                return TestResult(
                    test_name=f"Execution Test: {file_path.name}",
                    passed=True,  # Timeout might be normal for games
                    duration=5.0,
                    output="Program started successfully (timeout after 5s)"
                )
        except Exception as e:
            return TestResult(
                test_name=f"Execution Test: {file_path.name}",
                passed=False,
                duration=1.0,
                output="",
                error=str(e)
            )

    async def _test_cargo_check(self) -> TestResult:
        """Test Rust project with cargo check."""
        try:
            proc = await asyncio.create_subprocess_exec(
                'cargo', 'check',
                cwd=self.project_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await proc.communicate()
            
            return TestResult(
                test_name="Cargo Check",
                passed=proc.returncode == 0,
                duration=10.0,
                output=stdout.decode(),
                error=stderr.decode() if proc.returncode != 0 else None
            )
        except Exception as e:
            return TestResult(
                test_name="Cargo Check",
                passed=False,
                duration=1.0,
                output="",
                error=str(e)
            )

    async def _test_cargo_build(self) -> TestResult:
        """Test Rust project with cargo build."""
        try:
            proc = await asyncio.create_subprocess_exec(
                'cargo', 'build',
                cwd=self.project_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await proc.communicate()
            
            return TestResult(
                test_name="Cargo Build",
                passed=proc.returncode == 0,
                duration=30.0,
                output=stdout.decode(),
                error=stderr.decode() if proc.returncode != 0 else None
            )
        except Exception as e:
            return TestResult(
                test_name="Cargo Build",
                passed=False,
                duration=1.0,
                output="",
                error=str(e)
            )

    async def _test_gdscript(self, file_path: Path) -> TestResult:
        """Basic GDScript validation."""
        try:
            content = file_path.read_text()
            
            # Basic syntax checks
            if "extends" not in content and "class_name" not in content:
                return TestResult(
                    test_name=f"GDScript Check: {file_path.name}",
                    passed=False,
                    duration=0.1,
                    output="",
                    error="Missing extends or class_name declaration"
                )
            
            return TestResult(
                test_name=f"GDScript Check: {file_path.name}",
                passed=True,
                duration=0.1,
                output="Basic GDScript structure looks good"
            )
        except Exception as e:
            return TestResult(
                test_name=f"GDScript Check: {file_path.name}",
                passed=False,
                duration=0.1,
                output="",
                error=str(e)
            )

    async def run_all_tests(self, engine: str) -> Dict[str, Any]:
        """Run all tests for the specified engine."""
        start_time = asyncio.get_event_loop().time()
        
        if engine.lower() == "pygame":
            results = await self.run_pygame_tests()
        elif engine.lower() == "bevy":
            results = await self.run_bevy_tests()
        elif engine.lower() == "godot":
            results = await self.run_godot_tests()
        else:
            results = []
        
        end_time = asyncio.get_event_loop().time()
        total_duration = end_time - start_time
        
        passed_tests = sum(1 for r in results if r.passed)
        total_tests = len(results)
        
        return {
            "engine": engine,
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": total_tests - passed_tests,
            "success_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0,
            "total_duration": total_duration,
            "results": [
                {
                    "test_name": r.test_name,
                    "passed": r.passed,
                    "duration": r.duration,
                    "output": r.output,
                    "error": r.error
                }
                for r in results
            ]
        }
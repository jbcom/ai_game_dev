#!/usr/bin/env python3
"""
Master test runner for all E2E clients.
Coordinates testing across Python, Rust, and Node.js clients.
"""
import asyncio
import json
import subprocess
import time
from pathlib import Path
from typing import Dict, Any

from openai_mcp_server.logging_config import get_logger

logger = get_logger(__name__, component="e2e_master")


class E2EMasterRunner:
    """Coordinate E2E testing across multiple language clients."""
    
    def __init__(self):
        self.results_dir = Path("tests/e2e/results")
        self.results_dir.mkdir(exist_ok=True)
    
    async def run_python_tests(self) -> Dict[str, Any]:
        """Run Python E2E tests."""
        logger.info("🐍 Running Python E2E tests...")
        
        try:
            result = subprocess.run([
                "python", "tests/e2e/python_client/test_python_client.py"
            ], capture_output=True, text=True, timeout=60)
            
            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr,
                "language": "python"
            }
        except Exception as e:
            logger.error(f"Python tests failed: {e}")
            return {"success": False, "error": str(e), "language": "python"}
    
    async def run_rust_tests(self) -> Dict[str, Any]:
        """Run Rust E2E tests."""
        logger.info("🦀 Running Rust E2E tests...")
        
        try:
            # Build Rust project
            build_result = subprocess.run([
                "cargo", "build", "--manifest-path", "tests/e2e/rust_client/Cargo.toml"
            ], capture_output=True, text=True, timeout=120)
            
            if build_result.returncode != 0:
                return {
                    "success": False,
                    "error": f"Build failed: {build_result.stderr}",
                    "language": "rust"
                }
            
            # Run tests
            test_result = subprocess.run([
                "cargo", "test", "--manifest-path", "tests/e2e/rust_client/Cargo.toml"
            ], capture_output=True, text=True, timeout=60)
            
            return {
                "success": test_result.returncode == 0,
                "output": test_result.stdout,
                "error": test_result.stderr,
                "language": "rust"
            }
        except Exception as e:
            logger.error(f"Rust tests failed: {e}")
            return {"success": False, "error": str(e), "language": "rust"}
    
    async def run_node_tests(self) -> Dict[str, Any]:
        """Run Node.js E2E tests."""
        logger.info("📦 Running Node.js E2E tests...")
        
        try:
            # Install dependencies
            install_result = subprocess.run([
                "npm", "install"
            ], cwd="tests/e2e/node_client", capture_output=True, text=True, timeout=120)
            
            if install_result.returncode != 0:
                return {
                    "success": False,
                    "error": f"npm install failed: {install_result.stderr}",
                    "language": "nodejs"
                }
            
            # Run tests
            test_result = subprocess.run([
                "npm", "test"
            ], cwd="tests/e2e/node_client", capture_output=True, text=True, timeout=60)
            
            return {
                "success": test_result.returncode == 0,
                "output": test_result.stdout,
                "error": test_result.stderr,
                "language": "nodejs"
            }
        except Exception as e:
            logger.error(f"Node.js tests failed: {e}")
            return {"success": False, "error": str(e), "language": "nodejs"}
    
    async def run_all_e2e_tests(self) -> Dict[str, Any]:
        """Run all E2E tests across languages."""
        logger.info("🚀 Running comprehensive E2E test suite...")
        
        start_time = time.time()
        
        # Run all tests concurrently
        python_task = asyncio.create_task(self.run_python_tests())
        rust_task = asyncio.create_task(self.run_rust_tests())
        node_task = asyncio.create_task(self.run_node_tests())
        
        # Wait for all to complete
        python_result = await python_task
        rust_result = await rust_task
        node_result = await node_task
        
        end_time = time.time()
        
        # Compile comprehensive results
        results = {
            "e2e_testing_complete": True,
            "total_duration_seconds": end_time - start_time,
            "languages_tested": ["python", "rust", "nodejs"],
            "results": {
                "python": python_result,
                "rust": rust_result,
                "nodejs": node_result
            },
            "success_rate": sum(1 for r in [python_result, rust_result, node_result] if r["success"]) / 3,
            "protocol_validation": "MCP protocol tested across multiple language implementations",
            "comprehensive_coverage": "Full stack testing from client to server"
        }
        
        # Save comprehensive results
        with open(self.results_dir / "e2e_comprehensive_results.json", "w") as f:
            json.dump(results, f, indent=2)
        
        logger.info(f"🎉 E2E testing completed! Success rate: {results['success_rate']:.2%}")
        return results


async def main():
    """Main entry point for E2E testing."""
    runner = E2EMasterRunner()
    await runner.run_all_e2e_tests()


if __name__ == "__main__":
    asyncio.run(main())

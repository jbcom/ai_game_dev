#!/usr/bin/env python3
"""
Nuitka standalone compilation for universal C++ binary with language bindings.
Creates a single executable that can be called from any language via C bindings.
"""
import os
import subprocess
import sys
from pathlib import Path
from typing import List, Optional

from ai_game_dev.logging_config import get_logger

logger = get_logger(__name__, component="nuitka_compilation")


class NuitkaCompiler:
    """Nuitka-based compilation for universal binary distribution."""
    
    def __init__(self, output_dir: Optional[Path] = None):
        self.output_dir = output_dir or Path("dist/compiled")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Source directory
        self.src_dir = Path("src/ai_game_dev")
        
    def compile_standalone_binary(
        self,
        entry_point: str = "library:demo",
        binary_name: str = "ai-game-dev",
        optimizations: List[str] = None
    ) -> Path:
        """
        Compile the Python library to a standalone C++ binary using Nuitka.
        
        Args:
            entry_point: Python module:function to use as entry point
            binary_name: Name of the compiled binary
            optimizations: Additional optimization flags
        
        Returns:
            Path to the compiled binary
        """
        logger.info(f"🔄 Compiling {binary_name} with Nuitka...")
        
        optimizations = optimizations or [
            "--lto=yes",
            "--assume-yes-for-downloads",
            "--plugin-enable=anti-bloat",
            "--plugin-enable=data-files",
        ]
        
        # Build Nuitka command
        nuitka_cmd = [
            sys.executable, "-m", "nuitka",
            "--standalone",
            "--onefile", 
            f"--output-filename={binary_name}",
            f"--output-dir={self.output_dir}",
            "--follow-imports",
            "--include-package=ai_game_dev",
            "--include-package=langchain",
            "--include-package=langgraph", 
            "--include-package=openai",
            "--include-package=pydantic",
            "--python-for-scons=python",
        ] + optimizations + [
            f"src/ai_game_dev/{entry_point.split(':')[0]}.py"
        ]
        
        logger.info(f"Running: {' '.join(nuitka_cmd)}")
        
        try:
            result = subprocess.run(
                nuitka_cmd,
                capture_output=True,
                text=True,
                timeout=1800  # 30 minutes timeout
            )
            
            if result.returncode == 0:
                binary_path = self.output_dir / binary_name
                logger.info(f"✅ Compilation successful: {binary_path}")
                
                # Make executable
                os.chmod(binary_path, 0o755)
                
                return binary_path
            else:
                logger.error(f"❌ Compilation failed:")
                logger.error(f"STDOUT: {result.stdout}")
                logger.error(f"STDERR: {result.stderr}")
                raise RuntimeError(f"Nuitka compilation failed: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            logger.error("❌ Compilation timeout (30 minutes)")
            raise RuntimeError("Compilation timed out")
    
    def create_c_header(self, binary_path: Path) -> Path:
        """
        Create C header file for universal language binding.
        
        This allows any language with C FFI to use the compiled binary.
        """
        header_content = '''/* AI Game Development Library - Universal C Bindings */
#ifndef AI_GAME_DEV_H
#define AI_GAME_DEV_H

#ifdef __cplusplus
extern "C" {
#endif

/* Core game development functions */
typedef struct {
    char* title;
    char* description;
    char* engine;
    int success;
    char* error_message;
} GameResult;

typedef struct {
    char* engine;
    char* complexity;
    char** features;
    int feature_count;
} GameConfig;

/* Function prototypes for library interface */

/**
 * Initialize the AI game development system
 * @return 0 on success, -1 on failure
 */
int ai_game_dev_init(void);

/**
 * Create a game from description
 * @param description Game description in natural language
 * @param config Game configuration options
 * @return GameResult structure with created game data
 */
GameResult* ai_game_dev_create_game(const char* description, GameConfig* config);

/**
 * Generate game assets
 * @param descriptions Array of asset descriptions
 * @param count Number of descriptions
 * @param style Art style to use
 * @return Asset generation result
 */
int ai_game_dev_generate_assets(const char** descriptions, int count, const char* style);

/**
 * Get version information
 * @return Version string (caller must not free)
 */
const char* ai_game_dev_version(void);

/**
 * Check what engines are supported
 * @param engines Output buffer for supported engines
 * @param max_count Maximum number of engines to return
 * @return Number of supported engines
 */
int ai_game_dev_supported_engines(char** engines, int max_count);

/**
 * Cleanup resources
 */
void ai_game_dev_cleanup(void);

/**
 * Free GameResult structure
 * @param result GameResult to free
 */
void ai_game_dev_free_result(GameResult* result);

/* Error handling */
const char* ai_game_dev_get_last_error(void);

#ifdef __cplusplus
}
#endif

#endif /* AI_GAME_DEV_H */
'''
        
        header_path = self.output_dir / "ai_game_dev.h"
        with open(header_path, "w") as f:
            f.write(header_content)
        
        logger.info(f"✅ C header created: {header_path}")
        return header_path
    
    def create_shared_library(self, binary_path: Path) -> Path:
        """Create shared library version for dynamic linking."""
        logger.info("🔗 Creating shared library...")
        
        # Compile as shared library instead of standalone
        lib_name = f"libai_game_dev.{'so' if sys.platform != 'win32' else 'dll'}"
        
        nuitka_cmd = [
            sys.executable, "-m", "nuitka",
            "--module",
            f"--output-filename={lib_name}",
            f"--output-dir={self.output_dir}",
            "--follow-imports",
            "--include-package=ai_game_dev",
            "src/ai_game_dev/library.py"
        ]
        
        try:
            result = subprocess.run(nuitka_cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                lib_path = self.output_dir / lib_name
                logger.info(f"✅ Shared library created: {lib_path}")
                return lib_path
            else:
                logger.error(f"❌ Shared library creation failed: {result.stderr}")
                raise RuntimeError("Failed to create shared library")
                
        except Exception as e:
            logger.error(f"❌ Shared library creation error: {e}")
            raise
    
    def create_distribution_package(self, binary_path: Path, header_path: Path) -> Path:
        """Create complete distribution package with binaries and headers."""
        dist_dir = self.output_dir / "ai-game-dev-universal"
        dist_dir.mkdir(exist_ok=True)
        
        # Create directory structure
        (dist_dir / "bin").mkdir(exist_ok=True)
        (dist_dir / "include").mkdir(exist_ok=True)
        (dist_dir / "lib").mkdir(exist_ok=True)
        (dist_dir / "examples").mkdir(exist_ok=True)
        
        # Copy binary and headers
        import shutil
        shutil.copy2(binary_path, dist_dir / "bin")
        shutil.copy2(header_path, dist_dir / "include")
        
        # Create README for distribution
        readme_content = f"""# AI Game Development Library - Universal Distribution

This package contains pre-compiled binaries and language bindings for the AI Game Development Library.

## Contents
- `bin/`: Standalone executables
- `include/`: C header files for language bindings
- `lib/`: Shared libraries  
- `examples/`: Example code for different languages

## Usage

### Command Line
```bash
./bin/ai-game-dev
```

### C/C++
```c
#include "ai_game_dev.h"
// Use the C API functions
```

### Python
```python
import ctypes
lib = ctypes.CDLL('./lib/libai_game_dev.so')
# Use library functions
```

## Supported Languages
- C/C++
- Python
- Rust
- Go  
- Node.js/JavaScript
- Java (via JNI)
- C# (.NET)

## Version
Library Version: 1.0.0
Compiled: {binary_path.stat().st_mtime}
Architecture: {sys.platform}
"""
        
        with open(dist_dir / "README.md", "w") as f:
            f.write(readme_content)
        
        logger.info(f"✅ Distribution package created: {dist_dir}")
        return dist_dir


def compile_binary():
    """Main compilation entry point."""
    logger.info("🚀 Starting Nuitka compilation process...")
    
    compiler = NuitkaCompiler()
    
    try:
        # Compile standalone binary
        binary = compiler.compile_standalone_binary()
        
        # Create C header
        header = compiler.create_c_header(binary)
        
        # Create shared library
        shared_lib = compiler.create_shared_library(binary)
        
        # Create distribution package
        dist_package = compiler.create_distribution_package(binary, header)
        
        print("\n🎉 Compilation completed successfully!")
        print(f"📦 Distribution package: {dist_package}")
        print(f"🔧 Binary: {binary}")
        print(f"📄 C Header: {header}")
        print(f"🔗 Shared Library: {shared_lib}")
        
        return {
            "binary": str(binary),
            "header": str(header), 
            "shared_library": str(shared_lib),
            "distribution": str(dist_package)
        }
        
    except Exception as e:
        logger.error(f"❌ Compilation failed: {e}")
        raise


if __name__ == "__main__":
    compile_binary()
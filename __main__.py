"""
AI Game Development Platform - Main Entry Point
Streamlit-based unified server with integrated education system.
"""

import sys
import subprocess
from pathlib import Path

def main():
    """Launch the Streamlit AI Game Development Platform."""
    
    # Add src directory to Python path
    src_path = Path(__file__).parent / "src"
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))
    
    # Launch Streamlit app
    subprocess.run([
        sys.executable, "-m", "streamlit", "run", 
        str(src_path / "ai_game_dev" / "streamlit_app.py"),
        "--server.port", "5000",
        "--server.address", "0.0.0.0",
        "--server.headless", "true",
        "--browser.gatherUsageStats", "false"
    ])

if __name__ == "__main__":
    main()
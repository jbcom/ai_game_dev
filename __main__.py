"""
AI Game Development Platform - Main Entry Point
Unified server with integrated education system.
"""

import sys
from pathlib import Path

def main():
    """Launch the AI Game Development Platform."""
    
    # Add src directory to Python path
    src_path = Path(__file__).parent / "src"
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))
    
    # Try Streamlit first, then simple server, then minimal server
    try:
        # Import and run Streamlit app
        from ai_game_dev.streamlit_app import main as streamlit_main
        streamlit_main()
        
    except ImportError as e:
        print(f"⚠️ Streamlit not available ({e}), trying simple web interface...")
        
        try:
            # Fallback to simple server
            from ai_game_dev.simple_server import run_simple_server
            run_simple_server()
            
        except ImportError as e2:
            print(f"⚠️ Simple server not available ({e2}), using minimal server...")
            
            # Final fallback to minimal server
            from ai_game_dev.minimal_server import run_minimal_server
            run_minimal_server()

if __name__ == "__main__":
    main()
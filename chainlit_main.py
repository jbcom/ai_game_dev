#!/usr/bin/env python3
"""
Chainlit-based AI Game Development Platform
Replaces master orchestrator with direct subgraph management
"""
import sys
import os
from pathlib import Path

# Add src to path for imports
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

if __name__ == "__main__":
    # Chainlit will handle everything through its CLI
    print("🚀 Starting AI Game Development Platform with Chainlit...")
    print("✅ Direct LangGraph subgraph orchestration enabled")
    print("🎮 Game Workshop | 🎓 Arcade Academy")
    print("📊 Real-time graph traversal visualization")
    print("\nRun with: chainlit run src/ai_game_dev/chainlit_app.py -w")
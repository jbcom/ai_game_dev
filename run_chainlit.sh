#!/bin/bash
# Run the Chainlit-based AI Game Development Platform

echo "🚀 Starting AI Game Development Platform with Chainlit..."
echo "✨ Direct LangGraph subgraph orchestration"
echo "🎮 Visit http://localhost:8000 after startup"
echo ""

# Ensure we're in the right directory
cd "$(dirname "$0")"

# Run Chainlit with hot reload
chainlit run src/ai_game_dev/chainlit_app.py --port 8000 -w
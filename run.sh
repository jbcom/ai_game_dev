#!/bin/bash
# Replit run script for AI Game Development Platform

echo "🚀 Starting AI Game Development Platform..."
echo "📦 Checking dependencies..."

# Ensure we're in the right directory
cd /home/runner/$REPL_SLUG || cd /workspace || cd .

# Check if hatch is available, otherwise use standard python
if command -v hatch &> /dev/null; then
    echo "✅ Using hatch environment"
    hatch run python -m __main__
else
    echo "📦 Installing dependencies with pip..."
    pip install -e .
    echo "✅ Starting with Python"
    python -m __main__
fi
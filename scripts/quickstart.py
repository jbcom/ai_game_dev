#!/usr/bin/env python3
"""
Quick Start Script for AI Game Development Platform
Helps users get started with their first game generation
"""

import os
import sys
from pathlib import Path

def print_banner():
    """Display welcome banner."""
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║       🎮 AI Game Development Platform Quick Start 🎮       ║
    ║          Powered by OpenAI GPT-5 & GPT-Image-1           ║
    ╚═══════════════════════════════════════════════════════════╝
    """)

def check_api_key():
    """Check if OpenAI API key is set."""
    api_key = os.environ.get('OPENAI_API_KEY')
    if not api_key:
        print("❌ OpenAI API key not found!")
        print("\nTo set your API key:")
        print("  export OPENAI_API_KEY='your-api-key-here'")
        print("\nGet your API key from: https://platform.openai.com/api-keys")
        return False
    print("✅ OpenAI API key found")
    return True

def show_examples():
    """Show example game descriptions."""
    print("\n📚 Example Game Descriptions:")
    print("\n1. Platformer:")
    print("   'Create a pixel art platformer where a robot collects batteries while avoiding electric hazards'")
    print("\n2. Space Shooter:")
    print("   'Build a retro space shooter with power-ups and boss battles'")
    print("\n3. Puzzle Game:")
    print("   'Make a match-3 puzzle game with a fantasy theme and spell-casting mechanics'")
    print("\n4. Educational (Academy Mode):")
    print("   'Teach loops and conditionals through a tower defense game'")

def show_commands():
    """Show available commands."""
    print("\n🚀 Quick Start Commands:")
    print("\n1. Start the platform:")
    print("   hatch run server")
    print("\n2. Run in development mode:")
    print("   hatch run dev")
    print("\n3. Format code:")
    print("   hatch fmt")
    print("\n4. Run tests:")
    print("   hatch test")
    print("\n5. View example specs:")
    print("   ls examples/game_specs/")

def main():
    """Main quick start flow."""
    print_banner()
    
    # Check prerequisites
    print("🔍 Checking prerequisites...\n")
    
    if not check_api_key():
        sys.exit(1)
    
    # Check if hatch is installed
    if os.system("which hatch > /dev/null 2>&1") != 0:
        print("❌ Hatch not found!")
        print("\nInstall hatch:")
        print("  pip install hatch")
        sys.exit(1)
    print("✅ Hatch is installed")
    
    # Show getting started info
    print("\n" + "="*60)
    show_examples()
    print("\n" + "="*60)
    show_commands()
    print("\n" + "="*60)
    
    print("\n🎮 Ready to create amazing games with AI!")
    print("\nStart the platform with: hatch run server")
    print("Then open: http://localhost:8000")
    print("\nHappy game developing! 🚀")

if __name__ == "__main__":
    main()
"""
Chainlit-based AI Game Development Platform
Directly manages LangGraph subgraphs without master orchestrator
"""

import chainlit as cl
from typing import Dict, Any, List, Optional
import json
from pathlib import Path

# Import our subgraphs directly
from ai_game_dev.agents.subgraphs import (
    DialogueSubgraph,
    QuestSubgraph,
    GraphicsSubgraph,
    AudioSubgraph
)

# Import engine agents
from ai_game_dev.agents.pygame_agent import PygameAgent
from ai_game_dev.agents.godot_agent import GodotAgent
from ai_game_dev.agents.bevy_agent import BevyAgent
from ai_game_dev.agents.arcade_academy_agent import ArcadeAcademyAgent

# Import utilities
from ai_game_dev.cache_config import initialize_sqlite_cache_and_memory
from ai_game_dev.project_manager import ProjectManager
from ai_game_dev.game_specification import GameSpecificationParser

# Initialize caching
initialize_sqlite_cache_and_memory()

# Global instances
project_manager = ProjectManager()
spec_parser = GameSpecificationParser()

# Subgraph instances - initialized on startup
subgraphs = {
    "dialogue": None,
    "quest": None,
    "graphics": None,
    "audio": None
}

# Engine agents
engine_agents = {
    "pygame": None,
    "godot": None,
    "bevy": None
}

# Special agents
academy_agent = None


@cl.on_chat_start
async def start():
    """Initialize the chat session and display welcome message."""
    
    # Initialize subgraphs
    global subgraphs, engine_agents, academy_agent
    
    cl.user_session.set("mode", None)  # workshop or academy
    cl.user_session.set("current_project", None)
    cl.user_session.set("game_spec", None)
    
    # Send welcome message with custom UI
    await cl.Message(
        content="",
        elements=[
            cl.Text(
                name="welcome",
                display="inline",
                content="""
# 🎮 AI Game Development Platform

Welcome! Choose your path:

## 🚀 Game Workshop
Create complete games with AI assistance. Choose your engine, describe your vision, and watch it come to life!

**Commands:**
- `workshop` - Enter Game Workshop mode
- `create [description]` - Start creating a game
- `engine [pygame/godot/bevy]` - Select engine

## 🎓 Arcade Academy  
Learn game development through our educational RPG featuring Professor Pixel!

**Commands:**
- `academy` - Enter Academy mode
- `start lesson` - Begin learning journey
- `progress` - View your progress

---
Type `workshop` or `academy` to begin!
                """
            )
        ]
    ).send()


@cl.on_message
async def handle_message(message: cl.Message):
    """Process user messages and route to appropriate handlers."""
    
    user_input = message.content.lower().strip()
    mode = cl.user_session.get("mode")
    
    # Mode selection
    if user_input in ["workshop", "game workshop"]:
        await enter_workshop_mode()
        return
    
    elif user_input in ["academy", "arcade academy"]:
        await enter_academy_mode()
        return
    
    # Mode-specific routing
    if mode == "workshop":
        await handle_workshop_message(message)
    elif mode == "academy":
        await handle_academy_message(message)
    else:
        await cl.Message("Please choose a mode first: `workshop` or `academy`").send()


async def enter_workshop_mode():
    """Enter Game Workshop mode."""
    cl.user_session.set("mode", "workshop")
    
    # Initialize engine agents if needed
    global engine_agents
    if not engine_agents["pygame"]:
        engine_agents["pygame"] = PygameAgent()
        engine_agents["godot"] = GodotAgent()
        engine_agents["bevy"] = BevyAgent()
        
        # Initialize all agents
        for agent in engine_agents.values():
            await agent.initialize()
    
    await cl.Message(
        content="",
        elements=[
            cl.Text(
                name="workshop_welcome",
                display="inline",
                content="""
# 🚀 Game Workshop Mode

You're now in the Game Workshop! Here you can create complete games with AI assistance.

## Available Engines:
- **Pygame** - Great for 2D games and beginners
- **Godot** - Professional 2D/3D with visual scripting
- **Bevy** - High-performance Rust-based ECS

## How to Create a Game:

1. **Simple approach:**
   ```
   create a space shooter game
   ```

2. **With engine selection:**
   ```
   create a platformer game with pygame
   ```

3. **Detailed specification:**
   ```
   create a cyberpunk RPG with:
   - turn-based combat
   - dialogue system
   - pixel art style
   - godot engine
   ```

What game would you like to create?
                """
            )
        ]
    ).send()


async def enter_academy_mode():
    """Enter Arcade Academy mode."""
    cl.user_session.set("mode", "academy")
    
    # Initialize academy agent if needed
    global academy_agent
    if not academy_agent:
        academy_agent = ArcadeAcademyAgent()
        await academy_agent.initialize()
    
    await cl.Message(
        content="",
        elements=[
            cl.Text(
                name="academy_welcome",
                display="inline",
                content="""
# 🎓 Arcade Academy Mode

Welcome to NeoTokyo Code Academy: The Binary Rebellion!

Join Professor Pixel in an educational RPG adventure where you'll learn programming through an engaging storyline.

## Your Journey Includes:
- 📚 Interactive coding lessons
- 🎮 Mini-games to practice concepts
- 🏆 Achievements and progress tracking
- 🤖 AI-powered mentorship

## Commands:
- `start lesson` - Begin your journey
- `continue` - Resume from last checkpoint
- `progress` - View your achievements
- `help` - Get assistance from Professor Pixel

Ready to start your coding adventure?
                """
            )
        ]
    ).send()


async def handle_workshop_message(message: cl.Message):
    """Handle messages in workshop mode."""
    user_input = message.content.strip()
    
    # Parse create commands
    if user_input.lower().startswith("create"):
        await handle_create_game(user_input)
        return
    
    # Engine selection
    if user_input.lower() in ["pygame", "godot", "bevy"]:
        cl.user_session.set("selected_engine", user_input.lower())
        await cl.Message(f"✅ Selected {user_input.title()} engine. Now describe your game!").send()
        return
    
    # Check if we have a project in progress
    current_project = cl.user_session.get("current_project")
    if current_project:
        await handle_project_update(user_input, current_project)
    else:
        await cl.Message("Start by creating a game with `create [description]`").send()


async def handle_create_game(user_input: str):
    """Handle game creation request."""
    # Extract description
    description = user_input[6:].strip()  # Remove "create"
    if not description:
        await cl.Message("Please provide a game description. Example: `create a puzzle game`").send()
        return
    
    # Check for engine in description
    engine = None
    for eng in ["pygame", "godot", "bevy"]:
        if eng in description.lower():
            engine = eng
            description = description.lower().replace(f"with {eng}", "").replace(eng, "").strip()
            break
    
    # Use selected engine or default
    if not engine:
        engine = cl.user_session.get("selected_engine", "pygame")
    
    # Show progress
    progress_msg = cl.Message(content=f"🎮 Creating game with {engine.title()} engine...")
    await progress_msg.send()
    
    # Create game specification
    game_spec = {
        "title": f"AI Generated {description.split()[0].title()} Game",
        "description": description,
        "engine": engine,
        "complexity": "intermediate",
        "features": detect_features(description),
        "art_style": detect_art_style(description)
    }
    
    cl.user_session.set("game_spec", game_spec)
    
    # Update progress
    progress_msg.content = "📋 Generated game specification..."
    await progress_msg.update()
    
    # Initialize subgraphs if needed
    await initialize_subgraphs()
    
    # Route to appropriate engine agent
    agent = engine_agents[engine]
    
    # Generate game through agent
    progress_msg.content = "🔨 Generating game code and assets..."
    await progress_msg.update()
    
    try:
        # Direct subgraph orchestration based on features
        results = {}
        
        # Generate dialogue if needed
        if "dialogue" in game_spec["features"]:
            progress_msg.content = "💬 Creating dialogue system..."
            await progress_msg.update()
            dialogue_result = await subgraphs["dialogue"].process({
                "task": "generate_dialogue",
                "context": game_spec
            })
            results["dialogue"] = dialogue_result
        
        # Generate quests if RPG
        if "rpg" in description.lower() or "quest" in game_spec["features"]:
            progress_msg.content = "📜 Designing quests..."
            await progress_msg.update()
            quest_result = await subgraphs["quest"].process({
                "task": "generate_quests",
                "context": game_spec
            })
            results["quests"] = quest_result
        
        # Generate graphics
        progress_msg.content = "🎨 Creating visual assets..."
        await progress_msg.update()
        graphics_result = await subgraphs["graphics"].process({
            "task": "generate_assets",
            "asset_type": "game_sprites",
            "style": game_spec["art_style"],
            "context": game_spec
        })
        results["graphics"] = graphics_result
        
        # Generate audio
        if "audio" in game_spec["features"]:
            progress_msg.content = "🎵 Composing audio..."
            await progress_msg.update()
            audio_result = await subgraphs["audio"].process({
                "task": "generate_audio",
                "context": game_spec
            })
            results["audio"] = audio_result
        
        # Generate main game code
        progress_msg.content = "⚙️ Building game engine code..."
        await progress_msg.update()
        
        game_result = await agent.generate_game(game_spec, subgraph_results=results)
        
        # Create project
        project = project_manager.create_project(
            name=game_spec["title"],
            description=game_spec["description"],
            engine=engine,
            complexity=game_spec["complexity"],
            art_style=game_spec["art_style"]
        )
        
        cl.user_session.set("current_project", project)
        
        # Show results
        await cl.Message(
            content="",
            elements=[
                cl.Text(
                    name="game_created",
                    display="inline",
                    content=f"""
# ✅ Game Created Successfully!

## {game_spec['title']}
**Engine:** {engine.title()}  
**Description:** {game_spec['description']}  
**Features:** {', '.join(game_spec['features'])}  
**Art Style:** {game_spec['art_style']}

## Generated Assets:
- 🎨 Sprites and graphics
- 🎵 Sound effects and music
- 💻 Complete game code
- 📦 Project structure

## Project Location:
`{project.project_path}`

## Next Steps:
- Run `python main.py` to play your game
- Edit the code to customize further
- Type `show code` to view the main file
- Type `list assets` to see all generated assets

What would you like to do next?
                    """
                )
            ]
        ).send()
        
    except Exception as e:
        await cl.Message(f"❌ Error creating game: {str(e)}").send()


async def handle_academy_message(message: cl.Message):
    """Handle messages in academy mode."""
    user_input = message.content.lower().strip()
    
    if user_input in ["start", "start lesson", "begin"]:
        # Start the educational game
        result = await academy_agent.start_lesson()
        await display_academy_content(result)
    
    elif user_input == "progress":
        # Show progress
        progress = await academy_agent.get_progress()
        await display_progress(progress)
    
    else:
        # Process as game input
        result = await academy_agent.process_input(user_input)
        await display_academy_content(result)


async def initialize_subgraphs():
    """Initialize all subgraphs if not already done."""
    global subgraphs
    
    if not subgraphs["dialogue"]:
        subgraphs["dialogue"] = DialogueSubgraph()
        subgraphs["quest"] = QuestSubgraph()
        subgraphs["graphics"] = GraphicsSubgraph()
        subgraphs["audio"] = AudioSubgraph()
        
        # Initialize all
        for subgraph in subgraphs.values():
            await subgraph.initialize()


def detect_features(description: str) -> List[str]:
    """Detect game features from description."""
    features = []
    desc_lower = description.lower()
    
    feature_keywords = {
        "dialogue": ["dialogue", "conversation", "talk", "story"],
        "combat": ["fight", "battle", "combat", "shooter"],
        "puzzles": ["puzzle", "riddle", "solve"],
        "platformer": ["platform", "jump", "mario"],
        "rpg": ["rpg", "role-playing", "character", "quest"],
        "audio": ["music", "sound", "audio"],
        "multiplayer": ["multiplayer", "online", "co-op"]
    }
    
    for feature, keywords in feature_keywords.items():
        if any(keyword in desc_lower for keyword in keywords):
            features.append(feature)
    
    # Default features
    if not features:
        features = ["graphics", "audio", "gameplay"]
    
    return features


def detect_art_style(description: str) -> str:
    """Detect art style from description."""
    desc_lower = description.lower()
    
    styles = {
        "pixel": ["pixel", "8-bit", "retro", "arcade"],
        "cartoon": ["cartoon", "toon", "animated"],
        "realistic": ["realistic", "real", "photo"],
        "minimalist": ["minimal", "simple", "clean"],
        "cyberpunk": ["cyberpunk", "cyber", "neon", "futuristic"],
        "fantasy": ["fantasy", "medieval", "magic"]
    }
    
    for style, keywords in styles.items():
        if any(keyword in desc_lower for keyword in keywords):
            return style
    
    return "modern"


async def display_academy_content(content: Dict[str, Any]):
    """Display academy game content."""
    # Custom display for educational content
    elements = []
    
    if "image" in content:
        elements.append(cl.Image(path=content["image"], name="game_screen"))
    
    if "code_snippet" in content:
        elements.append(cl.Text(
            name="code",
            language="python",
            content=content["code_snippet"]
        ))
    
    await cl.Message(
        content=content.get("text", ""),
        elements=elements
    ).send()


async def display_progress(progress: Dict[str, Any]):
    """Display player progress."""
    await cl.Message(
        content=f"""
# 📊 Your Progress

**Level:** {progress.get('level', 1)}  
**XP:** {progress.get('xp', 0)}  
**Lessons Completed:** {progress.get('lessons_completed', 0)}  
**Achievements:** {', '.join(progress.get('achievements', []))}

Keep learning to unlock more content!
        """
    ).send()


# Custom CSS for our cyberpunk theme
custom_css = """
<style>
/* Cyberpunk theme */
.message {
    background: rgba(0, 0, 0, 0.8);
    border: 1px solid rgba(100, 255, 218, 0.3);
    border-radius: 8px;
}

.message:hover {
    border-color: rgba(100, 255, 218, 0.6);
    box-shadow: 0 0 10px rgba(100, 255, 218, 0.3);
}

/* Neon glow effects */
h1, h2, h3 {
    text-shadow: 0 0 10px rgba(100, 255, 218, 0.5);
}

/* Code blocks */
pre {
    background: rgba(0, 0, 0, 0.9);
    border: 1px solid rgba(255, 0, 255, 0.3);
    border-radius: 4px;
}

/* Buttons */
button {
    background: linear-gradient(45deg, #ff0080, #00ffff);
    border: none;
    border-radius: 20px;
    transition: all 0.3s;
}

button:hover {
    transform: scale(1.05);
    box-shadow: 0 0 20px rgba(255, 0, 128, 0.5);
}
</style>
"""


if __name__ == "__main__":
    # Chainlit handles the server startup
    pass
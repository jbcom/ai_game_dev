"""
Enhanced Chainlit app with full HTMX-style UI
"""
import chainlit as cl
from pathlib import Path
import json
import asyncio
from typing import Dict, Any, List, Optional

# Import our components
from ai_game_dev.agents.subgraphs import (
    DialogueSubgraph, QuestSubgraph, 
    GraphicsSubgraph, AudioSubgraph
)
from ai_game_dev.agents.pygame_agent import PygameAgent
from ai_game_dev.agents.godot_agent import GodotAgent
from ai_game_dev.agents.bevy_agent import BevyAgent
from ai_game_dev.agents.arcade_academy_agent import ArcadeAcademyAgent
from ai_game_dev.project_manager import ProjectManager
from ai_game_dev.cache_config import initialize_sqlite_cache_and_memory
from ai_game_dev.startup_assets import StartupAssetGenerator

# Initialize components
initialize_sqlite_cache_and_memory()
project_manager = ProjectManager()

# Asset generator instance
asset_generator = None

# Agent instances
agents = {
    "pygame": None,
    "godot": None,
    "bevy": None,
    "academy": None
}

# Subgraph instances  
subgraphs = {
    "dialogue": None,
    "quest": None,
    "graphics": None,
    "audio": None
}


@cl.on_chat_start
async def start():
    """Initialize session when user connects."""
    global asset_generator
    
    # Run startup asset generation if not done
    if asset_generator is None:
        print("🚀 Running startup asset generation...")
        asset_generator = StartupAssetGenerator()
        
        # Run in background to not block UI
        asyncio.create_task(run_asset_generation())
    
    # Set up custom UI
    await cl.Message(
        content="",
        elements=[
            cl.Html(
                name="app",
                display="page",
                content=f"""
                <html>
                <head>
                    <link rel="stylesheet" href="/public/style.css">
                    <link href="https://cdn.jsdelivr.net/npm/daisyui@4.12.11/dist/full.min.css" rel="stylesheet">
                    <script src="https://cdn.tailwindcss.com"></script>
                    <script src="/public/components/Workshop.js"></script>
                    <script src="/public/components/Academy.js"></script>
                    <script src="/public/chainlit-app.js"></script>
                </head>
                <body>
                    <div id="app-root"></div>
                </body>
                </html>
                """
            )
        ]
    ).send()
    
    # Initialize session state
    cl.user_session.set("mode", None)
    cl.user_session.set("current_project", None)
    cl.user_session.set("game_spec", None)
    cl.user_session.set("generation_progress", 0)


@cl.on_message
async def handle_message(message: cl.Message):
    """Process all incoming messages."""
    user_input = message.content.strip()
    
    # Handle connection message
    if user_input == "connected":
        return
    
    # Route based on command type
    if user_input.lower().startswith("create"):
        await handle_create_game(user_input)
    elif user_input.lower() in ["workshop", "academy"]:
        cl.user_session.set("mode", user_input.lower())
        await send_ui_update({"type": "mode_changed", "mode": user_input.lower()})
    elif user_input.lower() == "start lesson":
        await handle_academy_start()
    elif user_input.lower().startswith("run_code:"):
        await handle_code_execution(user_input[9:].strip())
    else:
        # General chat handling
        mode = cl.user_session.get("mode")
        if mode == "workshop":
            await handle_workshop_chat(user_input)
        elif mode == "academy":
            await handle_academy_chat(user_input)


async def handle_create_game(user_input: str):
    """Handle game creation workflow."""
    # Initialize agents if needed
    await ensure_agents_initialized()
    
    # Parse command
    description = user_input[6:].strip()
    engine = None
    
    for eng in ["pygame", "godot", "bevy"]:
        if eng in description.lower():
            engine = eng
            description = description.lower().replace(f"with {eng}", "").replace(eng, "").strip()
            break
    
    if not engine:
        engine = "pygame"  # default
    
    # Create game spec
    game_spec = {
        "title": f"AI Generated Game",
        "description": description,
        "engine": engine,
        "features": detect_features(description),
        "art_style": detect_art_style(description)
    }
    
    cl.user_session.set("game_spec", game_spec)
    
    # Send initial progress
    await send_ui_update({
        "type": "generation_start",
        "spec": game_spec
    })
    
    # Initialize subgraphs
    await ensure_subgraphs_initialized()
    
    # Execute generation workflow
    try:
        # Stage 1: Requirements Analysis
        await update_progress("Analyzing requirements...", 10)
        
        # Stage 2: Architecture
        await update_progress("Designing game architecture...", 20)
        
        # Stage 3: Graphics Generation
        if "graphics" in game_spec["features"] or True:  # Always generate graphics
            await update_progress("Creating visual assets...", 40)
            graphics_result = await subgraphs["graphics"].process({
                "task": "generate_assets",
                "context": game_spec
            })
            await send_ui_update({
                "type": "assets_generated",
                "assets": graphics_result.get("assets", [])
            })
        
        # Stage 4: Audio Generation
        if "audio" in game_spec["features"]:
            await update_progress("Composing audio...", 60)
            audio_result = await subgraphs["audio"].process({
                "task": "generate_audio",
                "context": game_spec
            })
        
        # Stage 5: Code Generation
        await update_progress("Writing game code...", 80)
        agent = agents[engine]
        game_result = await agent.generate_game(game_spec)
        
        # Stage 6: Finalization
        await update_progress("Finalizing project...", 95)
        
        # Create project
        project = project_manager.create_project(
            name=game_spec["title"],
            description=game_spec["description"],
            engine=engine
        )
        
        cl.user_session.set("current_project", project)
        
        # Complete
        await update_progress("Complete!", 100)
        await send_ui_update({
            "type": "generation_complete",
            "project": {
                "id": project.id,
                "name": project.name,
                "path": str(project.project_path),
                "description": project.description
            }
        })
        
    except Exception as e:
        await send_ui_update({
            "type": "generation_error",
            "error": str(e)
        })


async def handle_academy_start():
    """Start academy lesson."""
    if not agents["academy"]:
        agents["academy"] = ArcadeAcademyAgent()
        await agents["academy"].initialize()
    
    result = await agents["academy"].start_lesson()
    
    await send_ui_update({
        "type": "dialogue",
        "speaker": "Professor Pixel",
        "avatar": "/public/static/assets/characters/professor-pixel.png",
        "text": result.get("dialogue", "Welcome to the Academy!"),
        "choices": result.get("choices", [])
    })
    
    if result.get("show_code_editor"):
        await send_ui_update({"type": "show_code_editor"})


async def handle_code_execution(code: str):
    """Execute code from academy."""
    try:
        # Safe execution environment
        exec_globals = {"__builtins__": {"print": print, "len": len, "range": range}}
        exec_locals = {}
        
        # Capture output
        import io
        from contextlib import redirect_stdout
        
        output_buffer = io.StringIO()
        with redirect_stdout(output_buffer):
            exec(code, exec_globals, exec_locals)
        
        output = output_buffer.getvalue()
        
        await send_ui_update({
            "type": "code_output",
            "output": output or "Code executed successfully!",
            "success": True
        })
        
        # Update progress
        await send_ui_update({
            "type": "progress_update",
            "progress": {
                "level": 1,
                "xp": cl.user_session.get("xp", 0) + 10,
                "lessons": cl.user_session.get("lessons", [])
            }
        })
        
    except Exception as e:
        await send_ui_update({
            "type": "code_output",
            "output": f"Error: {str(e)}",
            "success": False
        })


async def update_progress(stage: str, percent: int):
    """Send progress update to UI."""
    await send_ui_update({
        "type": "generation_progress",
        "stage": stage,
        "percent": percent
    })


async def send_ui_update(data: Dict[str, Any]):
    """Send update to custom UI."""
    await cl.Message(
        content="",
        elements=[
            cl.Text(
                name="ui_update",
                display="inline",
                content=json.dumps(data)
            )
        ]
    ).send()


async def ensure_agents_initialized():
    """Initialize agents if not already done."""
    if not agents["pygame"]:
        agents["pygame"] = PygameAgent()
        agents["godot"] = GodotAgent()
        agents["bevy"] = BevyAgent()
        
        for agent in agents.values():
            if agent:
                await agent.initialize()


async def ensure_subgraphs_initialized():
    """Initialize subgraphs if not already done."""
    if not subgraphs["dialogue"]:
        subgraphs["dialogue"] = DialogueSubgraph()
        subgraphs["quest"] = QuestSubgraph()
        subgraphs["graphics"] = GraphicsSubgraph()
        subgraphs["audio"] = AudioSubgraph()
        
        for subgraph in subgraphs.values():
            await subgraph.initialize()


def detect_features(description: str) -> List[str]:
    """Detect game features from description."""
    features = []
    desc_lower = description.lower()
    
    feature_map = {
        "dialogue": ["dialogue", "conversation", "talk", "story"],
        "combat": ["fight", "battle", "combat", "shooter"],
        "puzzles": ["puzzle", "riddle", "solve"],
        "rpg": ["rpg", "role", "quest", "adventure"],
        "audio": ["music", "sound"],
        "graphics": ["visual", "art", "sprite"]
    }
    
    for feature, keywords in feature_map.items():
        if any(kw in desc_lower for kw in keywords):
            features.append(feature)
    
    # Always include basic features
    if "graphics" not in features:
        features.append("graphics")
    if "audio" not in features:
        features.append("audio")
    
    return features


def detect_art_style(description: str) -> str:
    """Detect art style preference."""
    desc_lower = description.lower()
    
    styles = {
        "pixel": ["pixel", "8-bit", "retro"],
        "cyberpunk": ["cyberpunk", "cyber", "neon"],
        "cartoon": ["cartoon", "toon"],
        "realistic": ["realistic", "real"]
    }
    
    for style, keywords in styles.items():
        if any(kw in desc_lower for kw in keywords):
            return style
    
    return "modern"


async def handle_workshop_chat(message: str):
    """Handle general workshop chat."""
    # Could add AI assistant responses here
    pass


async def handle_academy_chat(message: str):
    """Handle academy interactions."""
    if agents["academy"]:
        result = await agents["academy"].process_input(message)
        if result:
            await send_ui_update(result)


async def run_asset_generation():
    """Run asset generation in background."""
    global asset_generator
    try:
        await asset_generator.initialize()
        await asset_generator.generate_all_assets()
        print("✅ Startup asset generation complete!")
    except Exception as e:
        print(f"⚠️ Asset generation error: {e}")
        # Continue running even if some assets fail
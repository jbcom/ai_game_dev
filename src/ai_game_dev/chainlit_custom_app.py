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
    GraphicsSubgraph, AudioSubgraph,
    GameSpecSubgraph, GameWorkshopSubgraph,
    ArcadeAcademySubgraph
)
from ai_game_dev.project_manager import ProjectManager
from ai_game_dev.cache_config import initialize_sqlite_cache_and_memory
from ai_game_dev.startup_assets import StartupAssetGenerator

# Initialize components
initialize_sqlite_cache_and_memory()
project_manager = ProjectManager()

# Asset generator instance
asset_generator = None

# Main orchestration subgraphs
workshop_subgraph = None
academy_subgraph = None
spec_builder = None


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
    """Handle game creation workflow using Workshop subgraph."""
    global workshop_subgraph
    
    # Initialize workshop if needed
    if not workshop_subgraph:
        await ensure_subgraphs_initialized()
    
    # Parse command
    description = user_input[6:].strip()
    engine = None
    
    for eng in ["pygame", "godot", "bevy"]:
        if eng in description.lower():
            engine = eng
            description = description.lower().replace(f"with {eng}", "").replace(eng, "").strip()
            break
    
    # Send initial progress
    await send_ui_update({
        "type": "generation_start",
        "description": description,
        "engine": engine or "pygame"
    })
    
    # Use workshop subgraph for orchestration
    try:
        # Create progress callback
        async def progress_callback(stage: str, progress: float):
            await update_progress(stage, int(progress * 100))
        
        # Process through workshop
        result = await workshop_subgraph.process({
            "description": description,
            "engine": engine or "pygame",
            "progress_callback": progress_callback
        })
        
        if result["success"]:
            # Extract project details
            project_data = result["project"]
            paths_info = project_data.get("paths", {})
            
            # Use the code root from the project paths
            if paths_info.get("relative_to_repo", True):
                code_root = Path(paths_info["code_root"])
            else:
                # For absolute paths, create project in project manager's default location
                project = project_manager.create_project(
                    name=project_data["metadata"]["title"],
                    description=description,
                    engine=project_data["metadata"]["engine"]
                )
                code_root = Path(project.project_path)
            
            # Save generated files to the specified location
            code_root.mkdir(parents=True, exist_ok=True)
            for filename, content in project_data["code"].items():
                file_path = code_root / filename
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_text(content)
            
            # Store project info
            cl.user_session.set("current_project", {
                "name": project_data["metadata"]["title"],
                "path": str(code_root),
                "engine": project_data["metadata"]["engine"],
                "assets_path": paths_info.get("assets_root", "")
            })
            
            # Send completion
            await send_ui_update({
                "type": "generation_complete",
                "project": {
                    "name": project_data["metadata"]["title"],
                    "path": str(code_root),
                    "assets_path": paths_info.get("assets_root", ""),
                    "description": description,
                    "files": list(project_data["code"].keys()),
                    "assets": project_data.get("assets", {})
                }
            })
        else:
            await send_ui_update({
                "type": "generation_error",
                "errors": result["errors"]
            })
            
    except Exception as e:
        await send_ui_update({
            "type": "generation_error",
            "error": str(e)
        })


async def handle_academy_start():
    """Start academy lesson using Academy subgraph."""
    global academy_subgraph
    
    # Initialize academy if needed
    if not academy_subgraph:
        await ensure_subgraphs_initialized()
    
    # Start academy mode
    result = await academy_subgraph.start_academy_mode()
    
    if result["success"]:
        # Send initial dialogue
        await send_ui_update({
            "type": "dialogue",
            "speaker": "Professor Pixel",
            "avatar": "/public/static/assets/characters/professor-pixel.png",
            "text": "Welcome to NeoTokyo Code Academy! Ready to learn programming through our RPG adventure?",
            "choices": [
                {"text": "Start with Variables", "action": "start_lesson:variables"},
                {"text": "Continue my journey", "action": "continue_game"},
                {"text": "View my progress", "action": "show_progress"}
            ]
        })
        
        # Show educational content
        educational_content = result.get("educational_content", {})
        await send_ui_update({
            "type": "show_educational_overlay",
            "content": educational_content
        })
    else:
        await send_ui_update({
            "type": "error",
            "message": "Failed to initialize Academy mode"
        })


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


async def ensure_subgraphs_initialized():
    """Initialize orchestration subgraphs if not already done."""
    global workshop_subgraph, academy_subgraph, spec_builder
    
    if not workshop_subgraph:
        print("🔧 Initializing orchestration subgraphs...")
        
        # Initialize main subgraphs
        spec_builder = GameSpecSubgraph()
        workshop_subgraph = GameWorkshopSubgraph()
        academy_subgraph = ArcadeAcademySubgraph()
        
        # Initialize them
        await spec_builder.initialize()
        await workshop_subgraph.initialize()
        await academy_subgraph.initialize()
        
        print("✅ Orchestration subgraphs initialized")




async def handle_workshop_chat(message: str):
    """Handle general workshop chat."""
    # Could add AI assistant responses here
    pass


async def handle_academy_chat(message: str):
    """Handle academy interactions."""
    global academy_subgraph
    
    if academy_subgraph:
        # Handle lesson-specific commands
        if message.startswith("start_lesson:"):
            lesson = message.split(":")[1]
            # Load RPG spec if not already loaded
            if not hasattr(academy_subgraph, 'rpg_spec') or academy_subgraph.rpg_spec is None:
                academy_subgraph.rpg_spec = academy_subgraph._load_rpg_spec_from_unified()
            
            result = await academy_subgraph.process_with_education({
                "uploaded_spec": academy_subgraph.rpg_spec,
                "lesson_focus": lesson,
                "educational_mode": True
            })
            
            if result["success"]:
                await send_ui_update({
                    "type": "lesson_started",
                    "lesson": lesson,
                    "educational": result.get("educational", {})
                })
        else:
            # General academy chat
            await send_ui_update({
                "type": "professor_response",
                "text": "Let me help you with that!"
            })


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
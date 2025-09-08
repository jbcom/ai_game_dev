"""
Simplified Chainlit app using OpenAI agents.
"""
import asyncio
import json
from pathlib import Path

import chainlit as cl

from ai_game_dev.agent import process_request
from ai_game_dev.cache_config import initialize_sqlite_cache_and_memory
from ai_game_dev.project_manager import ProjectManager

# Initialize components
initialize_sqlite_cache_and_memory()
project_manager = ProjectManager()


@cl.on_chat_start
async def start():
    """Initialize session when user connects."""
    # Set initial mode
    cl.user_session.set("mode", "workshop")
    
    # Send welcome message with custom UI
    await cl.Message(
        content="",
        elements=[
            cl.Text(
                name="welcome",
                content="Welcome to AI Game Development Platform!",
                display="inline"
            )
        ]
    ).send()
    
    # Send UI configuration
    await send_ui_update({
        "type": "initialize",
        "modes": ["workshop", "academy"],
        "current_mode": "workshop"
    })


@cl.on_message
async def main(message: cl.Message):
    """Handle user messages."""
    mode = cl.user_session.get("mode", "workshop")
    
    # Handle mode switching
    if message.content.lower() in ["workshop", "academy"]:
        cl.user_session.set("mode", message.content.lower())
        await send_ui_update({
            "type": "mode_changed",
            "mode": message.content.lower()
        })
        return
    
    # Handle special commands
    if message.content.startswith("/"):
        await handle_command(message.content)
        return
    
    # Process game creation request
    try:
        # Show progress
        await send_ui_update({
            "type": "generation_start",
            "message": "Creating your game..."
        })
        
        # Call the OpenAI agent
        result = await process_request(
            mode=mode,
            user_input=message.content
        )
        
        if result["success"]:
            project = result["project"]
            
            # Save project files
            project_path = save_project(project)
            
            # Send completion update
            await send_ui_update({
                "type": "generation_complete",
                "project": {
                    "title": project["spec"]["title"],
                    "path": str(project_path),
                    "files": list(project["code_files"].keys()),
                    "assets": list(project["assets"].keys())
                }
            })
            
            # Send success message
            await cl.Message(
                content=f"✅ {result['message']}\n\nProject saved to: `{project_path}`"
            ).send()
        else:
            await cl.ErrorMessage(
                content=f"Failed to create game: {result.get('error', 'Unknown error')}"
            ).send()
            
    except Exception as e:
        await cl.ErrorMessage(
            content=f"Error: {str(e)}"
        ).send()
        
        await send_ui_update({
            "type": "generation_error",
            "error": str(e)
        })


async def handle_command(command: str):
    """Handle special commands."""
    parts = command.split()
    cmd = parts[0].lower()
    
    if cmd == "/mode":
        if len(parts) > 1 and parts[1] in ["workshop", "academy"]:
            cl.user_session.set("mode", parts[1])
            await cl.Message(f"Switched to {parts[1]} mode").send()
    
    elif cmd == "/list":
        projects = project_manager.list_projects()
        if projects:
            project_list = "\n".join([f"- {p.name} ({p.engine})" for p in projects])
            await cl.Message(f"Your projects:\n{project_list}").send()
        else:
            await cl.Message("No projects yet!").send()
    
    elif cmd == "/help":
        help_text = """**Available Commands:**
/mode [workshop|academy] - Switch modes
/list - List your projects
/help - Show this help

**Workshop Mode:**
Create any game by describing what you want!
Examples:
- "Create a platformer with a ninja character"
- "Make a puzzle game with falling blocks"
- "Build a space shooter with power-ups"

**Academy Mode:**
Learn programming through game creation!
Professor Pixel will guide you through concepts.
"""
        await cl.Message(help_text).send()


def save_project(project_data: dict) -> Path:
    """Save project to disk."""
    spec = project_data["spec"]
    
    # Create project via manager
    project = project_manager.create_project(
        name=spec["title"],
        description=spec["description"],
        engine=spec["engine"]
    )
    
    # Save code files
    for filename, content in project_data["code_files"].items():
        file_path = Path(project.project_path) / filename
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content)
    
    # Save asset references
    assets_file = Path(project.project_path) / "assets.json"
    assets_file.write_text(json.dumps(project_data["assets"], indent=2))
    
    return Path(project.project_path)


async def send_ui_update(data: dict):
    """Send UI update via custom message."""
    await cl.Message(
        content="",
        elements=[
            cl.Text(
                name="ui_update",
                content=json.dumps(data),
                display="none"
            )
        ]
    ).send()
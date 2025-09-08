"""
Chainlit app with proper wizard flows for Workshop and Academy modes.
"""
import asyncio
import json
from pathlib import Path
from typing import Any, Dict, List

import chainlit as cl

from ai_game_dev.agent import (
    create_game, 
    create_educational_game,
    workshop_agent,
    academy_agent,
)
from ai_game_dev.graphics import generate_game_sprite, generate_game_background, generate_ui_pack
from ai_game_dev.audio import generate_sound_effect, generate_background_music, generate_voice_acting
from ai_game_dev.fonts import generate_text_assets
from ai_game_dev.variants import generate_mechanic_variants
from ai_game_dev.cache_config import initialize_sqlite_cache_and_memory
from ai_game_dev.project_manager import ProjectManager
from ai_game_dev.constants import CHAINLIT_CONFIG
from ai_game_dev.startup import run_startup_generation

# Initialize components
initialize_sqlite_cache_and_memory()
project_manager = ProjectManager()

# Run startup generation in the background
asyncio.create_task(run_startup_generation())


@cl.on_chat_start
async def start():
    """Initialize session when user connects."""
    # Set initial state
    cl.user_session.set("mode", None)
    cl.user_session.set("workshop_state", {
        "stage": "engine_selection",
        "engine": None,
        "description": None,
        "features": [],
        "assets": {},
        "code": {}
    })
    cl.user_session.set("academy_state", {
        "stage": "welcome",
        "lesson": None,
        "progress": {"level": 1, "xp": 0, "lessons": []},
        "current_challenge": None
    })
    
    # The custom UI will handle the initial display
    await cl.Message(
        content="Welcome to the AI Game Development Platform! Choose your path:",
        elements=[
            cl.Text(
                name="ui_state",
                content=json.dumps({
                    "type": "initialize",
                    "modes": ["workshop", "academy"]
                }),
                display="none"
            )
        ]
    ).send()


@cl.on_message
async def main(message: cl.Message):
    """Handle user messages based on current mode and state."""
    mode = cl.user_session.get("mode")
    
    # Handle mode selection from homepage
    if message.content.lower() in ["workshop", "academy"]:
        await handle_mode_selection(message.content.lower())
        return
    
    # Route to appropriate handler
    if mode == "workshop":
        await handle_workshop_message(message)
    elif mode == "academy":
        await handle_academy_message(message)
    else:
        # No mode selected yet
        await cl.Message(
            content="Please choose a mode first: **Workshop** or **Academy**"
        ).send()


async def handle_mode_selection(mode: str):
    """Handle mode selection and start the appropriate flow."""
    cl.user_session.set("mode", mode)
    
    if mode == "workshop":
        # Start workshop flow
        await cl.Message(
            content="🚀 **Welcome to Game Workshop!**\n\nLet's create your game. First, choose your engine:",
            elements=[
                cl.Text(
                    name="ui_state",
                    content=json.dumps({
                        "type": "workshop_start",
                        "stage": "engine_selection",
                        "engines": ["pygame", "godot", "bevy"]
                    }),
                    display="none"
                )
            ]
        ).send()
        
    elif mode == "academy":
        # Start academy flow
        await cl.Message(
            content="🎓 **Welcome to Arcade Academy!**\n\nProfessor Pixel here! Ready to learn programming through game creation?",
            elements=[
                cl.Text(
                    name="ui_state", 
                    content=json.dumps({
                        "type": "academy_start",
                        "stage": "welcome",
                        "professor_pixel": "/public/static/assets/characters/professor-pixel.png"
                    }),
                    display="none"
                )
            ]
        ).send()


async def handle_workshop_message(message: cl.Message):
    """Handle workshop mode messages through the wizard flow."""
    state = cl.user_session.get("workshop_state")
    stage = state["stage"]
    
    if stage == "engine_selection":
        # User selected an engine
        if message.content.lower() in ["pygame", "godot", "bevy"]:
            state["engine"] = message.content.lower()
            state["stage"] = "game_description"
            cl.user_session.set("workshop_state", state)
            
            await cl.Message(
                content=f"Great choice! **{state['engine'].title()}** is perfect for your game.\n\nNow, describe your game idea:",
                elements=[
                    cl.Text(
                        name="ui_state",
                        content=json.dumps({
                            "type": "workshop_update",
                            "stage": "game_description",
                            "engine": state["engine"]
                        }),
                        display="none"
                    )
                ]
            ).send()
            
    elif stage == "game_description":
        # User provided game description
        state["description"] = message.content
        state["stage"] = "generating"
        cl.user_session.set("workshop_state", state)
        
        # Start generation process
        await generate_game_workshop(state)
        
    elif stage == "customization":
        # Handle customization requests
        await handle_workshop_customization(message.content, state)


async def generate_game_workshop(state: Dict[str, Any]):
    """Generate a complete game using the workshop flow."""
    # Show generation start
    msg = cl.Message(content="🔧 Starting game generation...")
    await msg.send()
    
    # Update UI to show progress
    await send_progress_update("Analyzing game concept...", 10)
    
    # Step 1: Generate game specification
    await msg.update(content="🔧 Creating game architecture...")
    await send_progress_update("Designing game architecture...", 25)
    
    # Step 2: Generate sprites
    await msg.update(content="🎨 Generating sprites...")
    await send_progress_update("Creating character sprites...", 40)
    
    sprites = []
    sprite_names = determine_sprites_needed(state["description"], state["engine"])
    
    for sprite_name in sprite_names[:3]:  # Limit to 3 main sprites
        sprite = await generate_game_sprite(
            name=sprite_name,
            description=f"{sprite_name} for {state['description']}",
            style="pixel" if state["engine"] == "pygame" else "cartoon",
            save_path=f"temp/{sprite_name}.png"
        )
        sprites.append(sprite)
        state["assets"][sprite_name] = sprite
    
    # Step 3: Generate background
    await msg.update(content="🎨 Creating backgrounds...")
    await send_progress_update("Designing game environments...", 55)
    
    background = await generate_game_background(
        scene=extract_scene_from_description(state["description"]),
        style="pixel" if state["engine"] == "pygame" else "painted",
        save_path="temp/background.png"
    )
    state["assets"]["background"] = background
    
    # Step 4: Generate UI
    await msg.update(content="🎨 Designing UI elements...")
    await send_progress_update("Creating user interface...", 70)
    
    ui_pack = await generate_ui_pack(
        theme=extract_theme_from_description(state["description"]),
        style="retro" if state["engine"] == "pygame" else "modern",
        save_dir="temp/ui"
    )
    state["assets"]["ui"] = ui_pack
    
    # Step 5: Generate sound effects
    await msg.update(content="🔊 Creating sound effects...")
    await send_progress_update("Generating audio assets...", 85)
    
    sounds = []
    for sound_name in ["jump", "collect", "hit"]:
        sound = await generate_sound_effect(
            effect_name=sound_name,
            style="retro" if state["engine"] == "pygame" else "realistic",
            save_path=f"temp/{sound_name}.wav"
        )
        sounds.append(sound)
        state["assets"][f"sound_{sound_name}"] = sound
    
    # Step 6: Generate code
    await msg.update(content="💻 Writing game code...")
    await send_progress_update("Generating game code...", 95)
    
    # Use the agent to create the game
    project = await create_game(
        description=state["description"],
        engine=state["engine"]
    )
    
    state["code"] = project.code_files
    state["stage"] = "complete"
    cl.user_session.set("workshop_state", state)
    
    # Save project
    project_path = save_workshop_project(state)
    
    # Show completion
    await msg.update(content="✅ **Game generation complete!**")
    await send_progress_update("Game ready!", 100)
    
    # Send detailed results
    await cl.Message(
        content=f"""
🎮 **Your game is ready!**

**Title**: {project.spec.title}
**Engine**: {state['engine'].title()}
**Location**: `{project_path}`

**Generated Assets**:
- {len(sprites)} character sprites
- 1 background scene
- {len(ui_pack.get('button', []))} UI elements
- {len(sounds)} sound effects

**Next Steps**:
1. Run your game with the appropriate engine
2. Customize the generated code
3. Add more features!

Would you like to customize anything?
""",
        elements=[
            cl.Text(
                name="ui_state",
                content=json.dumps({
                    "type": "workshop_complete",
                    "stage": "complete",
                    "project_path": str(project_path),
                    "assets": list(state["assets"].keys()),
                    "files": list(state["code"].keys())
                }),
                display="none"
            )
        ]
    ).send()


async def handle_academy_message(message: cl.Message):
    """Handle academy mode messages through educational flow."""
    state = cl.user_session.get("academy_state")
    stage = state["stage"]
    
    if stage == "welcome":
        if "start" in message.content.lower() or "begin" in message.content.lower():
            state["stage"] = "skill_assessment"
            cl.user_session.set("academy_state", state)
            
            await cl.Message(
                content="""
🎯 **Skill Assessment**

Professor Pixel: "Let's see what you already know! This helps me customize your learning journey."

**Question 1**: Have you programmed before?
- A) Never programmed
- B) Some experience (HTML/CSS, Scratch, etc.)
- C) Comfortable with Python or similar
- D) Advanced programmer

Type your answer (A, B, C, or D):
""",
                elements=[
                    cl.Text(
                        name="ui_state",
                        content=json.dumps({
                            "type": "academy_update",
                            "stage": "skill_assessment",
                            "question": 1
                        }),
                        display="none"
                    )
                ]
            ).send()
            
    elif stage == "skill_assessment":
        await handle_skill_assessment(message.content, state)
        
    elif stage == "lesson_active":
        await handle_lesson_interaction(message.content, state)
        
    elif stage == "challenge":
        await handle_challenge_submission(message.content, state)


async def handle_skill_assessment(answer: str, state: Dict[str, Any]):
    """Handle skill assessment flow."""
    answer = answer.upper().strip()
    
    if answer in ["A", "B", "C", "D"]:
        # Determine skill level
        skill_levels = {"A": "beginner", "B": "intermediate", "C": "advanced", "D": "expert"}
        state["skill_level"] = skill_levels[answer]
        state["stage"] = "lesson_selection"
        cl.user_session.set("academy_state", state)
        
        # Start first lesson based on skill level
        lesson = get_appropriate_lesson(state["skill_level"])
        state["lesson"] = lesson
        state["stage"] = "lesson_active"
        cl.user_session.set("academy_state", state)
        
        await start_academy_lesson(lesson, state)


async def start_academy_lesson(lesson: Dict[str, Any], state: Dict[str, Any]):
    """Start an academy lesson with Professor Pixel."""
    # Generate Professor Pixel's voice
    intro_audio = await generate_voice_acting(
        text=lesson["intro"],
        character_name="Professor Pixel",
        voice="nova",  # Friendly voice
        emotion="encouraging",
        save_path="temp/professor_intro.mp3"
    )
    
    await cl.Message(
        content=f"""
📚 **Lesson: {lesson['title']}**

{lesson['intro']}

**Today's Goal**: {lesson['goal']}

Let's start with a simple example:

```python
{lesson['code_example']}
```

**Your Challenge**: {lesson['challenge']}

Type your code when ready!
""",
        elements=[
            cl.Audio(path=intro_audio.path) if intro_audio.path else None,
            cl.Text(
                name="ui_state",
                content=json.dumps({
                    "type": "academy_lesson",
                    "stage": "lesson_active",
                    "lesson": lesson['id'],
                    "progress": state["progress"]
                }),
                display="none"
            )
        ]
    ).send()


# Helper functions
def determine_sprites_needed(description: str, engine: str) -> List[str]:
    """Determine what sprites are needed based on game description."""
    sprites = ["player"]
    
    desc_lower = description.lower()
    if "enemy" in desc_lower or "monster" in desc_lower:
        sprites.append("enemy")
    if "coin" in desc_lower or "collect" in desc_lower:
        sprites.append("collectible")
    if "platform" in desc_lower:
        sprites.append("platform")
    if "power" in desc_lower:
        sprites.append("powerup")
        
    return sprites


def extract_scene_from_description(description: str) -> str:
    """Extract scene/environment from game description."""
    desc_lower = description.lower()
    
    if "space" in desc_lower:
        return "space station with stars"
    elif "fantasy" in desc_lower or "medieval" in desc_lower:
        return "fantasy forest with castle"
    elif "cyberpunk" in desc_lower or "cyber" in desc_lower:
        return "cyberpunk city with neon lights"
    elif "underwater" in desc_lower or "ocean" in desc_lower:
        return "underwater scene with coral"
    else:
        return "colorful game environment"


def extract_theme_from_description(description: str) -> str:
    """Extract UI theme from game description."""
    desc_lower = description.lower()
    
    if "sci-fi" in desc_lower or "space" in desc_lower or "cyber" in desc_lower:
        return "sci-fi"
    elif "fantasy" in desc_lower or "medieval" in desc_lower:
        return "fantasy"
    elif "retro" in desc_lower or "arcade" in desc_lower:
        return "retro"
    else:
        return "modern"


def get_appropriate_lesson(skill_level: str) -> Dict[str, Any]:
    """Get an appropriate lesson based on skill level."""
    lessons = {
        "beginner": {
            "id": "variables_101",
            "title": "Variables: Your Game's Memory",
            "intro": "Welcome, young coder! Today we'll learn about variables - think of them as labeled boxes where your game stores information!",
            "goal": "Create variables to track player score and lives",
            "code_example": """# Variables are like labeled boxes
player_name = "Hero"
score = 0
lives = 3

# We can change what's in the box
score = score + 10
print(f"{player_name} has {score} points!")""",
            "challenge": "Create variables for a player's health (starting at 100) and gold (starting at 50)"
        },
        "intermediate": {
            "id": "game_loops",
            "title": "Game Loops: The Heart of Your Game",
            "intro": "Ready to make things move? Game loops are what make games tick - literally!",
            "goal": "Create a game loop that updates and draws continuously",
            "code_example": """# Basic game loop structure
running = True
while running:
    # Handle events
    for event in get_events():
        if event.type == "QUIT":
            running = False
    
    # Update game state
    player.move()
    enemies.update()
    
    # Draw everything
    screen.clear()
    player.draw()
    enemies.draw()""",
            "challenge": "Add a frame counter to the game loop that increases each frame"
        }
    }
    
    return lessons.get(skill_level, lessons["beginner"])


def save_workshop_project(state: Dict[str, Any]) -> Path:
    """Save the workshop project to disk."""
    # Create project directory
    project_name = f"workshop_{state['engine']}_{int(asyncio.get_event_loop().time())}"
    project_path = Path("generated_games") / project_name
    project_path.mkdir(parents=True, exist_ok=True)
    
    # Save code files
    for filename, content in state["code"].items():
        (project_path / filename).write_text(content)
    
    # Save asset metadata
    assets_meta = {
        "engine": state["engine"],
        "description": state["description"],
        "assets": {k: str(v) if hasattr(v, '__dict__') else v for k, v in state["assets"].items()}
    }
    (project_path / "assets.json").write_text(json.dumps(assets_meta, indent=2))
    
    return project_path


async def send_progress_update(message: str, progress: int):
    """Send progress update to UI."""
    await cl.Message(
        content="",
        elements=[
            cl.Text(
                name="progress_update",
                content=json.dumps({
                    "type": "progress",
                    "message": message,
                    "progress": progress
                }),
                display="none"
            )
        ]
    ).send()


async def handle_workshop_customization(request: str, state: Dict[str, Any]):
    """Handle customization requests after game generation."""
    # Determine what the user wants to customize
    request_lower = request.lower()
    
    if "sprite" in request_lower or "character" in request_lower:
        await cl.Message("Let me generate a new sprite for you. What would you like?").send()
        # Handle sprite regeneration
        
    elif "mechanic" in request_lower or "variant" in request_lower:
        # Generate mechanic variants
        variants = await generate_mechanic_variants(
            base_code=state["code"].get("main.py", ""),
            mechanic_type="movement",
            count=3
        )
        
        await cl.Message(
            content="Here are some mechanic variants you can try:",
            elements=[
                cl.Text(
                    name=f"variant_{i}",
                    content=f"**{var.name}**\n{var.description}\n\n```python\n{var.code}\n```",
                    display="inline"
                )
                for i, var in enumerate(variants)
            ]
        ).send()


async def handle_lesson_interaction(code: str, state: Dict[str, Any]):
    """Handle code submission during lessons."""
    # Check if the code meets the challenge requirements
    lesson = state["lesson"]
    
    # Simple validation (in real implementation, would be more sophisticated)
    if "health" in code and "gold" in code and "=" in code:
        # Success!
        state["progress"]["xp"] += 50
        state["progress"]["lessons"].append(lesson["id"])
        
        if state["progress"]["xp"] >= 100:
            state["progress"]["level"] += 1
            state["progress"]["xp"] = 0
        
        cl.user_session.set("academy_state", state)
        
        await cl.Message(
            content=f"""
🎉 **Excellent work!**

Professor Pixel: "That's exactly right! You've mastered {lesson['title']}!"

**+50 XP earned!**
{f"**LEVEL UP! You're now level {state['progress']['level']}!**" if state["progress"]["xp"] == 0 else ""}

Ready for the next lesson? Type 'continue' or 'next'!
""",
            elements=[
                cl.Text(
                    name="ui_state",
                    content=json.dumps({
                        "type": "academy_progress",
                        "stage": "lesson_complete",
                        "progress": state["progress"]
                    }),
                    display="none"
                )
            ]
        ).send()
    else:
        # Provide helpful feedback
        await cl.Message(
            content="""
🤔 **Not quite right...**

Professor Pixel: "Good try! Remember, we need to create two variables:
- `health` starting at 100
- `gold` starting at 50

Here's a hint:
```python
variable_name = value
```

Try again!
"""
        ).send()


async def handle_challenge_submission(code: str, state: Dict[str, Any]):
    """Handle challenge code submissions."""
    # Validate and provide feedback on challenge submissions
    pass
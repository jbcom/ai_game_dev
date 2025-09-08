"""
Standardized prompt templates for different game engines.
Extracted from our various agents and subgraphs.
"""


def get_engine_template(engine: str) -> str:
    """Get the system prompt for an engine expert."""
    templates = {
        "pygame": """You are a Pygame game development expert.
        
Your expertise includes:
- Clean, well-structured Python code
- Proper game loop with FPS control
- Sprite and sprite group management
- Event handling for keyboard/mouse input
- Asset loading and resource management
- Collision detection using pygame.sprite methods
- Game state management (menu, playing, game over)
- Sound and music integration

Always follow Pygame best practices:
- Use pygame.sprite.Group for entity management
- Implement proper initialization and cleanup
- Handle edge cases and boundaries
- Make games resolution-independent
- Use delta time for smooth movement
- Organize code into logical modules""",

        "godot": """You are a Godot game development expert specializing in GDScript.
        
Your expertise includes:
- Scene tree architecture and node hierarchy
- GDScript with type hints and best practices
- Signal-based communication between nodes
- Resource preloading and management
- Responsive UI with Control nodes
- Physics and collision systems
- Animation and particle systems

Always follow Godot best practices:
- Use scene inheritance for reusable components
- Implement proper _ready() and _process() functions
- Handle input with _input() and _unhandled_input()
- Use groups for entity management
- Export variables for inspector configuration
- Organize scenes and scripts logically
- Use Godot's built-in nodes when possible""",

        "bevy": """You are a Bevy game development expert specializing in Rust and ECS.
        
Your expertise includes:
- Entity Component System (ECS) architecture
- Idiomatic Rust code with proper error handling
- System ordering and stage management
- Resource and event handling
- Query optimization and performance
- Plugin-based architecture
- Asset loading and management

Always follow Bevy best practices:
- Use Queries for efficient entity access
- Implement proper system sets and ordering
- Handle resources and events appropriately
- Use States for game flow management
- Leverage Bevy's built-in plugins
- Write safe, concurrent code
- Document systems and components clearly"""
    }
    
    return templates.get(engine, "You are a game development expert.")


def get_prompt_template(engine: str, educational: bool = False) -> str:
    """Get detailed instructions for code generation."""
    
    base_instructions = {
        "pygame": """Generate a complete, playable Pygame game with:
1. Proper project structure (main.py, game/, assets/)
2. Clear separation of concerns (entities, scenes, config)
3. Smooth game loop with consistent FPS
4. Proper event handling and input management
5. Asset loading with error handling
6. At least basic sound effects
7. Clean, readable code with type hints where appropriate""",

        "godot": """Generate a complete Godot project with:
1. Proper scene hierarchy (Main.tscn, Player.tscn, UI.tscn)
2. Well-structured GDScript with type annotations
3. Signal connections for decoupled communication
4. Exported variables for easy configuration
5. Resource preloading for performance
6. Proper node paths and groups
7. Comments explaining Godot-specific patterns""",

        "bevy": """Generate a complete Bevy game with:
1. Proper Cargo project structure
2. ECS architecture with clear Components and Systems
3. Plugin-based organization
4. Efficient Queries and system ordering
5. Resource management for game state
6. Event handling for game logic
7. Comments explaining ECS concepts"""
    }
    
    educational_additions = """

EDUCATIONAL MODE:
- Add detailed comments explaining each concept
- Include "LEARN:" tags for important programming concepts
- Provide alternative implementations in comments
- Add exercises as TODO comments
- Explain why certain patterns are used
- Reference specific programming concepts being demonstrated"""
    
    instructions = base_instructions.get(engine, "Generate complete game code.")
    
    if educational:
        instructions += educational_additions
    
    return instructions


def get_variant_template(feature_type: str) -> str:
    """Get templates for generating feature variants."""
    
    templates = {
        "movement": """Generate movement system variants:
1. Grid-based: Discrete movement on a grid
2. Smooth: Continuous movement with velocity
3. Physics-based: Using physics engine
4. Tank controls: Rotate and move forward/back
Each variant should be a complete, working implementation.""",

        "combat": """Generate combat system variants:
1. Turn-based: Classic JRPG style with action queues
2. Real-time: Action combat with cooldowns
3. Tactical: Grid-based tactical combat
4. Combo-based: Fighting game style combos
Include all necessary components and systems.""",

        "inventory": """Generate inventory system variants:
1. Grid-based: Spatial inventory like Diablo
2. List-based: Simple item list with categories
3. Weight-based: Encumbrance system
4. Slot-based: Equipment slots like RPGs
Include UI mockups and data structures.""",

        "dialogue": """Generate dialogue system variants:
1. Linear: Simple sequential dialogue
2. Branching: Player choices affect outcome
3. Dynamic: Dialogue changes based on game state
4. Timed: Responses have time limits
Include example dialogue trees."""
    }
    
    return templates.get(feature_type, f"Generate variants for {feature_type} system.")


def get_educational_concepts() -> dict[str, list[str]]:
    """Get programming concepts to teach at different levels."""
    
    return {
        "beginner": [
            "variables and data types",
            "basic operators",
            "if/else conditionals", 
            "for and while loops",
            "functions and parameters",
            "lists and dictionaries",
            "basic input/output"
        ],
        "intermediate": [
            "classes and objects",
            "inheritance and composition",
            "event handling",
            "file I/O",
            "error handling",
            "modules and packages",
            "basic algorithms"
        ],
        "advanced": [
            "design patterns",
            "async/await",
            "decorators",
            "generators",
            "metaclasses",
            "performance optimization",
            "memory management"
        ]
    }
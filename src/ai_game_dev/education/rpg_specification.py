"""
Complete Late 90s JRPG Specification for Educational Purposes
Inspired by classics like Final Fantasy VI, Secret of Mana, and Chrono Trigger
This will be used to pre-generate a full playable RPG using our AI tools
"""

RPG_GAME_SPEC = {
    "name": "Legends of Code Valley",
    "description": "An epic educational JRPG where students learn Python by following the adventures of young programmers in a magical realm",
    "engine": "pygame",
    "complexity": "advanced", 
    "art_style": "16-bit pixel art",
    "view_perspective": "3/4 top-down isometric",
    "target_resolution": "1280x720",
    "inspiration": "Final Fantasy VI, Secret of Mana, Chrono Trigger, Radiant Historia",
    
    "core_systems": {
        "party_system": {
            "max_party_size": 4,
            "character_switching": True,
            "formation_system": ["front_row", "back_row"],
            "combo_attacks": True
        },
        
        "character_classes": [
            {
                "name": "Code Knight",
                "description": "Defender of logical order, masters object-oriented programming",
                "base_stats": {"health": 120, "mana": 60, "attack": 15, "defense": 18, "speed": 8, "luck": 10},
                "primary_stat": "defense",
                "abilities": ["Class Shield", "Method Strike", "Inheritance Barrier", "Polymorphic Slash"],
                "starting_equipment": ["Syntax Sword", "Logic Shield", "Debugger Armor"],
                "signature_move": "Encapsulation Fortress",
                "learns_concepts": ["OOP", "Classes", "Inheritance", "Polymorphism"]
            },
            {
                "name": "Data Sage",
                "description": "Wise manipulator of information structures and algorithms",
                "base_stats": {"health": 85, "mana": 180, "attack": 10, "defense": 8, "speed": 12, "luck": 15},
                "primary_stat": "mana",
                "abilities": ["List Lightning", "Dict Heal", "Sort Storm", "Algorithm Aura"],
                "starting_equipment": ["Staff of Arrays", "Robes of Recursion", "Tome of Big-O"],
                "signature_move": "Fractal Recursion",
                "learns_concepts": ["Data Structures", "Algorithms", "Complexity", "Recursion"]
            },
            {
                "name": "Bug Hunter",
                "description": "Swift tracker of errors with keen debugging instincts",
                "base_stats": {"health": 100, "mana": 90, "attack": 16, "defense": 10, "speed": 18, "luck": 12},
                "primary_stat": "speed", 
                "abilities": ["Exception Strike", "Try-Catch Dodge", "Assert Trap", "Stack Trace"],
                "starting_equipment": ["Debugging Dagger", "Exception Cloak", "Logging Lens"],
                "signature_move": "Perfect Traceback",
                "learns_concepts": ["Error Handling", "Debugging", "Testing", "Logging"]
            },
            {
                "name": "Web Weaver",
                "description": "Creator of digital realms and interactive experiences",
                "base_stats": {"health": 95, "mana": 120, "attack": 12, "defense": 9, "speed": 14, "luck": 20},
                "primary_stat": "luck",
                "abilities": ["HTML Heal", "CSS Style", "JS Dynamic", "API Call"],
                "starting_equipment": ["Framework Wand", "Responsive Robe", "Browser Badge"],
                "signature_move": "Full Stack Fusion",
                "learns_concepts": ["Web Dev", "APIs", "Frameworks", "UI/UX"]
            }
        ],
        
        "leveling_system": {
            "max_level": 99,  # Classic JRPG max level
            "xp_formula": "logarithmic",  # XP = base * (level^1.5) 
            "base_xp": 100,
            "stat_growth_per_level": {
                "health": 8,
                "mana": 5,
                "attack": 3,
                "defense": 2,
                "speed": 2,
                "luck": 1
            },
            "skill_points_per_level": 2,
            "ability_unlock_levels": [5, 12, 20, 35, 50, 75, 90]
        },
        
        "skill_trees": {
            "branching_paths": True,
            "prerequisite_system": True,
            "max_skills_learnable": "75% of total",
            "skill_categories": ["Offensive", "Defensive", "Utility", "Passive", "Ultimate"]
        },
        
        "combat_system": {
            "style": "Active Time Battle (ATB)",  # Like FF6/Chrono Trigger
            "turn_based": True,
            "time_bars": True,
            "combo_system": True,
            "elemental_system": ["Fire", "Ice", "Lightning", "Earth", "Water", "Wind", "Light", "Dark"],
            "damage_formula": "(attack + weapon_power) * skill_multiplier * elemental_modifier - (defense + armor) * random(0.8, 1.2)",
            "critical_chance": "(speed + luck) / 200",
            "critical_multiplier": 2.5,
            "status_effects": [
                "poison", "stun", "burn", "freeze", "paralysis", "sleep", "charm", "berserk",
                "haste", "slow", "regen", "protect", "shell", "reflect", "zombie", "stone"
            ],
            "formation_effects": {
                "front_row": "150% physical damage dealt, 150% physical damage taken",
                "back_row": "50% physical damage dealt, 50% physical damage taken, magic unaffected"
            },
            "special_attacks": {
                "limit_breaks": True,
                "combination_techs": True,
                "environmental_interactions": True
            }
        },
        
        "inventory_management": {
            "max_items": 99,  # Classic stack limit
            "item_categories": ["weapons", "armor", "accessories", "consumables", "key_items", "materials", "tools"],
            "equipment_slots": ["right_hand", "left_hand", "head", "body", "accessory1", "accessory2"],
            "stackable_items": ["potions", "materials", "arrows", "consumables"],
            "rare_items": True,
            "cursed_items": True,
            "item_synthesis": True,
            "equipment_upgrading": True
        },
        
        "magic_system": {
            "spell_schools": ["Elemental", "Healing", "Support", "Summoning", "Time", "Space"],
            "mp_cost_scaling": True,
            "spell_levels": [1, 2, 3, 4, 5],  # Like FF series
            "learning_methods": ["level_up", "item_use", "enemy_skill", "esper_equipped"],
            "summon_creatures": [
                "Ifrit (Fire)", "Shiva (Ice)", "Ramuh (Lightning)", "Titan (Earth)",
                "Leviathan (Water)", "Bahamut (Non-elemental)", "Phoenix (Revival)"
            ]
        },
        
        "mini_games": [
            "Chocobo Racing (teaches loops and timing)",
            "Slot Machine (teaches probability and random)", 
            "Card Game (teaches logic and strategy)",
            "Fishing (teaches patience and algorithms)",
            "Arena Tournaments (teaches competition AI)"
        ],
    },
    
    "world_design": {
        "overworld_map": {
            "name": "The Realm of Code Valley", 
            "size": "100x80 tiles",
            "biomes": [
                "Binary Plains (grassland with 0/1 patterns)",
                "Function Forest (tree-like call stacks)", 
                "Variable Mountains (constantly changing peaks)",
                "Loop Desert (endless recursive patterns)",
                "Exception Swamp (error-prone marshland)",
                "Cloud City (floating data structures)",
                "Underwater Database (deep blue data lakes)"
            ],
            "landmarks": [
                "The Great Compiler (massive central tower)",
                "Syntax Gardens (beautiful, perfectly formatted)",
                "Memory Palace (shifting magical library)",
                "Bug Graveyard (dark, glitchy wasteland)",
                "The Infinite Recursion (mystical spiral)",
                "Algorithm Academy (Professor Pixel's school)",
                "The Final Boss Tower (malware stronghold)"
            ],
            "travel_system": "tile-based movement with educational random encounters",
            "vehicles": [
                "Walking (default)",
                "Debug Horse (faster, reveals hidden paths)", 
                "Flying Sprite (airship equivalent)",
                "Submarine Object (underwater exploration)"
            ]
        },
        
        "villages_and_towns": [
            {
                "name": "Newbie Valley",
                "size": "25x20 tiles",
                "theme": "Beginner-friendly tutorial town",
                "npcs": [
                    "Master Print (teaches output)",
                    "Variable Vendor (explains data types)", 
                    "Loop Librarian (teaches iteration)",
                    "Condition Keeper (explains if/else)",
                    "Function Forger (introduces functions)"
                ],
                "buildings": ["Basic Syntax Shop", "Type Inn", "Logic Guild", "Error Clinic"],
                "purpose": "Learn fundamental programming concepts"
            },
            {
                "name": "Object Oriented Oasis",
                "size": "40x30 tiles",
                "theme": "Advanced OOP concepts",
                "npcs": [
                    "Class Constructor", "Method Master", "Inheritance Oracle", 
                    "Polymorphism Sage", "Encapsulation Guardian"
                ],
                "buildings": ["Class Factory", "Method Market", "Inheritance Inn", "Abstraction Academy"],
                "purpose": "Master object-oriented programming"
            },
            {
                "name": "Data Structure City",
                "size": "50x35 tiles",
                "theme": "Complex data manipulation hub",
                "npcs": [
                    "Array Architect", "List Lord", "Dictionary Duchess",
                    "Set Sovereign", "Tuple Tycoon", "Stack Samurai", "Queue Queen"
                ],
                "buildings": ["Big-O Observatory", "Algorithm Arena", "Sorting Stadium", "Search Sanctuary"],
                "purpose": "Learn advanced data structures and algorithms"
            },
            {
                "name": "Web Framework Metropolis", 
                "size": "60x45 tiles",
                "theme": "Modern web development",
                "npcs": [
                    "HTML Hero", "CSS Stylist", "JavaScript Jedi",
                    "API Ambassador", "Database Duke", "Framework Pharaoh"
                ],
                "buildings": ["Server Skyscraper", "Client Castle", "Database Dome", "API Arcade"],
                "purpose": "Build full-stack web applications"
            }
        ],
        
        "dungeon_system": {
            "procedural_generation": True,
            "generation_algorithm": "room-and-corridor with BSP tree (teaches recursive algorithms)",
            "dungeon_types": [
                "Syntax Caves (basic programming challenges)",
                "Logic Labyrinth (conditional puzzles)",
                "Loop Towers (iteration challenges)", 
                "Function Fortress (modular programming)",
                "Class Crypts (OOP boss battles)",
                "Algorithm Abyss (optimization challenges)",
                "Bug Basement (debugging nightmare)",
                "Memory Mines (data structure mazes)",
                "Recursion Ruins (infinite self-reference)",
                "Final Virus Vault (ultimate malware boss)"
            ],
            "room_sizes": "variable 8x8 to 20x20",
            "corridor_width": 3,
            "treasure_room_chance": 0.20,
            "boss_room_required": True,
            "puzzle_rooms": True,
            "trap_rooms": True,
            "secret_passages": True,
            "enemy_density": "1 enemy per 15 tiles average",
            "loot_distribution": "progressive based on depth and programming concept difficulty",
            "environmental_puzzles": [
                "Code block pushing (Sokoban-style)",
                "Switch sequences (logic gates)",
                "Pattern matching floors",
                "Timed coding challenges"
            ]
        }
    },
    
    "technical_implementation": {
        "map_system": {
            "tile_size": 32,
            "map_format": "2D array with tile IDs",
            "collision_detection": "tile-based with solid/passable flags",
            "layer_system": ["background", "decoration", "collision", "entities"]
        },
        
        "minimap": {
            "size": "200x150 pixels",
            "position": "top-right corner",
            "zoom_levels": [1.0, 0.5, 0.25],
            "fog_of_war": True,
            "explored_area_tracking": True,
            "point_of_interest_markers": True
        },
        
        "ui_components": [
            "Health/Mana bars with animation",
            "Experience bar with level display", 
            "Inventory grid with drag-and-drop",
            "Character stats panel",
            "Quest log with progress tracking",
            "Mini-map with explored areas",
            "Combat action menu",
            "Dialogue system with choices"
        ],
        
        "asset_requirements": {
            "sprites": {
                "player_characters": "3 classes x 4 directions x 4 animation frames = 48 sprites",
                "enemies": "12 different enemies x 4 directions x 3 frames = 144 sprites",
                "npcs": "20 unique NPCs x 4 directions = 80 sprites",
                "items": "100 different items (weapons, armor, consumables)",
                "ui_elements": "50 buttons, panels, icons"
            },
            "tilesets": {
                "overworld": "grass, trees, mountains, water, paths - 64 tiles",
                "village": "buildings, doors, windows, decorations - 48 tiles", 
                "dungeon": "walls, floors, stairs, treasures - 32 tiles",
                "interiors": "furniture, carpets, walls - 40 tiles"
            },
            "audio": {
                "music": ["overworld_theme.ogg", "village_theme.ogg", "dungeon_theme.ogg", "battle_theme.ogg"],
                "sound_effects": ["attack.wav", "hit.wav", "pickup.wav", "footstep.wav", "menu_select.wav"]
            }
        },
        
        "code_architecture": {
            "main_modules": [
                "game.py - Main game loop and state management",
                "player.py - Player character class with stats and inventory",
                "combat.py - Turn-based combat system",
                "world.py - Map loading and world state",
                "ui.py - User interface rendering and input",
                "entities.py - NPCs, enemies, and interactive objects",
                "items.py - Item definitions and equipment system",
                "dungeon_generator.py - Procedural dungeon creation",
                "save_system.py - Game save/load functionality"
            ],
            "design_patterns": [
                "State Machine for game states (menu, playing, combat, inventory)",
                "Entity-Component System for game objects",
                "Observer pattern for UI updates",
                "Command pattern for input handling",
                "Factory pattern for enemy/item creation"
            ]
        }
    },
    
    "educational_objectives": {
        "python_concepts": [
            "Object-Oriented Programming (classes, inheritance, polymorphism)",
            "Data Structures (lists, dictionaries, sets, tuples)",
            "File I/O for save systems and asset loading",
            "Exception Handling for robust game operation",
            "Algorithms (pathfinding, random generation, sorting)",
            "Event-Driven Programming with pygame events",
            "State Management and game loops",
            "JSON/data serialization",
            "Module organization and imports"
        ],
        "game_development_concepts": [
            "Game loop architecture and timing",
            "Sprite animation and rendering",
            "Collision detection algorithms", 
            "Map and level design principles",
            "User interface design and usability",
            "Game balance and progression systems",
            "Procedural generation techniques",
            "Audio integration and sound design",
            "Performance optimization strategies"
        ],
        "progression_structure": [
            "Chapter 1: Basic game window and player movement",
            "Chapter 2: Sprite loading and animation",
            "Chapter 3: Map system and collision detection",
            "Chapter 4: Character stats and progression",
            "Chapter 5: Combat system implementation",
            "Chapter 6: Inventory and item management", 
            "Chapter 7: NPCs and dialogue system",
            "Chapter 8: Dungeon generation algorithms",
            "Chapter 9: UI design and user experience",
            "Chapter 10: Audio, effects, and polish"
        ]
    }
}
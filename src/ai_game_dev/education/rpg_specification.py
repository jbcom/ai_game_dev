"""
Complete Late 90s JRPG Specification for Educational Purposes
Inspired by classics like Final Fantasy VI, Secret of Mana, and Chrono Trigger
This will be used to pre-generate a full playable RPG using our AI tools
"""

RPG_GAME_SPEC = {
    "name": "Dragon's Academy RPG",
    "description": "A comprehensive educational RPG showcasing all aspects of Python game development",
    "engine": "pygame",
    "complexity": "advanced",
    "art_style": "16-bit pixel art",
    "view_perspective": "3/4 top-down isometric",
    "target_resolution": "1280x720",
    
    "core_systems": {
        "character_classes": [
            {
                "name": "Warrior",
                "description": "Melee combat specialist with high health and defense",
                "base_stats": {"health": 120, "mana": 50, "attack": 15, "defense": 12, "speed": 8},
                "primary_stat": "attack",
                "abilities": ["Sword Strike", "Shield Block", "Berserker Rage"],
                "starting_equipment": ["Iron Sword", "Wooden Shield", "Leather Armor"]
            },
            {
                "name": "Mage",
                "description": "Magical damage dealer with powerful spells but low health",
                "base_stats": {"health": 80, "mana": 150, "attack": 8, "defense": 6, "speed": 10},
                "primary_stat": "mana",
                "abilities": ["Fireball", "Heal", "Lightning Bolt", "Mana Shield"],
                "starting_equipment": ["Magic Staff", "Robe of Power", "Mana Potion"]
            },
            {
                "name": "Rogue",
                "description": "Fast agile fighter with critical hit potential",
                "base_stats": {"health": 100, "mana": 75, "attack": 12, "defense": 8, "speed": 15},
                "primary_stat": "speed",
                "abilities": ["Backstab", "Stealth", "Poison Dart", "Quick Strike"],
                "starting_equipment": ["Dagger", "Throwing Knives", "Cloak of Shadows"]
            }
        ],
        
        "leveling_system": {
            "max_level": 50,
            "xp_formula": "logarithmic",  # XP = base * (level^1.5) 
            "base_xp": 100,
            "stat_growth_per_level": {
                "health": 5,
                "mana": 3,
                "attack": 2,
                "defense": 1,
                "speed": 1
            }
        },
        
        "combat_system": {
            "turn_based": True,
            "damage_formula": "attack * (1 + random(0.8, 1.2)) - enemy_defense * 0.5",
            "critical_chance": "speed / 100",
            "critical_multiplier": 2.0,
            "status_effects": ["poison", "stun", "burn", "freeze", "heal_over_time"]
        },
        
        "inventory_management": {
            "max_items": 50,
            "item_categories": ["weapons", "armor", "consumables", "key_items", "materials"],
            "equipment_slots": ["weapon", "armor", "accessory"],
            "stackable_items": ["potions", "materials", "arrows"]
        }
    },
    
    "world_design": {
        "overworld_map": {
            "name": "Kingdom of Pythonia",
            "size": "50x50 tiles",
            "biomes": ["grassland", "forest", "mountains", "desert", "swamp"],
            "landmarks": ["Dragon's Peak", "Mystic Forest", "Crystal Caves", "Ancient Ruins"],
            "travel_system": "tile-based movement with random encounters"
        },
        
        "villages_and_towns": [
            {
                "name": "Starter Village",
                "size": "20x15 tiles",
                "npcs": ["Blacksmith", "Item Shop Owner", "Inn Keeper", "Quest Giver", "Trainer"],
                "buildings": ["Weapon Shop", "Item Shop", "Inn", "Guild Hall", "Training Grounds"],
                "purpose": "Tutorial area with basic services"
            },
            {
                "name": "Port Town",
                "size": "30x25 tiles", 
                "npcs": ["Harbor Master", "Ship Captain", "Fish Vendor", "Sailor", "Merchant"],
                "buildings": ["Harbor", "Tavern", "Warehouse", "Lighthouse", "Market"],
                "purpose": "Mid-game hub with advanced equipment"
            }
        ],
        
        "dungeon_system": {
            "procedural_generation": True,
            "generation_algorithm": "room-and-corridor with BSP tree",
            "dungeon_types": ["Cave System", "Ancient Temple", "Underground Fortress", "Crystal Mine"],
            "room_sizes": "variable 5x5 to 15x15",
            "corridor_width": 3,
            "treasure_room_chance": 0.15,
            "boss_room_required": True,
            "enemy_density": "1 enemy per 20 tiles average",
            "loot_distribution": "progressive based on depth"
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
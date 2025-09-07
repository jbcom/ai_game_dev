"""
Game Specification Builder Subgraph
Converts user descriptions and engine choices into comprehensive game specifications
"""
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage

from ai_game_dev.agents.base_agent import BaseAgent, AgentConfig


@dataclass
class GameSpecState:
    """State for game specification building."""
    user_description: str = ""
    engine: str = "pygame"
    detected_genre: str = ""
    detected_features: List[str] = field(default_factory=list)
    detected_art_style: str = "modern"
    complexity: str = "intermediate"
    target_audience: str = "general"
    generated_spec: Dict[str, Any] = field(default_factory=dict)
    validation_errors: List[str] = field(default_factory=list)
    spec_complete: bool = False


class GameSpecSubgraph(BaseAgent):
    """
    Subgraph for building comprehensive game specifications from user input.
    
    Capabilities:
    - Natural language parsing of game descriptions
    - Feature detection and extraction
    - Genre classification
    - Art style inference
    - Complexity assessment
    - Complete spec generation with all required fields
    """
    
    def __init__(self):
        config = AgentConfig(
            model="gpt-4o",
            temperature=0.3,
            instructions=self._get_spec_builder_instructions()
        )
        super().__init__(config)
        self.graph = None
    
    def _get_spec_builder_instructions(self) -> str:
        return """You are a game specification expert who converts natural language game descriptions 
        into comprehensive, structured game specifications.
        
        Your task is to:
        1. Extract key features from the description
        2. Detect the game genre
        3. Infer the art style
        4. Assess complexity
        5. Generate a complete specification with all required fields
        
        Output structured JSON specifications that include:
        - title
        - description  
        - genre
        - features (list)
        - art_style
        - target_audience
        - complexity
        - mechanics (detailed gameplay systems)
        - assets_needed (comprehensive list)
        - technical_requirements
        """
    
    async def initialize(self):
        """Initialize the game spec subgraph."""
        await super().initialize()
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build the game specification workflow graph."""
        workflow = StateGraph(GameSpecState)
        
        # Add nodes
        workflow.add_node("parse_description", self._parse_description)
        workflow.add_node("detect_features", self._detect_features)
        workflow.add_node("classify_genre", self._classify_genre)
        workflow.add_node("assess_complexity", self._assess_complexity)
        workflow.add_node("generate_spec", self._generate_spec)
        workflow.add_node("validate_spec", self._validate_spec)
        
        # Add edges
        workflow.set_entry_point("parse_description")
        workflow.add_edge("parse_description", "detect_features")
        workflow.add_edge("detect_features", "classify_genre")
        workflow.add_edge("classify_genre", "assess_complexity")
        workflow.add_edge("assess_complexity", "generate_spec")
        workflow.add_edge("generate_spec", "validate_spec")
        workflow.add_edge("validate_spec", END)
        
        return workflow.compile()
    
    async def _parse_description(self, state: GameSpecState) -> GameSpecState:
        """Parse the user's game description."""
        messages = [
            HumanMessage(content=f"""
            Parse this game description and extract key elements:
            
            Description: {state.user_description}
            Engine: {state.engine}
            
            Extract:
            - Main gameplay concept
            - Key mechanics mentioned
            - Visual style hints
            - Target audience clues
            """)
        ]
        
        response = await self.llm.ainvoke(messages)
        # Process response to extract elements
        return state
    
    async def _detect_features(self, state: GameSpecState) -> GameSpecState:
        """Detect game features from the description."""
        description_lower = state.user_description.lower()
        
        # Feature detection logic
        feature_keywords = {
            "combat": ["fight", "battle", "combat", "attack", "defeat"],
            "puzzles": ["puzzle", "solve", "riddle", "challenge"],
            "exploration": ["explore", "discover", "adventure", "journey"],
            "story": ["story", "narrative", "plot", "tale"],
            "multiplayer": ["multiplayer", "co-op", "online", "versus"],
            "platforming": ["platform", "jump", "climb", "parkour"],
            "rpg": ["rpg", "role-playing", "character", "level up"],
            "strategy": ["strategy", "tactical", "plan", "resource"],
            "simulation": ["simulation", "sim", "manage", "build"],
            "racing": ["race", "racing", "speed", "track"],
            "survival": ["survival", "survive", "craft", "gather"],
            "stealth": ["stealth", "sneak", "hide", "infiltrate"]
        }
        
        detected_features = []
        for feature, keywords in feature_keywords.items():
            if any(keyword in description_lower for keyword in keywords):
                detected_features.append(feature)
        
        # Always add core features
        if not detected_features:
            detected_features = ["gameplay", "graphics", "audio"]
        
        state.detected_features = detected_features
        
        # Detect art style
        art_styles = {
            "pixel": ["pixel", "8-bit", "16-bit", "retro"],
            "low_poly": ["low poly", "lowpoly", "geometric"],
            "realistic": ["realistic", "photorealistic", "real"],
            "cartoon": ["cartoon", "toon", "animated"],
            "anime": ["anime", "manga", "japanese"],
            "cyberpunk": ["cyberpunk", "cyber", "neon", "futuristic"],
            "fantasy": ["fantasy", "magical", "medieval"],
            "minimalist": ["minimal", "simple", "clean"],
            "voxel": ["voxel", "minecraft", "blocky"]
        }
        
        for style, keywords in art_styles.items():
            if any(keyword in description_lower for keyword in keywords):
                state.detected_art_style = style
                break
        
        return state
    
    async def _classify_genre(self, state: GameSpecState) -> GameSpecState:
        """Classify the game genre based on features."""
        features = state.detected_features
        
        # Genre classification based on features
        if "platforming" in features:
            state.detected_genre = "platformer"
        elif "rpg" in features:
            state.detected_genre = "rpg"
        elif "strategy" in features:
            state.detected_genre = "strategy"
        elif "racing" in features:
            state.detected_genre = "racing"
        elif "puzzles" in features and "platforming" not in features:
            state.detected_genre = "puzzle"
        elif "combat" in features and "exploration" in features:
            state.detected_genre = "action_adventure"
        elif "combat" in features:
            state.detected_genre = "action"
        elif "simulation" in features:
            state.detected_genre = "simulation"
        elif "survival" in features:
            state.detected_genre = "survival"
        else:
            state.detected_genre = "arcade"
        
        return state
    
    async def _assess_complexity(self, state: GameSpecState) -> GameSpecState:
        """Assess the complexity of the game."""
        features_count = len(state.detected_features)
        description_length = len(state.user_description.split())
        
        # Complexity assessment
        if features_count <= 3 and description_length < 20:
            state.complexity = "simple"
        elif features_count >= 6 or description_length > 50:
            state.complexity = "complex"
        else:
            state.complexity = "intermediate"
        
        # Target audience inference
        description_lower = state.user_description.lower()
        if any(word in description_lower for word in ["kids", "children", "educational"]):
            state.target_audience = "children"
        elif any(word in description_lower for word in ["hardcore", "difficult", "challenging"]):
            state.target_audience = "hardcore"
        else:
            state.target_audience = "general"
        
        return state
    
    async def _generate_spec(self, state: GameSpecState) -> GameSpecState:
        """Generate the complete game specification."""
        
        # Generate a compelling title if not provided
        title_prompt = f"Generate a catchy game title for: {state.user_description}"
        title_response = await self.llm.ainvoke([HumanMessage(content=title_prompt)])
        title = title_response.content.strip('"').strip()
        
        # Build comprehensive specification
        game_spec = {
            "title": title,
            "description": state.user_description,
            "engine": state.engine,
            "genre": state.detected_genre,
            "features": state.detected_features,
            "art_style": state.detected_art_style,
            "complexity": state.complexity,
            "target_audience": state.target_audience,
            
            # Detailed mechanics based on genre and features
            "mechanics": self._generate_mechanics(state),
            
            # Comprehensive asset requirements
            "assets_needed": self._generate_asset_requirements(state),
            
            # Technical specifications
            "technical_requirements": {
                "resolution": "1280x720" if state.complexity != "simple" else "800x600",
                "fps_target": 60,
                "platform": "cross-platform",
                "save_system": state.complexity != "simple",
                "networking": "multiplayer" in state.detected_features
            },
            
            # Path specifications
            "paths": {
                "assets_base": "public/static/assets/generated",  # Relative to repo root
                "code_base": "generated_games",  # Relative to repo root
                "use_relative_paths": True,  # Use repo-relative paths
                "project_name": self._sanitize_project_name(title)
            },
            
            # Audio specifications
            "audio_specs": {
                "music_tracks": self._get_music_track_count(state),
                "sound_effects": self._get_sound_effects_list(state),
                "voice_acting": "story" in state.detected_features
            },
            
            # UI/UX specifications
            "ui_specs": {
                "menu_system": True,
                "hud_elements": self._get_hud_elements(state),
                "control_scheme": self._get_control_scheme(state)
            }
        }
        
        state.generated_spec = game_spec
        state.spec_complete = True
        return state
    
    def _generate_mechanics(self, state: GameSpecState) -> Dict[str, Any]:
        """Generate detailed game mechanics based on genre and features."""
        mechanics = {}
        
        # Core mechanics based on genre
        genre_mechanics = {
            "platformer": {
                "movement": {"jump": True, "double_jump": True, "wall_jump": True},
                "physics": {"gravity": 9.8, "friction": 0.8}
            },
            "rpg": {
                "character": {"stats": ["health", "mana", "attack", "defense"], "leveling": True},
                "inventory": {"slots": 20, "equipment": True}
            },
            "action": {
                "combat": {"combo_system": True, "special_attacks": True},
                "health": {"regeneration": False, "health_pickups": True}
            },
            "puzzle": {
                "puzzle_types": ["logic", "pattern", "spatial"],
                "hint_system": True
            },
            "strategy": {
                "resources": ["gold", "wood", "stone"],
                "units": {"types": 5, "upgrades": True}
            }
        }
        
        if state.detected_genre in genre_mechanics:
            mechanics.update(genre_mechanics[state.detected_genre])
        
        # Add feature-specific mechanics
        if "multiplayer" in state.detected_features:
            mechanics["multiplayer"] = {
                "max_players": 4,
                "modes": ["versus", "co-op"]
            }
        
        return mechanics
    
    def _generate_asset_requirements(self, state: GameSpecState) -> Dict[str, List[str]]:
        """Generate comprehensive asset requirements."""
        assets = {
            "sprites": [],
            "backgrounds": [],
            "ui_elements": [],
            "audio": [],
            "animations": []
        }
        
        # Player character
        assets["sprites"].append("player_character")
        assets["animations"].append("player_idle")
        assets["animations"].append("player_walk")
        
        # Genre-specific assets
        if state.detected_genre == "platformer":
            assets["sprites"].extend(["platform_tiles", "collectibles", "obstacles"])
            assets["backgrounds"].extend(["level_bg_1", "level_bg_2", "level_bg_3"])
            
        elif state.detected_genre == "rpg":
            assets["sprites"].extend(["npcs", "enemies", "items", "equipment"])
            assets["backgrounds"].extend(["town", "dungeon", "overworld"])
            assets["ui_elements"].extend(["inventory_ui", "character_sheet", "dialogue_box"])
            
        elif state.detected_genre == "action":
            assets["sprites"].extend(["enemies", "projectiles", "explosions"])
            assets["animations"].extend(["attack_combo_1", "attack_combo_2"])
            
        # Common UI elements
        assets["ui_elements"].extend([
            "main_menu_bg",
            "button_normal",
            "button_hover",
            "button_pressed",
            "health_bar",
            "pause_menu"
        ])
        
        # Audio assets
        assets["audio"].extend([
            "menu_music",
            "gameplay_music",
            "button_click",
            "player_jump",
            "player_hurt",
            "pickup_sound"
        ])
        
        return assets
    
    def _get_music_track_count(self, state: GameSpecState) -> int:
        """Determine number of music tracks needed."""
        if state.complexity == "simple":
            return 2  # Menu + gameplay
        elif state.complexity == "intermediate":
            return 4  # Menu + gameplay + boss + victory
        else:
            return 6  # Multiple level themes
    
    def _get_sound_effects_list(self, state: GameSpecState) -> List[str]:
        """Generate list of required sound effects."""
        effects = ["ui_click", "ui_hover", "pause", "unpause"]
        
        if "combat" in state.detected_features:
            effects.extend(["attack", "hit", "block", "death"])
        
        if "platforming" in state.detected_features:
            effects.extend(["jump", "land", "double_jump"])
            
        return effects
    
    def _get_hud_elements(self, state: GameSpecState) -> List[str]:
        """Determine HUD elements based on game type."""
        elements = []
        
        if state.detected_genre in ["action", "platformer", "rpg"]:
            elements.append("health_display")
            
        if state.detected_genre == "rpg":
            elements.extend(["mana_display", "experience_bar"])
            
        if "combat" in state.detected_features:
            elements.append("combo_counter")
            
        return elements
    
    def _get_control_scheme(self, state: GameSpecState) -> Dict[str, str]:
        """Define control scheme based on game type."""
        if state.detected_genre == "platformer":
            return {
                "move": "arrow_keys/wasd",
                "jump": "space",
                "action": "x"
            }
        elif state.detected_genre == "rpg":
            return {
                "move": "arrow_keys/wasd",
                "interact": "e",
                "inventory": "i",
                "menu": "esc"
            }
        else:
            return {
                "move": "arrow_keys/wasd",
                "action1": "left_click",
                "action2": "right_click"
            }
    
    async def _validate_spec(self, state: GameSpecState) -> GameSpecState:
        """Validate the generated specification."""
        spec = state.generated_spec
        errors = []
        
        # Required fields
        required_fields = ["title", "description", "engine", "genre", "features"]
        for field in required_fields:
            if field not in spec or not spec[field]:
                errors.append(f"Missing required field: {field}")
        
        # Engine validation
        valid_engines = ["pygame", "godot", "bevy"]
        if spec.get("engine") not in valid_engines:
            errors.append(f"Invalid engine: {spec.get('engine')}")
        
        state.validation_errors = errors
        return state
    
    def _sanitize_project_name(self, title: str) -> str:
        """Sanitize project name for filesystem."""
        import re
        # Remove special characters, replace spaces with underscores
        sanitized = re.sub(r'[^\w\s-]', '', title.lower())
        sanitized = re.sub(r'[-\s]+', '_', sanitized)
        return sanitized[:50]  # Limit length
    
    async def process(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Process game specification request."""
        # Create initial state
        initial_state = GameSpecState(
            user_description=inputs.get("description", ""),
            engine=inputs.get("engine", "pygame")
        )
        
        # Run the graph
        final_state = await self.graph.ainvoke(initial_state)
        
        return {
            "success": len(final_state.validation_errors) == 0,
            "spec": final_state.generated_spec,
            "errors": final_state.validation_errors
        }
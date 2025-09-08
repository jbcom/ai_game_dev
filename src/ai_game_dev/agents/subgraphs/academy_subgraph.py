"""
Arcade Academy Subgraph
Extends Game Workshop with educational features and teachable moments
"""
from typing import Any
from dataclasses import dataclass, field
import toml
from pathlib import Path

from .workshop_subgraph import GameWorkshopSubgraph, WorkshopState


@dataclass
class AcademyState(WorkshopState):
    """Extended state for educational features."""
    lesson_objectives: list[str] = field(default_factory=list)
    teachable_moments: list[dict[str, Any]] = field(default_factory=list)
    player_progress: dict[str, Any] = field(default_factory=dict)
    educational_mode: bool = True


class ArcadeAcademySubgraph(GameWorkshopSubgraph):
    """
    Educational game development subgraph.
    Inherits all workshop functionality and adds educational features.
    
    Additional capabilities:
    - Pre-configured with NeoTokyo Academy RPG spec
    - Teachable moment detection and insertion
    - Progress tracking and adaptive difficulty
    - Interactive code tutorials
    """
    
    def __init__(self):
        super().__init__()
        # Load the RPG spec from unified TOML on initialization
        self.rpg_spec = None
        self.current_lesson = None
        self.lesson_plans = self._load_lesson_plans()
    
    def _load_rpg_spec_from_unified(self) -> dict[str, Any]:
        """Load the RPG specification from the unified platform spec."""
        # Find workspace root
        current = Path.cwd()
        while current != current.parent:
            if (current / "pyproject.toml").exists():
                break
            current = current.parent
        
        # Load unified spec
        unified_spec_path = current / "src/ai_game_dev/specs/unified_platform_spec.toml"
        if unified_spec_path.exists():
            with open(unified_spec_path, 'r') as f:
                unified_spec = toml.load(f)
                rpg_spec = unified_spec.get("rpg_game", {})
                # Add required fields for compatibility
                rpg_spec["title"] = rpg_spec.get("name", "NeoTokyo Code Academy")
                rpg_spec["features"] = rpg_spec.get("features", {}).get("main", [])
                return rpg_spec
        else:
            # Fallback to a basic spec
            return {
                "name": "NeoTokyo Code Academy: The Binary Rebellion",
                "title": "NeoTokyo Code Academy",
                "description": "Educational RPG for learning programming",
                "engine": "pygame",
                "features": ["educational_rpg", "turn_based_combat", "skill_trees"],
                "paths": {
                    "assets_base": "public/static/assets/generated/academy",
                    "code_base": "generated_games/academy",
                    "use_relative_paths": True,
                    "project_name": "neotokyo_code_academy"
                }
            }
    
    def _load_lesson_plans(self) -> dict[str, Any]:
        """Load educational lesson plans."""
        return {
            "variables": {
                "title": "Variables and Data Types",
                "objectives": [
                    "Understand variable declaration",
                    "Learn about data types",
                    "Practice variable assignment"
                ],
                "code_concepts": ["int", "str", "float", "bool", "variable assignment"],
                "game_integration": "Player stats and inventory management"
            },
            "loops": {
                "title": "Loops and Iteration",
                "objectives": [
                    "Master for loops",
                    "Understand while loops",
                    "Apply loops in game logic"
                ],
                "code_concepts": ["for", "while", "range", "iteration", "break", "continue"],
                "game_integration": "Enemy spawn systems and animation cycles"
            },
            "conditionals": {
                "title": "Conditional Logic",
                "objectives": [
                    "Use if/elif/else statements",
                    "Understand boolean logic",
                    "Create decision trees"
                ],
                "code_concepts": ["if", "elif", "else", "and", "or", "not"],
                "game_integration": "Combat decisions and dialogue choices"
            },
            "functions": {
                "title": "Functions and Modularity",
                "objectives": [
                    "Define and call functions",
                    "Use parameters and returns",
                    "Understand scope"
                ],
                "code_concepts": ["def", "return", "parameters", "scope", "recursion"],
                "game_integration": "Spell system and ability mechanics"
            }
        }
    
    async def start_academy_mode(self) -> dict[str, Any]:
        """Initialize academy mode with the RPG game."""
        # Load RPG spec from unified TOML if not already loaded
        if self.rpg_spec is None:
            self.rpg_spec = self._load_rpg_spec_from_unified()
        
        # Use the loaded RPG spec
        result = await self.process({
            "uploaded_spec": self.rpg_spec,
            "educational_mode": True
        })
        
        # Add educational overlay
        if result["success"]:
            result["educational_content"] = {
                "available_lessons": list(self.lesson_plans.keys()),
                "current_progress": self._get_player_progress(),
                "next_lesson": self._get_next_lesson()
            }
        
        return result
    
    async def process_with_education(self, inputs: dict[str, Any]) -> dict[str, Any]:
        """Process with educational features enabled."""
        # First run standard workshop process
        result = await self.process(inputs)
        
        if result["success"] and inputs.get("educational_mode", True):
            # Inject teachable moments into the generated code
            result["project"] = self._inject_teachable_moments(
                result["project"],
                inputs.get("lesson_focus", "variables")
            )
            
            # Add educational metadata
            result["educational"] = {
                "teachable_moments": self._extract_teachable_moments(result["project"]),
                "exercises": self._generate_exercises(inputs.get("lesson_focus")),
                "hints": self._generate_hints(inputs.get("lesson_focus"))
            }
        
        return result
    
    def _inject_teachable_moments(self, project: dict[str, Any], lesson_focus: str) -> dict[str, Any]:
        """Inject educational comments and interactive tutorials into code."""
        lesson = self.lesson_plans.get(lesson_focus, self.lesson_plans["variables"])
        
        # Modify the generated code to include educational comments
        for filename, code in project.get("code", {}).items():
            if filename.endswith(".py"):
                # Add educational header
                educational_header = f'''"""
LESSON: {lesson['title']}
OBJECTIVES:
{chr(10).join(f"- {obj}" for obj in lesson['objectives'])}

Follow along with Professor Pixel as we explore these concepts!
"""

'''
                # Add inline educational comments
                modified_code = educational_header + self._add_inline_education(code, lesson)
                project["code"][filename] = modified_code
        
        return project
    
    def _add_inline_education(self, code: str, lesson: dict[str, Any]) -> str:
        """Add inline educational comments to code."""
        lines = code.split('\n')
        modified_lines = []
        
        for line in lines:
            # Add educational comments for specific concepts
            for concept in lesson["code_concepts"]:
                if concept in line and not line.strip().startswith("#"):
                    # Add explanatory comment
                    comment = self._get_concept_explanation(concept)
                    modified_lines.append(f"    # LEARN: {comment}")
            
            modified_lines.append(line)
        
        return '\n'.join(modified_lines)
    
    def _get_concept_explanation(self, concept: str) -> str:
        """Get educational explanation for a concept."""
        explanations = {
            "int": "Integer - whole numbers like health points or score",
            "str": "String - text data like character names or dialogue",
            "float": "Float - decimal numbers like position or speed",
            "bool": "Boolean - True/False values like is_alive or has_key",
            "for": "For loop - repeat code a specific number of times",
            "while": "While loop - repeat code while a condition is true",
            "if": "If statement - execute code only when condition is true",
            "def": "Function definition - create reusable code blocks",
            "return": "Return - send a value back from a function"
        }
        return explanations.get(concept, f"Concept: {concept}")
    
    def _extract_teachable_moments(self, project: dict[str, Any]) -> list[dict[str, Any]]:
        """Extract teachable moments from the generated project."""
        moments = []
        
        # Analyze code for teaching opportunities
        for filename, code in project.get("code", {}).items():
            if "player.py" in filename:
                moments.append({
                    "file": filename,
                    "line": 10,
                    "concept": "class_definition",
                    "explanation": "Classes let us create blueprints for game objects!"
                })
            
            if "combat.py" in filename:
                moments.append({
                    "file": filename,
                    "line": 25,
                    "concept": "conditional_logic",
                    "explanation": "Combat decisions use if/else to determine outcomes!"
                })
        
        return moments
    
    def _generate_exercises(self, lesson_focus: str) -> list[dict[str, Any]]:
        """Generate coding exercises for the lesson."""
        exercises = {
            "variables": [
                {
                    "title": "Create Player Stats",
                    "description": "Define variables for player health, mana, and level",
                    "starter_code": "# Create three variables for your player\n# health should be 100\n# mana should be 50\n# level should be 1\n",
                    "solution": "health = 100\nmana = 50\nlevel = 1",
                    "test": "assert health == 100 and mana == 50 and level == 1"
                }
            ],
            "loops": [
                {
                    "title": "Spawn Multiple Enemies",
                    "description": "Use a for loop to create 5 enemies",
                    "starter_code": "enemies = []\n# Use a for loop to add 5 enemies to the list\n",
                    "solution": "enemies = []\nfor i in range(5):\n    enemies.append(f'Enemy_{i}')",
                    "test": "assert len(enemies) == 5"
                }
            ]
        }
        
        return exercises.get(lesson_focus, [])
    
    def _generate_hints(self, lesson_focus: str) -> list[str]:
        """Generate hints for the current lesson."""
        hints = {
            "variables": [
                "Variables are like labeled boxes that store data",
                "Use descriptive names like 'player_health' not 'ph'",
                "Different data types serve different purposes"
            ],
            "loops": [
                "Loops help us avoid repeating code",
                "Use for loops when you know how many times to repeat",
                "Use while loops for conditions"
            ]
        }
        
        return hints.get(lesson_focus, [])
    
    def _get_player_progress(self) -> dict[str, Any]:
        """Get current player progress."""
        # This would connect to actual progress tracking
        return {
            "completed_lessons": ["variables"],
            "current_lesson": "loops",
            "total_xp": 150,
            "level": 2
        }
    
    def _get_next_lesson(self) -> str:
        """Determine the next lesson based on progress."""
        progress = self._get_player_progress()
        completed = progress["completed_lessons"]
        
        for lesson in ["variables", "loops", "conditionals", "functions"]:
            if lesson not in completed:
                return lesson
        
        return "advanced_topics"
"""
OpenAI structured tools for educational game development content.
Specialized tools for Arcade Academy mode.
"""
from typing import Any, Dict, List, Literal

from agents import function_tool

from ai_game_dev.templates import TemplateLoader
from .rpg_specification import get_rpg_specification
from .yarn_dialogue import YarnDialogueGenerator
from .characters_and_story import CharacterGenerator, StoryGenerator

# Initialize components
template_loader = TemplateLoader()
yarn_generator = YarnDialogueGenerator()
character_generator = CharacterGenerator()
story_generator = StoryGenerator()


@function_tool
async def create_lesson_plan(
    concept: str,
    student_level: Literal["beginner", "intermediate", "advanced"],
    game_project: str,
    duration_minutes: int = 45,
    include_solutions: bool = False
) -> str:
    """
    Create a complete lesson plan for teaching a programming concept through games.
    
    Args:
        concept: Programming concept to teach (e.g., "loops", "functions", "classes")
        student_level: Student's current skill level
        game_project: The game being built in this lesson
        duration_minutes: Lesson duration in minutes
        include_solutions: Whether to include challenge solutions
        
    Returns:
        Formatted lesson plan using the Academy template
    """
    # Define lesson structure based on level
    if student_level == "beginner":
        objectives = [
            f"Understand what {concept} are and why we use them",
            f"Write simple {concept} in their game",
            f"Debug common {concept} errors"
        ]
        challenges = [
            {
                "name": "First Steps",
                "difficulty": "Easy",
                "goal": f"Create a basic {concept}",
                "hint": "Start with the example and modify one thing",
                "solution": "# Solution code here"
            },
            {
                "name": "Level Up",
                "difficulty": "Medium", 
                "goal": f"Use {concept} to add a game feature",
                "hint": "Think about how this could make your game more fun",
                "solution": "# Solution code here"
            }
        ]
    else:
        objectives = [
            f"Master advanced {concept} techniques",
            f"Optimize {concept} for game performance",
            f"Create reusable {concept} patterns"
        ]
        challenges = [
            {
                "name": "Optimization Challenge",
                "difficulty": "Hard",
                "goal": f"Refactor {concept} for better performance",
                "hint": "Consider memory usage and execution speed",
                "solution": "# Advanced solution"
            }
        ]
    
    context = {
        "lesson_title": f"Mastering {concept.title()} in {game_project}",
        "student_level": student_level,
        "duration_minutes": duration_minutes,
        "game_project": game_project,
        "learning_objectives": objectives,
        "prerequisites": ["Previous lesson on variables"] if student_level == "beginner" else [],
        "hook_duration": 5,
        "concept_duration": 10,
        "coding_duration": 20,
        "challenge_duration": 10,
        "wrapup_duration": 5,
        "opening_hook": f"Today we'll unlock the power of {concept} to make your {game_project} amazing!",
        "concept_explanation": f"Let's explore how {concept} work in game development...",
        "language": "python",
        "starter_code": f"# Starter code for {concept}",
        "coding_steps": [
            {
                "description": f"First, let's create a simple {concept}",
                "code": f"# Code for step 1",
                "explanation": "This helps us understand the basics"
            }
        ],
        "challenges": challenges,
        "review_questions": [
            f"What problem do {concept} solve in games?",
            f"When would you use {concept} in your project?"
        ],
        "next_lesson_teaser": "Next time we'll combine this with animations!",
        "support_strategies": "Provide pre-written code snippets to modify",
        "extension_activities": f"Create multiple {concept} variations",
        "game_examples": [
            {"game": "Minecraft", "usage": f"Uses {concept} for crafting systems"},
            {"game": "Pokemon", "usage": f"Uses {concept} for battle mechanics"}
        ],
        "common_questions": [
            {
                "question": f"Why do {concept} seem complicated?",
                "answer": "They're new! With practice, they become second nature."
            }
        ],
        "include_solutions": include_solutions
    }
    
    return template_loader.render_academy_prompt("lesson_plan", **context)


@function_tool
async def identify_teachable_moment(
    code_snippet: str,
    student_level: Literal["beginner", "intermediate", "advanced"],
    language: str = "python",
    include_exercises: bool = True
) -> str:
    """
    Analyze code to identify teaching opportunities.
    
    Args:
        code_snippet: The code to analyze
        student_level: Student's current level
        language: Programming language
        include_exercises: Whether to generate practice exercises
        
    Returns:
        Teachable moment analysis with exercises
    """
    context = {
        "code_snippet": code_snippet,
        "student_level": student_level,
        "language": language,
        "include_exercises": include_exercises,
        "exercise_description": "Modify this code to add a new feature",
        "exercise_hint": "Think about what would make the game more fun",
        "expected_result": "The game should have the new feature working"
    }
    
    return template_loader.render_academy_prompt("teachable_moment", **context)


@function_tool
async def generate_educational_game_spec() -> Dict[str, Any]:
    """
    Generate the complete RPG specification for Arcade Academy.
    
    Returns:
        Complete game specification with educational metadata
    """
    return get_rpg_specification()


@function_tool
async def create_educational_dialogue(
    lesson_id: str,
    characters: list[str],
    concept_to_teach: str,
    include_choices: bool = True
) -> str:
    """
    Create educational dialogue for teaching programming concepts.
    
    Args:
        lesson_id: Unique lesson identifier
        characters: Characters in the dialogue (usually includes Professor Pixel)
        concept_to_teach: Programming concept being taught
        include_choices: Whether to include branching choices
        
    Returns:
        Yarnspinner-formatted educational dialogue
    """
    # Use the YarnDialogueGenerator for consistency
    dialogue_data = {
        "title": f"Lesson_{lesson_id}",
        "characters": characters,
        "concept": concept_to_teach,
        "educational": True,
        "include_choices": include_choices
    }
    
    return yarn_generator.generate_educational_dialogue(dialogue_data)


@function_tool
async def generate_academy_characters(
    include_students: bool = True,
    include_mentors: bool = True,
    skill_levels: list[str] | None = None
) -> List[Dict[str, Any]]:
    """
    Generate characters for the Arcade Academy setting.
    
    Args:
        include_students: Include student characters
        include_mentors: Include mentor characters
        skill_levels: Skill levels for student characters
        
    Returns:
        List of character profiles for the Academy
    """
    characters = []
    
    # Always include Professor Pixel
    characters.append({
        "name": "Professor Pixel",
        "role": "mentor",
        "description": "The wise and encouraging main teacher",
        "personality": ["patient", "enthusiastic", "knowledgeable"],
        "catchphrase": "Every bug is a learning opportunity!",
        "expertise": ["game development", "teaching", "debugging"]
    })
    
    if include_mentors:
        # Add specialized mentors
        mentor_specs = [
            ("Web Weaver", "web development", "HTML5 games"),
            ("Data Sage", "data structures", "game AI"),
            ("Code Knight", "algorithms", "optimization"),
            ("Bug Hunter", "debugging", "testing")
        ]
        
        for name, specialty, focus in mentor_specs:
            characters.append(character_generator.create_mentor(name, specialty, focus))
    
    if include_students:
        # Add diverse student characters
        student_levels = skill_levels or ["beginner", "intermediate"]
        for level in student_levels:
            characters.extend(character_generator.create_student_cohort(level, count=2))
    
    return characters


@function_tool
async def create_coding_challenge(
    concept: str,
    difficulty: Literal["easy", "medium", "hard"],
    game_context: str,
    provide_hints: bool = True
) -> Dict[str, Any]:
    """
    Create a coding challenge for students.
    
    Args:
        concept: Programming concept to practice
        difficulty: Challenge difficulty
        game_context: How this relates to their game project
        provide_hints: Whether to include hints
        
    Returns:
        Dictionary containing challenge details
    """
    challenge = {
        "concept": concept,
        "difficulty": difficulty,
        "title": f"{concept.title()} Challenge: {difficulty.title()}",
        "description": f"Use {concept} to enhance your {game_context}",
        "starter_code": generate_starter_code(concept, difficulty),
        "requirements": generate_requirements(concept, difficulty),
        "test_cases": generate_test_cases(concept, difficulty),
    }
    
    if provide_hints:
        challenge["hints"] = generate_progressive_hints(concept, difficulty)
        
    challenge["solution_explanation"] = f"This challenge teaches how {concept} can make games more interactive"
    
    return challenge


def generate_starter_code(concept: str, difficulty: str) -> str:
    """Generate appropriate starter code based on concept and difficulty."""
    templates = {
        "easy": "# TODO: Implement a simple {concept}\npass",
        "medium": "# TODO: Enhance this {concept}\nclass GameElement:\n    pass",
        "hard": "# TODO: Optimize this {concept} implementation\n# Current version works but is slow"
    }
    return templates.get(difficulty, "").format(concept=concept)


def generate_requirements(concept: str, difficulty: str) -> List[str]:
    """Generate challenge requirements."""
    base_reqs = [f"Must use {concept}", "Code must run without errors"]
    
    if difficulty == "medium":
        base_reqs.append("Include error handling")
    elif difficulty == "hard":
        base_reqs.extend(["Optimize for performance", "Add documentation"])
        
    return base_reqs


def generate_test_cases(concept: str, difficulty: str) -> List[Dict[str, Any]]:
    """Generate test cases for the challenge."""
    return [
        {
            "input": "test_input",
            "expected": "expected_output",
            "description": f"Basic {concept} functionality"
        }
    ]


def generate_progressive_hints(concept: str, difficulty: str) -> List[str]:
    """Generate hints that progressively reveal more information."""
    hints = [
        f"Think about what {concept} do in games you've played",
        f"Start by identifying where {concept} would be useful",
        f"Look at the example code from the lesson"
    ]
    
    if difficulty == "hard":
        hints.append("Consider using advanced patterns we discussed")
        
    return hints
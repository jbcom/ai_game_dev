"""
Quest Generation Subgraph
Proper LangGraph StateGraph workflow for quest design and progression systems
"""

from typing_extensions import TypedDict
from typing import Dict, Any, List
from langchain_core.messages import HumanMessage
from langchain_anthropic import ChatAnthropic
from langgraph.graph import StateGraph, START, END


# State definition following LangGraph patterns
class QuestState(TypedDict):
    game_spec: Dict[str, Any]
    quest_categories: List[str]
    main_quests: List[Dict[str, Any]]
    side_quests: List[Dict[str, Any]]
    tutorial_quests: List[Dict[str, Any]]
    progression_system: Dict[str, Any]
    final_output: Dict[str, Any]


def analyze_quest_requirements(state: QuestState) -> QuestState:
    """Analyze game specification to determine quest requirements."""
    
    game_spec = state.get('game_spec', {})
    complexity = game_spec.get('complexity', 'intermediate')
    genre = game_spec.get('genre', 'adventure')
    features = game_spec.get('features', [])
    
    # Determine quest categories based on game spec
    quest_categories = ["main_story", "side_content", "tutorial"]
    
    if complexity == "complex":
        quest_categories.extend(["achievements", "daily_challenges"])
    
    if "rpg" in genre.lower() or "progression" in features:
        quest_categories.append("character_development")
    
    if "multiplayer" in features:
        quest_categories.append("cooperative_quests")
    
    return {"quest_categories": quest_categories}


def generate_main_questline(state: QuestState) -> QuestState:
    """Generate main story questline with proper progression."""
    
    # Initialize LLM
    llm = ChatAnthropic(model="claude-3-5-sonnet-latest")
    
    game_spec = state.get('game_spec', {})
    complexity = game_spec.get('complexity', 'intermediate')
    
    # Determine number of main quests based on complexity
    quest_count = {"simple": 3, "intermediate": 5, "complex": 7}.get(complexity, 5)
    
    main_quest_prompt = f"""Design {quest_count} main story quests for the game: {game_spec.get('title', 'Game')}

Game Details:
- Genre: {game_spec.get('genre', 'Unknown')}
- Description: {game_spec.get('description', 'A game')}
- Complexity: {complexity}
- Features: {', '.join(game_spec.get('features', []))}

For each quest, provide:
1. Quest Title
2. Objective Description
3. Prerequisites (if any)
4. Rewards (XP, items, progression)
5. Estimated completion time
6. Narrative importance

Create a coherent storyline that progresses from beginning to end.
Format as JSON array with quest objects."""

    try:
        response = llm.invoke([HumanMessage(content=main_quest_prompt)])
        # For demo purposes, create structured quest data
        main_quests = [
            {
                "title": f"Main Quest {i+1}",
                "description": f"Part {i+1} of the main storyline",
                "objectives": [f"Complete objective {i+1}"],
                "prerequisites": [] if i == 0 else [f"Main Quest {i}"],
                "rewards": {"xp": 100 * (i+1), "items": []},
                "estimated_time": f"{15 + i*10} minutes"
            }
            for i in range(quest_count)
        ]
    except Exception as e:
        main_quests = [{"error": f"Failed to generate main quests: {str(e)}"}]
    
    return {"main_quests": main_quests}


def generate_side_content(state: QuestState) -> QuestState:
    """Generate side quests and optional content."""
    
    # Initialize LLM
    llm = ChatAnthropic(model="claude-3-5-sonnet-latest")
    
    game_spec = state.get('game_spec', {})
    
    side_quest_prompt = f"""Design 5-8 side quests for the game: {game_spec.get('title', 'Game')}

Game Genre: {game_spec.get('genre', 'Unknown')}
Game Features: {', '.join(game_spec.get('features', []))}

Create diverse side quests including:
1. Exploration challenges
2. Collection tasks
3. Character interaction quests
4. Skill-based challenges
5. Optional boss encounters

Each quest should:
- Be completable independently
- Offer meaningful rewards
- Add to world-building
- Provide gameplay variety

Format as JSON array with quest details."""

    try:
        response = llm.invoke([HumanMessage(content=side_quest_prompt)])
        # For demo purposes, create structured side quest data
        side_quests = [
            {
                "title": f"Side Quest: {category}",
                "category": category,
                "description": f"Optional {category.lower()} quest",
                "objectives": [f"Complete {category.lower()} task"],
                "rewards": {"xp": 50, "items": [f"{category} reward"]},
                "optional": True
            }
            for category in ["Exploration", "Collection", "Combat", "Puzzle", "Social"]
        ]
    except Exception as e:
        side_quests = [{"error": f"Failed to generate side quests: {str(e)}"}]
    
    return {"side_quests": side_quests}


def generate_tutorial_system(state: QuestState) -> QuestState:
    """Generate tutorial quests for onboarding players."""
    
    # Initialize LLM
    llm = ChatAnthropic(model="claude-3-5-sonnet-latest")
    
    game_spec = state.get('game_spec', {})
    
    tutorial_prompt = f"""Design tutorial quests for the game: {game_spec.get('title', 'Game')}

Game Genre: {game_spec.get('genre', 'Unknown')}
Key Features: {', '.join(game_spec.get('features', []))}

Create 3-5 tutorial quests that teach:
1. Basic movement and controls
2. Core game mechanics
3. UI interaction
4. First challenge/goal
5. Progression systems

Each tutorial quest should:
- Introduce one concept at a time
- Provide clear guidance
- Give immediate feedback
- Build confidence
- Connect to main gameplay

Format with step-by-step instructions."""

    try:
        response = llm.invoke([HumanMessage(content=tutorial_prompt)])
        # For demo purposes, create structured tutorial data
        tutorial_quests = [
            {
                "title": "Getting Started",
                "type": "movement_tutorial",
                "instructions": ["Learn basic movement", "Practice controls"],
                "completion_criteria": ["Move in all directions", "Interact with object"]
            },
            {
                "title": "First Challenge", 
                "type": "gameplay_tutorial",
                "instructions": ["Use main game mechanic", "Complete simple task"],
                "completion_criteria": ["Successfully use mechanic", "Achieve goal"]
            },
            {
                "title": "Understanding Progress",
                "type": "progression_tutorial", 
                "instructions": ["View progress screen", "Understand rewards"],
                "completion_criteria": ["Open progress menu", "Collect first reward"]
            }
        ]
    except Exception as e:
        tutorial_quests = [{"error": f"Failed to generate tutorials: {str(e)}"}]
    
    return {"tutorial_quests": tutorial_quests}


def design_progression_system(state: QuestState) -> QuestState:
    """Design the overall quest progression and reward system."""
    
    game_spec = state.get('game_spec', {})
    main_quests = state.get('main_quests', [])
    side_quests = state.get('side_quests', [])
    
    progression_system = {
        "level_system": {
            "max_level": len(main_quests) * 2,
            "xp_per_level": 200,
            "level_rewards": ["New abilities", "Stat increases", "Equipment unlocks"]
        },
        "achievement_system": {
            "story_achievements": len(main_quests),
            "exploration_achievements": len(side_quests),
            "special_achievements": 5
        },
        "unlock_system": {
            "linear_progression": True,
            "optional_branches": len(side_quests) > 3,
            "secret_content": game_spec.get('complexity') == 'complex'
        }
    }
    
    return {"progression_system": progression_system}


def compile_quest_output(state: QuestState) -> QuestState:
    """Compile final quest system output."""
    
    main_quests = state.get('main_quests', [])
    side_quests = state.get('side_quests', [])
    tutorial_quests = state.get('tutorial_quests', [])
    progression_system = state.get('progression_system', {})
    game_spec = state.get('game_spec', {})
    
    final_output = {
        "success": len(main_quests) > 0,
        "quest_content": {
            "main_quests": main_quests,
            "side_quests": side_quests,
            "tutorial_quests": tutorial_quests,
            "progression_system": progression_system
        },
        "total_quests": len(main_quests) + len(side_quests) + len(tutorial_quests),
        "type": "quest_generation",
        "game_title": game_spec.get('title', 'Game')
    }
    
    return {"final_output": final_output}


# Build the quest workflow using proper LangGraph StateGraph with prompt chaining
def create_quest_workflow():
    """Create quest generation workflow following LangGraph prompt chaining pattern."""
    
    workflow = StateGraph(QuestState)
    
    # Add nodes following LangGraph patterns
    workflow.add_node("analyze_requirements", analyze_quest_requirements)
    workflow.add_node("generate_main_quests", generate_main_questline)
    workflow.add_node("generate_side_quests", generate_side_content)
    workflow.add_node("generate_tutorials", generate_tutorial_system)
    workflow.add_node("design_progression", design_progression_system)
    workflow.add_node("compile_output", compile_quest_output)
    
    # Add edges using prompt chaining pattern - sequential quest generation
    workflow.add_edge(START, "analyze_requirements")
    workflow.add_edge("analyze_requirements", "generate_main_quests")
    workflow.add_edge("generate_main_quests", "generate_side_quests")
    workflow.add_edge("generate_side_quests", "generate_tutorials")
    workflow.add_edge("generate_tutorials", "design_progression")
    workflow.add_edge("design_progression", "compile_output")
    workflow.add_edge("compile_output", END)
    
    return workflow.compile()


# Create the compiled workflow
quest_workflow = create_quest_workflow()


class QuestSubgraph:
    """Wrapper class for the quest workflow."""
    
    def __init__(self):
        self.workflow = quest_workflow
    
    async def initialize(self):
        """Initialize the quest subgraph."""
        pass  # No async initialization needed
    
    async def generate_quests(self, game_spec: Dict[str, Any]) -> Dict[str, Any]:
        """Generate quests using the LangGraph workflow."""
        
        try:
            # Run the workflow with game spec
            result = self.workflow.invoke({"game_spec": game_spec})
            return result.get("final_output", {
                "success": False,
                "error": "No final output generated",
                "type": "quest_generation"
            })
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "type": "quest_generation"
            }
"""
Dialogue Generation Subgraph
Proper LangGraph StateGraph workflow for dialogue and narrative generation
"""

from typing_extensions import TypedDict
from typing import Dict, Any, List
from langchain_core.messages import HumanMessage
from langchain_anthropic import ChatAnthropic
from langgraph.graph import StateGraph, START, END
import os


# State definition following LangGraph patterns
class DialogueState(TypedDict):
    game_spec: Dict[str, Any]
    character_profiles: List[Dict[str, str]]
    dialogue_categories: List[str]
    generated_dialogue: Dict[str, Any]
    final_output: Dict[str, Any]


def analyze_dialogue_needs(state: DialogueState) -> DialogueState:
    """Analyze game spec to determine dialogue generation needs."""
    
    game_spec = state.get('game_spec', {})
    genre = game_spec.get('genre', 'Unknown')
    features = game_spec.get('features', [])
    
    # Determine character profiles needed
    character_profiles = [
        {"name": "Player Character", "role": "protagonist"},
        {"name": "Tutorial Guide", "role": "mentor"},
        {"name": "Shopkeeper", "role": "vendor"}
    ]
    
    # Add genre-specific characters
    if genre.lower() in ['rpg', 'adventure']:
        character_profiles.extend([
            {"name": "Quest Giver", "role": "npc"},
            {"name": "Companion", "role": "ally"}
        ])
    
    # Determine dialogue categories
    dialogue_categories = [
        "character_dialogue",
        "narrative_text", 
        "tutorial_instructions",
        "menu_text",
        "ui_messages"
    ]
    
    if "multiplayer" in features:
        dialogue_categories.append("multiplayer_chat")
    
    return {
        "character_profiles": character_profiles,
        "dialogue_categories": dialogue_categories
    }


def generate_character_dialogue(state: DialogueState) -> DialogueState:
    """Generate character-specific dialogue content."""
    
    # Initialize LLM
    llm = ChatAnthropic(model="claude-3-5-sonnet-latest")
    
    game_spec = state.get('game_spec', {})
    character_profiles = state.get('character_profiles', [])
    
    character_dialogue = {}
    
    for character in character_profiles:
        dialogue_prompt = f"""Generate dialogue for {character['name']} in the game: {game_spec.get('title', 'Game')}

Character Role: {character['role']}
Game Genre: {game_spec.get('genre', 'Unknown')}
Game Style: {game_spec.get('art_style', 'Modern')}

Generate 5-10 dialogue lines that this character would say, including:
- Introduction lines
- Interaction responses  
- Situational comments
- Emotional reactions

Make the dialogue match the game's tone and the character's role."""

        try:
            response = llm.invoke([HumanMessage(content=dialogue_prompt)])
            character_dialogue[character['name']] = response.content
        except Exception as e:
            character_dialogue[character['name']] = f"Error generating dialogue: {str(e)}"
    
    generated_dialogue = state.get('generated_dialogue', {})
    generated_dialogue['character_dialogue'] = character_dialogue
    
    return {"generated_dialogue": generated_dialogue}


def generate_narrative_content(state: DialogueState) -> DialogueState:
    """Generate narrative text and story content."""
    
    # Initialize LLM
    llm = ChatAnthropic(model="claude-3-5-sonnet-latest")
    
    game_spec = state.get('game_spec', {})
    
    narrative_prompt = f"""Generate narrative content for the game: {game_spec.get('title', 'Game')}

Game Details:
- Genre: {game_spec.get('genre', 'Unknown')}
- Description: {game_spec.get('description', 'A game')}
- Features: {', '.join(game_spec.get('features', []))}

Generate:
1. Opening story/introduction
2. Chapter/level transitions
3. Victory/completion text
4. Game over messages
5. Lore and background text

Format as clear sections with descriptive headers."""

    try:
        response = llm.invoke([HumanMessage(content=narrative_prompt)])
        narrative_content = response.content
    except Exception as e:
        narrative_content = f"Error generating narrative: {str(e)}"
    
    generated_dialogue = state.get('generated_dialogue', {})
    generated_dialogue['narrative_text'] = narrative_content
    
    return {"generated_dialogue": generated_dialogue}


def generate_ui_text(state: DialogueState) -> DialogueState:
    """Generate UI text and system messages."""
    
    # Initialize LLM  
    llm = ChatAnthropic(model="claude-3-5-sonnet-latest")
    
    game_spec = state.get('game_spec', {})
    
    ui_prompt = f"""Generate UI text and system messages for the game: {game_spec.get('title', 'Game')}

Generate concise, clear text for:
1. Menu options (Start Game, Settings, Quit, etc.)
2. Tutorial instructions
3. System notifications
4. Error messages
5. Loading screens
6. Achievement notifications
7. Settings labels

Keep text brief and user-friendly. Match the game's tone: {game_spec.get('art_style', 'modern')}."""

    try:
        response = llm.invoke([HumanMessage(content=ui_prompt)])
        ui_text = response.content
    except Exception as e:
        ui_text = f"Error generating UI text: {str(e)}"
    
    generated_dialogue = state.get('generated_dialogue', {})
    generated_dialogue['ui_messages'] = ui_text
    
    return {"generated_dialogue": generated_dialogue}


def compile_dialogue_output(state: DialogueState) -> DialogueState:
    """Compile final dialogue output."""
    
    generated_dialogue = state.get('generated_dialogue', {})
    game_spec = state.get('game_spec', {})
    
    final_output = {
        "success": len(generated_dialogue) > 0,
        "dialogue_content": generated_dialogue,
        "categories_generated": list(generated_dialogue.keys()),
        "type": "dialogue_generation",
        "game_title": game_spec.get('title', 'Game')
    }
    
    return {"final_output": final_output}


# Build the dialogue workflow using proper LangGraph StateGraph
def create_dialogue_workflow():
    """Create dialogue generation workflow following LangGraph patterns."""
    
    workflow = StateGraph(DialogueState)
    
    # Add nodes following LangGraph patterns
    workflow.add_node("analyze_needs", analyze_dialogue_needs)
    workflow.add_node("generate_characters", generate_character_dialogue)
    workflow.add_node("generate_narrative", generate_narrative_content)
    workflow.add_node("generate_ui", generate_ui_text)
    workflow.add_node("compile_output", compile_dialogue_output)
    
    # Add edges - using parallelization pattern for generation steps
    workflow.add_edge(START, "analyze_needs")
    workflow.add_edge("analyze_needs", "generate_characters")
    workflow.add_edge("analyze_needs", "generate_narrative") 
    workflow.add_edge("analyze_needs", "generate_ui")
    workflow.add_edge("generate_characters", "compile_output")
    workflow.add_edge("generate_narrative", "compile_output")
    workflow.add_edge("generate_ui", "compile_output")
    workflow.add_edge("compile_output", END)
    
    return workflow.compile()


# Create the compiled workflow
dialogue_workflow = create_dialogue_workflow()


class DialogueSubgraph:
    """Wrapper class for the dialogue workflow."""
    
    def __init__(self):
        self.workflow = dialogue_workflow
    
    async def initialize(self):
        """Initialize the dialogue subgraph."""
        pass  # No async initialization needed
    
    async def generate_dialogue(self, game_spec: Dict[str, Any]) -> Dict[str, Any]:
        """Generate dialogue using the LangGraph workflow."""
        
        try:
            # Run the workflow with game spec
            result = self.workflow.invoke({"game_spec": game_spec})
            return result.get("final_output", {
                "success": False,
                "error": "No final output generated",
                "type": "dialogue_generation"
            })
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "type": "dialogue_generation"
            }
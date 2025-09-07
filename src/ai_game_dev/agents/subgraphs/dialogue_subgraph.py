"""
Dialogue Generation Subgraph
Handles all dialogue, narrative text, and character conversations
"""

import asyncio
from typing import Dict, Any
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, START, END

from ai_game_dev.agents.base_agent import BaseAgent, AgentState, AgentConfig


class DialogueSubgraph(BaseAgent):
    """Specialized subgraph for generating game dialogue and narrative content."""
    
    def __init__(self):
        config = AgentConfig(
            model="gpt-4o",
            temperature=0.7,  # Higher creativity for dialogue
            instructions=self._get_dialogue_instructions()
        )
        super().__init__(config)
    
    def _get_dialogue_instructions(self) -> str:
        return """
        You are a specialized dialogue generation agent for game development.
        
        Your expertise includes:
        - Character dialogue and conversations
        - Narrative text and storytelling
        - Tutorial instructions and guides
        - Menu text and UI messages
        - Character voice and personality consistency
        
        Always generate engaging, context-appropriate dialogue that:
        - Matches the game's tone and setting
        - Maintains character consistency
        - Advances the narrative or gameplay
        - Is appropriate for the target audience
        """
    
    async def generate_dialogue(self, game_spec: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive dialogue content for a game."""
        
        try:
            dialogue_prompt = f"""Generate dialogue for the game: {game_spec.get('title', 'Game')}
            
            Game Details:
            - Genre: {game_spec.get('genre', 'Unknown')}
            - Art Style: {game_spec.get('art_style', 'Modern')}
            - Features: {', '.join(game_spec.get('features', []))}
            - Target Audience: {game_spec.get('target_audience', 'General')}
            
            Generate comprehensive dialogue including:
            1. Main character dialogue lines
            2. NPC conversations
            3. Narrative text and cutscenes
            4. Tutorial instructions
            5. Menu text and UI messages
            6. System messages and feedback
            
            Format as JSON with clear categories and content."""
            
            response = await self.llm.ainvoke([HumanMessage(content=dialogue_prompt)])
            
            return {
                "success": True,
                "dialogue_content": response.content,
                "type": "dialogue_generation",
                "game_title": game_spec.get('title', 'Game')
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "type": "dialogue_generation"
            }
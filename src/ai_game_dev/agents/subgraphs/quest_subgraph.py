"""
Quest Generation Subgraph
Handles quest design, objectives, progression, and rewards
"""

import asyncio
from typing import Dict, Any
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, START, END

from ai_game_dev.agents.base_agent import BaseAgent, AgentState, AgentConfig


class QuestSubgraph(BaseAgent):
    """Specialized subgraph for generating game quests and objectives."""
    
    def __init__(self):
        config = AgentConfig(
            model="gpt-4o",
            temperature=0.5,  # Balanced creativity for quest design
            instructions=self._get_quest_instructions()
        )
        super().__init__(config)
    
    def _get_quest_instructions(self) -> str:
        return """
        You are a specialized quest generation agent for game development.
        
        Your expertise includes:
        - Main storyline quest design
        - Side quest creation
        - Tutorial quest progression
        - Achievement and objective systems
        - Quest rewards and progression mechanics
        
        Always generate well-structured quests that:
        - Have clear objectives and outcomes
        - Provide appropriate difficulty progression
        - Offer meaningful rewards
        - Integrate with the game's narrative
        - Are engaging and fun to complete
        """
    
    async def generate_quests(self, game_spec: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive quest content for a game."""
        
        try:
            quest_prompt = f"""Generate quests for the game: {game_spec.get('title', 'Game')}
            
            Game Details:
            - Genre: {game_spec.get('genre', 'Unknown')}
            - Complexity: {game_spec.get('complexity', 'Intermediate')}
            - Features: {', '.join(game_spec.get('features', []))}
            - Target Audience: {game_spec.get('target_audience', 'General')}
            
            Generate comprehensive quest system including:
            1. Main storyline quests (3-5 major quests)
            2. Side quests (5-10 optional quests)
            3. Tutorial quests (for onboarding)
            4. Achievement objectives
            5. Quest rewards and progression systems
            6. Quest chains and dependencies
            
            For each quest, include:
            - Title and description
            - Objectives and requirements
            - Rewards (XP, items, progression)
            - Prerequisites and dependencies
            - Estimated completion time
            
            Format as JSON with clear quest structures."""
            
            response = await self.llm.ainvoke([HumanMessage(content=quest_prompt)])
            
            return {
                "success": True,
                "quest_content": response.content,
                "type": "quest_generation",
                "game_title": game_spec.get('title', 'Game')
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "type": "quest_generation"
            }
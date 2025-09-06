"""
Unified audio tools integrating TTS, music generation, and sound effects.
Provides LangGraph structured tools for complete audio workflow.
"""
from typing import Any
from dataclasses import dataclass

from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field

from ai_game_dev.assets.ai_game_assets.audio.tts_generator import TTSGenerator
from ai_game_dev.assets.ai_game_assets.audio.music_generator import MusicGenerator
from ai_game_dev.assets.ai_game_assets.audio.freesound_client import FreesoundClient


class AudioWorkflowRequest(BaseModel):
    """Request for complete audio workflow."""
    game_description: str = Field(description="Description of the game")
    audio_needs: list[str] = Field(description="List of audio needs (dialogue, music, sfx)")
    style_preferences: str = Field(default="", description="Audio style preferences")
    target_duration: int = Field(default=120, description="Target duration for music in seconds")


@dataclass
class AudioWorkflowResult:
    """Result of complete audio workflow."""
    dialogue_audio: dict[str, Any]
    background_music: dict[str, Any]
    sound_effects: list[dict[str, Any]]
    audio_pack_summary: str


class AudioTools:
    """Unified audio tools for complete game audio generation."""
    
    def __init__(self, openai_api_key: str | None = None, freesound_api_key: str | None = None):
        self.tts_generator = TTSGenerator(api_key=openai_api_key)
        self.music_generator = MusicGenerator()
        self.freesound_client = FreesoundClient(api_key=freesound_api_key) if freesound_api_key else None
    
    async def generate_complete_audio_pack(
        self,
        game_description: str,
        audio_needs: list[str],
        style_preferences: str = "",
        target_duration: int = 120
    ) -> AudioWorkflowResult:
        """Generate a complete audio pack for a game."""
        
        # Analyze game description for audio context
        audio_context = self._analyze_audio_context(game_description, style_preferences)
        
        # Generate dialogue if needed
        dialogue_audio = {}
        if "dialogue" in audio_needs or "narration" in audio_needs:
            dialogue_audio = await self._generate_dialogue_pack(game_description, audio_context)
        
        # Generate background music
        background_music = {}
        if "music" in audio_needs or "background" in audio_needs:
            background_music = await self._generate_music_pack(
                game_description, audio_context, target_duration
            )
        
        # Generate sound effects
        sound_effects = []
        if "sfx" in audio_needs or "effects" in audio_needs:
            sound_effects = await self._generate_sfx_pack(game_description, audio_context)
        
        # Create summary
        summary = self._create_audio_summary(dialogue_audio, background_music, sound_effects)
        
        return AudioWorkflowResult(
            dialogue_audio=dialogue_audio,
            background_music=background_music,
            sound_effects=sound_effects,
            audio_pack_summary=summary
        )
    
    def _analyze_audio_context(self, game_description: str, style_preferences: str) -> dict[str, Any]:
        """Analyze game description to determine audio context."""
        
        desc_lower = game_description.lower()
        style_lower = style_preferences.lower()
        
        # Determine game genre
        genre = "modern"
        if any(word in desc_lower for word in ["fantasy", "magic", "medieval", "dragon"]):
            genre = "fantasy"
        elif any(word in desc_lower for word in ["sci-fi", "space", "robot", "cyber", "future"]):
            genre = "sci-fi"
        elif any(word in desc_lower for word in ["horror", "scary", "dark", "zombie"]):
            genre = "horror"
        elif any(word in desc_lower for word in ["retro", "pixel", "8bit", "arcade"]):
            genre = "retro"
        
        # Determine mood
        mood = "peaceful"
        if any(word in desc_lower for word in ["action", "battle", "fight", "combat"]):
            mood = "intense"
        elif any(word in desc_lower for word in ["adventure", "hero", "quest"]):
            mood = "heroic"
        elif any(word in desc_lower for word in ["mystery", "puzzle", "hidden"]):
            mood = "mysterious"
        elif any(word in desc_lower for word in ["victory", "win", "success"]):
            mood = "victorious"
        
        # Determine game context
        context = "gameplay"
        if any(word in desc_lower for word in ["menu", "ui", "interface"]):
            context = "menu"
        elif any(word in desc_lower for word in ["battle", "combat", "fight"]):
            context = "battle"
        elif any(word in desc_lower for word in ["explore", "world", "environment"]):
            context = "exploration"
        
        return {
            "genre": genre,
            "mood": mood,
            "context": context,
            "style_preferences": style_preferences
        }
    
    async def _generate_dialogue_pack(
        self,
        game_description: str,
        audio_context: dict[str, Any]
    ) -> dict[str, Any]:
        """Generate dialogue and narration audio."""
        
        # Generate sample dialogue based on game type
        dialogue_lines = self._create_sample_dialogue(game_description, audio_context)
        
        # Generate TTS for dialogue
        tts_results = await self.tts_generator.generate_dialogue_set(dialogue_lines)
        
        # Generate narration
        narration_text = f"Welcome to {game_description.split('.')[0]}. Your adventure begins now."
        narration_result = await self.tts_generator.generate_narration(narration_text)
        
        return {
            "dialogue": [
                {
                    "character": result.character_context,
                    "text": result.text,
                    "audio_path": result.audio_path,
                    "voice": result.voice
                } for result in tts_results
            ],
            "narration": {
                "text": narration_result.text,
                "audio_path": narration_result.audio_path,
                "voice": narration_result.voice
            }
        }
    
    def _create_sample_dialogue(
        self,
        game_description: str,
        audio_context: dict[str, Any]
    ) -> list[dict[str, str]]:
        """Create sample dialogue based on game context."""
        
        genre = audio_context["genre"]
        
        # Base dialogue templates by genre
        dialogue_templates = {
            "fantasy": [
                {"character": "hero", "text": "I must find the ancient artifact before it's too late!"},
                {"character": "wizard", "text": "Beware, young adventurer. Dark magic lies ahead."},
                {"character": "villain", "text": "You cannot stop the rising darkness!"}
            ],
            "sci-fi": [
                {"character": "pilot", "text": "Incoming transmission from the mothership."},
                {"character": "ai", "text": "Warning: hull breach detected in sector 7."},
                {"character": "alien", "text": "Your species is not welcome here."}
            ],
            "modern": [
                {"character": "player", "text": "I need to find a way out of here."},
                {"character": "guide", "text": "Follow the markers to reach the exit."},
                {"character": "antagonist", "text": "You're making a big mistake."}
            ],
            "retro": [
                {"character": "player", "text": "Game start!"},
                {"character": "announcer", "text": "Level complete! Bonus points awarded."},
                {"character": "enemy", "text": "You cannot defeat me!"}
            ]
        }
        
        return dialogue_templates.get(genre, dialogue_templates["modern"])
    
    async def _generate_music_pack(
        self,
        game_description: str,
        audio_context: dict[str, Any],
        target_duration: int
    ) -> dict[str, Any]:
        """Generate background music pack."""
        
        mood = audio_context["mood"]
        context = audio_context["context"]
        
        # Generate main theme
        main_theme = await self.music_generator.generate_music(
            mood=mood,
            context=context,
            duration_seconds=target_duration,
            loop_compatible=True
        )
        
        # Generate additional tracks for different contexts
        menu_music = await self.music_generator.generate_music(
            mood="peaceful",
            context="menu",
            duration_seconds=60,
            loop_compatible=True
        )
        
        return {
            "main_theme": {
                "midi_path": main_theme.midi_path,
                "mood": main_theme.mood,
                "context": main_theme.context,
                "duration_seconds": main_theme.duration_seconds,
                "tempo_bpm": main_theme.tempo_bpm
            },
            "menu_music": {
                "midi_path": menu_music.midi_path,
                "mood": menu_music.mood,
                "context": menu_music.context,
                "duration_seconds": menu_music.duration_seconds,
                "tempo_bpm": menu_music.tempo_bpm
            }
        }
    
    async def _generate_sfx_pack(
        self,
        game_description: str,
        audio_context: dict[str, Any]
    ) -> list[dict[str, Any]]:
        """Generate sound effects pack."""
        
        genre = audio_context["genre"]
        
        # Determine needed sound effects based on game description
        sfx_needs = self._analyze_sfx_needs(game_description, genre)
        
        sound_effects = []
        
        # If Freesound client is available, search for effects
        if self.freesound_client:
            for sfx_type in sfx_needs:
                try:
                    sounds = await self.freesound_client.search_game_sounds(
                        sound_type=sfx_type,
                        game_genre=genre,
                        max_results=3
                    )
                    
                    for sound in sounds:
                        sound_effects.append({
                            "type": sfx_type,
                            "name": sound.name,
                            "description": sound.description,
                            "download_url": sound.download_url,
                            "preview_url": sound.preview_url,
                            "license": sound.license,
                            "duration": sound.duration
                        })
                except Exception as e:
                    print(f"Error searching for {sfx_type}: {e}")
        
        # If no Freesound client or no results, provide placeholders
        if not sound_effects:
            for sfx_type in sfx_needs:
                sound_effects.append({
                    "type": sfx_type,
                    "name": f"{sfx_type.title()} Sound",
                    "description": f"Placeholder for {sfx_type} sound effect",
                    "download_url": None,
                    "preview_url": None,
                    "license": "CC0",
                    "duration": 1.0
                })
        
        return sound_effects
    
    def _analyze_sfx_needs(self, game_description: str, genre: str) -> list[str]:
        """Analyze game description to determine needed sound effects."""
        
        desc_lower = game_description.lower()
        base_sfx = ["button", "coin", "jump"]
        
        # Add genre-specific effects
        if genre == "fantasy":
            base_sfx.extend(["sword", "magic", "footstep"])
        elif genre == "sci-fi":
            base_sfx.extend(["laser", "engine", "ambient"])
        elif genre == "retro":
            base_sfx.extend(["powerup", "explosion", "victory"])
        
        # Add context-specific effects based on description
        if any(word in desc_lower for word in ["battle", "fight", "combat"]):
            base_sfx.extend(["explosion", "hurt"])
        
        if any(word in desc_lower for word in ["explore", "adventure"]):
            base_sfx.extend(["footstep", "ambient"])
        
        if any(word in desc_lower for word in ["door", "open", "enter"]):
            base_sfx.append("door")
        
        return list(set(base_sfx))  # Remove duplicates
    
    def _create_audio_summary(
        self,
        dialogue_audio: dict[str, Any],
        background_music: dict[str, Any],
        sound_effects: list[dict[str, Any]]
    ) -> str:
        """Create a summary of the generated audio pack."""
        
        summary_parts = []
        
        if dialogue_audio:
            dialogue_count = len(dialogue_audio.get("dialogue", []))
            narration_count = 1 if dialogue_audio.get("narration") else 0
            summary_parts.append(f"Generated {dialogue_count} dialogue lines and {narration_count} narration")
        
        if background_music:
            music_count = len([k for k in background_music.keys() if k.endswith("music") or k.endswith("theme")])
            summary_parts.append(f"Created {music_count} background music tracks")
        
        if sound_effects:
            sfx_count = len(sound_effects)
            summary_parts.append(f"Found {sfx_count} sound effects")
        
        return "Audio pack includes: " + ", ".join(summary_parts) + "."
    
    def create_langraph_tool(self) -> StructuredTool:
        """Create a unified LangGraph tool for complete audio workflow."""
        
        async def _generate_audio_workflow(
            game_description: str,
            audio_needs: list[str],
            style_preferences: str = "",
            target_duration: int = 120
        ) -> dict[str, Any]:
            """Generate complete audio pack for game development."""
            
            result = await self.generate_complete_audio_pack(
                game_description=game_description,
                audio_needs=audio_needs,
                style_preferences=style_preferences,
                target_duration=target_duration
            )
            
            return {
                "dialogue_audio": result.dialogue_audio,
                "background_music": result.background_music,
                "sound_effects": result.sound_effects,
                "summary": result.audio_pack_summary,
                "total_assets": (
                    len(result.dialogue_audio.get("dialogue", [])) +
                    len(result.background_music) +
                    len(result.sound_effects)
                )
            }
        
        return StructuredTool.from_function(
            func=_generate_audio_workflow,
            name="generate_complete_audio",
            description=(
                "Generate a complete audio pack for game development including "
                "TTS dialogue, procedural background music, and curated sound effects. "
                "Provides end-to-end audio production workflow with context-aware generation."
            ),
            args_schema=AudioWorkflowRequest
        )
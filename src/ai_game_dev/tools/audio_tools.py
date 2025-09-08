"""
Audio generation tools for game development.
Provides structured tools for sound effects, music, and TTS.
"""
from pathlib import Path
from typing import Literal

from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field

from ai_game_dev.tools.audio.freesound_client import FreesoundClient
from ai_game_dev.tools.audio.music_generator import MusicGenerator
from ai_game_dev.tools.audio.tts_generator import TTSGenerator


class AudioGenerationInput(BaseModel):
    """Input for audio generation."""
    audio_type: Literal["sound_effect", "music", "voice"] = Field(
        description="Type of audio to generate"
    )
    description: str = Field(
        description="Description of the audio to generate"
    )
    duration: float = Field(
        default=1.0,
        description="Duration in seconds"
    )
    output_path: str = Field(
        description="Path to save the audio file"
    )
    # Music-specific
    genre: str | None = Field(
        default=None,
        description="Music genre (for music generation)"
    )
    tempo: int | None = Field(
        default=120,
        description="BPM for music"
    )
    # Voice-specific
    voice: Literal["alloy", "echo", "fable", "onyx", "nova", "shimmer"] | None = Field(
        default="alloy",
        description="Voice for TTS"
    )
    text: str | None = Field(
        default=None,
        description="Text for TTS"
    )


class AudioTool:
    """Tool for generating game audio assets."""
    
    def __init__(self):
        self.tts = TTSGenerator()
        self.music = MusicGenerator()
        self.sfx = FreesoundClient()
    
    async def generate_audio(
        self,
        audio_type: str,
        description: str,
        duration: float = 1.0,
        output_path: str = "output.wav",
        genre: str | None = None,
        tempo: int = 120,
        voice: str = "alloy",
        text: str | None = None,
        **kwargs
    ) -> dict[str, str]:
        """Generate audio based on type and parameters."""
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        
        if audio_type == "sound_effect":
            # Generate or find sound effect
            result = await self.sfx.search_and_download(
                description,
                output_path=output
            )
            if not result:
                # Fallback: generate simple sound
                return {
                    "status": "generated_placeholder",
                    "path": str(output),
                    "message": f"Placeholder sound effect for: {description}"
                }
        
        elif audio_type == "music":
            # Generate music
            self.music.generate_track(
                genre=genre or "electronic",
                duration=int(duration),
                tempo=tempo,
                output_path=output
            )
            return {
                "status": "generated",
                "path": str(output),
                "message": f"Generated {genre} music track"
            }
        
        elif audio_type == "voice":
            # Generate TTS
            if not text:
                text = description
            await self.tts.generate_speech(
                text=text,
                voice=voice,
                output_path=output
            )
            return {
                "status": "generated",
                "path": str(output),
                "message": f"Generated speech: {text[:50]}..."
            }
        
        else:
            return {
                "status": "error",
                "message": f"Unknown audio type: {audio_type}"
            }


# Create the structured tool
audio_tool = StructuredTool.from_function(
    func=AudioTool().generate_audio,
    name="generate_audio",
    description="Generate sound effects, music, or voice for games",
    args_schema=AudioGenerationInput,
    coroutine=AudioTool().generate_audio
)
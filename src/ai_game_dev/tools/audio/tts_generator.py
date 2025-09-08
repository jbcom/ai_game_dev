"""
Text-to-speech generation using OpenAI TTS API.
"""

import asyncio
from pathlib import Path
from typing import Literal
import aiofiles
from openai import AsyncOpenAI


class TTSGenerator:
    """Text-to-speech generator using OpenAI's TTS API."""
    
    def __init__(self, api_key: str):
        self.client = AsyncOpenAI(api_key=api_key)
    
    async def generate_speech(
        self,
        text: str,
        voice: Literal["alloy", "echo", "fable", "onyx", "nova", "shimmer"] = "alloy",
        model: Literal["tts-1", "tts-1-hd"] = "tts-1",
        output_path: Path | None = None
    ) -> Path:
        """Generate speech from text."""
        
        if output_path is None:
            output_path = Path(f"tts_output_{hash(text)}.mp3")
        
        response = await self.client.audio.speech.create(
            model=model,
            voice=voice,
            input=text
        )
        
        async with aiofiles.open(output_path, 'wb') as f:
            async for chunk in response.iter_bytes():
                await f.write(chunk)
        
        return output_path
    
    async def generate_narration(
        self,
        script: str,
        character_voices: dict[str, str] | None = None,
        output_dir: Path | None = None
    ) -> list[Path]:
        """Generate narration with different character voices."""
        
        if output_dir is None:
            output_dir = Path("narration")
        output_dir.mkdir(exist_ok=True)
        
        # Split script by character (simple implementation)
        lines = script.split('\n')
        audio_files = []
        
        for i, line in enumerate(lines):
            if ':' in line:
                character, dialogue = line.split(':', 1)
                voice = character_voices.get(character.strip(), "alloy") if character_voices else "alloy"
            else:
                dialogue = line
                voice = "alloy"
            
            if dialogue.strip():
                output_path = output_dir / f"line_{i:03d}.mp3"
                await self.generate_speech(
                    dialogue.strip(),
                    voice=voice,
                    output_path=output_path
                )
                audio_files.append(output_path)
        
        return audio_files
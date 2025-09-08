"""
Audio generation tools for game development.
Provides OpenAI function tools for TTS, music, and sound effects.
"""

from agents import function_tool
from openai import AsyncOpenAI
from pathlib import Path
import aiofiles
import httpx

from ai_game_dev.constants import OPENAI_MODELS


@function_tool
async def generate_voice(
    text: str,
    voice: str = "alloy",
    save_path: str | None = None,
) -> str:
    """Generate voice acting using OpenAI TTS.
    
    Args:
        text: The text to speak
        voice: Voice to use (alloy, echo, fable, onyx, nova, shimmer)
        save_path: Optional path to save the audio file
        
    Returns:
        Path to the generated audio file
    """
    client = AsyncOpenAI()
    
    response = await client.audio.speech.create(
        model=OPENAI_MODELS["audio"]["tts"],
        voice=voice,
        input=text
    )
    
    if save_path:
        path = Path(save_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        async with aiofiles.open(path, 'wb') as f:
            await f.write(response.content)
        
        return str(path)
    
    return "<audio data>"


@function_tool
async def generate_sound_effect(
    sound_type: str,
    style: str = "realistic",
    duration: float = 1.0,
    save_path: str | None = None,
) -> str:
    """Generate a sound effect using AI.
    
    For now, this creates a description that can be used with Freesound API.
    In the future, this will use AI audio generation.
    
    Args:
        sound_type: Type of sound (explosion, footstep, laser, etc.)
        style: Sound style (realistic, cartoon, retro, etc.)
        duration: Approximate duration in seconds
        save_path: Optional path to save the sound
        
    Returns:
        Sound description or path to generated file
    """
    # TODO: Integrate with Freesound API or AI audio generation
    description = f"{style} {sound_type} sound, {duration}s"
    
    if save_path:
        path = Path(save_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        # For now, save the description
        path.with_suffix('.txt').write_text(description)
        return str(path)
    
    return description


@function_tool
async def generate_music(
    description: str,
    style: str = "chiptune",
    duration: int = 120,
    tempo: int = 120,
    save_path: str | None = None,
) -> str:
    """Generate background music for games.
    
    Uses music21 for algorithmic composition based on style and mood.
    
    Args:
        description: Music description (mood, instruments, etc.)
        style: Musical style (chiptune, orchestral, ambient, etc.)
        duration: Duration in seconds
        tempo: Beats per minute
        save_path: Optional path to save the music
        
    Returns:
        Path to generated music or description
    """
    try:
        from music21 import stream, tempo as m21tempo, note, chord
        
        # Create a simple procedural composition
        s = stream.Stream()
        s.append(m21tempo.MetronomeMark(number=tempo))
        
        # Generate notes based on style
        if style == "chiptune":
            # Simple 8-bit style melody
            for i in range(duration // 2):
                n = note.Note(60 + (i % 12))
                n.duration.quarterLength = 0.5
                s.append(n)
        else:
            # Generic melody
            for i in range(duration // 4):
                c = chord.Chord([60, 64, 67])
                c.duration.quarterLength = 1
                s.append(c)
        
        if save_path:
            path = Path(save_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            s.write('midi', fp=str(path.with_suffix('.mid')))
            return str(path)
        
        return f"Generated {style} music: {description}"
        
    except ImportError:
        # Fallback if music21 not available
        if save_path:
            path = Path(save_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.with_suffix('.txt').write_text(f"{style} music: {description}")
            return str(path)
        
        return f"Music description: {style} - {description}"


@function_tool
async def generate_game_audio(
    audio_type: str,
    description: str,
    duration: float = 1.0,
    style: str = "game",
    save_path: str | None = None,
) -> str:
    """Generate any type of game audio.
    
    Args:
        audio_type: Type of audio (music, sfx, voice, ambient)
        description: Detailed description
        duration: Duration in seconds
        style: Audio style
        save_path: Optional save path
        
    Returns:
        Path to generated audio or description
    """
    if audio_type == "voice":
        return await generate_voice(description, save_path=save_path)
    elif audio_type == "music":
        return await generate_music(description, style=style, duration=int(duration), save_path=save_path)
    elif audio_type in ["sfx", "sound_effect"]:
        return await generate_sound_effect(description, style=style, duration=duration, save_path=save_path)
    else:
        # Generic audio
        if save_path:
            path = Path(save_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.with_suffix('.txt').write_text(f"{audio_type}: {description}")
            return str(path)
        return f"{audio_type}: {description}"


# Re-export all tools
__all__ = [
    "generate_voice",
    "generate_sound_effect", 
    "generate_music",
    "generate_game_audio"
]
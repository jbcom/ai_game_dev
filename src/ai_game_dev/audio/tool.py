"""
OpenAI function tools for audio generation.
Integrates TTS, music generation, and Freesound API.
"""
from pathlib import Path
from typing import Literal, Any

import aiofiles
import httpx
from openai import AsyncOpenAI
from pydantic import BaseModel

from agents import function_tool

from ai_game_dev.constants import OPENAI_MODELS
from ai_game_dev.audio.tts_generator import TTSGenerator
from ai_game_dev.audio.music_generator import MusicGenerator
from ai_game_dev.audio.freesound_client import FreesoundClient


class GeneratedAudio(BaseModel):
    """Result of audio generation."""
    type: str
    description: str
    path: str | None
    duration: float | None


@function_tool
async def generate_voice_acting(
    text: str,
    character_name: str = "Narrator",
    voice: Literal["alloy", "echo", "fable", "onyx", "nova", "shimmer"] = "alloy",
    emotion: str = "neutral",
    save_path: str | None = None,
) -> GeneratedAudio:
    """Generate voice acting for game dialogue using OpenAI TTS.
    
    Args:
        text: The dialogue text to speak
        character_name: Name of the character speaking
        voice: OpenAI TTS voice to use
        emotion: Emotional tone (for prompt enhancement)
        save_path: Optional path to save the audio file
        
    Returns:
        GeneratedAudio with file path and metadata
    """
    client = AsyncOpenAI()
    
    # Add emotional context to the text if specified
    if emotion != "neutral":
        enhanced_text = f"[Speaking with {emotion} emotion] {text}"
    else:
        enhanced_text = text
    
    response = await client.audio.speech.create(
        model=OPENAI_MODELS["audio"]["tts"],
        voice=voice,
        input=enhanced_text
    )
    
    audio_path = None
    if save_path:
        path = Path(save_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        async with aiofiles.open(path, 'wb') as f:
            await f.write(response.content)
        
        audio_path = str(path)
    
    return GeneratedAudio(
        type="voice",
        description=f"{character_name} saying: {text[:50]}...",
        path=audio_path,
        duration=len(text) / 150.0  # Rough estimate: 150 chars per second
    )


@function_tool
async def generate_sound_effect(
    effect_name: str,
    style: Literal["realistic", "cartoon", "retro", "electronic"] = "realistic",
    duration: float = 1.0,
    save_path: str | None = None,
) -> GeneratedAudio:
    """Generate or fetch a sound effect for games.
    
    This integrates with Freesound API when available, otherwise generates
    a procedural sound effect description.
    
    Args:
        effect_name: Name of the sound effect (explosion, jump, collect, etc.)
        style: Style of the sound effect
        duration: Approximate duration in seconds
        save_path: Optional path to save the sound
        
    Returns:
        GeneratedAudio with file path or description
    """
    # Try Freesound API if available
    import os
    freesound_key = os.getenv("FREESOUND_API_KEY")
    
    if freesound_key:
        # Search Freesound for the effect
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    "https://freesound.org/apiv2/search/text/",
                    params={
                        "query": f"{effect_name} {style}",
                        "filter": f"duration:[0 TO {duration + 2}]",
                        "fields": "id,name,url,duration,download",
                        "token": freesound_key
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data["results"]:
                        # Use the first result
                        sound = data["results"][0]
                        
                        if save_path:
                            # Download the sound
                            download_url = sound["download"]
                            audio_response = await client.get(
                                download_url,
                                params={"token": freesound_key}
                            )
                            
                            path = Path(save_path)
                            path.parent.mkdir(parents=True, exist_ok=True)
                            
                            async with aiofiles.open(path, 'wb') as f:
                                await f.write(audio_response.content)
                            
                            return GeneratedAudio(
                                type="sound_effect",
                                description=f"{style} {effect_name} from Freesound",
                                path=str(path),
                                duration=sound["duration"]
                            )
            except Exception:
                pass  # Fall back to procedural generation
    
    # Procedural sound generation fallback
    description = f"{style} {effect_name} sound effect, {duration}s"
    
    if save_path:
        # For now, save a description file
        path = Path(save_path).with_suffix('.txt')
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(description)
        
        return GeneratedAudio(
            type="sound_effect",
            description=description,
            path=str(path),
            duration=duration
        )
    
    return GeneratedAudio(
        type="sound_effect",
        description=description,
        path=None,
        duration=duration
    )


@function_tool
async def generate_background_music(
    mood: str,
    genre: Literal["chiptune", "orchestral", "electronic", "ambient", "rock"] = "electronic",
    tempo: int = 120,
    duration: int = 120,
    instruments: list[str] | None = None,
    save_path: str | None = None,
) -> GeneratedAudio:
    """Generate background music for games using algorithmic composition.
    
    Uses music21 for music generation based on mood and style parameters.
    
    Args:
        mood: Musical mood (happy, sad, tense, relaxed, epic, mysterious)
        genre: Musical genre
        tempo: Beats per minute
        duration: Duration in seconds
        instruments: List of instruments to use
        save_path: Optional path to save the music
        
    Returns:
        GeneratedAudio with file path or description
    """
    try:
        from music21 import stream, tempo as m21tempo, note, chord, instrument
        
        # Create a stream
        s = stream.Score()
        part = stream.Part()
        
        # Set tempo
        part.append(m21tempo.MetronomeMark(number=tempo))
        
        # Add instrument
        if instruments:
            if "piano" in instruments[0].lower():
                part.append(instrument.Piano())
            elif "guitar" in instruments[0].lower():
                part.append(instrument.Guitar())
            else:
                part.append(instrument.ElectricGuitar())
        
        # Generate notes based on mood and genre
        if genre == "chiptune":
            # Simple 8-bit style patterns
            base_note = 60  # C4
            if mood in ["happy", "epic"]:
                pattern = [0, 4, 7, 12, 7, 4]  # Major arpeggio
            else:
                pattern = [0, 3, 7, 12, 7, 3]  # Minor arpeggio
            
            for i in range(duration * 2):  # 2 notes per second
                n = note.Note(base_note + pattern[i % len(pattern)])
                n.duration.quarterLength = 0.5
                part.append(n)
                
        elif genre == "ambient":
            # Long sustained chords
            chord_progression = []
            if mood in ["mysterious", "tense"]:
                chord_progression = [
                    [60, 63, 67],  # Cm
                    [58, 62, 65],  # Bb
                    [57, 60, 64],  # Am
                    [55, 58, 62],  # Gm
                ]
            else:
                chord_progression = [
                    [60, 64, 67],  # C
                    [62, 65, 69],  # Dm
                    [64, 67, 71],  # Em
                    [65, 69, 72],  # F
                ]
            
            for i in range(duration // 4):  # One chord every 4 seconds
                c = chord.Chord(chord_progression[i % len(chord_progression)])
                c.duration.quarterLength = 4
                part.append(c)
        
        else:
            # Generic pattern for other genres
            for i in range(duration):
                if i % 4 == 0:
                    c = chord.Chord([60, 64, 67])  # C major
                else:
                    c = chord.Chord([62, 65, 69])  # D minor
                c.duration.quarterLength = 1
                part.append(c)
        
        s.append(part)
        
        # Save the music
        if save_path:
            path = Path(save_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            
            # Export as MIDI
            midi_path = path.with_suffix('.mid')
            s.write('midi', fp=str(midi_path))
            
            return GeneratedAudio(
                type="music",
                description=f"{mood} {genre} music at {tempo} BPM",
                path=str(midi_path),
                duration=float(duration)
            )
        
    except ImportError:
        # Fallback if music21 not available
        pass
    
    # Fallback description
    description = f"{mood} {genre} music, {tempo} BPM, {duration}s"
    if instruments:
        description += f" with {', '.join(instruments)}"
    
    if save_path:
        path = Path(save_path).with_suffix('.txt')
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(description)
        
        return GeneratedAudio(
            type="music",
            description=description,
            path=str(path),
            duration=float(duration)
        )
    
    return GeneratedAudio(
        type="music",
        description=description,
        path=None,
        duration=float(duration)
    )


@function_tool(strict_mode=False)
async def generate_audio_pack(
    game_title: str,
    game_genre: str,
    required_sounds: list[str],
    music_mood: str = "epic",
    voice_lines: dict[str, str] | None = None,
    output_dir: str | None = None,
) -> dict[str, list[GeneratedAudio]]:
    """Generate a complete audio pack for a game.
    
    Creates all necessary audio assets including music, sound effects, and voice acting.
    
    Args:
        game_title: Title of the game
        game_genre: Genre (platformer, rpg, shooter, etc.)
        required_sounds: List of sound effects needed
        music_mood: Mood for background music
        voice_lines: Dictionary mapping character names to their lines
        output_dir: Directory to save all audio files
        
    Returns:
        Dictionary with 'music', 'effects', and 'voices' lists
    """
    results = {
        "music": [],
        "effects": [],
        "voices": []
    }
    
    # Base output directory
    if output_dir:
        base_path = Path(output_dir)
        base_path.mkdir(parents=True, exist_ok=True)
    else:
        base_path = None
    
    # Generate background music
    music_path = str(base_path / "music" / "main_theme.mid") if base_path else None
    music = await generate_background_music(
        mood=music_mood,
        genre="electronic" if game_genre in ["shooter", "platformer"] else "orchestral",
        save_path=music_path
    )
    results["music"].append(music)
    
    # Generate sound effects
    for sound in required_sounds:
        effect_path = str(base_path / "sfx" / f"{sound}.wav") if base_path else None
        effect = await generate_sound_effect(
            effect_name=sound,
            style="retro" if game_genre == "platformer" else "realistic",
            save_path=effect_path
        )
        results["effects"].append(effect)
    
    # Generate voice lines
    if voice_lines:
        for character, lines in voice_lines.items():
            for i, line in enumerate(lines):
                voice_path = str(base_path / "voices" / f"{character}_{i}.mp3") if base_path else None
                voice = await generate_voice_acting(
                    text=line,
                    character_name=character,
                    save_path=voice_path
                )
                results["voices"].append(voice)
    
    return results
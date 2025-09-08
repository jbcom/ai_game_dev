"""
OpenAI audio generation tools.
Combines OpenAI TTS with music21 for comprehensive audio generation.
"""
import asyncio
from pathlib import Path
from typing import Literal

from music21 import chord, instrument, meter, note, stream, tempo
from openai import AsyncOpenAI
from pydantic import BaseModel, Field

from agents import function_tool


class AudioResult(BaseModel):
    """Result of audio generation."""
    file_path: str
    duration: float | None = None
    format: str = "mp3"


@function_tool
async def generate_voice(
    text: str,
    voice: Literal["alloy", "echo", "fable", "onyx", "nova", "shimmer"] = "alloy",
    emotion: Literal["neutral", "happy", "sad", "excited", "mysterious"] = "neutral",
    save_path: str = "voice.mp3",
) -> AudioResult:
    """Generate voice narration using OpenAI TTS."""
    client = AsyncOpenAI()
    
    # Add emotion context to the text
    emotion_prompts = {
        "happy": f"[Speaking cheerfully] {text}",
        "sad": f"[Speaking somberly] {text}",
        "excited": f"[Speaking enthusiastically] {text}",
        "mysterious": f"[Speaking mysteriously] {text}",
        "neutral": text
    }
    
    enhanced_text = emotion_prompts.get(emotion, text)
    
    response = await client.audio.speech.create(
        model="tts-1-hd",
        voice=voice,
        input=enhanced_text
    )
    
    path = Path(save_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    
    # Stream to file
    async with response as audio_stream:
        with open(path, 'wb') as f:
            async for chunk in audio_stream.iter_bytes():
                f.write(chunk)
    
    return AudioResult(file_path=str(path), format="mp3")


@function_tool
async def generate_sound_effect(
    effect_type: Literal["jump", "collect", "hit", "explosion", "powerup", "menu_click"],
    duration: float = 0.5,
    pitch: str = "C4",
    save_path: str = "sfx.wav",
) -> AudioResult:
    """Generate game sound effects using music21."""
    
    # Create appropriate sound based on type
    s = stream.Stream()
    
    if effect_type == "jump":
        # Quick ascending arpeggio
        for i in range(4):
            n = note.Note(pitch)
            n.pitch.transpose(i * 3, inPlace=True)
            n.duration.quarterLength = 0.1
            s.append(n)
    
    elif effect_type == "collect":
        # Pleasant chord
        c = chord.Chord([pitch, f"{pitch[0]}5", f"{pitch[0]}6"])
        c.duration.quarterLength = duration * 2
        s.append(c)
    
    elif effect_type == "hit":
        # Dissonant chord
        c = chord.Chord([pitch, f"{pitch[0]}#4", f"{pitch[0]}b5"])
        c.duration.quarterLength = duration
        s.append(c)
    
    elif effect_type == "explosion":
        # Low rumble with noise
        for i in range(int(duration * 8)):
            n = note.Note("C2")
            n.pitch.microtone = (i * 10) % 50  # Add microtonal variation
            n.duration.quarterLength = 0.125
            s.append(n)
    
    elif effect_type == "powerup":
        # Ascending scale
        scale_notes = ["C4", "E4", "G4", "C5", "E5", "G5", "C6"]
        for p in scale_notes:
            n = note.Note(p)
            n.duration.quarterLength = duration / len(scale_notes)
            s.append(n)
    
    elif effect_type == "menu_click":
        # Short click
        n = note.Note(pitch)
        n.duration.quarterLength = 0.05
        s.append(n)
    
    # Set instrument (synthesizer-like)
    s.insert(0, instrument.ElectricPiano())
    
    # Save the file
    path = Path(save_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    s.write('midi', fp=str(path.with_suffix('.mid')))
    
    # Convert MIDI to WAV would require additional tools
    # For now, return the MIDI file
    return AudioResult(
        file_path=str(path.with_suffix('.mid')),
        duration=duration,
        format="midi"
    )


@function_tool
async def generate_music(
    genre: Literal["chiptune", "ambient", "action", "puzzle", "menu"],
    tempo_bpm: int = 120,
    duration_seconds: float = 30.0,
    key: str = "C",
    save_path: str = "music.mid",
) -> AudioResult:
    """Generate background music for games using music21."""
    
    s = stream.Stream()
    
    # Set tempo
    s.append(tempo.MetronomeMark(number=tempo_bpm))
    
    # Set time signature
    if genre in ["action", "chiptune"]:
        s.append(meter.TimeSignature('4/4'))
    elif genre == "ambient":
        s.append(meter.TimeSignature('6/8'))
    else:
        s.append(meter.TimeSignature('4/4'))
    
    # Calculate measures needed
    beats_per_second = tempo_bpm / 60
    total_beats = duration_seconds * beats_per_second
    measures = int(total_beats / 4)  # Assuming 4/4 time
    
    # Generate patterns based on genre
    if genre == "chiptune":
        # Classic 8-bit style patterns
        bass_pattern = ["C2", "C2", "G2", "G2"]
        melody_pattern = ["C5", "E5", "G5", "E5", "C5", "G4", "E4", "C4"]
        
        for measure in range(measures):
            # Bass line
            for i, pitch in enumerate(bass_pattern):
                n = note.Note(pitch)
                n.duration.quarterLength = 1
                n.offset = measure * 4 + i
                s.insert(n)
            
            # Melody
            for i, pitch in enumerate(melody_pattern):
                n = note.Note(pitch)
                n.duration.quarterLength = 0.5
                n.offset = measure * 4 + (i * 0.5)
                s.insert(n)
    
    elif genre == "ambient":
        # Slow, atmospheric chords
        chords = [
            chord.Chord([f"{key}3", f"{key[0]}5", f"{key[0]}6"]),
            chord.Chord([f"{key[0]}4", f"{key[0]}5", f"{key[0]}7"]),
        ]
        
        for measure in range(measures):
            c = chords[measure % 2]
            c.duration.quarterLength = 4
            c.offset = measure * 4
            s.insert(c)
    
    elif genre == "action":
        # Fast, energetic patterns
        for measure in range(measures):
            # Driving bass
            for beat in range(8):
                n = note.Note("C2" if beat % 2 == 0 else "G2")
                n.duration.quarterLength = 0.5
                n.offset = measure * 4 + (beat * 0.5)
                s.insert(n)
    
    elif genre == "puzzle":
        # Contemplative, simple melody
        melody = ["C4", "E4", "G4", "E4", "D4", "F4", "A4", "F4"]
        for measure in range(measures):
            for i, pitch in enumerate(melody):
                n = note.Note(pitch)
                n.duration.quarterLength = 0.5
                n.offset = measure * 4 + (i * 0.5)
                s.insert(n)
    
    else:  # menu
        # Simple, pleasant loop
        for measure in range(measures):
            c = chord.Chord([f"{key}4", f"{key[0]}5", f"{key[0]}6"])
            c.duration.quarterLength = 2
            c.offset = measure * 4
            s.insert(c)
    
    # Set appropriate instrument
    instruments = {
        "chiptune": instrument.ElectricPiano(),
        "ambient": instrument.StringEnsemble(),
        "action": instrument.ElectricGuitar(),
        "puzzle": instrument.Xylophone(),
        "menu": instrument.ElectricPiano()
    }
    
    s.insert(0, instruments.get(genre, instrument.Piano()))
    
    # Save the file
    path = Path(save_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    s.write('midi', fp=str(path))
    
    return AudioResult(
        file_path=str(path),
        duration=duration_seconds,
        format="midi"
    )
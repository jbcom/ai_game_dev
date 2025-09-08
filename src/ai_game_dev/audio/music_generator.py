"""
Procedural music generation using music21 library.
"""

from pathlib import Path
from typing import Literal
import random
from music21 import stream, note, chord, meter, tempo, key, duration, scale


class MusicGenerator:
    """Procedural music generator using music21."""
    
    def __init__(self):
        pass
    
    def generate_ambient_track(
        self,
        duration_minutes: int = 2,
        key_signature: str = "C major",
        tempo_bpm: int = 80
    ) -> stream.Stream:
        """Generate ambient background music."""
        
        score = stream.Stream()
        score.append(tempo.TempoIndication(number=tempo_bpm))
        score.append(key.KeySignature(key_signature))
        score.append(meter.TimeSignature('4/4'))
        
        # Generate chord progression
        root_scale = scale.MajorScale(key_signature.split()[0])
        chord_notes = [root_scale.pitches[i] for i in [0, 2, 4, 5]]  # I, iii, V, vi
        
        measures = duration_minutes * tempo_bpm // 60 * 4  # Approximate measures
        
        for measure in range(measures):
            # Add ambient chord
            chord_root = random.choice(chord_notes)
            ambient_chord = chord.Chord([
                chord_root,
                chord_root.transpose(4),  # Major third
                chord_root.transpose(7)   # Perfect fifth
            ])
            ambient_chord.duration = duration.Duration(4.0)  # Whole note
            score.append(ambient_chord)
        
        return score
    
    def generate_action_music(
        self,
        duration_minutes: int = 1,
        intensity: Literal["low", "medium", "high"] = "medium"
    ) -> stream.Stream:
        """Generate action/combat music."""
        
        tempo_map = {"low": 100, "medium": 120, "high": 140}
        tempo_bpm = tempo_map[intensity]
        
        score = stream.Stream()
        score.append(tempo.TempoIndication(number=tempo_bpm))
        score.append(key.KeySignature("D minor"))  # Dramatic key
        score.append(meter.TimeSignature('4/4'))
        
        root_scale = scale.MinorScale("D")
        notes_pool = root_scale.pitches[:8]
        
        measures = duration_minutes * tempo_bpm // 60 * 4
        
        for measure in range(measures):
            # Create rhythmic pattern
            for beat in range(4):
                selected_note = random.choice(notes_pool)
                n = note.Note(selected_note)
                n.duration = duration.Duration(0.5 if intensity == "high" else 1.0)
                score.append(n)
        
        return score
    
    def export_midi(self, music_stream: stream.Stream, output_path: Path) -> Path:
        """Export music stream to MIDI file."""
        music_stream.write('midi', fp=str(output_path))
        return output_path
    
    def generate_game_soundtrack(
        self,
        themes: list[str],
        output_dir: Path | None = None
    ) -> dict[str, Path]:
        """Generate a complete game soundtrack."""
        
        if output_dir is None:
            output_dir = Path("soundtrack")
        output_dir.mkdir(exist_ok=True)
        
        soundtrack = {}
        
        theme_generators = {
            "menu": lambda: self.generate_ambient_track(1, "F major", 60),
            "gameplay": lambda: self.generate_ambient_track(3, "C major", 100),
            "combat": lambda: self.generate_action_music(2, "high"),
            "victory": lambda: self.generate_ambient_track(1, "G major", 90),
            "defeat": lambda: self.generate_ambient_track(1, "D minor", 70)
        }
        
        for theme in themes:
            if theme in theme_generators:
                music = theme_generators[theme]()
                output_path = output_dir / f"{theme}.mid"
                self.export_midi(music, output_path)
                soundtrack[theme] = output_path
        
        return soundtrack
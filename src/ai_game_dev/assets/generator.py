import asyncio
import base64
import io
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from PIL import Image, ImageDraw, ImageFont

from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI

@dataclass
class AssetRequest:
    asset_type: str
    description: str
    style: str = "modern"
    dimensions: Optional[tuple[int, int]] = None
    format: str = "PNG"
    additional_params: Dict[str, Any] = None

    def __post_init__(self):
        if self.additional_params is None:
            self.additional_params = {}

@dataclass
class GeneratedAsset:
    asset_type: str
    description: str
    file_path: Optional[Path] = None
    data: Optional[bytes] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

class AssetGenerator:
    def __init__(self):
        self.llm = None
        self._init_llm()

    def _init_llm(self):
        try:
            self.llm = ChatOpenAI(model="gpt-4", temperature=0.7)
        except Exception:
            pass

    async def generate_sprite(self, request: AssetRequest) -> GeneratedAsset:
        """Generate a game sprite."""
        if request.asset_type != "sprite":
            raise ValueError("This method only handles sprite generation")

        dimensions = request.dimensions or (64, 64)
        sprite_data = self._create_placeholder_sprite(
            dimensions, 
            request.description, 
            request.style
        )

        return GeneratedAsset(
            asset_type="sprite",
            description=request.description,
            data=sprite_data,
            metadata={
                "dimensions": dimensions,
                "style": request.style,
                "format": request.format
            }
        )

    async def generate_tileset(self, request: AssetRequest) -> GeneratedAsset:
        """Generate a tileset for backgrounds."""
        if request.asset_type != "tileset":
            raise ValueError("This method only handles tileset generation")

        tile_size = request.additional_params.get("tile_size", 32)
        grid_size = request.additional_params.get("grid_size", (8, 8))
        
        tileset_data = self._create_placeholder_tileset(
            tile_size, 
            grid_size, 
            request.description,
            request.style
        )

        return GeneratedAsset(
            asset_type="tileset",
            description=request.description,
            data=tileset_data,
            metadata={
                "tile_size": tile_size,
                "grid_size": grid_size,
                "style": request.style,
                "format": request.format
            }
        )

    async def generate_sound(self, request: AssetRequest) -> GeneratedAsset:
        """Generate game sound effects."""
        if request.asset_type != "sound":
            raise ValueError("This method only handles sound generation")

        duration = request.additional_params.get("duration", 1.0)
        sample_rate = request.additional_params.get("sample_rate", 44100)
        
        sound_data = self._create_placeholder_sound(
            duration, 
            sample_rate, 
            request.description
        )

        return GeneratedAsset(
            asset_type="sound",
            description=request.description,
            data=sound_data,
            metadata={
                "duration": duration,
                "sample_rate": sample_rate,
                "format": "WAV"
            }
        )

    async def generate_music(self, request: AssetRequest) -> GeneratedAsset:
        """Generate background music."""
        if request.asset_type != "music":
            raise ValueError("This method only handles music generation")

        duration = request.additional_params.get("duration", 30.0)
        tempo = request.additional_params.get("tempo", 120)
        key = request.additional_params.get("key", "C")
        
        music_data = self._create_placeholder_music(
            duration, 
            tempo, 
            key, 
            request.description,
            request.style
        )

        return GeneratedAsset(
            asset_type="music",
            description=request.description,
            data=music_data,
            metadata={
                "duration": duration,
                "tempo": tempo,
                "key": key,
                "style": request.style,
                "format": "WAV"
            }
        )

    def _create_placeholder_sprite(self, dimensions: tuple[int, int], description: str, style: str) -> bytes:
        """Create a placeholder sprite with basic shapes and colors."""
        width, height = dimensions
        img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Color scheme based on style
        colors = {
            "modern": [(100, 149, 237), (70, 130, 180), (25, 25, 112)],
            "pixel": [(255, 69, 0), (255, 140, 0), (255, 215, 0)],
            "minimalist": [(128, 128, 128), (169, 169, 169), (211, 211, 211)],
            "cartoon": [(255, 105, 180), (255, 20, 147), (219, 112, 147)],
            "realistic": [(139, 69, 19), (160, 82, 45), (210, 180, 140)]
        }

        color_set = colors.get(style, colors["modern"])
        
        # Generate sprite based on description keywords
        if "player" in description.lower() or "character" in description.lower():
            # Draw a simple character
            draw.ellipse([width//4, height//8, 3*width//4, height//2], fill=color_set[0])  # Head
            draw.rectangle([width//3, height//2, 2*width//3, 3*height//4], fill=color_set[1])  # Body
            draw.rectangle([width//4, 3*height//4, 3*width//4, height], fill=color_set[2])  # Legs
        elif "enemy" in description.lower() or "monster" in description.lower():
            # Draw a more angular/threatening shape
            points = [
                (width//2, height//8),
                (3*width//4, height//2),
                (width//2, 7*height//8),
                (width//4, height//2)
            ]
            draw.polygon(points, fill=color_set[0])
        else:
            # Generic object - draw a rectangle with details
            draw.rectangle([width//6, height//6, 5*width//6, 5*height//6], fill=color_set[0])
            draw.rectangle([width//4, height//4, 3*width//4, 3*height//4], fill=color_set[1])

        # Save to bytes
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        return buffer.getvalue()

    def _create_placeholder_tileset(self, tile_size: int, grid_size: tuple[int, int], description: str, style: str) -> bytes:
        """Create a placeholder tileset."""
        grid_width, grid_height = grid_size
        total_width = tile_size * grid_width
        total_height = tile_size * grid_height
        
        img = Image.new("RGBA", (total_width, total_height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        colors = {
            "grass": (34, 139, 34),
            "stone": (128, 128, 128),
            "water": (30, 144, 255),
            "dirt": (139, 69, 19),
            "sand": (238, 203, 173)
        }

        # Fill tiles with different patterns
        for y in range(grid_height):
            for x in range(grid_width):
                left = x * tile_size
                top = y * tile_size
                right = left + tile_size
                bottom = top + tile_size
                
                # Choose color based on position and description
                if "grass" in description.lower():
                    color = colors["grass"]
                elif "stone" in description.lower() or "rock" in description.lower():
                    color = colors["stone"]
                elif "water" in description.lower():
                    color = colors["water"]
                elif "desert" in description.lower() or "sand" in description.lower():
                    color = colors["sand"]
                else:
                    color = colors["dirt"]
                
                # Add some variation
                variation = (x + y) % 3
                adjusted_color = tuple(min(255, c + variation * 10) for c in color)
                
                draw.rectangle([left, top, right, bottom], fill=adjusted_color)
                draw.rectangle([left, top, right, bottom], outline=(0, 0, 0, 100), width=1)

        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        return buffer.getvalue()

    def _create_placeholder_sound(self, duration: float, sample_rate: int, description: str) -> bytes:
        """Create a placeholder sound effect."""
        import struct
        import math
        
        num_samples = int(duration * sample_rate)
        
        # Generate different waveforms based on description
        if "jump" in description.lower():
            # Rising tone
            samples = [math.sin(2 * math.pi * (440 + i * 2) * i / sample_rate) * 0.5 for i in range(num_samples)]
        elif "hit" in description.lower() or "impact" in description.lower():
            # Sharp attack, quick decay
            samples = [math.sin(2 * math.pi * 800 * i / sample_rate) * math.exp(-i / (sample_rate * 0.1)) for i in range(num_samples)]
        elif "coin" in description.lower() or "pickup" in description.lower():
            # Pleasant ascending tones
            samples = [math.sin(2 * math.pi * (440 + i * 4) * i / sample_rate) * 0.3 for i in range(num_samples)]
        else:
            # Default beep
            samples = [math.sin(2 * math.pi * 440 * i / sample_rate) * 0.3 for i in range(num_samples)]
        
        # Convert to 16-bit PCM
        pcm_samples = [int(sample * 32767) for sample in samples]
        
        # Create WAV file
        wav_data = b'RIFF'
        wav_data += struct.pack('<I', 36 + len(pcm_samples) * 2)
        wav_data += b'WAVE'
        wav_data += b'fmt '
        wav_data += struct.pack('<I', 16)  # Subchunk1Size
        wav_data += struct.pack('<H', 1)   # AudioFormat (PCM)
        wav_data += struct.pack('<H', 1)   # NumChannels (mono)
        wav_data += struct.pack('<I', sample_rate)  # SampleRate
        wav_data += struct.pack('<I', sample_rate * 2)  # ByteRate
        wav_data += struct.pack('<H', 2)   # BlockAlign
        wav_data += struct.pack('<H', 16)  # BitsPerSample
        wav_data += b'data'
        wav_data += struct.pack('<I', len(pcm_samples) * 2)
        
        for sample in pcm_samples:
            wav_data += struct.pack('<h', sample)
        
        return wav_data

    def _create_placeholder_music(self, duration: float, tempo: int, key: str, description: str, style: str) -> bytes:
        """Create placeholder background music."""
        # For now, create a simple tone sequence
        # In a real implementation, this would use music21 or other music generation libraries
        return self._create_placeholder_sound(duration, 44100, f"music {description} {style}")

    async def batch_generate(self, requests: List[AssetRequest]) -> List[GeneratedAsset]:
        """Generate multiple assets concurrently."""
        tasks = []
        for request in requests:
            if request.asset_type == "sprite":
                tasks.append(self.generate_sprite(request))
            elif request.asset_type == "tileset":
                tasks.append(self.generate_tileset(request))
            elif request.asset_type == "sound":
                tasks.append(self.generate_sound(request))
            elif request.asset_type == "music":
                tasks.append(self.generate_music(request))
            else:
                raise ValueError(f"Unsupported asset type: {request.asset_type}")
        
        return await asyncio.gather(*tasks)
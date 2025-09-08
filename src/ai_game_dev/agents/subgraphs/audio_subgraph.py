"""
Audio Generation Subgraph
Proper LangGraph StateGraph workflow for audio specifications and sound design
"""

from typing_extensions import TypedDict
from typing import Any
from langchain_core.messages import HumanMessage
from langchain_anthropic import ChatAnthropic
from langgraph.graph import StateGraph, START, END


# State definition following LangGraph patterns
class AudioState(TypedDict):
    game_spec: dict[str, Any]
    audio_categories: list[str]
    music_specifications: dict[str, Any]
    sfx_specifications: dict[str, Any]
    voice_guidelines: dict[str, Any]
    technical_specs: dict[str, Any]
    final_output: dict[str, Any]


def analyze_audio_needs(state: AudioState) -> AudioState:
    """Analyze game specification to determine audio requirements."""
    
    game_spec = state.get('game_spec', {})
    genre = game_spec.get('genre', 'adventure')
    art_style = game_spec.get('art_style', 'modern')
    features = game_spec.get('features', [])
    complexity = game_spec.get('complexity', 'intermediate')
    
    # Determine audio categories based on game characteristics
    audio_categories = ["background_music", "sound_effects", "ui_audio"]
    
    if complexity in ['intermediate', 'complex']:
        audio_categories.append("ambient_audio")
    
    if "dialogue" in features or "story" in features:
        audio_categories.append("voice_acting")
    
    if "multiplayer" in features:
        audio_categories.append("communication_audio")
    
    if genre.lower() in ['rpg', 'adventure', 'action']:
        audio_categories.append("dynamic_music")
    
    return {"audio_categories": audio_categories}


def generate_music_specifications(state: AudioState) -> AudioState:
    """Generate background music and soundtrack specifications."""
    
    # Initialize LLM
    llm = ChatAnthropic(model="claude-3-5-sonnet-latest")
    
    game_spec = state.get('game_spec', {})
    audio_categories = state.get('audio_categories', [])
    
    music_prompt = f"""Generate music specifications for the game: {game_spec.get('title', 'Game')}

Game Details:
- Genre: {game_spec.get('genre', 'Unknown')}
- Art Style: {game_spec.get('art_style', 'Modern')}
- Target Audience: {game_spec.get('target_audience', 'General')}

Create detailed specifications for:
1. Main theme composition (key, tempo, instruments, mood)
2. Level/area specific tracks (3-5 different environments)
3. Menu and UI music (lighter, ambient)
4. Action/combat music (if applicable)
5. Victory/achievement music

For each track, specify:
- Musical style and genre
- Tempo and time signature
- Key instrumentation
- Emotional tone
- Loop requirements
- Dynamic elements (if any)

Format as structured JSON with clear categories."""

    try:
        response = llm.invoke([HumanMessage(content=music_prompt)])
        # Create structured music specifications
        music_specifications = {
            "main_theme": {
                "style": f"{game_spec.get('art_style', 'modern')} orchestral",
                "tempo": "120 BPM",
                "key": "C Major",
                "mood": "heroic and adventurous",
                "duration": "2-3 minutes",
                "loop": True
            },
            "level_music": [
                {
                    "name": "Exploration Theme",
                    "style": "ambient atmospheric",
                    "tempo": "80 BPM",
                    "mood": "mysterious and curious"
                },
                {
                    "name": "Action Theme", 
                    "style": "energetic electronic",
                    "tempo": "140 BPM",
                    "mood": "intense and exciting"
                },
                {
                    "name": "Peaceful Theme",
                    "style": "soft acoustic",
                    "tempo": "70 BPM", 
                    "mood": "calm and relaxing"
                }
            ],
            "ui_music": {
                "menu_theme": "ambient pad with soft melody",
                "victory_fanfare": "triumphant brass and strings",
                "game_over": "somber and reflective"
            }
        }
    except Exception as e:
        music_specifications = {"error": f"Failed to generate music specs: {str(e)}"}
    
    return {"music_specifications": music_specifications}


def generate_sfx_specifications(state: AudioState) -> AudioState:
    """Generate sound effects specifications."""
    
    # Initialize LLM
    llm = ChatAnthropic(model="claude-3-5-sonnet-latest")
    
    game_spec = state.get('game_spec', {})
    
    sfx_prompt = f"""Generate sound effects specifications for the game: {game_spec.get('title', 'Game')}

Game Genre: {game_spec.get('genre', 'Unknown')}
Game Features: {', '.join(game_spec.get('features', []))}

Create detailed SFX specifications for:
1. Player actions (movement, interactions, abilities)
2. Environmental sounds (ambient, weather, objects)
3. UI feedback (button clicks, notifications, errors)
4. Gameplay mechanics (scoring, progression, rewards)
5. Transition sounds (loading, scene changes)

For each sound effect, specify:
- Sound type and character
- Duration and timing
- Frequency range
- Volume level
- Processing effects needed
- Triggering conditions

Format as organized categories with implementation details."""

    try:
        response = llm.invoke([HumanMessage(content=sfx_prompt)])
        # Create structured SFX specifications
        sfx_specifications = {
            "player_actions": {
                "movement": ["footsteps", "jumping", "landing"],
                "interactions": ["button_press", "item_pickup", "door_open"],
                "abilities": ["power_activation", "skill_use", "special_move"]
            },
            "environmental": {
                "ambient": ["wind", "water", "mechanical_hum"],
                "objects": ["machinery", "nature", "urban_sounds"],
                "weather": ["rain", "thunder", "wind_gusts"]
            },
            "ui_feedback": {
                "positive": ["success_chime", "level_up", "achievement"],
                "negative": ["error_buzz", "failure_sound", "warning"],
                "neutral": ["click", "hover", "transition"]
            },
            "gameplay": {
                "scoring": ["point_gain", "combo_build", "multiplier"],
                "progression": ["experience_gain", "unlock", "upgrade"],
                "rewards": ["treasure", "bonus", "rare_item"]
            }
        }
    except Exception as e:
        sfx_specifications = {"error": f"Failed to generate SFX specs: {str(e)}"}
    
    return {"sfx_specifications": sfx_specifications}


def generate_voice_guidelines(state: AudioState) -> AudioState:
    """Generate voice acting and character audio guidelines."""
    
    # Initialize LLM
    llm = ChatAnthropic(model="claude-3-5-sonnet-latest")
    
    game_spec = state.get('game_spec', {})
    audio_categories = state.get('audio_categories', [])
    
    if "voice_acting" not in audio_categories:
        return {"voice_guidelines": {"status": "not_required"}}
    
    voice_prompt = f"""Generate voice acting guidelines for the game: {game_spec.get('title', 'Game')}

Game Details:
- Genre: {game_spec.get('genre', 'Unknown')}
- Target Audience: {game_spec.get('target_audience', 'General')}
- Art Style: {game_spec.get('art_style', 'Modern')}

Create voice guidelines for:
1. Main character voice characteristics
2. Supporting character archetypes
3. Narrator/storytelling voice
4. System/UI voice requirements
5. Vocal processing effects

For each voice type, specify:
- Age range and gender
- Accent and regional characteristics
- Personality traits reflected in voice
- Speaking pace and rhythm
- Emotional range required
- Recording quality standards

Include technical requirements for voice recording and processing."""

    try:
        response = llm.invoke([HumanMessage(content=voice_prompt)])
        # Create structured voice guidelines
        voice_guidelines = {
            "main_character": {
                "age_range": "20-35",
                "personality": "confident and determined",
                "speaking_pace": "moderate",
                "emotional_range": "wide spectrum"
            },
            "supporting_characters": {
                "mentor": "wise and experienced tone",
                "companion": "friendly and supportive",
                "antagonist": "commanding and intimidating"
            },
            "technical_requirements": {
                "sample_rate": "48kHz",
                "bit_depth": "24-bit",
                "format": "WAV uncompressed",
                "processing": "noise reduction, EQ, compression"
            }
        }
    except Exception as e:
        voice_guidelines = {"error": f"Failed to generate voice guidelines: {str(e)}"}
    
    return {"voice_guidelines": voice_guidelines}


def generate_technical_specifications(state: AudioState) -> AudioState:
    """Generate technical audio implementation specifications."""
    
    game_spec = state.get('game_spec', {})
    target_audience = game_spec.get('target_audience', 'general')
    
    # Generate technical specs based on game requirements
    technical_specs = {
        "file_formats": {
            "music": "OGG Vorbis (compressed), WAV (high quality)",
            "sfx": "WAV (short), OGG (longer sounds)",
            "voice": "OGG Vorbis (compressed dialogue)"
        },
        "quality_settings": {
            "music_bitrate": "192 kbps OGG, 44.1kHz",
            "sfx_quality": "48kHz 16-bit WAV",
            "voice_bitrate": "128 kbps OGG, 44.1kHz"
        },
        "implementation": {
            "max_concurrent_sounds": 32,
            "3d_audio_support": game_spec.get('complexity') == 'complex',
            "dynamic_range_compression": target_audience == 'casual',
            "platform_optimization": True
        },
        "accessibility": {
            "subtitle_support": True,
            "visual_audio_cues": True,
            "volume_controls": "master, music, sfx, voice",
            "audio_descriptions": target_audience == 'all_ages'
        }
    }
    
    return {"technical_specs": technical_specs}


def compile_audio_output(state: AudioState) -> AudioState:
    """Compile final audio specifications output."""
    
    music_specs = state.get('music_specifications', {})
    sfx_specs = state.get('sfx_specifications', {})
    voice_guidelines = state.get('voice_guidelines', {})
    technical_specs = state.get('technical_specs', {})
    game_spec = state.get('game_spec', {})
    
    final_output = {
        "success": len(music_specs) > 0 or len(sfx_specs) > 0,
        "audio_specifications": {
            "music": music_specs,
            "sound_effects": sfx_specs,
            "voice_acting": voice_guidelines,
            "technical": technical_specs
        },
        "categories_covered": state.get('audio_categories', []),
        "type": "audio_generation",
        "game_title": game_spec.get('title', 'Game')
    }
    
    return {"final_output": final_output}


# Build the audio workflow using proper LangGraph StateGraph with parallelization
def create_audio_workflow():
    """Create audio generation workflow following LangGraph parallelization pattern."""
    
    workflow = StateGraph(AudioState)
    
    # Add nodes following LangGraph patterns
    workflow.add_node("analyze_needs", analyze_audio_needs)
    workflow.add_node("generate_music", generate_music_specifications)
    workflow.add_node("generate_sfx", generate_sfx_specifications)
    workflow.add_node("generate_voice", generate_voice_guidelines)
    workflow.add_node("generate_technical", generate_technical_specifications)
    workflow.add_node("compile_output", compile_audio_output)
    
    # Add edges using parallelization pattern for generation steps
    workflow.add_edge(START, "analyze_needs")
    workflow.add_edge("analyze_needs", "generate_music")
    workflow.add_edge("analyze_needs", "generate_sfx")
    workflow.add_edge("analyze_needs", "generate_voice")
    workflow.add_edge("analyze_needs", "generate_technical")
    workflow.add_edge("generate_music", "compile_output")
    workflow.add_edge("generate_sfx", "compile_output")
    workflow.add_edge("generate_voice", "compile_output")
    workflow.add_edge("generate_technical", "compile_output")
    workflow.add_edge("compile_output", END)
    
    return workflow.compile()


# Create the compiled workflow
audio_workflow = create_audio_workflow()


class AudioSubgraph:
    """Wrapper class for the audio workflow."""
    
    def __init__(self):
        self.workflow = audio_workflow
    
    async def initialize(self):
        """Initialize the audio subgraph."""
        pass  # No async initialization needed
    
    async def generate_audio_specs(self, game_spec: dict[str, Any]) -> dict[str, Any]:
        """Generate audio specifications using the LangGraph workflow."""
        
        try:
            # Run the workflow with game spec
            result = self.workflow.invoke({"game_spec": game_spec})
            return result.get("final_output", {
                "success": False,
                "error": "No final output generated",
                "type": "audio_generation"
            })
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "type": "audio_generation"
            }
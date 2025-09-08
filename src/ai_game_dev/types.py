"""
Type definitions for AI Game Development.
Provides structured types instead of generic dicts.
"""
from typing import Literal, Any
from typing_extensions import TypedDict, NotRequired
from pydantic import BaseModel


class DialogueNode(TypedDict):
    """Structure for a dialogue node in a tree."""
    id: str
    character: str
    text: str
    emotion: NotRequired[str]
    branches: NotRequired[list['DialogueNode']]


class QuestObjective(TypedDict):
    """Structure for a quest objective."""
    id: str
    description: str
    type: Literal["main", "side", "optional"]
    completed: NotRequired[bool]


class Quest(TypedDict):
    """Structure for a quest."""
    id: str
    title: str
    description: str
    objectives: list[QuestObjective]
    rewards: NotRequired[list[str]]
    prerequisites: NotRequired[list[str]]


class GameNarrative(TypedDict):
    """Structure for game narrative."""
    title: str
    setting: str
    protagonist: str
    conflict: str
    resolution: str
    themes: list[str]
    mood: str


class CharacterProfile(TypedDict):
    """Structure for a character profile."""
    name: str
    role: str
    personality: str
    backstory: str
    motivation: str
    dialogue_style: str
    relationships: NotRequired[dict[str, str]]


class LessonObjective(TypedDict):
    """Structure for an educational objective."""
    concept: str
    explanation: str
    example_code: str
    practice_task: str


class LessonPlan(TypedDict):
    """Structure for a lesson plan."""
    title: str
    level: Literal["beginner", "intermediate", "advanced"]
    objectives: list[LessonObjective]
    exercises: list[str]
    assessment: str


class TeachableMoment(TypedDict):
    """Structure for a teachable moment."""
    trigger: str
    concept: str
    explanation: str
    code_example: NotRequired[str]
    interactive: bool


class GameAssets(TypedDict):
    """Structure for game assets."""
    sprites: NotRequired[dict[str, str]]
    backgrounds: NotRequired[dict[str, str]]
    audio: NotRequired[dict[str, str]]
    fonts: NotRequired[dict[str, str]]
    ui: NotRequired[dict[str, str]]


class GameSpec(TypedDict):
    """Structure for a complete game specification."""
    title: str
    engine: Literal["pygame", "godot", "bevy"]
    type: str
    description: str
    mechanics: list[str]
    features: list[str]
    assets: NotRequired[GameAssets]
    characters: NotRequired[list[str]]
    levels: NotRequired[list[str]]
    dialogue: NotRequired[dict[str, str]]
    ui: NotRequired[dict[str, str]]
    educational: NotRequired[dict[str, Any]]


class CodeRepository(TypedDict):
    """Structure for generated code repository."""
    files: dict[str, str]  # filename -> content
    structure: dict[str, list[str]]  # directory -> files
    readme: str
    requirements: NotRequired[str]
    build_instructions: NotRequired[list[str]]


# Pydantic models for stricter validation
class DialogueNodeModel(BaseModel):
    """Pydantic model for dialogue validation."""
    id: str
    character: str
    text: str
    emotion: str | None = None
    branches: list['DialogueNodeModel'] | None = None


class QuestModel(BaseModel):
    """Pydantic model for quest validation."""
    id: str
    title: str
    description: str
    objectives: list[QuestObjective]
    rewards: list[str] = []
    prerequisites: list[str] = []


class GameNarrativeModel(BaseModel):
    """Pydantic model for narrative validation."""
    title: str
    setting: str
    protagonist: str
    conflict: str
    resolution: str
    themes: list[str]
    mood: str


# Update forward references
DialogueNodeModel.model_rebuild()
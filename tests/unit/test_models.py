"""Test Pydantic models and schemas."""
import pytest
from pydantic import ValidationError
from ai_game_dev.models import (
    GameSpec,
    GameProject,
    ProjectFile,
    GameEngine,
    GameType,
    ComplexityLevel,
    GameFeature,
    AssetRequirement,
    NPCCharacter,
    DialogueNode,
    QuestObjective,
    GameWorld,
    EngineConfig
)


class TestGameProject:
    """Test GameProject model."""

    def test_valid_game_project(self):
        """Test creating valid game project."""
        project = GameProject(
            name="Test Game",
            description="A test game",
            genre="Action",
            target_platform="PC",
            engine="pygame"
        )
        
        assert project.name == "Test Game"
        assert project.description == "A test game"
        assert project.genre == "Action"
        assert project.target_platform == "PC"
        assert project.engine == "pygame"

    def test_game_project_with_features(self):
        """Test game project with features."""
        feature = GameFeature(
            name="Combat System",
            description="Real-time combat",
            priority="high"
        )
        
        project = GameProject(
            name="RPG Game",
            description="Role-playing game",
            genre="RPG",
            target_platform="PC",
            engine="pygame",
            features=[feature]
        )
        
        assert len(project.features) == 1
        assert project.features[0].name == "Combat System"

    def test_game_project_required_fields(self):
        """Test game project with missing required fields."""
        with pytest.raises(ValidationError) as exc_info:
            GameProject(
                description="Missing name",
                genre="Action"
            )
        
        assert "name" in str(exc_info.value)

    def test_game_project_invalid_engine(self):
        """Test game project with invalid engine."""
        with pytest.raises(ValidationError) as exc_info:
            GameProject(
                name="Test Game",
                description="Test",
                genre="Action",
                target_platform="PC",
                engine="invalid_engine"
            )
        
        assert "engine" in str(exc_info.value)


class TestGameFeature:
    """Test GameFeature model."""

    def test_valid_game_feature(self):
        """Test creating valid game feature."""
        feature = GameFeature(
            name="Inventory System",
            description="Player inventory management",
            priority="medium"
        )
        
        assert feature.name == "Inventory System"
        assert feature.description == "Player inventory management"
        assert feature.priority == "medium"

    def test_game_feature_invalid_priority(self):
        """Test game feature with invalid priority."""
        with pytest.raises(ValidationError) as exc_info:
            GameFeature(
                name="Test Feature",
                description="Test description",
                priority="invalid_priority"
            )
        
        assert "priority" in str(exc_info.value)


class TestAssetRequirement:
    """Test AssetRequirement model."""

    def test_valid_asset_requirement(self):
        """Test creating valid asset requirement."""
        asset = AssetRequirement(
            asset_type="sprite",
            name="Player Character",
            description="Main character sprite",
            quantity=1
        )
        
        assert asset.asset_type == "sprite"
        assert asset.name == "Player Character"
        assert asset.quantity == 1

    def test_asset_requirement_invalid_quantity(self):
        """Test asset requirement with invalid quantity."""
        with pytest.raises(ValidationError) as exc_info:
            AssetRequirement(
                asset_type="sprite",
                name="Test Asset",
                description="Test",
                quantity=-1
            )
        
        assert "quantity" in str(exc_info.value)


class TestNPCCharacter:
    """Test NPCCharacter model."""

    def test_valid_npc_character(self):
        """Test creating valid NPC character."""
        npc = NPCCharacter(
            name="Village Elder",
            role="Quest Giver",
            personality="Wise and helpful",
            appearance="Old man with grey beard",
            location="Village Center"
        )
        
        assert npc.name == "Village Elder"
        assert npc.role == "Quest Giver"
        assert npc.personality == "Wise and helpful"

    def test_npc_with_dialogue(self):
        """Test NPC with dialogue nodes."""
        dialogue = DialogueNode(
            text="Welcome, traveler!",
            speaker="Village Elder",
            options=["Hello!", "I need help"]
        )
        
        npc = NPCCharacter(
            name="Village Elder",
            role="Quest Giver",
            personality="Wise",
            appearance="Old man",
            location="Village",
            dialogue=[dialogue]
        )
        
        assert len(npc.dialogue) == 1
        assert npc.dialogue[0].text == "Welcome, traveler!"


class TestDialogueNode:
    """Test DialogueNode model."""

    def test_valid_dialogue_node(self):
        """Test creating valid dialogue node."""
        dialogue = DialogueNode(
            text="Hello there!",
            speaker="NPC",
            options=["Hi!", "Goodbye"]
        )
        
        assert dialogue.text == "Hello there!"
        assert dialogue.speaker == "NPC"
        assert len(dialogue.options) == 2

    def test_dialogue_node_empty_options(self):
        """Test dialogue node with empty options."""
        dialogue = DialogueNode(
            text="Farewell!",
            speaker="NPC",
            options=[]
        )
        
        assert len(dialogue.options) == 0


class TestQuestObjective:
    """Test QuestObjective model."""

    def test_valid_quest_objective(self):
        """Test creating valid quest objective."""
        objective = QuestObjective(
            title="Collect Ancient Artifact",
            description="Find the lost artifact in the ancient ruins",
            type="collection",
            target="Ancient Artifact",
            quantity=1
        )
        
        assert objective.title == "Collect Ancient Artifact"
        assert objective.type == "collection"
        assert objective.quantity == 1
        assert not objective.completed

    def test_quest_objective_completion(self):
        """Test quest objective completion."""
        objective = QuestObjective(
            title="Defeat Boss",
            description="Defeat the final boss",
            type="combat",
            target="Final Boss",
            quantity=1,
            completed=True
        )
        
        assert objective.completed


class TestGameWorld:
    """Test GameWorld model."""

    def test_valid_game_world(self):
        """Test creating valid game world."""
        npc = NPCCharacter(
            name="Shop Keeper",
            role="Vendor",
            personality="Friendly",
            appearance="Middle-aged woman",
            location="Shop"
        )
        
        objective = QuestObjective(
            title="Buy Sword",
            description="Purchase a weapon",
            type="interaction",
            target="Shop Keeper",
            quantity=1
        )
        
        world = GameWorld(
            name="Fantasy Kingdom",
            description="A magical medieval world",
            setting="Medieval Fantasy",
            locations=["Castle", "Village", "Forest"],
            npcs=[npc],
            quests=[objective]
        )
        
        assert world.name == "Fantasy Kingdom"
        assert len(world.locations) == 3
        assert len(world.npcs) == 1
        assert len(world.quests) == 1

    def test_game_world_empty_lists(self):
        """Test game world with empty lists."""
        world = GameWorld(
            name="Empty World",
            description="An empty world",
            setting="Void",
            locations=[],
            npcs=[],
            quests=[]
        )
        
        assert len(world.locations) == 0
        assert len(world.npcs) == 0
        assert len(world.quests) == 0


class TestEngineConfig:
    """Test EngineConfig model."""

    def test_valid_engine_config(self):
        """Test creating valid engine config."""
        config = EngineConfig(
            engine="pygame",
            resolution="1920x1080",
            fps=60,
            fullscreen=False,
            vsync=True
        )
        
        assert config.engine == "pygame"
        assert config.resolution == "1920x1080"
        assert config.fps == 60
        assert not config.fullscreen
        assert config.vsync

    def test_engine_config_defaults(self):
        """Test engine config with default values."""
        config = EngineConfig(
            engine="pygame"
        )
        
        assert config.resolution == "1280x720"
        assert config.fps == 60
        assert not config.fullscreen
        assert not config.vsync

    def test_engine_config_invalid_engine(self):
        """Test engine config with invalid engine."""
        with pytest.raises(ValidationError) as exc_info:
            EngineConfig(
                engine="invalid_engine"
            )
        
        assert "engine" in str(exc_info.value)

    def test_engine_config_invalid_fps(self):
        """Test engine config with invalid fps."""
        with pytest.raises(ValidationError) as exc_info:
            EngineConfig(
                engine="pygame",
                fps=0
            )
        
        assert "fps" in str(exc_info.value)
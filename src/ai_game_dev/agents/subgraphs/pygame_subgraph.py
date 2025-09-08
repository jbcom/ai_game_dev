"""
Pygame Engine Subgraph
Generates complete Pygame games from specifications
"""
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from langchain_core.messages import HumanMessage
from langgraph.graph import END, StateGraph

from ai_game_dev.agents.base_agent import AgentConfig, BaseAgent


@dataclass
class PygameState:
    """State for Pygame game generation."""
    game_spec: dict[str, Any] = field(default_factory=dict)
    generated_files: dict[str, str] = field(default_factory=dict)
    main_file: str = ""
    assets_config: dict[str, Any] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)
    complete: bool = False


class PygameSubgraph(BaseAgent):
    """
    Subgraph for generating Pygame games.
    
    Handles:
    - Game loop generation
    - Sprite management
    - Event handling
    - Asset integration
    - Educational annotations
    """
    
    def __init__(self):
        config = AgentConfig(
            model="gpt-4o",
            temperature=0.2,
            instructions=self._get_pygame_instructions()
        )
        super().__init__(config)
        self.graph = None
    
    def _get_pygame_instructions(self) -> str:
        return """You are a Pygame game development expert.
        
        Generate complete, playable Pygame games with:
        1. Clean, well-structured code
        2. Proper game loop with FPS control
        3. Sprite and sprite group management
        4. Event handling for keyboard/mouse
        5. Asset loading and management
        6. Educational comments for learning
        
        Follow Pygame best practices:
        - Use pygame.sprite.Group for entity management
        - Implement proper collision detection
        - Handle game states (menu, playing, game over)
        - Include sound and music support
        - Make games resolution-independent
        """
    
    async def initialize(self):
        """Initialize the Pygame subgraph."""
        await super().initialize()
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build the Pygame generation workflow."""
        workflow = StateGraph(PygameState)
        
        # Add nodes
        workflow.add_node("analyze_spec", self._analyze_spec)
        workflow.add_node("generate_structure", self._generate_structure)
        workflow.add_node("generate_main", self._generate_main)
        workflow.add_node("generate_entities", self._generate_entities)
        workflow.add_node("generate_scenes", self._generate_scenes)
        workflow.add_node("generate_config", self._generate_config)
        workflow.add_node("validate_code", self._validate_code)
        
        # Add edges
        workflow.set_entry_point("analyze_spec")
        workflow.add_edge("analyze_spec", "generate_structure")
        workflow.add_edge("generate_structure", "generate_main")
        workflow.add_edge("generate_main", "generate_entities")
        workflow.add_edge("generate_entities", "generate_scenes")
        workflow.add_edge("generate_scenes", "generate_config")
        workflow.add_edge("generate_config", "validate_code")
        workflow.add_edge("validate_code", END)
        
        return workflow.compile()
    
    async def _analyze_spec(self, state: PygameState) -> PygameState:
        """Analyze game specification for Pygame requirements."""
        spec = state.game_spec
        
        # Extract key features for Pygame
        features = spec.get("features", [])
        
        # Determine required components
        state.assets_config = {
            "needs_sprites": any(f in features for f in ["sprites", "characters", "enemies"]),
            "needs_audio": "audio" in features or "music" in features,
            "needs_physics": "physics" in features,
            "needs_ui": "menu" in features or "ui" in features,
            "screen_size": spec.get("resolution", "1280x720"),
            "fps": spec.get("fps_target", 60)
        }
        
        return state
    
    async def _generate_structure(self, state: PygameState) -> PygameState:
        """Generate project structure."""
        state.generated_files = {
            "main.py": "",
            "game/__init__.py": "",
            "game/entities.py": "",
            "game/scenes.py": "",
            "game/utils.py": "",
            "game/config.py": "",
            "assets/README.md": "# Game Assets\nPlace sprites, sounds, and fonts here.",
            "requirements.txt": "pygame>=2.5.0\n"
        }
        return state
    
    async def _generate_main(self, state: PygameState) -> PygameState:
        """Generate main game file."""
        spec = state.game_spec
        title = spec.get("title", "Pygame Game")
        
        main_code = f'''#!/usr/bin/env python3
"""
{title}
{spec.get("description", "A Pygame game")}
"""

import pygame
import sys
from pathlib import Path

# Add game directory to path
sys.path.insert(0, str(Path(__file__).parent))

from game.config import Config
from game.scenes import MenuScene, GameScene


class Game:
    """Main game class."""
    
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        
        self.config = Config()
        self.screen = pygame.display.set_mode(self.config.SCREEN_SIZE)
        pygame.display.set_caption("{title}")
        
        self.clock = pygame.time.Clock()
        self.running = True
        self.current_scene = MenuScene(self)
        
    def handle_events(self):
        """Process pygame events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            else:
                self.current_scene.handle_event(event)
    
    def update(self, dt):
        """Update game state."""
        self.current_scene.update(dt)
        
        # Handle scene transitions
        next_scene = self.current_scene.next_scene
        if next_scene:
            self.current_scene = next_scene
    
    def draw(self):
        """Draw everything."""
        self.screen.fill(self.config.BACKGROUND_COLOR)
        self.current_scene.draw(self.screen)
        pygame.display.flip()
    
    def run(self):
        """Main game loop."""
        while self.running:
            dt = self.clock.tick(self.config.FPS) / 1000.0
            
            self.handle_events()
            self.update(dt)
            self.draw()
        
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = Game()
    game.run()
'''
        
        state.generated_files["main.py"] = main_code
        state.main_file = "main.py"
        return state
    
    async def _generate_entities(self, state: PygameState) -> PygameState:
        """Generate entity classes."""
        spec = state.game_spec
        
        entities_code = '''"""Game entities and sprites."""

import pygame
from pygame.sprite import Sprite, Group


class Player(Sprite):
    """Player character sprite."""
    
    def __init__(self, x, y):
        super().__init__()
        
        # Create a simple colored rectangle for now
        self.image = pygame.Surface((32, 32))
        self.image.fill((0, 255, 0))  # Green player
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
        # Movement
        self.velocity = pygame.Vector2(0, 0)
        self.speed = 300  # pixels per second
        
    def update(self, dt):
        """Update player state."""
        # Get keyboard input
        keys = pygame.key.get_pressed()
        
        # Calculate movement
        self.velocity.x = 0
        self.velocity.y = 0
        
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.velocity.x = -self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.velocity.x = self.speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.velocity.y = -self.speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.velocity.y = self.speed
        
        # Apply movement
        self.rect.x += self.velocity.x * dt
        self.rect.y += self.velocity.y * dt
        
        # Keep on screen
        self.rect.clamp_ip(pygame.display.get_surface().get_rect())


class Enemy(Sprite):
    """Basic enemy sprite."""
    
    def __init__(self, x, y):
        super().__init__()
        
        self.image = pygame.Surface((24, 24))
        self.image.fill((255, 0, 0))  # Red enemy
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
    def update(self, dt):
        """Update enemy behavior."""
        # Simple movement pattern
        pass
'''
        
        state.generated_files["game/entities.py"] = entities_code
        return state
    
    async def _generate_scenes(self, state: PygameState) -> PygameState:
        """Generate scene management."""
        scenes_code = '''"""Game scenes and states."""

import pygame
from game.entities import Player, Enemy


class Scene:
    """Base scene class."""
    
    def __init__(self, game):
        self.game = game
        self.next_scene = None
        
    def handle_event(self, event):
        """Process input events."""
        pass
        
    def update(self, dt):
        """Update scene logic."""
        pass
        
    def draw(self, screen):
        """Draw the scene."""
        pass


class MenuScene(Scene):
    """Main menu scene."""
    
    def __init__(self, game):
        super().__init__(game)
        self.font = pygame.font.Font(None, 74)
        self.title_text = self.font.render("Pygame Game", True, (255, 255, 255))
        self.title_rect = self.title_text.get_rect(center=(640, 200))
        
        self.font_small = pygame.font.Font(None, 36)
        self.start_text = self.font_small.render("Press SPACE to Start", True, (255, 255, 255))
        self.start_rect = self.start_text.get_rect(center=(640, 400))
        
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                self.next_scene = GameScene(self.game)
    
    def draw(self, screen):
        screen.blit(self.title_text, self.title_rect)
        screen.blit(self.start_text, self.start_rect)


class GameScene(Scene):
    """Main gameplay scene."""
    
    def __init__(self, game):
        super().__init__(game)
        
        # Create sprite groups
        self.all_sprites = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        
        # Create player
        self.player = Player(640, 360)
        self.all_sprites.add(self.player)
        
        # Create some enemies
        for i in range(5):
            enemy = Enemy(100 + i * 150, 100)
            self.all_sprites.add(enemy)
            self.enemies.add(enemy)
    
    def update(self, dt):
        self.all_sprites.update(dt)
        
        # Check collisions
        hits = pygame.sprite.spritecollide(self.player, self.enemies, True)
        for hit in hits:
            # Handle collision
            pass
    
    def draw(self, screen):
        self.all_sprites.draw(screen)
'''
        
        state.generated_files["game/scenes.py"] = scenes_code
        return state
    
    async def _generate_config(self, state: PygameState) -> PygameState:
        """Generate configuration file."""
        config = state.assets_config
        
        config_code = f'''"""Game configuration and constants."""

import pygame


class Config:
    """Game configuration."""
    
    # Display
    SCREEN_SIZE = ({config.get("screen_size", "1280, 720")})
    FPS = {config.get("fps", 60)}
    BACKGROUND_COLOR = (20, 20, 30)
    
    # Game settings
    PLAYER_SPEED = 300
    ENEMY_SPEED = 150
    
    # Asset paths
    ASSETS_DIR = "assets"
    SPRITES_DIR = "assets/sprites"
    SOUNDS_DIR = "assets/sounds"
    FONTS_DIR = "assets/fonts"
'''
        
        state.generated_files["game/config.py"] = config_code
        state.generated_files["game/__init__.py"] = '"""Game package."""\n'
        state.generated_files["game/utils.py"] = '''"""Utility functions."""

import pygame
from pathlib import Path


def load_image(path, scale=None):
    """Load and optionally scale an image."""
    image = pygame.image.load(path)
    if scale:
        image = pygame.transform.scale(image, scale)
    return image


def load_sound(path):
    """Load a sound effect."""
    return pygame.mixer.Sound(path)
'''
        
        return state
    
    async def _validate_code(self, state: PygameState) -> PygameState:
        """Validate generated code."""
        # Basic validation
        if not state.generated_files:
            state.errors.append("No files generated")
        elif "main.py" not in state.generated_files:
            state.errors.append("Missing main.py")
        else:
            state.complete = True
        
        return state
    
    async def process(self, inputs: dict[str, Any]) -> dict[str, Any]:
        """Process Pygame generation request."""
        initial_state = PygameState(
            game_spec=inputs.get("game_spec", inputs)
        )
        
        # Run the graph
        final_state = await self.graph.ainvoke(initial_state)
        
        return {
            "success": final_state.complete,
            "files": final_state.generated_files,
            "main_file": final_state.main_file,
            "errors": final_state.errors,
            "engine": "pygame"
        }
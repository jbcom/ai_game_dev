"""
NeoTokyo Code Academy: The Binary Rebellion
A cyberpunk educational RPG for learning Python game development
"""

import pygame
import sys
import json
import random
from enum import Enum
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple

# Initialize Pygame
pygame.init()

# Game Constants
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60
TILE_SIZE = 32

# Colors (Cyberpunk theme)
NEON_BLUE = (0, 255, 255)
NEON_PINK = (255, 20, 147)
DARK_BG = (10, 10, 25)
UI_DARK = (20, 20, 40)
TEXT_WHITE = (255, 255, 255)
HEALTH_RED = (255, 50, 50)
MANA_BLUE = (50, 150, 255)


class GameState(Enum):
    """Game state management for educational flow."""
    MAIN_MENU = "main_menu"
    CHAR_SELECT = "character_select"
    GAMEPLAY = "gameplay"
    COMBAT = "combat"
    INVENTORY = "inventory"
    DIALOGUE = "dialogue"
    CHAPTER_INTRO = "chapter_intro"


@dataclass
class CharacterClass:
    """Character class definitions for educational RPG."""
    name: str
    description: str
    base_health: int
    base_mana: int
    base_attack: int
    base_defense: int
    base_speed: int
    abilities: List[str]
    learns_concepts: List[str]


# Character Classes from our specification
CHARACTER_CLASSES = {
    "code_knight": CharacterClass(
        name="Code Knight",
        description="Cybernetic warrior defending with object-oriented mastery",
        base_health=120, base_mana=60, base_attack=15, base_defense=18, base_speed=8,
        abilities=["Neural Shield", "Class Strike", "Inheritance Wall", "Polymorphic Slash"],
        learns_concepts=["OOP", "Classes", "Inheritance", "Polymorphism"]
    ),
    "data_sage": CharacterClass(
        name="Data Sage", 
        description="Mystical hacker manipulating digital reality structures",
        base_health=85, base_mana=180, base_attack=10, base_defense=8, base_speed=12,
        abilities=["Neon List Storm", "Dictionary Heal Matrix", "Quantum Sort", "Algorithm Singularity"],
        learns_concepts=["Data Structures", "Algorithms", "Complexity", "Recursion"]
    ),
    "bug_hunter": CharacterClass(
        name="Bug Hunter",
        description="Agile cyber-assassin hunting code corruption",
        base_health=100, base_mana=90, base_attack=16, base_defense=10, base_speed=18,
        abilities=["Exception Shuriken", "Try-Catch Phantom Step", "Assert Snare", "Stack Trace Vision"],
        learns_concepts=["Error Handling", "Debugging", "Testing", "Logging"]
    ),
    "web_weaver": CharacterClass(
        name="Web Weaver",
        description="Digital architect crafting immersive virtual worlds", 
        base_health=95, base_mana=120, base_attack=12, base_defense=9, base_speed=14,
        abilities=["HTML Reality Shift", "CSS Hologram", "JavaScript Lightning", "API Portal"],
        learns_concepts=["Web Dev", "APIs", "Frameworks", "UI/UX"]
    )
}


class Player:
    """Player character with stats and progression."""
    
    def __init__(self, character_class: CharacterClass):
        self.character_class = character_class
        self.level = 1
        self.experience = 0
        self.health = character_class.base_health
        self.max_health = character_class.base_health
        self.mana = character_class.base_mana
        self.max_mana = character_class.base_mana
        self.attack = character_class.base_attack
        self.defense = character_class.base_defense
        self.speed = character_class.base_speed
        
        # Position in the world
        self.x = SCREEN_WIDTH // 2
        self.y = SCREEN_HEIGHT // 2
        
        # Inventory and progression
        self.inventory = []
        self.learned_concepts = []
        self.current_chapter = 1
        
    def gain_experience(self, amount: int):
        """Gain experience points and handle leveling up."""
        self.experience += amount
        # Simple leveling: need level * 100 XP for next level
        exp_needed = self.level * 100
        
        if self.experience >= exp_needed:
            self.level_up()
    
    def level_up(self):
        """Level up the character and increase stats."""
        self.level += 1
        self.experience = 0  # Reset for next level
        
        # Stat growth
        self.max_health += 8
        self.max_mana += 5
        self.attack += 3
        self.defense += 2
        self.speed += 2
        
        # Restore health and mana on level up
        self.health = self.max_health
        self.mana = self.max_mana
        
        print(f"Level up! {self.character_class.name} is now level {self.level}")


class CyberUI:
    """Cyberpunk-themed UI system for educational game."""
    
    def __init__(self, screen):
        self.screen = screen
        self.font_small = pygame.font.Font(None, 24)
        self.font_medium = pygame.font.Font(None, 32)
        self.font_large = pygame.font.Font(None, 48)
        
    def draw_neon_rect(self, rect: pygame.Rect, color: Tuple[int, int, int], width: int = 2):
        """Draw a glowing neon rectangle border."""
        pygame.draw.rect(self.screen, color, rect, width)
        # Add glow effect
        for i in range(3):
            glow_rect = rect.inflate(i*2, i*2)
            glow_color = tuple(max(0, c - i*50) for c in color)
            pygame.draw.rect(self.screen, glow_color, glow_rect, 1)
    
    def draw_health_bar(self, x: int, y: int, current: int, maximum: int):
        """Draw cyberpunk-style health bar."""
        bar_width = 200
        bar_height = 20
        
        # Background
        bg_rect = pygame.Rect(x, y, bar_width, bar_height)
        pygame.draw.rect(self.screen, UI_DARK, bg_rect)
        
        # Health fill
        health_percent = current / maximum
        fill_width = int(bar_width * health_percent)
        fill_rect = pygame.Rect(x, y, fill_width, bar_height)
        pygame.draw.rect(self.screen, HEALTH_RED, fill_rect)
        
        # Neon border
        self.draw_neon_rect(bg_rect, NEON_BLUE, 2)
        
        # Text
        text = f"HP: {current}/{maximum}"
        text_surface = self.font_small.render(text, True, TEXT_WHITE)
        self.screen.blit(text_surface, (x + 5, y + 2))
    
    def draw_mana_bar(self, x: int, y: int, current: int, maximum: int):
        """Draw cyberpunk-style mana bar."""
        bar_width = 200
        bar_height = 20
        
        # Background
        bg_rect = pygame.Rect(x, y, bar_width, bar_height)
        pygame.draw.rect(self.screen, UI_DARK, bg_rect)
        
        # Mana fill
        mana_percent = current / maximum
        fill_width = int(bar_width * mana_percent)
        fill_rect = pygame.Rect(x, y, fill_width, bar_height)
        pygame.draw.rect(self.screen, MANA_BLUE, fill_rect)
        
        # Neon border
        self.draw_neon_rect(bg_rect, NEON_PINK, 2)
        
        # Text
        text = f"MP: {current}/{maximum}"
        text_surface = self.font_small.render(text, True, TEXT_WHITE)
        self.screen.blit(text_surface, (x + 5, y + 2))
    
    def draw_dialogue_box(self, speaker: str, text: str):
        """Draw Professor Pixel dialogue box."""
        dialog_rect = pygame.Rect(50, SCREEN_HEIGHT - 200, SCREEN_WIDTH - 100, 150)
        
        # Background with transparency effect
        dialog_surface = pygame.Surface((dialog_rect.width, dialog_rect.height))
        dialog_surface.set_alpha(220)
        dialog_surface.fill(UI_DARK)
        self.screen.blit(dialog_surface, dialog_rect.topleft)
        
        # Neon border
        self.draw_neon_rect(dialog_rect, NEON_BLUE, 3)
        
        # Speaker name
        speaker_text = self.font_medium.render(speaker, True, NEON_PINK)
        self.screen.blit(speaker_text, (dialog_rect.x + 20, dialog_rect.y + 10))
        
        # Dialogue text (with word wrapping)
        words = text.split(' ')
        lines = []
        current_line = ""
        
        for word in words:
            test_line = current_line + " " + word if current_line else word
            if self.font_small.size(test_line)[0] < dialog_rect.width - 40:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word
        lines.append(current_line)
        
        for i, line in enumerate(lines[:4]):  # Max 4 lines
            line_surface = self.font_small.render(line, True, TEXT_WHITE)
            self.screen.blit(line_surface, (dialog_rect.x + 20, dialog_rect.y + 50 + i * 25))


class Game:
    """Main game class managing all systems."""
    
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("NeoTokyo Code Academy: The Binary Rebellion")
        self.clock = pygame.time.Clock()
        self.running = True
        
        self.state = GameState.MAIN_MENU
        self.player = None
        self.ui = CyberUI(self.screen)
        
        # Educational tracking
        self.current_chapter = 1
        self.dialogue_active = False
        self.current_speaker = ""
        self.current_dialogue = ""
        
    def handle_events(self):
        """Handle pygame events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                if self.state == GameState.MAIN_MENU:
                    if event.key == pygame.K_RETURN:
                        self.state = GameState.CHAR_SELECT
                
                elif self.state == GameState.CHAR_SELECT:
                    if event.key == pygame.K_1:
                        self.create_player("code_knight")
                    elif event.key == pygame.K_2:
                        self.create_player("data_sage")
                    elif event.key == pygame.K_3:
                        self.create_player("bug_hunter")
                    elif event.key == pygame.K_4:
                        self.create_player("web_weaver")
                
                elif self.state == GameState.DIALOGUE:
                    if event.key == pygame.K_SPACE:
                        self.dialogue_active = False
                        self.state = GameState.GAMEPLAY
                
                elif self.state == GameState.GAMEPLAY:
                    self.handle_gameplay_input(event.key)
    
    def create_player(self, class_key: str):
        """Create player character and start the game."""
        character_class = CHARACTER_CLASSES[class_key]
        self.player = Player(character_class)
        self.start_chapter_intro()
    
    def start_chapter_intro(self):
        """Start educational chapter with Professor Pixel."""
        self.state = GameState.DIALOGUE
        self.dialogue_active = True
        self.current_speaker = "Professor Pixel"
        
        chapter_intros = {
            1: "Welcome to the real world, rookie. See that pretty interface the Empire gives you? It's a cage. Let's start with something simple - creating your first game window.",
            2: "Now we breathe life into our world with sprites! Watch how a few lines of code can create animated characters moving through digital space.",
            3: "Movement and collision - the physics of our digital universe. See how we make characters interact with their environment!"
        }
        
        self.current_dialogue = chapter_intros.get(self.current_chapter, "Ready for the next lesson?")
    
    def handle_gameplay_input(self, key):
        """Handle movement and gameplay input."""
        if not self.player:
            return
            
        move_speed = 5
        
        if key == pygame.K_LEFT or key == pygame.K_a:
            self.player.x = max(0, self.player.x - move_speed)
        elif key == pygame.K_RIGHT or key == pygame.K_d:
            self.player.x = min(SCREEN_WIDTH - 32, self.player.x + move_speed)
        elif key == pygame.K_UP or key == pygame.K_w:
            self.player.y = max(0, self.player.y - move_speed)
        elif key == pygame.K_DOWN or key == pygame.K_s:
            self.player.y = min(SCREEN_HEIGHT - 32, self.player.y + move_speed)
        elif key == pygame.K_RETURN:
            # Next chapter
            self.current_chapter += 1
            self.start_chapter_intro()
    
    def update(self):
        """Update game state."""
        if self.state == GameState.GAMEPLAY and self.player:
            # Simple XP gain for movement (educational: showing variables changing)
            if random.randint(1, 120) == 1:  # Rare XP gain
                self.player.gain_experience(10)
    
    def render(self):
        """Render the current game state."""
        self.screen.fill(DARK_BG)
        
        if self.state == GameState.MAIN_MENU:
            self.render_main_menu()
        elif self.state == GameState.CHAR_SELECT:
            self.render_character_select()
        elif self.state == GameState.GAMEPLAY:
            self.render_gameplay()
        elif self.state == GameState.DIALOGUE:
            self.render_dialogue()
        
        pygame.display.flip()
    
    def render_main_menu(self):
        """Render cyberpunk main menu."""
        title_text = self.ui.font_large.render("NeoTokyo Code Academy", True, NEON_BLUE)
        subtitle_text = self.ui.font_medium.render("The Binary Rebellion", True, NEON_PINK)
        start_text = self.ui.font_medium.render("Press ENTER to begin your journey", True, TEXT_WHITE)
        
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH//2, 200))
        subtitle_rect = subtitle_text.get_rect(center=(SCREEN_WIDTH//2, 250))
        start_rect = start_text.get_rect(center=(SCREEN_WIDTH//2, 400))
        
        self.screen.blit(title_text, title_rect)
        self.screen.blit(subtitle_text, subtitle_rect)
        self.screen.blit(start_text, start_rect)
        
        # Add some cyberpunk flair
        for i in range(5):
            x = random.randint(0, SCREEN_WIDTH)
            y = random.randint(0, SCREEN_HEIGHT)
            pygame.draw.circle(self.screen, NEON_BLUE, (x, y), 1)
    
    def render_character_select(self):
        """Render character class selection."""
        title_text = self.ui.font_large.render("Choose Your Path", True, NEON_PINK)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH//2, 100))
        self.screen.blit(title_text, title_rect)
        
        y_start = 200
        for i, (key, char_class) in enumerate(CHARACTER_CLASSES.items()):
            y_pos = y_start + i * 80
            
            # Class selection box
            class_rect = pygame.Rect(200, y_pos, 880, 60)
            self.ui.draw_neon_rect(class_rect, NEON_BLUE, 2)
            
            # Class info
            number_text = self.ui.font_medium.render(f"{i+1}.", True, NEON_PINK)
            name_text = self.ui.font_medium.render(char_class.name, True, TEXT_WHITE)
            desc_text = self.ui.font_small.render(char_class.description, True, TEXT_WHITE)
            concepts_text = self.ui.font_small.render(f"Learns: {', '.join(char_class.learns_concepts)}", True, NEON_BLUE)
            
            self.screen.blit(number_text, (class_rect.x + 10, y_pos + 5))
            self.screen.blit(name_text, (class_rect.x + 50, y_pos + 5))
            self.screen.blit(desc_text, (class_rect.x + 50, y_pos + 25))
            self.screen.blit(concepts_text, (class_rect.x + 50, y_pos + 45))
    
    def render_gameplay(self):
        """Render main gameplay view."""
        # Simple grid background
        for x in range(0, SCREEN_WIDTH, TILE_SIZE):
            pygame.draw.line(self.screen, (30, 30, 50), (x, 0), (x, SCREEN_HEIGHT))
        for y in range(0, SCREEN_HEIGHT, TILE_SIZE):
            pygame.draw.line(self.screen, (30, 30, 50), (0, y), (SCREEN_WIDTH, y))
        
        # Draw player (simple rectangle for now)
        if self.player:
            player_rect = pygame.Rect(self.player.x, self.player.y, TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(self.screen, NEON_PINK, player_rect)
            
            # Draw UI
            self.ui.draw_health_bar(20, 20, self.player.health, self.player.max_health)
            self.ui.draw_mana_bar(20, 50, self.player.mana, self.player.max_mana)
            
            # Level and XP
            level_text = self.ui.font_medium.render(f"Level {self.player.level}", True, TEXT_WHITE)
            xp_text = self.ui.font_small.render(f"XP: {self.player.experience}/{self.player.level * 100}", True, TEXT_WHITE)
            chapter_text = self.ui.font_small.render(f"Chapter {self.current_chapter}", True, NEON_BLUE)
            
            self.screen.blit(level_text, (20, 90))
            self.screen.blit(xp_text, (20, 120))
            self.screen.blit(chapter_text, (20, 140))
            
            # Instructions
            instruction_text = self.ui.font_small.render("Use WASD/Arrows to move, ENTER for next chapter", True, TEXT_WHITE)
            self.screen.blit(instruction_text, (20, SCREEN_HEIGHT - 30))
    
    def render_dialogue(self):
        """Render dialogue overlay."""
        # First render the gameplay background
        self.render_gameplay()
        
        # Then add dialogue overlay
        if self.dialogue_active:
            self.ui.draw_dialogue_box(self.current_speaker, self.current_dialogue)
            
            # Continue prompt
            continue_text = self.ui.font_small.render("Press SPACE to continue", True, NEON_PINK)
            continue_rect = continue_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT - 20))
            self.screen.blit(continue_text, continue_rect)
    
    def run(self):
        """Main game loop."""
        while self.running:
            self.handle_events()
            self.update()
            self.render()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()


def main():
    """Entry point for the educational RPG."""
    print("🎮 Starting NeoTokyo Code Academy: The Binary Rebellion")
    print("🎓 Educational Python Game Development RPG")
    
    game = Game()
    game.run()


if __name__ == "__main__":
    main()

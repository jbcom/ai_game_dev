#!/usr/bin/env python3
"""
Pygame Tower Defense Example
Demonstrates AI-powered game development with pygame_game_dev
"""

import pygame
import sys
from pathlib import Path

# Add the workspace packages to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "packages"))

try:
    from pygame_game_dev import generate_pygame_project, GameSpec, GameType, ComplexityLevel
    from ai_game_dev import AIGameDev
    from ai_game_assets import AssetGenerator
except ImportError as e:
    print(f"Please install the AI Game Dev packages: {e}")
    sys.exit(1)


def create_tower_defense_game():
    """Generate a complete tower defense game using AI."""
    
    # Define game specification
    spec = GameSpec(
        name="AI Tower Defense",
        description="A strategic tower defense game with AI-generated assets",
        game_type=GameType.TWO_DIMENSIONAL,
        features=[
            "Multiple tower types",
            "Enemy waves with different behaviors", 
            "Upgrade system",
            "Score tracking",
            "Particle effects"
        ],
        complexity=ComplexityLevel.INTERMEDIATE
    )
    
    print("🎮 Generating Tower Defense game...")
    
    # Generate the pygame project structure
    project = generate_pygame_project(spec)
    
    # Initialize AI systems
    game_dev = AIGameDev()
    asset_gen = AssetGenerator()
    
    print("🎨 Generating game assets...")
    
    # Generate game assets
    assets = {
        "tower_sprites": asset_gen.generate_image(
            "Pixel art tower sprites for tower defense game, multiple types",
            style="pixel_art"
        ),
        "enemy_sprites": asset_gen.generate_image(
            "Pixel art enemy sprites, various types and sizes",
            style="pixel_art" 
        ),
        "background_music": asset_gen.generate_audio(
            "Epic orchestral background music for tower defense game",
            duration=120
        ),
        "sound_effects": asset_gen.generate_audio(
            "Tower shooting and explosion sound effects",
            duration=2
        )
    }
    
    print("📁 Project structure created:")
    print(f"Main file: {len(project.main_py)} characters")
    print(f"Game logic: {len(project.game_py)} characters") 
    print(f"Player system: {len(project.player_py)} characters")
    print(f"Constants: {len(project.constants_py)} characters")
    print(f"Assets generated: {len(assets)} items")
    
    return project, assets


class TowerDefenseDemo:
    """Interactive demo of the generated tower defense game."""
    
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("AI Generated Tower Defense Demo")
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Demo state
        self.towers = []
        self.enemies = []
        self.score = 0
        
    def run_demo(self):
        """Run the interactive demo."""
        print("🚀 Starting Tower Defense demo...")
        print("Click to place towers, enemies spawn automatically")
        
        while self.running:
            self.handle_events()
            self.update()
            self.render()
            self.clock.tick(60)
        
        pygame.quit()
    
    def handle_events(self):
        """Handle pygame events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Place tower at mouse position
                pos = pygame.mouse.get_pos()
                self.place_tower(pos)
    
    def place_tower(self, pos):
        """Place a tower at the given position."""
        tower = {
            'pos': pos,
            'range': 100,
            'damage': 10,
            'color': (0, 255, 0)
        }
        self.towers.append(tower)
        print(f"Tower placed at {pos}")
    
    def update(self):
        """Update game state."""
        # Spawn enemies periodically
        if pygame.time.get_ticks() % 2000 < 50:  # Every 2 seconds
            self.spawn_enemy()
        
        # Update enemies
        for enemy in self.enemies[:]:
            enemy['pos'] = (enemy['pos'][0] + enemy['speed'], enemy['pos'][1])
            if enemy['pos'][0] > 800:  # Off screen
                self.enemies.remove(enemy)
        
        # Tower shooting logic (simplified)
        for tower in self.towers:
            for enemy in self.enemies[:]:
                distance = ((tower['pos'][0] - enemy['pos'][0])**2 + 
                           (tower['pos'][1] - enemy['pos'][1])**2)**0.5
                if distance < tower['range']:
                    self.enemies.remove(enemy)
                    self.score += 10
                    break
    
    def spawn_enemy(self):
        """Spawn a new enemy."""
        enemy = {
            'pos': (0, 300),
            'speed': 2,
            'health': 100,
            'color': (255, 0, 0)
        }
        self.enemies.append(enemy)
    
    def render(self):
        """Render the game."""
        self.screen.fill((50, 50, 50))
        
        # Draw towers
        for tower in self.towers:
            pygame.draw.circle(self.screen, tower['color'], tower['pos'], 20)
            # Draw range indicator
            pygame.draw.circle(self.screen, (0, 255, 0, 50), tower['pos'], tower['range'], 1)
        
        # Draw enemies
        for enemy in self.enemies:
            pygame.draw.circle(self.screen, enemy['color'], enemy['pos'], 15)
        
        # Draw UI
        font = pygame.font.Font(None, 36)
        score_text = font.render(f"Score: {self.score}", True, (255, 255, 255))
        self.screen.blit(score_text, (10, 10))
        
        instructions = font.render("Click to place towers", True, (255, 255, 255))
        self.screen.blit(instructions, (10, 50))
        
        pygame.display.flip()


def main():
    """Main entry point."""
    print("🤖 AI-Powered Game Development Demo")
    print("=" * 40)
    
    try:
        # Generate the game
        project, assets = create_tower_defense_game()
        
        print("\n✅ Game generation completed!")
        print("\n🎮 Starting interactive demo...")
        
        # Run the demo
        demo = TowerDefenseDemo()
        demo.run_demo()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Make sure all dependencies are installed and API keys are configured")


if __name__ == "__main__":
    main()
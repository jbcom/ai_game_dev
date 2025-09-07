"""
Pygame Template for WebAssembly Deployment with Professor Pixel Integration
Designed for educational RPG games with interactive learning breakpoints.
"""

import asyncio
import sys
from typing import Dict, Any, Callable, Optional
from pathlib import Path

try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False

class ProfessorPixelIntegration:
    """Integration system for Professor Pixel teaching moments in pygame WebAssembly games."""
    
    def __init__(self):
        self.breakpoints = {}
        self.triggered_lessons = set()
        self.game_state = {}
        
    def register_breakpoint(self, event_name: str, lesson_id: str, condition: Optional[Callable[[Dict[str, Any]], bool]] = None):
        """Register a learning breakpoint in the game."""
        self.breakpoints[event_name] = {
            'lesson_id': lesson_id,
            'condition': condition,
            'triggered': False
        }
    
    def trigger_breakpoint(self, event_name: str, game_state: Optional[Dict[str, Any]] = None):
        """Check and trigger a learning breakpoint if conditions are met."""
        if event_name not in self.breakpoints:
            return False
            
        breakpoint = self.breakpoints[event_name]
        
        # Skip if already triggered
        if breakpoint['triggered'] or breakpoint['lesson_id'] in self.triggered_lessons:
            return False
            
        # Check condition if provided
        condition = breakpoint['condition']
        if condition and not condition(game_state or self.game_state):
            return False
            
        # Trigger the lesson via JavaScript bridge
        self.show_professor_lesson(breakpoint['lesson_id'], game_state)
        breakpoint['triggered'] = True
        self.triggered_lessons.add(breakpoint['lesson_id'])
        return True
    
    def show_professor_lesson(self, lesson_id: str, context: Optional[Dict[str, Any]] = None):
        """Bridge to JavaScript Professor Pixel modal system."""
        # In WebAssembly, we can call JavaScript functions from Python
        # This would trigger the Professor Pixel modal we created
        context_str = str(context) if context else "{}"
        js_call = f"showProfessorLesson('{lesson_id}', {context_str})"
        
        # For WebAssembly builds, this would use emscripten to call JavaScript
        try:
            import emscripten  # type: ignore
            emscripten.run_script(js_call)  # type: ignore
        except ImportError:
            # Fallback for desktop testing
            print(f"🎓 Professor Pixel: Teaching moment '{lesson_id}' triggered!")


class EducationalRPGGame:
    """Educational RPG game template with Professor Pixel integration."""
    
    def __init__(self):
        if not PYGAME_AVAILABLE:
            raise ImportError("pygame is required but not available")
            
        pygame.init()
        
        # Game setup
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("NeoTokyo Code Academy: The Binary Rebellion")
        self.clock = pygame.time.Clock()
        
        # Game state
        self.running = True
        self.player_health = 100
        self.player_level = 1
        self.enemies_defeated = 0
        self.current_stage = "tutorial"
        
        # Professor Pixel integration
        self.professor = ProfessorPixelIntegration()
        self.setup_learning_breakpoints()
        
        # Colors
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.GREEN = (0, 255, 0)
        self.RED = (255, 0, 0)
        self.CYAN = (0, 255, 255)
        
    def setup_learning_breakpoints(self):
        """Setup educational breakpoints throughout the game."""
        
        # Variables lesson - triggered when player health changes
        self.professor.register_breakpoint(
            'player_takes_damage',
            'variables',
            lambda state: state.get('player_health', 100) < 100
        )
        
        # Loops lesson - triggered when game loop runs for first time
        self.professor.register_breakpoint(
            'game_loop_start',
            'loops',
            lambda state: state.get('frame_count', 0) == 60  # After 1 second
        )
        
        # Functions lesson - triggered when attack function is called
        self.professor.register_breakpoint(
            'attack_function_called',
            'functions',
            lambda state: state.get('attacks_made', 0) >= 3
        )
        
        # Conditionals lesson - triggered when making decisions
        self.professor.register_breakpoint(
            'decision_point',
            'conditionals',
            lambda state: state.get('choices_made', 0) >= 1
        )
        
        # Data structures lesson - triggered when inventory system used
        self.professor.register_breakpoint(
            'inventory_used',
            'data_structures',
            lambda state: len(state.get('inventory', [])) >= 2
        )
    
    def handle_events(self):
        """Handle pygame events with learning integration."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.attack_enemy()
                elif event.key == pygame.K_h:
                    self.use_health_potion()
                elif event.key == pygame.K_i:
                    self.open_inventory()
    
    def attack_enemy(self):
        """Attack function that triggers learning breakpoint."""
        # Update game state
        self.professor.game_state['attacks_made'] = self.professor.game_state.get('attacks_made', 0) + 1
        
        # Simulate combat
        damage_dealt = 25
        enemy_health = 50  # Simplified enemy
        
        # Trigger Professor Pixel lesson about functions
        self.professor.trigger_breakpoint('attack_function_called', {
            'attacks_made': self.professor.game_state['attacks_made'],
            'damage_dealt': damage_dealt,
            'function_name': 'attack_enemy'
        })
        
        self.enemies_defeated += 1
        print(f"⚔️ Attack! Enemy defeated. Total: {self.enemies_defeated}")
    
    def take_damage(self, amount: int):
        """Player takes damage - triggers variables lesson."""
        old_health = self.player_health
        self.player_health = max(0, self.player_health - amount)
        
        # Update Professor Pixel game state
        self.professor.game_state['player_health'] = self.player_health
        self.professor.game_state['damage_taken'] = amount
        
        # Trigger learning about variables
        self.professor.trigger_breakpoint('player_takes_damage', {
            'old_health': old_health,
            'new_health': self.player_health,
            'damage': amount
        })
        
        print(f"💥 Took {amount} damage! Health: {self.player_health}")
    
    def use_health_potion(self):
        """Use health potion - demonstrates inventory/data structures."""
        inventory = self.professor.game_state.get('inventory', [])
        
        if 'health_potion' in inventory:
            inventory.remove('health_potion')
            self.player_health = min(100, self.player_health + 30)
            self.professor.game_state['inventory'] = inventory
            
            # Trigger inventory/data structures lesson
            self.professor.trigger_breakpoint('inventory_used', {
                'inventory': inventory,
                'action': 'used_health_potion',
                'new_health': self.player_health
            })
            
            print("💚 Used health potion! Health restored.")
        else:
            print("❌ No health potions in inventory!")
    
    def open_inventory(self):
        """Open inventory system - adds items for learning."""
        inventory = self.professor.game_state.get('inventory', [])
        
        # Add sample items for learning
        if len(inventory) < 2:
            inventory.extend(['health_potion', 'key_card', 'data_chip'])
            self.professor.game_state['inventory'] = inventory
            
            print(f"🎒 Inventory: {inventory}")
            
            # Trigger data structures lesson
            self.professor.trigger_breakpoint('inventory_used', {
                'inventory': inventory,
                'action': 'opened_inventory'
            })
    
    def make_choice(self, choice: str):
        """Make story choice - triggers conditionals lesson."""
        choices_made = self.professor.game_state.get('choices_made', 0) + 1
        self.professor.game_state['choices_made'] = choices_made
        
        # Trigger conditionals lesson
        self.professor.trigger_breakpoint('decision_point', {
            'choice': choice,
            'choices_made': choices_made
        })
        
        print(f"🤔 Choice made: {choice}")
    
    def update(self):
        """Update game state."""
        # Update frame count for loop lesson
        frame_count = self.professor.game_state.get('frame_count', 0) + 1
        self.professor.game_state['frame_count'] = frame_count
        
        # Trigger game loop lesson early in the game
        if frame_count == 60:  # After 1 second at 60fps
            self.professor.trigger_breakpoint('game_loop_start', {
                'frame_count': frame_count,
                'fps': 60
            })
        
        # Simulate taking damage occasionally for demonstration
        if frame_count == 180 and self.player_health == 100:  # After 3 seconds
            self.take_damage(15)
        
        # Add inventory items for demo
        if frame_count == 300:  # After 5 seconds
            self.open_inventory()
    
    def draw(self):
        """Render the game."""
        self.screen.fill(self.BLACK)
        
        # Draw simple UI
        font = pygame.font.Font(None, 36)
        
        # Title
        title = font.render("NeoTokyo Code Academy: The Binary Rebellion", True, self.CYAN)
        self.screen.blit(title, (50, 50))
        
        # Health bar
        health_text = font.render(f"Health: {self.player_health}/100", True, self.GREEN if self.player_health > 50 else self.RED)
        self.screen.blit(health_text, (50, 150))
        
        # Health bar visual
        bar_width = 300
        bar_height = 20
        health_percentage = self.player_health / 100
        pygame.draw.rect(self.screen, self.RED, (50, 180, bar_width, bar_height))
        pygame.draw.rect(self.screen, self.GREEN, (50, 180, bar_width * health_percentage, bar_height))
        
        # Instructions
        instructions = [
            "SPACE - Attack Enemy (Functions)",
            "H - Use Health Potion (Data Structures)", 
            "I - Open Inventory (Data Structures)",
            "",
            "👨‍🏫 Professor Pixel will teach you as you play!",
            "🎮 Watch for teaching moments during gameplay."
        ]
        
        for i, instruction in enumerate(instructions):
            color = self.WHITE if not instruction.startswith(('👨‍🏫', '🎮')) else self.CYAN
            text = pygame.font.Font(None, 24).render(instruction, True, color)
            self.screen.blit(text, (50, 250 + i * 30))
        
        # Game stats
        stats = [
            f"Enemies Defeated: {self.enemies_defeated}",
            f"Frame: {self.professor.game_state.get('frame_count', 0)}",
            f"Lessons Learned: {len(self.professor.triggered_lessons)}"
        ]
        
        for i, stat in enumerate(stats):
            text = pygame.font.Font(None, 24).render(stat, True, self.WHITE)
            self.screen.blit(text, (500, 250 + i * 30))
        
        pygame.display.flip()
    
    async def run(self):
        """Main game loop - async for WebAssembly compatibility."""
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            
            # Critical for WebAssembly: yield control to browser
            await asyncio.sleep(0)
        
        pygame.quit()


# Pygbag deployment instructions
async def main():
    """Entry point for pygbag WebAssembly deployment."""
    game = EducationalRPGGame()
    await game.run()


if __name__ == "__main__":
    # Run the game
    asyncio.run(main())


# Pygbag deployment info:
"""
To deploy this educational RPG to WebAssembly with pygbag:

1. Install pygbag:
   pip install pygbag

2. Create project structure:
   educational_rpg/
   ├── main.py          # This file
   ├── assets/          # Images, sounds
   ├── favicon.png      # Optional
   └── professor_pixel_modal.html  # Copy our modal component

3. Deploy to web:
   pygbag educational_rpg

4. Access at:
   http://localhost:8000

The game will run in the browser with Professor Pixel teaching moments
triggered automatically during gameplay!

Key Features:
- WebAssembly compatible async game loop
- Professor Pixel integration via JavaScript bridge
- Educational breakpoints for core programming concepts
- Mobile-friendly browser deployment
- Real-time learning during gameplay
"""
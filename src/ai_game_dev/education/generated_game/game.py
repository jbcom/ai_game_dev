Creating a complete game like "NeoTokyo Code Academy: The Binary Rebellion" is a complex task, especially for a text-based platform. However, I can provide you with a foundational structure for the game using Pygame. This will include the main components and classes you need to get started. You can expand upon this structure by adding more detailed game logic, assets, and educational content.

```python
import pygame
import sys

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Game States
MENU, PLAYING, GAME_OVER = 'menu', 'playing', 'game_over'

# Character Classes
CHARACTER_CLASSES = ['Code Knight', 'Data Sage', 'Bug Hunter', 'Web Weaver']

# Load assets (placeholder)
def load_assets():
    # Load images, sounds, etc.
    pass

# Game Class
class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("NeoTokyo Code Academy: The Binary Rebellion")
        self.clock = pygame.time.Clock()
        self.state = MENU
        self.character_class = None
        self.professor_pixel = ProfessorPixel()
        self.load_assets()

    def load_assets(self):
        load_assets()

    def run(self):
        while True:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if self.state == MENU:
                    self.handle_menu_input(event.key)
                elif self.state == PLAYING:
                    self.handle_playing_input(event.key)
                elif self.state == GAME_OVER:
                    self.handle_game_over_input(event.key)

    def handle_menu_input(self, key):
        if key == pygame.K_RETURN:
            self.state = PLAYING
            self.character_class = CHARACTER_CLASSES[0]  # Placeholder for character selection

    def handle_playing_input(self, key):
        if key == pygame.K_ESCAPE:
            self.state = GAME_OVER

    def handle_game_over_input(self, key):
        if key == pygame.K_RETURN:
            self.state = MENU

    def update(self):
        if self.state == PLAYING:
            # Update game logic
            pass

    def draw(self):
        self.screen.fill(BLACK)
        if self.state == MENU:
            self.draw_menu()
        elif self.state == PLAYING:
            self.draw_playing()
        elif self.state == GAME_OVER:
            self.draw_game_over()
        pygame.display.flip()

    def draw_menu(self):
        # Draw menu screen
        pass

    def draw_playing(self):
        # Draw playing screen
        pass

    def draw_game_over(self):
        # Draw game over screen
        pass

# Professor Pixel Class
class ProfessorPixel:
    def __init__(self):
        # Initialize mentor attributes
        pass

    def guide(self):
        # Provide guidance to the player
        pass

# Main function
def main():
    game = Game()
    game.run()

if __name__ == "__main__":
    main()
```

### Explanation:

1. **Game Class**: Manages the game state, including the menu, playing, and game over states. It handles events, updates game logic, and draws the appropriate screen.

2. **Professor Pixel**: A placeholder class for the mentor character. You can expand this with methods to provide guidance and educational content.

3. **Character Classes**: A list of character classes. You can expand this with specific attributes and methods for each class.

4. **Asset Loading**: A placeholder function for loading game assets like images and sounds.

5. **Event Handling**: Basic event handling for transitioning between game states.

6. **Drawing Functions**: Placeholder functions for drawing the menu, playing, and game over screens.

This code provides a basic framework. You will need to expand it with specific game logic, educational content, assets, and more detailed mechanics to create a complete game.
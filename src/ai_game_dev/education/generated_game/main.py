Below is a complete `main.py` file for "NeoTokyo Code Academy: The Binary Rebellion", a cyberpunk educational RPG. This script initializes Pygame, sets up the game window, and includes a professional game loop with error handling and graceful shutdown. It assumes that you have separate `game` and `player` modules to handle specific game mechanics and player interactions.

```python
import pygame
import sys
from game import Game
from player import Player

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
CYBERPUNK_COLOR = (10, 10, 50)  # Dark blue background for cyberpunk theme

def main():
    # Initialize Pygame
    pygame.init()
    
    # Set up the screen
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("NeoTokyo Code Academy: The Binary Rebellion")
    
    # Create a clock object to manage the frame rate
    clock = pygame.time.Clock()
    
    # Initialize game and player objects
    game = Game()
    player = Player()

    # Main game loop
    running = True
    try:
        while running:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                # Handle other events like key presses
                game.handle_event(event, player)

            # Update game state
            game.update(player)

            # Draw everything
            screen.fill(CYBERPUNK_COLOR)
            game.draw(screen, player)
            pygame.display.flip()

            # Cap the frame rate
            clock.tick(FPS)

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Clean up and exit
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    main()
```

### Explanation:

1. **Pygame Initialization**: The script starts by initializing Pygame with `pygame.init()`.

2. **Screen Setup**: It sets up an 800x600 window with a cyberpunk color scheme using a dark blue background.

3. **Game Loop**: The main game loop runs at 60 FPS, handling events, updating the game state, and drawing the game screen.

4. **Error Handling**: The game loop is wrapped in a try-except block to catch and print any exceptions that occur, ensuring that the game can shut down gracefully.

5. **Graceful Shutdown**: The `finally` block ensures that Pygame quits and the program exits cleanly, even if an error occurs.

6. **Modules**: The script imports `Game` and `Player` from their respective modules, which are assumed to handle game logic and player interactions.

This code provides a solid foundation for your cyberpunk educational RPG, allowing you to focus on developing the game mechanics and educational content in the `game` and `player` modules.
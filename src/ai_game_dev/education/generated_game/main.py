import pygame
import sys
from game import Game
from player import Player

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
CYBERPUNK_BLUE = (0, 255, 255)
CYBERPUNK_PURPLE = (255, 0, 255)

def main():
    # Initialize Pygame
    pygame.init()
    
    # Set up the display
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("NeoTokyo Code Academy: The Binary Rebellion")
    
    # Create a clock object to manage the frame rate
    clock = pygame.time.Clock()
    
    # Initialize game and player objects
    try:
        game = Game()
        player = Player()
    except Exception as e:
        print(f"Error initializing game or player: {e}")
        pygame.quit()
        sys.exit()

    # Main game loop
    running = True
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        # Game logic
        try:
            game.update()
            player.update()
        except Exception as e:
            print(f"Error during game update: {e}")
            running = False

        # Drawing
        screen.fill(CYBERPUNK_BLUE)  # Fill the screen with a cyberpunk blue
        try:
            game.draw(screen)
            player.draw(screen)
        except Exception as e:
            print(f"Error during drawing: {e}")
            running = False

        # Update the display
        pygame.display.flip()
        
        # Cap the frame rate
        clock.tick(FPS)
    
    # Clean up and exit
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        pygame.quit()
        sys.exit()

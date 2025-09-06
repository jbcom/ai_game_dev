To create a comprehensive `utils.py` file for your game "NeoTokyo Code Academy: The Binary Rebellion," we'll structure it to include utility functions and constants that would be commonly used throughout the game. This file will help manage assets, perform mathematical operations, manage screen configurations, and include helpful constants for color and configuration settings. Here's a production-quality example:

```python
import pygame
import os
import json
import math

# Initialize Pygame
pygame.init()

# Constants
ASSET_FOLDER = 'assets'
IMAGE_FOLDER = os.path.join(ASSET_FOLDER, 'images')
SOUND_FOLDER = os.path.join(ASSET_FOLDER, 'sounds')
FONT_FOLDER = os.path.join(ASSET_FOLDER, 'fonts')

# Configuration Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Color Constants for 16-bit Cyberpunk Pixel Art Style
CYBER_BLUE = (0, 255, 255)
NEON_GREEN = (57, 255, 20)
NEON_PINK = (255, 20, 147)
NEON_YELLOW = (255, 255, 0)
BACKGROUND_COLOR = (10, 10, 20)

# Helper Functions

def load_image(filename):
    """Load an image from the images folder."""
    path = os.path.join(IMAGE_FOLDER, filename)
    try:
        image = pygame.image.load(path).convert_alpha()
        return image
    except pygame.error as e:
        print(f"Cannot load image: {filename}")
        raise SystemExit(e)

def load_sound(filename):
    """Load a sound from the sounds folder."""
    path = os.path.join(SOUND_FOLDER, filename)
    try:
        sound = pygame.mixer.Sound(path)
        return sound
    except pygame.error as e:
        print(f"Cannot load sound: {filename}")
        raise SystemExit(e)

def load_font(filename, size):
    """Load a font from the fonts folder."""
    path = os.path.join(FONT_FOLDER, filename)
    try:
        font = pygame.font.Font(path, size)
        return font
    except pygame.error as e:
        print(f"Cannot load font: {filename}")
        raise SystemExit(e)

def distance(point1, point2):
    """Calculate the Euclidean distance between two points."""
    return math.sqrt((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2)

def check_collision(rect1, rect2):
    """Check if two rectangles collide."""
    return rect1.colliderect(rect2)

def vector_add(v1, v2):
    """Add two vectors."""
    return (v1[0] + v2[0], v1[1] + v2[1])

def vector_subtract(v1, v2):
    """Subtract two vectors."""
    return (v1[0] - v2[0], v1[1] - v2[1])

def normalize_vector(v):
    """Normalize a vector."""
    length = math.sqrt(v[0] ** 2 + v[1] ** 2)
    if length == 0:
        return (0, 0)
    return (v[0] / length, v[1] / length)

def screen_center():
    """Get the center point of the screen."""
    return (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

def load_json(filename):
    """Load a JSON file from the asset folder."""
    path = os.path.join(ASSET_FOLDER, filename)
    try:
        with open(path, 'r') as file:
            data = json.load(file)
            return data
    except FileNotFoundError as e:
        print(f"Cannot load JSON file: {filename}")
        raise SystemExit(e)

def save_json(data, filename):
    """Save data to a JSON file in the asset folder."""
    path = os.path.join(ASSET_FOLDER, filename)
    try:
        with open(path, 'w') as file:
            json.dump(data, file, indent=4)
    except IOError as e:
        print(f"Cannot save JSON file: {filename}")
        raise SystemExit(e)

# Screen Utility Function
def set_screen_mode(fullscreen=False):
    """Set the screen mode, toggle between fullscreen and windowed."""
    flags = pygame.FULLSCREEN if fullscreen else 0
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), flags)
    pygame.display.set_caption("NeoTokyo Code Academy: The Binary Rebellion")
    return screen

# Ensure Pygame quits properly
def quit_game():
    """Quit the Pygame application."""
    pygame.quit()
    exit()

# Additional Helper Functions can be added as needed
```

### Explanation:
- **Asset Loading**: Functions like `load_image`, `load_sound`, and `load_font` are designed to handle asset loading from predefined folders. They raise an error if the asset cannot be loaded, ensuring robust error handling.
- **Math Helpers**: Functions like `distance`, `check_collision`, and vector operations are included for common mathematical operations used in game programming.
- **Color Constants**: Predefined colors help maintain consistency and style throughout the game's design.
- **Screen Utility**: Functions for setting screen modes and quitting the game are included for ease of use.
- **JSON Operations**: Functions for loading and saving JSON data, which might be used for configurations or game state persistence.

This structure ensures that utility functions are organized, reusable, and maintainable, serving as an excellent resource for educational purposes and practical game development.
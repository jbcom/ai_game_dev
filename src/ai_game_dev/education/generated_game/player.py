import pygame
from pygame.locals import *

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load('player_sprite.png').convert_alpha()
        self.rect = self.image.get_rect(topleft=(x, y))
        
        # Movement attributes
        self.velocity = pygame.math.Vector2(0, 0)
        self.speed = 5
        
        # Character progression
        self.level = 1
        self.experience = 0
        self.experience_to_next_level = 100
        
        # Skills (representing programming concepts)
        self.skills = {
            'loops': 1,
            'functions': 1,
            'oop': 1
        }
        
        # Inventory management
        self.inventory = {
            'IDE': None,
            'Debugger': None,
            'TextEditor': None
        }
        
        # Attributes
        self.health = 100
        self.mana = 50
        self.coding_skill = 10
        
        # Animation and sprite handling
        self.animations = {
            'idle': [pygame.image.load(f'idle_{i}.png').convert_alpha() for i in range(4)],
            'walk': [pygame.image.load(f'walk_{i}.png').convert_alpha() for i in range(4)]
        }
        self.current_animation = 'idle'
        self.animation_index = 0
        self.animation_speed = 0.1
        self.animation_timer = 0
        
    def update(self, dt):
        self.handle_input()
        self.move()
        self.update_animation(dt)
        self.check_level_up()
        
    def handle_input(self):
        keys = pygame.key.get_pressed()
        
        self.velocity.x = 0
        self.velocity.y = 0
        
        if keys[K_LEFT] or keys[K_a]:
            self.velocity.x = -self.speed
            self.current_animation = 'walk'
        elif keys[K_RIGHT] or keys[K_d]:
            self.velocity.x = self.speed
            self.current_animation = 'walk'
        else:
            self.current_animation = 'idle'
        
        if keys[K_UP] or keys[K_w]:
            self.velocity.y = -self.speed
        elif keys[K_DOWN] or keys[K_s]:
            self.velocity.y = self.speed
        
    def move(self):
        self.rect.x += self.velocity.x
        self.rect.y += self.velocity.y
    
    def update_animation(self, dt):
        self.animation_timer += dt
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            self.animation_index = (self.animation_index + 1) % len(self.animations[self.current_animation])
            self.image = self.animations[self.current_animation][self.animation_index]
    
    def gain_experience(self, amount):
        self.experience += amount
        self.check_level_up()
    
    def check_level_up(self):
        if self.experience >= self.experience_to_next_level:
            self.level += 1
            self.experience -= self.experience_to_next_level
            self.experience_to_next_level *= 1.5
            self.level_up_skills()
    
    def level_up_skills(self):
        # Increase skills based on level
        self.skills['loops'] += 1
        self.skills['functions'] += 1
        self.skills['oop'] += 1
        self.health += 10
        self.mana += 5
        self.coding_skill += 2
    
    def use_item(self, item_name):
        if item_name in self.inventory and self.inventory[item_name]:
            # Implement item usage logic
            pass
    
    def draw(self, surface):
        surface.blit(self.image, self.rect.topleft)

# Example usage
if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()
    
    player = Player(100, 100)
    all_sprites = pygame.sprite.Group(player)
    
    running = True
    while running:
        dt = clock.tick(60) / 1000  # Amount of seconds between each loop
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
        
        all_sprites.update(dt)
        
        screen.fill((0, 0, 0))
        all_sprites.draw(screen)
        pygame.display.flip()
    
    pygame.quit()

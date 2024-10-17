import pygame
import random

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Side-Scrolling Game with Steppers")

# Game constants
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (135, 206, 250)  # Sky color
GREEN = (34, 139, 34)  # Grass color
BROWN = (139, 69, 19)  # Land color
GRAY = (169, 169, 169)  # Stepper color
RED = (255, 0, 0)  # Dangerous enemy color
FPS = 60
GRAVITY = 0.8

# Ground height
GROUND_HEIGHT = 50

# Load images (correct image loading)
PLAYER_IMG = pygame.image.load("flappy.png").convert_alpha()
PLAYER_IMG = pygame.transform.scale(PLAYER_IMG, (40, 40))  # Resize to width: 100 and height: 100
ENEMY_IMG = pygame.Surface((50, 50))
ENEMY_IMG.fill(RED)
COLLECTIBLE_IMG = pygame.Surface((30, 30))
COLLECTIBLE_IMG.fill((0, 0, 255))


# Classes

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = PLAYER_IMG
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = 100, SCREEN_HEIGHT - GROUND_HEIGHT - 100  # Adjusted for resized player image
        self.speed_x = 0
        self.speed_y = 0
        self.jumping = False
        self.health = 100
        self.lives = 3
        self.projectiles = pygame.sprite.Group()
        self.score = 0
        self.last_platform_y = SCREEN_HEIGHT  # For scoring purposes

    def update(self, platforms):
        # Apply gravity
        self.speed_y += GRAVITY

        # Control movement and jump
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.speed_x = -5
        elif keys[pygame.K_RIGHT]:
            self.speed_x = 5
        else:
            self.speed_x = 0

        if keys[pygame.K_SPACE] and not self.jumping:
            self.jumping = True
            self.speed_y = -15  # Jump force

        # Shooting
        if keys[pygame.K_z]:
            self.shoot()

        # Update position
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y

        # Check for collision with the ground or platforms
        if self.rect.bottom >= SCREEN_HEIGHT - GROUND_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT - GROUND_HEIGHT
            self.jumping = False  # Allow jumping again when on the ground
        else:
            # Check for collision with platforms
            self.check_platform_collisions(platforms)

        # Scoring based on platforms passed
        for platform in platforms:
            if platform.rect.top < self.rect.bottom < platform.rect.bottom:
                if self.rect.y < platform.rect.top and self.last_platform_y > platform.rect.top:
                    self.score += 1  # Increment score for each platform passed
                    self.last_platform_y = platform.rect.top  # Update last passed platform y-coordinate

        # Check if the player has reached the highest platform
        if self.score == len(platforms):
            self.win_game()

        # Boundary checking
        if self.rect.x < 0:
            self.rect.x = 0
        elif self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH

    def check_platform_collisions(self, platforms):
        for platform in platforms:
            if platform.rect.colliderect(self.rect) and self.speed_y > 0:  # Check if player is falling onto platform
                self.rect.bottom = platform.rect.top  # Place player on top of the platform
                self.speed_y = 0
                self.jumping = False

    def shoot(self):
        # Shoot a projectile
        projectile = Projectile(self.rect.right, self.rect.centery)
        self.projectiles.add(projectile)

    def draw(self, screen):
        screen.blit(self.image, self.rect)
        self.projectiles.update()
        self.projectiles.draw(screen)

    def win_game(self):
        self.display_message("You Win!", self.score)

    def game_over(self):
        self.display_message("Game Over", self.score)

    def display_message(self, message, score):
        # Display the message on the screen
        font = pygame.font.SysFont(None, 72)
        text = font.render(message, True, WHITE)
        score_text = font.render(f'Score: {score}', True, WHITE)

        # Render restart button
        restart_text = font.render('Press R to Restart', True, WHITE)

        screen.fill(BLACK)  # Clear the screen
        screen.blit(text, (SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2 - 50))
        screen.blit(score_text, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 10))
        screen.blit(restart_text, (SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2 + 70))
        pygame.display.flip()

        # Wait for user input to restart
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:  # Restart the game
                        waiting = False
                        main()  # Restart the game


class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill(GRAY)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        # Create a more natural appearance
        self.image.set_alpha(200)  # Semi-transparent for a natural look
        pygame.draw.rect(self.image, (0, 255, 0), (0, 0, width, height))  # Green platform with alpha

        # Add some texture or detail to the platform
        for _ in range(5):
            pygame.draw.circle(self.image, (100, 100, 100), (random.randint(0, width), random.randint(0, height)),
                               random.randint(5, 10))

    def draw(self, screen):
        screen.blit(self.image, self.rect)


class Projectile(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((10, 5))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed = 10

    def update(self):
        self.rect.x += self.speed
        if self.rect.x > SCREEN_WIDTH:
            self.kill()  # Remove projectile when it goes off screen


class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = ENEMY_IMG
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y
        self.health = 50
        self.speed = random.randint(2, 5)

    def update(self):
        self.rect.x -= self.speed
        if self.rect.right < 0:
            self.kill()

    def draw(self, screen):
        screen.blit(self.image, self.rect)


class Collectible(pygame.sprite.Sprite):
    def __init__(self, x, y, kind):
        super().__init__()
        self.image = COLLECTIBLE_IMG
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y
        self.kind = kind  # Health boost or extra life

    def apply_effect(self, player):
        if self.kind == 'health':
            player.health = min(player.health + 25, 100)
        elif self.kind == 'life':
            player.lives += 1
        self.kill()


class Level:
    def __init__(self, player):
        self.player = player
        self.enemies = pygame.sprite.Group()
        self.collectibles = pygame.sprite.Group()
        self.platforms = self.create_platforms()
        self.score = 0
        self.level = 1
        self.enemy_spawn_timer = 0  # Timer to control enemy spawning frequency

    def create_platforms(self):
        # Create a series of platforms (steppers) at different heights
        platforms = pygame.sprite.Group()
        for i in range(6):
            x = random.randint(100, SCREEN_WIDTH - 200)
            y = SCREEN_HEIGHT - GROUND_HEIGHT - (i * 80 + 100)  # Spread vertically, 80px apart
            width = random.randint(100, 200)
            height = 20
            platform = Platform(x, y, width, height)
            platforms.add(platform)
        return platforms

    def spawn_enemy(self):
        # Spawn an enemy at a random position on a random platform
        if self.platforms:
            platform = random.choice(self.platforms.sprites())
            x = platform.rect.right + 20
            y = platform.rect.top - 50  # Place just above the platform
            enemy = Enemy(x, y)
            self.enemies.add(enemy)

    def spawn_collectible(self):
        # Spawn a collectible at a random position on a random platform
        if self.platforms:
            platform = random.choice(self.platforms.sprites())
            x = random.randint(platform.rect.left, platform.rect.right - 30)
            y = platform.rect.top - 30  # Place just above the platform
            kind = random.choice(['health', 'life'])
            collectible = Collectible(x, y, kind)
            self.collectibles.add(collectible)

    def update(self):
        self.platforms.update()
        self.enemies.update()
        self.collectibles.update()
        self.enemy_spawn_timer += 1

        if self.enemy_spawn_timer > 100:  # Spawn an enemy every 100 frames
            self.spawn_enemy()
            self.enemy_spawn_timer = 0

    def draw(self, screen):
        self.platforms.draw(screen)
        self.enemies.draw(screen)
        self.collectibles.draw(screen)


# Main game loop

def main():
    # Set up the game objects
    player = Player()
    level = Level(player)
    all_sprites = pygame.sprite.Group(player)

    # Clock to control frame rate
    clock = pygame.time.Clock()

    # Main game loop
    running = True
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Update game state
        player.update(level.platforms)
        level.update()

        # Check for collisions with enemies and collectibles
        for enemy in pygame.sprite.spritecollide(player, level.enemies, False):
            player.health -= 10  # Reduce health on collision with enemy
            if player.health <= 0:
                player.game_over()
                running = False

        for collectible in pygame.sprite.spritecollide(player, level.collectibles, True):
            collectible.apply_effect(player)

        # Clear screen
        screen.fill(BLUE)

        # Draw background
        pygame.draw.rect(screen, GREEN, (0, SCREEN_HEIGHT - GROUND_HEIGHT, SCREEN_WIDTH, GROUND_HEIGHT))

        # Draw all game objects
        player.draw(screen)
        level.draw(screen)

        # Update the display
        pygame.display.flip()

        # Cap the frame rate
        clock.tick(FPS)

    # Quit Pygame
    pygame.quit()


if __name__ == '__main__':
    main()

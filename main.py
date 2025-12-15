import pygame
import random
import math

# ------------------------------
# Game Constants
# ------------------------------
WIDTH, HEIGHT = 700, 1000
PLAYER_RADIUS = int(HEIGHT * 0.01)
FPS = 60
COLORS = [
    (0, 0, 255),       # Blue
    (0, 255, 0),       # Green
    (255, 0, 0),       # Red
    (255, 255, 0),     # Yellow
    (255, 165, 0),     # Orange
    (128, 0, 128),     # Purple
    (0, 255, 255),     # Cyan
    (255, 192, 203),   # Pink
]

# ---------------------------------------------
# Player class
# ---------------------------------------------
class Player:

    def __init__(self):
        """
        Initialize the player obj with a default position, color, radius, and physical properties

        :attr x (float): Horizontal position of the player relative to the screen.
        :attr y (float): Vertical position of the player relative to the screen.
        :attr radius (int): Radius of the player's circle.
        :attr color (tuple[int, int, int]): RGB color of the player.
        :attr vel_y (float): Current vertical velocity (positive = downward).
        :attr jump_power (float): Vertical velocity applied when player jumps (negative = upward).
        :attr gravity (float): Acceleration applied downward each frame.
        :attr max_jumps_per_second (int): Maximum number of jumps allowed per second.
        """
        self.x = WIDTH * 0.25       
        self.y = HEIGHT * 0.5     
        self.radius = PLAYER_RADIUS
        self.color = (0, 153, 255)
        self.vel_y = 0
        self.jump_power = -HEIGHT * 0.012
        self.gravity = HEIGHT * 0.0008
        self.max_jumps_per_second = 5

    def jump(self):
        """
        Apply vertical jump velocity to the player.
        """
        self.vel_y = self.jump_power

    def update_position(self):
        """
        Update the player's vertical position using velocity and gravity, and handle ground collision.
        """
        self.vel_y += self.gravity
        self.y += self.vel_y
        if self.y >= (HEIGHT - self.radius):
            self.y = (HEIGHT - self.radius)
            self.vel_y = 0

    def draw(self, screen):
        """
        Draw the player as a circle on the screen.

        :param screen (pygame.Surface): Pygame surface to draw the player on.
        """
        pygame.draw.circle(screen, self.color, (self.x, int(self.y)), self.radius)


    
# ---------------------------------------------
# Obstacle class
# ---------------------------------------------
class Obstacle:

    def __init__(self, x, gap, gap_y, width):
        """
        Initialize an obstacle with top and bottom rectangles and a vertical gap.

        :param world_x: Horizontal position of the obstacle in the world.
        :param gap_height: Vertical height of the gap the player must pass through.
        :param gap_y: Y-coordinate of the top of the gap.
        :param width: Width of the obstacle.

        :attr world_x (float): Horizontal position of the obstacle in the world.
        :attr width (int): Width of the obstacle.
        :attr color (tuple[int, int, int]): RGB color of the obstacle.
        :attr gap (int): Height of the gap between top and bottom rectangles.
        :attr gap_y (float): Y-coordinate of the top of the gap (clamped to screen bounds).
        :attr r1_y (int): Top rectangle Y-coordinate (always 0).
        :attr r1_height (int): Height of the top rectangle (gap_y).
        :attr r2_y (int): Bottom rectangle Y-coordinate (gap_y + gap_height).
        :attr r2_height (int): Height of the bottom rectangle (fills remaining screen height).
        """
        self.world_x = x
        self.width = width
        self.color = random.choice(COLORS)
        self.gap = gap
        self.gap_y = max(0, min(HEIGHT - gap, gap_y))

        # Top rectangle height is gap_y
        self.r1_y = 0
        self.r1_height = self.gap_y

        # Bottom rectangle height starts at gap_y + gap
        self.r2_y = self.gap_y + gap
        self.r2_height = HEIGHT - self.r2_y

    def get_screen_x(self, world_offset):
        """
        Convert world X-coordinate to screen X-coordinate.

        :param world_offset (float): Current horizontal scroll of the world.
        :return (float): Screen X-coordinate of the obstacle.
        """
        return self.world_x - world_offset

    def draw(self, screen, x):
        """
        Draw the top and bottom rectangles of the obstacle.

        :param screen (pygame.Surface): Pygame surface to draw on.
        :param x (float): Screen X-coordinate of the obstacle.
        """
        pygame.draw.rect(screen, self.color, (x, self.r1_y, self.width, self.r1_height))
        pygame.draw.rect(screen, self.color, (x, self.r2_y, self.width, self.r2_height))

# ---------------------------------------------
# Game class
# ---------------------------------------------
class Game:
    def __init__(self):
        """
        Initialize the game, create the window, player, obstacles, and other settings.

        :attr screen (pygame.Surface): The game window.
        :attr player (Player): The player instance.
        :attr clock (pygame.time.Clock): Clock to manage frames per second.
        :attr running (bool): Determines whether the game loop is active.
        :attr speed (int): The rate at which the world moves leftward.
        :attr world_x (float): Horizontal offset of the world relative to the screen.
        :attr obstacles (list): List of active obstacles in the world.
        :attr game_over (bool): True when the game is over.
        """
        pygame.init()
        pygame.display.set_caption("Ryans World")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.player = Player()
        self.clock = pygame.time.Clock()
        self.running = True
        self.speed = 2
        self.world_x = 0
        self.obstacles = []
        self.game_over = False

    def get_jump_height(self):
        """
        Compute the maximum vertical height of a jump based on player's jump power and gravity.

        :return (float): Maximum jump height in pixels.
        """
        v0 = abs(self.player.jump_power)
        g = self.player.gravity
        h = (v0 * v0) / (2 * g)
        return h
    
    def get_jump_distance(self):
        """
        Compute the maximum horizontal distance the player can travel during a jump.

        :return (float): Maximum horizontal distance in pixels.
        """
        v0 = abs(self.player.jump_power)
        g = self.player.gravity
        airtime = 2 * v0 / g
        vx = self.speed
        return vx * airtime

    def collision(self):
        """
        Check if the player collides with any obstacle.

        :return (bool): True if collision occurs, False otherwise.
        """
        for o in self.obstacles:
            x = o.get_screen_x(self.world_x)
            for ry, rh in [(o.r1_y, o.r1_height), (o.r2_y, o.r2_height)]:
                closest_x = max(x, min(self.player.x, x + o.width))
                closest_y = max(ry, min(self.player.y, ry + rh))
                dx = self.player.x - closest_x
                dy = self.player.y - closest_y
                if dx * dx + dy * dy < self.player.radius * self.player.radius:
                    return True
        return False
            
    def handle_events(self):
        """
        Handle all user inputs. QUIT events stops the game loop and the KEYDOWN event
        with SPACE triggers the player's jump
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.player.jump()
                elif self.game_over and event.key == pygame.K_r:
                    self.reset_game()

    def calculate_obstacle_width(self):
        """
        Calculate the width of the next obstacle based off player radius and jump distance.

        :return (int): Width in pixels.
        """
        jump_distance = int(self.get_jump_distance())
        min_width = int(self.player.radius)
        max_width = jump_distance * 3
        return min_width, max_width, random.randint(min_width, max_width)

    def calculate_gap_height(self):
        """
        Calculate the height of the next obstacle's gap based off player radius and jump height.

        :return (int): Gap height in pixels.
        """
        y_max = self.get_jump_height()
        min_gap = int(((self.player.radius * 2) + y_max) * 1.1)
        max_gap = int(min_gap * 3)
        return min_gap, max_gap, random.randint(min_gap, max_gap)

    def calculate_spawn_distance(self):
        """
        Compute the distance a player travels in one jump for obstacle spawning based off player radius and jump distance

        :return (tuple[int, int, int]): Minimum distance, maximum distance, random distance.
        """
        jump_distance_x = self.get_jump_distance()
        min_dist = int(jump_distance_x + self.player.radius * 2)
        max_dist = int(min_dist * 4)
        return min_dist, max_dist, random.randint(min_dist, max_dist)
    
    def calculate_max_height_increase(self, x):
        """
        Compute the maximum vertical height the player can reach while moving horizontally
        toward the next obstacle, based on jump power, gravity, and number of frames available.
        
        :param horizontal_distance: Distance to the next obstacle (pixels)
        :return: Maximum height increase (positive number, pixels)
        """
        frames = math.floor(x / self.speed)
        frames_per_jump = math.floor(FPS / self.player.max_jumps_per_second)
        v = 0
        y = 0
        max_increase = 0
        for i in range(frames):
            if i % frames_per_jump == 0:
                v += self.player.jump_power
            v += self.player.gravity
            y += v
            if y < max_increase:
                max_increase = y
        return -max_increase

    def calculate_max_height_decrease(self, x):
        """
        Compute the maximum vertical fall distance the player can reach while moving
        horizontally toward the next obstacle IF they jump from the edge of the most 
        recent obstacle
        
        :param horizontal_distance: Distance to the next obstacle (pixels)
        :return: Maximum fall distance (positive number, pixels)
        """
        frames = math.floor(x / self.speed)
        v = self.player.jump_power # jump from edge of last ubstacle
        y = 0
        for i in range(frames):
            v += self.player.gravity 
            y += v
        max_decrease = max(0, y)
        return max_decrease
    
    def calculate_gap_position(self, y0, x_distance, gap_height):
        """
        Calculate the Y-position of the next obstacle's gap based on player physics.

        :param y0 (float): Y-coordinate of the previous obstacle's gap.
        :param x_distance (float): Horizontal distance to the next obstacle.
        :param gap_height (int): Height of the gap.
        :return (tuple[int, int, int]): Highest gap Y, lowest gap Y, random chosen gap Y.
        """
        max_inc = self.calculate_max_height_increase(x_distance)
        max_dec = self.calculate_max_height_decrease(x_distance)
        highest_gap_position = math.floor(max(0, y0 - max_inc))
        lowest_gap_position = math.ceil(min(HEIGHT - gap_height, y0 + max_dec))
        gap_position = random.randint(highest_gap_position, lowest_gap_position)
        return highest_gap_position, lowest_gap_position, gap_position
    
    def spawn_obstacle(self):
        """
        Spawn a new obstacle with a gap reachable by the player.

        :return: None
        """
        if not self.obstacles:
            prev_gap_y = HEIGHT // 2
            last_obstacle_x = WIDTH * 0.6
            last_obstacle_width = 0
        else:
            prev_obstacle = self.obstacles[-1]
            prev_gap_y = prev_obstacle.gap_y
            last_obstacle_x = prev_obstacle.world_x
            last_obstacle_width = prev_obstacle.width

        min_spawn_distance, max_spawn_distance, rand_spawn_distance = self.calculate_spawn_distance()
        d = rand_spawn_distance
        min_gap_height, max_gap_height, rand_gap_height = self.calculate_gap_height()
        h = rand_gap_height
        min_gap_position, max_gap_position, rand_gap_position = self.calculate_gap_position(prev_gap_y, d, h)
        y = rand_gap_position
        min_obstacle_width, max_obstacle_width, rand_obstacle_width = self.calculate_obstacle_width()
        w = rand_obstacle_width

        x = last_obstacle_x + last_obstacle_width + d

        if self.obstacles:
            self.obstacles.append(Obstacle(x, h, y, w))
        else:
            self.obstacles.append(Obstacle(x, h, 0, w))

    def update_world(self):
        """
        Update the game world: move world, spawn obstacles, update player, remove off-screen obstacles,
        and check for collisions.
        """
        if self.game_over:
            return 
        
        # Move the world to the left
        self.world_x += self.speed

        # Update the player's position on the screen
        self.player.update_position()

        # Spawn a new obstacle when the last-created obstacle appears on the screen
        if not self.obstacles or self.obstacles[-1].get_screen_x(self.world_x) < WIDTH:
            self.spawn_obstacle()

        # Remove obstacles that have gone off the screen
        self.obstacles = [o for o in self.obstacles if o.get_screen_x(self.world_x)+o.width > 0]

        # Check for collision
        if self.collision():
            self.game_over = True

    def draw_world(self):
        """
        Draw the current state of the game world including player, obstacles, and game over screen.
        """
        self.screen.fill((0, 0, 0))
        self.player.draw(self.screen)
        for o in self.obstacles:
            o.draw(self.screen, o.get_screen_x(self.world_x))

        if self.game_over:
            font = pygame.font.SysFont("Courier", 48, bold=True)
            lines = ["Game Over!", "YOU FUCKING SUCK.", "Press R to Restart"]
            total_height = len(lines) * font.get_linesize()
            start_y = HEIGHT // 2 - total_height // 2
            for i, line in enumerate(lines):
                text_surf = font.render(line, True, (255, 0, 0))
                rect = text_surf.get_rect(center=(WIDTH // 2, start_y + i * font.get_linesize()))
                self.screen.blit(text_surf, rect)

        pygame.display.update()

    def reset_game(self):
        """
        Reset the game to initial state after a collision.
        """
        self.player = Player()
        self.world_x = 0
        self.obstacles = []
        self.game_over = False


    def run(self):
        """
        Starts the game loop
        """
        while self.running:
            self.handle_events()
            self.update_world()
            self.draw_world()
            self.clock.tick(FPS)
        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()

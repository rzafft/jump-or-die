import pygame
import random
import math

# Dimensions for the game, player, etc.
WIDTH, HEIGHT = 700, 1000
PLAYER_RADIUS = int(HEIGHT * 0.01)

FPS = 60
COLORS = [
    (0, 0, 255),        # Blue
    (0, 255, 0),        # Green
    (255, 0, 0),        # Red
    (255, 255, 0),      # Yellow
    (255, 165, 0),      # Orange
    (128, 0, 128),      # Purple
    (0, 255, 255),      # Cyan
    (255, 192, 203),    # Pink
]
# ---------------------------------------------
# Player class
# ---------------------------------------------
class Player:

    def __init__(self):
        """
        Initialize the player obj with a default position, color, radius, and physical properties (e.g. velocity, gravity,
        and jump power)

        :attr x (int): The horizontal position of the player relative to the screen
        :attr y (float): The vertical position of the player relative to the screen
        :attr radius (int): The radius of the player's circle
        :attr color (tuple): The RGB color of the player
        :attr vel_y (float): The current velcity of player (positive vals move player down, negative vals move player up)
        :attr jump_power (float): The vertical velcity applied instantly when player jumps (negative so player moves down)
        :attr gravity (float): The acceleration applied downwards each frame
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
        Makes the player jump by setting the vertical velcoity to the jump power.
        The player will move upward in the next frames due to negative velocity
        """
        self.vel_y = self.jump_power

    def update_position(self):
        """
        Updates the players vertical position based on physics - i.e. apply gravity
        to the vertical velocity to bring the player downward, update the players 
        vertical position, and handle collisions with the ground and ceiling
        """
        # Apply physics
        self.vel_y += self.gravity
        self.y += self.vel_y

        # Ground collision
        if self.y >= (HEIGHT - self.radius):
            self.y = (HEIGHT - self.radius)
            self.vel_y = 0

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (self.x, int(self.y)), self.radius)


    def get_max_rise(self):
        """
        Calculate the maximum vertical distance the player can move upward 
        during a jump, based on current jump power and gravity.
        
        :return: Maximum upward displacement (float)
        """
        v0 = self.jump_power
        t_up = -v0 / self.gravity 
        rise = abs(v0 * t_up + 0.5 * self.gravity * t_up**2)
        return rise
    
    def get_min_gap(self):
        """
        Calculate the smallest possible gap that the player can jump through an survive
        """
        # compute maximum jump height (rise)
        rise = self.get_max_rise()
        # compute smallest safe gap the player can jump through
        return math.ceil((self.radius * 2) + rise)

    
# ---------------------------------------------
# Obstacle class
# ---------------------------------------------
class Obstacle:

    def __init__(self, x, gap, gap_y):
        """
        Initialize an obstacle in the game world with a specified vertical gap.

        :param x: The horizontal position of the obstacle in the world.
        :param gap: The vertical size of the gap between the top and bottom parts of the obstacle.
        :param gap_y: The vertical position (y-coordinate) of the top edge of the gap. 
                    This determines where the player can pass through. It is automatically 
                    clamped so that the gap stays fully on-screen.

        :attr world_x (int): Horizontal position of the obstacle in the world.
        :attr width (int): Width of the obstacle (randomly chosen within a range).
        :attr color (tuple): RGB color of the obstacle.
        :attr gap (int): Size of the vertical gap between the top and bottom rectangles.
        :attr gap_y (int): Y-coordinate of the top of the gap (clamped to stay on-screen).
        :attr r1_y (int): Y-coordinate of the top rectangle (always 0, fills space above gap).
        :attr r1_height (int): Height of the top rectangle (equals gap_y).
        :attr r2_y (int): Y-coordinate of the bottom rectangle (starts at gap_y + gap).
        :attr r2_height (int): Height of the bottom rectangle (fills remaining space below gap).

        The `gap_y` attribute is key for controlling the vertical position of the gap so that 
        it is reachable by the player based on physics (jump height) and distance from the 
        previous obstacle.
        """
        self.world_x = x
        self.width = random.randint(25, 25)
        self.color = random.choice(COLORS)

        # Store the gap information
        self.gap = gap
        self.gap_y = max(0, min(HEIGHT - gap, gap_y))

        # Top rectangle height is gap_y
        self.r1_y = 0
        self.r1_height = self.gap_y

        # Bottom rectangle height starts at gap_y + gap
        self.r2_y = self.gap_y + gap
        self.r2_height = HEIGHT - self.r2_y

    def get_screen_x(self, world_x):
        """
        Calculate the obstacles x position relative to the screen using world current
        x coordinate and the obstacles x coordinate in the world

        :param world_x: The current x coordinate of the world
        :return (int): The x coordinate of the obstacle on the screen
        """     
        return self.world_x - world_x

    def draw(self, screen, x):
        """
        Draw the obstacles top and bottom parts on the screen

        :param screen (pygame.Surface): The pygame surface to draw on
        :param x (int): The obstacles x coordinate relative to the screen
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

        :attr screen (pygame.Surface): The game window
        :attr player (Player): The player instance
        :attr clock (pygame.time.Clock): Clock to manage frames per second
        :attr running (bool): Determines whether the game loop is active
        :attr speed (int): The rate at which the world moves leftward
        :attr world_x (int): Horizontal offset of the world relative to the screen
        :attr min_spawn_distance (int): Minimum horizontal spacing between obstacles
        :attr max_spawn_distance (int): Maximum horizontal spacing between obstacles
        :attr obstacles (list): List of active obstacles in the world
        :attr game_over (bool): true when the game is over
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
        self.difficulty = 10
        self.min_gap_difficulty = {
            1: 2,
            2: 1.8,
            3: 1.8,
            4: 1.7,
            5: 1.7,
            6: 1.6,
            7: 1.5,
            8: 1.3,
            9: 1.3,
            10: 1.2,
            11: 1.1
        }
        self.max_gap_difficulty = {
            1: 2,
            2: 2,
            3: 1.9,
            4: 1.9,
            5: 1.8,
            6: 1.8,
            7: 1.7,
            8: 1.7,
            9: 1.6,
            10: 1.6,
            11: 1.5
        }
        self.min_distance_difficulty = {
            1: 2.0,
            2: 2.0,
            3: 2.0,
            4: 2.0,
            5: 2.0,
            6: 2.0,
            7: 2.0,
            8: 2.0,
            9: 2.0,
            10: 2.0,
            11: 2.0
        }
        self.max_distance_difficulty = {
            1: 10.0,
            2: 9.0,
            3: 8.0,
            4: 7.0,
            5: 6.0,
            6: 5.0,
            7: 4.0,
            8: 3.0,
            9: 2.0,
            10: 1.0,
            11: 0.0
        }


    def collision(self):
        """
        Determines if the player has collided with any obstacle in the game world.
        This checks collisions between the player's circular shape and both the
        top and bottom rectangles of each obstacle using proper circle-rectangle
        collision detection.

        :return (bool): True if the player collides with any obstacle, False otherwise.
        """
        for o in self.obstacles:
            x = o.get_screen_x(self.world_x)
            # Check collision with top and bottom rectangles
            for ry, rh in [(o.r1_y, o.r1_height), (o.r2_y, o.r2_height)]:
                # Find closest point on rectangle to player center
                closest_x = max(x, min(self.player.x, x + o.width))
                closest_y = max(ry, min(self.player.y, ry + rh))
                # Distance from circle center to closest point
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

    def calculate_gap_height(self):
        v0 = self.player.jump_power
        t_up = -v0 / self.player.gravity
        rise = abs(v0 * t_up + 0.5 * self.player.gravity  * (t_up**2))
        min_gap = int(((self.player.radius * 2) + rise) * 1.5)
        max_gap = min_gap 
        return random.randint(min_gap, max_gap)
        
    def calculate_spawn_distance(self):
        # Compute the distance a player travels in one jump
        vel_y = self.player.jump_power
        y = 0
        frames = 0
        while True:
            y += vel_y
            vel_y += self.player.gravity
            frames += 1
            if y >= 0:  
                break
        jump_distance_x = (frames*self.speed)
        min_dist = int(jump_distance_x / 2 + self.player.radius * 2)
        max_dist = int(jump_distance_x * 1.5 + self.player.radius * 2)
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
        horizontally toward the next obstacle.
        
        :param horizontal_distance: Distance to the next obstacle (pixels)
        :return: Maximum fall distance (positive number, pixels)
        """
        frames = math.floor(x / self.speed)
        v = 0
        y = 0
        for i in range(frames):
            v += self.player.gravity 
            y += v
        max_decrease = max(0, y)
        return max_decrease

    def calculate_gap_position(self, y0, x_distance, gap_height):
        """
        Given the distance to the next obstacle, calculate the lowest position 
        for the start of the next gap and the highest position for the start of
        the next gap, then choose a random value between the two heights
        """
        max_inc = self.calculate_max_height_increase(x_distance) # POSITIVE DECREASE IN HEIGHT
        max_dec = self.calculate_max_height_decrease(x_distance) # POSITIVE INCREASE IN HEIGHT
        highest_gap_position = math.floor(max(0, y0 - max_inc))
        lowest_gap_position = math.ceil(min(HEIGHT-gap_height, y0 + max_dec))
        gap_position = random.randint(highest_gap_position, lowest_gap_position)
        return highest_gap_position, lowest_gap_position, gap_position
    
    def spawn_obstacle(self):
        """
        Spawn a new obstacle with a gap that is reachable based on player physics
        and previous obstacle position.
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

        # Step 1: Determine spawn distance
        min_spawn_distance, max_spawn_distance, spawn_distance_random = self.calculate_spawn_distance()
        spawn_x = (last_obstacle_x + last_obstacle_width + min_spawn_distance)

        # Step 2: Chooe teh gap height 
        gap_height = self.calculate_gap_height()

        # Step 4: Choose the gap position
        gap_y_position_highest, gap_y_position_lowest, gap_y_position_random = self.calculate_gap_position(prev_gap_y, min_spawn_distance, gap_height)
                           

        self.obstacles.append(Obstacle(spawn_x, gap_height, gap_y_position_random))

    def update_world(self):
        """
        Update the game world for the current frame by moving the world leftware to
        simulate forward movement, spawning new obstacles, updating the players position, 
        and removing obstacles that are no longer on the screen
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
        Draws the current state of the game world by clearnign the screen, drawing the 
        player and all the obstacles, and updating the dipslay to show the new frame
        """
        # Draw the background
        self.screen.fill((0, 0, 0))

        # Draw the player
        self.player.draw(self.screen)

        # Draw the obstacles
        for o in self.obstacles:
            o.draw(self.screen, o.get_screen_x(self.world_x))

        if self.game_over:
            font = pygame.font.SysFont("Courier", 48, bold=True)
            lines = [
                "Game Over!",
                "YOU FUCKING SUCK.",
                "Press R to Restart"
            ]
            total_height = len(lines) * font.get_linesize()
            start_y = HEIGHT // 2 - total_height // 2
            for i, line in enumerate(lines):
                text_surf = font.render(line, True, (255, 0, 0))
                rect = text_surf.get_rect(center=(WIDTH // 2, start_y + i * font.get_linesize()))
                self.screen.blit(text_surf, rect)

        # Update the screen 
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

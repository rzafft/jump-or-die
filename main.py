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
        self.width = random.randint(25, 250)
        self.color = random.choice(COLORS)

        # Store the gap information
        self.gap = gap
        self.gap_y = max(0, min(HEIGHT - gap, gap_y))  # clamp to screen

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
        self.difficulty = 5
        self.gap_difficulty = {
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
        self.min_distance_difficulty = {
            1: 1.0,
            2: 1.0,
            3: 1.0,
            4: 1.0,
            5: 1.0,
            6: 1.0,
            7: 1.0,
            8: 1.0,
            9: 1.0,
            10: 1.0,
            11: 1.0
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

    def spawn_obstacle(self):
        """
        Spawn a new obstacle with a gap that is reachable based on player physics
        and previous obstacle position.
        """
        # ======================================================================
        # Get information about the previous obstacle to help create the new one

        if not self.obstacles:
            prev_gap_y = HEIGHT // 2
            last_obstacle_x = WIDTH * 0.6
            last_obstacle_width = 0
        else:
            prev_obstacle = self.obstacles[-1]
            prev_gap_y = prev_obstacle.gap_y
            last_obstacle_x = prev_obstacle.world_x
            last_obstacle_width = prev_obstacle.width

        # ======================================================================
        # Determine the height of the gap for the new obstacle

        # Calculate the maximum vertical distance that the player can move upward during a jump
        v0 = self.player.jump_power
        t_up = -v0 / self.player.gravity 
        rise = abs(v0 * t_up + 0.5 * self.player.gravity  * (t_up**2))

        # Determine the smallest gap that the player can jump through
        min_gap = math.ceil((self.player.radius*2) + rise * self.gap_difficulty[self.difficulty])

        # Determine the largest gap allowed in the game
        max_gap = int(min_gap * 2)

        # Choose the height of the gap
        gap = random.randint(min_gap, max_gap)

        # ======================================================================
        # Determine the position of the new obstacle

        min_spawn_distance = int(int(self.player.radius*2) * self.min_distance_difficulty[self.difficulty])
        max_spawn_distance = int(min_spawn_distance * self.max_distance_difficulty[self.difficulty])
        spawn_distance = random.randint(min_spawn_distance, max_spawn_distance)

        spawn_x = last_obstacle_x + last_obstacle_width + spawn_distance

        # Calculate the horizontal distance (in pixels) to the next obstacle
        dx = spawn_x - (last_obstacle_x + last_obstacle_width)

        # Calculate the number of frames until the next obstacle reaches the player
        frames_until_next_obstacle = dx / self.speed 

        # ======================================================================
        # Determine the the lowest possible position for the new gap that the player could fall to

        # Calculate the lowest possible position for the new gap that the player could reach if falling
        max_fall_distance = (1/2) * self.player.gravity * (frames_until_next_obstacle ** 2)
        lowest_gap_y = min(prev_gap_y + max_fall_distance, HEIGHT - gap)

        # ======================================================================
        # Determine the highest possible position for the new gap that the player could jump to

        jump_rate_per_sec = 4
        frames_between_jumps = FPS / jump_rate_per_sec
        vel = 0
        y_rise = 0
        frames = int(frames_until_next_obstacle)
        for f in range(frames):
            if f % int(frames_between_jumps) == 0:
                vel += self.player.jump_power
            vel += self.player.gravity
            y_rise -= vel 
        highest_gap_y = max(0, prev_gap_y - y_rise)

        # ======================================================================
        # Determine the position of the new gap

        # Determine the position of hte next gap
        low = int(lowest_gap_y)
        high = int(highest_gap_y)
        if low > high:
            low, high = high, low 
        gap_y = random.randint(low, high)
        gap_y = random.choice([low, high])


        # ======================================================================
        # Create the new obstacle 

        self.obstacles.append(Obstacle(spawn_x, gap, gap_y))

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

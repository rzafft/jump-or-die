import pygame
import random
 
WIDTH, HEIGHT = 500, 800
MIN_GAP = int(HEIGHT * 0.12)  
MAX_GAP = int(HEIGHT * 0.35)   
MIN_DIST = int(WIDTH * 0.15)   
MAX_DIST = int(WIDTH * 0.35)   
DIFFICULTY = 0.8
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
        self.x = WIDTH * 0.1       
        self.y = HEIGHT * 0.5     
        self.radius = int(HEIGHT * 0.02)
        self.color = (0, 0, 255)
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


# ---------------------------------------------
# Obstacle class
# ---------------------------------------------
class Obstacle:

    def __init__(self, x):
        """
        Initialize the obstacle, setting its position in the world and calcualte the size and position of its gap

        :attr world_x (int): The horizontal position of the obstacle in the world
        :attr color (tuple): The RGB color of th obstacle
        :attr width (int): The width of the obstacle
        :attr gap (int): The size of the vertical gap between the two parts of the obstacle
        :attr r1_height (int): Height of the top part of the obstacle
        :attr r2_height (int): Height of the bottom part of the obstacle
        :attr r1_y (int): Vertical position of the top part of the obstacle (always 0)
        :attr r2_y (int): Vertical position of the bottom part of the obstacle
        """
        self.world_x = x                                                                                        
        self.color = random.choice(COLORS)
        self.width = random.randint(25, 250)                                     
        self.gap = random.randint(MIN_GAP, MAX_GAP)   
        self.r1_height = random.randint(0, (HEIGHT - self.gap))
        self.r2_height = HEIGHT - self.r1_height - self.gap
        self.r1_y = 0
        self.r2_y = self.r1_height + self.gap   

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
        self.min_spawn_distance = MIN_DIST     
        self.max_spawn_distance = MAX_DIST       
        self.obstacles = [Obstacle(WIDTH)]  
        self.game_over = False 

    def collision(self):
        """
        Determines if the player has collided with an obsticle
        
        :return (bool): Whether or not the player has collided with an obstacle
        """
        for o in self.obstacles:
            x = o.get_screen_x(self.world_x)
            if (x < self.player.x + self.player.radius < x + o.width) or (x < self.player.x - self.player.radius < x + o.width):
                if (self.player.y + self.player.radius > o.r2_y) or (self.player.y - self.player.radius < o.r1_height):
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
        last_obstacle = self.obstacles[-1]
        if last_obstacle.get_screen_x(self.world_x) < WIDTH:
            new_obstacle_pos_in_world = (last_obstacle.world_x + last_obstacle.width) + random.randint(self.min_spawn_distance, self.max_spawn_distance)
            self.obstacles.append(Obstacle(new_obstacle_pos_in_world))

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
        self.obstacles = [Obstacle(WIDTH)]
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
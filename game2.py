import pygame
import random

# Set up the screen dimensions and maximum speed for agents
WIDTH = 1280
HEIGHT = 720
MAX_SPEED = 5
NUMBER_AGENT = 100  # Number of agents (fish) in the simulation
FOOD_RADIUS = 50  # Radius within which fish will detect food
HUNGER_THRESHOLD = 60  # Hunger level at which fish will seek food
FOOD_DROP_INTERVAL = 30  # Interval for dropping food (frames)

# Factors controlling the behavior of the agents
COHERENCE_FACTOR = 0.01  # Controls how strongly agents are attracted to the center of mass
ALIGNMENT_FACTOR = 0.1  # Controls how strongly agents align their direction with others
SEPARATION_FACTOR = 0.05  # Controls how strongly agents avoid each other
SEPARATION_DIST = 25  # Minimum distance to maintain between agents
ZONE_OF_WALL = 5  # Zone around the wall where agents will be repelled
WALL_CONST = 2.0  # Force applied when agents are near the wall

# -----------------------------------------------------------------------
# Agent class represents each moving entity in the simulation
# -----------------------------------------------------------------------

class Agent:
    def __init__(self, x, y) -> None:
        self.position = pygame.Vector2(x, y)
        self.velocity = pygame.Vector2(
            random.uniform(-MAX_SPEED, MAX_SPEED), random.uniform(-MAX_SPEED, MAX_SPEED))
        self.acceleration = pygame.Vector2(0, 0)
        self.mass = 1
        self.hunger = random.randint(0, 60)  # Initialize hunger level randomly
        self.hunger_decrement = 0.05  # Rate at which hunger increases over time
        self.target_food = None  # To track the current food target
        self.font = pygame.font.Font(None, 24)  # Font for rendering hunger text

    def update(self, agents, foods):
        # Increment hunger level over time
        if self.hunger < 100:
            self.hunger += self.hunger_decrement
            self.hunger = min(100, self.hunger)  # Cap hunger at 100

        if self.hunger > HUNGER_THRESHOLD and foods:
            self.find_nearest_food(foods)
            if self.target_food:
                self.seek(self.target_food.position)
                # Check if the agent is close enough to the food to eat it
                if self.position.distance_to(self.target_food.position) < FOOD_RADIUS:
                    self.eat_food(foods)
                    self.target_food = None  # Clear the target food after eating
            else:
                # No food found, fallback to normal behavior
                self.coherence(agents)
                self.separation(agents)
                self.alignment(agents)
        else:
            # Normal behavior when not hungry or no food available
            self.coherence(agents)
            self.separation(agents)
            self.alignment(agents)

        self.velocity += self.acceleration
        if self.velocity.length() > MAX_SPEED:
            self.velocity = self.velocity.normalize() * MAX_SPEED
        self.position += self.velocity
        self.acceleration = pygame.Vector2(0, 0)

        # Calculate and apply wall forces
        wall_forces = self.calc_wall_forces(WIDTH, HEIGHT)
        self.apply_force(wall_forces[0], wall_forces[1])

    def apply_force(self, x, y):
        force = pygame.Vector2(x, y)
        self.acceleration += force / self.mass

    def seek(self, target_pos):
        d = target_pos - self.position
        d = d.normalize() * 0.1
        seeking_force = d
        self.apply_force(seeking_force.x, seeking_force.y)

    def find_nearest_food(self, foods):
        nearest_food = None
        nearest_distance = float('inf')
        for food in foods:
            distance = self.position.distance_to(food.position)
            if distance < nearest_distance:
                nearest_food = food
                nearest_distance = distance
        self.target_food = nearest_food

    def eat_food(self, foods):
        if self.hunger > HUNGER_THRESHOLD:
            self.hunger = max(0, self.hunger - 100)  # Decrease hunger by 100 after eating food
            # Remove the food from the list
            foods[:] = [food for food in foods if food.position != self.target_food.position]

    def coherence(self, agents):
        center_of_mass = pygame.Vector2(0, 0)
        agent_in_range_count = 0
        for agent in agents:
            if agent != self:
                dist = self.position.distance_to(agent.position)
                if dist < 100:
                    center_of_mass += agent.position
                    agent_in_range_count += 1

        if agent_in_range_count > 0:
            center_of_mass /= agent_in_range_count
            d = center_of_mass - self.position
            f = d * COHERENCE_FACTOR
            self.apply_force(f.x, f.y)

    def separation(self, agents):
        d = pygame.Vector2(0, 0)
        for agent in agents:
            if agent != self:
                dist = self.position.distance_to(agent.position)
                if dist < SEPARATION_DIST:
                    d += self.position - agent.position

        separation_force = d * SEPARATION_FACTOR
        self.apply_force(separation_force.x, separation_force.y)

    def alignment(self, agents):
        v = pygame.Vector2(0, 0)
        agent_in_range_count = 0
        for agent in agents:
            if agent != self:
                dist = self.position.distance_to(agent.position)
                if dist < 100:
                    v += agent.velocity
                    agent_in_range_count += 1

        if agent_in_range_count > 0:
            v /= agent_in_range_count
            alignment_force = v * ALIGNMENT_FACTOR
            self.apply_force(alignment_force.x, alignment_force.y)

    def draw(self, screen):
        color = (255, 0, 0) if self.hunger > HUNGER_THRESHOLD else (0, 255, 0)
        pygame.draw.circle(screen, color, self.position, 10)
        # Render and display hunger level
        #hunger_text = self.font.render(f"{self.hunger}", True, (255, 255, 255))
        #screen.blit(hunger_text, (self.position.x - hunger_text.get_width() // 2, self.position.y - hunger_text.get_height() // 2))

    def calc_wall_forces(self, width, height):
        """Calculate the inward force of a wall, which is very short range. Either 0 or CONST."""
        F_x, F_y = 0, 0
        if self.position.x < ZONE_OF_WALL:
            F_x += WALL_CONST
        elif self.position.x > (width - ZONE_OF_WALL):
            F_x -= WALL_CONST
        if self.position.y < ZONE_OF_WALL:
            F_y += WALL_CONST
        elif self.position.y > (height - ZONE_OF_WALL):
            F_y -= WALL_CONST
        return F_x, F_y

# -----------------------------------------------------------------------
# Food class represents food items in the simulation
# -----------------------------------------------------------------------

class Food:
    def __init__(self, x, y):
        self.position = pygame.Vector2(x, y)

    def draw(self, screen):
        pygame.draw.circle(screen, (0, 255, 255), self.position, 5)

# -----------------------------------------------------------------------
#  Begin
# -----------------------------------------------------------------------

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)

agents = [Agent(random.uniform(0, WIDTH), random.uniform(0, HEIGHT)) for _ in range(NUMBER_AGENT)]
foods = []
food_timer = 0

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            foods.append(Food(x, y))

    screen.fill((128, 128, 128))

    for agent in agents:
        agent.update(agents, foods)
        agent.draw(screen)

    for food in foods:
        food.draw(screen)

    food_timer += 1
    if food_timer >= FOOD_DROP_INTERVAL:
        food_timer = 0

    

    fps = int(clock.get_fps())
    fps_text = font.render(f"FPS: {fps}", True, pygame.Color('white'))
    screen.blit(fps_text, (WIDTH - fps_text.get_width() - 10, 10))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()

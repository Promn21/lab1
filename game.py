import pygame
import random
import math
import time

WIDTH = 1920
HEIGHT = 1080
MAX_SPEED = 5
MAX_AGENTS = 95
SPAWN_INTERVAL = 0.5  # Time in seconds between spawns

COHERENCE_FACTOR = 0.05
ALIGNMENT_FACTOR = 0.05
SEPARATION_FACTOR = 1
SEPARATION_DIST = 100

class Agent:
    def __init__(self, x, y) -> None:
        self.position = pygame.Vector2(x, y)
        self.velocity = pygame.Vector2(0, 0)
        self.acceleration = pygame.Vector2(0, 0)
        self.mass = 1
        self.max_force = 0.2  # Maximum steering force

    def update(self):
        self.velocity += self.acceleration
        if self.velocity.length() > MAX_SPEED:
            self.velocity = self.velocity.normalize() * MAX_SPEED
        self.position += self.velocity
        self.acceleration = pygame.Vector2(0, 0)

    def apply_force(self, x, y):
        force = pygame.Vector2(x, y)
        if force.length() > self.max_force:
            force = force.normalize() * self.max_force
        self.acceleration += (force / self.mass)

    def seek(self, x, y):
        dir = pygame.Vector2(x, y) - self.position
        distance = dir.length()
        
        if distance > 500:
            speed_factor = 0.2
        elif distance > 300:
            speed_factor = 0.8
        else:
            speed_factor = 0.3

        steering_force = dir.normalize() * speed_factor
        self.apply_force(steering_force.x, steering_force.y)

    def coherence(self, agents):
        center_of_mass = pygame.Vector2(0, 0)
        agent_in_range_count = 0
        
        for agent in agents:
            if agent != self:
                dist = math.sqrt((self.position.x - agent.position.x)**2 
                        + (self.position.y - agent.position.y)**2)
                if dist < 200:
                    center_of_mass += agent.position
                    agent_in_range_count += 1
        
        if agent_in_range_count > 0:
            center_of_mass /= agent_in_range_count 

        dir = center_of_mass - self.position
        force = dir.normalize() * COHERENCE_FACTOR
        self.apply_force(force.x, force.y) 
    
    def separation(self, agents):
        dir = pygame.Vector2(0, 0)
        for agent in agents:
            dist = math.sqrt((self.position.x - agent.position.x)**2 
                        + (self.position.y - agent.position.y)**2)
            if dist < SEPARATION_DIST:
                dir += self.position - agent.position
            
        separation_force = dir * SEPARATION_FACTOR
        self.apply_force(separation_force.x, separation_force.y)    

    def alignment(self, agents):
        v = pygame.Vector2(0, 0)
        num_agents = len(agents) - 1  # Exclude self

        if num_agents > 0:  # Ensure there are other agents to align with
            for agent in agents:
                if agent != self:
                    v += agent.velocity
            
            v /= num_agents
            alignment_force = v * ALIGNMENT_FACTOR
            self.apply_force(alignment_force.x, alignment_force.y)

    def draw(self):
        pygame.draw.circle(screen, "white", self.position, 50, width=2)
        pygame.draw.circle(screen, "red", self.position, 25)

def spawn_far_from_player(player, min_distance, max_distance):
    angle = random.uniform(0, 2 * math.pi)  # Random direction
    distance = random.uniform(min_distance, max_distance)  # Random distance in a given range
    x = player.x + distance * math.cos(angle)
    y = player.y + distance * math.sin(angle)

    if x < -50: x = -50
    if x > WIDTH + 50: x = WIDTH + 50
    if y < -50: y = -50
    if y > HEIGHT + 50: y = HEIGHT + 50

    return Agent(x, y)

# ----- pygame setup ------
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Homework")
clock = pygame.time.Clock()

#----- player setup -----
player = pygame.Vector2(960, 540)
player_radius = 10
velocity = 5

# Initialize target position as player position
target_position = pygame.Vector2(player.x, player.y)
move_speed = 60  # Movement speed
stop_threshold = 60  # Distance threshold to stop movement

# Initialize agents
agents = []

# Track time for spawning
last_spawn_time = time.time()

running = True

while running:
    current_time = time.time()
    
    screen.fill("grey")

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            target_position = pygame.Vector2(event.pos)
        
    pygame.draw.circle(screen, "black", (int(player.x), int(player.y)), player_radius)

    # Check if it's time to spawn a new agent
    if current_time - last_spawn_time >= SPAWN_INTERVAL and len(agents) < MAX_AGENTS:
        new_agent = spawn_far_from_player(player, min_distance=1500, max_distance=1920)
        agents.append(new_agent)
        last_spawn_time = current_time

    # Move player towards target position
    direction = target_position - player
    if direction.length() > stop_threshold:  # Only move if beyond the stop threshold
        direction = direction.normalize() * move_speed
        player += direction

    
    
    
    
    for agent in agents:
        agent.seek(player.x, player.y)
        agent.coherence(agents)
        agent.separation(agents)
        agent.alignment(agents)
        agent.update()
        agent.draw()
    
    pygame.display.update()
    pygame.display.flip()

    clock.tick(60)

pygame.quit()

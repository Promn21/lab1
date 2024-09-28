import pygame
import random
import math

# Screen dimensions
WIDTH = 1152
HEIGHT = 1000
screen = pygame.display.set_mode((WIDTH, HEIGHT))

# Constants
MAX_SPEED = 3
MAX_AGENT = float('inf') 
MAX_HUMAN = 100

HUNGER_THRESHOLD = 60
HUNGER_MAX = 100
EAT_DISTANCE = 25  # Distance at which agents can transform humans

COHERENCE_FACTOR = 0.01
ALIGNMENT_FACTOR = 0.1
SEPARATION_FACTOR = 0.05
SEPARATION_DIST = 35

# Wall bounce
ZONE_OF_WALL = 5
WALL_CONST = 2.0

# Load the map and collision images
map_image = pygame.image.load('C:/Users/WIN/Documents/GitHub/lab1/Assets/Sprite and Map/Tilemap/resident.png').convert()
# Define a scale factor
MAP_SCALE = 1  # Adjust this value to scale your map (0.5 = 50% size)

class Agent:
    def __init__(self, x, y):
        self.position = pygame.Vector2(x, y)
        self.velocity = pygame.Vector2(
            random.uniform(-MAX_SPEED, MAX_SPEED), random.uniform(-MAX_SPEED, MAX_SPEED))
        self.acceleration = pygame.Vector2(0, 0)
        self.mass = 1
        
        # Hunger
        self.hunger = random.randint(0, HUNGER_MAX)  # Agents spawn with random hunger value
        self.hungerIncreaseRate = 0.09
        self.targetHuman = None  # Agent's target human

    def update(self):
        self.velocity += self.acceleration
        if self.velocity.length() > MAX_SPEED:
            self.velocity = self.velocity.normalize() * MAX_SPEED
        self.position += self.velocity
        self.acceleration = pygame.Vector2(0, 0)
        
        # Hunger increases over time
        if self.hunger < HUNGER_MAX:
            self.hunger += self.hungerIncreaseRate  # Increase hunger
            self.hunger = min(HUNGER_MAX, self.hunger)  # Cap hunger at max value
        
        # Wall bounce
        wallForce = self.wallBounce(WIDTH, HEIGHT)
        self.applyForce(wallForce[0], wallForce[1])

    def applyForce(self, x, y):
        force = pygame.Vector2(x, y)
        self.acceleration += force / self.mass

    def hungry(self, agents, humans):
        if self.hunger > HUNGER_THRESHOLD and humans:
            self.findNearestHuman(humans)
            if self.targetHuman:
                self.seek(self.targetHuman.position)  # Seek human position
                if self.position.distance_to(self.targetHuman.position) < EAT_DISTANCE:
                    self.transformHuman(humans)  # Transform human into agent
                    self.targetHuman = None
            else:
                self.coherence(agents)
                self.separation(agents)
                self.alignment(agents)
        else:
            self.coherence(agents)
            self.separation(agents)
            self.alignment(agents)
    
    def findNearestHuman(self, humans):
        nearestHuman = None
        nearestDist = float('inf')
        for human in humans:
            dist = self.position.distance_to(human.position)
            if dist < nearestDist:
                nearestHuman = human
                nearestDist = dist
        self.targetHuman = nearestHuman

    def transformHuman(self, humans):
        # Create a new agent at the human's position
        new_agent = Agent(self.targetHuman.position.x, self.targetHuman.position.y)
        # Add the new agent to the agents list
        agents.append(new_agent)
        # Remove the human from the simulation
        humans.remove(self.targetHuman)

    def seek(self, targetPosition):
        dir = targetPosition - self.position
        dir = dir.normalize() * 0.1
        seekingForce = dir
        MAX_SPEED = 5
        self.applyForce(seekingForce.x, seekingForce.y)

    def coherence(self, agents):
        centerOfMass = pygame.Vector2(0, 0)
        agentInRangeCount = 0
        for agent in agents:
            if agent != self:
                dist = self.position.distance_to(agent.position)
                if dist < 100:  # Only consider nearby agents within 100 units
                    centerOfMass += agent.position
                    agentInRangeCount += 1

        if agentInRangeCount > 0:
            centerOfMass /= agentInRangeCount  # Calculate average position
            dir = centerOfMass - self.position
            f = dir * COHERENCE_FACTOR 
            self.applyForce(f.x, f.y)  # Apply coherence force

    def separation(self, agents):
        # Steer to avoid crowding neighbors (separation behavior)
        dir = pygame.Vector2(0, 0)
        for agent in agents:
            if agent != self:
                dist = self.position.distance_to(agent.position)
                if dist < SEPARATION_DIST:  # Only consider agents within separation distance
                    dir += self.position - agent.position
            
        separationForce = dir * SEPARATION_FACTOR
        self.applyForce(separationForce.x, separationForce.y)

    def alignment(self, agents):
        # Steer towards the average heading (velocity) of nearby agents (alignment behavior)
        velo = pygame.Vector2(0, 0)
        agentInRangeCount = 0
        for agent in agents:
            if agent != self:
                dist = self.position.distance_to(agent.position)
                if dist < 100:  # Only consider nearby agents within 100 units
                    velo += agent.velocity
                    agentInRangeCount += 1

        if agentInRangeCount > 0:
            velo /= agentInRangeCount  # Calculate average velocity
            alignmentForce = velo * ALIGNMENT_FACTOR  # Apply alignment force
            self.applyForce(alignmentForce.x, alignmentForce.y)

    def draw(self, screen):
        pygame.draw.circle(screen, "white", (int(self.position.x), int(self.position.y)), 12, width=2)
        color = ("red") if self.hunger > HUNGER_THRESHOLD else ("yellow")
        pygame.draw.circle(screen, color, (int(self.position.x), int(self.position.y)), 4)

    def wallBounce(self, WIDTH, HEIGHT):
        wallX, wallY = 0, 0
        if self.position.x < ZONE_OF_WALL:
            wallX += WALL_CONST
        elif self.position.x > (WIDTH - ZONE_OF_WALL):
            wallX -= WALL_CONST
        if self.position.y < ZONE_OF_WALL:
            wallY += WALL_CONST
        if self.position.y > (HEIGHT - ZONE_OF_WALL):
            wallY -= WALL_CONST
        return wallX, wallY

class Human:
    def __init__(self, x, y):
        self.position = pygame.Vector2(x, y)
        self.velocity = pygame.Vector2(
            random.uniform(-MAX_SPEED, MAX_SPEED), random.uniform(-MAX_SPEED, MAX_SPEED))
        self.acceleration = pygame.Vector2(0, 0)
        self.mass = 1

    def update(self):
        # Make the human run away from the nearest agent
        nearest_agent = self.findNearestAgent(agents)
        if nearest_agent:
            self.flee(nearest_agent.position)
        
        # Update position, velocity, and wall bouncing like normal
        self.velocity += self.acceleration
        if self.velocity.length() > MAX_SPEED:
            self.velocity = self.velocity.normalize() * MAX_SPEED
        self.position += self.velocity
        self.acceleration = pygame.Vector2(0, 0)
        
        # Apply wall bounce logic
        wallForce = self.wallBounce(WIDTH, HEIGHT)
        self.applyForce(wallForce[0], wallForce[1])

    def applyForce(self, x, y):
        force = pygame.Vector2(x, y)
        self.acceleration += force / self.mass

    def findNearestAgent(self, agents):
        nearest_agent = None
        nearestDist = float('inf')
        for agent in agents:
            dist = self.position.distance_to(agent.position)
            if dist < nearestDist:
                nearest_agent = agent
                nearestDist = dist
        return nearest_agent

    def flee(self, targetPosition):
        # Reverse the seeking force to flee from the nearest agent
        dir = self.position - targetPosition
        if dir.length() > 0:
            dir = dir.normalize() * 0.1
            fleeForce = dir
            self.applyForce(fleeForce.x, fleeForce.y)

    def wallBounce(self, WIDTH, HEIGHT):
        wallX, wallY = 0, 0
        if self.position.x < ZONE_OF_WALL:
            wallX += WALL_CONST
        elif self.position.x > (WIDTH - ZONE_OF_WALL):
            wallX -= WALL_CONST
        if self.position.y < ZONE_OF_WALL:
            wallY += WALL_CONST
        if self.position.y > (HEIGHT - ZONE_OF_WALL):
            wallY -= WALL_CONST
        return wallX, wallY

    def draw(self, screen):
        pygame.draw.circle(screen, "blue", (int(self.position.x), int(self.position.y)), 12, width=2)
        pygame.draw.circle(screen, "green", (int(self.position.x), int(self.position.y)), 4)

# ----- pygame setup ------
pygame.display.set_caption("Agent Simulation")
pygame.init()
clock = pygame.time.Clock()

# Initialize agents and humans
agents = []
humans = [Human(random.randint(0, WIDTH), random.randint(0, HEIGHT)) for _ in range(MAX_HUMAN)]

# ----- Main loop -----
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Spawn 1 to 5 agents at the mouse click position
            x, y = event.pos
            num_agents_to_spawn = random.randint(1, 3)  # Randomly choose number of agents to spawn (1-5)
            for _ in range(num_agents_to_spawn):
                if len(agents) < MAX_AGENT:
                    agents.append(Agent(x, y))  # Spawn agent

 # Draw the map
    scaled_map = pygame.transform.scale(map_image, (WIDTH * MAP_SCALE, HEIGHT * MAP_SCALE))
    screen.blit(scaled_map, (0, 0))

    for agent in agents:
        agent.hungry(agents, humans)  # Update agent behavior based on hunger
        agent.update()  # Update agent position
        agent.draw(screen)  # Draw agent

    # Update and draw humans
    for human in humans:
        human.update()  # Update human position
        human.draw(screen)  # Draw human

    pygame.display.flip()  # Update the display
    clock.tick(60)  # Limit the frame rate to 60 FPS

pygame.quit()

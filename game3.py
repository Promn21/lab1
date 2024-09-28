import pygame
import random
import math
import pytmx


# Screen dimensions
WIDTH = 1037
HEIGHT = 1037
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
WALL_CONST = 4

# Load the map and collision images
map_image = pygame.image.load('C:/Users/WIN/Documents/GitHub/lab1/Assets/Sprite and Map/Tilemap/resident.png').convert()
# Define a scale factor
MAP_SCALE = 1  # Adjust this value to scale your map (0.5 = 50% size)
OBJECT_SCALE = MAP_SCALE * 1.355  # Adjust for objects being half the size

# Load the TMX file for obstacles
tmx_data = pytmx.load_pygame('C:/Users/WIN/Documents/GitHub/lab1/Assets/Objects.tmx')  # Replace with your TMX file path
obstacles = []



# Extract the object layer and create rectangles for obstacles
for obj in tmx_data.objects:
    if obj.name == "Obstacle":  # Adjust based on your TMX object names
        # Apply scaling to position and size
        scaled_rect = pygame.Rect(obj.x * OBJECT_SCALE, obj.y * OBJECT_SCALE, obj.width * OBJECT_SCALE, obj.height * OBJECT_SCALE)
        obstacles.append(scaled_rect)

class Agent:
    def __init__(self, x, y):
        self.position = pygame.Vector2(x, y)
        self.velocity = pygame.Vector2(
            random.uniform(-MAX_SPEED, MAX_SPEED), random.uniform(-MAX_SPEED, MAX_SPEED))
        self.acceleration = pygame.Vector2(0, 0)
        self.mass = 1
        
        # Hunger
        self.hunger = random.randint(1, HUNGER_MAX)  # Agents spawn with random hunger value
        self.hungerIncreaseRate = 0.1
        self.targetHuman = None  # Agent's target human

        self.spriteSheets = [
            pygame.image.load('C:/Users/WIN/Documents/GitHub/lab1/Assets/ghostsspritesheet_1.png').convert_alpha(),
            pygame.image.load('C:/Users/WIN/Documents/GitHub/lab1/Assets/ghostsspritesheet_2.png').convert_alpha(),
            pygame.image.load('C:/Users/WIN/Documents/GitHub/lab1/Assets/ghostsspritesheet_3.png').convert_alpha(),
            pygame.image.load('C:/Users/WIN/Documents/GitHub/lab1/Assets/ghostsspritesheet_4.png').convert_alpha() ]
        
        self.currentSheet = random.choice(self.spriteSheets)
        self.frameIndex = 0
        self.frameCount = 6  # Total frames
        self.spriteWidth = self.currentSheet.get_width() // self.frameCount   # Calculate sprite width
        self.spriteHeight = self.currentSheet.get_height()  # Assuming all sprites have the same height
        self.animationSpeed = 0.1  # Adjust this value for speed of animation
        self.animationTimer = 0.0

    def update(self):
        self.velocity += self.acceleration
        if self.velocity.length() > MAX_SPEED:
            self.velocity = self.velocity.normalize() * MAX_SPEED
        self.position += self.velocity
        self.acceleration = pygame.Vector2(0, 0)

        # Wall bounce
        wallForce = self.wallBounce(WIDTH, HEIGHT)
        self.applyForce(wallForce[0], wallForce[1])

        self.animationTimer += self.animationSpeed
        if self.animationTimer >= 1.0:  # Update every second
            self.frameIndex = (self.frameIndex + 1) % self.frameCount
            self.animationTimer = 0.0



    def applyForce(self, x, y):
        force = pygame.Vector2(x, y)
        self.acceleration += force / self.mass

    def hungry(self, agents, humans):
        if self.hunger < 100:
            self.hunger += self.hungerIncreaseRate
            self.hunger = min(100, self.hunger) 

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
        if self.hunger > HUNGER_THRESHOLD:
            self.hunger = max(0, self.hunger - 100)

        new_agent = Agent(self.targetHuman.position.x, self.targetHuman.position.y)
        # Add the new agent to the agents list
        agents.append(new_agent)
        # Remove the human from the simulation
        humans.remove(self.targetHuman)

    def seek(self, targetPosition):
        dir = targetPosition - self.position
        dir = dir.normalize() * 0.1
        seekingForce = dir
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
        spriteHeight = self.currentSheet.get_height()  # Assuming all sprites have the same height
        frameRect = pygame.Rect(self.frameIndex * self.spriteWidth, 0, self.spriteWidth, spriteHeight)

        # Define the desired scale factor
        scaleFactor = 2  # Change this to increase or decrease the size

        # Scale the sprite before drawing
        scaledSprite = pygame.transform.scale(self.currentSheet.subsurface(frameRect), 
                                                (int(self.spriteWidth * scaleFactor), int(spriteHeight * scaleFactor)))
        
        circle_color = "purple" if self.hunger > HUNGER_THRESHOLD else "yellow"
        pygame.draw.circle(screen, circle_color, (int(self.position.x), int(self.position.y)), 20, width=2)

        # Draw the scaled sprite
        screen.blit(scaledSprite, (self.position.x - (self.spriteWidth * scaleFactor) // 2, 
                                    self.position.y - (spriteHeight * scaleFactor) // 2))
        

    def avoidObstacles(self, obstacles):
        for obstacle in obstacles:
            if obstacle.collidepoint(self.position):
                # Reflect the velocity when colliding with an obstacle
                self.velocity = -self.velocity  # Reverse the direction of the velocity
                self.position += self.velocity  # Move the agent slightly in the opposite direction

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

class Human(Agent):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.spriteSheets = [
            pygame.image.load('C:/Users/WIN/Documents/GitHub/lab1/Assets/eldersspritesheet_1.png').convert_alpha(),
            pygame.image.load('C:/Users/WIN/Documents/GitHub/lab1/Assets/eldersspritesheet_2.png').convert_alpha(),
            pygame.image.load('C:/Users/WIN/Documents/GitHub/lab1/Assets/eldersspritesheet_3.png').convert_alpha(),
            pygame.image.load('C:/Users/WIN/Documents/GitHub/lab1/Assets/eldersspritesheet_4.png').convert_alpha() ]
        
       

        self.currentSheet = random.choice(self.spriteSheets)
        self.frameIndex = 0
        self.frameCount = 6  # Total frames
        self.spriteWidth = self.currentSheet.get_width() // self.frameCount   # Calculate sprite width
        self.spriteHeight = self.currentSheet.get_height()  # Assuming all sprites have the same height
        self.animationSpeed = 0.1  # Adjust this value for speed of animation
        self.animationTimer = 0.0


        self.MIN_SPEED = -1   
        self.MAX_SPEED = 5

    def update(self, obstacles):
        
        # Make the human run away from the nearest agent
        nearestAgent = self.findNearestAgent(agents)

        if nearestAgent:
            dist = self.position.distance_to(nearestAgent.position)
            if dist < 300:  # If within 100 pixels, use normal speed
                speed = self.MAX_SPEED
            else:  # Otherwise, use slow speed
                speed = self.MIN_SPEED
            
            self.flee(nearestAgent.position)  # Make the human run away from the nearest agent

            # Update position, velocity, and wall bouncing like normal
            self.velocity += self.acceleration
            if self.velocity.length() > MAX_SPEED:
                self.velocity = self.velocity.normalize() * MAX_SPEED
        
        # Update position, velocity, and wall bouncing like normal
        self.velocity += self.acceleration
        if self.velocity.length() > MAX_SPEED:
            self.velocity = self.velocity.normalize() * MAX_SPEED
        self.position += self.velocity
        self.acceleration = pygame.Vector2(0, 0)

        # Apply obstacle avoidance logic
        self.avoidObstacles(obstacles)

        # Apply wall bounce logic
        wallForce = self.wallBounce(WIDTH, HEIGHT)
        self.applyForce(wallForce[0], wallForce[1])

        self.animationTimer += self.animationSpeed
        if self.animationTimer >= 1.0:  # Update every second
            self.frameIndex = (self.frameIndex + 1) % self.frameCount
            self.animationTimer = 0.0


    def flee(self, targetPosition):
        dir = self.position - targetPosition
        dir = dir.normalize() * 0.1
        fleeingForce = dir
        self.applyForce(fleeingForce.x, fleeingForce.y)

    def findNearestAgent(self, agents):
        nearestAgent = None
        nearestDist = 300
        for agent in agents:
            dist = self.position.distance_to(agent.position)
            if dist < nearestDist:
                nearestAgent = agent
                nearestDist = dist
        return nearestAgent
    

    def draw(self, screen):
        spriteHeight = self.currentSheet.get_height()  # Assuming all sprites have the same height
        frameRect = pygame.Rect(self.frameIndex * self.spriteWidth, 0, self.spriteWidth, spriteHeight)

        # Define the desired scale factor
        scaleFactor = 2  # Change this to increase or decrease the size

        # Scale the sprite before drawing
        scaledSprite = pygame.transform.scale(self.currentSheet.subsurface(frameRect), 
                                                (int(self.spriteWidth * scaleFactor), int(spriteHeight * scaleFactor)))

        # Draw the scaled sprite
        screen.blit(scaledSprite, (self.position.x - (self.spriteWidth * scaleFactor) // 2, 
                                    self.position.y - (spriteHeight * scaleFactor) // 2))


def random_position_avoiding_obstacles(obstacles):
    while True:
        x = random.randint(0, WIDTH)
        y = random.randint(0, HEIGHT)
        new_human_rect = pygame.Rect(x, y, 16, 16) 
        if not any(obstacle.colliderect(new_human_rect) for obstacle in obstacles):
            return (x, y)

def can_spawn_agent(position, obstacles):
    """Check if the position collides with any obstacles."""
    spawn_rect = pygame.Rect(position[0], position[1], 16, 16)  
    return not any(obstacle.colliderect(spawn_rect) for obstacle in obstacles)

# Initialize Pygame
pygame.init()
clock = pygame.time.Clock()
agents = []
humans = []
for _ in range(MAX_HUMAN):
    x, y = random_position_avoiding_obstacles(obstacles)
    humans.append(Human(x, y))

# Game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Spawn 1 to 5 agents at the mouse click position
            x, y = event.pos
            if can_spawn_agent((x, y), obstacles):  # Check if the spawn position is valid
                num_agents_to_spawn = random.randint(1, 3)  # Randomly choose number of agents to spawn (1-5)
                for _ in range(num_agents_to_spawn):
                    if len(agents) < MAX_AGENT:
                        agents.append(Agent(x, y))

     # Draw the map
    scaled_map = pygame.transform.scale(map_image, (WIDTH * MAP_SCALE, HEIGHT * MAP_SCALE))
    screen.blit(scaled_map, (0, 0))

    #for obstacle in obstacles:
     #   pygame.draw.rect(screen, (255, 0, 0), obstacle)

    for agent in agents:
        agent.hungry(agents, humans)
        agent.avoidObstacles(obstacles)  # Avoid obstacles
        agent.update()  # Update agent position
        agent.draw(screen)  # Draw agent

    for human in humans:
        human.update(obstacles)  # Update human position
        human.draw(screen)  # Draw human

    pygame.display.flip()
    clock.tick(60)

pygame.quit()

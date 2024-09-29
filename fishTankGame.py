import pygame
import random
import math
import pytmx

WIDTH = 1037
HEIGHT = 1037
screen = pygame.display.set_mode((WIDTH, HEIGHT))

# Constants
MAX_SPEED = 3
MAX_AGENT = float('inf') 
MAX_HUMAN = 100

HUNGER_THRESHOLD = 60
HUNGER_MAX = 100
EAT_DISTANCE = 25  

COHERENCE_FACTOR = 0.01
ALIGNMENT_FACTOR = 0.1
SEPARATION_FACTOR = 0.05
SEPARATION_DIST = 35

# Wall bounce
ZONE_OF_WALL = 5
WALL_CONST = 4

mapImage = pygame.image.load('Assets/Sprite and Map/Tilemap/resident.png').convert()
MAP_SCALE = 1  
OBJECT_SCALE = MAP_SCALE * 1.355 

tmxData = pytmx.load_pygame('Assets/Objects.tmx')
obstacles = []

for obj in tmxData.objects:
    if obj.name == "Obstacle":  
        scaledRect = pygame.Rect(obj.x * OBJECT_SCALE, obj.y * OBJECT_SCALE, obj.width * OBJECT_SCALE, obj.height * OBJECT_SCALE)
        obstacles.append(scaledRect)  # apply scaling to position and size

class Agent:
    def __init__(self, x, y):
        self.position = pygame.Vector2(x, y)
        self.velocity = pygame.Vector2(
            random.uniform(-MAX_SPEED, MAX_SPEED), random.uniform(-MAX_SPEED, MAX_SPEED))
        self.acceleration = pygame.Vector2(0, 0)
        self.mass = 1
        
        # Hunger
        self.hunger = random.randint(1, HUNGER_MAX)  # ag spawn with random hunger number
        self.hungerIncreaseRate = 0.1
        self.targetHuman = None  

        self.spriteSheets = [
            pygame.image.load('Assets/ghostsspritesheet_1.png').convert_alpha(),
            pygame.image.load('Assets/ghostsspritesheet_2.png').convert_alpha(),
            pygame.image.load('Assets/ghostsspritesheet_3.png').convert_alpha(),
            pygame.image.load('Assets/ghostsspritesheet_4.png').convert_alpha() ]
        
        self.currentSheet = random.choice(self.spriteSheets)
        self.frameIndex = 0
        self.frameCount = 6  # f
        self.spriteWidth = self.currentSheet.get_width() // self.frameCount  
        self.spriteHeight = self.currentSheet.get_height()  
        self.animationSpeed = 0.2  
        self.animationTimer = 0.0

    def update(self):
        self.velocity += self.acceleration
        if self.velocity.length() > MAX_SPEED:
            self.velocity = self.velocity.normalize() * MAX_SPEED
        self.position += self.velocity
        self.acceleration = pygame.Vector2(0, 0)

        wallForce = self.wallBounce(WIDTH, HEIGHT)
        self.applyForce(wallForce[0], wallForce[1])

        self.animationTimer += self.animationSpeed
        if self.animationTimer >= 1.0:  # uppdate every second
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
                self.seek(self.targetHuman.position)  # seek human position
                if self.position.distance_to(self.targetHuman.position) < EAT_DISTANCE:
                    self.transformHuman(humans)  # transform human into agent
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
        agents.append(new_agent) # add new agent to the agents list and remove human one
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
                if dist < 100:  
                    centerOfMass += agent.position
                    agentInRangeCount += 1

        if agentInRangeCount > 0:
            centerOfMass /= agentInRangeCount 
            dir = centerOfMass - self.position
            f = dir * COHERENCE_FACTOR 
            self.applyForce(f.x, f.y)  

    def separation(self, agents):
        dir = pygame.Vector2(0, 0)
        for agent in agents:
            if agent != self:
                dist = self.position.distance_to(agent.position)
                if dist < SEPARATION_DIST:  
                    dir += self.position - agent.position
            
        separationForce = dir * SEPARATION_FACTOR
        self.applyForce(separationForce.x, separationForce.y)

    def alignment(self, agents):
        velo = pygame.Vector2(0, 0)
        agentInRangeCount = 0
        for agent in agents:
            if agent != self:
                dist = self.position.distance_to(agent.position)
                if dist < 100:  
                    velo += agent.velocity
                    agentInRangeCount += 1

        if agentInRangeCount > 0:
            velo /= agentInRangeCount 
            alignmentForce = velo * ALIGNMENT_FACTOR  
            self.applyForce(alignmentForce.x, alignmentForce.y)

    def draw(self, screen):
        spriteHeight = self.currentSheet.get_height() 
        frameRect = pygame.Rect(self.frameIndex * self.spriteWidth, 0, self.spriteWidth, spriteHeight)
        scaleFactor = 2  
        scaledSprite = pygame.transform.scale(self.currentSheet.subsurface(frameRect), 
                                                (int(self.spriteWidth * scaleFactor), int(spriteHeight * scaleFactor)))
        
        #Hunger Ui
        circleColor = "purple" if self.hunger > HUNGER_THRESHOLD else "yellow"
        pygame.draw.circle(screen, circleColor, (int(self.position.x), int(self.position.y)), 20, width=2)

        screen.blit(scaledSprite, (self.position.x - (self.spriteWidth * scaleFactor) // 2, 
                                    self.position.y - (spriteHeight * scaleFactor) // 2))  
        

    def avoidObstacles(self, obstacles):
        for obstacle in obstacles:
            if obstacle.collidepoint(self.position):
                self.velocity = -self.velocity 
                self.position += self.velocity  

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
            pygame.image.load('Assets/eldersspritesheet_1.png').convert_alpha(),
            pygame.image.load('Assets/eldersspritesheet_2.png').convert_alpha(),
            pygame.image.load('Assets/eldersspritesheet_3.png').convert_alpha(),
            pygame.image.load('Assets/eldersspritesheet_4.png').convert_alpha() ]
        
        self.currentSheet = random.choice(self.spriteSheets)

        self.MIN_SPEED = -1   
        self.MAX_SPEED = 5

    def update(self, obstacles):
        
        nearestAgent = self.findNearestAgent(agents)
        if nearestAgent:
            dist = self.position.distance_to(nearestAgent.position)
            if dist < 300:  
                speed = self.MAX_SPEED
            else:  
                speed = self.MIN_SPEED
            
            self.flee(nearestAgent.position) 
            self.velocity += self.acceleration
            if self.velocity.length() > MAX_SPEED:
                self.velocity = self.velocity.normalize() * MAX_SPEED
        
        self.velocity += self.acceleration
        if self.velocity.length() > MAX_SPEED:
            self.velocity = self.velocity.normalize() * MAX_SPEED
        self.position += self.velocity
        self.acceleration = pygame.Vector2(0, 0)

        self.avoidObstacles(obstacles)

        self.animationTimer += self.animationSpeed
        if self.animationTimer >= 1.0:  
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
        scaleFactor = 2  
        scaledSprite = pygame.transform.scale(self.currentSheet.subsurface(frameRect), 
                                                (int(self.spriteWidth * scaleFactor), int(spriteHeight * scaleFactor)))

        screen.blit(scaledSprite, (self.position.x - (self.spriteWidth * scaleFactor) // 2, 
                                    self.position.y - (spriteHeight * scaleFactor) // 2))

def spawnFromRandomPosition_noObstacles(obstacles):
    while True:
        x = random.randint(0, WIDTH)
        y = random.randint(0, HEIGHT)
        newHumanRect = pygame.Rect(x, y, 16, 16) 
        if not any(obstacle.colliderect(newHumanRect) for obstacle in obstacles):
            return (x, y)

def canSpawnAgent(position, obstacles):
    spawnRect = pygame.Rect(position[0], position[1], 16, 16)  
    return not any(obstacle.colliderect(spawnRect) for obstacle in obstacles)

# Initialize Pygame
pygame.init()
clock = pygame.time.Clock()
agents = []
humans = []
for _ in range(MAX_HUMAN):
    x, y = spawnFromRandomPosition_noObstacles(obstacles)
    humans.append(Human(x, y))

# Game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            if canSpawnAgent((x, y), obstacles):  # can't spawn on obstacles collision
                numAgentToSpawn = random.randint(1, 3)  # spawn 1 to 5 agents at the mouse click position
                for _ in range(numAgentToSpawn):
                    if len(agents) < MAX_AGENT:
                        agents.append(Agent(x, y))

    scaledMap = pygame.transform.scale(mapImage, (WIDTH * MAP_SCALE, HEIGHT * MAP_SCALE))
    screen.blit(scaledMap, (0, 0)) # draw the map

    #for obstacle in obstacles:
     #   pygame.draw.rect(screen, (255, 0, 0), obstacle)

    for agent in agents:
        agent.hungry(agents, humans)
        agent.avoidObstacles(obstacles) 
        agent.update()  
        agent.draw(screen)  

    for human in humans:
        human.update(obstacles)  
        human.draw(screen)  

    pygame.display.flip()
    clock.tick(60)

pygame.quit()

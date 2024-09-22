import pygame
import random
import math
#Screen
WIDTH = 1280
HEIGHT = 720

maxSpeed = 5
maxAgents = 95

foodRadius = 50
hungerThreshold = 60
foodDropInterval = 30



coherenceFactor = 0.01
alignmentFactor = 0.1
separationFactor = 0.05
separationDist = 35

#wallBounce
zoneOfWall = 5
wallConst = 2.0

class Agent:
    def __init__(self, x, y) -> None:
        self.position = pygame.Vector2(x, y)
        self.velocity = pygame.Vector2(
            random.uniform(-maxSpeed, maxSpeed), random.uniform(-maxSpeed, maxSpeed))
        self.acceleration = pygame.Vector2(0, 0)
        self.mass = 1
        
        #hunger
        self.hunger = random.randint(0, 60)
        self.hungerIncreaseRate = 0.05
        self.targetFood = None
        # font.Font? hunger text when?

    def update(self):
        self.velocity += self.acceleration
        if self.velocity.length() > maxSpeed:
            self.velocity = self.velocity.normalize() * maxSpeed
        self.position += self.velocity
        self.acceleration = pygame.Vector2(0, 0)
        
        #hungerIncreaseUpdate
        if self.hunger < 100:
            self.hunger += self.hungerIncreaseRate #if hunger is less than 100 then increase until 100
            self.hunger = min(100, self.hunger) #cap hunger at 100
        
        #wallCheck
        wallBounce = self.wallBounce(WIDTH, HEIGHT)
        self.applyForce(wallBounce[0], wallBounce[1])

  

    def applyForce(self, x, y):
        force = pygame.Vector2(x, y)
        self.acceleration += force / self.mass

    
   

    def hungry(self, agents, foods):
        if self.hunger > hungerThreshold and foods:
            self.findNearestFood(foods)
            if self.targetFood:
                self.seek(self.targetFood.position) #seek food position
                if self.position.distance_to(self.targetFood.position) < foodRadius: #if close to food then eat
                    self.eatFood(foods)
                    self.targetFood = None #remove food after eaten
            else: 
                self.coherence(agents)
                self.separation(agents) #}No food/no seek -> Back to other state
                self.alignment(agents)
        else:
            self.coherence(agents)
            self.separation(agents) #}No hungry/ no food/ no seek -> Back to other state
            self.alignment(agents)
    
    def findNearestFood(self, foods):
        nearestfood = None
        nearestDist = float('inf')
        for food in foods:
                dist = self.position.distance_to(food.position)
                if dist < nearestDist:
                    nearestfood = food
                    nearestDist = dist
        self.targetFood = nearestfood
    
    def eatFood(self, foods): #to remove food agent/ to decrease hunger 100 -> 0
        if self.hunger > hungerThreshold:
            self.hunger = max(0, self.hunger - 100)
            foods[:] = [food for food in foods if food.position != self.targetFood.position]

    def seek(self, targetPosition):
        d = targetPosition - self.position 
        d = d.normalize() * 0.1  
        seekingForce = d
        self.applyForce(seekingForce.x, seekingForce.y)

    def coherence(self, agents):
         # Steer towards the average position (center of mass) of neighboring agents
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
            d = centerOfMass - self.position
            f = d * coherenceFactor 
            self.applyForce(f.x, f.y)  # Apply coherence force
    
    def separation(self, agents):
        # Steer to avoid crowding neighbors (separation behavior)
        d = pygame.Vector2(0, 0)
        for agent in agents:
            if agent != self:
                dist = self.position.distance_to(agent.position)
                if dist < separationDist:  # Only consider agents within separation distance
                    d += self.position - agent.position
            
        separationForce = dir * separationFactor
        self.applyForce(separationForce.x, separationForce.y)    

    def alignment(self, agents):
        # Steer towards the average heading (velocity) of nearby agents (alignment behavior)
        v = pygame.Vector2(0, 0)
        agentInRangeCount = 0
        for agent in agents:
            if agent != self:
                dist = self.position.distance_to(agent.position)
                if dist < 100:  # Only consider nearby agents within 100 units
                    v += agent.velocity
                    agentInRangeCount += 1

        if agentInRangeCount > 0:
            v /= agentInRangeCount  # Calculate average velocity
            alignmentForce = v * alignmentFactor  # Apply alignment force
            self.applyForce(alignmentForce.x, alignmentForce.y)

    def draw(self, screen):
        pygame.draw.circle(screen, "white", self.position, 15, width=2)
        color = ("red") if self.hunger > hungerThreshold else ("yellow")
        pygame.draw.circle(screen, color, self.position, 5)

    def wallBounce(self, WIDTH, HEIGHT):
        wallX, wallY = 0, 0
        if self.position.x < zoneOfWall:
            wallX += wallConst
        elif self.position.x > (WIDTH - zoneOfWall):
            wallX -= wallConst
        if self.position.y < zoneOfWall:
            wallY += wallConst
        if self.position.y > (HEIGHT - zoneOfWall):
            wallY -= wallConst
        return wallX, wallY

class Food:
    def __init__(self, x, y):
        self.position = pygame.Vector2(x, y)

    def draw(self, screen):
        pygame.draw.circle(screen, "brown", self.position, 5)



# ----- pygame setup ------
pygame.display.set_caption("Homework")

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)


# Initialize agents and foods
agents = [Agent(random.uniform(0, WIDTH), random.uniform(0, HEIGHT))
          for _ in range(maxAgents)]
foods = []
foodTimer = 0

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            foods.append(Food(x, y))
    
    screen.fill("grey")

    for agent in agents:
        #agent.seek
        #agent.coherence(agents)
        #agent.separation(agents) } they're already called
        #agent.alignment(agents)
        agent.hungry(agents, foods)
        agent.update()
        agent.draw(screen)
    
    for food in foods:
        food.draw(screen)
    
    foodTimer += 1
    if foodTimer >= foodDropInterval:
        foodTimer = 0
    
    fps = int(clock.get_fps())
    fps_text = font.render(f"FPS: {fps}", True, pygame.Color('white'))
    screen.blit(fps_text, (WIDTH - fps_text.get_width() - 10, 10))

    pygame.display.update()
    pygame.display.flip()
    clock.tick(60)

pygame.quit()

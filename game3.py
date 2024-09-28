import pygame
import random
import math
import pytmx
from pytmx.util_pygame import load_pygame

#Screen
WIDTH = 1280
HEIGHT = 720


MAX_SPEED = 5
MAX_AGENTS = 95

FOOD_RADIUS = 50
HUNGER_THRESHOLD = 60
FOOD_DROP_INTERVAL = 30



COHERENCE_FACTOR = 0.01
ALIGNMENT_FACTOR = 0.1
SEPARATION_FACTOR = 0.05
SEPARATION_DIST = 35

#wallBounce
ZONE_OF_WALL = 5
WALL_CONST = 2.0

class Agent:
    def __init__(self, x, y) -> None:
        self.position = pygame.Vector2(x, y)
        self.velocity = pygame.Vector2(
            random.uniform(-MAX_SPEED, MAX_SPEED), random.uniform(-MAX_SPEED, MAX_SPEED))
        self.acceleration = pygame.Vector2(0, 0)
        self.mass = 1
        
        #hunger
        self.hunger = random.randint(0, 60)
        self.hungerIncreaseRate = 0.05
        self.targetFood = None
        # font.Font? hunger text when?

    def update(self):
        self.velocity += self.acceleration
        if self.velocity.length() > MAX_SPEED:
            self.velocity = self.velocity.normalize() * MAX_SPEED
        self.position += self.velocity
        self.acceleration = pygame.Vector2(0, 0)
        
        #hungerIncreaseUpdate
        if self.hunger < 100:
            self.hunger += self.hungerIncreaseRate #if hunger is less than 100 then increase until 100
            self.hunger = min(100, self.hunger) #cap hunger at 100
        
        #wallCheck
        wallBounce = self.wallBounce(WIDTH, HEIGHT)
        self.APPLY_FORCE(wallBounce[0], wallBounce[1])

    def APPLY_FORCE(self, x, y):
        force = pygame.Vector2(x, y)
        self.acceleration += force / self.mass

    def hungry(self, agents, foods):
        if self.hunger > HUNGER_THRESHOLD and foods:
            self.findNearestFood(foods)
            if self.targetFood:
                self.seek(self.targetFood.position) #seek food position
                if self.position.distance_to(self.targetFood.position) < FOOD_RADIUS: #if close to food then eat
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
        if self.hunger > HUNGER_THRESHOLD:
            self.hunger = max(0, self.hunger - 100)
            foods[:] = [food for food in foods if food.position != self.targetFood.position]

    def seek(self, targetPosition):
        dir = targetPosition - self.position 
        dir = dir.normalize() * 0.1  
        seekingForce = dir
        self.APPLY_FORCE(seekingForce.x, seekingForce.y)

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
            f = d * COHERENCE_FACTOR 
            self.APPLY_FORCE(f.x, f.y)  # Apply coherence force
    
    def separation(self, agents):
        # Steer to avoid crowding neighbors (separation behavior)
        d = pygame.Vector2(0, 0)
        for agent in agents:
            if agent != self:
                dist = self.position.distance_to(agent.position)
                if dist < SEPARATION_DIST:  # Only consider agents within separation distance
                    d += self.position - agent.position
            
        separationForce = d * SEPARATION_FACTOR
        self.APPLY_FORCE(separationForce.x, separationForce.y)    

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
            alignmentForce = v * ALIGNMENT_FACTOR  # Apply alignment force
            self.APPLY_FORCE(alignmentForce.x, alignmentForce.y)

    def draw(self, screen):
        pygame.draw.circle(screen, "white", self.position, 15, width=2)
        color = ("red") if self.hunger > HUNGER_THRESHOLD else ("yellow")
        pygame.draw.circle(screen, color, self.position, 5)

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
        

class Food:
    def __init__(self, x, y):
        self.position = pygame.Vector2(x, y)

    def draw(self, screen):
        pygame.draw.circle(screen, "brown", self.position, 5)

class Camera:
    def __init__(self, width, height):
        self.camera = pygame.Vector2(10, -18)
        self.width = width
        self.height = height
        self.zoom = 1.7  # Default zoom level

    def apply(self, entity):
        # Offset entities by camera position and zoom
        return (entity.position.x - self.camera.x) * self.zoom, (entity.position.y - self.camera.y) * self.zoom

    def update(self, target):
        # Center the camera on the target
        self.camera.x = target.position.x - self.width // (2 * self.zoom)
        self.camera.y = target.position.y - self.height // (2 * self.zoom)

        # Keep the camera within the map bounds
        self.camera.x = max(0, min(self.camera.x, tmxdata.width * tmxdata.tilewidth * self.zoom - self.width))
        self.camera.y = max(0, min(self.camera.y, tmxdata.height * tmxdata.tileheight * self.zoom - self.height))

        # Adjust zoom level as needed
        self.zoom = 1  # Set to your desired zoom level (e.g., 1.2 for zooming in)

    

def drawMap(screen, tmxdata, camera):
    for layer in tmxdata.visible_layers:
        if isinstance(layer, pytmx.TiledTileLayer):
            for x, y, gid in layer:
                if gid != 0:
                    tile = tmxdata.get_tile_image_by_gid(gid)
                    if tile:
                        # Scale tile position and size by zoom level
                        scaled_x = (x * tmxdata.tilewidth - camera.camera.x) * camera.zoom
                        scaled_y = (y * tmxdata.tileheight - camera.camera.y) * camera.zoom
                        scaled_tile = pygame.transform.scale(tile, (int(tmxdata.tilewidth * camera.zoom), int(tmxdata.tileheight * camera.zoom)))
                        screen.blit(scaled_tile, (scaled_x, scaled_y))



# ----- pygame setup ------
pygame.display.set_caption("Homework")

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)

#MAP
tmxdata = load_pygame("C:/Users/Student/Documents/pondProject/lab1/Assets/Sprite and Map/Tilemap/sample_fantasy.tmx")
print(tmxdata)

# Initialize agents and foods
agents = [Agent(random.uniform(0, WIDTH), random.uniform(0, HEIGHT))
          for _ in range(MAX_AGENTS)]
foods = []
foodTimer = 0


camera = Camera(WIDTH, HEIGHT)


running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            foods.append(Food(x, y))
    
    screen.fill((60,172,215))
    

    drawMap(screen, tmxdata, camera)

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
    if foodTimer >= FOOD_DROP_INTERVAL:
        foodTimer = 0
    
    fps = int(clock.get_fps())
    fps_text = font.render(f"FPS: {fps}", True, pygame.Color('white'))
    screen.blit(fps_text, (WIDTH - fps_text.get_width() - 10, 10))

    pygame.display.update()
    pygame.display.flip()
    clock.tick(60)

pygame.quit()

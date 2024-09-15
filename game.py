# Example file showing a basic pygame "game loop"
import pygame
import random
import math

WIDTH=1280
HEIGHT=720
MAX_SPEED = 5

COHERENCE_FACTOR = 0.1
ALIGNMENT_FACTOR = 0.1
SEPARATION_FACTOR = 0.05
SEPARATION_DIST = 30

class Agent:
    def __init__(self, x, y) -> None:
       self.position = pygame.Vector2(x,y)
       self.velocity = pygame.Vector2(0,0)
       self.acceleration = pygame.Vector2(0,0)
       self.mass = 1

    def update(self):
        self.velocity = self.velocity + self.acceleration
        if self.velocity.length() > MAX_SPEED:
            self.velocity = self.velocity.normalize() * MAX_SPEED
        self.position = self.position + self.velocity
        self.acceleration = pygame.Vector2(0,0)

    def apply_force(self, x,y):
        force = pygame.Vector2(x,y)
        self.acceleration = self.acceleration + (force/self.mass)

    def seek(self, x,y):
        dir = player - self.position #seeking direction
        dir = dir.normalize() * 0.2
        seeking_force = dir
        self.apply_force(seeking_force.x, seeking_force.y)

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
        dir = pygame.Vector2(0,0)
        for agent in agents:
            dist = math.sqrt((self.position.x - agent.position.x)**2 
                        + (self.position.y - agent.position.y)**2)
            if dist < SEPARATION_DIST:
                dir += self.position - agent.position
            
        separation_force = dir * SEPARATION_FACTOR
        self.apply_force(separation_force.x, separation_force.y)    

    def alignment(self, agents):
        v = pygame.Vector2(0,0)
        for agent in agents:
            if agent != self:
                v += agent.velocity

        v /= len(agents) - 1
        alignment_force = v * ALIGNMENT_FACTOR
        self.apply_force(alignment_force.x, alignment_force.y)

    def draw(self):
        pygame.draw.circle(screen,"white",  self.position, 20, width=2) #for silly white outline to make the agent cooller idk
        pygame.draw.circle(screen,"red", self.position, 10)
        #pygame.draw.circle(screen,"grey",  self.position, 150, width=2) #invisible circle for detection range

agents = []
for i in range(100):
    agents.append(Agent(random.uniform(0, WIDTH), random.uniform(0, HEIGHT)))

# ----- pygame setup ------
pygame.init()
screen = pygame.display.set_mode((1280, 720))
pygame.display.set_caption("Homework")
clock = pygame.time.Clock()


#----- player editors -----
player = pygame.Vector2()
x = 50
y = 50
#width = 40
#height = 60
radius = 10
velocity = 5

running = True

while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
   
    #WASD for movement controls
    keys = pygame.key.get_pressed()

    if keys[pygame.K_a]:
        player.x -= velocity
    
    if keys[pygame.K_d]:
        player.x += velocity
    
    if keys[pygame.K_w]:
        player.y -= velocity
   
    if keys[pygame.K_s]:
        player.y += velocity
    
    

    # fill the screen with a color to wipe away anything from last frame
    screen.fill("grey")

    # RENDER YOUR GAME HERE
    ###pygame.draw.circle(screen, "black", [640,360], 15)
    pygame.draw.circle(screen,("black"), (player.x, player.y), radius) 
    
    for agent in agents:
            agent.seek(400,400) # "#" this to make below function work!
            agent.coherence(agents)
            agent.separation(agents)
            agent.alignment(agents)
            agent.update()
            agent.draw()
    
    for agent in agents:
        if agent.position.x > WIDTH + 1:
                agent.position.x =1
        elif agent.position.x < 0:
            agent.position.x = WIDTH
        if agent.position.y > HEIGHT + 1:
                agent.position.y =1
        elif agent.position.y < 0:
            agent.position.y = HEIGHT
 
 
    pygame.display.update()

    # flip() the display to put your work on screen
    pygame.display.flip()

    clock.tick(60)  # limits FPS to 60

pygame.quit()
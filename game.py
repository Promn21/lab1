# Example file showing a basic pygame "game loop"
import pygame
import random
WIDTH=1280
HEIGHT=720

class Agent:
    def __init__(self, x, y) -> None:
       self.position = pygame.Vector2(x,y)
       self.velocity = pygame.Vector2(0,0)
       self.acceleration = pygame.Vector2(0,0)
       self.mass = 1

    def update(self):
        self.velocity = self.velocity + self.acceleration
        self.position = self.position + self.velocity
        self.acceleration = pygame.Vector2(0,0)

    def apply_force(self, x,y):
        force = pygame.Vector2(x,y)
        self.acceleration = self.acceleration + (force/self.mass)

    def draw(self):
        pygame.draw.circle(screen,"red", self.position, 10)

agents = []
for i in range(100):
    agents.append(Agent(random.uniform(0, WIDTH), random.uniform(0, HEIGHT)))

# ----- pygame setup ------
pygame.init()
screen = pygame.display.set_mode((1280, 720))
pygame.display.set_caption("Homework")
clock = pygame.time.Clock()


#----- player editors -----
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
        x -= velocity
    
    if keys[pygame.K_d]:
        x += velocity
    
    if keys[pygame.K_w]:
        y -= velocity
   
    if keys[pygame.K_s]:
        y += velocity
    
    

    # fill the screen with a color to wipe away anything from last frame
    screen.fill("grey")

    # RENDER YOUR GAME HERE
    ###pygame.draw.circle(screen, "black", [640,360], 15)
    pygame.draw.circle(screen,("black"), (x, y), radius) 
    
    for agent in agents:
            agent.update()
            agent.draw()

 
    pygame.display.update()

    # flip() the display to put your work on screen
    pygame.display.flip()

    clock.tick(60)  # limits FPS to 60

pygame.quit()
import pygame
import random
import enum
import math

WIDTH, HEIGHT = 800, 600
NUM_AGENTS = 5
FOOD_SIZE = 5
MAX_PATROL_SPEED = 1.5
CHASE_SPEED = 3
HUNGER_DECAY_RATE = 5  
CHASE_DISTANCE = 150  
ATTACK_DURATION = 0.5  # Duration of the attack animation in seconds

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Raptor State Machine")

# Load and slice sprite sheets
def load_sprite_sheet(path, frame_count, frame_width, frame_height=64):
    sheet = pygame.image.load(path).convert_alpha()
    return [sheet.subsurface(pygame.Rect(i * frame_width, 0, frame_width, frame_height)) for i in range(frame_count)]

raptor_walk_anim = load_sprite_sheet('assets/raptor-walk.png', 6, 128)
raptor_run_anim = load_sprite_sheet('assets/raptor-run.png', 6, 128)
raptor_idle_anim = load_sprite_sheet('assets/raptor-scanning.png', 18, 128)
raptor_atk_anim = load_sprite_sheet('assets/raptor-bite.png', 10, 128)
raptor_dead_anim = load_sprite_sheet('assets/raptor-dead.png', 6, 128)

FRAME_RATE = 30
FONT = pygame.font.Font(None, 24)  # Font for displaying hunger level

class AgentState(enum.Enum):
    PATROL_STATE = 0
    CHASE_STATE = 1
    ATK_STATE = 2
    IDLE_STATE = 3
    DEAD_STATE = 4

class Agent:
    def __init__(self):
        self.hungriness = 100
        self.position = pygame.Vector2(random.uniform(0, WIDTH), random.uniform(0, HEIGHT))
        self.velocity = pygame.Vector2(0, 0)
        self.frame_index = 0
        self.current_state = AgentState.PATROL_STATE
        self.current_anim = raptor_walk_anim
        self.time_since_last_frame = 0
        self.anim_completed = False  

        # Patrol attributes
        self.patrol_timer = 0  
        self.patrol_duration = random.uniform(1.0, 2.0)  
        self.set_random_patrol_direction()

    def set_random_patrol_direction(self):
        angle = random.uniform(0, 360)
        radians = math.radians(angle)
        self.velocity = pygame.Vector2(MAX_PATROL_SPEED * math.cos(radians), MAX_PATROL_SPEED * math.sin(radians))

    def update_animation(self, dt):
        if not self.anim_completed:
            self.frame_index += FRAME_RATE * dt
            if self.frame_index >= len(self.current_anim):
                self.frame_index = 0
                if self.current_state == AgentState.IDLE_STATE:
                    self.anim_completed = True  

    def change_state(self, new_state, new_anim):
        if self.current_state != new_state:
            self.current_state = new_state
            self.current_anim = new_anim
            self.frame_index = 0
            self.anim_completed = False

            # Reset patrol timer when switching from PATROL_STATE
            if new_state == AgentState.PATROL_STATE:
                self.patrol_timer = 0
                self.set_random_patrol_direction()  # Set new patrol direction
            elif new_state == AgentState.ATK_STATE:
                self.attack_timer = 0  # Reset attack timer when entering attack state

    def update(self, food_list, dt):
        if self.hungriness <= 0:
            self.change_state(AgentState.DEAD_STATE, raptor_dead_anim)

        if self.current_state != AgentState.DEAD_STATE:
            self.hungriness -= HUNGER_DECAY_RATE * dt

        # Initialize nearest_food variable
        nearest_food = None

        if self.current_state == AgentState.PATROL_STATE:
            self.patrol_timer += dt
            if self.patrol_timer >= self.patrol_duration:
                self.change_state(AgentState.IDLE_STATE, raptor_idle_anim)
            else:
                self.position += self.velocity
            
            # Change to CHASE_STATE if food is present
            nearest_food = min(food_list, key=lambda f: (f.position - self.position).length(), default=None)
            if nearest_food and (nearest_food.position - self.position).length() < CHASE_DISTANCE:
                self.change_state(AgentState.CHASE_STATE, raptor_run_anim)

        elif self.current_state == AgentState.IDLE_STATE:
            if self.anim_completed:
                self.change_state(AgentState.PATROL_STATE, raptor_walk_anim)
                self.set_random_patrol_direction()

            # Check for nearby food to transition to CHASE_STATE
            nearest_food = min(food_list, key=lambda f: (f.position - self.position).length(), default=None)
            if nearest_food and (nearest_food.position - self.position).length() < CHASE_DISTANCE:
                self.change_state(AgentState.CHASE_STATE, raptor_run_anim)

        elif self.current_state == AgentState.CHASE_STATE:
            nearest_food = min(food_list, key=lambda f: (f.position - self.position).length(), default=None)
            if nearest_food:
                distance_to_food = (nearest_food.position - self.position).length()
                if distance_to_food > CHASE_DISTANCE:
                    self.change_state(AgentState.IDLE_STATE, raptor_idle_anim)
                    return

                self.velocity = (nearest_food.position - self.position).normalize() * CHASE_SPEED
                self.position += self.velocity

                if distance_to_food < FOOD_SIZE + 10:  # Agent reached the food
                    self.change_state(AgentState.ATK_STATE, raptor_atk_anim)  # Transition to attack state

        elif self.current_state == AgentState.ATK_STATE:
            self.attack_timer += dt  # Update attack timer
            if self.attack_timer >= ATTACK_DURATION:  # Check if the attack animation has completed
                if nearest_food:  # Check if nearest_food is not None
                    food_list[:] = [food for food in food_list if food.position != nearest_food.position]

        elif self.current_state == AgentState.DEAD_STATE:
            if self.frame_index < len(self.current_anim) - 1:
                self.update_animation(dt)
            else:
                self.frame_index = len(raptor_dead_anim) - 1  

        self.update_animation(dt)
        self.wrap_around_screen()

    def wrap_around_screen(self):
        if self.position.x > WIDTH:
            self.position.x = 0
        elif self.position.x < 0:
            self.position.x = WIDTH
        if self.position.y > HEIGHT:
            self.position.y = 0
        elif self.position.y < 0:
            self.position.y = HEIGHT

    def render_hunger(self, screen):
        # Render the hunger level as text above the agent
        hunger_text = FONT.render(f"Hunger: {int(self.hungriness)}", True, (255, 255, 255))
        text_rect = hunger_text.get_rect(center=(self.position.x, self.position.y - 40))
        screen.blit(hunger_text, text_rect)

    def draw(self, screen):
        current_frame = self.current_anim[int(self.frame_index) % len(self.current_anim)]
        sprite_rect = current_frame.get_rect(center=(self.position.x, self.position.y))
        
        if self.velocity.x < 0:
            current_frame = pygame.transform.flip(current_frame, True, False)
        
        screen.blit(current_frame, sprite_rect)
        self.render_hunger(screen)  # Draw hunger level above the agent

# Food class
class Food:
    def __init__(self, x, y):
        self.position = pygame.Vector2(x, y)

    def draw(self, screen):
        # Draw the food as a circle
        pygame.draw.circle(screen, (0, 255, 0), (int(self.position.x), int(self.position.y)), FOOD_SIZE)

# Main function
def main():
    agents = [Agent() for _ in range(NUM_AGENTS)]
    food_list = []  # List to hold multiple food items
    clock = pygame.time.Clock()

    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        screen.fill((100, 100, 100))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:  # Check for mouse click
                if event.button == 1:  # Left mouse button
                    x, y = event.pos
                    food_list.append(Food(x, y))  # Add food at mouse position

        # Update and draw agents
        for agent in agents:
            agent.update(food_list, dt)
            agent.draw(screen)

        # Draw all food items that are still in the food_list
        for food in food_list:
            food.draw(screen)

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()

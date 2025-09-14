import pygame
import random
import sys
import os
# Initialize pygame
pygame.init()
WORKING_DIR = r'C:\Users\ShaneP\Documents\Coding\Python\RO_HMI\hunt_for_red_oktober'
os.chdir(WORKING_DIR)
# Screen setup
WIDTH, HEIGHT = 1280, 1024
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Depth Charge Attack")

# Load images
ship_img = pygame.image.load("Ship.png")
ship_img = pygame.transform.scale(ship_img, (100, 30))

barrel_img = pygame.image.load("barrel.png")
barrel_img = pygame.transform.scale(barrel_img, (15,20))

sub_img = pygame.image.load("sub.png")
sub_img = pygame.transform.scale(sub_img, (100, 30))

sub_explosion = pygame.image.load("Explosion.png")

background_img = pygame.image.load("ocean.png")
background_img = pygame.transform.scale(background_img, (WIDTH, HEIGHT))


# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED   = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 100, 200)

# Fonts
font = pygame.font.SysFont("Arial", 24)

# Player setup
ship_x = WIDTH // 2 - 100
ship_y = 450
ship_speed = 6

# Depth charge setup
charges = []  # [(x, y, target_depth, dropped_depth)]
charge_speed = 4

# Submarine setup
sub_x = WIDTH // 2 - 100
sub_y = HEIGHT - 100
sub_speed = 1
sub_health = 100

# Depth input
depth_input = ""
input_active = True

# Clock
clock = pygame.time.Clock()

def draw_background():
    screen.blit(background_img, (0, 0))

def draw_ship(x, y):
    screen.blit(ship_img, (x, y))


def draw_sub(x, y):
    screen.blit(sub_img, (x, y))
    # Health bar
    pygame.draw.rect(screen, RED, (x, y - 15, 100, 10))
    pygame.draw.rect(screen, GREEN, (x, y - 15, sub_health, 10))


def draw_charges():
    for charge in charges:
        screen.blit(barrel_img, (charge[0], charge[1]))
        #draw_explosion()
def draw_explosion():
    screen.blit(sub_explosion, (charge[0], charge[1]))

def draw_text():
    input_text = font.render(f"Depth Input: {depth_input}", True, WHITE)
    health_text = font.render(f"Sub Health: {sub_health}", True, WHITE)
    screen.blit(input_text, (10, 10))
    screen.blit(health_text, (10, 40))

sub_target_x = random.randint(0, WIDTH - 200)
sub_target_y = random.randint(HEIGHT // 2, HEIGHT - 60)

def move_sub():
    global sub_x, sub_y, sub_target_x, sub_target_y
    if sub_health > 0:
        # If sub is close enough to its target, pick a new one
        if abs(sub_x - sub_target_x) < 5 and abs(sub_y - sub_target_y) < 5:
            sub_target_x = random.randint(0, WIDTH - 200)
            sub_target_y = random.randint(HEIGHT // 2, HEIGHT - 60)

        # Move toward target coordinates
        if sub_x < sub_target_x:
            sub_x += sub_speed
        elif sub_x > sub_target_x:
            sub_x -= sub_speed

        if sub_y < sub_target_y:
            sub_y += sub_speed
        elif sub_y > sub_target_y:
            sub_y -= sub_speed
    else:
        pass



def check_hits():
    global sub_health
    for charge in charges[:]:
        cx, cy, target_depth, dropped_depth = charge
        if cy >= target_depth:
            distance = abs((cy) - (sub_y + 30))
            if abs(cx - sub_x) < 100:  # within horizontal range
                damage = max(0, 50 - distance // 5)
                sub_health -= damage
            charges.remove(charge)
            if sub_health <= 0:
                draw_explosion()



# Game loop
running = True
while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Keyboard input
        if event.type == pygame.KEYDOWN:
            if input_active:
                if event.key == pygame.K_RETURN:
                    input_active = False
                elif event.key == pygame.K_BACKSPACE:
                    depth_input = depth_input[:-1]
                elif event.unicode.isdigit():
                    depth_input += event.unicode
            else:
                if event.key == pygame.K_SPACE and depth_input:
                    try:
                        depth_value = int(depth_input)
                        charges.append([ship_x + 85, ship_y + 40, depth_value, 0])
                        print(charges, depth_value)
                    except ValueError:
                        pass
                    depth_input = ""
                    input_active = True
    screen.blit(background_img, (0, 0))
    # Movement
    keys = pygame.key.get_pressed()
    if keys[pygame.K_a] and ship_x > 0:
        ship_x -= ship_speed
    if keys[pygame.K_d] and ship_x < WIDTH - 200:
        ship_x += ship_speed

    # Update charges
    for charge in charges:
        charge[1] += charge_speed
        charge[3] = charge[1]
    check_hits()

    # Move submarine
    move_sub()

    # Draw everything
    draw_ship(ship_x, ship_y)
    draw_sub(sub_x, sub_y)
    draw_charges()

    draw_text()

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()

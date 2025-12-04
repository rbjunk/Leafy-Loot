import pygame
import sys
import time
import os
from shop import Shop
from production import Plant, Upgrade

# Initialize Pygame
pygame.init()

#  Setup window
WIDTH, HEIGHT = 900, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
#get the center position of the window
screen_center = screen.get_rect().center
pygame.display.set_caption("Leafy Loot")
clock = pygame.time.Clock()

# Make sure you have an image at: assets/icon.png
if os.path.exists("assets/icon.png"):
    icon = pygame.image.load("assets/icon.png").convert_alpha()
    pygame.display.set_icon(icon)
elif os.path.exists("assets/missing.png"):
    icon = pygame.image.load("assets/missing.png")
    pygame.display.set_icon(icon)
else:
    print("⚠️  Missing 'assets/icon.png' — using fallback icon.")



#  Colors & Fonts
BG_COLOR = (44, 44, 44)
TEXT_COLOR = (144, 238, 144)

# Pixel-styled font (Courier-like)
font = pygame.font.Font(pygame.font.match_font('couriernew', bold=True), 24)


#  Game State
debug_state = True
leafs = 0 #current number of leafs the player has
last_update = time.time()
running = True #variable to hold whether the game is currently running
shop = Shop(800, 500) #create a shop window
current_season = 1 #1 for spring, 2 for summer, 3 for fall
clock = pygame.time.Clock()

#Initialize game data
#Create Plants (Name, base production, base cost)
all_plants = [
    Plant(name="Sunflower", base_production=5, base_cost=50),
    Plant(name="Daisy", base_production=10, base_cost=100),
    Plant(name="Magic Vine", base_production=25, base_cost=250)
]
#Create Upgrades(Name, Cost, Multiplier, Description)
all_upgrades = [
    Upgrade(name="Better Soil", cost=50, multiplier_bonus=0.1, description ="+10% Production to all plants")
]

def debugInit(screen):
    plant_info = font.render(f"Sunflower owned:{all_plants[0].quantity} Daisy owned:{all_plants[1].quantity} Magic Vine owned:{all_plants[2].quantity}", True, TEXT_COLOR)
    screen.blit(plant_info, (20,70))

def calculateLps():
    #Calculates Currency Per Second based on plants owned and upgrades owned
    raw_production = sum(p.getProduction() for p in all_plants)

    #Calculate global multiplier from purchased upgrades
    global_multiplier = 1.0 + sum(u.multiplier_bonus for u in all_upgrades if u.purchased)

    return raw_production * global_multiplier

#  Main Game Loop
while running:
    # Handle events (quit, input, etc.)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_b:
                shop.toggle()
                print("Shop window is open: " + str(shop.is_open))

    # increase leafs every second
    current_time = time.time()
    dt = current_time - last_update
    if dt >= 1:
        #Calculate Leafs per second (LPS) and add it
        lps = calculateLps() + 1
        leafs += int(lps)
        last_update = current_time

    # background
    screen.fill(BG_COLOR)
    # Render leaf counter
    lps_val = calculateLps() + 1
    leaf_text = font.render(f"leafs: {leafs}", True, TEXT_COLOR)
    lps_text = font.render(f"Per Second: {lps_val:.1f}", True, (200, 200, 200))
    screen.blit(leaf_text, (20, 20))
    screen.blit(lps_text, (20,50))
    
    if (debug_state):
        debugInit(screen)




    #draw the shop last so it overlays on top of the main screen
    if shop.is_open:
        shop.draw(screen, screen_center)
    # Update the display
    pygame.display.flip()

    # Cap FPS
    clock.tick(60)

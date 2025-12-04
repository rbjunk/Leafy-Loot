import pygame
import sys
import time
import os
from shop import Shop


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
leafs = 0 #current number of leafs the player has
last_update = time.time()
running = True #variable to hold whether the game is currently running
shop = Shop(800, 500) #create a shop window
clock = pygame.time.Clock()

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
    if current_time - last_update >= 1:
        leafs+= 1
        last_update = current_time

    # background
    screen.fill(BG_COLOR)

    # Render leaf counter
    leaf_text = font.render(f"leafs: {leafs}", True, TEXT_COLOR)
    screen.blit(leaf_text, (10, 10))

    #draw the shop last so it overlays on top of the main screen
    if shop.is_open:
        shop.draw(screen, screen_center)
    # Update the display
    pygame.display.flip()

    # Cap FPS
    clock.tick(60)

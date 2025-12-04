import pygame
import sys
import time
import os


# Initialize Pygame
pygame.init()

#  Setup window
WIDTH, HEIGHT = 400, 300
screen = pygame.display.set_mode((WIDTH, HEIGHT))
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
seeds = 0
last_update = time.time()
clock = pygame.time.Clock()

#  Main Game Loop
while True:
    # Handle events (quit, input, etc.)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # increase seeds every second
    current_time = time.time()
    if current_time - last_update >= 1:
        seeds += 1
        last_update = current_time

    # background
    screen.fill(BG_COLOR)

    # Render seed counter
    seed_text = font.render(f"Seeds: {seeds}", True, TEXT_COLOR)
    screen.blit(seed_text, (10, 10))

    # Update the display
    pygame.display.flip()

    # Cap FPS
    clock.tick(60)

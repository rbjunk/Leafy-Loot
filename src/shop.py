import pygame

class Shop:
    def __init__(self, width, height):
        self.is_open = False
        
        # Create a semi-transparent overlay
        self.surface = pygame.Surface((width, height))
        self.surface.set_alpha(180)
        self.surface.fill((0, 0, 0))

        # example shop items
        self.font = pygame.font.Font(None, 40)

    def toggle(self):
        self.is_open = not self.is_open

    def handle_event(self, event):
        """Only called when shop is open."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE or event.key == pygame.K_b:
                self.toggle()

        # You can add button clicking, item buying, etc here.

    def draw(self, screen, screen_center_position):
        """Draw the shop overlay."""
        #center the shop window
        rect = self.surface.get_rect(center = screen_center_position)
        screen.blit(self.surface, rect)

        text = self.font.render("SHOP MENU", True, (255, 255, 255))
        #get text rectangle and center it horizontally in the shop with a small y offset
        text_rect = text.get_rect(center=(rect.centerx, rect.y + 40))
        #draw centered text
        screen.blit(text, text_rect)

        # Add more UI drawing here
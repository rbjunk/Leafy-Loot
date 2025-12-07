import pygame
from settings import BUTTON_COLOR, BUTTON_HOVER_COLOR, BUTTON_TEXT_COLOR, SLIDER_BG_COLOR, SLIDER_COLOR, SLIDER_HANDLE_COLOR


class Button:
    def __init__(self, x, y, width, height, text, action_id, font_size=32, is_back_button=False):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.action_id = action_id
        self.is_back = is_back_button

        self.hovered = False
        self.was_hovered = False  # For sound trigger
        self.font = pygame.font.Font(None, font_size)

    def draw(self, surface):
        color = BUTTON_HOVER_COLOR if self.hovered else BUTTON_COLOR
        border_radius = 10 if self.rect.height > 40 else 6

        pygame.draw.rect(surface, color, self.rect, border_radius=border_radius)
        pygame.draw.rect(surface, (200, 200, 200), self.rect, 2, border_radius=border_radius)

        text_surf = self.font.render(self.text, True, BUTTON_TEXT_COLOR)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def update(self, mouse_pos, sound_mgr):
        # Returns True if sound should be played
        self.was_hovered = self.hovered
        self.hovered = self.rect.collidepoint(mouse_pos)

        # Play hover sound only on the frame we enter the rect
        if self.hovered and not self.was_hovered:
            sound_mgr.play("hover")

    def handle_click(self, sound_mgr):
        if self.hovered:
            sound_type = "back" if self.is_back else "select"
            sound_mgr.play(sound_type)
            return self.action_id
        return None


class Slider:
    def __init__(self, x, y, width, value=0.5):
        self.rect = pygame.Rect(x, y, width, 20)
        self.value = value
        self.dragging = False

    def draw(self, surface):
        # Draw Background
        pygame.draw.rect(surface, SLIDER_BG_COLOR, self.rect, border_radius=10)
        pygame.draw.rect(surface, (80, 80, 90), self.rect, 2, border_radius=10)

        # Draw Fill
        fill_width = int(self.value * self.rect.width)
        fill_rect = pygame.Rect(self.rect.x, self.rect.y, fill_width, self.rect.height)
        pygame.draw.rect(surface, SLIDER_COLOR, fill_rect, border_radius=10)

        # Draw Handle
        handle_x = self.rect.x + fill_width
        pygame.draw.circle(surface, SLIDER_HANDLE_COLOR, (handle_x, self.rect.centery), 12)
        pygame.draw.circle(surface, (255, 255, 255), (handle_x, self.rect.centery), 12, 2)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos) or \
                    (event.pos[0] >= self.rect.left and event.pos[0] <= self.rect.right and abs(
                        event.pos[1] - self.rect.centery) < 15):
                self.dragging = True
                self.update_val(event.pos[0])
                return True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            self.update_val(event.pos[0])
            return True
        return False

    def update_val(self, x):
        x = max(self.rect.left, min(self.rect.right, x))
        self.value = (x - self.rect.left) / self.rect.width
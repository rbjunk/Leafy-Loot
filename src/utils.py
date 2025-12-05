import pygame
import os
import json
import time


# Get the current script's directory
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
ASSETS_DIR = os.path.join(PROJECT_ROOT, "assets")

# Setup window
WIDTH, HEIGHT = 900, 600

# Colors
BG_COLOR = (30, 40, 30)
TEXT_COLOR = (144, 238, 144)
MENU_BG_COLOR = (30, 30, 40)
BUTTON_COLOR = (70, 130, 70)
BUTTON_HOVER_COLOR = (100, 180, 100)
BUTTON_TEXT_COLOR = (255, 255, 255)
SLIDER_COLOR = (100, 100, 120)
SLIDER_HANDLE_COLOR = (144, 238, 144)
SLIDER_BG_COLOR = (50, 50, 60)
PAUSE_OVERLAY_COLOR = (0, 0, 0, 180)
GAME_UI_BG = (40, 50, 40, 200)
PLANTING_AREA_COLOR = (50, 80, 50)
PLANTING_GRID_COLOR = (70, 100, 70)


# Fonts
def get_font(size=24, bold=True):
    return pygame.font.Font(pygame.font.match_font('couriernew', bold=bold), size)


# Sound Effects Manager
class SoundManager:
    def __init__(self):
        self.sounds = {}
        self.muted = False

    def load_sound(self, name, filename):
        path = os.path.join(ASSETS_DIR, filename)
        if os.path.exists(path):
            try:
                self.sounds[name] = pygame.mixer.Sound(path)
                print(f"Loaded sound: {name} from {filename}")
            except Exception as e:
                print(f"Could not load sound {filename}: {e}")
        else:
            print(f"Sound file not found: {path}")
            # Create a silent placeholder
            self.sounds[name] = pygame.mixer.Sound(buffer=bytes([0] * 1000))

    def play(self, name, volume=1.0):
        if not self.muted and name in self.sounds:
            sound = self.sounds[name]
            sound.set_volume(volume)
            sound.play()

    def set_muted(self, muted):
        self.muted = muted


# Music Manager
class MusicManager:
    def __init__(self):
        self.current_music = None
        self.menu_music = None
        self.game_music = None
        self.volume = 0.5

    def load_music(self, name, filename):
        path = os.path.join(ASSETS_DIR, filename)
        if os.path.exists(path):
            return path
        else:
            print(f"Music file not found: {path}")
            return None

    def play_music(self, music_type, fade_ms=500):
        if music_type == "menu" and self.menu_music:
            if self.current_music != "menu":
                pygame.mixer.music.load(self.menu_music)
                pygame.mixer.music.set_volume(self.volume)
                pygame.mixer.music.play(-1, fade_ms=fade_ms)
                self.current_music = "menu"
        elif music_type == "game" and self.game_music:
            if self.current_music != "game":
                pygame.mixer.music.load(self.game_music)
                pygame.mixer.music.set_volume(self.volume)
                pygame.mixer.music.play(-1, fade_ms=fade_ms)
                self.current_music = "game"

    def stop_music(self, fade_ms=500):
        pygame.mixer.music.fadeout(fade_ms)
        self.current_music = None

    def set_volume(self, volume):
        self.volume = volume
        if pygame.mixer.get_init():  # Check if mixer is initialized
            pygame.mixer.music.set_volume(volume)


# Settings class to manage volume
class Settings:
    def __init__(self):
        self.music_volume = 0.5
        self.sfx_volume = 0.7
        self.settings_path = os.path.join(PROJECT_ROOT, "settings.json")
        self.load_settings()

    def load_settings(self):
        try:
            if os.path.exists(self.settings_path):
                with open(self.settings_path, "r") as f:
                    data = json.load(f)
                    self.music_volume = data.get("music_volume", 0.5)
                    self.sfx_volume = data.get("sfx_volume", 0.7)
        except Exception as e:
            print(f"Could not load settings: {e}")
            self.save_settings()

    def save_settings(self):
        try:
            data = {
                "music_volume": self.music_volume,
                "sfx_volume": self.sfx_volume
            }
            with open(self.settings_path, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"⚠️  Could not save settings: {e}")

    def update_music_volume(self):
        from utils import music_manager
        music_manager.set_volume(self.music_volume)


# Game Save Manager
class SaveManager:
    def __init__(self):
        self.save_path = os.path.join(PROJECT_ROOT, "savegame.json")

    def new_game(self):
        save_data = {
            "leafs": 0,
            "season": "Spring",
            "season_index": 0,
            "season_timer": 0,
            "plants": 0,
            "plant_cost": 10,
            "owns_improved_soil": False,
            "created_at": time.time(),
            "last_updated": time.time()
        }
        self.save_game(save_data)
        return save_data

    def load_game(self):
        try:
            if os.path.exists(self.save_path):
                with open(self.save_path, "r") as f:
                    save_data = json.load(f)
                    print(f"Loaded save game with {save_data.get('leafs', 0)} leafs")
                    return save_data
            else:
                print("No save file found, creating new game")
                return self.new_game()
        except Exception as e:
            print(f"Could not load save game: {e}")
            return self.new_game()

    def save_game(self, save_data):
        try:
            save_data["last_updated"] = time.time()
            with open(self.save_path, "w") as f:
                json.dump(save_data, f, indent=2)
            print(f"Game saved with {save_data.get('leafs', 0)} leafs")
        except Exception as e:
            print(f"Could not save game: {e}")


# Slider class for volume controls
class Slider:
    def __init__(self, x, y, width, value=0.5):
        self.rect = pygame.Rect(x, y, width, 20)
        self.handle_radius = 12
        self.value = value  # 0.0 to 1.0
        self.dragging = False

    def draw(self, surface):
        # Draw slider background
        pygame.draw.rect(surface, SLIDER_BG_COLOR, self.rect, border_radius=10)
        pygame.draw.rect(surface, (80, 80, 90), self.rect, 2, border_radius=10)

        # Draw filled portion
        fill_width = int(self.value * self.rect.width)
        fill_rect = pygame.Rect(self.rect.x, self.rect.y, fill_width, self.rect.height)
        pygame.draw.rect(surface, SLIDER_COLOR, fill_rect, border_radius=10)

        # Draw handle
        handle_x = self.rect.x + int(self.value * self.rect.width)
        handle_pos = (handle_x, self.rect.centery)
        pygame.draw.circle(surface, SLIDER_HANDLE_COLOR, handle_pos, self.handle_radius)
        pygame.draw.circle(surface, (255, 255, 255), handle_pos, self.handle_radius, 2)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            handle_x = self.rect.x + int(self.value * self.rect.width)
            handle_rect = pygame.Rect(handle_x - self.handle_radius,
                                      self.rect.y - self.handle_radius,
                                      self.handle_radius * 2,
                                      self.handle_radius * 2)
            if handle_rect.collidepoint(mouse_pos) or self.rect.collidepoint(mouse_pos):
                self.dragging = True
                self.update_value(mouse_pos[0])
                return True

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.dragging = False

        elif event.type == pygame.MOUSEMOTION and self.dragging:
            self.update_value(event.pos[0])
            return True

        return False

    def update_value(self, mouse_x):
        mouse_x = max(self.rect.x, min(self.rect.right, mouse_x))
        self.value = (mouse_x - self.rect.x) / self.rect.width
        return self.value


# Button class
class Button:
    def __init__(self, x, y, width, height, text, action=None, is_back_button=False, font_size=32):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.action = action
        self.is_back_button = is_back_button
        self.hovered = False
        self.was_hovered = False
        self.font = get_font(font_size)

    def draw(self, surface):
        color = BUTTON_HOVER_COLOR if self.hovered else BUTTON_COLOR
        border_radius = 10 if self.font.get_height() > 24 else 8
        pygame.draw.rect(surface, color, self.rect, border_radius=border_radius)
        pygame.draw.rect(surface, (255, 255, 255), self.rect, 2, border_radius=border_radius)

        text_surf = self.font.render(self.text, True, BUTTON_TEXT_COLOR)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def check_hover(self, pos):
        self.was_hovered = self.hovered
        self.hovered = self.rect.collidepoint(pos)

        if self.hovered and not self.was_hovered:
            from utils import sound_manager, settings
            sound_manager.play("hover", settings.sfx_volume)

        return self.hovered

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.hovered:
                from utils import sound_manager, settings
                if self.is_back_button:
                    sound_manager.play("back", settings.sfx_volume)
                else:
                    sound_manager.play("select", settings.sfx_volume)
                return self.action
        return None


# Load background images with scaling
def load_background_image(filename, target_size=(WIDTH, HEIGHT)):
    path = os.path.join(ASSETS_DIR, filename)
    if os.path.exists(path):
        try:
            image = pygame.image.load(path).convert()
            # Scale to fit screen while maintaining aspect ratio
            img_width, img_height = image.get_size()

            # Calculate scale ratio
            width_ratio = target_size[0] / img_width
            height_ratio = target_size[1] / img_height
            scale_ratio = max(width_ratio, height_ratio)  # Cover the screen

            # Calculate new dimensions
            new_width = int(img_width * scale_ratio)
            new_height = int(img_height * scale_ratio)

            # Scale the image
            image = pygame.transform.scale(image, (new_width, new_height))

            # Calculate position to center the image
            x_offset = (new_width - target_size[0]) // 2
            y_offset = (new_height - target_size[1]) // 2

            # Crop if needed
            if x_offset > 0 or y_offset > 0:
                image = image.subsurface((x_offset, y_offset, target_size[0], target_size[1]))

            print(f"Loaded background: {filename}")
            return image
        except Exception as e:
            print(f"Could not load background {filename}: {e}")

    # Create fallback background
    print(f"Background not found: {path} - creating fallback")
    fallback = pygame.Surface(target_size)
    # Create a gradient background
    for y in range(target_size[1]):
        color_val = 20 + int(y / target_size[1] * 50)
        pygame.draw.line(fallback, (color_val, color_val + 40, color_val),
                         (0, y), (target_size[0], y))
    return fallback


# Create a semi-transparent surface for overlays
def create_overlay(color, alpha):
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((*color, alpha))
    return overlay


# Initialize managers (but don't load sounds yet - will be done in main.py after mixer init)
sound_manager = SoundManager()
music_manager = MusicManager()
settings = Settings()
save_manager = SaveManager()

import pygame
import sys
import math
import os
from new_test.settings import *
from new_test.managers import SoundManager, MusicManager, SaveManager, SettingsManager
from new_test.game_logic import GameManager, Shop
from new_test.ui import Button, Slider


class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Leafy Loot")

        # Load Icon
        try:
            icon = pygame.image.load(os.path.join(ASSETS_DIR, "icon.png"))
            pygame.display.set_icon(icon)
        except:
            pass

        # --- LOAD BACKGROUNDS ---
        self.menu_bg = None
        self.game_bg = None
        try:
            m_bg = pygame.image.load(os.path.join(ASSETS_DIR, "menu_bg.png")).convert()
            self.menu_bg = pygame.transform.scale(m_bg, (WIDTH, HEIGHT))
            g_bg = pygame.image.load(os.path.join(ASSETS_DIR, "game_bg.png")).convert()
            self.game_bg = pygame.transform.scale(g_bg, (WIDTH, HEIGHT))
        except:
            print("Background images not found, using colors.")

        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 32)
        self.large_font = pygame.font.Font(None, 64)

        # Managers
        self.settings_mgr = SettingsManager()
        self.sound_mgr = SoundManager(self.settings_mgr)
        self.music_mgr = MusicManager(self.settings_mgr)
        self.save_mgr = SaveManager()

        # Load Sounds
        self.sound_mgr.load_sound("select", "Item_Accept.wav")
        self.sound_mgr.load_sound("back", "Item_Decline.wav")
        self.sound_mgr.load_sound("hover", "Option_Selection.wav")
        self.sound_mgr.load_sound("start", "Option_Accept.wav")

        # Game Objects
        self.game_mgr = None
        self.shop = None

        # State Management
        self.state = "PRESCREEN"
        self.prev_state = "MENU"
        self.flash_timer = 0
        self.setup_ui()

        # Start Menu Music
        self.music_mgr.play_music("menu_music.mp3")

    def setup_ui(self):
        cx = WIDTH // 2
        # Main Menu Buttons
        self.menu_buttons = [
            Button(cx - 150, 270, 300, 60, "New Game", "new_game"),
            Button(cx - 150, 350, 300, 60, "Load Game", "load_game"),
            Button(cx - 150, 430, 300, 60, "Settings", "settings"),
            Button(cx - 150, 510, 300, 60, "Exit", "exit", is_back_button=True)
        ]
        # Settings UI
        self.music_slider = Slider(cx - 100, 300, 200, self.settings_mgr.music_vol)
        self.sfx_slider = Slider(cx - 100, 400, 200, self.settings_mgr.sfx_vol)
        self.settings_back_btn = Button(cx - 150, 500, 300, 60, "Back", "back", is_back_button=True)
        # Game Top Bar Buttons
        self.game_buttons = [
            Button(20, 10, 120, 40, "MENU", "game_menu", font_size=24, is_back_button=True),
            Button(160, 10, 120, 40, "SHOP", "game_shop", font_size=24),
            Button(300, 10, 120, 40, "UPGRADES", "game_upgrades", font_size=24)
        ]

    def handle_input(self):
        events = pygame.event.get()
        mouse_pos = pygame.mouse.get_pos()

        for event in events:
            if event.type == pygame.QUIT:
                self.quit_game()

            # --- PRESCREEN LOGIC ---
            if self.state == "PRESCREEN":
                if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                    self.sound_mgr.play("start")
                    self.state = "MENU"

            # --- MOUSE CLICKS ---
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.state == "MENU":
                    for btn in self.menu_buttons:
                        action = btn.handle_click(self.sound_mgr)
                        if action == "new_game":
                            self.start_game(new=True)
                        elif action == "load_game":
                            self.start_game(new=False)
                        elif action == "settings":
                            self.prev_state = "MENU"
                            self.state = "SETTINGS"
                        elif action == "exit":
                            self.quit_game()

                elif self.state == "SETTINGS":
                    action = self.settings_back_btn.handle_click(self.sound_mgr)
                    if action == "back":
                        self.settings_mgr.save()
                        self.state = self.prev_state

                elif self.state == "GAME":
                    if self.shop.is_open:
                        result = self.shop.handle_click(mouse_pos, self.game_mgr.leafs, self.sound_mgr)
                        self.game_mgr.leafs, bought_plant, rate_boost, item_id, mult_value = result

                        # Apply multiplier if one was purchased
                        if mult_value > 1.0:
                            self.game_mgr.production_multiplier *= mult_value

                        # Logic for ALL grid items (Plants, Fertilizer, Sprinklers)
                        if item_id and rate_boost >= 0 and bought_plant:
                            # FIX 2: Use insert(0) to add to Top Left (Newest first)
                            self.game_mgr.plant_grid.insert(0, item_id)
                            self.game_mgr.upgrade_rate_bonus += rate_boost
                        elif item_id and rate_boost > 0 and not bought_plant:
                            # Items like fertilizer that add to grid but aren't "buy_plant" ID
                            self.game_mgr.plant_grid.insert(0, item_id)
                            self.game_mgr.upgrade_rate_bonus += rate_boost

                    else:
                        for btn in self.game_buttons:
                            action = btn.handle_click(self.sound_mgr)
                            if action == "game_menu":
                                # FIX 1: Save shop state
                                self.save_mgr.save_game(self.game_mgr.get_save_data(self.shop))
                                self.state = "MENU"
                                self.music_mgr.play_music("menu_music.mp3")
                            elif action == "game_shop":
                                self.shop.toggle(is_upgrades=False)
                            elif action == "game_upgrades":
                                self.shop.toggle(is_upgrades=True)

        # --- SLIDER DRAGGING ---
        if self.state == "SETTINGS":
            for e in events:
                if self.music_slider.handle_event(e):
                    self.settings_mgr.music_vol = self.music_slider.value
                    self.music_mgr.update_volume()
                if self.sfx_slider.handle_event(e):
                    self.settings_mgr.sfx_vol = self.sfx_slider.value

    def update(self):
        dt = self.clock.tick(FPS) / 1000.0
        mouse_pos = pygame.mouse.get_pos()

        # Update Buttons (Hover Sounds)
        if self.state == "MENU":
            for btn in self.menu_buttons: btn.update(mouse_pos, self.sound_mgr)
        elif self.state == "SETTINGS":
            self.settings_back_btn.update(mouse_pos, self.sound_mgr)
        elif self.state == "GAME":
            # Check for hovers:
            if self.shop.is_open:
                self.shop.check_hover(mouse_pos, self.sound_mgr)
            else:
                for btn in self.game_buttons: btn.update(mouse_pos, self.sound_mgr)

            self.game_mgr.update(dt)

        # Flash Timer
        if self.state == "PRESCREEN":
            self.flash_timer += dt * 1000

    def draw(self):
        self.screen.fill(BG_COLOR)

        if self.state == "PRESCREEN":
            self.draw_prescreen()
        elif self.state == "MENU":
            self.draw_menu()
        elif self.state == "SETTINGS":
            self.draw_settings()
        elif self.state == "GAME":
            self.draw_game()

        pygame.display.flip()

    def _draw_common_menu_elements(self, title_y_offset):
        if self.menu_bg:
            self.screen.blit(self.menu_bg, (0, 0))
        else:
            self.screen.fill(BG_COLOR)  # Fallback to color

        # Draw Title with Shadow
        title = self.large_font.render("LEAFY LOOT", True, TEXT_COLOR)
        shadow = self.large_font.render("LEAFY LOOT", True, (0, 0, 0))

        # Apply offset for shadow (3px down/right)
        self.screen.blit(shadow, (WIDTH // 2 - title.get_width() // 2 + 3, title_y_offset + 3))
        # Apply main title
        self.screen.blit(title, (WIDTH // 2 - title.get_width() // 2, title_y_offset))

    def draw_menu(self):
        self._draw_common_menu_elements(title_y_offset=100)
        for btn in self.menu_buttons:
            btn.draw(self.screen)

    def draw_prescreen(self):
        self._draw_common_menu_elements(title_y_offset=HEIGHT // 2 - 50)
        if (self.flash_timer // 500) % 2 == 0:
            msg = self.font.render("Press any key to start", True, (200, 200, 200))
            self.screen.blit(msg, (WIDTH // 2 - msg.get_width() // 2, HEIGHT // 2 + 50))

    def draw_settings(self):
        if self.menu_bg:
            self.screen.blit(self.menu_bg, (0, 0))
        else:
            self.screen.fill(BG_COLOR)

        title = self.large_font.render("SETTINGS", True, TEXT_COLOR)
        self.screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 100))

        # Music
        lbl = self.font.render(f"Music Volume: {int(self.music_slider.value * 100)}%", True, TEXT_COLOR)
        self.screen.blit(lbl, (WIDTH // 2 - 100, 270))
        self.music_slider.draw(self.screen)

        # SFX
        lbl2 = self.font.render(f"SFX Volume: {int(self.sfx_slider.value * 100)}%", True, TEXT_COLOR)
        self.screen.blit(lbl2, (WIDTH // 2 - 100, 370))
        self.sfx_slider.draw(self.screen)

        self.settings_back_btn.draw(self.screen)

    def draw_game(self):
        if self.game_bg:
            self.screen.blit(self.game_bg, (0, 0))

        # Top Bar
        pygame.draw.rect(self.screen, GAME_UI_BG, (0, 0, WIDTH, 60))
        pygame.draw.line(self.screen, TEXT_COLOR, (0, 60), (WIDTH, 60), 2)

        # Planting Area
        pygame.draw.rect(self.screen, PLANTING_AREA_COLOR, (50, 80, WIDTH - 100, HEIGHT - 180), border_radius=10)

        # Info
        stats = self.game_mgr.get_stats()
        info = f"Leafs: {stats['leafs']} | Season: {stats['season']} | Rate: {stats['rate']:.1f}/s"
        txt = self.font.render(info, True, TEXT_COLOR)
        self.screen.blit(txt, (WIDTH // 2 - txt.get_width() // 2, HEIGHT - 60))

        # Draw Grid/Plants
        self.draw_plants()

        # Buttons
        for btn in self.game_buttons: btn.draw(self.screen)

        # Season Visual
        if stats.get('season_visual_alpha', 0) > 0:
            alpha = stats['season_visual_alpha']
            season_name = stats['season'].upper()
            s_surf = pygame.Surface((WIDTH, 100), pygame.SRCALPHA)
            s_surf.fill((0, 0, 0, min(150, alpha)))
            s_font = pygame.font.Font(None, 80)
            txt_s = s_font.render(f"{season_name} IS HERE", True, (255, 255, 255))
            txt_s.set_alpha(alpha)
            rect = txt_s.get_rect(center=(WIDTH // 2, 50))
            s_surf.blit(txt_s, rect)
            self.screen.blit(s_surf, (0, HEIGHT // 2 - 50))

        # Shop Overlay
        self.shop.draw(self.screen, WIDTH, HEIGHT, self.game_mgr.leafs)

    def draw_plants(self):
        for i, item_id in enumerate(self.game_mgr.plant_grid[:100]):
            x, y = self.game_mgr.get_plant_screen_pos(i)

            img = self.game_mgr.plant_images.get(item_id)
            if img:
                self.screen.blit(img, (x, y))
            else:
                color = (100, 200, 100)
                if item_id == "rate_10min":
                    color = (150, 150, 100)
                elif item_id == "rate_50min":
                    color = (100, 100, 200)
                pygame.draw.circle(self.screen, color, (x + 20, y + 20), 15)

    def start_game(self, new=False):
        if new:
            data = self.save_mgr.new_game()
        else:
            data = self.save_mgr.load_game()

        self.game_mgr = GameManager(data)
        self.shop = Shop()

        # FIX 1: Load shop state if it exists in save data
        if "shop_state" in data:
            self.shop.load_state(data["shop_state"])
        else:
            # Recalculate cost based on plant count if no specific shop state exists (legacy support)
            self.shop.recalculate_cost(self.game_mgr.plants)

        self.state = "GAME"
        self.music_mgr.play_music("game_music.mp3")

    def quit_game(self):
        if self.game_mgr:
            # FIX 1: Pass shop instance so its data is saved
            self.save_mgr.save_game(self.game_mgr.get_save_data(self.shop))
        self.settings_mgr.save()
        pygame.quit()
        sys.exit()

    def run(self):
        while True:
            self.handle_input()
            self.update()
            self.draw()


if __name__ == "__main__":
    Game().run()
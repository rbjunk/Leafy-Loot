import pygame
import sys
import os
from settings import WIDTH, HEIGHT, FPS, BG_COLOR, TEXT_COLOR, GAME_UI_BG, PLANTING_AREA_COLOR, ASSETS_DIR
from managers import SoundManager, MusicManager, SaveManager, SettingsManager
from game_logic import GameManager, Shop
from ui import Button, Slider


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

        # --- BACKGROUND LOADING (With Seasons) ---
        self.backgrounds = {}
        self.menu_bg = None
        self.current_bg = None
        self.next_bg = None  # For fading
        self.bg_fade_alpha = 0

        # Helper to safely load backgrounds
        def load_bg(name):
            try:
                img = pygame.image.load(os.path.join(ASSETS_DIR, name)).convert()
                return pygame.transform.scale(img, (WIDTH, HEIGHT))
            except:
                return None

        self.menu_bg = load_bg("menu_bg.png")
        self.backgrounds["Spring"] = load_bg("game_spring_bg.png")
        self.backgrounds["Summer"] = load_bg("game_summer_bg.png")
        self.backgrounds["Fall"] = load_bg("game_fall_bg.png")
        self.backgrounds["Winter"] = load_bg("game_winter_bg.png")

        # UI ICONS
        self.icons = {}

        def load_icon(name):
            path = os.path.join(ASSETS_DIR, name)
            if os.path.exists(path):
                img = pygame.image.load(path).convert_alpha()
                return pygame.transform.scale(img, (32, 32))
            return None

        self.icons["season"] = load_icon("season_icon.png")
        self.icons["rate"] = load_icon("rate_icon.png")
        self.icons["leaf"] = load_icon("leaf_icon.png")

        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 32)
        self.large_font = pygame.font.Font(None, 64)

        # Managers
        self.settings_mgr = SettingsManager()
        self.sound_mgr = SoundManager(self.settings_mgr)
        self.music_mgr = MusicManager(self.settings_mgr)
        self.save_mgr = SaveManager()

        # Load Sounds (Two variations of hover)
        self.sound_mgr.load_sound("select", "Item_Accept.wav")
        self.sound_mgr.load_sound("back", "Item_Decline.wav")
        self.sound_mgr.load_sound("hover1", "Option_Selection.wav")
        self.sound_mgr.load_sound("hover2", "Option_Selection2.wav")
        self.sound_mgr.load_sound("start", "Option_Accept.wav")
        self.sound_mgr.load_sound("error", "Error.wav")  # Added error sound mapping

        # Game Objects
        self.game_mgr = None
        self.shop = None
        self.shop_scroll = 0
        self.shop_scroll_dragging = False
        self.shop_scroll_drag_offset = 0

        self.state = "PRESCREEN"
        self.prev_state = "MENU"
        self.flash_timer = 0
        self.setup_ui()

        # Start Menu Music
        self.music_mgr.play_music("menu_music.mp3")

    def setup_ui(self):
        cx = WIDTH // 2
        self.menu_buttons = [
            Button(cx - 150, 270, 300, 60, "New Game", "new_game"),
            Button(cx - 150, 350, 300, 60, "Load Game", "load_game"),
            Button(cx - 150, 430, 300, 60, "Settings", "settings"),
            Button(cx - 150, 510, 300, 60, "Exit", "exit", is_back_button=True)
        ]
        self.music_slider = Slider(cx - 100, 300, 200, self.settings_mgr.music_vol)
        self.sfx_slider = Slider(cx - 100, 400, 200, self.settings_mgr.sfx_vol)
        self.settings_back_btn = Button(cx - 150, 500, 300, 60, "Back", "back", is_back_button=True)
        self.game_buttons = [
            Button(20, 10, 120, 40, "MENU", "game_menu", font_size=24, is_back_button=True),
            Button(160, 10, 120, 40, "SHOP", "game_shop", font_size=24),
            Button(300, 10, 120, 40, "UPGRADES", "game_upgrades", font_size=24)
        ]

    def update_background(self, season):
        """Logic to switch backgrounds smoothly"""
        target_bg = self.backgrounds.get(season)
        if self.current_bg != target_bg and self.next_bg != target_bg:
            if self.current_bg is None:
                self.current_bg = target_bg
            else:
                self.next_bg = target_bg
                self.bg_fade_alpha = 0

    def update_music(self, season):
        """Logic to switch music based on season"""
        # Mapping season name to filename
        track_map = {
            "Spring": "music_spring.mp3",
            "Summer": "music_summer.mp3",
            "Fall": "music_fall.mp3",
            "Winter": "music_winter.mp3"
        }
        filename = track_map.get(season, "game_music.mp3")
        self.music_mgr.play_music(filename, fade_ms=2000)

    def handle_input(self):
        events = pygame.event.get()
        mouse_pos = pygame.mouse.get_pos()

        for event in events:
            if event.type == pygame.QUIT:
                self.quit_game()

            if self.state == "PRESCREEN":
                if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                    self.sound_mgr.play("start")
                    self.state = "MENU"
                    return

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
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
                            track_rect, thumb_rect, max_scroll = self.shop.get_scrollbar_info(WIDTH, HEIGHT,
                                                                                              self.shop_scroll)
                            if thumb_rect and thumb_rect.collidepoint(mouse_pos):
                                self.shop_scroll_dragging = True
                                self.shop_scroll_drag_offset = mouse_pos[1] - thumb_rect.top
                            elif track_rect and track_rect.collidepoint(mouse_pos) and thumb_rect:
                                thumb_h = thumb_rect.height
                                track_space = track_rect.height - thumb_h
                                new_thumb_top = max(track_rect.top,
                                                    min(track_rect.bottom - thumb_h, mouse_pos[1] - thumb_h // 2))
                                proportion = (new_thumb_top - track_rect.top) / track_space if track_space > 0 else 0
                                self.shop_scroll = proportion * max_scroll
                            else:
                                result = self.shop.handle_click(mouse_pos, self.game_mgr.leafs, self.sound_mgr)
                                self.game_mgr.leafs, bought_plant, rate_boost, item_id, mult_value = result

                                if mult_value > 1.0:
                                    self.game_mgr.production_multiplier *= mult_value

                                if item_id and rate_boost >= 0 and bought_plant:
                                    self.game_mgr.plant_grid.insert(0, item_id)
                                    self.game_mgr.upgrade_rate_bonus += rate_boost
                                elif item_id and rate_boost > 0 and not bought_plant:
                                    self.game_mgr.plant_grid.insert(0, item_id)
                                    self.game_mgr.upgrade_rate_bonus += rate_boost

                        else:
                            for btn in self.game_buttons:
                                action = btn.handle_click(self.sound_mgr)
                                if action == "game_menu":
                                    self.save_mgr.save_game(self.game_mgr.get_save_data(self.shop))
                                    self.state = "MENU"
                                    self.music_mgr.play_music("menu_music.mp3")
                                elif action == "game_shop":
                                    self.shop.toggle(is_upgrades=False)
                                    self.shop_scroll = 0
                                elif action == "game_upgrades":
                                    self.shop.toggle(is_upgrades=True)
                                    self.shop_scroll = 0

            if event.type == pygame.MOUSEMOTION:
                if getattr(self, 'shop_scroll_dragging', False) and self.shop and self.shop.is_open:
                    track_rect, thumb_rect, max_scroll = self.shop.get_scrollbar_info(WIDTH, HEIGHT, self.shop_scroll)
                    if thumb_rect:
                        thumb_h = thumb_rect.height
                        track_space = track_rect.height - thumb_h
                        new_thumb_top = mouse_pos[1] - self.shop_scroll_drag_offset
                        new_thumb_top = max(track_rect.top, min(track_rect.bottom - thumb_h, new_thumb_top))
                        proportion = (new_thumb_top - track_rect.top) / track_space if track_space > 0 else 0
                        self.shop_scroll = proportion * max_scroll

            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    if getattr(self, 'shop_scroll_dragging', False):
                        self.shop_scroll_dragging = False

            if event.type == pygame.MOUSEWHEEL:
                if self.state == "GAME" and self.shop and self.shop.is_open:
                    scroll_step = 40
                    self.shop_scroll -= event.y * scroll_step
                    max_scroll = self.shop.get_max_scroll(WIDTH, HEIGHT)
                    if self.shop_scroll < 0: self.shop_scroll = 0
                    if self.shop_scroll > max_scroll: self.shop_scroll = max_scroll

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

        if self.state == "MENU":
            for btn in self.menu_buttons: btn.update(mouse_pos, self.sound_mgr)
        elif self.state == "SETTINGS":
            self.settings_back_btn.update(mouse_pos, self.sound_mgr)
        elif self.state == "GAME":
            if self.shop.is_open:
                self.shop.check_hover(mouse_pos, self.sound_mgr)
            else:
                for btn in self.game_buttons: btn.update(mouse_pos, self.sound_mgr)

            self.game_mgr.update(dt)

            # Check for season change to trigger music/BG fade
            if self.game_mgr.just_changed_season:
                self.update_background(self.game_mgr.season)
                self.update_music(self.game_mgr.season)

            # Handle BG Fading
            if self.next_bg:
                self.bg_fade_alpha += dt * 100  # Speed of fade
                if self.bg_fade_alpha >= 255:
                    self.bg_fade_alpha = 255
                    self.current_bg = self.next_bg
                    self.next_bg = None

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
            self.screen.fill(BG_COLOR)
        title = self.large_font.render("LEAFY LOOT", True, TEXT_COLOR)
        shadow = self.large_font.render("LEAFY LOOT", True, (0, 0, 0))
        self.screen.blit(shadow, (WIDTH // 2 - title.get_width() // 2 + 3, title_y_offset + 3))
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
        lbl = self.font.render(f"Music Volume: {int(self.music_slider.value * 100)}%", True, TEXT_COLOR)
        self.screen.blit(lbl, (WIDTH // 2 - 100, 270))
        self.music_slider.draw(self.screen)
        lbl2 = self.font.render(f"SFX Volume: {int(self.sfx_slider.value * 100)}%", True, TEXT_COLOR)
        self.screen.blit(lbl2, (WIDTH // 2 - 100, 370))
        self.sfx_slider.draw(self.screen)
        self.settings_back_btn.draw(self.screen)

    def draw_game(self):
        # 1. Background (with Fade Support)
        if self.current_bg:
            self.screen.blit(self.current_bg, (0, 0))
        else:
            self.screen.fill(BG_COLOR)  # Fallback

        if self.next_bg:
            # We must blit next_bg with alpha
            # Pygame surfaces don't support per-pixel alpha easily without blitting to a temp surface
            # but for a full screen fade, set_alpha on the surface works.
            self.next_bg.set_alpha(int(self.bg_fade_alpha))
            self.screen.blit(self.next_bg, (0, 0))
            # Reset alpha for next frame use or when it becomes main bg
            self.next_bg.set_alpha(255)

            # 2. Top Bar
        pygame.draw.rect(self.screen, GAME_UI_BG, (0, 0, WIDTH, 60))
        pygame.draw.line(self.screen, TEXT_COLOR, (0, 60), (WIDTH, 60), 2)

        # 3. Planting Area (Transparent)
        # Create a surface with per-pixel alpha capability
        plant_area_surf = pygame.Surface((WIDTH - 100, HEIGHT - 180), pygame.SRCALPHA)
        # Fill with color + alpha (R, G, B, Alpha) - 180 is transparency level
        r, g, b = PLANTING_AREA_COLOR
        plant_area_surf.fill((r, g, b, 180))
        self.screen.blit(plant_area_surf, (50, 80))
        # Draw border
        pygame.draw.rect(self.screen, (80, 100, 80), (50, 80, WIDTH - 100, HEIGHT - 180), 2, border_radius=10)

        # 4. Draw Grid/Plants
        self.draw_plants()

        # 5. Info Bar (Season | Rate | Leafs) with Icons
        stats = self.game_mgr.get_stats()

        # Define layout
        start_y = HEIGHT - 50
        section_width = WIDTH // 3

        # Helper to draw icon+text centered in a section
        def draw_stat(idx, icon_key, text):
            center_x = (section_width * idx) + (section_width // 2)

            icon = self.icons.get(icon_key)
            txt_surf = self.font.render(text, True, TEXT_COLOR)

            total_w = txt_surf.get_width()
            if icon: total_w += icon.get_width() + 10

            start_x = center_x - (total_w // 2)

            if icon:
                self.screen.blit(icon, (start_x, start_y - 8))  # -8 centers 32px icon vs 32px font roughly
                self.screen.blit(txt_surf, (start_x + icon.get_width() + 10, start_y))
            else:
                self.screen.blit(txt_surf, (start_x, start_y))

        # Draw Stats: Season -> Rate -> Leafs
        draw_stat(0, "season", f"{stats['season']}")
        draw_stat(1, "rate", f"{stats['rate']:.1f}/s")
        draw_stat(2, "leaf", f"{stats['leafs']}")

        # 6. Buttons
        for btn in self.game_buttons: btn.draw(self.screen)

        # 7. Season Visual Overlay Text
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

        # 8. Shop Overlay
        self.shop.draw(self.screen, WIDTH, HEIGHT, self.game_mgr.leafs, self.shop_scroll)

    def draw_plants(self):
        # We iterate plant grid
        for i, item_id in enumerate(self.game_mgr.plant_grid[:100]):
            x, y = self.game_mgr.get_plant_screen_pos(i)
            # Use universal loaded image or missing fallback
            img = self.game_mgr.plant_images.get(item_id)

            # Should not happen due to universal load, but safety check
            if img:
                self.screen.blit(img, (x, y))
            else:
                # Ultimate failsafe magenta circle
                pygame.draw.circle(self.screen, (255, 0, 255), (x + 20, y + 20), 15)

    def start_game(self, new=False):
        if new:
            data = self.save_mgr.new_game()
        else:
            data = self.save_mgr.load_game()

        self.game_mgr = GameManager(data)
        self.shop = Shop()

        if "shop_state" in data:
            self.shop.load_state(data["shop_state"])
        else:
            self.shop.recalculate_cost(self.game_mgr.plants)

        # Initialize Background and Music for current season
        self.current_bg = self.backgrounds.get(self.game_mgr.season)
        self.update_music(self.game_mgr.season)

        self.state = "GAME"

    def quit_game(self):
        if self.game_mgr:
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
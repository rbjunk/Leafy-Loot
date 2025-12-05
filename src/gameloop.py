import pygame
import sys
import time
import os
from utils import (
    WIDTH, HEIGHT, get_font, load_background_image, create_overlay,
    sound_manager, music_manager, settings, save_manager, ASSETS_DIR,
    Button, Slider, TEXT_COLOR, GAME_UI_BG, PLANTING_AREA_COLOR,
    PLANTING_GRID_COLOR, BUTTON_HOVER_COLOR
)
from game_objects import GameManager, Shop


class GameLoop:
    def __init__(self, screen):
        self.screen = screen
        self.screen_center = screen.get_rect().center
        self.clock = pygame.time.Clock()

        # Load background images
        self.game_background = load_background_image("game_bg.png")
        self.menu_background = load_background_image("menu_bg.png")

        # Initialize fonts FIRST
        self.font = get_font(24)
        self.title_font = get_font(64)  # Initialize this BEFORE load_logo()
        self.menu_font = get_font(36)
        self.large_game_font = get_font(28)
        self.game_font = get_font(20)

        # Load or create logo (AFTER fonts are created)
        self.logo = None
        self.load_logo()

        # Game state
        self.game_state = 'menu'  # 'menu', 'main_menu', 'game', 'settings', 'pause'
        self.settings_source = 'main_menu'  # 'main_menu' or 'pause_menu'

        # Initialize game objects
        self.game_manager = GameManager()
        self.shop = Shop(700, 500)

        # Menu variables
        self.flash_text = True
        self.flash_timer = 0
        self.flash_interval = 500

        # Create overlays
        self.pause_overlay = create_overlay((0, 0, 0), 180)

        # Create buttons
        self.create_buttons()

        # Create sliders
        self.music_slider = Slider(WIDTH // 2 - 100, 300, 200, settings.music_volume)
        self.sfx_slider = Slider(WIDTH // 2 - 100, 400, 200, settings.sfx_volume)

        # Start menu music on prescreen
        if music_manager.menu_music:
            music_manager.play_music("menu")

        self.last_frame_time = time.time()

    def load_logo(self):
        logo_path = os.path.join(ASSETS_DIR, "logo.png")
        if os.path.exists(logo_path):
            self.logo = pygame.image.load(logo_path).convert_alpha()
        else:
            # Create a simple logo with centered text
            logo_width, logo_height = 400, 200
            self.logo = pygame.Surface((logo_width, logo_height), pygame.SRCALPHA)
            # Draw decorative border
            pygame.draw.rect(self.logo, (144, 238, 144), (0, 0, logo_width, logo_height), 5, border_radius=15)
            # Draw background with some transparency
            for i in range(logo_height):
                alpha = 200 - int(i / logo_height * 50)
                color = (30 + int(i / logo_height * 20),
                         50 + int(i / logo_height * 40),
                         30 + int(i / logo_height * 20))
                pygame.draw.line(self.logo, (*color, alpha), (0, i), (logo_width, i))
            # Create centered title text - NOW self.title_font exists
            logo_text = self.title_font.render("LEAFY LOOT", True, TEXT_COLOR)
            text_rect = logo_text.get_rect(center=(logo_width // 2, logo_height // 2))
            self.logo.blit(logo_text, text_rect)

    def create_buttons(self):
        # Main menu buttons
        self.main_menu_buttons = [
            Button(WIDTH // 2 - 150, 270, 300, 60, "New Game", 'new_game', font_size=32),
            Button(WIDTH // 2 - 150, 350, 300, 60, "Load Game", 'load_game', font_size=32),
            Button(WIDTH // 2 - 150, 430, 300, 60, "Settings", 'settings', font_size=32),
            Button(WIDTH // 2 - 150, 510, 300, 60, "Exit", 'exit', font_size=32)
        ]

        # Settings back button
        self.settings_buttons = [
            Button(WIDTH // 2 - 150, 430, 300, 60, "Back", 'back_from_settings', is_back_button=True, font_size=32)
        ]

        # Pause menu buttons
        self.pause_menu_buttons = [
            Button(WIDTH // 2 - 150, 250, 300, 60, "Settings", 'pause_settings', font_size=32),
            Button(WIDTH // 2 - 150, 330, 300, 60, "Exit to Menu", 'exit_to_menu', is_back_button=True, font_size=32),
            Button(WIDTH // 2 - 150, 410, 300, 60, "Back to Game", 'back_to_game', is_back_button=True, font_size=32)
        ]

        # Game UI buttons
        button_width, button_height = 120, 40
        button_spacing = 20
        total_width = 3 * button_width + 2 * button_spacing
        start_x = (WIDTH - total_width) // 2

        self.game_ui_buttons = [
            Button(start_x, 10, button_width, button_height, "MENU", 'game_menu', font_size=20),
            Button(start_x + button_width + button_spacing, 10, button_width, button_height, "SHOP", 'game_shop',
                   font_size=20),
            Button(start_x + 2 * (button_width + button_spacing), 10, button_width, button_height, "UPGRADES",
                   'game_upgrades', font_size=20)
        ]

    def draw_game_ui(self, stats):
        # Top Bar with buttons
        top_bar = pygame.Rect(0, 0, WIDTH, 60)
        pygame.draw.rect(self.screen, (*GAME_UI_BG[:3], 220), top_bar)
        pygame.draw.line(self.screen, (144, 238, 144), (0, 60), (WIDTH, 60), 3)

        # Draw buttons
        for btn in self.game_ui_buttons:
            btn.draw(self.screen)

        # Planting Area (middle section)
        planting_area = pygame.Rect(50, 80, WIDTH - 100, HEIGHT - 180)
        pygame.draw.rect(self.screen, PLANTING_AREA_COLOR, planting_area, border_radius=10)
        pygame.draw.rect(self.screen, (100, 140, 100), planting_area, 3, border_radius=10)

        # Draw planting grid - 10x10
        grid_cols, grid_rows = 10, 10
        cell_width = planting_area.width // grid_cols
        cell_height = planting_area.height // grid_rows

        # Draw grid lines
        for x in range(planting_area.left, planting_area.right + 1, cell_width):
            pygame.draw.line(self.screen, PLANTING_GRID_COLOR, (x, planting_area.top), (x, planting_area.bottom), 1)
        for y in range(planting_area.top, planting_area.bottom + 1, cell_height):
            pygame.draw.line(self.screen, PLANTING_GRID_COLOR, (planting_area.left, y), (planting_area.right, y), 1)

        # Draw plants based on how many are purchased
        max_plants_display = grid_cols * grid_rows  # 100 plants can be displayed
        plants_to_draw = min(stats["plants"], max_plants_display)

        if plants_to_draw > 0:
            for i in range(plants_to_draw):
                col = i % grid_cols
                row = i // grid_cols

                center_x = planting_area.left + col * cell_width + cell_width // 2
                center_y = planting_area.top + row * cell_height + cell_height // 2

                # Draw plant image if available, otherwise draw fallback
                if self.game_manager.plant_image:
                    plant_rect = self.game_manager.plant_image.get_rect(center=(center_x, center_y))
                    self.screen.blit(self.game_manager.plant_image, plant_rect)
                else:
                    # Fallback plant drawing (smaller for 10x10 grid)
                    import math
                    plant_radius = 8
                    pygame.draw.line(self.screen, (80, 130, 80),
                                     (center_x, center_y + plant_radius),
                                     (center_x, center_y - plant_radius), 1)

                    leaf_radius = 4
                    for angle in [45, 135, 225, 315]:
                        rad = math.radians(angle)
                        end_x = center_x + math.cos(rad) * plant_radius
                        end_y = center_y + math.sin(rad) * leaf_radius
                        pygame.draw.circle(self.screen, (144, 238, 144), (int(end_x), int(end_y)), leaf_radius)

            # If we have more plants than can be displayed, show a count
            if stats["plants"] > max_plants_display:
                extra_text = self.game_font.render(f"+{stats['plants'] - max_plants_display} more", True,
                                                   (200, 200, 200))
                self.screen.blit(extra_text, (planting_area.right - 120, planting_area.bottom - 25))

        # Bottom stats bar
        bottom_bar = pygame.Rect(0, HEIGHT - 100, WIDTH, 100)
        pygame.draw.rect(self.screen, (*GAME_UI_BG[:3], 220), bottom_bar)
        pygame.draw.line(self.screen, (144, 238, 144), (0, HEIGHT - 100), (WIDTH, HEIGHT - 100), 3)

        # Draw stats
        stat_y = HEIGHT - 80
        stat_spacing = 280

        # Leafs
        leaf_text = self.large_game_font.render(f"LEAFS: {stats['leafs']}", True, TEXT_COLOR)
        self.screen.blit(leaf_text, (30, stat_y))

        # Season with progress bar and time
        season_text = self.large_game_font.render(f"SEASON: {stats['season']}", True, TEXT_COLOR)
        self.screen.blit(season_text, (30 + stat_spacing, stat_y))

        # Season time remaining
        minutes_left = int(stats['season_time_left'] // 60)
        seconds_left = int(stats['season_time_left'] % 60)
        time_text = self.game_font.render(f"Time: {minutes_left:02d}:{seconds_left:02d}", True, (200, 200, 200))
        self.screen.blit(time_text, (30 + stat_spacing, stat_y + 30))

        # Season progress bar
        progress_width = 200
        progress_bar = pygame.Rect(30 + stat_spacing, stat_y + 55, progress_width, 15)
        pygame.draw.rect(self.screen, (50, 50, 50), progress_bar, border_radius=3)

        fill_width = int(progress_width * stats['season_progress'])
        fill_bar = pygame.Rect(30 + stat_spacing, stat_y + 55, fill_width, 15)
        pygame.draw.rect(self.screen, TEXT_COLOR, fill_bar, border_radius=3)
        pygame.draw.rect(self.screen, (200, 200, 200), progress_bar, 2, border_radius=3)

        # Production rate and plants
        prod_text = self.large_game_font.render(f"PRODUCTION: {stats['production_rate']}", True, TEXT_COLOR)
        self.screen.blit(prod_text, (30 + 2 * stat_spacing, stat_y))

        plants_text = self.game_font.render(f"Plants: {stats['plants']} (+{stats['plants']}/sec)", True,
                                            (200, 200, 200))
        self.screen.blit(plants_text, (30 + 2 * stat_spacing, stat_y + 30))

    def handle_menu_events(self, event, mouse_pos):
        for button in self.main_menu_buttons:
            button.check_hover(mouse_pos)
            action = button.handle_event(event)
            if action:
                if action == 'new_game':
                    # Create new save file
                    save_data = save_manager.new_game()
                    self.game_manager.leafs = save_data["leafs"]
                    self.game_manager.plants = save_data.get("plants", 0)
                    self.shop.plant_cost = save_data.get("plant_cost", 10)
                    self.shop.owns_improved_soil = save_data.get("owns_improved_soil", False)
                    # Load season data
                    self.game_manager.season = save_data.get("season", "Spring")
                    self.game_manager.season_index = save_data.get("season_index", 0)
                    self.game_manager.season_timer = save_data.get("season_timer", 0)

                    self.game_state = 'game'
                    # Switch to game music
                    if music_manager.game_music:
                        music_manager.play_music("game")
                elif action == 'load_game':
                    # Load existing save file
                    save_data = save_manager.load_game()
                    self.game_manager.leafs = save_data.get("leafs", 0)
                    self.game_manager.season = save_data.get("season", "Spring")
                    self.game_manager.season_index = save_data.get("season_index", 0)
                    self.game_manager.season_timer = save_data.get("season_timer", 0)
                    self.game_manager.plants = save_data.get("plants", 0)
                    self.shop.plant_cost = save_data.get("plant_cost", 10)
                    self.shop.owns_improved_soil = save_data.get("owns_improved_soil", False)
                    self.game_state = 'game'
                    # Switch to game music
                    if music_manager.game_music:
                        music_manager.play_music("game")
                elif action == 'settings':
                    self.settings_source = 'main_menu'
                    self.game_state = 'settings'
                elif action == 'exit':
                    settings.save_settings()
                    pygame.quit()
                    sys.exit()

    def handle_settings_events(self, event, mouse_pos):
        # Handle sliders
        if self.music_slider.handle_event(event):
            settings.music_volume = self.music_slider.value
            settings.update_music_volume()

        if self.sfx_slider.handle_event(event):
            settings.sfx_volume = self.sfx_slider.value

        # Handle buttons
        for button in self.settings_buttons:
            button.check_hover(mouse_pos)
            action = button.handle_event(event)
            if action == 'back_from_settings':
                # Return to where we came from
                if self.settings_source == 'main_menu':
                    self.game_state = 'main_menu'
                elif self.settings_source == 'pause_menu':
                    self.game_state = 'pause'

    def handle_game_events(self, event, mouse_pos):
        # Check hover for game UI buttons
        for button in self.game_ui_buttons:
            button.check_hover(mouse_pos)

        # Handle clicks for game UI buttons
        for button in self.game_ui_buttons:
            action = button.handle_event(event)
            if action:
                if action == 'game_menu':
                    self.game_state = 'pause'
                elif action == 'game_shop':
                    self.shop.toggle(is_upgrades=False)
                    print("Plant Shop toggled: " + str(self.shop.is_open))
                elif action == 'game_upgrades':
                    self.shop.toggle(is_upgrades=True)
                    print("Upgrades Shop toggled: " + str(self.shop.is_open))

        # Check hover for shop buttons
        if self.shop.is_open:
            self.shop.check_hover(mouse_pos)

        # Handle shop clicks
        if self.shop.is_open and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            updated_leafs, should_close, plant_purchased = self.shop.handle_click(mouse_pos, self.game_manager.leafs)
            if should_close:
                self.shop.toggle()
            elif updated_leafs < self.game_manager.leafs:  # If we spent leafs
                self.game_manager.leafs = updated_leafs
                if plant_purchased:
                    self.game_manager.add_plant()

    def handle_pause_events(self, event, mouse_pos):
        # Check hover for pause menu buttons
        for button in self.pause_menu_buttons:
            button.check_hover(mouse_pos)

        # Handle clicks for pause menu buttons
        for button in self.pause_menu_buttons:
            action = button.handle_event(event)
            if action:
                if action == 'pause_settings':
                    self.settings_source = 'pause_menu'
                    self.game_state = 'settings'
                elif action == 'exit_to_menu':
                    # Save game before exiting
                    save_data = {
                        "leafs": self.game_manager.leafs,
                        "season": self.game_manager.season,
                        "season_index": self.game_manager.season_index,
                        "season_timer": self.game_manager.season_timer,
                        "plants": self.game_manager.plants,
                        "plant_cost": self.shop.plant_cost,
                        "owns_improved_soil": self.shop.owns_improved_soil
                    }
                    save_manager.save_game(save_data)
                    self.game_state = 'main_menu'
                    # Switch back to menu music
                    if music_manager.menu_music:
                        music_manager.play_music("menu")
                elif action == 'back_to_game':
                    self.game_state = 'game'

        # ESC also exits pause menu
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                sound_manager.play("back", settings.sfx_volume)
                self.game_state = 'game'

    def draw_menu_screen(self):
        # Draw logo
        if self.logo:
            logo_rect = self.logo.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 100))
            self.screen.blit(self.logo, logo_rect)

        # Draw flashing "Press any key to start"
        if self.flash_text:
            press_text = self.font.render("Press any key to start", True, TEXT_COLOR)
            press_rect = press_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 150))
            self.screen.blit(press_text, press_rect)

        # Draw copyright - updated to SWE Group
        credit_text = self.font.render("SWE Group © 2023", True, (200, 200, 200, 180))
        self.screen.blit(credit_text, (WIDTH - 250, HEIGHT - 40))

    def draw_main_menu(self):
        # Draw logo
        if self.logo:
            logo_rect = self.logo.get_rect(center=(WIDTH // 2, 150))
            self.screen.blit(self.logo, logo_rect)

        # Draw buttons
        for button in self.main_menu_buttons:
            button.draw(self.screen)

    def draw_settings_screen(self):
        # Draw semi-transparent overlay
        self.screen.blit(self.pause_overlay, (0, 0))

        # Draw title
        title = self.menu_font.render("SETTINGS", True, TEXT_COLOR)
        self.screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 100))

        # Draw music volume control
        music_text = self.font.render(f"Music Volume: {int(settings.music_volume * 100)}%", True, TEXT_COLOR)
        self.screen.blit(music_text, (WIDTH // 2 - 200, 270))
        self.music_slider.draw(self.screen)

        # Draw SFX volume control
        sfx_text = self.font.render(f"SFX Volume: {int(settings.sfx_volume * 100)}%", True, TEXT_COLOR)
        self.screen.blit(sfx_text, (WIDTH // 2 - 200, 370))
        self.sfx_slider.draw(self.screen)

        # Draw buttons (only Back button)
        for button in self.settings_buttons:
            button.draw(self.screen)

    def run(self):
        while True:
            current_time = pygame.time.get_ticks()
            mouse_pos = pygame.mouse.get_pos()

            # Calculate delta time for smooth updates
            current_real_time = time.time()
            delta_time = current_real_time - self.last_frame_time
            self.last_frame_time = current_real_time

            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    # Auto-save on quit if in game
                    if self.game_state == 'game':
                        save_data = {
                            "leafs": self.game_manager.leafs,
                            "season": self.game_manager.season,
                            "season_index": self.game_manager.season_index,
                            "season_timer": self.game_manager.season_timer,
                            "plants": self.game_manager.plants,
                            "plant_cost": self.shop.plant_cost,
                            "owns_improved_soil": self.shop.owns_improved_soil
                        }
                        save_manager.save_game(save_data)
                    settings.save_settings()
                    pygame.quit()
                    sys.exit()

                # State: Initial menu (press any key to continue)
                if self.game_state == 'menu':
                    if event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                        sound_manager.play("start", settings.sfx_volume)
                        self.game_state = 'main_menu'

                # State: Main menu with buttons
                elif self.game_state == 'main_menu':
                    self.handle_menu_events(event, mouse_pos)

                # State: Settings menu
                elif self.game_state == 'settings':
                    self.handle_settings_events(event, mouse_pos)

                # State: In-game
                elif self.game_state == 'game':
                    self.handle_game_events(event, mouse_pos)

                # State: Pause menu
                elif self.game_state == 'pause':
                    self.handle_pause_events(event, mouse_pos)

            # Update flashing text timer
            if current_time - self.flash_timer > self.flash_interval:
                self.flash_text = not self.flash_text
                self.flash_timer = current_time

            # Update game state
            if self.game_state == 'game':
                self.game_manager.update(delta_time)

            # Draw everything based on state
            if self.game_state in ['game', 'pause']:
                # Draw game background
                self.screen.blit(self.game_background, (0, 0))

                if self.game_state == 'game':
                    # Get current stats
                    stats = self.game_manager.get_stats()

                    # Draw game UI
                    self.draw_game_ui(stats)

                    # Draw shop if open
                    if self.shop.is_open:
                        self.shop.draw(self.screen, self.screen_center, int(self.game_manager.leafs))

                elif self.game_state == 'pause':
                    # Draw game UI first
                    stats = self.game_manager.get_stats()
                    self.draw_game_ui(stats)

                    # Draw semi-transparent overlay
                    self.screen.blit(self.pause_overlay, (0, 0))

                    # Draw pause menu title
                    pause_title = self.menu_font.render("PAUSED", True, TEXT_COLOR)
                    self.screen.blit(pause_title, (WIDTH // 2 - pause_title.get_width() // 2, 150))

                    # Draw pause menu buttons
                    for button in self.pause_menu_buttons:
                        button.draw(self.screen)

            else:
                # Draw menu background
                self.screen.blit(self.menu_background, (0, 0))

                if self.game_state == 'menu':
                    self.draw_menu_screen()
                elif self.game_state == 'main_menu':
                    self.draw_main_menu()
                elif self.game_state == 'settings':
                    self.draw_settings_screen()

            # Auto-save every 30 seconds while in game
            if self.game_state == 'game':
                if current_time % 30000 < 50:  # Every ~30 seconds
                    save_data = {
                        "leafs": self.game_manager.leafs,
                        "season": self.game_manager.season,
                        "season_index": self.game_manager.season_index,
                        "season_timer": self.game_manager.season_timer,
                        "plants": self.game_manager.plants,
                        "plant_cost": self.shop.plant_cost,
                        "owns_improved_soil": self.shop.owns_improved_soil
                    }
                    save_manager.save_game(save_data)

            # Update display
            pygame.display.flip()
            self.clock.tick(60)

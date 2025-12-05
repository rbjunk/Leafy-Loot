import pygame
import os
import math
from utils import ASSETS_DIR, BUTTON_HOVER_COLOR, get_font, sound_manager, settings


# Shop class
class Shop:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.is_open = False
        self.plant_cost = 10
        self.improved_soil_cost = 100
        self.owns_improved_soil = False
        self.is_upgrades_shop = False  # Differentiate between shop and upgrades

        # Store button rects for click handling
        self.shop_rect = None
        self.close_rect = None
        self.buy_rect = None
        self.close_button_hovered = False
        self.buy_button_hovered = False

    def toggle(self, is_upgrades=False):
        self.is_open = not self.is_open
        self.is_upgrades_shop = is_upgrades

    def draw(self, screen, center, leafs):
        if self.is_open:
            # Create shop background
            shop_rect = pygame.Rect(0, 0, self.width, self.height)
            shop_rect.center = center
            self.shop_rect = shop_rect

            pygame.draw.rect(screen, (40, 40, 50), shop_rect, border_radius=15)
            pygame.draw.rect(screen, (144, 238, 144), shop_rect, 4, border_radius=15)

            # Draw shop title
            title_font = get_font(48)
            title_text = "UPGRADES" if self.is_upgrades_shop else "PLANT SHOP"
            title = title_font.render(title_text, True, (255, 255, 255))
            title_rect = title.get_rect(center=(shop_rect.centerx, shop_rect.top + 40))
            screen.blit(title, title_rect)

            # Create button font here so it's available in both branches
            button_font = get_font(24)

            if self.is_upgrades_shop:
                mouse_pos = pygame.mouse.get_pos()
                # Draw available leafs
                leaf_font = get_font(32)
                leaf_text = leaf_font.render(f"Available Leafs: {leafs}", True, (144, 238, 144))
                leaf_rect = leaf_text.get_rect(center=(shop_rect.centerx, shop_rect.top + 80))
                screen.blit(leaf_text, leaf_rect)

                # Draw plant info
                upgrade_font = get_font(28)
                upgrade_description_area = pygame.Rect(
                    shop_rect.left + 10,
                    shop_rect.top + 280,
                    shop_rect.width - 20,
                    140
                )

                #Try to load improved soil image
                imrpoved_soil_image = None
                improved_soil_image_path = os.path.join(ASSETS_DIR, "improved_soil.png")
                if os.path.exists(improved_soil_image_path):
                    try:
                        improved_soil_image = pygame.image.load(improved_soil_image_path).convert_alpha()
                        # Scale if needed
                        max_size = 120
                        if improved_soil_image.get_width() > max_size or improved_soil_image.get_height() > max_size:
                            scale = max_size / max(improved_soil_image.get_width(), improved_soil_image.get_height())
                            new_width = int(improved_soil_image.get_width() * scale)
                            new_height = int(improved_soil_image.get_height() * scale)
                            improved_soil_image = pygame.transform.scale(improved_soil_image, (new_width, new_height))
                    except:
                        improved_soil_image = None
                # improved soil image/icon area
                improved_soil_area = pygame.Rect(
                    shop_rect.left + 10,
                    shop_rect.top + 120,
                    shop_rect.width / 4,
                    150
                )
                pygame.draw.rect(screen, (50, 70, 50), improved_soil_area, border_radius=10)
                pygame.draw.rect(screen, (100, 150, 100), improved_soil_area, 2, border_radius=10)

                if improved_soil_image:
                    improved_soil_rect = improved_soil_image.get_rect(center=improved_soil_area.center)
                    screen.blit(improved_soil_image, improved_soil_rect)

                is_hovering_improved_soil = improved_soil_area.collidepoint(mouse_pos)
                if is_hovering_improved_soil:
                    pygame.draw.rect(screen, (50, 70, 50), upgrade_description_area, border_radius=10)
                    pygame.draw.rect(screen, (100, 150, 100), upgrade_description_area, 2, border_radius=10)
                    # upgrade name and description
                    improved_soil_name = upgrade_font.render("Improved Soil", True, (220, 220, 220))
                    improved_soil_desc = button_font.render("Improved production of all plants by 10%", True, (180, 180, 180))
                    improved_soil_cost_text = button_font.render(f"Cost: {self.improved_soil_cost} leafs", True, (200, 200, 100))
                    # Name: Centered horizontally, slightly down from the top
                    name_rect = improved_soil_name.get_rect(
                        midtop=(upgrade_description_area.centerx, upgrade_description_area.top + 15)
                    )
                    # Description: Dead center of the box
                    desc_rect = improved_soil_desc.get_rect(
                        center=upgrade_description_area.center
                    )
                    # Cost: Centered horizontally, slightly up from the bottom
                    cost_rect = improved_soil_cost_text.get_rect(
                        midbottom=(upgrade_description_area.centerx, upgrade_description_area.bottom - 15)
                    )
                    # 4. Draw text
                    screen.blit(improved_soil_name, name_rect)
                    screen.blit(improved_soil_desc, desc_rect)
                    screen.blit(improved_soil_cost_text, cost_rect)
                    #Check for mouse clicks
                    if pygame.mouse.get_pressed()[0] and self.owns_improved_soil == False:
                        if leafs >= self.improved_soil_cost:
                            sound_manager.play("select", settings.sfx_volume * 0.7)
                            leafs -= self.improved_soil_cost
                            #Change to now owned
                            self.owns_improved_soil = True
                            print(f"Purchased an upgrade: Improved Soil")



            else:
                # Plant shop
                # Draw available leafs
                leaf_font = get_font(32)
                leaf_text = leaf_font.render(f"Available Leafs: {leafs}", True, (144, 238, 144))
                leaf_rect = leaf_text.get_rect(center=(shop_rect.centerx, shop_rect.top + 80))
                screen.blit(leaf_text, leaf_rect)

                # Draw plant info
                plant_font = get_font(28)

                # Try to load plant image
                plant_image = None
                plant_image_path = os.path.join(ASSETS_DIR, "plant.png")
                if os.path.exists(plant_image_path):
                    try:
                        plant_image = pygame.image.load(plant_image_path).convert_alpha()
                        # Scale if needed
                        max_size = 120
                        if plant_image.get_width() > max_size or plant_image.get_height() > max_size:
                            scale = max_size / max(plant_image.get_width(), plant_image.get_height())
                            new_width = int(plant_image.get_width() * scale)
                            new_height = int(plant_image.get_height() * scale)
                            plant_image = pygame.transform.scale(plant_image, (new_width, new_height))
                    except:
                        plant_image = None

                # Plant image/icon area
                plant_area = pygame.Rect(
                    shop_rect.left + 50,
                    shop_rect.top + 120,
                    shop_rect.width - 100,
                    150
                )
                pygame.draw.rect(screen, (50, 70, 50), plant_area, border_radius=10)
                pygame.draw.rect(screen, (100, 150, 100), plant_area, 2, border_radius=10)

                # Draw plant image or fallback
                if plant_image:
                    plant_rect = plant_image.get_rect(center=plant_area.center)
                    screen.blit(plant_image, plant_rect)
                else:
                    # Fallback plant drawing
                    plant_center = (plant_area.centerx, plant_area.centery - 10)
                    pygame.draw.circle(screen, (100, 150, 100), plant_center, 20)  # Stem base
                    pygame.draw.line(screen, (80, 130, 80),
                                     (plant_center[0], plant_center[1] + 20),
                                     (plant_center[0], plant_center[1] - 40), 4)  # Stem

                    # Draw leaves
                    for angle in [45, 135, 225, 315]:
                        rad = math.radians(angle)
                        end_x = plant_center[0] + math.cos(rad) * 25
                        end_y = plant_center[1] - 20 + math.sin(rad) * 15
                        pygame.draw.circle(screen, (144, 238, 144), (int(end_x), int(end_y)), 12)

                # Plant name and description
                plant_name = plant_font.render("LEAFY PLANT", True, (220, 220, 220))
                screen.blit(plant_name, (plant_area.centerx - plant_name.get_width() // 2, plant_area.bottom + 20))

                plant_desc = button_font.render("Adds +1 leaf per second to production", True, (180, 180, 180))
                screen.blit(plant_desc, (plant_area.centerx - plant_desc.get_width() // 2, plant_area.bottom + 50))

                # Cost
                cost_text = button_font.render(f"Cost: {self.plant_cost} leafs", True, (200, 200, 100))
                screen.blit(cost_text, (plant_area.centerx - cost_text.get_width() // 2, plant_area.bottom + 80))

                # Buy button
                button_width, button_height = 180, 50
                buy_rect = pygame.Rect(
                    shop_rect.centerx - button_width // 2,
                    shop_rect.bottom - 130,
                    button_width,
                    button_height
                )
                self.buy_rect = buy_rect

                # Check if affordable
                can_afford = leafs >= self.plant_cost
                button_color = BUTTON_HOVER_COLOR if self.buy_button_hovered else (70, 150, 70) if can_afford else (
                    100, 100, 100)

                pygame.draw.rect(screen, button_color, buy_rect, border_radius=10)
                pygame.draw.rect(screen, (200, 200, 200), buy_rect, 2, border_radius=10)

                buy_text = button_font.render("BUY PLANT" if can_afford else "CAN'T AFFORD", True, (255, 255, 255))
                buy_rect_text = buy_text.get_rect(center=buy_rect.center)
                screen.blit(buy_text, buy_rect_text)

            # Close button (for both shops)
            close_rect = pygame.Rect(
                shop_rect.centerx - 60,
                shop_rect.bottom - 60,
                120,
                40
            )
            self.close_rect = close_rect

            close_button_color = (200, 80, 80) if self.close_button_hovered else (180, 70, 70)
            pygame.draw.rect(screen, close_button_color, close_rect, border_radius=8)
            pygame.draw.rect(screen, (255, 255, 255), close_rect, 2, border_radius=8)

            close_text = button_font.render("CLOSE", True, (255, 255, 255))
            close_rect_text = close_text.get_rect(center=close_rect.center)
            screen.blit(close_text, close_rect_text)

    def check_hover(self, pos):
        was_close_hovered = self.close_button_hovered
        was_buy_hovered = self.buy_button_hovered

        # Check close button
        self.close_button_hovered = self.close_rect and self.close_rect.collidepoint(pos)

        # Check buy button (only in plant shop)
        self.buy_button_hovered = False
        if not self.is_upgrades_shop and self.buy_rect:
            self.buy_button_hovered = self.buy_rect.collidepoint(pos)

        # Play hover sounds
        if self.close_button_hovered and not was_close_hovered:
            sound_manager.play("hover", settings.sfx_volume * 0.7)
        if self.buy_button_hovered and not was_buy_hovered:
            sound_manager.play("hover", settings.sfx_volume * 0.7)

    def handle_click(self, pos, leafs):
        if not self.is_open or not self.shop_rect:
            return leafs, False, False

        # Check close button
        if self.close_rect and self.close_rect.collidepoint(pos):
            sound_manager.play("select", settings.sfx_volume * 0.7)
            return leafs, True, False

        # Check buy button (only in plant shop)
        if not self.is_upgrades_shop and self.buy_rect and self.buy_rect.collidepoint(pos):
            if leafs >= self.plant_cost:
                sound_manager.play("select", settings.sfx_volume * 0.7)
                leafs -= self.plant_cost
                # Increase cost for next plant
                self.plant_cost = int(self.plant_cost * 1.1)  # 10% increase
                print(f"Purchased a plant! New cost: {self.plant_cost} leafs")
                return leafs, False, True  # Return leafs, don't close, plant purchased

        return leafs, False, False


# Game Manager to handle game state
class GameManager:
    def __init__(self):
        self.leafs = 0
        self.season = "Spring"
        self.seasons = ["Spring", "Summer", "Fall", "Winter"]
        self.season_index = 0  # This should already exist
        self.season_timer = 0  # This should already exist
        self.season_duration = 20 * 60  # 20 minutes in seconds
        self.base_production_rate = 10  # base leaves per second
        self.plants = 0  # number of plants purchased
        self.production_multiplier = 1.0
        self.plant_image = None

        # Try to load plant image
        plant_image_path = os.path.join(ASSETS_DIR, "plant.png")
        if os.path.exists(plant_image_path):
            try:
                self.plant_image = pygame.image.load(plant_image_path).convert_alpha()
                # Scale for planting area - smaller for 10x10 grid
                scale = 20 / max(self.plant_image.get_width(), self.plant_image.get_height())
                new_width = int(self.plant_image.get_width() * scale)
                new_height = int(self.plant_image.get_height() * scale)
                self.plant_image = pygame.transform.scale(self.plant_image, (new_width, new_height))
            except:
                self.plant_image = None

    def update(self, delta_time):
        # Update season timer
        self.season_timer += delta_time
        if self.season_timer >= self.season_duration:
            self.season_timer = 0
            self.season_index = (self.season_index + 1) % len(self.seasons)
            self.season = self.seasons[self.season_index]

            # Apply season multipliers
            if self.season == "Spring":
                self.production_multiplier = 1.2
            elif self.season == "Summer":
                self.production_multiplier = 1.5
            elif self.season == "Fall":
                self.production_multiplier = 1.0
            else:  # Winter
                self.production_multiplier = 0.7

        # Calculate leaf production (base + 1 per plant)
        total_production_rate = self.base_production_rate + self.plants
        effective_rate = total_production_rate * self.production_multiplier
        self.leafs += effective_rate * delta_time

    def add_plant(self):
        self.plants += 1
        print(f" Plant added! Total plants: {self.plants}")

    def get_stats(self):
        total_production = self.base_production_rate + self.plants
        effective_rate = total_production * self.production_multiplier
        return {
            "leafs": int(self.leafs),
            "season": self.season,
            "production_rate": f"{effective_rate:.1f}/sec",
            "plants": self.plants,
            "base_rate": self.base_production_rate,
            "season_progress": self.season_timer / self.season_duration,
            "season_time_left": self.season_duration - self.season_timer
        }

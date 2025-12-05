import pygame
import os
import math
from utils import ASSETS_DIR, BUTTON_HOVER_COLOR, get_font, sound_manager, settings, load_image

# Data class to hold plant info
class PlantItem:
    def __init__(self, name, base_cost, production, color, filename=None):
        self.name = name
        self.base_cost = base_cost
        self.cost = base_cost
        self.production = production
        self.color = color
        # Optional filename for an icon in assets/; may be None
        self.filename = filename
        self.icon = None
        self.count = 0
        self.buy_rect = None

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

        # Define available plants 
        self.plant_items = [
            # TIER 1
            PlantItem("Maple Sapling", 10, 2, (255, 100, 100)), 
            # TIER 2
            PlantItem("Pine Tree", 80, 10, (50, 120, 50)),      
            # TIER 3
            PlantItem("Giant Sequoia", 450, 50, (150, 100, 50))
        ]

        # Load individual images for each plant in the shop UI
        self._load_shop_icons()

        # Store button rects for click handling
        self.shop_rect = None
        self.close_rect = None
        self.buy_rect = None
        self.close_button_hovered = False
        self.buy_button_hovered = False
        # Track which buy button is hovered (-1 means none)
        self.hovered_buy_index = -1
        # Placeholder tree image for shop icons
        self.tree_image = load_image("missing.png", size=(60, 60))

        # Loads a 60x60 icon for each plant item defined in plant_items
    def _load_shop_icons(self):
        for item in self.plant_items:
            # Only attempt to load if a filename was provided
            if item.filename:
                try:
                    item.icon = load_image(item.filename, size=(60, 60))
                except Exception:
                    item.icon = None
            else:
                item.icon = None

    def toggle(self, is_upgrades=False):
        self.is_open = not self.is_open
        self.is_upgrades_shop = is_upgrades

    def draw(self, screen, center, leafs):
        if self.is_open:
            # Create shop background
            shop_rect = pygame.Rect(0, 0, self.width, self.height)
            shop_rect.center = center
            self.shop_rect = shop_rect

            # Draw Modal Background
            pygame.draw.rect(screen, (40, 40, 50), shop_rect, border_radius=15)
            pygame.draw.rect(screen, (144, 238, 144), shop_rect, 4, border_radius=15)

            # Draw shop title
            title_font = get_font(48)
            title_text = "UPGRADES" if self.is_upgrades_shop else "PLANT NURSERY"
            title = title_font.render(title_text, True, (255, 255, 255))
            title_rect = title.get_rect(center=(shop_rect.centerx, shop_rect.top + 40))
            screen.blit(title, title_rect)

            # Draw Available Leafs Counter
            leaf_font = get_font(28)
            leaf_text = leaf_font.render(f"Wallet: {int(leafs)} Leafs", True, (144, 238, 144))
            leaf_rect = leaf_text.get_rect(center=(shop_rect.centerx, shop_rect.top + 85))
            screen.blit(leaf_text, leaf_rect)

            button_font = get_font(20)
            desc_font = get_font(18)

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
                    improved_soil_bought_text = button_font.render(f"SOLD OUT", True, (250, 0, 30))
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
                    # Bought: Centered horizontally, slightly up from the bottom
                    bought_rect = improved_soil_bought_text.get_rect(
                        midbottom=(upgrade_description_area.centerx, upgrade_description_area.bottom - 15)
                    )
                    # 4. Draw text
                    screen.blit(improved_soil_name, name_rect)
                    screen.blit(improved_soil_desc, desc_rect)
                    if self.owns_improved_soil:
                        screen.blit(improved_soil_bought_text, bought_rect)
                    else:
                        screen.blit(improved_soil_cost_text, cost_rect)
                    #Check for mouse clicks
                    if pygame.mouse.get_pressed()[0] and self.owns_improved_soil == False:
                        if leafs >= self.improved_soil_cost:
                            self.handle_upgrade_purchase("Improved Soil", leafs)

            else:
                # --- MULTI-ITEM PLANT SHOP UI ---
                item_height = 90
                start_y = shop_rect.top + 120
                
                for index, item in enumerate(self.plant_items):
                    # Item Row Background
                    item_rect = pygame.Rect(shop_rect.left + 30, start_y + (index * (item_height + 15)), shop_rect.width - 60, item_height)
                    pygame.draw.rect(screen, (50, 55, 65), item_rect, border_radius=10)
                    pygame.draw.rect(screen, (70, 75, 85), item_rect, 2, border_radius=10)

                    # 1. Icon (Use the loaded image, or fallback to circle)
                    icon_center = (item_rect.left + 50, item_rect.centery)
                    
                    if item.icon:
                        # Draw the specific loaded image icon
                        icon_rect = item.icon.get_rect(center=icon_center)
                        screen.blit(item.icon, icon_rect)
                    else:
                        # Fallback: Draw the simple colored circle
                        pygame.draw.circle(screen, item.color, icon_center, 30)
                        pygame.draw.circle(screen, (255,255,255), icon_center, 30, 2)

                    # 2. Name & Production Rate
                    name_text = get_font(24).render(f"{item.name}", True, (255, 255, 255))
                    screen.blit(name_text, (item_rect.left + 100, item_rect.top + 15))
                    
                    stats_text = desc_font.render(f"+{item.production} leafs/sec | Owned: {item.count}", True, (180, 180, 180))
                    screen.blit(stats_text, (item_rect.left + 100, item_rect.bottom - 35))

                    # 3. Buy Button
                    btn_width, btn_height = 140, 50
                    item.buy_rect = pygame.Rect(item_rect.right - 160, item_rect.centery - btn_height//2, btn_width, btn_height)
                    
                    can_afford = leafs >= item.cost
                    
                    # Determine Color
                    if index == self.hovered_buy_index:
                        btn_color = BUTTON_HOVER_COLOR
                    elif can_afford:
                        btn_color = (70, 130, 70)
                    else:
                        btn_color = (80, 80, 80) # Greyed out

                    pygame.draw.rect(screen, btn_color, item.buy_rect, border_radius=8)
                    pygame.draw.rect(screen, (200,200,200), item.buy_rect, 2, border_radius=8)

                    # Cost Text inside button
                    cost_txt = button_font.render(f"{int(item.cost)}", True, (255, 255, 255) if can_afford else (150,150,150))
                    screen.blit(cost_txt, cost_txt.get_rect(center=item.buy_rect.center))

            # Close button
            close_rect = pygame.Rect(shop_rect.centerx - 60, shop_rect.bottom - 60, 120, 40)
            self.close_rect = close_rect

            close_button_color = (200, 80, 80) if self.close_button_hovered else (180, 70, 70)
            pygame.draw.rect(screen, close_button_color, close_rect, border_radius=8)
            pygame.draw.rect(screen, (255, 255, 255), close_rect, 2, border_radius=8)

            close_text = button_font.render("CLOSE", True, (255, 255, 255))
            screen.blit(close_text, close_text.get_rect(center=close_rect.center))

    def handle_upgrade_purchase(self, upgrade_bought, leafs):
        sound_manager.play("purchase", settings.sfx_volume * 0.7)
        if upgrade_bought == "Improved Soil":
            leafs -= self.improved_soil_cost
            #Change to now owned
            self.owns_improved_soil = True
            print(f"Purchased an upgrade: Improved Soil")


    def check_hover(self, pos):
        # Close button hover
        self.close_button_hovered = self.close_rect and self.close_rect.collidepoint(pos)

        # Buy buttons hover
        self.hovered_buy_index = -1
        if not self.is_upgrades_shop:
            for index, item in enumerate(self.plant_items):
                if item.buy_rect and item.buy_rect.collidepoint(pos):
                    self.hovered_buy_index = index
                    
        # Sound logic could go here if we tracked previous state
        if self.close_button_hovered or self.hovered_buy_index != -1:
             pass # Logic handled in main loop usually, or add "was_hovered" tracking here

    def handle_click(self, pos, leafs):
        # Returns: (new_leaf_count, should_close_shop, production_increase_amount) """
        if not self.is_open or not self.shop_rect:
            return leafs, False, 0

        # Check close Button
        if self.close_rect and self.close_rect.collidepoint(pos):
            sound_manager.play("back", settings.sfx_volume)
            return leafs, True, 0

        # Buy Buttons
        if not self.is_upgrades_shop:
            for item in self.plant_items:
                if item.buy_rect and item.buy_rect.collidepoint(pos):
                    leafs >= item.cost
                    sound_manager.play("select", settings.sfx_volume)
                    leafs -= item.cost
                    # Increase count, scale cost, return production boost
                    item.count += 1
                    item.cost = int(item.cost * 1.1) # 10% cost increase per purchase
                    return leafs, False, item.production
                    
        return leafs, False, 0


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
        self._load_assets()

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

    def _load_assets(self):
        # Load image with fallback from utils
        self.plant_image = load_image("plant.png")
        if self.plant_image:
             # Scale if needed for grid
             if self.plant_image.get_width() > 32 or self.plant_image.get_height() > 32:
                 self.plant_image = pygame.transform.scale(self.plant_image, (32, 32))

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
        self.global_upgrade_multiplier = 1
        # Calculate leaf production (base + 1 per plant)
        total_production_rate = self.base_production_rate + self.plants
        effective_rate = total_production_rate * self.production_multiplier * self.global_upgrade_multiplier
        self.leafs += effective_rate * delta_time

    def add_plant(self, production_increase=1):
        """ Called when shop buys a plant. production_increase is now passed from the ShopItem. """
        self.plants_total_count += 1
        self.plants_production_rate += production_increase
        # Original print statement was here: print(f"Plant added! Rate increased by {production_increase}")

    def get_stats(self):
        total_production = self.base_production_rate + self.plants_production_rate
        effective_rate = total_production * self.production_multiplier
        
        return {
            "leafs": int(self.leafs),
            "season": self.season,
            "production_rate": f"{effective_rate:.1f}/sec",
            "plants": self.plants_total_count, # Used for grid drawing in gameloop
            "base_rate": self.base_production_rate,
            "season_progress": self.season_timer / self.season_duration,
            "season_time_left": self.season_duration - self.season_timer
        }

import pygame
import os
from .settings import *


class GameManager:
    def __init__(self, save_data):
        self.leafs = save_data.get("leafs", 0)
        # We normalize to IDs.
        self.plant_grid = save_data.get("plant_grid", [])
        self.season = save_data.get("season", "Spring")
        self.upgrade_rate_bonus = save_data.get("upgrade_rate_bonus", 0)
        self.production_multiplier = save_data.get("production_multiplier", 1.0)

        # FIX 1: Shop State Persistence (Data held here to be passed to Shop later)
        self.saved_shop_state = save_data.get("shop_state", None)

        # Backwards compat: If grid is empty but we have plants count
        loaded_plant_count = save_data.get("plants", 0)
        if loaded_plant_count > 0 and not self.plant_grid:
            for _ in range(loaded_plant_count):
                self.plant_grid.insert(0, "buy_plant")

        self.seasons = ["Spring", "Summer", "Fall", "Winter"]
        self.season_timer = 0
        self.base_prod = 1
        self.season_change_timer = 0

        # Assets
        self.plant_images = {}
        self.load_plant_image("buy_plant", "plant.png")
        self.load_plant_image("rate_10min", "fertilizer.png")
        self.load_plant_image("rate_50min", "sprinkler.png")

    @property
    def plants(self):
        return len(self.plant_grid)

    def load_plant_image(self, item_id, file_name):
        path = os.path.join(ASSETS_DIR, file_name)
        if os.path.exists(path):
            img = pygame.image.load(path).convert_alpha()
            self.plant_images[item_id] = pygame.transform.scale(img, (40, 40))
        else:
            self.plant_images[item_id] = None

    def get_plant_screen_pos(self, index):
        """Calculates where a grid index is on screen"""
        start_x, start_y = 60, 90
        # 10 columns
        r, c = divmod(index, 10)
        x = start_x + c * ((WIDTH - 120) // 10) + 10
        y = start_y + r * ((HEIGHT - 200) // 10) + 10
        return x, y

    def update(self, dt):
        # Season Logic
        self.season_timer += dt
        if self.season_timer >= SEASON_DURATION:
            self.season_timer = 0
            curr_idx = self.seasons.index(self.season)
            self.season = self.seasons[(curr_idx + 1) % 4]
            self.season_change_timer = 3.0
        if self.season_change_timer > 0:
            self.season_change_timer -= dt

        # Rate Calculation
        multiplier = {"Spring": 1.2, "Summer": 1.5, "Fall": 1.0, "Winter": 0.7}.get(self.season, 1.0)

        # Base(1) + Plant Count + Bonus Items
        base_rate = (self.base_prod + self.plants + self.upgrade_rate_bonus)

        total_rate = base_rate * multiplier * self.production_multiplier
        self.leafs += total_rate * dt

    def get_stats(self):
        multiplier = {"Spring": 1.2, "Summer": 1.5, "Fall": 1.0, "Winter": 0.7}.get(self.season, 1.0)
        base_rate = (self.base_prod + self.plants + self.upgrade_rate_bonus)
        rate = base_rate * multiplier * self.production_multiplier

        return {
            "leafs": int(self.leafs),
            "plants": self.plants,
            "season": self.season,
            "rate": rate,
            "season_visual_alpha": int((self.season_change_timer / 3.0) * 255) if self.season_change_timer > 0 else 0
        }

    def get_save_data(self, shop_instance):
        return {
            "leafs": self.leafs,
            "plants": self.plants,
            "plant_grid": self.plant_grid,
            "season": self.season,
            "upgrade_rate_bonus": self.upgrade_rate_bonus,
            "production_multiplier": self.production_multiplier,
            "shop_state": shop_instance.get_state()  # FIX 1: Saving Shop Prices/Upgrades
        }


class Shop:
    def __init__(self):
        self.is_open = False
        self.is_upgrades = False
        self.rect = None
        self.close_rect = None
        self.close_hovered = False

        self.shop_items = [
            {"id": "buy_plant", "name": "Basic Plant", "cost": 10, "desc": "+1 Leaf/sec", "rate_boost": 0,
             "cost_mult": 1.15},
            {"id": "rate_10min", "name": "Fertilizer", "cost": 50, "desc": "+10 Leafs/min", "rate_boost": 10 / 60,
             "cost_mult": 1.25},
            {"id": "rate_50min", "name": "Sprinkler", "cost": 250, "desc": "+50 Leafs/min", "rate_boost": 50 / 60,
             "cost_mult": 1.40}
        ]

        self.upgrade_items = [
            {"id": "multiplier_x2", "name": "Super-Fertilizer", "cost": 500, "desc": "Doubles Leaf Output (x2)",
             "multiplier_value": 2.0, "cost_mult": 10.0, "purchased": False}
        ]

    # FIX 1: Methods to extract and restore shop data
    def get_state(self):
        """Extracts dynamic data for saving"""
        return {
            "shop_items": [{"id": i["id"], "cost": i["cost"]} for i in self.shop_items],
            "upgrade_items": [{"id": i["id"], "purchased": i.get("purchased", False)} for i in self.upgrade_items]
        }

    def load_state(self, data):
        """Restores costs and purchased status"""
        if not data: return

        # Restore Costs
        saved_costs = {item["id"]: item["cost"] for item in data.get("shop_items", [])}
        for item in self.shop_items:
            if item["id"] in saved_costs:
                item["cost"] = saved_costs[item["id"]]

        # Restore Upgrades
        saved_upgrades = {item["id"]: item["purchased"] for item in data.get("upgrade_items", [])}
        for item in self.upgrade_items:
            if item["id"] in saved_upgrades:
                item["purchased"] = saved_upgrades[item["id"]]

    def toggle(self, is_upgrades=False):
        self.is_open = True
        self.is_upgrades = is_upgrades

    def recalculate_cost(self, num_plants):
        # Fallback legacy logic if needed, but load_state is preferred
        pass

    def draw(self, screen, width, height, leafs):
        if not self.is_open: return

        # Dim background
        overlay = pygame.Surface((width, height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))

        self.rect = pygame.Rect(0, 0, 700, 500)
        self.rect.center = (width // 2, height // 2)
        pygame.draw.rect(screen, (40, 40, 50), self.rect, border_radius=15)
        pygame.draw.rect(screen, (144, 238, 144), self.rect, 4, border_radius=15)

        font = pygame.font.Font(None, 48)
        title_text = "UPGRADES" if self.is_upgrades else "PLANT SHOP"
        title = font.render(title_text, True, (255, 255, 255))
        screen.blit(title, title.get_rect(center=(self.rect.centerx, self.rect.top + 50)))

        current_list = self.upgrade_items if self.is_upgrades else self.shop_items
        item_start_y = self.rect.top + 100
        btn_font = pygame.font.Font(None, 32)
        desc_font = pygame.font.Font(None, 24)

        for i, item in enumerate(current_list):
            item_h = 80
            item_y = item_start_y + (i * (item_h + 10))
            item_rect = pygame.Rect(self.rect.left + 50, item_y, self.rect.width - 100, item_h)
            item["rect"] = item_rect

            is_bought = item.get("purchased", False) and item.get("multiplier_value")
            can_afford = leafs >= item["cost"]

            if is_bought:
                base_col = (50, 50, 50)
            else:
                base_col = (70, 130, 70) if can_afford else (80, 80, 80)
                if item.get("hovered"): base_col = (100, 160, 100) if can_afford else (100, 100, 100)

            pygame.draw.rect(screen, base_col, item_rect, border_radius=8)
            pygame.draw.rect(screen, (200, 200, 200), item_rect, 2, border_radius=8)

            if is_bought:
                name_txt = btn_font.render(f"{item['name']} - OWNED", True, (150, 150, 150))
            else:
                name_txt = btn_font.render(f"{item['name']} - {item['cost']} Leafs", True, (255, 255, 255))

            screen.blit(name_txt, (item_rect.x + 20, item_rect.y + 15))
            desc_txt = desc_font.render(item['desc'], True, (200, 200, 200))
            screen.blit(desc_txt, (item_rect.x + 20, item_rect.y + 45))

        self.close_rect = pygame.Rect(0, 0, 100, 40)
        self.close_rect.topleft = (self.rect.left + 20, self.rect.top + 20)
        close_col = (200, 80, 80) if self.close_hovered else (180, 70, 70)
        pygame.draw.rect(screen, close_col, self.close_rect, border_radius=8)

        txt_close = btn_font.render("CLOSE", True, (255, 255, 255))
        screen.blit(txt_close, txt_close.get_rect(center=self.close_rect.center))

    def check_hover(self, pos, sound_mgr):
        if not self.is_open: return
        if self.close_rect and self.close_rect.collidepoint(pos):
            if not self.close_hovered: sound_mgr.play("hover")
            self.close_hovered = True
        else:
            self.close_hovered = False

        current_list = self.upgrade_items if self.is_upgrades else self.shop_items
        for item in current_list:
            if "rect" in item:
                was_hover = item.get("hovered", False)
                item["hovered"] = item["rect"].collidepoint(pos)
                if item["hovered"] and not was_hover:
                    sound_mgr.play("hover")

    def handle_click(self, pos, current_leafs, sound_mgr):
        if not self.is_open: return current_leafs, False, 0, None, 1.0

        if self.close_rect and self.close_rect.collidepoint(pos):
            sound_mgr.play("back")
            self.is_open = False
            return current_leafs, False, 0, None, 1.0

        current_list = self.upgrade_items if self.is_upgrades else self.shop_items
        for item in current_list:
            if "rect" in item and item["rect"].collidepoint(pos):
                if item.get("purchased", False):
                    sound_mgr.play("error")
                    return current_leafs, False, 0, None, 1.0

                if current_leafs >= item["cost"]:
                    sound_mgr.play("select")
                    new_leafs = current_leafs - item["cost"]

                    # Increase cost logic
                    item["cost"] = int(item["cost"] * item.get("cost_mult", 1.1))

                    item_id = item["id"]
                    mult_val = item.get("multiplier_value", 1.0)
                    rate_boost = item.get("rate_boost", 0)

                    if mult_val > 1.0:
                        item["purchased"] = True
                        return new_leafs, False, 0, item_id, mult_val
                    else:
                        # Return purchase info
                        return new_leafs, True, rate_boost, item_id, 1.0

        return current_leafs, False, 0, None, 1.0
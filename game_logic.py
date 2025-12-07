import pygame
import os
from settings import *


class GameManager:
    def __init__(self, save_data):
        self.leafs = save_data.get("leafs", 0)
        self.plant_grid = save_data.get("plant_grid", [])
        self.season = save_data.get("season", "Spring")
        self.upgrade_rate_bonus = save_data.get("upgrade_rate_bonus", 0)
        self.production_multiplier = save_data.get("production_multiplier", 1.0)

        # Legacy support for old saves
        loaded_plant_count = save_data.get("plants", 0)
        if loaded_plant_count > 0 and not self.plant_grid:
            for _ in range(loaded_plant_count):
                self.plant_grid.insert(0, "buy_plant")

        self.seasons = ["Spring", "Summer", "Fall", "Winter"]
        self.season_timer = 0
        self.season_change_timer = 0
        self.just_changed_season = False  # Flag for Main to detect change

        # --- ASSET LOADING ---
        self.plant_images = {}

        # We load textures for ALL known IDs.
        # If the file doesn't exist, universal_load handles it.
        known_plants = [
            "maple_sapling", "oak_tree", "willow_tree",
            "ginkgo_tree", "ancient_banyan", "crystal_tree", "spirit_blossom"
        ]

        for pid in known_plants:
            # Assumes file name matches ID + .png, e.g., "oak_tree.png"
            # Special case for "buy_plant" which was historically "plant.png"
            fname = "plant.png" if pid == "buy_plant" else f"{pid}.png"
            self.plant_images[pid] = self.universal_load(fname)

    def universal_load(self, file_name):
        """Loads image, falls back to missing.png, falls back to magenta square."""
        path = os.path.join(ASSETS_DIR, file_name)

        # 1. Try Loading Real Image
        if os.path.exists(path):
            try:
                img = pygame.image.load(path).convert_alpha()
                return pygame.transform.scale(img, (40, 40))
            except:
                pass

        # 2. Try Loading missing.png
        missing_path = os.path.join(ASSETS_DIR, "missing.png")
        if os.path.exists(missing_path):
            try:
                img = pygame.image.load(missing_path).convert_alpha()
                return pygame.transform.scale(img, (40, 40))
            except:
                pass

        # 3. Create Magenta Fallback Surface
        surf = pygame.Surface((40, 40))
        surf.fill((255, 0, 255))
        return surf

    @property
    def plants(self):
        return len(self.plant_grid)

    def get_plant_screen_pos(self, index):
        start_x, start_y = 60, 90
        r, c = divmod(index, 10)
        x = start_x + c * ((WIDTH - 120) // 10) + 10
        y = start_y + r * ((HEIGHT - 200) // 10) + 10
        return x, y

    def update(self, dt):
        self.just_changed_season = False

        # Season Logic
        self.season_timer += dt
        if self.season_timer >= SEASON_DURATION:
            self.season_timer = 0
            curr_idx = self.seasons.index(self.season)
            self.season = self.seasons[(curr_idx + 1) % 4]
            self.season_change_timer = 3.0
            self.just_changed_season = True  # Trigger music/bg change in Main

        if self.season_change_timer > 0:
            self.season_change_timer -= dt

        # Rate Calculation
        multiplier = {"Spring": 1.3, "Summer": 1.1, "Fall": 1.0, "Winter": 0.7}.get(self.season, 1.0)
        base_rate = self.upgrade_rate_bonus
        total_rate = base_rate * multiplier * self.production_multiplier
        self.leafs += total_rate * dt

    def get_stats(self):
        multiplier = {"Spring": 1.3, "Summer": 1.1, "Fall": 1.0, "Winter": 0.7}.get(self.season, 1.0)
        base_rate = self.upgrade_rate_bonus
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
            "shop_state": shop_instance.get_state()
        }


class Shop:
    def __init__(self):
        self.is_open = False
        self.is_upgrades = False
        self.rect = None
        self.close_rect = None
        self.close_hovered = False

        self.shop_items = [
            {"id": "maple_sapling", "name": "Maple Sapling", "cost": 10, "desc": "+0.5 Leaf/sec", "rate_boost": 0.5,
             "cost_mult": 1.1, "count": 0},
            {"id": "oak_tree", "name": "Oak Tree", "cost": 100, "desc": "+5 Leaf/sec", "rate_boost": 5.0,
             "cost_mult": 1.2, "count": 0},
            {"id": "willow_tree", "name": "Weeping Willow", "cost": 1000, "desc": "+25 Leaf/sec", "rate_boost": 25.0,
             "cost_mult": 1.3, "count": 0},
            {"id": "ginkgo_tree", "name": "Ginkgo Tree", "cost": 7500, "desc": "+100 Leaf/sec", "rate_boost": 100.0,
             "cost_mult": 1.4, "count": 0},
            {"id": "ancient_banyan", "name": "Ancient Banyan", "cost": 50000, "desc": "+500 Leaf/sec",
             "rate_boost": 500.0, "cost_mult": 1.5, "count": 0},
            {"id": "crystal_tree", "name": "Crystal Tree", "cost": 500000, "desc": "+5000 Leaf/sec",
             "rate_boost": 5000.0, "cost_mult": 1.5, "count": 0},
            {"id": "spirit_blossom", "name": "Spirit Blossom", "cost": 1000000, "desc": "+10000 Leaf/sec",
             "rate_boost": 10000.0, "cost_mult": 1.5, "count": 0},

            # --- INFLATION RESET ITEM ---
            {"id": "inflation_reset", "name": "Market Crash", "cost": 100000, "desc": "Reset shop costs to default.",
             "rate_boost": 0.0, "cost_mult": 20.0, "count": 0}
        ]

        for item in self.shop_items:
            item["base_cost"] = item["cost"]

        self.upgrade_items = [
            {"id": "rate_10%", "name": "Fertilizer", "cost": 100, "desc": "Output +10%", "multiplier_value": 1.1,
             "purchased": False},
            {"id": "rate_20%", "name": "Sprinkler", "cost": 500, "desc": "Output +20%", "multiplier_value": 1.2,
             "purchased": False},
            {"id": "rate_30%", "name": "Rich Compost", "cost": 2500, "desc": "Output +30%", "multiplier_value": 1.3,
             "purchased": False},
            {"id": "rate_50%", "name": "Magic Pollen", "cost": 15000, "desc": "Output +50%", "multiplier_value": 1.5,
             "purchased": False},
            {"id": "rate_100%", "name": "Holy Water", "cost": 250000, "desc": "Output x2", "multiplier_value": 2.0,
             "purchased": False},
            {"id": "rate_300%", "name": "Terra Mater", "cost": 5000000, "desc": "Output x4", "multiplier_value": 4.0,
             "purchased": False},
            {"id": "rate_700%", "name": "Gaia's Bless", "cost": 1000000000, "desc": "Output x8",
             "multiplier_value": 8.0, "purchased": False},
            {"id": "rate_1500%", "name": "Mother of all Nature", "cost": 1000000000000, "desc": "Output x16",
             "multiplier_value": 16.0, "purchased": False}
        ]

    def get_state(self):
        return {
            "shop_items": [{"id": i["id"], "cost": i["cost"]} for i in self.shop_items],
            "upgrade_items": [{"id": i["id"], "purchased": i.get("purchased", False)} for i in self.upgrade_items]
        }

    def load_state(self, data):
        if not data: return
        saved_costs = {item["id"]: item["cost"] for item in data.get("shop_items", [])}
        for item in self.shop_items:
            if item["id"] in saved_costs:
                item["cost"] = saved_costs[item["id"]]

        saved_upgrades = {item["id"]: item["purchased"] for item in data.get("upgrade_items", [])}
        for item in self.upgrade_items:
            if item["id"] in saved_upgrades:
                item["purchased"] = saved_upgrades[item["id"]]

    def toggle(self, is_upgrades=False):
        self.is_open = True
        self.is_upgrades = is_upgrades

    def recalculate_cost(self, num_plants):
        pass

    def get_max_scroll(self, width, height):
        modal_h = 500
        item_h = 80
        spacing = 10
        current_list = self.upgrade_items if self.is_upgrades else self.shop_items
        content_h = len(current_list) * (item_h + spacing)
        visible_h = modal_h - 150
        max_scroll = max(0, content_h - visible_h)
        return max_scroll

    def get_scrollbar_info(self, width, height, scroll_offset):
        modal_w, modal_h = 700, 500
        rect = pygame.Rect(0, 0, modal_w, modal_h)
        rect.center = (width // 2, height // 2)

        item_h = 80
        spacing = 10
        current_list = self.upgrade_items if self.is_upgrades else self.shop_items
        content_h = len(current_list) * (item_h + spacing)
        visible_h = modal_h - 150
        max_scroll = max(0, content_h - visible_h)
        track_rect = pygame.Rect(rect.right - 30, rect.top + 100, 12, visible_h)

        if content_h <= visible_h:
            return track_rect, None, max_scroll

        thumb_h = max(20, int(visible_h * (visible_h / content_h)))
        track_space = visible_h - thumb_h
        thumb_top = track_rect.top if max_scroll == 0 else track_rect.top + int(
            (scroll_offset / max_scroll) * track_space)
        thumb_rect = pygame.Rect(track_rect.x, thumb_top, track_rect.width, thumb_h)
        return track_rect, thumb_rect, max_scroll

    def draw(self, screen, width, height, leafs, scroll_offset=0):
        if not self.is_open: return

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

        modal_h = self.rect.height
        visible_h = modal_h - 150
        clip_rect = pygame.Rect(self.rect.left + 50, self.rect.top + 100, self.rect.width - 100, visible_h)
        prev_clip = screen.get_clip()
        screen.set_clip(clip_rect)

        for i, item in enumerate(current_list):
            item_h = 80
            item_y = item_start_y + (i * (item_h + 10))
            item_rect = pygame.Rect(self.rect.left + 50, item_y, self.rect.width - 100, item_h)
            offset_rect = item_rect.move(0, -scroll_offset)
            item["rect"] = offset_rect

            is_bought = item.get("purchased", False) and item.get("multiplier_value")
            can_afford = leafs >= item["cost"]

            if is_bought:
                base_col = (50, 50, 50)
            else:
                base_col = (70, 130, 70) if can_afford else (80, 80, 80)
                if item.get("hovered"): base_col = (100, 160, 100) if can_afford else (100, 100, 100)

            # Inflation Reset Color
            if item["id"] == "inflation_reset":
                base_col = (150, 80, 80) if can_afford else (100, 60, 60)
                if item.get("hovered") and can_afford: base_col = (180, 90, 90)

            pygame.draw.rect(screen, base_col, offset_rect, border_radius=8)
            pygame.draw.rect(screen, (200, 200, 200), offset_rect, 2, border_radius=8)

            if is_bought:
                name_txt = btn_font.render(f"{item['name']} - OWNED", True, (150, 150, 150))
            else:
                name_txt = btn_font.render(f"{item['name']} - {item['cost']} Leafs", True, (255, 255, 255))

            screen.blit(name_txt, (offset_rect.x + 20, offset_rect.y + 15))
            desc_txt = desc_font.render(item['desc'], True, (200, 200, 200))
            screen.blit(desc_txt, (offset_rect.x + 20, offset_rect.y + 45))

        screen.set_clip(prev_clip)

        self.close_rect = pygame.Rect(0, 0, 100, 40)
        self.close_rect.topleft = (self.rect.left + 20, self.rect.top + 20)
        close_col = (200, 80, 80) if self.close_hovered else (180, 70, 70)
        pygame.draw.rect(screen, close_col, self.close_rect, border_radius=8)

        txt_close = btn_font.render("CLOSE", True, (255, 255, 255))
        screen.blit(txt_close, txt_close.get_rect(center=self.close_rect.center))

        track_rect, thumb_rect, max_scroll = self.get_scrollbar_info(width, height, scroll_offset)
        if thumb_rect:
            pygame.draw.rect(screen, (80, 80, 90), track_rect, border_radius=6)
            pygame.draw.rect(screen, (160, 160, 160), thumb_rect, border_radius=6)
            pygame.draw.rect(screen, (220, 220, 220), thumb_rect, 2, border_radius=6)

    def check_hover(self, pos, sound_mgr):
        if not self.is_open: return
        if self.close_rect and self.close_rect.collidepoint(pos):
            if not self.close_hovered: sound_mgr.play("hover")
            self.close_hovered = True
        else:
            self.close_hovered = False

        if self.rect:
            modal_h = self.rect.height
            visible_h = modal_h - 150
            clip_rect = pygame.Rect(self.rect.left + 50, self.rect.top + 100, self.rect.width - 100, visible_h)
        else:
            return

        current_list = self.upgrade_items if self.is_upgrades else self.shop_items
        for item in current_list:
            if "rect" in item:
                # Check Visible Area
                is_visible = clip_rect.collidepoint(pos)
                was_hover = item.get("hovered", False)
                item["hovered"] = item["rect"].collidepoint(pos) and is_visible

                if item["hovered"] and not was_hover:
                    sound_mgr.play("hover")

    def handle_click(self, pos, current_leafs, sound_mgr):
        if not self.is_open: return current_leafs, False, 0, None, 1.0

        if self.close_rect and self.close_rect.collidepoint(pos):
            sound_mgr.play("back")
            self.is_open = False
            return current_leafs, False, 0, None, 1.0

        modal_h = self.rect.height
        visible_h = modal_h - 150
        clip_rect = pygame.Rect(self.rect.left + 50, self.rect.top + 100, self.rect.width - 100, visible_h)

        current_list = self.upgrade_items if self.is_upgrades else self.shop_items
        for item in current_list:
            if "rect" in item and item["rect"].collidepoint(pos) and clip_rect.collidepoint(pos):
                if item.get("purchased", False):
                    sound_mgr.play("error")
                    return current_leafs, False, 0, None, 1.0

                if current_leafs >= item["cost"]:
                    sound_mgr.play("select")
                    new_leafs = current_leafs - item["cost"]

                    if item["id"] == "inflation_reset":
                        item["cost"] = int(item["cost"] * item.get("cost_mult", 1.5))
                        for s_item in self.shop_items:
                            if s_item["id"] != "inflation_reset":
                                s_item["cost"] = s_item["base_cost"]
                        return new_leafs, False, 0, None, 1.0

                    item["cost"] = int(item["cost"] * item.get("cost_mult", 1.1))
                    item_id = item["id"]
                    mult_val = item.get("multiplier_value", 1.0)
                    rate_boost = item.get("rate_boost", 0)

                    if mult_val > 1.0:
                        item["purchased"] = True
                        return new_leafs, False, 0, item_id, mult_val
                    else:
                        return new_leafs, True, rate_boost, item_id, 1.0

        return current_leafs, False, 0, None, 1.0
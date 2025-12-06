import os
import pygame

# Screen
WIDTH, HEIGHT = 900, 600
FPS = 60

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
SAVE_FILE = os.path.join(BASE_DIR, "savegame.json")
SETTINGS_FILE = os.path.join(BASE_DIR, "settings.json")

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
PLANTING_AREA_COLOR = (50, 80, 50)
PLANTING_GRID_COLOR = (70, 100, 70)
GAME_UI_BG = (40, 50, 40, 200)

# Game Constants
SEASON_DURATION = 20 * 60  # seconds
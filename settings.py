import os
import sys

# Screen
WIDTH, HEIGHT = 900, 600
FPS = 60

# --- CRITICAL PATH FIX FOR EXE ---
if getattr(sys, 'frozen', False):
    # If running as a compiled exe, look in the temporary folder
    BASE_DIR = sys._MEIPASS
else:
    # If running as a script, look in the current folder
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

ASSETS_DIR = os.path.join(BASE_DIR, "assets")
SAVE_FILE = os.path.join(os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else BASE_DIR, "savegame.json")
SETTINGS_FILE = os.path.join(os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else BASE_DIR, "settings.json")

# Colors
BG_COLOR = (30, 40, 30)
TEXT_COLOR = (255, 255, 255)
BUTTON_COLOR = (70, 130, 70)
BUTTON_HOVER_COLOR = (100, 180, 100)
BUTTON_TEXT_COLOR = (255, 255, 255)

SLIDER_COLOR = (100, 100, 120)
SLIDER_HANDLE_COLOR = (144, 238, 144)
SLIDER_BG_COLOR = (50, 50, 60)

PLANTING_AREA_COLOR = (20, 40, 20)
GAME_UI_BG = (40, 50, 40)

# Game Constants
SEASON_DURATION = 3 * 60  # seconds
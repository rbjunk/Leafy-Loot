import pygame
import os
import json
import time
from settings import ASSETS_DIR, SETTINGS_FILE, SAVE_FILE


class SettingsManager:
    def __init__(self):
        self.music_vol = 0.5
        self.sfx_vol = 0.7
        self.load()

    def load(self):
        try:
            if os.path.exists(SETTINGS_FILE):
                with open(SETTINGS_FILE, "r") as f:
                    data = json.load(f)
                    self.music_vol = data.get("music_volume", 0.5)
                    self.sfx_vol = data.get("sfx_volume", 0.7)
        except Exception:
            print("Could not load settings.")

    def save(self):
        data = {"music_volume": self.music_vol, "sfx_volume": self.sfx_vol}
        with open(SETTINGS_FILE, "w") as f:
            json.dump(data, f, indent=2)


class SoundManager:
    def __init__(self, settings_mgr):
        self.sounds = {}
        self.settings = settings_mgr
        # Initialize default silent sound
        self.sounds["default"] = pygame.mixer.Sound(buffer=bytes([0] * 1000))

    def load_sound(self, name, filename):
        path = os.path.join(ASSETS_DIR, filename)
        if os.path.exists(path):
            try:
                self.sounds[name] = pygame.mixer.Sound(path)
            except Exception:
                print(f"Error loading {filename}")
        else:
            print(f"Sound not found: {filename}")

    def play(self, name):
        vol = self.settings.sfx_vol
        if name in self.sounds:
            self.sounds[name].set_volume(vol)
            self.sounds[name].play()


class MusicManager:
    def __init__(self, settings_mgr):
        self.current_music = None
        self.settings = settings_mgr

    def play_music(self, filename, fade_ms=500):
        path = os.path.join(ASSETS_DIR, filename)
        if not os.path.exists(path): return

        if self.current_music != filename:
            try:
                pygame.mixer.music.load(path)
                pygame.mixer.music.set_volume(self.settings.music_vol)
                pygame.mixer.music.play(-1, fade_ms=fade_ms)
                self.current_music = filename
            except Exception as e:
                print(f"Music Error: {e}")

    def update_volume(self):
        pygame.mixer.music.set_volume(self.settings.music_vol)


class SaveManager:
    def new_game(self):
        return {
            "leafs": 0, "season": "Spring", "plants": 0,
            "plant_cost": 10, "last_updated": time.time()
        }

    def load_game(self):
        if os.path.exists(SAVE_FILE):
            try:
                with open(SAVE_FILE, "r") as f:
                    return json.load(f)
            except:
                pass
        return self.new_game()

    def save_game(self, data):
        data["last_updated"] = time.time()
        with open(SAVE_FILE, "w") as f:
            json.dump(data, f, indent=2)
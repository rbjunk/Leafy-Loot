import pygame
import os
from gameloop import GameLoop
from utils import WIDTH, HEIGHT, ASSETS_DIR


def main():
    # Initialize Pygame FIRST
    pygame.init()
    pygame.mixer.init()

    # Setup window
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Leafy Loot")

    # Load icon - check in assets folder
    icon_path = os.path.join(ASSETS_DIR, "icon.png")
    if os.path.exists(icon_path):
        icon = pygame.image.load(icon_path).convert_alpha()
        pygame.display.set_icon(icon)

    # Import and initialize managers AFTER pygame is initialized
    from utils import sound_manager, music_manager, settings, save_manager

    # Load sound effects (now that mixer is initialized)
    sound_manager.load_sound("start", "Option_Accept.wav")
    sound_manager.load_sound("hover", "Option_Selection.wav")
    sound_manager.load_sound("select", "Item_Accept.wav")
    sound_manager.load_sound("back", "Item_Decline.wav")

    # Load separate music tracks
    music_manager.menu_music = music_manager.load_music("menu", "menu_music.mp3")
    music_manager.game_music = music_manager.load_music("game", "game_music.mp3")
    music_manager.set_volume(settings.music_volume)

    # Create and run the game loop
    game = GameLoop(screen)
    game.run()


if __name__ == "__main__":
    main()

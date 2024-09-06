from direct.gui.DirectGui import DirectSlider, DirectButton, DirectLabel, DirectOptionMenu
from panda3d.core import *

class UIManager:
    def __init__(self, game):
        self.game = game
        self.ui_elements = []  # List to keep track of UI elements
        self.main_menu()

    def main_menu(self):
        """Create the main menu UI."""
        self.clear_ui()

        self.title = DirectLabel(text="My 3D Platformer", scale=0.1, pos=(0, 0, 0.8), text_fg=(1, 1, 1, 1))
        self.ui_elements.append(self.title)

        play_button = DirectButton(text="Play", scale=0.1, pos=(0, 0, 0.5),
                                   command=self.level_selection)  # Add level_selection
        self.ui_elements.append(play_button)

        options_button = DirectButton(text="Options", scale=0.1, pos=(0, 0, 0.3),
                                      command=self.options_menu)
        self.ui_elements.append(options_button)

        leaderboard_button = DirectButton(text="Leaderboard", scale=0.1, pos=(0, 0, 0.1),
                                          command=self.leaderboard)
        self.ui_elements.append(leaderboard_button)

        exit_button = DirectButton(text="Exit", scale=0.1, pos=(0, 0, -0.1),
                                   command=self.exit_game)
        self.ui_elements.append(exit_button)

    def level_selection(self):
        """Create the level selection UI."""
        self.clear_ui()

        # Example level names
        levels = ["Level 1", "Level 2", "Level 3"]

        for index, level in enumerate(levels):
            level_button = DirectButton(text=level, scale=0.1, pos=(0, 0, 0.5 - index * 0.2),
                                        command=lambda l=level: self.start_level(l))
            self.ui_elements.append(level_button)

        # Back button to return to the main menu
        back_button = DirectButton(text="Back", scale=0.1, pos=(0, 0, -0.5),
                                   command=self.main_menu)
        self.ui_elements.append(back_button)

    def start_level(self, level_name):
        """Start the selected level."""
        print(f"Starting {level_name}...")
        self.game.load_level(level_name)

    def options_menu(self):
        """Create the options menu UI."""
        self.clear_ui()

        # Audio Settings
        DirectLabel(text="Audio Settings", scale=0.1, pos=(0, 0, 0.6), text_fg=(1, 1, 1, 1))
        self.music_slider = DirectSlider(range=(0, 100), value=50, scale=0.3, pos=(0, 0, 0.4), command=self.adjust_music_volume)
        self.ui_elements.append(self.music_slider)

        self.sfx_slider = DirectSlider(range=(0, 100), value=50, scale=0.3, pos=(0, 0, 0.2), command=self.adjust_sfx_volume)
        self.ui_elements.append(self.sfx_slider)

        # Video Settings
        DirectLabel(text="Video Settings", scale=0.1, pos=(0, 0, -0.1), text_fg=(1, 1, 1, 1))
        self.resolution_menu = DirectOptionMenu(text="Resolution", scale=0.1, items=["1920x1080", "1280x720", "800x600"], initialitem=0,
                                                command=self.change_resolution, pos=(0, 0, -0.3))
        self.ui_elements.append(self.resolution_menu)

        self.fullscreen_button = DirectButton(text="Toggle Fullscreen", scale=0.1, pos=(0, 0, -0.5),
                                              command=self.toggle_fullscreen)
        self.ui_elements.append(self.fullscreen_button)

        # Back Button
        back_button = DirectButton(text="Back", scale=0.1, pos=(0, 0, -0.7),
                                   command=self.main_menu)
        self.ui_elements.append(back_button)

    def adjust_music_volume(self):
        """Adjust the music volume."""
        volume = self.music_slider['value']
        # Adjust the music volume (assuming there's a background music player)
        print(f"Music Volume: {volume}")

    def adjust_sfx_volume(self):
        """Adjust the sound effects volume."""
        volume = self.sfx_slider['value']
        # Adjust the sound effects volume
        print(f"SFX Volume: {volume}")

    def change_resolution(self, resolution):
        """Change screen resolution."""
        if resolution == "1920x1080":
            self.game.win.requestProperties(WindowProperties(size=(1920, 1080)))
        elif resolution == "1280x720":
            self.game.win.requestProperties(WindowProperties(size=(1280, 720)))
        elif resolution == "800x600":
            self.game.win.requestProperties(WindowProperties(size=(800, 600)))
        print(f"Resolution changed to: {resolution}")

    def toggle_fullscreen(self):
        """Toggle fullscreen mode."""
        props = WindowProperties()
        props.setFullscreen(not self.game.win.isFullscreen())
        self.game.win.requestProperties(props)
        print(f"Fullscreen: {self.game.win.isFullscreen()}")

    def leaderboard(self):
        """Create the leaderboard UI."""
        self.clear_ui()
        DirectLabel(text="Leaderboard (Not Implemented)", scale=0.1, pos=(0, 0, 0.5))
        back_button = DirectButton(text="Back", scale=0.1, pos=(0, 0, -0.5),
                                   command=self.main_menu)
        self.ui_elements.append(back_button)

    def clear_ui(self):
        """Clear the current UI elements."""
        for element in self.ui_elements:
            element.destroy()  # Destroy each UI element
        self.ui_elements.clear()  # Clear the list of UI elements

    def exit_game(self):
        """Exit the game."""
        self.game.userExit()

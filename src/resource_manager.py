"""
Resource manager for game resources like audio files, images, etc.
This class ensures resources are loaded only once and stored in memory.
"""
import os
import pygame
from pygame.locals import SRCALPHA
from singleton import Singleton
from file_manager import FileManager
from config import MENU_BGM_PATH, GAME_BGM_PATH

class ResourceManager(Singleton):
    """
    Singleton manager for game resources like audio files, images, etc.
    This class ensures resources are loaded only once and stored in memory.
    """

    def __init__(self):
        # Initialize only once
        if not hasattr(self, 'initialized'):
            print("[ResourceManager] Initializing resource manager...")
            # Get the file manager singleton
            self.file_manager = FileManager()
            # Storage for different resource types
            self.music_tracks = {}
            self.sound_effects = {}
            self.images = {}
            self.sprites = {}
            # Load default resources
            self._load_default_music()
            # Mark as initialized
            self.initialized = True
            print("[ResourceManager] Resource manager initialized")

    def _load_file(self, name, file_path):
        """Load a file and store it by name"""
        if name in self.files:
            print(f"[ResourceManager] File '{name}' already loaded")
            return self.files[name]
        if not os.path.exists(file_path):
            print(f"[ResourceManager] ERROR: Sound file not found: {file_path}")
            return False
        return True

    def _load_default_music(self):
        """Pre-load the default music tracks"""
        self.load_music("MENU", MENU_BGM_PATH)
        self.load_music("PLAYING", GAME_BGM_PATH)

    def load_music(self, name, file_path):
        """Load a music track and store it by name"""
        if name in self.music_tracks:
            print(f"[ResourceManager] Music '{name}' already loaded")
            return True

        if not self.file_manager.exists(file_path):
            print(f"[ResourceManager] ERROR: Music file not found: {file_path}")
            return False

        # We don't actually load the music file into memory,
        # just store the path for later use with pygame.mixer.music
        self.music_tracks[name] = file_path
        print(f"[ResourceManager] Music track '{name}' registered: {file_path}")
        return True

    def load_sound(self, name, file_path):
        """Load a sound effect and store it by name"""
        if name in self.sound_effects:
            print(f"[ResourceManager] Sound '{name}' already loaded")
            return True

        if not self.file_manager.exists(file_path):
            print(f"[ResourceManager] ERROR: Sound file not found: {file_path}")
            return False

        try:
            # Load the binary data using FileManager
            binary_data = self.file_manager.load_bytes(f"sound_{name}", file_path)
            if binary_data is None:
                return False
                
            # Convert the binary data to a pygame Sound
            self.sound_effects[name] = pygame.mixer.Sound(binary_data)
            print(f"[ResourceManager] Loaded sound effect: {name}")
            return True
        except Exception as e:
            print(f"[ResourceManager] ERROR loading sound '{name}': {e}")
            return False

    def load_image(self, name, file_path, convert_alpha=True):
        """Load an image and store it by name"""
        if name in self.images:
            print(f"[ResourceManager] Image '{name}' already loaded")
            return self.images[name]

        if not self.file_manager.exists(file_path):
            print(f"[ResourceManager] ERROR: Image file not found: {file_path}")
            return None

        try:
            # Load the binary data using FileManager
            binary_data = self.file_manager.load_bytes(f"image_{name}", file_path)
            if binary_data is None:
                return None
                
            # Convert the binary data to a pygame Surface
            import io
            image_stream = io.BytesIO(binary_data)
            image = pygame.image.load(image_stream)
            
            if convert_alpha:
                image = image.convert_alpha()
            else:
                image = image.convert()
                
            self.images[name] = image
            print(f"[ResourceManager] Loaded image: {name}")
            return image
        except Exception as e:
            print(f"[ResourceManager] ERROR loading image '{name}': {e}")
            return None

    def load_sprite_sheet(self, name, file_path, sprite_width, sprite_height):
        """Load a sprite sheet and store it by name"""
        if name in self.sprites:
            print(f"[ResourceManager] Sprite sheet '{name}' already loaded")
            return self.sprites[name]

        base_image = self.load_image(f"{name}_base", file_path)
        if not base_image:
            return None

        # Store metadata about the sprite sheet
        self.sprites[name] = {
            "sheet": base_image,
            "width": sprite_width,
            "height": sprite_height
        }

        print(f"[ResourceManager] Loaded sprite sheet: {name}")
        return self.sprites[name]

    def load_config(self, name, file_path):
        """Load a JSON configuration file"""
        return self.file_manager.load_json(f"config_{name}", file_path)

    def load_data(self, name, file_path, as_dict=True):
        """Load a CSV data file"""
        return self.file_manager.load_csv(f"data_{name}", file_path, as_dict=as_dict)

    def get_music_path(self, name):
        """Get the file path for a music track"""
        if name in self.music_tracks:
            return self.music_tracks[name]
        print(f"[ResourceManager] Music '{name}' not found")
        return None

    def get_sound(self, name):
        """Get a loaded sound effect"""
        if name in self.sound_effects:
            return self.sound_effects[name]
        print(f"[ResourceManager] Sound effect '{name}' not found")
        return None

    def get_image(self, name):
        """Get a loaded image"""
        if name in self.images:
            return self.images[name]
        print(f"[ResourceManager] Image '{name}' not found")
        return None

    def get_sprite_sheet(self, name):
        """Get a loaded sprite sheet"""
        if name in self.sprites:
            return self.sprites[name]
        print(f"[ResourceManager] Sprite sheet '{name}' not found")
        return None

    def get_sprite(self, sheet_name, row, col):
        """Extract a specific sprite from a loaded sprite sheet"""
        if sheet_name not in self.sprites:
            print(f"[ResourceManager] Sprite sheet '{sheet_name}' not found")
            return None

        sheet = self.sprites[sheet_name]
        sprite_width = sheet["width"]
        sprite_height = sheet["height"]

        # Create a surface for the sprite
        sprite = pygame.Surface((sprite_width, sprite_height), pygame.SRCALPHA)

        # Calculate the position in the sprite sheet
        x = col * sprite_width
        y = row * sprite_height

        # Extract the sprite
        sprite.blit(sheet["sheet"], (0, 0), (x, y, sprite_width, sprite_height))

        return sprite

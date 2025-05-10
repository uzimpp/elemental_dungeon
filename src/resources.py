"""
A simple resource manager for game assets (audio, images, etc.) using a singleton pattern.
"""
import os
import pygame


class Resources:
    """
    Singleton resources manager for game assets like audio files, images, etc.
    This class ensures resources are loaded only once and stored in memory.
    """
    _instance = None
    @classmethod
    def get_instance(cls):
        """Get the singleton instance"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        if hasattr(self, "initialized"):
            return
        # Resource storage dictionaries
        self._images = {}     # Image/sprite resources
        self._sounds = {}     # Sound resources
        self._fonts = {}      # Font resources
        self._data = {}       # General data resources
        
        # Base paths
        self.base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.asset_path = os.path.join(self.base_path, "assets")
        self.data_path = os.path.join(self.base_path, "data")
        
        self.initialized = True
        print(f"Resources initialized (base path: {self.base_path})")
            
    def get_path(self, relative_path):
        """Convert a relative path to an absolute path based on the game's root directory"""
        if os.path.isabs(relative_path):
            return relative_path
            
        return os.path.join(self.base_path, relative_path)

    def load_image(self, name, relative_path):
        """Load and cache an image by name."""
        if name in self._images:
            return self._images[name]
            
        full_path = self.get_path(relative_path)
        try:
            image = pygame.image.load(full_path).convert_alpha()
            self._images[name] = image
            return image
        except Exception as e:
            print(f"Error loading image '{full_path}': {e}")
            return None

    def get_image(self, name):
        """Retrieve a loaded image by name."""
        return self._images.get(name)
    
    def load_sound(self, name, relative_path):
        """Load and cache a sound file by name."""
        if name in self._sounds:
            return self._sounds[name]
            
        full_path = self.get_path(relative_path)
        try:
            sound = pygame.mixer.Sound(full_path)
            self._sounds[name] = sound
            return sound
        except Exception as e:
            print(f"Error loading sound '{full_path}': {e}")
            return None

    def get_sound(self, name):
        """Retrieve a loaded sound by name."""
        return self._sounds.get(name)

    def load_font(self, name, relative_path, size):
        """Load and cache a font by name and size."""
        font_key = f"{name}_{size}"
        if font_key in self._fonts:
            return self._fonts[font_key]
        full_path = self.get_path(relative_path)
        try:
            font = pygame.font.Font(full_path, size)
            self._fonts[font_key] = font
            return font
        except Exception as e:
            print(f"Error loading font '{full_path}': {e}")
            return None
    def get_font(self, name, size):
        """Retrieve a loaded font by name and size."""
        font_key = f"{name}_{size}"
        return self._fonts.get(font_key)

    def store_data(self, name, data):
        """Store arbitrary data by name."""
        self._data[name] = data
        return data

    def get_data(self, name):
        """Retrieve stored data by name."""
        return self._data.get(name)

    def clear(self, resource_type=None):
        """Clear resources of a specific type or all resources if type is None."""
        if resource_type is None:
            self._images.clear()
            self._sounds.clear()
            self._fonts.clear()
            self._data.clear()
        elif resource_type == "images":
            self._images.clear()
        elif resource_type == "sounds":
            self._sounds.clear()
        elif resource_type == "fonts":
            self._fonts.clear()
        elif resource_type == "data":
            self._data.clear()

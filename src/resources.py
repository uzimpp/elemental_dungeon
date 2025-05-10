"""
Resource manager for game resources like audio files, images, etc.
This class ensures resources are loaded only once and stored in memory.
"""
import os


class Resources:
    """
    Singleton resources manager for game resources like audio files, images, etc.
    This class ensures resources are loaded only once and stored in memory.
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "initialized"):
            self._resources = {}  # instance attribute for all resources
            self.initialized = True
            print("[Resources] Initialized resource storage.")

    def exists(self, file_path):
        """Check if a file exists."""
        return os.path.exists(file_path)

    def load_file(self, name, file_path):
        """Load a file and store it by name. Returns the file path if successful."""
        if name in self._resources:
            return self._resources[name]
        if not self.exists(file_path):
            print(f"[Resources] File not found: {file_path}")
            return None
        self._resources[name] = file_path
        print(f"[Resources] Loaded file: {name} -> {file_path}")
        return file_path

    def get_file(self, name):
        """Retrieve a loaded file path by name."""
        return self._resources.get(name, None)

    def load_image(self, name, file_path, pygame_module=None):
        """Load and cache an image (sprite sheet) by name."""
        if name in self._resources:
            return self._resources[name]
        if not self.exists(file_path):
            print(f"[Resources] Image file not found: {file_path}")
            return None
        try:
            image = pygame_module.image.load(file_path).convert_alpha()
            self._resources[name] = image
            print(f"[Resources] Loaded image: {name} -> {file_path}")
            return image
        except Exception as e:
            print(f"[Resources] Error loading image '{file_path}': {e}")
            return None

    def get_image(self, name):
        """Retrieve a loaded image by name."""
        return self._resources.get(name, None)

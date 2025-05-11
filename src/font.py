"""
Font management module for Incantato game.

Provides a singleton Font class to centralize font loading and access,
ensuring consistent typography across the game interface.
"""
import pygame


class Font:
    """
    Central font manager using singleton pattern for all game fonts.

    Ensures proper initialization and caching of fonts at different sizes.
    """
    _instance = None
    _initialized = False
    _fonts = {}
    _font_path = None

    def __new__(cls):
        """
        Create or return the singleton instance.

        Returns:
            Font: The singleton Font instance
        """
        if cls._instance is None:
            cls._instance = super(Font, cls).__new__(cls)
            # Initialize instance attributes (to avoid defining them outside __init__)
            cls._instance._fonts = {}
            cls._instance._font_path = None
            cls._instance._initialized = False
        return cls._instance

    def initialize(self, font_path, sizes):
        """
        Initialize fonts after pygame has been initialized.

        Args:
            font_path: Path to the font file
            sizes: Dictionary mapping name to font size

        Raises:
            RuntimeError: If pygame is not initialized
        """
        if not pygame.get_init():
            raise RuntimeError(
                "Pygame must be initialized before initializing fonts")

        self._initialized = True
        self._font_path = font_path

        # Load all fonts at specified sizes
        for name, size in sizes.items():
            self._fonts[name] = pygame.font.Font(font_path, size)

    def get_font(self, name):
        """
        Get a font by name or size.

        Args:
            name: Font name from initialization or an integer size

        Returns:
            pygame.font.Font: The requested font

        Raises:
            RuntimeError: If fonts are not initialized
            ValueError: If the requested font name doesn't exist
        """
        if not self._initialized:
            raise RuntimeError("Call initialize() first")

        if name in self._fonts:
            return self._fonts[name]

        # If requesting a numeric size directly
        if isinstance(name, int):
            if name not in self._fonts:
                self._fonts[name] = pygame.font.Font(self._font_path, name)
            return self._fonts[name]

        raise ValueError(f"Font '{name}' not found")

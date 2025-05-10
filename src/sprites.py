import pygame
from resources import Resources

class Sprites:
    """Utility class to handle loading and extracting sprites from a sheet."""

    def __init__(self, name, image_path):
        self.resources = Resources.get_instance()  # Get the singleton instance
        self.sprite_sheet = self.resources.load_image(name, image_path)
        if self.sprite_sheet is None:
            raise SystemExit(f"Error loading sprite sheet: {image_path}")

    def get_sprite(self, x, y, width, height):
        """Extracts a single sprite (surface) from the sheet."""
        sprite = pygame.Surface((width, height), pygame.SRCALPHA)
        sprite.blit(self.sprite_sheet, (0, 0), (x, y, width, height))
        return sprite

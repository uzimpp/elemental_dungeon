import pygame
from resources import Resources

class SpriteSheet:
    """Utility class to handle loading and extracting sprites from a sheet."""

    def __init__(self, name, image_path):
        self.resources = Resources()  # Composition: use the singleton resource manager
        self.sprite_sheet = self.resources.load_image(name, image_path, pygame)
        if self.sprite_sheet is None:
            raise SystemExit(f"Error loading sprite sheet: {image_path}")

    def get_sprite(self, x, y, width, height):
        """Extracts a single sprite (surface) from the sheet."""
        sprite = pygame.Surface((width, height), pygame.SRCALPHA)
        sprite.blit(self.sprite_sheet, (0, 0), (x, y, width, height))
        return sprite

"""
Sprite handling module for Incantato.
Provides utility classes for loading and extracting sprites from sprite sheets.
"""
import pygame
from resources import Resources


class Sprites:
    """
    Utility class to handle loading and extracting sprites from a sprite sheet.
    
    Provides the primary interface for accessing sprite frames from loaded
    sprite sheets with appropriate sizing and positioning.
    """

    def __init__(self, name, image_path):
        """
        Initialize a sprite sheet handler.
        
        Args:
            name (str): Name identifier for the sprite sheet
            image_path (str): Path to the sprite sheet image file
        """
        self.resources = Resources.get_instance()  # Get the singleton instance
        self.sprite_sheet = self.resources.load_image(name, image_path)
        if self.sprite_sheet is None:
            raise SystemExit(f"Error loading sprite sheet: {image_path}")

    def get_sprite(self, x, y, width, height):
        """
        Extracts a single sprite (surface) from the sheet.
        
        Args:
            x (int): X coordinate of the top-left corner of the sprite
            y (int): Y coordinate of the top-left corner of the sprite
            width (int): Width of the sprite in pixels
            height (int): Height of the sprite in pixels
            
        Returns:
            pygame.Surface: The extracted sprite as a Surface
        """
        sprite = pygame.Surface((width, height), pygame.SRCALPHA)
        sprite.blit(self.sprite_sheet, (0, 0), (x, y, width, height))
        return sprite

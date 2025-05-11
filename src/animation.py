"""
Animation module for sprite-based character animations in Incantato.

Handles sprite sheet loading, animation state management, and
directional 8-way character animations based on movement.
"""
import math

import pygame

from config import Config as C
from utils import Utils


class SpriteSheet:
    """Utility class to handle loading and extracting sprites from a sheet."""

    def __init__(self, image_path):
        """
        Initialize a sprite sheet from an image file.

        Args:
            image_path: Path to the sprite sheet image

        Raises:
            SystemExit: If the sprite sheet cannot be loaded
        """
        try:
            self.sprite_sheet = pygame.image.load(image_path).convert_alpha()
        except pygame.error as e:
            print(f"Error loading sprite sheet: {image_path}")
            print(e)
            raise SystemExit() from e

    def get_sprite(self, x, y, width, height):
        """
        Extracts a single sprite from the sheet.

        Args:
            x: X-coordinate of the sprite in the sheet
            y: Y-coordinate of the sprite in the sheet
            width: Width of the sprite
            height: Height of the sprite

        Returns:
            pygame.Surface: The extracted sprite
        """
        sprite = pygame.Surface((width, height), pygame.SRCALPHA)
        sprite.blit(self.sprite_sheet, (0, 0), (x, y, width, height))
        return sprite


class CharacterAnimation:
    """Handles state-based character animation from an 8-directional sprite sheet."""

    # Maps atan2 movement angle to the sprite sheet row index
    DIRECTION_ROWS = {
        90:  0,   # Angle 90 (Movement DOWN) uses Row 0
        45: 1,    # Angle 45 (Movement DOWN-LEFT) uses Row 1
        0: 2,     # Angle 0 (Movement LEFT) uses Row 2
        315: 3,   # Angle 315 (Movement UP-LEFT) uses Row 3
        270: 4,   # Angle 270 (Movement UP) uses Row 4
        225: 5,   # Angle 225 (Movement UP-RIGHT) uses Row 5
        180: 6,   # Angle 180 (Movement RIGHT) uses Row 6
        135: 7    # Angle 135 (Movement DOWN-RIGHT) uses Row 7
    }

    # List of valid atan2 angles for easy lookup
    ANGLES = list(DIRECTION_ROWS.keys())

    def __init__(self, sprite_sheet_path, config, sprite_width=32, sprite_height=32):
        """
        Initializes the animation handler with state configurations.

        Args:
            sprite_sheet_path: Path to the sprite sheet image
            config: Dictionary defining animation states and their properties
                    Example: {'idle': {'animations':[0,1], 'duration':0.2, 'loop':True, 'directional':True}}
            sprite_width: Width of a single sprite frame
            sprite_height: Height of a single sprite frame
        """
        self.sprite_sheet = SpriteSheet(sprite_sheet_path)
        self.config = config
        self.sprite_width = sprite_width
        self.sprite_height = sprite_height

        self.current_state = 'idle'
        self.current_frame_index = 0
        self.frame_timer = 0.0
        self.current_direction_angle = 90  # Start facing DOWN
        self.animation_finished = False

        # Pre-load all frames from the sheet for efficiency
        self.all_frames = self._load_all_frames_from_sheet()

    def _load_all_frames_from_sheet(self):
        """
        Loads and scales the entire sprite sheet.

        Returns:
            list: 2D array of extracted sprite frames
        """
        # Determine sheet dimensions based on known rows and max columns needed
        num_rows = len(self.DIRECTION_ROWS)
        max_col = 0

        for state_data in self.config.values():
            max_col = max(max_col, max(state_data['animations']) + 1)

        all_frames = []
        for row in range(num_rows):
            row_frames = []
            for col in range(max_col):
                x = col * self.sprite_width
                y = row * self.sprite_height
                sprite = self.sprite_sheet.get_sprite(
                    x, y, self.sprite_width, self.sprite_height)
                row_frames.append(sprite)
            all_frames.append(row_frames)
        return all_frames

    def _get_closest_direction_angle(self, target_angle_rad):
        """
        Finds the closest of the 8 movement directions to the target angle.

        Args:
            target_angle_rad: Target angle in radians, or None

        Returns:
            int: The closest angle from the ANGLES list
        """
        if target_angle_rad is None:
            return self.current_direction_angle

        target_angle_deg = math.degrees(target_angle_rad)
        target_angle_deg = (target_angle_deg + 360) % 360

        closest_angle = min(
            self.ANGLES,
            key=lambda angle: Utils.angle_diff(angle, target_angle_deg))
        return closest_angle

    def set_state(self, new_state, force_reset=False):
        """
        Changes the current animation state if different.

        Args:
            new_state: Name of the new state to set
            force_reset: Whether to reset even if state is the same
        """
        if new_state != self.current_state or force_reset:
            if new_state in self.config:
                self.current_state = new_state
                self.current_frame_index = 0
                self.frame_timer = 0.0
                self.animation_finished = False

    def update(self, dt, move_dx=0, move_dy=0):
        """
        Updates the animation frame and direction based on state and movement.

        Args:
            dt: Delta time since last update
            move_dx: Horizontal movement direction
            move_dy: Vertical movement direction
        """
        if self.current_state not in self.config:
            return

        state_cfg = self.config[self.current_state]
        is_directional = state_cfg.get('directional', False)
        num_frames = len(state_cfg['animations'])
        duration = state_cfg['duration']
        loop = state_cfg['loop']

        # Update Direction
        if is_directional:
            is_moving = (move_dx != 0 or move_dy != 0)
            if is_moving:
                movement_angle_rad = math.atan2(move_dy, move_dx)
                self.current_direction_angle = self._get_closest_direction_angle(
                    movement_angle_rad)

        # Update Frame
        if self.animation_finished and not loop:
            return

        self.frame_timer += dt
        if self.frame_timer >= duration:
            self.frame_timer -= duration

            if self.current_frame_index < num_frames - 1:
                self.current_frame_index += 1
            elif loop:
                self.current_frame_index = 0
            else:
                self.animation_finished = True

    def get_current_sprite(self):
        """
        Returns the current sprite surface based on state and direction.

        Returns:
            pygame.Surface: The current sprite to render
        """
        if self.current_state not in self.config:
            return self.all_frames[0][0]

        state_cfg = self.config[self.current_state]
        is_directional = state_cfg.get('directional', False)

        # Determine row index
        row_index = 0
        if is_directional:
            if self.current_direction_angle in self.DIRECTION_ROWS:
                row_index = self.DIRECTION_ROWS[self.current_direction_angle]
            else:
                row_index = self.DIRECTION_ROWS[90]
        else:
            row_index = state_cfg.get('fixed_row', 0)

        # Determine column index
        animations = state_cfg['animations']
        frame_idx = min(self.current_frame_index, len(animations) - 1)
        col_index = animations[frame_idx]

        # Get the sprite
        try:
            sprite = self.all_frames[row_index][col_index]
            return sprite
        except IndexError:
            return self.all_frames[0][0]

    @staticmethod
    def get_sprite_size():
        """
        Returns the size of the sprite sheet.

        Returns:
            tuple: (scale, width, height) of sprites after scaling
        """
        scale = C.RENDER_SIZE / C.SPRITE_SIZE
        scale_width = C.SPRITE_SIZE * scale
        scale_height = C.SPRITE_SIZE * scale
        return scale, scale_width, scale_height

import pygame
import math
from config import Config as C
from utils import Utils

class SpriteSheet:
    """Utility class to handle loading and extracting sprites from a sheet."""

    def __init__(self, image_path):
        try:
            self.sprite_sheet = pygame.image.load(image_path).convert_alpha()
        except pygame.error as e:
            print(f"Error loading sprite sheet: {image_path}")
            print(e)
            # You might want to provide a default fallback image or exit
            raise SystemExit()  # Or handle it differently

    def get_sprite(self, x, y, width, height):
        """Extracts a single sprite (surface) from the sheet."""
        # Create a blank surface with transparency
        sprite = pygame.Surface((width, height), pygame.SRCALPHA)
        # Blit the relevant part of the sprite sheet onto the blank surface
        sprite.blit(self.sprite_sheet, (0, 0), (x, y, width, height))
        return sprite



class CharacterAnimation:
    """Handles state-based character animation from an 8-directional sprite sheet."""

    # --- Direction Mapping (Adjusted based on previous feedback) ---
    # Maps atan2 movement angle to the sprite sheet row index
    DIRECTION_ROWS = {
        # atan2 Angle: Sprite Sheet Row Index
        90:  0,   # Angle 90 (Movement DOWN) uses Row 0 (Visually Down)
        45: 1,   # Angle 45 (Movement DOWN-LEFT) uses Row 1
        0: 2,   # Angle 0 (Movement LEFT) uses Row 2
        315: 3,   # Angle 315 (Movement UP-LEFT) uses Row 3
        270: 4,   # Angle 270 (Movement UP) uses Row 4 (Visually Up)
        225: 5,   # Angle 225 (Movement UP-RIGHT) uses Row 5
        180:   6,   # Angle 180 (Movement RIGHT) uses Row 6 (Visually Right)
        135:  7    # Angle 135 (Movement DOWN-RIGHT) uses Row 7
    }

    # Define animation configurations based on sprite sheet columns
    # Remember: Columns are 0-indexed!
    ANIMATION_CONFIG = {
        # State: {animations, frames, duration_per_frame, loop?, directional?, fixed_row?}
        # Col 1,2
        'idle':   {'animations': [0, 1], 'duration': 0.2, 'loop': True, 'directional': True},
        # Cols 3, 4
        'walk':   {'animations': [2, 1, 3], 'duration': 0.15, 'loop': True, 'directional': True},
        # Cols 3,4
        'sprint': {'animations': [2, 1, 3], 'duration': 0.1, 'loop': True, 'directional': True},
        # Cols 5-8
        'sweep': {'animations': [4, 5, 6, 7], 'duration': 0.1, 'loop': False, 'directional': True},
        # Future: Cols 9-12
        'shoot_arrow': {'animations': [8, 9, 10, 11], 'duration': 0.1, 'loop': False, 'directional': True},
        # Cols 13, 14, 15
        'cast':   {'animations': [12, 13, 14], 'duration': 0.1, 'loop': False, 'directional': True},
        # Cols 16, 17, 18
        'throw': {'animations': [15, 16, 17], 'duration': 0.1, 'loop': False, 'directional': True},
        # Future?: Col 20 - Likely needs special handling
        'hurt': {'animations': [18, 19, 20], 'duration': 0.1, 'loop': False, 'directional': True},
        # Cols 21-24. Assume fixed row (e.g., UP Row 4) for dying? Or use last direction? Let's try fixed row.
        'dying':  {'animations': [21, 22, 23], 'duration': 0.2, 'loop': False, 'directional': True},
    }
    # List of valid atan2 angles for easy lookup
    ANGLES = list(DIRECTION_ROWS.keys())

    def __init__(self, name, sprite_sheet_path, sprite_width=32, sprite_height=32):
        """
        Initializes the animation handler with state configurations.

        Args:
            sprite_sheet_path (str): Path to the sprite sheet image.
            config (dict): Dictionary defining animation states and their properties.
                           Example: {'idle': {'start_col':0, 'frames':1, 'duration':0.2, 'loop':True, 'directional':True}, ...}
            sprite_width (int): Width of a single sprite frame.
            sprite_height (int): Height of a single sprite frame.
        """
        self.sprite_sheet = Sprites(name, sprite_sheet_path)
        self.sprite_width = sprite_width
        self.sprite_height = sprite_height

        self.state = 'idle'
        self.frame_index = 0  # Index within the *current state's* animation sequence
        self.frame_timer = 0.0
        self.direction_angle = 90  # Start facing DOWN
        self.animation_finished = False  # Flag for non-looping animations

        # Pre-load all frames from the sheet for efficiency
        self.all_frames = self._load_all_frames_from_sheet()

    def _load_all_frames_from_sheet(self):
        """Loads and scales the entire sprite sheet."""
        # Determine sheet dimensions based on known rows and max columns needed
        num_rows = len(self.DIRECTION_ROWS)
        max_col = 0

        for state_data in self.ANIMATION_CONFIG.values():
            max_col = max(max_col, max(state_data['animations']) + 1)

        all_frames = []
        for row in range(num_rows):
            row_frames = []
            for col in range(max_col):
                x = col * self.sprite_width
                y = row * self.sprite_height
                sprite = self.sprite_sheet.get_sprite(x, y, self.sprite_width, self.sprite_height)
                row_frames.append(sprite)
            all_frames.append(row_frames)
        return all_frames

    def _get_closest_direction_angle(self, target_angle_rad):
        """Finds the closest of the 8 movement directions to the target angle."""
        if target_angle_rad is None:  # Handle cases where direction is irrelevant or fixed
            return self.direction_angle

        target_angle_deg = math.degrees(target_angle_rad)
        target_angle_deg = (target_angle_deg + 360) % 360

        closest_angle = min(
            self.ANGLES, key=lambda angle: Utils.angle_diff(angle, target_angle_deg))
        return closest_angle


    def set_state(self, new_state, force_reset=False):
        """Changes the current animation state if different."""
        if new_state != self.current_state or force_reset:
            if new_state in self.config:
                self.current_state = new_state
                self.current_frame_index = 0
                self.frame_timer = 0.0
                self.animation_finished = False  # Reset finished flag on state change
            else:
                # Silently fail with invalid states
                pass

    def update(self, dt, move_dx=0, move_dy=0):
        """Updates the animation frame and direction based on state and movement."""
        if self.state not in self.ANIMATION_CONFIG:
            return

        state_cfg = self.ANIMATION_CONFIG[self.state]
        is_directional = state_cfg.get('directional', False)
        num_frames = len(state_cfg['animations'])
        duration = state_cfg['duration']
        loop = state_cfg['loop']

        # --- Update Direction ---
        if is_directional:
            is_moving = (move_dx != 0 or move_dy != 0)
            if is_moving:
                movement_angle_rad = math.atan2(move_dy, move_dx)
                self.direction_angle = self._get_closest_direction_angle(
                    movement_angle_rad)
            # Else: keep the last direction if not moving but in a directional state (like idle)

        # --- Update Frame ---
        if self.animation_finished and not loop:
            return  # Don't update frame if a non-looping animation is done

        self.frame_timer += dt
        if self.frame_timer >= duration:
            self.frame_timer -= duration  # Use subtraction for accuracy

            if self.frame_index < num_frames - 1:
                self.frame_index += 1
            elif loop:
                self.frame_index = 0  # Loop back to start
            else:
                self.animation_finished = True  # Mark as finished

    def get_sprite(self):
        """Returns the current sprite surface based on state and direction."""
        if self.current_state not in self.config:
            # Return a default sprite if state is invalid
            return self.all_frames[0][0]  # Return a default sprite

        state_cfg = self.ANIMATION_CONFIG[self.state]
        is_directional = state_cfg.get('directional', False)

        # Determine row index
        row_index = 0  # Default row
        if is_directional:
            if self.direction_angle in self.DIRECTION_ROWS:
                row_index = self.DIRECTION_ROWS[self.direction_angle]
            else:
                # Use default down direction if angle not found
                row_index = self.DIRECTION_ROWS[90]
        else:
            # For non-directional, maybe use a fixed row specified in config
            row_index = state_cfg.get('fixed_row', 0)

        # Determine column index
        animations = state_cfg['animations']
        frame_idx = min(self.current_frame_index, len(animations) - 1)  # Safety check
        col_index = animations[frame_idx]

        # Get the sprite
        try:
            sprite = self.all_frames[row_index][col_index]
            return sprite
        except IndexError:
            # Return default sprite on error
            return self.all_frames[0][0]

    @staticmethod
    def get_sprite_size():
        """Returns the size of the sprite sheet."""
        scale = C.RENDER_SIZE / C.SPRITE_SIZE
        scale_width = C.SPRITE_SIZE * scale
        scale_height = C.SPRITE_SIZE * scale
        return scale, scale_width, scale_height

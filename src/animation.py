import pygame
import math

class SpriteSheet:
    """Utility class to handle loading and extracting sprites from a sheet."""
    def __init__(self, image_path):
        try:
            self.sprite_sheet = pygame.image.load(image_path).convert_alpha()
        except pygame.error as e:
            print(f"Error loading sprite sheet: {image_path}")
            print(e)
            # You might want to provide a default fallback image or exit
            raise SystemExit() # Or handle it differently

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
    # List of valid atan2 angles for easy lookup
    ANGLES = list(DIRECTION_ROWS.keys())

    def __init__(self, sprite_sheet_path, config, sprite_width=32, sprite_height=32):
        """
        Initializes the animation handler with state configurations.

        Args:
            sprite_sheet_path (str): Path to the sprite sheet image.
            config (dict): Dictionary defining animation states and their properties.
                           Example: {'idle': {'start_col':0, 'frames':1, 'duration':0.2, 'loop':True, 'directional':True}, ...}
            sprite_width (int): Width of a single sprite frame.
            sprite_height (int): Height of a single sprite frame.
        """
        self.sprite_sheet = SpriteSheet(sprite_sheet_path)
        self.config = config
        self.sprite_width = sprite_width
        self.sprite_height = sprite_height

        self.current_state = 'idle'
        self.current_frame_index = 0 # Index within the *current state's* animation sequence
        self.frame_timer = 0.0
        self.current_direction_angle = 90  # Start facing DOWN
        self.animation_finished = False # Flag for non-looping animations

        # Pre-load all frames from the sheet for efficiency
        self.all_frames = self._load_all_frames_from_sheet()
        # print("[DEBUG] Finished loading all frames.") # Keep for debugging

    def _load_all_frames_from_sheet(self):
        """Loads the entire sprite sheet into a 2D list: all_frames[row][col]"""
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
                 sprite = self.sprite_sheet.get_sprite(x, y,
                                                     self.sprite_width,
                                                     self.sprite_height)
                 row_frames.append(sprite)
             all_frames.append(row_frames)
        return all_frames


    def _get_closest_direction_angle(self, target_angle_rad):
        """Finds the closest of the 8 movement directions to the target angle."""
        if target_angle_rad is None: # Handle cases where direction is irrelevant or fixed
             return self.current_direction_angle

        target_angle_deg = math.degrees(target_angle_rad)
        target_angle_deg = (target_angle_deg + 360) % 360

        def angle_diff(a1, a2):
            diff = abs(a1 - a2) % 360
            return min(diff, 360 - diff)

        closest_angle = min(self.ANGLES, key=lambda angle: angle_diff(angle, target_angle_deg))
        return closest_angle

    def set_state(self, new_state, force_reset=False):
        """Changes the current animation state if different."""
        if new_state != self.current_state or force_reset:
            if new_state in self.config:
                # print(f"[DEBUG] Animation State Change: {self.current_state} -> {new_state}") # Keep for debugging
                self.current_state = new_state
                self.current_frame_index = 0
                self.frame_timer = 0.0
                self.animation_finished = False # Reset finished flag on state change
            else:
                print(f"Warning: Attempted to set unknown animation state '{new_state}'")

    def update(self, dt, move_dx=0, move_dy=0):
        """Updates the animation frame and direction based on state and movement."""
        if self.current_state not in self.config:
            return # Unknown state

        state_cfg = self.config[self.current_state]
        is_directional = state_cfg.get('directional', False)
        num_frames = len(state_cfg['animations'])
        duration = state_cfg['duration']
        loop = state_cfg['loop']

        # --- Update Direction ---
        if is_directional:
            is_moving = (move_dx != 0 or move_dy != 0)
            if is_moving:
                 movement_angle_rad = math.atan2(move_dy, move_dx)
                 self.current_direction_angle = self._get_closest_direction_angle(movement_angle_rad)
            # Else: keep the last direction if not moving but in a directional state (like idle)

        # --- Update Frame ---
        if self.animation_finished and not loop:
             return # Don't update frame if a non-looping animation is done

        self.frame_timer += dt
        if self.frame_timer >= duration:
            self.frame_timer -= duration # Use subtraction for accuracy

            if self.current_frame_index < num_frames - 1:
                self.current_frame_index += 1
            elif loop:
                self.current_frame_index = 0 # Loop back to start
            else:
                self.animation_finished = True # Mark as finished


    def get_current_sprite(self):
        """Returns the current sprite surface based on state and direction."""
        if self.current_state not in self.config:
             print(f"Warning: Current animation state '{self.current_state}' not in config.")
             return self.all_frames[0][0] # Return a default sprite

        state_cfg = self.config[self.current_state]
        is_directional = state_cfg.get('directional', False)

        # Determine row index
        row_index = 0 # Default row?
        if is_directional:
             if self.current_direction_angle in self.DIRECTION_ROWS:
                 row_index = self.DIRECTION_ROWS[self.current_direction_angle]
             else:
                 print(f"Warning: Current direction angle {self.current_direction_angle} not in mapping.")
                 row_index = self.DIRECTION_ROWS[90] # Default to down?
        else:
             # For non-directional, maybe use a fixed row specified in config?
             row_index = state_cfg.get('fixed_row', 0) # Example: defaults to row 0 if not specified

        # Determine column index
        animations = state_cfg['animations']
        frame_idx = min(self.current_frame_index, len(animations) - 1)  # Safety check
        col_index = animations[frame_idx]  # Use the column directly from animations array

        # Get the sprite
        try:
            sprite = self.all_frames[row_index][col_index]
            return sprite
        except IndexError:
            print(f"!!! Error getting sprite: Row {row_index}, Col {col_index} out of bounds!")
            print(f"    State={self.current_state}, Angle={self.current_direction_angle}, FrameIdx={self.current_frame_index}")
            return self.all_frames[0][0] # Return default sprite on error

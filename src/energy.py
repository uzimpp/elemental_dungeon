import time


class DashAfterimage:
    """A fading afterimage effect using a specific sprite."""

    def __init__(self, x, y, sprite, duration=0.2, start_alpha=150):
        self.x = x
        self.y = y
        self.sprite = sprite.copy()  # Copy the surface to modify alpha
        self.duration = duration
        self.start_alpha = start_alpha
        self.start_time = time.time()
        self.active = True
        self.width = sprite.get_width()
        self.height = sprite.get_height()

    def update(self, dt):
        elapsed = time.time() - self.start_time
        progress = elapsed / self.duration

        if progress >= 1.0:
            self.active = False
            return

        # Calculate current alpha (fade out)
        current_alpha = self.start_alpha * (1.0 - progress)
        # Apply alpha to the copied sprite
        self.sprite.set_alpha(int(max(0, current_alpha)))

    def draw(self, surf):
        if not self.active or not self.sprite:
            return

        # Calculate top-left draw position (centering the stored sprite)
        draw_x = self.x - self.width / 2
        draw_y = self.y - self.height / 2
        surf.blit(self.sprite, (int(draw_x), int(draw_y)))

    def is_ground_effect(self):  # Helper for potential layering in game.py
        return True  # Treat afterimage as a ground effect maybe?

class Energy:
    """Manages energy-related attributes and behaviors for entities"""
    def __init__(self, walk_speed, sprint_speed, max_stamina, stamina_regen, sprint_drain, dash_cost, stamina_cooldown):
        # Speed attributes
        self.walk_speed = walk_speed
        self.sprint_speed = sprint_speed
        self.current_speed = walk_speed

        # Stamina System
        self.max_stamina = max_stamina
        self.stamina = max_stamina
        self.stamina_regen = stamina_regen
        self.sprint_drain = sprint_drain
        self.dash_cost = dash_cost
        self.stamina_depleted_time = None
        self.stamina_cooldown = stamina_cooldown
        
        # State tracking
        self.is_sprinting = False

    def update(self, dt, is_moving):
        """Update stamina and speed based on movement"""
        # Handle sprinting
        if self.is_sprinting and is_moving:
            self.stamina -= self.sprint_drain * dt
            if self.stamina <= 0:
                self.stamina = 0
                self.stamina_depleted_time = time.time()
                self.is_sprinting = False
        else:
            # Regenerate stamina
            can_regen = True
            if self.stamina == 0 and self.stamina_depleted_time is not None:
                if time.time() - self.stamina_depleted_time < self.stamina_cooldown:
                    can_regen = False
            if can_regen and self.stamina < self.max_stamina:
                self.stamina += self.stamina_regen * dt
                if self.stamina > self.max_stamina:
                    self.stamina = self.max_stamina
                    self.stamina_depleted_time = None

        # Update current speed
        self.current_speed = self.sprint_speed if self.is_sprinting else self.walk_speed

    def can_dash(self):
        """Check if entity can perform a dash"""
        return self.stamina >= self.dash_cost

    def use_dash(self):
        """Use stamina for a dash"""
        if self.can_dash():
            self.stamina -= self.dash_cost
            return True
        return False

    def set_sprinting(self, is_sprinting):
        """Set sprinting state"""
        self.is_sprinting = is_sprinting

    def get_current_speed(self):
        """Get current movement speed"""
        return self.current_speed

    def get_stamina_percentage(self):
        """Get current stamina as a percentage"""
        return self.stamina / self.max_stamina

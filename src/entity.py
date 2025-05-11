"""
Entity module for Incantato game.

Provides the base Entity class for all game objects like players, enemies,
projectiles, and summons with common functionality like movement,
health management, and collision.
"""
import pygame
from config import Config as C
from ui import UI


class Entity(pygame.sprite.Sprite):
    """
    Base class for all game entities with movement, health, and rendering.

    Inherits from pygame.sprite.Sprite to enable sprite group functionality.
    """

    def __init__(self, x, y, radius, max_health, speed, color):
        """
        Initialize an entity with basic properties.

        Args:
            x: Initial x position
            y: Initial y position
            radius: Collision radius 
            max_health: Maximum health points
            speed: Movement speed in pixels per second
            color: RGB tuple for entity color
        """
        super().__init__()
        # Position and movement using Vector2
        self.pos = pygame.math.Vector2(x, y)
        self.vel = pygame.math.Vector2(0, 0)
        self.radius = radius
        self.speed = speed

        # Health
        self.max_health = max_health
        self.health = max_health

        # Visual
        self.color = color

        # Create a simple surface for default rendering
        self.image = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
        pygame.draw.circle(self.image, color, (radius, radius), radius)
        self.rect = self.image.get_rect(center=(x, y))

        # Direction as Vector2 for easier math
        self.direction = pygame.math.Vector2(1, 0)
        self.attack_radius = C.ATTACK_RADIUS

        # Internal state - we'll keep this for animation handling
        self._alive = True

        # Animation state tracking
        self.state = 'idle'
        self.animation = None  # Will be set by subclasses
        self.attack_cooldown = C.ATTACK_COOLDOWN
        self.attack_animation_timer = 0.0
        self.attack_timer = 0.0  # For attack cooldown

    @property
    def alive(self):
        """
        Check if the entity is alive.

        Returns:
            bool: True if entity is alive, False otherwise
        """
        return self._alive and self.health > 0

    @alive.setter
    def alive(self, value):
        """
        Set entity alive status.

        When set to False, automatically removes the entity from all sprite groups.

        Args:
            value: Boolean alive state
        """
        self._alive = value
        if not value:
            # Call pygame's kill method to remove from all sprite groups
            self.kill()

    @property
    def x(self):
        """Get the entity's x coordinate."""
        return self.pos.x

    @x.setter
    def x(self, value):
        """
        Set the entity's x coordinate.

        Updates both the Vector2 position and the rect.

        Args:
            value: New x position
        """
        self.pos.x = value
        self.rect.centerx = int(value)

    @property
    def y(self):
        """Get the entity's y coordinate."""
        return self.pos.y

    @y.setter
    def y(self, value):
        """
        Set the entity's y coordinate.

        Updates both the Vector2 position and the rect.

        Args:
            value: New y position
        """
        self.pos.y = value
        self.rect.centery = int(value)

    @property
    def dx(self):
        """Get the entity's x direction."""
        return self.direction.x

    @dx.setter
    def dx(self, value):
        """
        Set the entity's x direction.

        Args:
            value: New x direction
        """
        self.direction.x = value

    @property
    def dy(self):
        """Get the entity's y direction."""
        return self.direction.y

    @dy.setter
    def dy(self, value):
        """
        Set the entity's y direction.

        Args:
            value: New y direction
        """
        self.direction.y = value

    def move(self, dx, dy, dt):
        """
        Move the entity by the given delta x and y, scaled by dt.

        Handles screen boundaries to keep entity on screen.

        Args:
            dx: X movement direction (-1 to 1)
            dy: Y movement direction (-1 to 1)
            dt: Delta time in seconds since last frame
        """
        # Set direction vector (normalize if needed)
        self.dx = dx
        self.dy = dy

        if self.direction.length() > 0:
            self.direction.normalize_ip()

        # Calculate movement
        movement = self.direction * self.speed * dt

        # Apply movement and update rect
        self.pos += movement

        # Get entity boundaries
        entity_radius = self.radius
        if hasattr(self, 'animation') and self.animation:
            # Use the scaled sprite size if available
            scale = C.RENDER_SIZE / C.SPRITE_SIZE
            entity_radius = max(
                entity_radius, (self.animation.sprite_width * scale) / 2)

        # Keep entity within screen bounds
        self.pos.x = max(entity_radius, min(
            C.WIDTH - entity_radius, self.pos.x))
        self.pos.y = max(entity_radius, min(
            C.HEIGHT - entity_radius, self.pos.y))

        # Update rect position to match
        self.rect.center = (int(self.pos.x), int(self.pos.y))

    def take_damage(self, amount):
        """
        Apply damage to the entity.

        Handles death animations when health reaches zero.

        Args:
            amount: Amount of damage to apply
        """
        if not self.alive:
            return  # Don't damage dead entities

        if amount > 0:
            self.health -= amount
            if self.health <= 0:
                self.health = 0
                if hasattr(self, 'animation') and self.animation is not None:
                    # Start death animation if we have animation capabilities
                    if self.state != 'dying':
                        self.state = 'dying'
                        self.animation.set_state('dying', force_reset=True)
                        animations_length = len(
                            self.animation.config['dying']['animations'])
                        death_duration = self.animation.config['dying']['duration'] * \
                            animations_length
                        self.attack_animation_timer = death_duration
                else:
                    # For entities without animations, mark as dead immediately
                    self.alive = False  # This will call kill() through the property setter
            elif hasattr(self, 'animation') and self.animation is not None:
                # Only show hurt animation if not already in a more important state
                if self.state not in ['dying', 'sweep']:
                    self.state = 'hurt'
                    self.animation.set_state('hurt', force_reset=True)
                    animations_length = len(
                        self.animation.config['hurt']['animations'])
                    hurt_duration = self.animation.config['hurt']['duration'] * \
                        animations_length
                    self.attack_animation_timer = hurt_duration

    def heal(self, amount):
        """
        Heal the entity.

        Args:
            amount: Amount of health to restore
        """
        if not self.alive:
            return  # Don't heal dead entities

        if amount > 0:
            self.health = min(self.max_health, self.health + amount)

    def attack(self, target, damage=None):
        """
        Generic attack method for entities.

        Args:
            target: The target entity to attack
            damage: Damage amount (uses self's damage attr if None)
        """
        if hasattr(self, 'damage'):
            damage_amount = damage if damage is not None else self.damage
            target.take_damage(damage_amount)
        else:
            # Default minimal damage if no damage attribute exists
            target.take_damage(1)

    def get_distance_to(self, other_x, other_y):
        """
        Calculate distance to another point.

        Args:
            other_x: Target x coordinate
            other_y: Target y coordinate

        Returns:
            float: Distance to the point
        """
        return self.pos.distance_to(pygame.math.Vector2(other_x, other_y))

    def get_direction_to(self, target_x, target_y):
        """
        Calculate direction to a target point, normalized.

        Args:
            target_x: Target x coordinate
            target_y: Target y coordinate

        Returns:
            tuple: Normalized (dx, dy) direction vector
        """
        direction = pygame.math.Vector2(
            target_x - self.pos.x, target_y - self.pos.y)
        if direction.length() > 0:
            direction.normalize_ip()
        return direction.x, direction.y

    def update_animation(self, dt):
        """
        Update animation state based on timers.

        Handles dying, hurt, and attack animations.

        Args:
            dt: Delta time in seconds since last frame
        """
        if hasattr(self, 'animation') and self.animation is not None:
            # Handle dying animation
            if not self.alive and self.state == 'dying':
                self.animation.update(dt)
                if self.attack_animation_timer > 0:
                    self.attack_animation_timer -= dt
                    if self.attack_animation_timer <= 0:
                        # Actually kill the entity when animation completes
                        self.alive = False
                return

            # Handle action animations (hurt/attack)
            if self.state in ['hurt', 'sweep']:
                self.attack_animation_timer -= dt
                self.animation.update(dt)

                # If animation is done, return to idle state
                if self.attack_animation_timer <= 0:
                    if self.health <= 0:
                        self.state = 'dying'
                        self.animation.set_state('dying', force_reset=True)
                        animations_length = len(
                            self.animation.config['dying']['animations'])
                        death_duration = self.animation.config['dying']['duration'] * \
                            animations_length
                        self.attack_animation_timer = death_duration
                    else:
                        self.state = 'idle'
                        self.animation.set_state('idle', force_reset=True)
            else:
                # Regular animation update
                self.animation.update(dt, self.dx, self.dy)

    def draw(self, screen):
        """
        Draw the entity on the screen.

        Renders the sprite animation if available, otherwise draws a circle.
        Also draws hitbox, attack radius, and health bar.

        Args:
            screen: Pygame surface to draw on
        """
        if not self.alive and (not hasattr(self, 'animation') or self.state != 'dying'):
            return  # Don't draw dead entities unless they're in dying animation

        # Draw hitbox - always visible for debugging
        hitbox_color = (*self.color, 100)  # Semi-transparent
        pygame.draw.circle(screen, hitbox_color, (int(
            self.pos.x), int(self.pos.y)), self.radius)
        # Draw hitbox outline
        pygame.draw.circle(screen, self.color, (int(
            self.pos.x), int(self.pos.y)), self.radius, 2)

        # If we have an animation, use it
        if hasattr(self, 'animation') and self.animation is not None:
            current_sprite = self.animation.get_current_sprite()
            if current_sprite:
                # Use consistent scale factor
                scale = C.RENDER_SIZE / C.SPRITE_SIZE

                # Calculate scaled dimensions
                scaled_width = self.animation.sprite_width * scale
                scaled_height = self.animation.sprite_height * scale

                # Calculate top-left position for blitting (center the sprite)
                draw_x = self.pos.x - scaled_width / 2
                draw_y = self.pos.y - scaled_height / 2

                # Scale sprite if needed
                if scale != 1:
                    scaled_sprite = pygame.transform.scale(current_sprite,
                                                           (int(scaled_width),
                                                            int(scaled_height)))
                    # Draw the sprite
                    screen.blit(scaled_sprite, (int(draw_x), int(draw_y)))
                else:
                    # Draw without scaling if scale is 1
                    screen.blit(current_sprite, (int(draw_x), int(draw_y)))
            else:
                # Fallback to circle if sprite is not available
                pygame.draw.circle(screen, self.color,
                                   (int(self.pos.x), int(self.pos.y)), self.radius)
        else:
            # Draw the entity circle (fallback if no animation)
            pygame.draw.circle(screen, self.color,
                               (int(self.pos.x), int(self.pos.y)), self.radius)

        # # Draw attack radius if set
        # if hasattr(self, 'attack_radius') and self.attack_radius > 0:
        #     # Create a transparent surface for the attack radius indicator
        #     radius_surf = pygame.Surface(
        #         (self.attack_radius * 2, self.attack_radius * 2), pygame.SRCALPHA)
        #     # Draw a semi-transparent circle for the attack radius
        #     pygame.draw.circle(radius_surf, (*self.color, 40),
        #                        (self.attack_radius, self.attack_radius), self.attack_radius)
        #     # Draw circle outline
        #     pygame.draw.circle(radius_surf, (*self.color, 100),
        #                        (self.attack_radius, self.attack_radius), self.attack_radius, 2)
        #     # Blit the radius surface to the screen
        #     screen.blit(radius_surf, (int(
        #         self.pos.x - self.attack_radius), int(self.pos.y - self.attack_radius)))

        # Draw health bar if entity is alive or in dying animation
        if self.alive or (hasattr(self, 'animation') and self.state == 'dying'):
            self.draw_health_bar(screen)

    def draw_health_bar(self, surf):
        """
        Draw a health bar above the entity.

        Shows current health as a proportion of max health.

        Args:
            surf: Pygame surface to draw on
        """
        # Add HP bar
        bar_x = self.x - 25
        bar_y = self.y - self.radius - 10
        UI.draw_hp_bar(
            surf,
            bar_x,
            bar_y,
            self.health,
            self.max_health,
            self.color)

    def update(self, dt):
        """
        Update entity state.

        Updates animation and attack timers. Checks for death conditions.

        Args:
            dt: Delta time in seconds since last frame
        """
        # Update animation if available
        if hasattr(self, 'animation') and self.animation is not None:
            self.update_animation(dt)

        # Update attack timer
        if hasattr(self, 'attack_timer') and self.attack_timer > 0:
            self.attack_timer -= dt

        # Implement basic check - if health is zero, mark as dead
        if self.health <= 0 and self.alive:
            if not hasattr(self, 'animation') or self.animation is None:
                self.alive = False

        # Update rect position to match vector position
        self.rect.center = (int(self.pos.x), int(self.pos.y))

import pygame
import math
from config import Config as C


class Entity(pygame.sprite.Sprite):
    def __init__(self, x, y, radius, max_health, speed, color, attack_radius=0):
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

        # Direction
        self.direction = pygame.math.Vector2(1, 0)
        self.attack_radius = attack_radius
        
        # Internal state - we'll keep this for animation handling
        self._alive = True

    @property
    def alive(self):
        return self._alive and self.health > 0
        
    @alive.setter
    def alive(self, value):
        self._alive = value
        if not value:
            # Call pygame's kill method to remove from all sprite groups
            self.kill()

    @property
    def x(self):
        return self.pos.x
        
    @x.setter
    def x(self, value):
        self.pos.x = value
        self.rect.centerx = int(value)
        
    @property
    def y(self):
        return self.pos.y
        
    @y.setter
    def y(self, value):
        self.pos.y = value
        self.rect.centery = int(value)
        
    @property
    def dx(self):
        return self.direction.x
        
    @dx.setter
    def dx(self, value):
        self.direction.x = value
        
    @property
    def dy(self):
        return self.direction.y
        
    @dy.setter
    def dy(self, value):
        self.direction.y = value

    def move(self, dx, dy, dt):
        """Move the entity by the given delta x and y, scaled by dt (delta time)"""
        # Calculate new position using Vector2
        self.direction.x = dx
        self.direction.y = dy
        
        if self.direction.length() > 0:
            self.direction.normalize_ip()
        
        movement = self.direction * self.speed * dt
        new_pos = self.pos + movement

        # Keep entity within screen bounds
        self.pos.x = max(self.radius, min(C.WIDTH - self.radius, new_pos.x))
        self.pos.y = max(self.radius, min(C.HEIGHT - self.radius, new_pos.y))
        
        # Update rect position to match
        self.rect.center = (int(self.pos.x), int(self.pos.y))

    def take_damage(self, amount):
        """Apply damage to the entity"""
        if not self.alive:
            return  # Don't damage dead entities
            
        if amount > 0:
            self.health -= amount
            if self.health <= 0:
                self.health = 0
                # For entities without animations, mark as dead immediately 
                if not hasattr(self, 'animation'):
                    self.alive = False  # This will call kill() through the property setter

    def heal(self, amount):
        """Heal the entity"""
        if not self.alive:
            return  # Don't heal dead entities
            
        if amount > 0:
            self.health = min(self.max_health, self.health + amount)

    def draw(self, screen):
        """Draw the entity on the screen"""
        if not self.alive:
            return  # Don't draw dead entities
            
        # Draw the entity circle (fallback if image not set)
        if not hasattr(self, 'image') or self.image is None:
            pygame.draw.circle(screen, self.color,
                                (int(self.pos.x), int(self.pos.y)), self.radius)
        else:
            screen.blit(self.image, self.rect)

        # Draw attack radius if debug is enabled and attack radius is set
        if self.attack_radius > 0:
            # Create a transparent surface for the attack radius indicator
            radius_surf = pygame.Surface(
                (self.attack_radius * 2, self.attack_radius * 2), pygame.SRCALPHA)
            # Draw a semi-transparent circle for the attack radius
            pygame.draw.circle(radius_surf, (*self.color, 40),
                                (self.attack_radius, self.attack_radius), self.attack_radius)
            # Draw circle outline
            pygame.draw.circle(radius_surf, (*self.color, 100),
                                (self.attack_radius, self.attack_radius), self.attack_radius, 2)
            # Blit the radius surface to the screen
            screen.blit(radius_surf, (int(
                self.pos.x - self.attack_radius), int(self.pos.y - self.attack_radius)))

        # Draw health bar
        self.draw_health_bar(screen)

    def draw_health_bar(self, screen):
        """Draw health bar above the entity"""
        bar_width = self.radius * 2
        bar_height = 5
        bar_x = self.pos.x - self.radius
        bar_y = self.pos.y - self.radius - 10

        # Background (red)
        pygame.draw.rect(screen, (255, 0, 0),
                         (bar_x, bar_y, bar_width, bar_height))

        # Foreground (green)
        health_width = (self.health / self.max_health) * bar_width
        if health_width > 0:
            pygame.draw.rect(screen, (0, 255, 0),
                             (bar_x, bar_y, health_width, bar_height))

    def update(self, dt):
        """Update method to be overridden by child classes"""
        # Implement basic check - if health is zero, mark as dead
        if self.health <= 0 and self.alive:
            self.alive = False

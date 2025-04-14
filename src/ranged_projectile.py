# ranged_projectile.py
import pygame
import math

class RangedProjectile:
    """Projectile fired by ranged enemies."""
    def __init__(self, x, y, target_x, target_y, speed, damage, color):
        self.x = x
        self.y = y
        self.radius = 5
        self.speed = speed
        self.damage = damage
        self.color = color
        self.active = True
        
        # Calculate direction
        dx = target_x - x
        dy = target_y - y
        dist = math.hypot(dx, dy)
        if dist == 0:
            self.vx, self.vy = 0, 0
        else:
            self.vx = (dx / dist) * speed
            self.vy = (dy / dist) * speed
    
    def update(self, dt):
        """Update projectile position."""
        self.x += self.vx * dt
        self.y += self.vy * dt
        
        # Deactivate if out of screen
        if (self.x < 0 or self.x > 1028 or  # Using WIDTH from config
            self.y < 0 or self.y > 720):    # Using HEIGHT from config
            self.active = False
    
    def check_collision(self, entity):
        """Check if projectile hit an entity."""
        dist = math.hypot(entity.x - self.x, entity.y - self.y)
        if dist < (entity.radius + self.radius):
            entity.take_damage(self.damage)
            self.active = False
            return True
        return False
    
    def draw(self, surf):
        """Draw the projectile."""
        pygame.draw.circle(
            surf, self.color, (int(self.x), int(self.y)), self.radius)
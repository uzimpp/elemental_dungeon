import pygame
import math
from config import WIDTH, HEIGHT

class Entity:
    def __init__(self, x, y, radius, max_health, speed, color):
        # Position and movement
        self.x = x
        self.y = y
        self.radius = radius
        self.speed = speed
        
        # Health
        self.max_health = max_health
        self.health = max_health
        
        # Visual
        self.color = color
        
        # State
        self.alive = True

    def move(self, dx, dy, dt):
        """Move the entity by the given delta x and y, scaled by dt (delta time)"""
        new_x = self.x + dx * self.speed * dt
        new_y = self.y + dy * self.speed * dt
        
        # Keep entity within screen bounds
        self.x = max(self.radius, min(WIDTH - self.radius, new_x))
        self.y = max(self.radius, min(HEIGHT - self.radius, new_y))

    def take_damage(self, amount):
        """Apply damage to the entity"""
        if amount > 0:
            self.health -= amount
            if self.health <= 0:
                self.health = 0
                self.alive = False

    def heal(self, amount):
        """Heal the entity"""
        if amount > 0:
            self.health = min(self.max_health, self.health + amount)

    def is_colliding_with(self, other):
        """Check if this entity is colliding with another entity"""
        distance = self.get_distance_to(other.x, other.y)
        return distance < (self.radius + other.radius)

    def draw(self, screen):
        """Draw the entity on the screen"""
        if self.alive:
            # Draw the entity circle
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
            
            # Draw health bar
            self.draw_health_bar(screen)

    def draw_health_bar(self, screen):
        """Draw health bar above the entity"""
        bar_width = self.radius * 2
        bar_height = 5
        bar_x = self.x - self.radius
        bar_y = self.y - self.radius - 10
        
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
        pass 
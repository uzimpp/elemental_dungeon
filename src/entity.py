import pygame
import math
from config import WIDTH, HEIGHT
from entity_state import EntityStateMachine
from resources import Resources


class Entity:
    def __init__(self, x, y, radius, max_health, speed, attack_radius=0):
        # Get resources
        self.resources = Resources.get_instance()
        
        # Position and movement
        self.x = x
        self.y = y
        self.radius = radius
        self.speed = speed

        # Health
        self.max_health = max_health
        self.health = max_health

        # State
        self.alive = True

        # Direction
        self.dx = 1
        self.dy = 0
        self.attack_radius = attack_radius
        
        # Create state machine
        self.state_machine = EntityStateMachine(self)
        
        # For entities without animation
        if not hasattr(self, 'animation'):
            self.state_machine.change_state("none")

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
                self.state_machine.change_state("dying")
            else:
                # Only transition to hurt if not in a more important state
                current_state = self.state_machine.get_state_name()
                if current_state not in ["dying", "sweep"]:
                    self.state_machine.change_state("hurt")

    def heal(self, amount):
        """Heal the entity"""
        if amount > 0:
            self.health = min(self.max_health, self.health + amount)

    def draw(self, screen):
        """Draw the entity on the screen"""
        if self.alive:
            # If the entity has an animation, it will be drawn by the child class
            # Otherwise, draw a basic circle
            if not hasattr(self, 'animation'):
                # Default color if not specified
                self.color = getattr(self, 'color', (255, 0, 0))
                # Draw the entity circle
                pygame.draw.circle(screen, self.color,
                                  (int(self.x), int(self.y)), self.radius)

            # Draw attack radius if debug is enabled and attack radius is set
            if self.attack_radius > 0:
                # Default color if not specified
                self.color = getattr(self, 'color', (255, 0, 0))
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
                    self.x - self.attack_radius), int(self.y - self.attack_radius)))

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
        # Update the state machine
        self.state_machine.update(dt, dx=self.dx, dy=self.dy)

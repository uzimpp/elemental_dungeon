"""
Visual effects module for Incantato game.

Provides various visual effects including explosions, healing,
slash attacks, and chain lightning effects using Pygame surfaces.
"""
import math
import random
import time

import pygame
from config import Config as C


class VisualEffect:
    """
    Visual effect class for rendering various special effects in the game.

    Supports different effect types including explosions, healing, slashes,
    and connecting lines for chain attacks.
    """

    def __init__(
            self,
            x,
            y,
            effect_type,
            color,
            radius=30,
            duration=0.3,
            start_angle=0,
            sweep_angle=math.pi / 3,
            end_x=None,
            end_y=None):
        """
        Initialize a visual effect.

        Args:
            x: X-coordinate of the effect's center
            y: Y-coordinate of the effect's center
            effect_type: Type of effect ("explosion", "heal", "slash", "line")
            color: RGB tuple for the effect's color
            radius: Size of the effect
            duration: How long the effect lasts in seconds
            start_angle: Starting angle for directional effects (in radians)
            sweep_angle: Angular size of arc effects (in radians)
            end_x: End X-coordinate for line effects
            end_y: End Y-coordinate for line effects
        """
        self.x = x
        self.y = y
        self.effect_type = effect_type
        self.color = color
        self.radius = radius
        self.duration = duration
        self.start_time = pygame.time.get_ticks() / 1000.0
        self.active = True
        self.alpha = 255
        self.current_size = 0
        self.start_angle = start_angle
        self.sweep_angle = sweep_angle
        self.angle = 0
        self.particles = []
        self.end_x = end_x
        self.end_y = end_y

        # Generate initial particles for some effect types
        if effect_type == "explosion":
            for _ in range(20):
                angle = random.uniform(0, 2 * math.pi)
                distance = random.uniform(0, radius * 0.8)
                self.particles.append({
                    'x': distance * math.cos(angle),
                    'y': distance * math.sin(angle),
                    'alpha': random.randint(150, 255),
                    'size': random.randint(2, 4)
                })
        elif effect_type == "line" and end_x is not None and end_y is not None:
            # Generate particles along the line
            line_length = math.hypot(end_x - x, end_y - y)
            num_particles = int(line_length / 5)  # One particle every 5 pixels
            for i in range(num_particles):
                t = i / max(1, num_particles - 1)
                px = x + t * (end_x - x)
                py = y + t * (end_y - y)
                self.particles.append({
                    'x': px,
                    'y': py,
                    'alpha': random.randint(150, 255),
                    'size': random.randint(2, 4),
                    'offset_x': random.uniform(-3, 3),
                    'offset_y': random.uniform(-3, 3)
                })

    def update(self, dt):
        """
        Update the visual effect state based on elapsed time.

        Args:
            dt: Delta time in seconds since last update

        Returns:
            bool: True if the effect is still active, False if it should be removed
        """
        # Calculate elapsed time
        current_time = pygame.time.get_ticks() / 1000.0
        elapsed = current_time - self.start_time
        progress = elapsed / self.duration

        if progress >= 1.0:
            self.active = False
            return self.active

        # Common fade out
        self.alpha = 255 * (1 - progress)

        if self.effect_type == "explosion":
            # Simple expanding circle
            self.current_size = self.radius * min(1.0, progress * 2.0)

        elif self.effect_type == "heal":
            # Rising effect
            self.y -= dt * 50

        elif self.effect_type == "slash":
            self.angle = self.sweep_angle * progress

            if progress < 0.5:
                for _ in range(2):
                    particle_angle = self.start_angle + self.angle * random.random()
                    r = random.uniform(0.7, 1.0) * self.radius
                    px = r * math.cos(particle_angle)
                    py = r * math.sin(particle_angle)
                    self.particles.append({
                        'x': px,
                        'y': py,
                        'alpha': 255,
                        'size': random.randint(2, 4)
                    })

            for p in self.particles:
                p['alpha'] = max(0, p['alpha'] - 10)
            self.particles = [p for p in self.particles if p['alpha'] > 0]

        elif self.effect_type == "line":
            for p in self.particles:
                fade_speed = random.uniform(10, 25)
                p['alpha'] = max(0, p['alpha'] - fade_speed * dt * 60)

                # Add some subtle movement to particles
                p['x'] += random.uniform(-1, 1) * dt * 20
                p['y'] += random.uniform(-1, 1) * dt * 20

            # Remove faded particles
            self.particles = [p for p in self.particles if p['alpha'] > 0]

        return self.active

    def draw(self, surf):
        """
        Draw the visual effect on the screen.

        Args:
            surf: Pygame surface to draw on
        """
        if not self.active:
            return

        if self.effect_type == "explosion":
            # Draw expanding circle with decreasing alpha
            temp_surf = pygame.Surface(
                (self.current_size * 2, self.current_size * 2), pygame.SRCALPHA)

            # Draw main glow
            glow_alpha = min(self.alpha, 100)
            glow_color = (*self.color, glow_alpha)
            pygame.draw.circle(temp_surf, glow_color,
                               (self.current_size, self.current_size), self.current_size)

            # Draw center with higher opacity
            center_color = (*self.color, min(self.alpha, 180))
            center_size = self.current_size * 0.6
            pygame.draw.circle(temp_surf, center_color,
                               (self.current_size, self.current_size), center_size)

            # Draw particles
            for p in self.particles:
                particle_color = (*self.color, min(p['alpha'], self.alpha))
                pygame.draw.circle(temp_surf, particle_color,
                                   (int(self.current_size +
                                    p['x']), int(self.current_size + p['y'])),
                                   p['size'])

            # Blit the effect to the main surface
            surf.blit(temp_surf, (int(self.x - self.current_size),
                      int(self.y - self.current_size)))

        elif self.effect_type == "heal":
            # Draw rising particles with decreasing alpha
            for i in range(5):
                particle_y_offset = i * 5
                particle_size = 4 - i * 0.5
                particle_alpha = min(self.alpha * (1 - i/5), 255)
                particle_color = (*self.color, particle_alpha)

                pygame.draw.circle(surf, particle_color,
                                   (int(self.x), int(self.y + particle_y_offset)),
                                   max(1, int(particle_size)))

            # Draw a transparent glow
            glow_surf = pygame.Surface(
                (self.radius * 2, self.radius * 2), pygame.SRCALPHA)
            glow_color = (*self.color, min(self.alpha * 0.5, 100))
            pygame.draw.circle(glow_surf, glow_color,
                               (self.radius, self.radius), self.radius)
            surf.blit(glow_surf, (int(self.x - self.radius),
                      int(self.y - self.radius)))

        elif self.effect_type == "slash":
            # Draw arc
            arc_surf = pygame.Surface(
                (self.radius * 2, self.radius * 2), pygame.SRCALPHA)

            # Draw inner glow for the arc
            arc_color = (*self.color, min(self.alpha * 0.7, 180))
            pygame.draw.arc(arc_surf, arc_color,
                            (0, 0, self.radius * 2, self.radius * 2),
                            self.start_angle, self.start_angle + self.angle, width=int(self.radius * 0.6))

            # Draw outer edge with higher opacity
            edge_color = (*self.color, min(self.alpha, 255))
            pygame.draw.arc(arc_surf, edge_color,
                            (0, 0, self.radius * 2, self.radius * 2),
                            self.start_angle, self.start_angle + self.angle, width=3)

            # Draw particles
            for p in self.particles:
                particle_color = (*self.color, min(p['alpha'], self.alpha))
                pygame.draw.circle(arc_surf, particle_color,
                                   (int(self.radius + p['x']),
                                    int(self.radius + p['y'])),
                                   p['size'])

            surf.blit(arc_surf, (int(self.x - self.radius),
                      int(self.y - self.radius)))

        elif self.effect_type == "line" and self.end_x is not None and self.end_y is not None:
            # Draw line connecting two points
            line_color = (*self.color, min(self.alpha, 200))
            pygame.draw.line(surf, line_color,
                             (int(self.x), int(self.y)),
                             (int(self.end_x), int(self.end_y)),
                             width=2)

            # Draw glow along the line
            for p in self.particles:
                if 'alpha' in p and p['alpha'] > 0:
                    particle_color = (*self.color, min(p['alpha'], self.alpha))

                    # Get position from particle with any offset
                    pos_x = p['x'] + p.get('offset_x', 0)
                    pos_y = p['y'] + p.get('offset_y', 0)

                    pygame.draw.circle(surf, particle_color,
                                       (int(pos_x), int(pos_y)),
                                       p.get('size', 2))


class DashAfterimage:
    """
    Visual effect that creates a fading afterimage when the player dashes.

    Renders a ghost-like trail of the player's sprite with decreasing opacity.
    """

    def __init__(self, x, y, sprite, duration=0.2, start_alpha=150):
        """
        Initialize a dash afterimage effect.

        Args:
            x: X-coordinate of the afterimage
            y: Y-coordinate of the afterimage
            sprite: The sprite to render as an afterimage
            duration: How long the afterimage lasts in seconds
            start_alpha: Initial alpha transparency value (0-255)
        """
        self.x = x
        self.y = y
        self.original_sprite = sprite
        self.duration = duration
        self.start_time = pygame.time.get_ticks() / 1000.0
        self.active = True
        self.alpha = start_alpha

        # Create a copy of the sprite with alpha
        self.sprite = sprite.copy()

    def update(self, dt):
        """
        Update the afterimage effect state.

        Args:
            dt: Delta time in seconds since last update

        Returns:
            bool: True if the effect is still active, False if it should be removed
        """
        # Calculate elapsed time and progress
        current_time = pygame.time.get_ticks() / 1000.0
        elapsed = current_time - self.start_time
        progress = elapsed / self.duration

        if progress >= 1.0:
            self.active = False
            return False

        # Decrease alpha based on progress (faster fade at beginning)
        self.alpha = int(150 * (1 - progress))

        return True

    def draw(self, surf):
        """
        Draw the afterimage on the screen.

        Args:
            surf: Pygame surface to draw on
        """
        if not self.active:
            return

        # Create a copy with the current alpha value
        temp_sprite = self.original_sprite.copy()
        temp_sprite.set_alpha(self.alpha)

        # Draw sprite at position
        surf.blit(temp_sprite, (int(self.x - temp_sprite.get_width() / 2),
                                int(self.y - temp_sprite.get_height() / 2)))

    def is_ground_effect(self):
        """
        Check if this is a ground effect (drawn below entities).

        Returns:
            bool: True, as afterimages should be drawn below the player
        """
        return True

# visual_effects.py
import time
import math
import pygame
import random


class VisualEffect:
    def __init__(
            self,
            x,
            y,
            effect_type,
            color,
            radius=30,
            duration=0.3,
            start_angle=0,
            sweep_angle=math.pi /
            3):
        self.x = x
        self.y = y
        self.effect_type = effect_type
        self.color = color
        self.radius = radius
        self.duration = duration
        self.start_time = time.time()
        self.active = True

        # Animation variables
        self.current_size = 0
        self.alpha = 255
        self.angle = 0

        # Slash specific variables
        if effect_type == "slash":
            self.slash_width = 4  # Wider line for slash
            self.particles = []  # Particles for slash trail
            self.start_angle = start_angle + math.pi / 6
            self.sweep_angle = sweep_angle

    def update(self, dt):
        elapsed = time.time() - self.start_time
        progress = elapsed / self.duration

        if progress >= 1.0:
            self.active = False
            return

        # Common fade out
        self.alpha = 255 * (1 - progress)

        if self.effect_type == "explosion":
            # Simple expanding circle
            self.current_size = self.radius * min(1.0, progress * 2.0)

        elif self.effect_type == "heal":
            # Rising effect
            self.y -= dt * 50

        elif self.effect_type == "slash":
            # Enhanced slash animation
            self.angle = self.sweep_angle * progress  # Wider sweep

            # Add particles along the arc
            if progress < 0.5:  # Only add particles in first half of animation
                for _ in range(2):  # Add 2 particles per frame
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

            # Update existing particles
            for p in self.particles:
                p['alpha'] = max(0, p['alpha'] - 10)

            # Remove faded particles
            self.particles = [p for p in self.particles if p['alpha'] > 0]

    def draw(self, surf):
        if not self.active:
            return

        # Create a surface for transparency
        effect_surf = pygame.Surface(
            (self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        center = (self.radius, self.radius)

        if self.effect_type == "explosion":
            # Draw expanding circle
            alpha_color = (*self.color, int(self.alpha))
            pygame.draw.circle(
                effect_surf, alpha_color, center, int(
                    self.current_size))

        elif self.effect_type == "heal":
            # Draw healing particles
            alpha_color = (*self.color, int(self.alpha))
            pygame.draw.circle(effect_surf, alpha_color, center, 5)

        elif self.effect_type == "slash":
            # Draw main slash arc
            alpha_color = (*self.color, int(self.alpha))
            rect = (0, 0, self.radius * 2, self.radius * 2)
            pygame.draw.arc(effect_surf, alpha_color, rect,
                            self.start_angle, self.start_angle + self.angle,
                            self.slash_width)

            # Draw particles
            for p in self.particles:
                particle_color = (*self.color, int(p['alpha']))
                particle_pos = (center[0] + p['x'], center[1] + p['y'])
                pygame.draw.circle(
                    effect_surf, particle_color, (int(
                        particle_pos[0]), int(
                        particle_pos[1])), p['size'])

            # Draw inner arc (for more visibility)
            inner_rect = (
                self.radius / 2,
                self.radius / 2,
                self.radius,
                self.radius)
            pygame.draw.arc(effect_surf, alpha_color, inner_rect,
                            self.start_angle, self.start_angle + self.angle,
                            max(1, self.slash_width - 2))

        # Draw the effect
        surf.blit(effect_surf, (self.x - self.radius, self.y - self.radius))


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

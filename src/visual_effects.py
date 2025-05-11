# visual_effects.py
import time
import math
import pygame
import random


class VisualEffectManager:
    """Manages visual effects for a game instance"""
    def __init__(self):
        self.effects = []

    def add_effect(self, effect):
        """Add a new visual effect"""
        self.effects.append(effect)

    def update(self, dt):
        """Update all active effects"""
        self.effects = [effect for effect in self.effects if effect.active]
        for effect in self.effects:
            effect.update(dt)

    def draw(self, surface):
        """Draw all active effects"""
        for effect in self.effects:
            effect.draw(surface)

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
            sweep_angle=math.pi / 3,
            end_x=None,
            end_y=None):
        self.x = x
        self.y = y
        self.effect_type = effect_type
        self.color = color
        self.radius = radius
        self.duration = duration
        self.start_time = time.time()
        self.active = True
        self.end_x = end_x
        self.end_y = end_y

        # Animation variables
        self.current_size = 0
        self.alpha = 255
        self.angle = 0

        # Initialize effect-specific properties
        self._init_effect_properties()

    def _init_effect_properties(self):
        """Initialize properties specific to each effect type"""
        if self.effect_type == "slash":
            self.slash_width = 4
            self.particles = []
            self.start_angle = self.start_angle
            self.sweep_angle = self.sweep_angle
        elif self.effect_type == "line":
            self.line_width = self.radius
            self.particles = []
            if self.end_x is not None and self.end_y is not None:
                self._init_line_particles()

    def _init_line_particles(self):
        """Initialize particles for line effects"""
        num_particles = 15
        for i in range(num_particles):
            t = i / (num_particles - 1)
            px = self.x + (self.end_x - self.x) * t
            py = self.y + (self.end_y - self.y) * t
            jitter = 5
            px += random.uniform(-jitter, jitter)
            py += random.uniform(-jitter, jitter)
            self.particles.append({
                'x': px,
                'y': py,
                'alpha': 255,
                'size': random.randint(2, 5)
            })

    def update(self, dt):
        """Update effect state"""
        elapsed = time.time() - self.start_time
        progress = elapsed / self.duration

        if progress >= 1.0:
            self.active = False
            return

        self.alpha = 255 * (1 - progress)
        self._update_effect_specific(progress, dt)

    def _update_effect_specific(self, progress, dt):
        """Update effect-specific properties"""
        if self.effect_type == "explosion":
            self.current_size = self.radius * min(1.0, progress * 2.0)
        elif self.effect_type == "heal":
            self.y -= dt * 50
        elif self.effect_type == "slash":
            self._update_slash(progress)
        elif self.effect_type == "line":
            self._update_line(progress)

    def _update_slash(self, progress):
        """Update slash-specific properties"""
        self.angle = self.sweep_angle * progress
        if progress < 0.5:
            self._add_slash_particles()
        self._update_particles()

    def _update_line(self, progress):
        """Update line-specific properties"""
        self._update_particles()
        if progress < 0.7 and self.end_x is not None and self.end_y is not None:
            self._add_line_particles()

    def _add_slash_particles(self):
        """Add particles for slash effect"""
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

    def _add_line_particles(self):
        """Add particles for line effect"""
        for _ in range(3):
            t = random.random()
            px = self.x + (self.end_x - self.x) * t
            py = self.y + (self.end_y - self.y) * t
            jitter = 8
            px += random.uniform(-jitter, jitter)
            py += random.uniform(-jitter, jitter)
            self.particles.append({
                'x': px,
                'y': py,
                'alpha': 200 + random.randint(0, 55),
                'size': random.randint(2, 5)
            })

    def _update_particles(self):
        """Update all particles"""
        for p in self.particles:
            p['alpha'] = max(0, p['alpha'] - 10)
            if self.effect_type == "line":
                p['x'] += random.uniform(-2, 2)
                p['y'] += random.uniform(-2, 2)
        self.particles = [p for p in self.particles if p['alpha'] > 0]

    def draw(self, surface):
        """Draw the effect"""
        if not self.active:
            return

        if self.effect_type == "explosion":
            self._draw_explosion(surface)
        elif self.effect_type == "heal":
            self._draw_heal(surface)
        elif self.effect_type == "slash":
            self._draw_slash(surface)
        elif self.effect_type == "line":
            self._draw_line(surface)

    def _draw_explosion(self, surface):
        """Draw explosion effect"""
        effect_surf = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        center = (self.radius, self.radius)
        alpha_color = (*self.color, int(self.alpha))
        pygame.draw.circle(effect_surf, alpha_color, center, int(self.current_size))
        surface.blit(effect_surf, (self.x - self.radius, self.y - self.radius))

    def _draw_heal(self, surface):
        """Draw heal effect"""
        effect_surf = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        center = (self.radius, self.radius)
        alpha_color = (*self.color, int(self.alpha))
        pygame.draw.circle(effect_surf, alpha_color, center, 5)
        surface.blit(effect_surf, (self.x - self.radius, self.y - self.radius))

    def _draw_slash(self, surface):
        """Draw slash effect"""
        effect_surf = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        center = (self.radius, self.radius)
        alpha_color = (*self.color, int(self.alpha))
        
        # Draw main arc
        rect = (0, 0, self.radius * 2, self.radius * 2)
        pygame.draw.arc(effect_surf, alpha_color, rect,
                       self.start_angle, self.start_angle + self.angle,
                       self.slash_width)

        # Draw particles
        for p in self.particles:
            particle_color = (*self.color, int(p['alpha']))
            particle_pos = (center[0] + p['x'], center[1] + p['y'])
            pygame.draw.circle(effect_surf, particle_color, 
                             (int(particle_pos[0]), int(particle_pos[1])), 
                             p['size'])

        # Draw inner arc
        inner_rect = (self.radius / 2, self.radius / 2, self.radius, self.radius)
        pygame.draw.arc(effect_surf, alpha_color, inner_rect,
                       self.start_angle, self.start_angle + self.angle,
                       max(1, self.slash_width - 2))
        
        surface.blit(effect_surf, (self.x - self.radius, self.y - self.radius))

    def _draw_line(self, surface):
        """Draw line effect"""
        if self.end_x is None or self.end_y is None:
            return

        # Draw main line
        alpha_color = (*self.color, int(self.alpha * 0.7))
        pygame.draw.line(surface, alpha_color, 
                        (int(self.x), int(self.y)),
                        (int(self.end_x), int(self.end_y)), 
                        max(1, int(self.line_width * 0.3)))

        # Draw particles
        for p in self.particles:
            particle_color = (*self.color, int(p['alpha']))
            pygame.draw.circle(surface, particle_color, 
                             (int(p['x']), int(p['y'])), 
                             p['size'])

        # Draw glow
        for i in range(3):
            glow_alpha = int(self.alpha * (0.3 - i * 0.1))
            glow_color = (*self.color, glow_alpha)
            glow_width = int(self.line_width * (0.5 + i * 0.5))
            pygame.draw.line(surface, glow_color,
                           (int(self.x), int(self.y)),
                           (int(self.end_x), int(self.end_y)),
                           glow_width)


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

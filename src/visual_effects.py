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
        self.end_x = end_x  # For line effect
        self.end_y = end_y  # For line effect

        # Animation variables
        self.current_size = 0
        self.alpha = 255
        self.angle = 0

        # Slash specific variables
        if effect_type == "slash":
            self.slash_width = 4  # Wider line for slash
            self.particles = []  # Particles for slash trail
            self.start_angle = start_angle
            self.sweep_angle = sweep_angle
        # Line specific variables (for chain lightning)
        if effect_type == "line":
            self.line_width = radius  # Use radius as line width
            self.particles = []  # Particles along the line

            # Generate initial particles if we have end coordinates
            if self.end_x is not None and self.end_y is not None:
                num_particles = 15  # Number of particles along the line
                for i in range(num_particles):
                    t = i / (num_particles - 1)  # Interpolation factor
                    px = x + (self.end_x - x) * t
                    py = y + (self.end_y - y) * t
                    jitter = 5  # Randomize slightly for more organic look
                    px += random.uniform(-jitter, jitter)
                    py += random.uniform(-jitter, jitter)
                    self.particles.append({
                        'x': px,
                        'y': py,
                        'alpha': 255,
                        'size': random.randint(2, 5)
                    })

    def update(self, dt):
        elapsed = time.time() - self.start_time
        progress = elapsed / self.duration

        if progress >= 1.0:
            self.active = False
            return self.active  # Effect is done

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
            if progress < 0.05:
                pass  # Keep print minimal
                # print(
                #     f"[VisualEffect] Slash animation beginning - Start: {math.degrees(self.start_angle):.1f}°, Current: {math.degrees(self.start_angle + self.angle):.1f}°, End: {math.degrees(self.start_angle + self.sweep_angle):.1f}°")
            elif 0.45 < progress < 0.55:
                pass  # Keep print minimal
                # print(
                #     f"[VisualEffect] Slash animation midpoint - Current angle: {math.degrees(self.start_angle + self.angle):.1f}°")

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
                p['alpha'] = max(0, p['alpha'] - fade_speed)
                jitter = 2
                p['x'] += random.uniform(-jitter, jitter)
                p['y'] += random.uniform(-jitter, jitter)
            self.particles = [p for p in self.particles if p['alpha'] > 0]

            if progress < 0.7 and self.end_x is not None and self.end_y is not None:
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
        return self.active  # Effect is still active

    def draw(self, surf):
        if not self.active:
            return

        if self.effect_type == "explosion":
            # Draw expanding circle
            alpha_color = (*self.color, int(self.alpha))
            # Create a surface for transparency
            effect_surf = pygame.Surface(
                (self.radius * 2, self.radius * 2), pygame.SRCALPHA)
            center = (self.radius, self.radius)
            pygame.draw.circle(effect_surf, alpha_color,
                               center, int(self.current_size))
            surf.blit(effect_surf, (self.x - self.radius, self.y - self.radius))

        elif self.effect_type == "heal":
            # Draw healing particles
            # Create a surface for transparency
            effect_surf = pygame.Surface(
                (self.radius * 2, self.radius * 2), pygame.SRCALPHA)
            center = (self.radius, self.radius)
            alpha_color = (*self.color, int(self.alpha))
            pygame.draw.circle(effect_surf, alpha_color, center, 5)
            surf.blit(effect_surf, (self.x - self.radius, self.y - self.radius))

        elif self.effect_type == "slash":
            # Create a surface for transparency
            effect_surf = pygame.Surface(
                (self.radius * 2, self.radius * 2), pygame.SRCALPHA)
            center = (self.radius, self.radius)

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

            surf.blit(effect_surf, (self.x - self.radius, self.y - self.radius))

        elif self.effect_type == "line":
            if self.end_x is not None and self.end_y is not None:
                alpha_color = (*self.color, int(self.alpha * 0.7))
                pygame.draw.line(surf, alpha_color, (int(self.x), int(self.y)),
                                 (int(self.end_x), int(self.end_y)), max(1, int(self.line_width * 0.3)))

                # Draw particles for lightning effect
                for p in self.particles:
                    particle_color = (*self.color, int(p['alpha']))
                    pygame.draw.circle(surf, particle_color,
                                       (int(p['x']), int(p['y'])), p['size'])

                # Draw a glow effect along the line
                for i in range(3):  # Multiple layers for glow
                    # Decreasing alpha for outer glow
                    glow_alpha = int(self.alpha * (0.3 - i * 0.1))
                    glow_color = (*self.color, glow_alpha)
                    # Increasing width for outer glow
                    glow_width = int(self.line_width * (0.5 + i * 0.5))
                    pygame.draw.line(surf, glow_color, (int(self.x), int(self.y)),
                                     (int(self.end_x), int(self.end_y)), glow_width)


class DashAfterimage:
    """
    A fading afterimage effect using a specific sprite.
    This will destroy it self after animation ends
    """

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
            return self.active  # Effect is done

        # Calculate current alpha (fade out)
        current_alpha = self.start_alpha * (1.0 - progress)
        # Apply alpha to the copied sprite
        self.sprite.set_alpha(int(max(0, current_alpha)))
        return self.active  # Effect is still active

    def draw(self, surf):
        if not self.active or not self.sprite:
            return

        # Calculate top-left draw position (centering the stored sprite)
        draw_x = self.x - self.width / 2
        draw_y = self.y - self.height / 2
        surf.blit(self.sprite, (int(draw_x), int(draw_y)))

    def is_ground_effect(self):  # Helper for potential layering in game.py
        return True  # Treat afterimage as a ground effect maybe?

# skill.py
import time
from enum import Enum, auto
import math
import pygame
from utils import draw_hp_bar
from config import (
    WIDTH, HEIGHT, FPS,
    WHITE, BLACK, RED, BLUE, PURPLE, GREEN,
    ELEMENT_COLORS
)


class SkillType(Enum):
    PROJECTILE = auto()
    SUMMON = auto()
    HEAL = auto()
    AOE = auto()
    SLASH = auto()
    CHAIN = auto()


class BaseSkill:
    """Base class for all skills"""

    def __init__(self, name, element, skill_type, damage, speed,
                 radius, duration, pull, heal_amount, cooldown, description):
        self.name = name
        self.element = element
        self.skill_type = skill_type
        self.damage = damage
        self.speed = speed
        self.radius = radius
        self.duration = duration
        self.pull = pull
        self.heal_amount = heal_amount
        self.cooldown = cooldown
        self.description = description
        self.active = True

        # Get color from element
        if element in ELEMENT_COLORS:
            self.color = ELEMENT_COLORS[element]['primary']
        else:
            print(f"Warning: Unknown element {element}, using default color")
            self.color = WHITE

        self.last_use_time = 0

    def is_off_cooldown(self, now):
        return (now - self.last_use_time) >= self.cooldown

    def trigger_cooldown(self, now):
        self.last_use_time = now

    def update(self, dt):
        pass

    def draw(self, surf):
        pass


class Projectile(BaseSkill):
    def __init__(self, x, y, base_skill, target_x, target_y):
        super().__init__(
            base_skill.name, base_skill.element, base_skill.skill_type,
            base_skill.damage, base_skill.speed, base_skill.radius,
            base_skill.duration, base_skill.pull, base_skill.heal_amount,
            base_skill.cooldown, base_skill.description
        )
        self.x = x
        self.y = y
        self.radius = 5  # Visual radius for projectile

        # Use the speed from the CSV (multiply by 60 to convert to pixels per second)
        projectile_speed = self.speed * 60

        # Calculate velocity with the speed from CSV
        dx = target_x - x
        dy = target_y - y
        dist = math.hypot(dx, dy)
        if dist == 0:
            dist = 1
        self.vx = (dx / dist) * projectile_speed
        self.vy = (dy / dist) * projectile_speed

    def update(self, dt, enemies):
        self.x += self.vx * dt
        self.y += self.vy * dt
        # Deactivate if out of screen
        if (self.x < 0 or self.x > WIDTH or
                self.y < 0 or self.y > HEIGHT):
            self.active = False
        else:
            # Check collision with enemies
            for e in enemies:
                dist = math.hypot(e.x - self.x, e.y - self.y)
                if dist < (e.radius + self.radius - 2):
                    e.health -= self.damage
                    self.active = False
                    break

    def draw(self, surf):
        pygame.draw.circle(
            surf, self.color, (int(
                self.x), int(
                self.y)), self.radius)
        pygame.draw.circle(surf, (255,0,0), (int(self.x), int(self.y)), self.radius, 1)


class Summons(BaseSkill):
    def __init__(self, x, y, base_skill):
        super().__init__(
            base_skill.name, base_skill.element, base_skill.skill_type,
            base_skill.damage, base_skill.speed, base_skill.radius,
            base_skill.duration, base_skill.pull, base_skill.heal_amount,
            base_skill.cooldown, base_skill.description
        )
        self.x = x
        self.y = y
        self.radius = 12
        self.health = 50
        self.max_health = 50
        self.alive = True
        self.start_time = time.time()

    def update(self, enemies):
        if time.time() - self.start_time > self.duration:
            self.alive = False
            return

        if not enemies:
            return

        closest = None
        closest_dist = float('inf')
        for e in enemies:
            dist = math.hypot(e.x - self.x, e.y - self.y)
            if dist < closest_dist:
                closest_dist = dist
                closest = e

        if closest and closest_dist > 0:
            dx = closest.x - self.x
            dy = closest.y - self.y
            self.x += (dx / closest_dist) * self.speed
            self.y += (dy / closest_dist) * self.speed
            if closest_dist < (self.radius + closest.radius):
                closest.health -= self.damage * 0.1

        self.x = max(self.radius, min(WIDTH - self.radius, self.x))
        self.y = max(self.radius, min(HEIGHT - self.radius, self.y))
        if self.health <= 0:
            self.alive = False

    def draw(self, surf):
        pygame.draw.circle(surf, self.color, (int(self.x), int(self.y)), self.radius)
        bar_x = self.x - 25
        bar_y = self.y - self.radius - 10
        draw_hp_bar(surf, bar_x, bar_y, self.health, self.max_health, GREEN)


class AOE(BaseSkill):
    def __init__(self, x, y, base_skill):
        super().__init__(
            base_skill.name, base_skill.element, base_skill.skill_type,
            base_skill.damage, base_skill.speed, base_skill.radius,
            base_skill.duration, base_skill.pull, base_skill.heal_amount,
            base_skill.cooldown, base_skill.description
        )
        self.x = x
        self.y = y
        self.start_time = time.time()
        self.current_radius = 0
        self.damage_dealt = False

    def update(self, dt):
        elapsed = time.time() - self.start_time
        if elapsed >= self.duration:
            self.active = False
        else:
            progress = elapsed / self.duration
            self.current_radius = self.radius * min(1.0, progress * 2.0)

    def draw(self, surf):
        if self.active:
            pygame.draw.circle(surf, self.color, (int(self.x), int(self.y)),
                               int(self.current_radius), 2)


class Slash(BaseSkill):
    def __init__(self, player_x, player_y, cursor_x, cursor_y, base_skill):
        super().__init__(
            base_skill.name, base_skill.element, base_skill.skill_type,
            base_skill.damage, base_skill.speed, base_skill.radius,
            base_skill.duration, base_skill.pull, base_skill.heal_amount,
            base_skill.cooldown, base_skill.description
        )
        self.x = player_x
        self.y = player_y
        self.start_time = time.time()
        self.damage_dealt = False

        # Calculate direction based on cursor position
        dx = cursor_x - player_x
        dy = cursor_y - player_y
        self.direction = math.atan2(dy, dx)

        # Set start and sweep angles based on direction
        # Start 30 degrees to the left of the direction
        self.start_angle = self.direction - math.pi / 6
        self.sweep_angle = math.pi / 3  # Sweep 60 degrees

    def update(self, dt):
        elapsed = time.time() - self.start_time
        if elapsed >= self.duration:
            self.active = False

    def draw(self, surf):
        if self.active:
            elapsed = time.time() - self.start_time
            progress = elapsed / self.duration
            current_angle = self.sweep_angle * progress

            # Draw main arc
            pygame.draw.arc(surf,
                            self.color,
                            (int(self.x - self.radius),
                             int(self.y - self.radius),
                                self.radius * 2,
                                self.radius * 2),
                            self.start_angle,
                            self.start_angle + current_angle,
                            4)

            # Draw inner arc for better visibility
            inner_radius = self.radius * 0.7
            pygame.draw.arc(surf,
                            self.color,
                            (int(self.x - inner_radius),
                             int(self.y - inner_radius),
                                inner_radius * 2,
                                inner_radius * 2),
                            self.start_angle,
                            self.start_angle + current_angle,
                            2)


class Chain(BaseSkill):
    def __init__(self, x, y, base_skill, targets):
        super().__init__(
            base_skill.name, base_skill.element, base_skill.skill_type,
            base_skill.damage, base_skill.speed, base_skill.radius,
            base_skill.duration, base_skill.pull, base_skill.heal_amount,
            base_skill.cooldown, base_skill.description
        )
        self.targets = targets
        self.jump_delay = 0.1
        self.current_jump = 0
        self.time_since_jump = 0
        self.start_time = time.time()

    def update(self, dt):
        if time.time() - self.start_time > self.duration:
            self.active = False
            return

        self.time_since_jump += dt
        if self.time_since_jump >= self.jump_delay:
            self.current_jump += 1
            self.time_since_jump = 0
            if self.current_jump >= len(self.targets) - 1:
                self.active = False

    def draw(self, surf):
        if self.active and self.current_jump < len(self.targets) - 1:
            start = self.targets[self.current_jump]
            end = self.targets[self.current_jump + 1]
            pygame.draw.line(surf, self.color,
                             (int(start[0]), int(start[1])),
                             (int(end[0]), int(end[1])), 3)


class Heal(BaseSkill):
    def __init__(self, x, y, base_skill):
        super().__init__(
            base_skill.name, base_skill.element, base_skill.skill_type,
            base_skill.damage, base_skill.speed, base_skill.radius,
            base_skill.duration, base_skill.pull, base_skill.heal_amount,
            base_skill.cooldown, base_skill.description
        )
        self.x = x
        self.y = y
        self.start_time = time.time()
        self.healing_done = False

    def update(self, dt):
        if time.time() - self.start_time >= self.duration:
            self.active = False

    def draw(self, surf):
        if self.active:
            elapsed = time.time() - self.start_time
            progress = elapsed / self.duration
            current_radius = self.radius * (1 - progress)

            pygame.draw.circle(surf, self.color, (int(self.x), int(self.y)),
                               int(current_radius), 2)
            # Inner circle
            pygame.draw.circle(surf, self.color, (int(self.x), int(self.y)),
                               int(current_radius * 0.7), 1)


def create_skill(skill_type, x, y, base_skill, **kwargs):
    """Factory function to create skills with proper parameters"""
    if skill_type == SkillType.PROJECTILE:
        return Projectile(
            x,
            y,
            base_skill,
            kwargs.get('tx'),
            kwargs.get('ty'))
    elif skill_type == SkillType.CHAIN:
        return Chain(x, y, base_skill, kwargs.get('targets', []))
    elif skill_type == SkillType.SUMMON:
        return Summons(x, y, base_skill)
    elif skill_type == SkillType.HEAL:
        return Heal(x, y, base_skill)
    elif skill_type == SkillType.AOE:
        return AOE(x, y, base_skill)
    elif skill_type == SkillType.SLASH:
        return Slash(
            kwargs.get('player_x'),
            kwargs.get('player_y'),
            kwargs.get('cursor_x'),
            kwargs.get('cursor_y'),
            base_skill)
    else:
        raise ValueError(f"Unknown skill type: {skill_type}")

import pygame
import math
import time
from utils import draw_hp_bar


class Enemy:
    def __init__(
            self,
            x,
            y,
            wave_number,
            radius,
            base_speed,
            base_hp,
            wave_multiplier,
            color,
            damage,
            attack_cooldown):
        self.x = x
        self.y = y
        self.radius = radius
        self.base_speed = base_speed
        # scale with wave
        self.health = base_hp * (wave_number * wave_multiplier)
        self.max_health = self.health
        self.damage = damage
        self.alive = True
        self.color = color
        self.attack_cooldown = attack_cooldown  # seconds
        self.attack_timer = 0.0     # current timer for attacks

    def update(self, player, dt):
        # 1) Check for attack BEFORE moving
        closest_type, closest_dist, closest_obj = self.get_closest_target(
            player)

        # Update attack timer
        if self.attack_timer > 0:
            self.attack_timer -= dt

        # Try to attack if we can
        if closest_dist < (
                self.radius +
                closest_obj[3]) and self.attack_timer <= 0:
            self.attack(closest_type, closest_obj[4])  # Pass the actual object
            self.attack_timer = self.attack_cooldown

        # 2) Then move toward target
        if closest_obj and closest_dist > 0:
            tx = closest_obj[1]
            ty = closest_obj[2]
            dx = tx - self.x
            dy = ty - self.y
            speed = self.base_speed * dt
            self.x += (dx / closest_dist) * speed
            self.y += (dy / closest_dist) * speed

        # 3) Check for death
        if self.health <= 0:
            self.alive = False

    def get_closest_target(self, player):
        """Find the closest target and return its info."""
        targets = []
        # (type, x, y, radius, object)
        targets.append(('player', player.x, player.y, player.radius, player))
        for w in player.summons:
            targets.append(('wraith', w.x, w.y, w.radius, w))

        closest_dist = float('inf')
        closest_type = None
        closest_obj = None

        for t in targets:
            dist = math.hypot(t[1] - self.x, t[2] - self.y)
            if dist < closest_dist:
                closest_dist = dist
                closest_type = t[0]
                closest_obj = t

        return closest_type, closest_dist, closest_obj

    def attack(self, target_type, target):
        """Deal damage to the target."""
        target.take_damage(self.damage)

    def draw(self, surf):
        pygame.draw.circle(
            surf, self.color, (int(
                self.x), int(
                self.y)), self.radius)
        # HP bar
        bar_x = self.x - 25
        bar_y = self.y - self.radius - 10
        draw_hp_bar(
            surf,
            bar_x,
            bar_y,
            self.health,
            self.max_health,
            self.color)

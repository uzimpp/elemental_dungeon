# player.py
import time
import math
import pygame
import random
from utils import angle_diff
# from skill import SkillType, create_skill, Projectile, Summons, Chain, Slash, Shield, Orbit, Mark, Zone, Beam, Trap, Buff
from skill import SkillType, create_skill, Projectile, Summons, Chain, Slash
from visual_effects import VisualEffect
from config import (WIDTH, HEIGHT)
from entity import Entity


class Player(Entity):
    def __init__(
            self,
            name,
            x,
            y,
            deck,
            radius,
            max_health,
            summon_limit,
            color,
            walk_speed,
            sprint_speed,
            max_stamina,
            stamina_regen,
            sprint_drain,
            dash_cost,
            dash_distance,
            stamina_cooldown):
        # Call parent class constructor
        super().__init__(x, y, radius, max_health, walk_speed, color)
        
        # Player specific attributes
        self.name = name
        self.deck = deck
        self.projectiles = []
        self.summons = []
        self.summon_limit = summon_limit

        # Speed attributes
        self.walk_speed = walk_speed
        self.sprint_speed = sprint_speed
        self.speed = self.walk_speed  # current speed

        # Stamina System
        self.max_stamina = max_stamina
        self.stamina = self.max_stamina
        self.stamina_regen = stamina_regen
        self.sprint_drain = sprint_drain
        self.dash_cost = dash_cost
        self.dash_distance = dash_distance
        self.stamina_depleted_time = None
        self.stamina_cooldown = stamina_cooldown
    
    def get_projectiles(self):
        return self.projectiles
    
    def get_summons(self):
        return self.summons
    
    def handle_input(self, dt):
        keys = pygame.key.get_pressed()

        # 1) Are we pressing SHIFT?
        shift_held = (keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT])
        
        # 2) Check if we can sprint
        can_sprint = shift_held and (self.stamina > 0)

        # 3) Decide speed
        if can_sprint:
            self.speed = self.sprint_speed
        else:
            self.speed = self.walk_speed

        # 4) Movement (using dt)
        tmp_dx = 0
        tmp_dy = 0
        if keys[pygame.K_w]: tmp_dy -= 1
        if keys[pygame.K_s]: tmp_dy += 1
        if keys[pygame.K_a]: tmp_dx -= 1
        if keys[pygame.K_d]: tmp_dx += 1
        
        # Update direction if moving
        if tmp_dx != 0 or tmp_dy != 0:
            dist = math.hypot(tmp_dx, tmp_dy)
            self.dx = tmp_dx / dist
            self.dy = tmp_dy / dist
            
            # Move
            current_speed = self.speed * dt
            self.x += tmp_dx * current_speed
            self.y += tmp_dy * current_speed
        
        # If not moving, point toward mouse
        else:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            tmp_dx = mouse_x - self.x
            tmp_dy = mouse_y - self.y
            dist = math.hypot(tmp_dx, tmp_dy)
            if dist > 0:
                self.dx = tmp_dx / dist
                self.dy = tmp_dy / dist
        
        # Stay within screen
        self.x = max(self.radius, min(WIDTH - self.radius, self.x))
        self.y = max(self.radius, min(HEIGHT - self.radius, self.y))

        # 5) Stamina logic (using dt)
        if can_sprint:
            # While SHIFT is held, do NOT regenerate
            self.stamina -= self.sprint_drain * dt
            if self.stamina < 0:
                self.stamina = 0
                self.stamina_depleted_time = time.time()  # Record depletion time
                # Force speed to walk if stamina is now empty
                self.speed = self.walk_speed
        else:
            # If SHIFT not held or stamina is zero, we REGENERATE
            if self.stamina < self.max_stamina:
                if self.stamina == 0 and self.stamina_depleted_time is not None:
                    # Check if cooldown period has passed
                    if time.time() - self.stamina_depleted_time >= self.stamina_cooldown:
                        self.stamina += self.stamina_regen * dt
                        if self.stamina > self.max_stamina:
                            self.stamina = self.max_stamina
                            self.stamina_depleted_time = None  # Reset depletion time
                elif self.stamina > 0:
                    self.stamina += self.stamina_regen * dt
                    if self.stamina > self.max_stamina:
                        self.stamina = self.max_stamina

    def handle_event(self, event, mouse_pos, enemies, now, effects):
        if event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4]:
                skill_idx = event.key - pygame.K_1
                self.cast_skill(skill_idx, mouse_pos, enemies, now, effects)
            elif event.key == pygame.K_SPACE:
                self.dash()
            elif event.key == pygame.K_ESCAPE:
                print("Player exited the game!")
                print("See you next time!")
                return 'exit'  # Signal to exit the game
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # left-click => skill 0
                self.cast_skill(0, mouse_pos, enemies, now, effects)

    def dash(self):
        """Dash in the direction (dx, dy)."""
        # Attempt dash if enough stamina
        if self.stamina >= self.dash_cost:
            self.stamina -= self.dash_cost
            # Determine dash direction from WASD
            dx = 0
            dy = 0
            keys = pygame.key.get_pressed()
            if keys[pygame.K_w]:
                dy -= 1
            if keys[pygame.K_s]:
                dy += 1
            if keys[pygame.K_a]:
                dx -= 1
            if keys[pygame.K_d]:
                dx += 1
            if dx == 0 and dy == 0:
                print("No movement direction, can't dash.")
            else:
                dist = math.hypot(dx, dy)
                if dist == 0:
                    return
                nx = dx / dist
                ny = dy / dist
                # move by dash_distance
                self.x += nx * self.dash_distance
                self.y += ny * self.dash_distance
                # clamp
                self.x = max(self.radius, min(WIDTH - self.radius, self.x))
                self.y = max(self.radius, min(HEIGHT - self.radius, self.y))
        else:
            print("Not enough stamina to dash!")

    def cast_skill(self, skill_idx, target_pos, enemies, now, effects):
        if skill_idx >= len(self.deck):
            return

        base_skill = self.deck[skill_idx]
        if not base_skill.is_off_cooldown(now):
            return

        tx, ty = target_pos
        base_skill.trigger_cooldown(now)

        # Create the appropriate skill instance using the factory
        if base_skill.skill_type == SkillType.PROJECTILE:
            skill = create_skill(
                SkillType.PROJECTILE,
                self.x,
                self.y,
                base_skill,
                tx=tx,
                ty=ty)
            self.projectiles.append(skill)
            effects.append(
                VisualEffect(
                    self.x,
                    self.y,
                    "explosion",
                    base_skill.color,
                    20,
                    0.2))

        elif base_skill.skill_type == SkillType.SUMMON:
            if len(self.summons) < self.summon_limit:
                skill = create_skill(
                    SkillType.SUMMON, self.x, self.y, base_skill)
                self.summons.append(skill)
                effects.append(
                    VisualEffect(
                        self.x,
                        self.y,
                        "heal",
                        base_skill.color,
                        30,
                        0.5))

        elif base_skill.skill_type == SkillType.HEAL:
            skill = create_skill(SkillType.HEAL, self.x, self.y, base_skill)
            self.health = min(
                self.max_health,
                self.health +
                base_skill.heal_amount)
            effects.append(skill)
            effects.append(
                VisualEffect(
                    self.x,
                    self.y,
                    "heal",
                    base_skill.color,
                    40,
                    0.8))

        elif base_skill.skill_type == SkillType.AOE:
            skill = create_skill(SkillType.AOE, tx, ty, base_skill)
            effects.append(skill)
            effects.append(
                VisualEffect(
                    tx,
                    ty,
                    "explosion",
                    base_skill.color,
                    base_skill.radius,
                    0.5))

            for e in enemies:
                dist = math.hypot(e.x - tx, e.y - ty)
                if dist <= base_skill.radius:
                    e.health -= base_skill.damage
                    effects.append(
                        VisualEffect(
                            e.x,
                            e.y,
                            "explosion",
                            base_skill.color,
                            20,
                            0.2))

        elif base_skill.skill_type == SkillType.SLASH:
            # Create a Slash skill around the player
            slash_skill = create_skill(
                SkillType.SLASH, self.x, self.y, base_skill,
                player_x=self.x, player_y=self.y, cursor_x=tx, cursor_y=ty
            )
            effects.append(slash_skill)
            # Create a VisualEffect for the slash
            slash_effect = VisualEffect(
                self.x, self.y, "slash", base_skill.color,
                radius=base_skill.radius, duration=0.3
            )
            slash_effect.start_angle = slash_skill.start_angle
            slash_effect.sweep_angle = slash_skill.sweep_angle
            effects.append(slash_effect)

            for enemy in enemies:
                # Calculate angle to the enemy
                dx = enemy.x - self.x
                dy = enemy.y - self.y
                angle_to_enemy = math.atan2(dy, dx)

                # Normalize angles to be within [0, 2*pi]
                start_angle = (slash_skill.start_angle +
                               2 * math.pi) % (2 * math.pi)
                end_angle = (
                    start_angle + slash_skill.sweep_angle) % (2 * math.pi)
                angle_to_enemy = (angle_to_enemy + 2 * math.pi) % (2 * math.pi)

                # Check if the enemy is within the sweep angle and radius
                if start_angle <= angle_to_enemy <= end_angle and math.hypot(
                        dx, dy) <= base_skill.radius:
                    enemy.health -= base_skill.damage

        elif base_skill.skill_type == SkillType.CHAIN:
            targets = [(self.x, self.y)]
            remaining = sorted(
                enemies,
                key=lambda e: math.hypot(
                    e.x -
                    tx,
                    e.y -
                    ty))[
                :3]

            for e in remaining:
                targets.append((e.x, e.y))
                e.health -= base_skill.damage
                effects.append(
                    VisualEffect(
                        e.x,
                        e.y,
                        "explosion",
                        base_skill.color,
                        25,
                        0.3))

            if targets:
                skill = create_skill(
                    SkillType.CHAIN, 0, 0, base_skill, targets=targets)
                effects.append(skill)

        # elif base_skill.skill_type == SkillType.SHIELD:
        #     shield = Shield(self, 50, base_skill.color, base_skill.duration)
        #     effects.append(shield)
        #     # Add shield activation effects
        #     effects.append(VisualEffect(self.x, self.y, "heal",
        #                               base_skill.color, 40, 0.6))
        #     effects.append(VisualEffect(self.x, self.y, "explosion",
        #                               base_skill.color, 35, 0.5))


    def take_damage(self, amt):
        if amt > 0:
            self.health -= amt
            if self.health < 0:
                self.health = 0

    def draw(self, surf):
        # pygame.draw.circle(
        #     surf, self.color, (int(
        #         self.x), int(
        #         self.y)), self.radius)
        # Draw directional triangle instead of circle
        self.draw_triangle(surf)

        for p in self.projectiles:
            p.draw(surf)
        for w in self.summons:
            w.draw(surf)



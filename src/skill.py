# skill.py
import time
from enum import Enum, auto
import math
import pygame
from utils import draw_hp_bar, angle_diff
from animation import CharacterAnimation
from entity import Entity  # Import the Entity base class
from config import (
    WIDTH, HEIGHT, FPS,
    WHITE, BLACK, RED, BLUE, PURPLE, GREEN,
    ELEMENT_COLORS, SHADOW_SUMMON_SPRITE_PATH, SHADOW_SUMMON_ANIMATION_CONFIG
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
    def __init__(self, name, element, skill_type, cooldown, description):
        self.name = name
        self.element = element
        self.skill_type = skill_type
        self.cooldown = cooldown
        self.description = description
        self.last_use_time = 0
        self.color = self._get_color_from_element(element)
    
    def _get_color_from_element(self, element):
        if element in ELEMENT_COLORS:
            return ELEMENT_COLORS[element]['primary']
        return WHITE  # Default fallback
    
    def is_off_cooldown(self, current_time):
        if current_time is None:
            current_time = time.time()
        return (current_time - self.last_use_time) >= self.cooldown
    
    def trigger_cooldown(self):
        self.last_use_time = time.time()

class ProjectileEntity(Entity):
    def __init__(self, start_x, start_y, target_x, target_y, skill):
        super().__init__(
            x=start_x,
            y=start_y,
            radius=5, # Visual radius
            max_health=1, # Projectiles die on hit
            speed=skill.speed * 60, # Convert to pixels per second
            color=skill.color
        )
        self.damage = skill.damage
        self.element = skill.element
        self.max_life_time = skill.duration
        self.life_time = 0

        # Calculate velocity
        dx = target_x - start_x
        dy = target_y - start_y
        dist = math.hypot(dx, dy)
        if dist == 0: dist = 1
        self.dx = (dx / dist) * self.speed
        self.dy = (dy / dist) * self.speed

    def update(self, dt, enemies):
        """Update projectile position and check collisions"""
        if not self.alive: return False

        self.x += self.dx * dt
        self.y += self.dy * dt
        self.life_time += dt

        # Check bounds and lifetime
        if (self.x < 0 or self.x > WIDTH or
            self.y < 0 or self.y > HEIGHT or
            self.life_time >= self.max_life_time):
            self.alive = False
            return False

        # Check collision with enemies
        for enemy in enemies:
            if not enemy.alive: continue
            dist = math.hypot(enemy.x - self.x, enemy.y - self.y)
            if dist < (enemy.radius + self.radius):
                enemy.take_damage(self.damage)
                self.alive = False
                return False

        return self.alive

    def draw(self, surface):
        """Draw the projectile"""
        if self.alive:
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)

class Projectile(BaseSkill):
    """Projectile skill that creates ProjectileEntity instances"""
    def __init__(self, name, element, damage, speed, radius, duration, cooldown, description):
        super().__init__(name, element, SkillType.PROJECTILE, cooldown, description)
        self.damage = damage
        self.speed = speed
        self.radius = radius
        self.duration = duration
    
    @staticmethod
    def create(skill, start_x, start_y, target_x, target_y):
        """Create a projectile instance"""
        return ProjectileEntity(start_x, start_y, target_x, target_y, skill)
    
    @staticmethod
    def update(projectile, dt, enemies):
        """Update the projectile (for compatibility with existing code)"""
        return projectile.update(dt, enemies)
    
    @staticmethod
    def draw(projectile, surface):
        """Draw the projectile (for compatibility with existing code)"""
        projectile.draw(surface)

class SummonEntity(Entity):
    """Entity class for summons that behaves like other game entities"""
    def __init__(self, x, y, skill):
        super().__init__(
            x=x,
            y=y,
            radius=12,
            max_health=50, # Example health
            speed=skill.speed * 60, # Convert to pixels per second
            color=skill.color
        )
        self.damage = skill.damage
        self.element = skill.element
        self.start_time = time.time()
        self.max_life_time = skill.duration
        self.state = 'idle'
        self.attack_range = skill.radius # Use skill radius as attack range
        self.attack_cooldown = 1.0 # Example attack cooldown
        self.last_attack_time = 0

        # Animation
        # self.animation = CharacterAnimation(
        #     sprite_sheet_path=skill.sprite_path,
        #     config=skill.animation_config,
        #     sprite_width=32,
        #     sprite_height=32
        # )
        try:
            # Use default sprite path and config if not provided
            sprite_path = getattr(skill, 'sprite_path', SHADOW_SUMMON_SPRITE_PATH)
            animation_config = getattr(skill, 'animation_config', SHADOW_SUMMON_ANIMATION_CONFIG)
            
            print(f"[SummonEntity] Loading sprite from: {sprite_path}")
            self.animation = CharacterAnimation(
                sprite_sheet_path=sprite_path,
                config=animation_config,
                sprite_width=32,
                sprite_height=32
            )
            print("[SummonEntity] Animation loaded successfully")
        except Exception as e:
            print(f"[SummonEntity] Error loading animation: {e}")
            self.animation = None

    def update(self, dt, enemies):
        """Update summon behavior: find target, move, attack"""
        if not self.alive: return False

        current_time = time.time()
        # Check lifetime
        if current_time - self.start_time >= self.max_life_time:
            self.alive = False
            return False

        # Find closest enemy
        target = None
        min_dist = float('inf')
        for enemy in enemies:
            if enemy.alive:
                dist = math.hypot(enemy.x - self.x, enemy.y - self.y)
                if dist < min_dist:
                    min_dist = dist
                    target = enemy

        # Determine state and action based on target
        if self.state == 'dying':
             self.animation.update(dt) # Continue dying animation
             if self.animation.animation_finished:
                 self.alive = False # Mark as dead after animation
             return self.alive # Don't do anything else if dying

        elif self.state == 'hurt':
             self.animation.update(dt)
             if self.animation.animation_finished:
                 self.state = 'idle' # Return to idle after hurt
                 self.animation.set_state('idle', force_reset=True)

        elif self.state == 'sweep':
             self.animation.update(dt)
             if self.animation.animation_finished:
                 self.state = 'idle' # Return to idle after attack
                 self.animation.set_state('idle', force_reset=True)

        elif target:
            dist_to_target = min_dist
            # Calculate direction
            dx = target.x - self.x
            dy = target.y - self.y
            if dist_to_target > 0:
                self.dx = dx / dist_to_target
                self.dy = dy / dist_to_target
            else:
                self.dx, self.dy = 0, 0

            # Attack if in range and off cooldown
            if dist_to_target <= self.attack_range and current_time - self.last_attack_time >= self.attack_cooldown:
                self.state = 'sweep'
                self.animation.set_state('sweep', force_reset=True)
                target.take_damage(self.damage) # Apply full damage
                self.last_attack_time = current_time
            # Move towards target if not attacking or hurt
            elif self.state not in ['sweep', 'hurt']:
                self.state = 'walk'
                self.animation.set_state('walk')
                self.x += self.dx * self.speed * dt
                self.y += self.dy * self.speed * dt
            # Update walk animation if already walking
            elif self.state == 'walk':
                 self.animation.update(dt, self.dx, self.dy)

        else: # No target
            if self.state not in ['idle', 'hurt']:
                 self.state = 'idle'
                 self.animation.set_state('idle')
                 self.animation.update(dt) # Update idle animation

        # Keep within screen bounds
        self.x = max(self.radius, min(WIDTH - self.radius, self.x))
        self.y = max(self.radius, min(HEIGHT - self.radius, self.y))

        return self.alive

    def take_damage(self, amount):
        """Override take_damage to handle animations"""
        if not self.alive or self.state == 'dying': return

        super().take_damage(amount) # Call parent Entity method

        if self.health <= 0:
            if self.state != 'dying':
                self.state = 'dying'
                self.animation.set_state('dying', force_reset=True)
                # Don't set self.alive = False yet, let animation finish
        elif self.state not in ['sweep', 'dying']: # Don't interrupt attack/death
            self.state = 'hurt'
            self.animation.set_state('hurt', force_reset=True)

    def draw(self, surface):
        """Draw summon with sprite or fallback, includes HP bar"""
        if not self.alive and self.state != 'dying': return # Don't draw if dead unless dying animation playing

        # Try to draw sprite first
        if self.animation and hasattr(self.animation, 'get_current_sprite'):
            try:
                current_sprite = self.animation.get_current_sprite()
                if current_sprite:
                    draw_x = self.x - self.animation.sprite_width / 2
                    draw_y = self.y - self.animation.sprite_height / 2
                    surface.blit(current_sprite, (int(draw_x), int(draw_y)))
                    print(f"[SummonEntity] Drawing sprite at ({draw_x}, {draw_y})")
                else:
                    print("[SummonEntity] No current sprite available, using fallback")
                    self._draw_fallback(surface)
            except Exception as e:
                print(f"[SummonEntity] Error drawing sprite: {e}")
                self._draw_fallback(surface)
        else:
            print("[SummonEntity] No animation available, using fallback")
            self._draw_fallback(surface)

        # Draw HP bar only if not dying
        if self.state != 'dying':
            bar_x = self.x - 25
            bar_y = self.y - self.radius - 10 # Position above the summon
            draw_hp_bar(surface, bar_x, bar_y, self.health, self.max_health, GREEN)

    def _draw_fallback(self, surface):
        """Fallback drawing method when sprite is not available"""
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)
        # Draw a simple triangle to indicate direction
        angle = math.atan2(self.dy, self.dy)
        points = [
            (self.x + math.cos(angle) * self.radius, self.y + math.sin(angle) * self.radius),
            (self.x + math.cos(angle + 2.5) * self.radius, self.y + math.sin(angle + 2.5) * self.radius),
            (self.x + math.cos(angle - 2.5) * self.radius, self.y + math.sin(angle - 2.5) * self.radius)
        ]
        pygame.draw.polygon(surface, self.color, points)

class Summon(BaseSkill):
    """Summon skill that creates SummonEntity instances"""
    def __init__(self, name, element, damage, speed, radius, duration, cooldown, description, sprite_path, animation_config):
        super().__init__(name, element, SkillType.SUMMON, cooldown, description)
        self.damage = damage
        self.speed = speed
        self.radius = radius
        self.duration = duration
        self.sprite_path = sprite_path
        self.animation_config = animation_config
    
    @staticmethod
    def create(skill, x, y):
        """Create a SummonEntity instance"""
        return SummonEntity(x, y, skill)
    
    @staticmethod
    def update(summon, dt, enemies):
        """Update the summon (for compatibility with existing code)"""
        return summon.update(dt, enemies)
    
    @staticmethod
    def draw(summon, surface):
        """Draw the summon (for compatibility with existing code)"""
        summon.draw(surface)

class Heal(BaseSkill):
    """Heal skill implementation"""
    def __init__(self, name, element, heal_amount, radius, duration, cooldown, description):
        super().__init__(name, element, SkillType.HEAL, cooldown, description)
        self.heal_amount = heal_amount
        self.radius = radius
        self.duration = duration
    
    @staticmethod
    def activate(skill, target):
        """Apply healing to target"""
        target.heal(skill.heal_amount)
        # Visual effects could be added here

class AOE(BaseSkill):
    """Area of Effect skill implementation"""
    def __init__(self, name, element, damage, radius, duration, cooldown, description):
        super().__init__(name, element, SkillType.AOE, cooldown, description)
        self.damage = damage
        self.radius = radius
        self.duration = duration

    @staticmethod
    def activate(skill, x, y, enemies):
        """Apply damage to all enemies in radius"""
        for enemy in enemies:
            if not enemy.alive: continue
            dist = math.hypot(enemy.x - x, enemy.y - y)
            if dist <= skill.radius:
                enemy.take_damage(skill.damage)
                print(f"[AOE] Hit enemy at ({enemy.x:.0f}, {enemy.y:.0f}) for {skill.damage} damage")

class Slash(BaseSkill):
    """Slash attack skill implementation"""
    def __init__(self, name, element, damage, radius, duration, cooldown, description):
        super().__init__(name, element, SkillType.SLASH, cooldown, description)
        self.damage = damage
        self.radius = radius
        self.duration = duration

    @staticmethod
    def activate(skill, player_x, player_y, target_x, target_y, enemies):
        """Apply damage to enemies in an arc"""
        # Calculate angle of slash
        angle = math.atan2(target_y - player_y, target_x - player_x)
        arc_width = math.pi / 3  # 60 degree arc
        
        for enemy in enemies:
            if not enemy.alive: continue
            # Calculate distance and angle to enemy
            dx = enemy.x - player_x
            dy = enemy.y - player_y
            dist = math.hypot(dx, dy)
            if dist <= skill.radius:
                enemy_angle = math.atan2(dy, dx)
                diff = abs(angle_diff(angle, enemy_angle))
                if diff <= arc_width:
                    enemy.take_damage(skill.damage)
                    print(f"[Slash] Hit enemy at ({enemy.x:.0f}, {enemy.y:.0f}) for {skill.damage} damage")

class Chain(BaseSkill):
    """Chain attack skill implementation"""
    def __init__(self, name, element, damage, radius, duration, pull, cooldown, description):
        super().__init__(name, element, SkillType.CHAIN, cooldown, description)
        self.damage = damage
        self.radius = radius
        self.duration = duration
        self.pull = pull

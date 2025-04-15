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
        self.max_life_time = float('inf')  # Infinite lifetime
        self.attack_range = skill.radius # Use skill radius as attack range
        self.attack_cooldown = 1.0 # Similar to Enemy's attack cooldown
        self.attack_timer = 0.0    # For tracking attack cooldown, like Enemy
        self.attack_animation_timer = 0.0 # For tracking animation duration
        self.last_attack_time = 0
        self.dx = 1  # Initial direction
        self.dy = 0  # Initial direction
        
        # State management (similar to Enemy)
        self.state = 'idle'

        # Animation
        try:
            sprite_path = getattr(skill, 'sprite_path', SHADOW_SUMMON_SPRITE_PATH)
            animation_config = getattr(skill, 'animation_config', SHADOW_SUMMON_ANIMATION_CONFIG)
            
            print(f"[SummonEntity] Loading sprite from: {sprite_path}")
            self.animation = CharacterAnimation(
                sprite_sheet_path=sprite_path,
                config=animation_config,
                sprite_width=32,
                sprite_height=32
            )
            # Force the animation to idle state
            self.animation.set_state('idle', force_reset=True)
            print(f"[SummonEntity] Animation loaded successfully and set to {self.state}")
        except Exception as e:
            print(f"[SummonEntity] Error loading animation: {e}")
            raise Exception(f"Failed to load summon animation: {e}")

    def update(self, dt, enemies):
        """Update summon behavior: find target, move, attack (similar to Enemy.update)"""
        print(f"[SummonEntity] update() called with dt={dt:.3f}, alive={self.alive}, health={self.health}, state={self.state}")
        
        # If entity is dead, only update dying animation and do nothing else
        if not self.alive or self.health <= 0:
            if self.state != 'dying':
                self.state = 'dying'
                self.animation.set_state('dying', force_reset=True)
                animations_length = len(self.animation.config['dying']['animations'])
                death_duration = self.animation.config['dying']['duration'] * animations_length
                self.attack_animation_timer = death_duration
                
            # Just update animation and check if it's time to set alive=False
            self.animation.update(dt)
            if self.attack_animation_timer > 0:
                self.attack_animation_timer -= dt
                if self.attack_animation_timer <= 0:
                    self.alive = False
            return False  # Don't do anything else if dying/dead
        
        # Handle hurt and attack animations
        if self.state in ['hurt', 'sweep']:
            self.attack_animation_timer -= dt
            self.animation.update(dt)
            
            # If animation is done, return to appropriate state
            if self.attack_animation_timer <= 0:
                if self.health <= 0:
                    self.state = 'dying'
                    self.animation.set_state('dying', force_reset=True)
                    animations_length = len(self.animation.config['dying']['animations'])
                    death_duration = self.animation.config['dying']['duration'] * animations_length
                    self.attack_animation_timer = death_duration
                else:
                    # Reset to idle or walking based on whether there's a target
                    self.state = 'idle'
                    self.animation.set_state('idle', force_reset=True)
            
            return True  # Don't move or attack during hurt/attack animations
        
        # Print enemies list to debug
        print(f"[SummonEntity] Checking for targets among {len(enemies)} enemies")
        for i, enemy in enumerate(enemies):
            if enemy.alive:
                print(f"[SummonEntity] Enemy {i}: at ({enemy.x:.1f}, {enemy.y:.1f}), alive={enemy.alive}")
        
        # Find closest enemy (target)
        target = None
        min_dist = float('inf')
        for enemy in enemies:
            if enemy.alive:
                dist = math.hypot(enemy.x - self.x, enemy.y - self.y)
                if dist < min_dist:
                    min_dist = dist
                    target = enemy
        
        # Print target info
        if target:
            print(f"[SummonEntity] Found target at ({target.x:.1f}, {target.y:.1f}), distance={min_dist:.1f}")
        else:
            print("[SummonEntity] No target found")
        
        # Update attack timer (like in Enemy class)
        if self.attack_timer > 0:
            self.attack_timer -= dt
            print(f"[SummonEntity] Attack timer: {self.attack_timer:.1f}")
        
        # Try to attack if we can (similar to Enemy.update)
        attack_distance = self.radius + self.attack_range
        if target and min_dist < attack_distance and self.attack_timer <= 0:
            print(f"[SummonEntity] Attacking enemy at ({target.x:.1f}, {target.y:.1f}), distance={min_dist:.1f} < {attack_distance}")
            
            # Set attack animation
            self.state = 'sweep'  # Use sweep as attack animation
            self.animation.set_state('sweep', force_reset=True)
            
            # Calculate attack animation duration
            animations_length = len(self.animation.config['sweep']['animations'])
            attack_duration = self.animation.config['sweep']['duration'] * animations_length
            self.attack_animation_timer = attack_duration
            
            # Perform the attack
            print(f"[SummonEntity] Enemy health before attack: {target.health}")
            target.take_damage(self.damage)
            print(f"[SummonEntity] Enemy health after attack: {target.health}, damage dealt: {self.damage}")
            self.attack_timer = self.attack_cooldown  # Reset attack timer
            self.last_attack_time = time.time()       # Update last attack time
            print(f"[SummonEntity] Dealt {self.damage} damage to target, reset attack_timer to {self.attack_cooldown}")
            return True  # Don't move after deciding to attack
        
        # Move toward target if not attacking
        if target and min_dist > 0:
            # Calculate direction
            dx = target.x - self.x
            dy = target.y - self.y
            if min_dist > 0:
                self.dx = dx / min_dist
                self.dy = dy / min_dist
            
            # Force minimum speed of 60 pixels per second
            effective_speed = max(60, self.speed)
            
            # Set walking animation if not already
            if self.state != 'walk':
                self.state = 'walk'
                self.animation.set_state('walk')
            
            # Move toward target using the move method from Entity
            old_x, old_y = self.x, self.y
            
            # Direct movement for debugging
            move_dist = effective_speed * dt
            self.x += self.dx * move_dist
            self.y += self.dy * move_dist
            print(f"[SummonEntity] Moving from ({old_x:.1f},{old_y:.1f}) to ({self.x:.1f},{self.y:.1f})")
            print(f"[SummonEntity] Movement: ({self.dx:.2f},{self.dy:.2f}) * {move_dist:.1f}")
            
            # Update animation with movement direction
            self.animation.update(dt, self.dx, self.dy)
        else:
            # If no target, set to idle
            if self.state != 'idle':
                self.state = 'idle'
                self.animation.set_state('idle')
            self.animation.update(dt)
        
        # Keep within screen bounds
        old_x, old_y = self.x, self.y
        self.x = max(self.radius, min(WIDTH - self.radius, self.x))
        self.y = max(self.radius, min(HEIGHT - self.radius, self.y))
        if old_x != self.x or old_y != self.y:
            print(f"[SummonEntity] Position clamped from ({old_x:.1f},{old_y:.1f}) to ({self.x:.1f},{self.y:.1f})")
        
        return True

    def get_direction_to(self, target_x, target_y):
        """Calculate direction (dx, dy) to a target point, normalized"""
        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.hypot(dx, dy)
        if distance == 0:
            return 0, 0
        return dx / distance, dy / distance

    def take_damage(self, amount):
        """Override take_damage to handle animations"""
        # Don't take damage if already dead
        if not self.alive or self.health <= 0:
            return

        if amount > 0:
            self.health -= amount
            
            if self.health <= 0:
                # Mark as dying but don't set alive=False yet (let animation finish)
                self.health = 0
                self.state = 'dying'
                self.animation.set_state('dying', force_reset=True)
                animations_length = len(self.animation.config['dying']['animations'])
                death_duration = self.animation.config['dying']['duration'] * animations_length
                self.attack_animation_timer = death_duration
            else:
                # Only show hurt animation if not already in a more important state
                if self.state not in ['dying', 'sweep']:
                    self.state = 'hurt'
                    self.animation.set_state('hurt', force_reset=True)
                    animations_length = len(self.animation.config['hurt']['animations'])
                    hurt_duration = self.animation.config['hurt']['duration'] * animations_length
                    self.attack_animation_timer = hurt_duration

    def draw(self, surface):
        """Draw summon with sprite, includes HP bar (similar to Enemy.draw)"""
        # Get the current sprite from the animation system
        current_sprite = self.animation.get_current_sprite()

        if current_sprite:
            # Calculate top-left position for blitting (center the sprite)
            draw_x = self.x - self.animation.sprite_width / 2
            draw_y = self.y - self.animation.sprite_height / 2

            # Draw the sprite
            surface.blit(current_sprite, (int(draw_x), int(draw_y)))
        else:
            raise Exception(f"[SummonEntity] No current sprite for state: {self.state}")
        
        # HP bar (only if not dying)
        if self.state != 'dying':
            bar_x = self.x - 25
            bar_y = self.y - self.radius - 10
            draw_hp_bar(surface, bar_x, bar_y, self.health, self.max_health, GREEN)


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
    def __init__(self, name, element, heal_amount, radius, duration, cooldown, description, heal_summons=True):
        super().__init__(name, element, SkillType.HEAL, cooldown, description)
        self.heal_amount = heal_amount
        self.radius = radius
        self.duration = duration
        self.heal_summons = heal_summons  # Flag to determine if this heal affects summons
    
    @staticmethod
    def activate(skill, target, summons=None):
        """Apply healing to target and optionally to summons"""
        # Always heal the primary target (player)
        if target:
            target.heal(skill.heal_amount)
            print(f"[Heal] Healed primary target for {skill.heal_amount} HP")
        
        # If heal_summons is True and summons are provided, heal them too
        if getattr(skill, 'heal_summons', True) and summons:
            for summon in summons:
                if summon.alive and summon.health < summon.max_health:
                    summon.heal(skill.heal_amount)
                    print(f"[Heal] Healed summon at ({summon.x:.0f}, {summon.y:.0f}) for {skill.heal_amount} HP")
        
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
    
    @staticmethod
    def activate(skill, player_x, player_y, target_x, target_y, enemies):
        """Apply damage to enemies in a chain, possibly pulling them"""
        # Find the closest enemy in the direction
        target = None
        min_dist = float('inf')
        
        for enemy in enemies:
            if not enemy.alive: continue
            dist = math.hypot(enemy.x - player_x, enemy.y - player_y)
            if dist <= skill.radius:
                # Check if enemy is in the general direction of the target point
                dx = enemy.x - player_x
                dy = enemy.y - player_y
                enemy_angle = math.atan2(dy, dx)
                target_angle = math.atan2(target_y - player_y, target_x - player_x)
                diff = abs(angle_diff(target_angle, enemy_angle))
                
                # Consider enemies in a 45-degree cone in target direction
                if diff <= math.pi / 4 and dist < min_dist:
                    min_dist = dist
                    target = enemy
        
        if target:
            # Apply damage
            target.take_damage(skill.damage)
            print(f"[Chain] Hit enemy at ({target.x:.0f}, {target.y:.0f}) for {skill.damage} damage")
            
            # Apply pull effect if enabled
            if skill.pull:
                pull_strength = 60  # Pull strength in pixels
                pull_dir_x = player_x - target.x
                pull_dir_y = player_y - target.y
                pull_dist = math.hypot(pull_dir_x, pull_dir_y)
                
                if pull_dist > 0:
                    # Normalize and scale by pull strength
                    pull_x = (pull_dir_x / pull_dist) * min(pull_strength, pull_dist)
                    pull_y = (pull_dir_y / pull_dist) * min(pull_strength, pull_dist)
                    
                    # Apply pull
                    target.x += pull_x
                    target.y += pull_y
                    print(f"[Chain] Pulled enemy by ({pull_x:.0f}, {pull_y:.0f})")

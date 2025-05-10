# skill.py
import time
from enum import Enum, auto
import math
import pygame
from utils import draw_hp_bar, angle_diff
from animation import CharacterAnimation
from entity import Entity  # Import the Entity base class
from config import Config as C
from visual_effects import VisualEffect

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
        self.owner = None  # Reference to the owner entity (e.g., player)

    def _get_color_from_element(self, element):
        if element in C.ELEMENT_COLORS:
            return C.ELEMENT_COLORS[element]['primary']
        return C.WHITE  # Default fallback
    
    def is_off_cooldown(self, current_time):
        if current_time is None:
            current_time = time.time()
        return (current_time - self.last_use_time) >= self.cooldown
    
    def trigger_cooldown(self):
        self.last_use_time = time.time()

class ProjectileEntity(Entity):
    """Projectile entity that inherits from Entity base class"""
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
        self.explosion_radius = skill.radius  # Use skill radius for explosion
        self.explosion_damage = skill.damage  # Use skill damage for explosion
        
        # Create proper sprite image with glow effect
        size = max(10, self.radius * 2)
        self.image = pygame.Surface((size, size), pygame.SRCALPHA)
        
        # Draw projectile with glow effect
        glow_radius = size // 2
        glow_color = (*self.color, 100)  # Semi-transparent
        pygame.draw.circle(self.image, glow_color, (size//2, size//2), glow_radius)
        pygame.draw.circle(self.image, self.color, (size//2, size//2), self.radius)
        pygame.draw.circle(self.image, (255, 255, 255), (size//2, size//2), self.radius, 1)
        
        # Set rect
        self.rect = self.image.get_rect(center=(self.pos.x, self.pos.y))
        
        # Calculate velocity vector using pygame.math.Vector2
        direction = pygame.math.Vector2(target_x - start_x, target_y - start_y)
        if direction.length() > 0:
            direction.normalize_ip()
        self.direction = direction

    def update(self, dt, enemies):
        """Update projectile position and check collisions"""
        if not self.alive:
            return False

        # Move using Vector2 and update position
        movement = self.direction * self.speed * dt
        self.pos += movement
        self.rect.center = (int(self.pos.x), int(self.pos.y))

        # Check screen bounds collision
        if (self.pos.x < 0 or self.pos.x > C.WIDTH or 
            self.pos.y < 0 or self.pos.y > C.HEIGHT):
            return self.explode(enemies)

        # Check collision with enemies
        for enemy in enemies:
            if not enemy.alive:
                continue
                
            # Check approximate distance using Entity method
            dist = self.get_distance_to(enemy.x, enemy.y)
            if dist <= (self.radius + enemy.radius):
                # Apply direct damage to the hit enemy
                enemy.take_damage(self.damage)
                return self.explode(enemies)

        return True

    def explode(self, enemies):
        """Create explosion effect and damage nearby enemies"""
        explosion = VisualEffect(
            self.pos.x, 
            self.pos.y, 
            "explosion", 
            self.color, 
            self.explosion_radius,
            0.3
        )

        # Damage nearby enemies
        for enemy in enemies:
            if not enemy.alive:
                continue
                
            # Use the Entity's get_distance_to method
            dist = self.get_distance_to(enemy.x, enemy.y)
            if dist <= self.explosion_radius:
                enemy.take_damage(self.explosion_damage)
            
        # Set alive to false will trigger the kill() method
        self.alive = False
        return explosion

    def draw(self, surface):
        """Draw the projectile with glow effect"""
        if not self.alive:
            return
            
        # Display explosion radius if enabled
        if hasattr(self, 'explosion_radius') and self.explosion_radius > 0:
            # Create a transparent surface for the explosion radius
            radius_surf = pygame.Surface((self.explosion_radius * 2, self.explosion_radius * 2), pygame.SRCALPHA)
            # Draw a semi-transparent circle
            pygame.draw.circle(radius_surf, (*self.color, 30), (self.explosion_radius, self.explosion_radius), self.explosion_radius)
            # Draw circle outline
            pygame.draw.circle(radius_surf, (*self.color, 80), (self.explosion_radius, self.explosion_radius), self.explosion_radius, 2)
            # Blit the radius surface
            surface.blit(radius_surf, (int(self.pos.x - self.explosion_radius), int(self.pos.y - self.explosion_radius)))
        
        # Draw the projectile
        surface.blit(self.image, self.rect)

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
    def __init__(self, x, y, skill, attack_radius):
        super().__init__(
            x=x,
            y=y,
            radius=12,
            max_health=50, # Example health
            speed=max(120, skill.speed * 60), # Ensure minimum speed of 120 pixels per second
            color=skill.color,
            attack_radius=attack_radius
        )
        self.damage = skill.damage
        self.element = skill.element
     
        self.animation = CharacterAnimation(
            sprite_sheet_path=C.SHADOW_SUMMON_SPRITE_PATH,
            config=C.SHADOW_SUMMON_ANIMATION_CONFIG,
            sprite_width=C.SPRITE_SIZE,
            sprite_height=C.SPRITE_SIZE
        )
        self.state = 'idle'
        self.animation.set_state('idle', force_reset=True)

    def update(self, dt, enemies):
        """Update summon behavior: find target, move, attack"""
        # If entity is dead or in special animation states, let base class handle it
        if not self.alive or self.state in ['dying', 'hurt', 'sweep']:
            super().update_animation(dt)
            return self.alive
        
        # Find closest enemy (target)
        target = None
        min_dist = float('inf')
        for enemy in enemies:
            if enemy.alive:
                dist = self.get_distance_to(enemy.x, enemy.y)
                if dist < min_dist:
                    min_dist = dist
                    target = enemy

        # Update attack timer
        if self.attack_timer > 0:
            self.attack_timer -= dt

        # Attack target if in range and cooldown ready
        if target and min_dist < self.attack_radius and self.attack_timer <= 0:
            # Set attack animation
            self.state = 'sweep'
            self.animation.set_state('sweep', force_reset=True)
            
            # Calculate attack animation duration
            animations_length = len(self.animation.config['sweep']['animations'])
            attack_duration = self.animation.config['sweep']['duration'] * animations_length
            self.attack_animation_timer = attack_duration
            
            # Perform the attack
            super().attack(target)

            # Add visual effect for attack
            if hasattr(self, 'owner') and hasattr(self.owner, 'game') and self.owner.game and hasattr(self.owner.game, 'effects'):
                hit_effect = VisualEffect(target.x, target.y, "explosion", self.color, 15, 0.2)
                self.owner.game.effects.append(hit_effect)
                
            self.attack_timer = self.attack_cooldown
            return True
        
        # Move toward target if not attacking
        elif target:
            # Calculate direction
            self.dx, self.dy = self.get_direction_to(target.x, target.y)
            
            # Set walking animation if not already
            if self.state != 'walk':
                self.state = 'walk'
                self.animation.set_state('walk')
            
            # Move toward target
            self.move(self.dx, self.dy, dt)
            
            # Update animation with movement direction
            self.animation.update(dt, self.dx, self.dy)
        else:
            # If no target, go to idle
            if self.state != 'idle':
                self.state = 'idle'
                self.animation.set_state('idle')
            self.animation.update(dt)
        
        return True

class Summon(BaseSkill):
    """Summon skill that creates SummonEntity instances"""
    def __init__(self, name, element, damage, speed, radius, duration, cooldown, description, sprite_path, animation_config, attack_radius):
        super().__init__(name, element, SkillType.SUMMON, cooldown, description)
        self.damage = damage
        self.speed = speed
        self.radius = radius
        self.duration = duration
        self.sprite_path = sprite_path
        self.animation_config = animation_config
        self.attack_radius = attack_radius

    @staticmethod
    def create(skill, x, y, attack_radius):
        """Create a SummonEntity instance"""
        return SummonEntity(x, y, skill, attack_radius)
    
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
        
        # If heal_summons is True and summons are provided, heal them too
        if getattr(skill, 'heal_summons', True) and summons:
            for summon in summons:
                if summon.alive and summon.health < summon.max_health:
                    summon.heal(skill.heal_amount)
        
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
        hit_count = 0
        for enemy in enemies:
            if not enemy.alive: continue
            
            # Calculate distance to enemy
            dist = math.hypot(enemy.x - x, enemy.y - y)
            if dist <= skill.radius:
                enemy.take_damage(skill.damage)
                hit_count += 1
                
        return hit_count > 0

class Slash(BaseSkill):
    """Slash attack skill implementation"""
    def __init__(self, name, element, damage, radius, duration, cooldown, description):
        super().__init__(name, element, SkillType.SLASH, cooldown, description)
        self.damage = damage
        self.radius = radius
        self.duration = duration

    @staticmethod
    def activate(skill, player_x, player_y, target_x, target_y, enemies, start_angle=None, sweep_angle=None):
        """Apply damage to enemies in an arc"""
        # Calculate target angle (used for debugging or if start/sweep not provided)
        target_angle = math.atan2(target_y - player_y, target_x - player_x)
        
        # If no start/sweep angles provided, calculate default 60-degree arc
        if start_angle is None or sweep_angle is None:
            arc_width = math.pi / 3  # 60 degree arc
            start_angle = target_angle - arc_width/2
            sweep_angle = arc_width
        
        # Calculate end angle for hit detection
        end_angle = start_angle + sweep_angle
        
        hit_count = 0
        for enemy in enemies:
            if not enemy.alive: 
                continue
                
            # Calculate distance and angle to enemy
            dx = enemy.x - player_x
            dy = enemy.y - player_y
            dist = math.hypot(dx, dy)
            
            if dist <= skill.radius:
                # Calculate enemy angle
                enemy_angle = math.atan2(dy, dx)
                enemy_angle_deg = math.degrees(enemy_angle)
                
                # Normalize all angles to 0-360 degree range for comparison
                start_deg = (math.degrees(start_angle) + 360) % 360
                end_deg = (math.degrees(end_angle) + 360) % 360
                enemy_deg = (enemy_angle_deg + 360) % 360
                
                # Check if enemy is within the arc
                is_in_arc = False
                if start_deg <= end_deg:
                    # Simple case: start to end
                    is_in_arc = start_deg <= enemy_deg <= end_deg
                else:
                    # Arc crosses 0/360 boundary
                    is_in_arc = enemy_deg >= start_deg or enemy_deg <= end_deg
                
                if is_in_arc:
                    enemy.take_damage(skill.damage)
                    hit_count += 1
        
        return hit_count > 0

class Chain(BaseSkill):
    """Chain attack skill implementation"""
    def __init__(self, name, element, damage, radius, duration, pull, cooldown, description, max_targets=3, chain_range=150):
        super().__init__(name, element, SkillType.CHAIN, cooldown, description)
        self.damage = damage
        self.radius = radius
        self.duration = duration
        self.pull = pull
        self.max_targets = max_targets  # Maximum number of targets to chain to
        self.chain_range = chain_range  # Range for chaining between targets
    
    @staticmethod
    def activate(skill, player_x, player_y, target_x, target_y, enemies):
        """Apply damage to enemies in a chain, hitting multiple targets in sequence"""
        # Find all valid targets
        valid_enemies = [e for e in enemies if e.alive]
        if not valid_enemies:
            return False
            
        hit_enemies = []  # Track which enemies we've already hit
        effects = []  # Collect all effects created
        
        # Find the initial target (enemy in the direction of click)
        first_target = None
        min_dist = float('inf')
        
        for enemy in valid_enemies:
            dist = math.hypot(enemy.x - player_x, enemy.y - player_y)
            if dist <= skill.radius:
                # Check if enemy is in the general direction of the target point
                dx = enemy.x - player_x
                dy = enemy.y - player_y
                enemy_angle = math.atan2(dy, dx)
                target_angle = math.atan2(target_y - player_y, target_x - player_x)
                diff = abs(angle_diff(target_angle, enemy_angle))
                
                # Consider enemies in a 60-degree cone in target direction
                if diff <= math.pi / 3 and dist < min_dist:
                    min_dist = dist
                    first_target = enemy
        
        if not first_target:
            return effects
            
        # Hit the first target
        current_target = first_target
        hit_enemies.append(current_target)
        current_target.take_damage(skill.damage)
        
        # Apply pull effect if enabled to the first target
        if skill.pull:
            pull_strength = 60  # Pull strength in pixels
            pull_dir_x = player_x - current_target.x
            pull_dir_y = player_y - current_target.y
            pull_dist = math.hypot(pull_dir_x, pull_dir_y)
            
            if pull_dist > 0:
                # Normalize and scale by pull strength
                pull_x = (pull_dir_x / pull_dist) * min(pull_strength, pull_dist)
                pull_y = (pull_dir_y / pull_dist) * min(pull_strength, pull_dist)
                
                # Apply pull
                current_target.x += pull_x
                current_target.y += pull_y
        
        # Create visual effect for the chain
        chain_effect = VisualEffect(
            player_x, 
            player_y, 
            "line",  # Assuming there's a line effect type
            skill.color,
            10,  # Thickness
            0.2,  # Duration
            end_x=current_target.x,
            end_y=current_target.y
        )
        effects.append(chain_effect)
        
        # Now chain to additional targets
        last_x, last_y = current_target.x, current_target.y
        
        # Chain to additional targets up to max_targets
        for _ in range(1, getattr(skill, 'max_targets', 3)):
            # Find the next closest enemy that hasn't been hit yet
            next_target = None
            min_chain_dist = float('inf')
            
            for enemy in valid_enemies:
                if enemy in hit_enemies:
                    continue  # Skip already hit enemies
                    
                chain_dist = math.hypot(enemy.x - last_x, enemy.y - last_y)
                if chain_dist <= getattr(skill, 'chain_range', 150):
                    if chain_dist < min_chain_dist:
                        min_chain_dist = chain_dist
                        next_target = enemy
            
            # If no more targets in range, stop chaining
            if not next_target:
                break
                
            # Hit the next target
            hit_enemies.append(next_target)
            next_target.take_damage(skill.damage)
            
            # Create visual effect for the chain
            chain_effect = VisualEffect(
                last_x, 
                last_y, 
                "line",
                skill.color,
                10,
                0.2,
                end_x=next_target.x,
                end_y=next_target.y
            )
            effects.append(chain_effect)
            
            # Update last position for next chain
            last_x, last_y = next_target.x, next_target.y
            
        return effects

# skill.py
import time
from enum import Enum, auto
import math
import pygame
from utils import Utils
from entity import Entity
from config import Config
from visual_effects import VisualEffect
from animation import Animation
from resources import Resources
from config import Config

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
        self.effect_manager = None  # Will be set by the game

    def _get_color_from_element(self, element):
        if element in Config.ELEM_COLORS:
            return Config.ELEM_COLORS[element]['primary']
        return Config.WHITE  # Default fallback
    
    def is_off_cooldown(self, current_time):
        if current_time is None:
            current_time = time.time()
        return (current_time - self.last_use_time) >= self.cooldown
    
    def trigger_cooldown(self):
        self.last_use_time = time.time()

    def set_effect_manager(self, effect_manager):
        """Set the effect manager for this skill"""
        self.effect_manager = effect_manager

    def add_effect(self, effect):
        """Add a visual effect to the effect manager"""
        if self.effect_manager:
            self.effect_manager.add_effect(effect)

    @staticmethod
    def _calculate_spawn_position(player_x, player_y, target_x, target_y, distance):
        """Calculate spawn position for projectiles and summons"""
        dx = target_x - player_x
        dy = target_y - player_y
        dist = math.hypot(dx, dy) or 1
        spawn_x = player_x + (dx / dist) * distance
        spawn_y = player_y + (dy / dist) * distance
        return spawn_x, spawn_y

class ProjectileEntity(Entity):
    def __init__(self, start_x, start_y, target_x, target_y, skill):
        self.color = skill.color
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

        # Calculate velocity
        dx = target_x - start_x
        dy = target_y - start_y
        dist = math.hypot(dx, dy)
        if dist == 0: dist = 1
        self.dx = dx / dist  # Normalized direction
        self.dy = dy / dist  # Normalized direction
        
        # Set to NoAnimationState explicitly
        self.state_machine.change_state("none")

    def update(self, dt, enemies):
        """Update projectile position and check collisions"""
        if not self.alive:
            return False

        # Move using normalized direction and speed
        self.x += self.dx * self.speed * dt
        self.y += self.dy * self.speed * dt

        # Check screen bounds collision
        if (self.x < 0 or self.x > Config.WIDTH or 
            self.y < 0 or self.y > Config.HEIGHT):
            self.explode(enemies)
            return False

        # Check collision with enemies
        for enemy in enemies:
            if not enemy.alive:
                continue
            dx = enemy.x - self.x
            dy = enemy.y - self.y
            dist = math.hypot(dx, dy)
            if dist <= (self.radius + enemy.radius):
                # Apply direct damage to the hit enemy
                enemy.take_damage(self.damage)
                self.explode(enemies)
                return False

        # Update state machine
        super().update(dt)
        return True

    def explode(self, enemies):
        """Create explosion effect and damage nearby enemies"""
        if hasattr(self, 'owner') and hasattr(self.owner, 'game') and self.owner.game and hasattr(self.owner.game, 'effects'):
            # Create explosion visual effect
            explosion = VisualEffect(
                self.x, 
                self.y, 
                "explosion", 
                self.color, 
                self.explosion_radius,  # Use explosion radius
                0.3   # Duration
            )
            self.owner.game.effects.append(explosion)

        # Damage nearby enemies
        hit_count = 0
        for enemy in enemies:
            if not enemy.alive:
                continue
            dx = enemy.x - self.x
            dy = enemy.y - self.y
            dist = math.hypot(dx, dy)
            if dist <= self.explosion_radius:
                hit_count += 1
                enemy.take_damage(self.explosion_damage)

        self.alive = False

    def draw(self, surface):
        """Draw the projectile with a glow effect"""
        if self.alive:
            # Draw glow effect (larger, semi-transparent circle)
            glow_surface = pygame.Surface((self.radius * 3, self.radius * 3), pygame.SRCALPHA)
            glow_color = (*self.color, 100)  # Add alpha channel
            pygame.draw.circle(glow_surface, glow_color, (self.radius * 1.5, self.radius * 1.5), self.radius * 1.5)
            surface.blit(glow_surface, (int(self.x - self.radius * 1.5), int(self.y - self.radius * 1.5)))
            # Draw main projectile
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)
            # Draw outline
            pygame.draw.circle(surface, (255, 255, 255), (int(self.x), int(self.y)), self.radius, 1)
            # Draw explosion radius if debug mode is enabled
            if hasattr(self, 'explosion_radius') and self.explosion_radius > 0:
                # Create a transparent surface for the explosion radius
                radius_surf = pygame.Surface((self.explosion_radius * 2, self.explosion_radius * 2), pygame.SRCALPHA)
                # Draw a semi-transparent circle
                pygame.draw.circle(radius_surf, (*self.color, 30), (self.explosion_radius, self.explosion_radius), self.explosion_radius)
                # Draw circle outline
                pygame.draw.circle(radius_surf, (*self.color, 80), (self.explosion_radius, self.explosion_radius), self.explosion_radius, 2)
                # Blit the radius surface
                surface.blit(radius_surf, (int(self.x - self.explosion_radius), int(self.y - self.explosion_radius)))

class Projectile(BaseSkill):
    """Projectile skill that creates ProjectileEntity instances"""
    def __init__(self, name, element, damage, speed, radius, duration, cooldown, description):
        super().__init__(name, element, SkillType.PROJECTILE, cooldown, description)
        self.damage = damage
        self.speed = speed
        self.radius = radius
        self.duration = duration
    
    def activate(self, start_x, start_y, target_x, target_y, enemies):
        """Create a projectile instance"""
        projectile = ProjectileEntity(start_x, start_y, target_x, target_y, self)
        # Add visual effect
        self.add_effect(VisualEffect(
            start_x, start_y,
            "explosion",
            self.color,
            radius=self.radius,
            duration=0.2
        ))
        return projectile
    
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
        # Set up animation before calling parent constructor
        try:
            sprite_path = getattr(skill, 'sprite_path', Config.SHADOW_SUMMON_SPRITE_PATH)
            self.animation = Animation(
                name="summon",
                sprite_sheet_path=sprite_path,
                sprite_width=Config.SPRITE_SIZE,
                sprite_height=Config.SPRITE_SIZE
            )
        except Exception as e:
            print(f"[SummonEntity] Error loading animation: {e}")
            raise Exception(f"Failed to load summon animation: {e}")
        
        # Call parent constructor with animation set up
        super().__init__(
            x=x,
            y=y,
            radius=12,
            max_health=50,
            speed=max(120, skill.speed * 60), # Ensure minimum speed
            attack_radius=attack_radius
        )
        
        # Set summon-specific properties
        self.damage = skill.damage
        self.element = skill.element
        self.attack_cooldown = 1.0
        self.attack_timer = 0.0
        self.color = skill.color
        
        # Ensure we start in idle state
        self.state_machine.change_state("idle")

    def update(self, dt, enemies):
        """Update summon behavior: find target, move, attack"""
        # Check if alive first
        if not self.alive or self.health <= 0:
            # Just update the state machine
            self.state_machine.update(dt)
            return False

        # Get current state
        current_state = self.state_machine.get_state_name()
        
        # If in a restricted movement state, just update the state machine
        if current_state in ["sweep", "hurt", "dying"]:
            self.state_machine.update(dt)
            return True

        # Update attack timer
        if self.attack_timer > 0:
            self.attack_timer -= dt

        # Find closest enemy
        closest_enemy = None
        min_dist = float('inf')
        for enemy in enemies:
            if enemy.alive:
                dist = math.hypot(enemy.x - self.x, enemy.y - self.y)
                if dist < min_dist:
                    min_dist = dist
                    closest_enemy = enemy

        # Try to attack if in range
        if closest_enemy and min_dist < self.attack_radius and self.attack_timer <= 0:
            # Attack animation
            self.state_machine.change_state("sweep")
            
            # Perform attack
            closest_enemy.take_damage(self.damage)
            self.attack_timer = self.attack_cooldown
            
            # Add visual effect
            if hasattr(self, 'owner') and hasattr(self.owner, 'game') and self.owner.game and hasattr(self.owner.game, 'effect_manager'):
                hit_effect = VisualEffect(closest_enemy.x, closest_enemy.y, "explosion", self.color, 15, 0.2)
                self.owner.game.effect_manager.add_effect(hit_effect)
            
            return True

        # Move toward target if not attacking
        if closest_enemy and min_dist > 0:
            # Calculate direction
            self.dx, self.dy = self.get_direction_to(closest_enemy.x, closest_enemy.y)
            
            # Set walking animation
            if current_state != "walk":
                self.state_machine.change_state("walk")
            
            # Move toward target
            self.move(self.dx, self.dy, dt)
        else:
            # If no target, set to idle
            if current_state != "idle":
                self.state_machine.change_state("idle")

        # Update state machine
        self.state_machine.update(dt, dx=self.dx, dy=self.dy)
        
        # Keep within screen bounds
        self.x = max(self.radius, min(Config.WIDTH - self.radius, self.x))
        self.y = max(self.radius, min(Config.HEIGHT - self.radius, self.y))
        
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
                self.state_machine.change_state("dying")
            else:
                # Only show hurt animation if not already in a more important state
                if self.state_machine.get_state_name() not in ['dying', 'sweep']:
                    self.state_machine.change_state("hurt")

    def draw(self, surface):
        """Draw summon with sprite, includes HP bar"""
        if not self.alive:
            return
            
        # Get current sprite
        current_sprite = self.animation.get_current_sprite()
        
        if current_sprite:
            # Calculate draw position
            draw_x = self.x - self.animation.sprite_width / 2
            draw_y = self.y - self.animation.sprite_height / 2
            
            # Draw sprite
            surface.blit(current_sprite, (int(draw_x), int(draw_y)))
            
            # Draw HP bar if not dying
            if self.state_machine.get_state_name() != "dying":
                self.draw_health_bar(surface)

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

    def activate(self, player_x, player_y, target_x, target_y, enemies):
        """Create a SummonEntity instance"""
        x, y = self._calculate_spawn_position(player_x, player_y, target_x, target_y, self.radius)
        summon = SummonEntity(x, y, self, self.attack_radius)
        # Add visual effect
        self.add_effect(VisualEffect(
            x, y,
            "explosion",
            self.color,
            radius=self.radius,
            duration=0.3
        ))
        return summon

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
    def __init__(self, name, element, heal_amount, radius, cooldown, description, heal_summons=False):
        super().__init__(name, element, SkillType.HEAL, cooldown, description)
        self.heal_amount = heal_amount
        self.radius = radius
        self.heal_summons = heal_summons

    def activate(self, player, summons=None):
        """Apply healing to player and optionally summons"""
        # Heal player
        player.heal(self.heal_amount)
        self.add_effect(VisualEffect(
            player.x, player.y,
            "heal",
            self.color,
            radius=self.radius,
            duration=0.5
        ))

        # Heal summons if specified
        if self.heal_summons and summons:
            for summon in summons:
                if summon.alive:
                    summon.heal(self.heal_amount)
                    self.add_effect(VisualEffect(
                        summon.x, summon.y,
                        "heal",
                        self.color,
                        radius=self.radius,
                        duration=0.5
                    ))

class AOE(BaseSkill):
    """Area of Effect skill implementation"""
    def __init__(self, name, element, damage, radius, duration, cooldown, description):
        super().__init__(name, element, SkillType.AOE, cooldown, description)
        self.damage = damage
        self.radius = radius
        self.duration = duration

    def activate(self, target_x, target_y, enemies):
        """Apply damage to enemies in area"""
        hit_count = 0
        for enemy in enemies:
            if not enemy.alive:
                continue
            dx = enemy.x - target_x
            dy = enemy.y - target_y
            dist = math.hypot(dx, dy)
            if dist <= self.radius:
                enemy.take_damage(self.damage)
                hit_count += 1

        # Add visual effect
        self.add_effect(VisualEffect(
            target_x, target_y,
            "explosion",
            self.color,
            radius=self.radius,
            duration=self.duration
        ))

class Slash(BaseSkill):
    """Slash attack skill implementation"""
    def __init__(self, name, element, damage, radius, duration, cooldown, description):
        super().__init__(name, element, SkillType.SLASH, cooldown, description)
        self.damage = damage
        self.radius = radius
        self.duration = duration

    def activate(self, player_x, player_y, target_x, target_y, enemies):
        """Apply damage to enemies in an arc"""
        angle = math.atan2(target_y - player_y, target_x - player_x)
        arc_width = math.pi / 3
        start_angle = angle - (arc_width / 2)
        sweep_angle = arc_width

        hit_count = 0
        for enemy in enemies:
            if not enemy.alive:
                continue
            dx = enemy.x - player_x
            dy = enemy.y - player_y
            dist = math.hypot(dx, dy)
            if dist <= self.radius:
                enemy_angle = math.atan2(dy, dx)
                if Utils.angle_diff(enemy_angle, angle) <= arc_width / 2:
                    enemy.take_damage(self.damage)
                    hit_count += 1

        # Add visual effect
        self.add_effect(VisualEffect(
            player_x, player_y,
            "slash",
            self.color,
            radius=self.radius,
            duration=self.duration,
            start_angle=start_angle,
            sweep_angle=sweep_angle
        ))

class Chain(BaseSkill):
    """Chain lightning skill implementation"""
    def __init__(self, name, element, damage, radius, duration, cooldown, description, chain_count=3):
        super().__init__(name, element, SkillType.CHAIN, cooldown, description)
        self.damage = damage
        self.radius = radius
        self.duration = duration
        self.chain_count = chain_count

    def activate(self, player_x, player_y, target_x, target_y, enemies):
        """Apply chain lightning damage"""
        if not enemies:
            return

        # Find initial target
        current_x, current_y = player_x, player_y
        hit_enemies = set()

        for _ in range(self.chain_count):
            # Find closest unhit enemy
            closest_enemy = None
            min_dist = float('inf')
            for enemy in enemies:
                if enemy.alive and enemy not in hit_enemies:
                    dx = enemy.x - current_x
                    dy = enemy.y - current_y
                    dist = math.hypot(dx, dy)
                    if dist < min_dist and dist <= self.radius:
                        min_dist = dist
                        closest_enemy = enemy

            if not closest_enemy:
                break

            # Apply damage and add to hit set
            closest_enemy.take_damage(self.damage)
            hit_enemies.add(closest_enemy)

            # Add visual effect
            self.add_effect(VisualEffect(
                current_x, current_y,
                "line",
                self.color,
                radius=self.radius,
                duration=self.duration,
                end_x=closest_enemy.x,
                end_y=closest_enemy.y
            ))

            # Update current position for next chain
            current_x, current_y = closest_enemy.x, closest_enemy.y

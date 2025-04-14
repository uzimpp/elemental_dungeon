import pygame
import math
import time
from utils import draw_hp_bar
from entity import Entity
from animation import CharacterAnimation
from config import (ENEMY_SPRITE_PATH, ENEMY_ANIMATION_CONFIG, WIDTH, HEIGHT)


class Enemy(Entity):
    """Base class for all enemy types."""
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
        # Calculate health with wave multiplier
        max_health = base_hp * (1 + (wave_number - 1) * wave_multiplier)
        
        # Call parent class constructor
        super().__init__(x, y, radius, max_health, base_speed, color)
        
        # Enemy specific attributes
        self.wave_number = wave_number
        self.damage = damage
        self.attack_cooldown = attack_cooldown
        self.attack_timer = 0.0
        
        # Animation setup
        self.animation = CharacterAnimation(
            sprite_sheet_path=ENEMY_SPRITE_PATH,
            config=ENEMY_ANIMATION_CONFIG,
            sprite_width=32,
            sprite_height=32
        )
        self.state = 'idle'
        self.attack_animation_timer = 0.0
    
    def update(self, player, dt):
        """Update method to be overridden by subclasses."""
        # Handle death animation and state first
        if not self.alive or self.health <= 0:
            self._handle_death_animation(dt)
            return
            
        # Handle hurt and attack animations
        if self.state in ['hurt', 'sweep']:
            self._handle_action_animation(dt, player)
            return
        
        # Find target and update movement/attack
        self._find_and_approach_target(player, dt)
        
        # Update the animation with current direction
        self.animation.update(dt, self.dx, self.dy)
    
    def _handle_death_animation(self, dt):
        """Handle death animation state and timing."""
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
    
    def _handle_action_animation(self, dt, player):
        """Handle hurt and attack animation states."""
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
                closest_type, closest_dist, closest_obj = self.get_closest_target(player)
                if closest_obj and closest_dist > 0:
                    self.state = 'walk'
                    self.animation.set_state('walk', force_reset=True)
                else:
                    self.state = 'idle'
                    self.animation.set_state('idle', force_reset=True)
    
    def _find_and_approach_target(self, player, dt):
        """Find the closest target and move toward it or attack it."""
        # This is the default behavior for melee enemies
        # For ranged enemies, this will be overridden
        closest_type, closest_dist, closest_obj = self.get_closest_target(player)

        # Update attack timer
        if self.attack_timer > 0:
            self.attack_timer -= dt

        # Try to attack if we can
        if closest_obj and closest_dist < (self.radius + closest_obj[3]) and self.attack_timer <= 0:
            self._perform_attack(closest_type, closest_obj)
            return  # Don't move after deciding to attack

        # Move toward target if not attacking
        if closest_obj and closest_dist > 0:
            tx = closest_obj[1]
            ty = closest_obj[2]
            self.dx, self.dy = self.get_direction_to(tx, ty)
            
            # Set walking animation if not already
            if self.state != 'walk':
                self.state = 'walk'
                self.animation.set_state('walk')
            
            self.move(self.dx, self.dy, dt)
        else:
            # If no target, set to idle
            if self.state != 'idle':
                self.state = 'idle'
                self.animation.set_state('idle')
    
    def _perform_attack(self, target_type, target_obj):
        """Perform attack action."""
        # Set attack animation
        self.state = 'sweep'  # Use sweep as attack animation
        self.animation.set_state('sweep', force_reset=True)
        
        # Calculate attack animation duration
        animations_length = len(self.animation.config['sweep']['animations'])
        attack_duration = self.animation.config['sweep']['duration'] * animations_length
        self.attack_animation_timer = attack_duration
        
        # Deal damage
        self.attack(target_type, target_obj[4])  # Pass the actual object
        self.attack_timer = self.attack_cooldown
    
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
            dist = self.get_distance_to(t[1], t[2])
            if dist < closest_dist:
                closest_dist = dist
                closest_type = t[0]
                closest_obj = t

        return closest_type, closest_dist, closest_obj

    def get_distance_to(self, other_x, other_y):
        """Calculate distance to another point"""
        return math.hypot(other_x - self.x, other_y - self.y)

    def get_direction_to(self, target_x, target_y):
        """Calculate direction (dx, dy) to a target point, normalized"""
        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.hypot(dx, dy)
        if distance == 0:
            return 0, 0
        return dx / distance, dy / distance

    def attack(self, target_type, target):
        """Deal damage to the target."""
        target.take_damage(self.damage)

    def take_damage(self, amount):
        """Override take_damage to play hurt animation"""
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

    def draw(self, surf):
        # Get the current sprite from the animation system
        current_sprite = self.animation.get_current_sprite()

        if current_sprite:
            # Calculate top-left position for blitting (center the sprite)
            draw_x = self.x - self.animation.sprite_width / 2
            draw_y = self.y - self.animation.sprite_height / 2

            # Draw the sprite
            surf.blit(current_sprite, (int(draw_x), int(draw_y)))
        else:
            # Fallback to triangle if no sprite available
            self.draw_triangle(surf)
        
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

    def move_along_path(self, path, dt):
        """Move along a given path"""
        if not path:
            return
        
        # Get next waypoint
        target_x, target_y = path[0]
        
        # Calculate direction and distance
        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.hypot(dx, dy)
        
        # If close enough, move to next waypoint
        if distance < self.speed * dt:
            if len(path) > 1:
                self.path = path[1:]
            else:
                self.path = []
            return
        
        # Normalize direction and move
        if distance > 0:
            self.dx = dx / distance
            self.dy = dy / distance
            self.move(self.dx, self.dy, dt)


class MeleeEnemy(Enemy):
    """Close-range enemy that moves toward the player and attacks when in range."""
    def __init__(
            self,
            x,
            y,
            wave_number,
            radius=15,
            base_speed=105,  # 1.75 * 60
            base_hp=50,
            wave_multiplier=0.2,
            color=(255, 0, 0),
            damage=5,
            attack_cooldown=1):
        super().__init__(
            x, y, wave_number, radius, base_speed, base_hp,
            wave_multiplier, color, damage, attack_cooldown
        )
        # Melee-specific attributes could be added here


class RangedEnemy(Enemy):
    """Ranged enemy that keeps distance and shoots projectiles."""
    def __init__(
            self,
            x,
            y,
            wave_number,
            radius=15,
            base_speed=90,  # 1.5 * 60 (slightly slower)
            base_hp=40,     # Less HP than melee
            wave_multiplier=0.2,
            color=(0, 0, 255),  # Blue to distinguish
            damage=3,            # Less damage per hit
            attack_cooldown=2,   # Longer cooldown
            projectile_speed=300,
            attack_range=250):    # Range at which to stop and attack
        super().__init__(
            x, y, wave_number, radius, base_speed, base_hp,
            wave_multiplier, color, damage, attack_cooldown
        )
        self.projectile_speed = projectile_speed
        self.attack_range = attack_range
        self.projectiles = []
    
    def _find_and_approach_target(self, player, dt):
        """Override to implement ranged behavior."""
        closest_type, closest_dist, closest_obj = self.get_closest_target(player)

        # Update attack timer
        if self.attack_timer > 0:
            self.attack_timer -= dt
            
        # Update projectiles
        for p in self.projectiles:
            p.update(dt)
        self.projectiles = [p for p in self.projectiles if p.active]

        # If target exists
        if closest_obj:
            tx = closest_obj[1]
            ty = closest_obj[2]
            
            # If in attack range, stop and shoot
            if closest_dist <= self.attack_range and self.attack_timer <= 0:
                # Face the target
                self.dx, self.dy = self.get_direction_to(tx, ty)
                
                # Perform ranged attack
                self._perform_ranged_attack(tx, ty)
                return
            
            # If too close, move away
            elif closest_dist < self.attack_range * 0.5:
                # Get direction away from target
                away_dx, away_dy = self.get_direction_to(tx, ty)
                self.dx, self.dy = -away_dx, -away_dy
                
                # Set walking animation
                if self.state != 'walk':
                    self.state = 'walk'
                    self.animation.set_state('walk')
                
                self.move(self.dx, self.dy, dt)
            
            # If too far, move closer (but not too close)
            elif closest_dist > self.attack_range:
                self.dx, self.dy = self.get_direction_to(tx, ty)
                
                # Set walking animation
                if self.state != 'walk':
                    self.state = 'walk'
                    self.animation.set_state('walk')
                
                self.move(self.dx, self.dy, dt)
            
            # Otherwise maintain distance
            else:
                if self.state != 'idle':
                    self.state = 'idle'
                    self.animation.set_state('idle')
        else:
            # No target, set to idle
            if self.state != 'idle':
                self.state = 'idle'
                self.animation.set_state('idle')
    
    def _perform_ranged_attack(self, target_x, target_y):
        """Perform a ranged attack by firing a projectile."""
        # Set "shoot_arrow" animation
        self.state = 'shoot_arrow'
        self.animation.set_state('shoot_arrow', force_reset=True)
        
        # Calculate animation duration
        animations_length = len(self.animation.config['shoot_arrow']['animations'])
        attack_duration = self.animation.config['shoot_arrow']['duration'] * animations_length
        self.attack_animation_timer = attack_duration
        
        # Create projectile
        from ranged_projectile import RangedProjectile
        projectile = RangedProjectile(
            self.x, self.y, 
            target_x, target_y, 
            self.projectile_speed, 
            self.damage, 
            self.color
        )
        self.projectiles.append(projectile)
        
        # Reset attack timer
        self.attack_timer = self.attack_cooldown
    
    def draw(self, surf):
        # Draw the enemy first
        super().draw(surf)
        
        # Then draw projectiles
        for p in self.projectiles:
            p.draw(surf)


class BossEnemy(Enemy):
    """Powerful boss enemy with special abilities."""
    def __init__(
            self,
            x,
            y,
            wave_number,
            radius=25,         # Larger size
            base_speed=75,     # Slower but more powerful
            base_hp=200,       # Much more HP
            wave_multiplier=0.2,
            color=(128, 0, 128),  # Purple to distinguish
            damage=10,           # More damage
            attack_cooldown=1.5): # Medium cooldown
        super().__init__(
            x, y, wave_number, radius, base_speed, base_hp,
            wave_multiplier, color, damage, attack_cooldown
        )
        # Boss-specific attributes
        self.special_attack_cooldown = 5.0
        self.special_attack_timer = 0.0
        self.phase = 1  # Boss phases
        
    def update(self, player, dt):
        # Update special attack timer
        if self.special_attack_timer > 0:
            self.special_attack_timer -= dt
            
        # If HP below 50%, enter phase 2
        if self.health < self.max_health * 0.5 and self.phase == 1:
            self.phase = 2
            self.damage *= 1.5  # Increase damage in phase 2
            
        # Call parent update to handle basic movement
        super().update(player, dt)
        
        # Check for special attack opportunity
        if self.special_attack_timer <= 0 and self.state not in ['hurt', 'sweep', 'dying']:
            self._perform_special_attack(player)
    
    def _perform_special_attack(self, player):
        """Perform a special boss attack."""
        # This is just a placeholder - implement actual special attack
        # Could be AOE, summon minions, etc.
        self.special_attack_timer = self.special_attack_cooldown
        
        # Example: AOE attack
        self.state = 'cast'
        self.animation.set_state('cast', force_reset=True)
        
        # Calculate animation duration
        animations_length = len(self.animation.config['cast']['animations'])
        attack_duration = self.animation.config['cast']['duration'] * animations_length
        self.attack_animation_timer = attack_duration
        
        # Deal damage in an area
        aoe_radius = 100
        dist_to_player = self.get_distance_to(player.x, player.y)
        if dist_to_player <= aoe_radius:
            player.take_damage(self.damage * 0.7)  # Reduced damage for AOE

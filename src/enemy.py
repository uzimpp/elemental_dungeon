import pygame
import math
import time
from utils import draw_hp_bar
from entity import Entity
from animation import CharacterAnimation
from config import (ENEMY_SPRITE_PATH, ENEMY_ANIMATION_CONFIG, SPRITE_SIZE, ATTACK_RADIUS)


class Enemy(Entity):
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
            attack_cooldown,
            attack_radius=ATTACK_RADIUS):
        # Call parent class constructor
        super().__init__(x, y, radius, base_hp * (wave_number * wave_multiplier), base_speed, color, attack_radius)
        
        # Enemy specific attributes
        self.damage = damage
        self.attack_cooldown = attack_cooldown
        self.attack_timer = 0.0
        self.attack_radius = attack_radius
        # Animation setup
        self.animation = CharacterAnimation(
            sprite_sheet_path=ENEMY_SPRITE_PATH,
            config=ENEMY_ANIMATION_CONFIG,
            sprite_width=SPRITE_SIZE,
            sprite_height=SPRITE_SIZE
        )
        self.state = 'idle'
        self.attack_animation_timer = 0.0

    def update(self, player, dt):
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
            return  # Don't do anything else if dying/dead
        
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
                    closest_type, closest_dist, closest_obj = self.get_closest_target(player)
                    if closest_obj and closest_dist > 0:
                        self.state = 'walk'
                        self.animation.set_state('walk', force_reset=True)
                    else:
                        self.state = 'idle'
                        self.animation.set_state('idle', force_reset=True)
        
        # Don't move or attack during hurt/attack animations
        if self.state in ['hurt', 'sweep']:
            return
        
        # 1) Check for attack BEFORE moving
        closest_type, closest_dist, closest_obj = self.get_closest_target(player)

        # Update attack timer
        if self.attack_timer > 0:
            self.attack_timer -= dt

        # Try to attack if we can - account for target's radius in the distance check
        if closest_obj:
            # Get target's radius to properly calculate attack distance
            target_radius = closest_obj[3]  # Index 3 contains the radius in closest_obj tuple
            
            # Effective attack range is the distance between centers minus both radii
            # If this is less than attack_radius, enemy can attack
            effective_distance = closest_dist - self.radius - target_radius
            
            if effective_distance <= self.attack_radius and self.attack_timer <= 0:
                # Set attack animation
                self.state = 'sweep'  # Use sweep as attack animation
                self.animation.set_state('sweep', force_reset=True)
                
                # Calculate attack animation duration
                animations_length = len(self.animation.config['sweep']['animations'])
                attack_duration = self.animation.config['sweep']['duration'] * animations_length
                self.attack_animation_timer = attack_duration
                
                # Perform the attack
                self.attack(closest_type, closest_obj[4])  # Pass the actual object
                self.attack_timer = self.attack_cooldown
                print(f"[Enemy] Attacking {closest_type} at distance {closest_dist:.1f} (effective: {effective_distance:.1f})")
                return  # Don't move after deciding to attack

        # 2) Then move toward target if not attacking
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
        
        # Update the animation with current direction
        self.animation.update(dt, self.dx, self.dy)

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
            print(f"[Enemy] Taking {amount} damage at ({self.x:.1f}, {self.y:.1f}), health: {self.health}/{self.max_health}")
            self.health -= amount
            print(f"[Enemy] Health after damage: {self.health}/{self.max_health}")
            
            if self.health <= 0:
                # Mark as dying but don't set alive=False yet (let animation finish)
                self.health = 0
                self.state = 'dying'
                self.animation.set_state('dying', force_reset=True)
                animations_length = len(self.animation.config['dying']['animations'])
                death_duration = self.animation.config['dying']['duration'] * animations_length
                self.attack_animation_timer = death_duration
                print(f"[Enemy] KILLED! Starting death animation for {death_duration:.2f}s")
            else:
                # Only show hurt animation if not already in a more important state
                if self.state not in ['dying', 'sweep']:
                    self.state = 'hurt'
                    self.animation.set_state('hurt', force_reset=True)
                    animations_length = len(self.animation.config['hurt']['animations'])
                    hurt_duration = self.animation.config['hurt']['duration'] * animations_length
                    self.attack_animation_timer = hurt_duration
                    print(f"[Enemy] Showing hurt animation for {hurt_duration:.2f}s")

    def draw(self, surf):
        # Get the current sprite from the animation system
        current_sprite = self.animation.get_current_sprite()

        if current_sprite:
            # Calculate top-left position for blitting (center the sprite)
            draw_x = self.x - self.animation.sprite_width / 2
            draw_y = self.y - self.animation.sprite_height / 2
            scale = 2  # Adjust scale factor as needed
            scaled_sprite = pygame.transform.scale(current_sprite, 
                                                  (self.animation.sprite_width * scale, 
                                                   self.animation.sprite_height * scale))
            # Draw the sprite
            surf.blit(scaled_sprite, (int(draw_x), int(draw_y)))
        else:
            raise Exception("[Enemy] No animation")
        
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

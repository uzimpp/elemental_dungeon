import pygame
import math
from utils import draw_hp_bar
from entity import Entity
from animation import Animation
from config import (ENEMY_SPRITE_PATH, ENEMY_ANIMATION_CONFIG,
                    SPRITE_SIZE, ATTACK_RADIUS)


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
            damage,
            attack_cooldown,
            attack_radius=ATTACK_RADIUS):
        # Set up animation before calling parent constructor
        self.animation = Animation(
            name="enemy",
            sprite_sheet_path=ENEMY_SPRITE_PATH,
            config=ENEMY_ANIMATION_CONFIG,
            sprite_width=SPRITE_SIZE,
            sprite_height=SPRITE_SIZE
        )
        
        # Call parent class constructor (will set up state machine)
        super().__init__(x, y, radius, base_hp * (wave_number *
                                                  wave_multiplier), base_speed, attack_radius)
        
        # Enemy specific attributes
        self.damage = damage
        self.attack_cooldown = attack_cooldown
        self.attack_timer = 0.0
        self.attack_radius = attack_radius

    def update(self, player, dt):
        # Get current state
        current_state = self.state_machine.get_state_name()
        
        # If entity is dead or dying, just update the state machine
        if not self.alive or self.health <= 0 or current_state == "dying":
            self.state_machine.update(dt)
            return
            
        # Handle states that restrict movement
        if current_state in ["sweep", "hurt"]:
            self.state_machine.update(dt)
            return  # Don't do anything else during these animations

        # 1) Check for attack BEFORE moving
        closest_type, closest_dist, closest_obj = self.get_closest_target(player)

        # Update attack timer
        if self.attack_timer > 0:
            self.attack_timer -= dt

        # Try to attack if we can
        if closest_obj:
            # Get target's radius for accurate attack distance
            target_radius = closest_obj[3]
            
            # Calculate effective attack distance
            effective_distance = closest_dist - self.radius - target_radius
            
            if effective_distance <= self.attack_radius and self.attack_timer <= 0:
                # Set attack animation through state machine
                self.state_machine.change_state("sweep")
                
                # Perform the attack
                self.attack(closest_type, closest_obj[4])
                self.attack_timer = self.attack_cooldown
                return  # Don't move after attacking

        # 2) Then move toward target if not attacking
        if closest_obj and closest_dist > 0:
            tx = closest_obj[1]
            ty = closest_obj[2]
            self.dx, self.dy = self.get_direction_to(tx, ty)
            
            # Set walking animation if not already
            if current_state != "walk":
                self.state_machine.change_state("walk")
                
            # Move toward target
            self.move(self.dx, self.dy, dt)
        else:
            # If no target, set to idle
            if current_state != "idle":
                self.state_machine.change_state("idle")
                
        # Update the state machine
        self.state_machine.update(dt, dx=self.dx, dy=self.dy)

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
            print("[Enemy] No sprite available for state:", self.state_machine.get_state_name())

        # Draw HP bar
        self.draw_health_bar(surf)

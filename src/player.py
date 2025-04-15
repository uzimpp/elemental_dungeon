# player.py
import time
import math
import pygame
import random
from utils import angle_diff
from deck import Deck
from visual_effects import VisualEffect, DashAfterimage
from config import (WIDTH, HEIGHT, PLAYER_SPRITE_PATH, PLAYER_ANIMATION_CONFIG, SHADOW_SUMMON_SPRITE_PATH, SHADOW_SUMMON_ANIMATION_CONFIG)
from entity import Entity
from animation import CharacterAnimation


class Player(Entity):
    def __init__(
            self,
            name,
            x,
            y,
            deck,  # This will be None initially
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
        self.game = None  # Will be set by Game class
        
        # Deck will be set later by Game class
        self.deck = deck
        
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
        
        # Animation setup - Pass the config now
        sprite_path = PLAYER_SPRITE_PATH
        self.animation = CharacterAnimation(
            sprite_sheet_path=sprite_path,
            config=PLAYER_ANIMATION_CONFIG,
            sprite_width=32,
            sprite_height=32
        )
        self.state = 'idle'  # Add player state tracking
        self.is_sprinting = False
        self.attack_timer = 0.0  # Timer to manage returning from cast state
    
    @property
    def summons(self):
        """Compatibility property for access to active summons"""
        return self.deck.get_summons()
        
    @property
    def projectiles(self):
        """Compatibility property for access to active projectiles"""
        return self.deck.get_projectiles()
    
    def handle_input(self, dt):
        # --- Prevent input/movement if dying ---
        if self.state in ['dying']:
            self.animation.update(dt) # Keep updating dying animation
            
            # Check if dying animation is complete
            self.attack_timer -= dt
            if self.attack_timer <= 0:
                self.alive = False  # Now we can mark as dead
            
            return
        
        # --- Handle casting and hurt states with reduced speed ---
        speed_multiplier = 1.0  # Default speed multiplier
        
        # Special handling for cast and hurt animations
        if self.state in ['cast', 'sweep', 'hurt']: 
            # Update action timer and animation
            self.attack_timer -= dt
            self.animation.update(dt)
            
            # For casting/sweeping, prevent movement until animation completes
            if self.state in ['cast', 'sweep'] and self.attack_timer <= 0:
                self.state = 'idle'
                self.animation.set_state('idle', force_reset=True)
                
            # For hurt state, allow movement at reduced speed
            elif self.state == 'hurt':
                speed_multiplier = 0.5  # Half speed during hurt animation
                if self.attack_timer <= 0:
                    self.state = 'idle'
                    self.animation.set_state('idle', force_reset=True)
            
            # For cast/sweep, don't allow any movement while animating
            elif self.state in ['cast', 'sweep']:
                return  # Don't process movement during casting
        
        # --- Input and Movement ---
        keys = pygame.key.get_pressed()
        self.is_sprinting = (keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]) and self.stamina > 0

        # Decide speed (with multiplier for hurt state)
        base_speed = self.sprint_speed if self.is_sprinting else self.walk_speed
        current_speed = base_speed * speed_multiplier  # Apply the speed multiplier

        # Calculate movement vector
        move_x = 0
        move_y = 0
        if keys[pygame.K_w]: move_y -= 1
        if keys[pygame.K_s]: move_y += 1
        if keys[pygame.K_a]: move_x -= 1
        if keys[pygame.K_d]: move_x += 1

        is_moving = (move_x != 0 or move_y != 0)

        # Normalize diagonal movement
        if move_x != 0 and move_y != 0:
            move_x *= 0.7071
            move_y *= 0.7071

        # Apply movement if moving
        if is_moving:
            self.x += move_x * current_speed * dt
            self.y += move_y * current_speed * dt

        # Stay within screen boundaries (using sprite size)
        self.x = max(self.animation.sprite_width / 2, min(WIDTH - self.animation.sprite_width / 2, self.x))
        self.y = max(self.animation.sprite_height / 2, min(HEIGHT - self.animation.sprite_height / 2, self.y))

        # --- Stamina logic (same as before) ---
        if self.is_sprinting and is_moving:
            self.stamina -= self.sprint_drain * dt
            if self.stamina <= 0:
                self.stamina = 0
                self.stamina_depleted_time = time.time()
                self.is_sprinting = False
        else:
            # Regenerate stamina
            can_regen = True
            if self.stamina == 0 and self.stamina_depleted_time is not None:
                if time.time() - self.stamina_depleted_time < self.stamina_cooldown:
                    can_regen = False
            if can_regen and self.stamina < self.max_stamina:
                self.stamina += self.stamina_regen * dt
                if self.stamina > self.max_stamina:
                    self.stamina = self.max_stamina
                    self.stamina_depleted_time = None

        # --- Update facing direction ---
        if is_moving:
            self.dx = move_x / math.hypot(move_x, move_y)
            self.dy = move_y / math.hypot(move_x, move_y)
        else:
            # Point towards mouse when idle
            mouse_x, mouse_y = pygame.mouse.get_pos()
            idle_dx = mouse_x - self.x
            idle_dy = mouse_y - self.y
            dist = math.hypot(idle_dx, idle_dy)
            if dist > 0:
                self.dx = idle_dx / dist
                self.dy = idle_dy / dist

        # --- Determine and Set Animation State ---
        # Only update animation state if not in a special state
        if self.state not in ['cast', 'sweep', 'hurt', 'dying']:
            target_state = 'idle'
            if is_moving:
                target_state = 'sprint' if self.is_sprinting else 'walk'
            self.animation.set_state(target_state)

        # --- Update Animation System ---
        self.animation.update(dt, self.dx, self.dy)

    def handle_event(self, event, mouse_pos, enemies, now, effects):
        # Ignore events if dying
        if self.state == 'dying':
            return None

        if event.type == pygame.KEYDOWN:
            # Ignore skill/dash if already performing an action
            if self.state not in ['cast', 'sweep']:
                if event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4]:
                    skill_idx = event.key - pygame.K_1
                    self.cast_skill(skill_idx, mouse_pos, enemies, now, effects)
                elif event.key == pygame.K_SPACE:
                    self.dash(effects)

            if event.key == pygame.K_ESCAPE:
                print("Player exited the game!")
                return 'exit'

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.state not in ['cast', 'sweep']:
                if event.button == 1:
                    self.cast_skill(0, mouse_pos, enemies, now, effects)
        return None

    def dash(self, effects):
        """Dash logic - Triggers an afterimage effect."""
        if self.state in ['dying', 'cast', 'sweep']: return

        if self.stamina >= self.dash_cost:
             # --- Create Afterimage ---
             # Capture position and sprite *before* moving
             start_x, start_y = self.x, self.y
             current_sprite = self.animation.get_current_sprite() # Get sprite before potential direction change
             if current_sprite: # Make sure sprite is valid
                  afterimage = DashAfterimage(start_x, start_y, current_sprite)
                  effects.append(afterimage) # Add to the main effects list

             # --- Perform Dash ---
             self.stamina -= self.dash_cost
             # (Keep existing dash movement logic: determine direction nx, ny)
             keys = pygame.key.get_pressed()
             dash_dx = 0
             dash_dy = 0
             if keys[pygame.K_w]: dash_dy -= 1
             if keys[pygame.K_s]: dash_dy += 1
             if keys[pygame.K_a]: dash_dx -= 1
             if keys[pygame.K_d]: dash_dx += 1

             if dash_dx == 0 and dash_dy == 0:
                  # Maybe dash in facing direction?
                  angle_rad = math.radians(self.animation.current_direction_angle)
                  nx, ny = math.cos(angle_rad), math.sin(angle_rad)
                  if abs(nx) < 0.01 and abs(ny) < 0.01 : # Avoid zero vector if facing perfectly up/down in atan2
                       print("Cannot determine dash direction.")
                       # Refund stamina if dash fails? Optional.
                       # self.stamina += self.dash_cost
                       return
             else:
                  dist = math.hypot(dash_dx, dash_dy)
                  nx = dash_dx / dist
                  ny = dash_dy / dist

             self.x += nx * self.dash_distance
             self.y += ny * self.dash_distance

             # Clamp to screen
             self.x = max(self.animation.sprite_width / 2, min(WIDTH - self.animation.sprite_width / 2, self.x))
             self.y = max(self.animation.sprite_height / 2, min(HEIGHT - self.animation.sprite_height / 2, self.y))

        else:
            print("Not enough stamina to dash!")

    def cast_skill(self, skill_idx, mouse_pos, enemies, now, effects):
        return self.deck.use_skill(skill_idx, mouse_pos[0], mouse_pos[1], enemies, now)

    def take_damage(self, amt):
        if self.state == 'dying' or not self.alive: 
            return  # Can't take damage if already dying/dead
        
        if amt > 0:
            self.health -= amt
            if self.health <= 0:
                # Player has died
                self.health = 0
                if self.state != 'dying':
                    print(f"{self.name} has died!")
                    self.state = 'dying'
                    self.animation.set_state('dying', force_reset=True)
                    # Don't set self.alive = False yet, let animation finish
                    animations_length = len(self.animation.config['dying']['animations'])
                    death_duration = self.animation.config['dying']['duration'] * animations_length
                    self.attack_timer = death_duration
            else:
                # Play hurt animation if not already in a more important state
                if self.state not in ['cast', 'sweep', 'dying']:
                    self.state = 'hurt'
                    self.animation.set_state('hurt', force_reset=True)
                    # Set a short timer for hurt animation
                    animations_length = len(self.animation.config['hurt']['animations'])
                    hurt_duration = self.animation.config['hurt']['duration'] * animations_length
                    self.attack_timer = hurt_duration

    def draw(self, surf):
        # Get the current sprite from the animation system
        current_sprite = self.animation.get_current_sprite()

        # Calculate top-left position for blitting (center the sprite)
        draw_x = self.x - self.animation.sprite_width / 2
        draw_y = self.y - self.animation.sprite_height / 2

        # Draw the sprite
        if current_sprite:
             surf.blit(current_sprite, (int(draw_x), int(draw_y)))
        # else: # Debugging print
        #      print("[DEBUG] !!! current_sprite is None in Player.draw !!!")

        # --- Remove projectile/summon drawing from here ---
        # Let game.py handle drawing order


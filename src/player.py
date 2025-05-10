# player.py
import time
import math
import pygame
import random
from deck import Deck
from visual_effects import VisualEffect, DashAfterimage
from config import (PLAYER_SPRITE_PATH,
                    PLAYER_ANIMATION_CONFIG, SPRITE_SIZE, ATTACK_RADIUS)
from entity import Entity
from animation import Animation
from energy import Energy


class Player(Entity):
    def __init__(self, name, width, height,
                 deck,
                 radius,
                 max_health,
                 walk_speed,
                 sprint_speed,
                 max_stamina,
                 stamina_regen,
                 sprint_drain,
                 dash_cost,
                 dash_distance,
                 stamina_cooldown):
        # Animation setup - must be before Entity constructor for state machine
        sprite_path = PLAYER_SPRITE_PATH
        self.animation = Animation(
            name="player",
            sprite_sheet_path=sprite_path,
            config=PLAYER_ANIMATION_CONFIG,
            sprite_width=SPRITE_SIZE,
            sprite_height=SPRITE_SIZE
        )
        
        # Call parent constructor (will set up state machine)
        super().__init__(width//2, height//2, radius, max_health, walk_speed)
        
        self.width = width
        self.height = height
        self.name = name
        self.game = None  # Will be set by Game class
        self.deck = deck

        # Initialize energy system
        self.energy = Energy(
            walk_speed=walk_speed,
            sprint_speed=sprint_speed,
            max_stamina=max_stamina,
            stamina_regen=stamina_regen,
            sprint_drain=sprint_drain,
            dash_cost=dash_cost,
            stamina_cooldown=stamina_cooldown
        )
        
        # Dash specific
        self.dash_distance = dash_distance
    
    @property
    def summons(self):
        """Compatibility property for access to active summons"""
        return self.deck.get_summons

    @property
    def projectiles(self):
        """Compatibility property for access to active projectiles"""
        return self.deck.get_projectiles

    def handle_input(self, dt):
        # Get current state
        current_state = self.state_machine.get_state_name()
        
        # 1. Prevent input/movement if dying
        if current_state == "dying":
            self.state_machine.update(dt)  # Keep updating dying animation
            return

        # 2. Handle casting and hurt states with reduced speed
        speed_multiplier = 1.0  # Default speed multiplier
        if current_state in ["cast", "sweep", "hurt"]:
            # Update action timer and animation
            self.state_machine.update(dt)
            speed_multiplier = 0.5  # Half speed during these animations

        # 3. Input and Movement
        keys = pygame.key.get_pressed()
        self.energy.set_sprinting((keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]))

        # Calculate movement vector
        move_x = 0
        move_y = 0
        if keys[pygame.K_w]:
            move_y -= 1
        if keys[pygame.K_s]:
            move_y += 1
        if keys[pygame.K_a]:
            move_x -= 1
        if keys[pygame.K_d]:
            move_x += 1

        # Normalize diagonal movement
        if move_x != 0 and move_y != 0:
            move_x *= 0.7071  # 1/sqrt(2)
            move_y *= 0.7071

        # Apply movement if moving
        is_moving = (move_x != 0 or move_y != 0)
        if is_moving:
            # Update energy system
            self.energy.update(dt, is_moving)
            current_speed = self.energy.get_current_speed() * speed_multiplier
            
            self.x += move_x * current_speed * dt
            self.y += move_y * current_speed * dt

            # Update facing direction based on movement
            self.dx = move_x
            self.dy = move_y
        else:
            # Update energy system without movement
            self.energy.update(dt, False)
            
            # Point towards mouse when idle
            mouse_x, mouse_y = pygame.mouse.get_pos()
            idle_dx = mouse_x - self.x
            idle_dy = mouse_y - self.y
            dist = math.hypot(idle_dx, idle_dy)
            if dist > 0:
                self.dx = idle_dx / dist
                self.dy = idle_dy / dist

        # Stay within screen boundaries
        self.x = max(self.animation.sprite_width / 2,
                     min(self.width - self.animation.sprite_width / 2, self.x))
        self.y = max(self.animation.sprite_height / 2,
                     min(self.height - self.animation.sprite_height / 2, self.y))

        # 5. Determine and Set Animation State
        if current_state not in ["cast", "sweep", "hurt", "dying"]:
            new_state = "idle"  # Only update animation state if not in a special state
            if is_moving:
                new_state = "sprint" if self.energy.is_sprinting else "walk"
            self.state_machine.change_state(new_state)
        
        # 6. Update State Machine with current movement direction
        self.state_machine.update(dt, dx=self.dx, dy=self.dy)

    def handle_event(self, event, mouse_pos, enemies, now, effects):
        # Ignore events if dying
        current_state = self.state_machine.get_state_name()
        if current_state == "dying":
            return None

        if event.type == pygame.KEYDOWN:
            # Ignore skill/dash if already performing an action
            if current_state not in ["cast", "sweep"]:
                if event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4]:
                    skill_idx = event.key - pygame.K_1
                    self.cast_skill(skill_idx, mouse_pos,
                                    enemies, now, effects)
                elif event.key == pygame.K_SPACE:
                    self.dash(effects)

            if event.key == pygame.K_ESCAPE:
                print("Player exited the game!")
                return 'exit'

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if current_state not in ["cast", "sweep"]:
                if event.button == 1:
                    self.cast_skill(0, mouse_pos, enemies, now, effects)
        return None

    def dash(self, effects):
        """Dash logic - Triggers an afterimage effect."""
        current_state = self.state_machine.get_state_name()
        if current_state in ["dying", "cast", "sweep"]:
            return

        if self.energy.can_dash():
            # --- Create Afterimage ---
            # Capture position and sprite *before* moving
            start_x, start_y = self.x, self.y
            # Get sprite before potential direction change
            current_sprite = self.animation.get_current_sprite()
            if current_sprite:  # Make sure sprite is valid
                afterimage = DashAfterimage(start_x, start_y, current_sprite)
                effects.append(afterimage)  # Add to the main effects list

            # --- Perform Dash ---
            self.energy.use_dash()
            
            # (Keep existing dash movement logic: determine direction nx, ny)
            keys = pygame.key.get_pressed()
            dash_dx = 0
            dash_dy = 0
            if keys[pygame.K_w]:
                dash_dy -= 1
            if keys[pygame.K_s]:
                dash_dy += 1
            if keys[pygame.K_a]:
                dash_dx -= 1
            if keys[pygame.K_d]:
                dash_dx += 1

            if dash_dx == 0 and dash_dy == 0:
                # Maybe dash in facing direction?
                angle_rad = math.radians(
                    self.animation.current_direction_angle)
                nx, ny = math.cos(angle_rad), math.sin(angle_rad)
                # Avoid zero vector if facing perfectly up/down in atan2
                if abs(nx) < 0.001 and abs(ny) < 0.001:
                    print("Cannot determine dash direction.")
                    return
            else:
                dist = math.hypot(dash_dx, dash_dy)
                nx = dash_dx / dist
                ny = dash_dy / dist

            self.x += nx * self.dash_distance
            self.y += ny * self.dash_distance

            # Clamp to screen
            self.x = max(self.animation.sprite_width / 2,
                         min(self.width - self.animation.sprite_width / 2, self.x))
            self.y = max(self.animation.sprite_height / 2,
                         min(self.height - self.animation.sprite_height / 2, self.y))
        else:
            print("Not enough stamina to dash!")

    def cast_skill(self, skill_idx, mouse_pos, enemies, now, effects):
        success = self.deck.use_skill(skill_idx, mouse_pos[0], mouse_pos[1], enemies, now)
        if success:
            # Set the casting state
            skill = self.deck.skills[skill_idx] 
            state = "sweep" if skill.skill_type == SkillType.SLASH else "cast"
            
            # Get animations length for correct duration
            if self.animation and self.animation.config and state in self.animation.config:
                animations = self.animation.config[state]['animations']
                duration_per_frame = self.animation.config[state]['duration']
                duration = len(animations) * duration_per_frame
                self.state_machine.change_state(state, duration=duration)
            else:
                # Default duration
                self.state_machine.change_state(state)
            
        return success

    def draw(self, surf):
        current_sprite = self.animation.get_current_sprite()
        if current_sprite:
            # Scale the sprite
            scale = 2  # Adjust scale factor as needed
            scaled_sprite = pygame.transform.scale(current_sprite,
                                                   (self.animation.sprite_width * scale,
                                                    self.animation.sprite_height * scale))
            # Calculate top-left position for blitting
            draw_x = self.x - (self.animation.sprite_width * scale) / 2
            draw_y = self.y - (self.animation.sprite_height * scale) / 2
            surf.blit(scaled_sprite, (int(draw_x), int(draw_y)))
        
        # Draw health and stamina bars
        self.draw_health_bar(surf)
        self.draw_stamina_bar(surf)
    
    def draw_stamina_bar(self, screen):
        """Draw stamina bar above the entity"""
        bar_width = self.radius * 2
        bar_height = 3
        bar_x = self.x - self.radius
        bar_y = self.y - self.radius - 15

        # Background (dark blue)
        pygame.draw.rect(screen, (0, 0, 100),
                         (bar_x, bar_y, bar_width, bar_height))

        # Foreground (bright blue)
        stamina_width = self.energy.get_stamina_percentage() * bar_width
        if stamina_width > 0:
            pygame.draw.rect(screen, (0, 100, 255),
                             (bar_x, bar_y, stamina_width, bar_height))

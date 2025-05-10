# player.py
import time
import math
import pygame
from visual_effects import DashAfterimage
from config import Config as C
from entity import Entity
from animation import CharacterAnimation


class Player(Entity):
    def __init__(self, name, width, height,
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
        super().__init__(width//2, height//2, radius, max_health, walk_speed, color)
        self.width = width
        self.height = height
        self.name = name
        self.game = None  # Will be set by Game class
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

        # Animation setup
        sprite_path = C.PLAYER_SPRITE_PATH
        self.animation = CharacterAnimation(
            sprite_sheet_path=sprite_path,
            config=C.PLAYER_ANIMATION_CONFIG,
            sprite_width=C.SPRITE_SIZE,
            sprite_height=C.SPRITE_SIZE
        )
        self.state = 'idle'  # Add player state tracking
        self.is_sprinting = False
        self.attack_timer = 0.0  # Timer to manage returning from cast state

    @property
    def summons(self):
        """Compatibility property for access to active summons"""
        return self.deck.get_summons

    @property
    def projectiles(self):
        """Compatibility property for access to active projectiles"""
        return self.deck.get_projectiles

    def handle_input(self, dt):
        # 1. Prevent input/movement if dying
        if self.state in ['dying']:
            self.animation.update(dt)  # Keep updating dying animation
            # Check if dying animation is complete
            self.attack_timer -= dt
            if self.attack_timer <= 0:
                self.alive = False
            return

        # 2. Handle casting and hurt states with reduced speed
        speed_multiplier = 1.0  # Default speed multiplier
        if self.state in ['cast', 'sweep', 'hurt']:
            # Update action timer and animation
            self.attack_timer -= dt
            self.animation.update(dt)
            speed_multiplier = 0.5  # Half speed during hurt animation
            if self.attack_timer <= 0:
                self.state = 'idle'
                self.animation.set_state('idle', force_reset=True)

        # 3. Input and Movement
        keys = pygame.key.get_pressed()
        self.is_sprinting = (keys[pygame.K_LSHIFT]
                             or keys[pygame.K_RSHIFT]) and self.stamina > 0

        base_speed = self.sprint_speed if self.is_sprinting else self.walk_speed
        # Apply the speed multiplier during animation
        current_speed = base_speed * speed_multiplier

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
            self.x += move_x * current_speed * dt
            self.y += move_y * current_speed * dt

            # Update facing direction based on movement
            self.dx = move_x
            self.dy = move_y
        else:
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

        # 4. Stamina logic
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

        # 5. Determine and Set Animation State
        if self.state not in ['cast', 'sweep', 'hurt', 'dying']:
            target_state = 'idle'  # Only update animation state if not in a special state
            if is_moving:
                target_state = 'sprint' if self.is_sprinting else 'walk'
            self.animation.set_state(target_state)

        # 6. Update Animation System
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
                    self.cast_skill(skill_idx, mouse_pos,
                                    enemies, now, effects)
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
        if self.state in ['dying', 'cast', 'sweep']:
            return

        if self.stamina >= self.dash_cost:
            # --- Create Afterimage ---
            # Capture position and sprite *before* moving
            start_x, start_y = self.x, self.y
            # Get sprite before potential direction change
            current_sprite = self.animation.get_current_sprite()
            if current_sprite:  # Make sure sprite is valid
                afterimage = DashAfterimage(start_x, start_y, current_sprite)
                effects.append(afterimage)  # Add to the main effects list

            # --- Perform Dash ---
            self.stamina -= self.dash_cost
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
                    # self.stamina += self.dash_cost # Refund stamina if dash fails?
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
                    animations_length = len(
                        self.animation.config['dying']['animations'])
                    death_duration = self.animation.config['dying']['duration'] * \
                        animations_length
                    self.attack_timer = death_duration
            else:
                # Play hurt animation if not already in a more important state
                if self.state not in ['cast', 'sweep', 'dying']:
                    self.state = 'hurt'
                    self.animation.set_state('hurt', force_reset=True)
                    # Set a short timer for hurt animation
                    animations_length = len(
                        self.animation.config['hurt']['animations'])
                    hurt_duration = self.animation.config['hurt']['duration'] * \
                        animations_length
                    self.attack_timer = hurt_duration

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
        # else: # Debugging print
        #      print("[DEBUG] !!! current_sprite is None in Player.draw !!!")

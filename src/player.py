# player.py
import time
import math
import pygame
import random
from visual_effects import DashAfterimage
from config import Config as C
from entity import Entity
from animation import CharacterAnimation


class Camera:
    def __init__(self):
        self.offset = pygame.math.Vector2(0, 0)
        self.shake_intensity = 0
        self.shake_duration = 0
        self.shake_start_time = 0

    def start_shake(self, intensity=5, duration=0.3):
        self.shake_intensity = intensity
        self.shake_duration = duration
        self.shake_start_time = time.time()

    def update(self):
        # Update camera shake
        if self.shake_duration > 0:
            elapsed = time.time() - self.shake_start_time
            if elapsed < self.shake_duration:
                # Calculate shake intensity based on remaining time (fade out)
                remaining_pct = 1 - (elapsed / self.shake_duration)
                current_intensity = self.shake_intensity * remaining_pct

                # Apply random offset
                self.offset.x = random.uniform(-current_intensity,
                                               current_intensity)
                self.offset.y = random.uniform(-current_intensity,
                                               current_intensity)
            else:
                # Shake finished
                self.shake_duration = 0
                self.offset.x = 0
                self.offset.y = 0

    def apply(self, pos):
        # Apply camera offset to a position
        return pos + self.offset


class Player(Entity):
    def __init__(self, name, game_instance, deck=None):
        super().__init__(C.WIDTH//2, C.HEIGHT//2, C.SPRITE_SIZE//2,
                         C.PLAYER_MAX_HEALTH, C.PLAYER_WALK_SPEED, C.PLAYER_COLOR)
        self.name = name
        self.game = game_instance  # Store reference to the game instance
        self._deck = deck
        # Speed attributes
        self.walk_speed = C.PLAYER_WALK_SPEED
        self.sprint_speed = C.PLAYER_SPRINT_SPEED
        self.max_stamina = C.PLAYER_MAX_STAMINA
        self.stamina = self.max_stamina
        self.stamina_regen = C.PLAYER_STAMINA_REGEN
        self.sprint_drain = C.PLAYER_SPRINT_DRAIN
        self.dash_cost = C.PLAYER_DASH_COST
        self.dash_distance = C.PLAYER_DASH_DISTANCE
        self.stamina_depleted_time = None
        self.stamina_cooldown = C.PLAYER_STAMINA_COOLDOWN
        self.is_sprinting = False
        self.attack_radius = C.ATTACK_RADIUS

        self.animation = CharacterAnimation(
            sprite_sheet_path=C.PLAYER_SPRITE_PATH,
            config=C.PLAYER_ANIMATION_CONFIG,
            sprite_width=C.SPRITE_SIZE,
            sprite_height=C.SPRITE_SIZE
        )
        self.animation.set_state('idle', force_reset=True)
        self.camera = Camera()
        self.move_vector = pygame.math.Vector2(0, 0)

    @property
    def deck(self):
        """Compatibility property for access to deck"""
        return self._deck

    @deck.setter
    def deck(self, new_deck):
        """Compatibility property for access to deck"""
        self._deck = new_deck

    @property
    def summons(self):
        """Compatibility property for access to active summons"""
        if self._deck is None:
            return []
        return self._deck.get_summons

    @property
    def projectiles(self):
        """Compatibility property for access to active projectiles"""
        if self._deck is None:
            return []
        return self._deck.get_projectiles

    def handle_input(self, dt):
        # Prevent input/movement if dying
        if self.state in ['dying']:
            self.animation.update(dt)
            # Check if dying animation is complete
            self.attack_animation_timer -= dt
            if self.attack_animation_timer <= 0:
                self.alive = False
            return
        # Handle casting and hurt states with reduced speed
        speed_multiplier = 1.0  # Default speed multiplier
        if self.state in ['cast', 'sweep', 'hurt']:
            # Update action timer and animation
            self.attack_animation_timer -= dt
            self.animation.update(dt)
            speed_multiplier = 0.5  # Half speed during hurt animation
            if self.attack_animation_timer <= 0:
                self.state = 'idle'
                self.animation.set_state('idle', force_reset=True)
        self._process_keyboard_input(dt, speed_multiplier)
        self._update_stamina(dt)
        self._update_animation_state(dt)
        self.camera.update()

    def _process_keyboard_input(self, dt, speed_multiplier):
        """Handle keyboard input for movement"""
        keys = pygame.key.get_pressed()
        # Check sprint key
        self.is_sprinting = (keys[pygame.K_LSHIFT]
                             or keys[pygame.K_RSHIFT]) and self.stamina > 0
        base_speed = self.sprint_speed if self.is_sprinting else self.walk_speed
        current_speed = base_speed * speed_multiplier
        # Build movement vector from WASD keys
        self.move_vector.x, self.move_vector.y = 0, 0
        if keys[pygame.K_w]:
            self.move_vector.y -= 1
        if keys[pygame.K_s]:
            self.move_vector.y += 1
        if keys[pygame.K_a]:
            self.move_vector.x -= 1
        if keys[pygame.K_d]:
            self.move_vector.x += 1
        # Normalize for consistent diagonal speed
        if self.move_vector.length() > 0:
            self.move_vector.normalize_ip()
            self.dx = self.move_vector.x
            self.dy = self.move_vector.y
            self.x += self.move_vector.x * current_speed * dt
            self.y += self.move_vector.y * current_speed * dt
        else:
            # Point towards mouse when idle
            mouse_pos = pygame.mouse.get_pos()
            mouse_vector = pygame.math.Vector2(
                mouse_pos[0] - self.x, mouse_pos[1] - self.y)
            if mouse_vector.length() > 0:
                mouse_vector.normalize_ip()
                self.dx = mouse_vector.x
                self.dy = mouse_vector.y
        # Calculate sprite boundaries based on actual scaled sprite size
        scale = C.RENDER_SIZE / C.SPRITE_SIZE
        half_width = (self.animation.sprite_width * scale) / 2
        half_height = (self.animation.sprite_height * scale) / 2
        # Stay within screen boundaries
        self.x = max(half_width, min(C.WIDTH - half_width, self.x))
        self.y = max(half_height, min(C.HEIGHT - half_height, self.y))

    def _update_stamina(self, dt):
        """Update stamina based on player actions"""
        # Drain stamina if sprinting and moving
        if self.is_sprinting and self.move_vector.length() > 0:
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

    def _update_animation_state(self, dt):
        """Update animation state based on player movement"""
        if self.state not in ['cast', 'sweep', 'hurt', 'dying']:
            if self.move_vector.length() > 0:
                target_state = 'sprint' if self.is_sprinting else 'walk'
                self.animation.set_state(target_state)
            else:
                self.animation.set_state('idle')
        # Update Animation System
        self.animation.update(dt, self.dx, self.dy)

    def handle_event(self, event, mouse_pos, enemies, now, effects=None):
        if self.state == 'dying':
            return None
        if event.type == pygame.KEYDOWN:
            # Ignore skill/dash if already performing an action
            if self.state not in ['cast', 'sweep']:
                if event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4]:
                    skill_idx = event.key - pygame.K_1
                    self.cast_skill(skill_idx, mouse_pos, enemies, now)
                elif event.key == pygame.K_SPACE:
                    self.dash()
            if event.key == pygame.K_ESCAPE:
                return 'exit'
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.state not in ['cast', 'sweep']:
                if event.button == 1:
                    self.cast_skill(0, mouse_pos, enemies, now)
        return None

    def dash(self):
        """Dash logic - Triggers an afterimage effect."""
        if self.state in ['dying', 'cast', 'sweep']:
            return
        if self.stamina >= self.dash_cost:
            # Capture position and sprite *before* moving
            start_x, start_y = self.x, self.y
            # Get sprite before potential direction change
            current_sprite = self.animation.get_current_sprite()
            if current_sprite:  # Make sure sprite is valid
                afterimage = DashAfterimage(start_x, start_y, current_sprite)
                self.deck.add_effect(afterimage)  # Add to deck's effects list
            self.stamina -= self.dash_cost
            # Get dash direction vector
            dash_vector = self._get_dash_direction()
            if dash_vector.length() == 0:
                return
            # Apply dash movement
            self.x += dash_vector.x * self.dash_distance
            self.y += dash_vector.y * self.dash_distance

            scale = C.RENDER_SIZE / C.SPRITE_SIZE
            half_width = (self.animation.sprite_width * scale) / 2
            half_height = (self.animation.sprite_height * scale) / 2

            # Stay within screen boundaries
            self.x = max(half_width, min(C.WIDTH - half_width, self.x))
            self.y = max(half_height, min(C.HEIGHT - half_height, self.y))
        else:
            # Not enough stamina
            pass

    def _get_dash_direction(self):
        """Calculate the direction vector for dash"""
        # Try to get direction from keyboard input
        keys = pygame.key.get_pressed()
        dash_vector = pygame.math.Vector2(0, 0)

        if keys[pygame.K_w]:
            dash_vector.y -= 1
        if keys[pygame.K_s]:
            dash_vector.y += 1
        if keys[pygame.K_a]:
            dash_vector.x -= 1
        if keys[pygame.K_d]:
            dash_vector.x += 1

        # If no keys pressed, use facing direction
        if dash_vector.length() == 0:
            angle_rad = math.radians(self.animation.current_direction_angle)
            dash_vector.x = math.cos(angle_rad)
            dash_vector.y = math.sin(angle_rad)

            # Avoid zero vector
            if abs(dash_vector.x) < 0.001 and abs(dash_vector.y) < 0.001:
                return pygame.math.Vector2(0, 0)

        # Normalize direction vector
        if dash_vector.length() > 0:
            dash_vector.normalize_ip()

        return dash_vector

    def cast_skill(self, skill_idx, mouse_pos, enemies, now):
        return self.deck.use_skill(skill_idx, mouse_pos[0], mouse_pos[1], enemies, now, self)

    def take_damage(self, amt):
        """Override take_damage to add camera shake effect"""
        if not self.alive:
            return
        super().take_damage(amt)
        # Add camera shake effect based on damage amount
        if amt > 0:
            shake_intensity = min(10, amt / 2)  # Scale shake based on damage
            self.camera.start_shake(intensity=shake_intensity, duration=0.3)

    def draw(self, surf):
        current_sprite = self.animation.get_current_sprite()
        if current_sprite:
            # Use consistent scale factor from config
            scale = C.RENDER_SIZE / C.SPRITE_SIZE
            # Calculate scaled dimensions
            scaled_width = self.animation.sprite_width * scale
            scaled_height = self.animation.sprite_height * scale

            # Scale the sprite if needed
            if scale != 1:
                scaled_sprite = pygame.transform.scale(current_sprite,
                                                       (int(scaled_width),
                                                        int(scaled_height)))
            else:
                scaled_sprite = current_sprite

            # Calculate top-left position for blitting with camera offset
            cam_pos = self.camera.apply(pygame.math.Vector2(self.x, self.y))
            draw_x = cam_pos.x - scaled_width / 2
            draw_y = cam_pos.y - scaled_height / 2

            # Draw the sprite
            surf.blit(scaled_sprite, (int(draw_x), int(draw_y)))
        else:
            # Fallback to circle if sprite is not available
            cam_pos = self.camera.apply(pygame.math.Vector2(self.x, self.y))
            pygame.draw.circle(surf, self.color, (int(
                cam_pos.x), int(cam_pos.y)), self.radius)

import math
from ui import UI
from entity import Entity
from animation import CharacterAnimation
from config import Config as C


class Enemy(Entity):
    def __init__(
            self,
            x,
            y,
            wave_number,
            base_speed,
            base_hp):
        scaled_hp = base_hp * (wave_number * C.WAVE_MULTIPLIER)
        super().__init__(x, y, C.SPRITE_SIZE // 2, scaled_hp, base_speed, C.ENEMY_COLOR)

        # Enemy specific attributes
        self.damage = C.ENEMY_DAMAGE
        
        # Initialize animation
        self.animation = CharacterAnimation(
            sprite_sheet_path=C.ENEMY_SPRITE_PATH,
            config=C.ENEMY_ANIMATION_CONFIG,
            sprite_width=C.SPRITE_SIZE,
            sprite_height=C.SPRITE_SIZE
        )
        self.animation.set_state('idle', force_reset=True)

    def update(self, player, dt):
        # If entity is dead or in special animation states, let base class handle it
        if not self.alive or self.state in ['dying', 'hurt', 'sweep']:
            super().update_animation(dt)
            return

        # Update attack timer
        if self.attack_timer > 0:
            self.attack_timer -= dt

        # Find closest target (player or summon)
        closest_type, closest_dist, closest_obj = self.get_closest_target(player)

        # Decide behavior based on distance
        if closest_obj:
            # Get target's radius to properly calculate attack distance
            target_radius = closest_obj[3]
            target_entity = closest_obj[4]
            
            # Effective attack range accounts for both entity radii
            effective_distance = closest_dist - self.radius - target_radius

            # Attack if in range and cooldown is ready
            if effective_distance <= self.attack_radius and self.attack_timer <= 0:
                # Set attack animation
                self.state = 'sweep'
                self.animation.set_state('sweep', force_reset=True)
                
                # Calculate attack animation duration
                animations_length = len(self.animation.config['sweep']['animations'])
                attack_duration = self.animation.config['sweep']['duration'] * animations_length
                self.attack_animation_timer = attack_duration
                
                # Perform the attack
                super().attack(target_entity)
                self.attack_timer = self.attack_cooldown
                return
                
            # Otherwise, move toward target
            # Set walking animation if not already
            if self.state != 'walk':
                self.state = 'walk'
                self.animation.set_state('walk')
                
            # Get direction to target and move
            self.dx, self.dy = self.get_direction_to(closest_obj[1], closest_obj[2])
            self.move(self.dx, self.dy, dt)
        else:
            # If no target, go to idle state
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

    def draw(self, surf):
        # Use the base class's draw method for animation
        super().draw(surf)
        
        # Add HP bar
        self.draw_health_bar(surf)

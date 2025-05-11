import csv
import math
import pygame
from skill import SkillType, Projectile, Summon, Heal, AOE, Slash, Chain
from config import Config as C
from visual_effects import VisualEffect, DashAfterimage


class Deck:
    """Centralized manager for player skills, projectiles, summons and effects"""

    def __init__(self):
        self._skills = []
        # Replace lists with sprite groups
        self._projectiles = pygame.sprite.Group()
        self._summons = pygame.sprite.Group()
        self.__summon_limit = C.PLAYER_SUMMON_LIMIT
        self._effects = []

    @property
    def get_projectiles(self):
        return list(self._projectiles.sprites())

    @property
    def get_summons(self):
        return list(self._summons.sprites())

    def add_effect(self, effect):
        """Add visual effect to the deck's effects list"""
        if effect is not None:
            self._effects.append(effect)

    @property
    def projectiles(self):
        return self._projectiles

    @property
    def summons(self):
        return self._summons

    @property
    def skills(self):
        return self._skills

    @skills.setter
    def skills(self, value):
        self._skills = value

    def add_skill(self, skill):
        self._skills.append(skill)

    def create_skills(self, selected_skills):
        """Load skills from CSV file into this deck"""
        for selected_skill in selected_skills:
            skill = self.create_skill(selected_skill)
            if skill:
                self.add_skill(skill)

    def create_skill(self, selected_skill):
        """Load skills from CSV file into this deck"""
        skill_type_str = selected_skill["skill_type"].upper()
        try:
            skill_type = SkillType[skill_type_str]
        except KeyError:
            print(f"Unknown skill type: {skill_type_str}")
            return None
        # Create the appropriate skill based on type
        if skill_type == SkillType.PROJECTILE:
            skill = Projectile(
                name=selected_skill["name"],
                element=selected_skill["element"].upper(),
                damage=int(selected_skill["damage"]),
                speed=float(selected_skill["speed"]),
                radius=float(selected_skill["radius"]),
                duration=float(selected_skill["duration"]),
                cooldown=float(selected_skill["cooldown"]),
                description=selected_skill["description"],
                pull=(selected_skill.get(
                    "pull", "FALSE").strip().lower() == "true")
            )
        elif skill_type == SkillType.SUMMON:
            element = selected_skill["element"].upper()
            if element == "SHADOW":
                sprite_path = C.SHADOW_SUMMON_SPRITE_PATH
                animation_config = C.SHADOW_SUMMON_ANIMATION_CONFIG
            elif element == "WOOD":
                sprite_path = C.WOOD_SUMMON_SPRITE_PATH
                animation_config = C.WOOD_SUMMON_ANIMATION_CONFIG
            else:
                raise ValueError(
                    f"Unsupported element for summon: {element}")
            skill = Summon(
                name=selected_skill["name"],
                element=element,
                damage=int(selected_skill["damage"]),
                speed=float(selected_skill["speed"]),
                radius=float(selected_skill["radius"]),
                # Infinite duration - summons stay until killed
                duration=float('inf'),
                cooldown=float(selected_skill["cooldown"]),
                description=selected_skill["description"],
                sprite_path=sprite_path,
                animation_config=animation_config,
                attack_radius=C.ATTACK_RADIUS
            )
        elif skill_type == SkillType.HEAL:
            # Parse the heal_summons parameter if it exists
            heal_summons = True  # Default to True for backward compatibility
            if "heal_summons" in selected_skill and selected_skill["heal_summons"].upper() == "FALSE":
                heal_summons = False

            skill = Heal(
                name=selected_skill["name"],
                element=selected_skill["element"].upper(),
                heal_amount=int(selected_skill["heal_amount"]),
                radius=float(selected_skill["radius"]),
                duration=float(selected_skill["duration"]),
                cooldown=float(selected_skill["cooldown"]),
                description=selected_skill["description"],
                heal_summons=heal_summons
            )
        elif skill_type == SkillType.AOE:
            skill = AOE(
                name=selected_skill["name"],
                element=selected_skill["element"].upper(),
                damage=int(selected_skill["damage"]),
                radius=float(selected_skill["radius"]),
                duration=float(selected_skill["duration"]),
                cooldown=float(selected_skill["cooldown"]),
                description=selected_skill["description"],
                pull=(selected_skill.get(
                    "pull", "FALSE").strip().lower() == "true")
            )
        elif skill_type == SkillType.SLASH:
            skill = Slash(
                name=selected_skill["name"],
                element=selected_skill["element"].upper(),
                damage=int(selected_skill["damage"]),
                radius=float(selected_skill["radius"]),
                duration=float(selected_skill["duration"]),
                cooldown=float(selected_skill["cooldown"]),
                description=selected_skill["description"],
                pull=(selected_skill.get(
                    "pull", "FALSE").strip().lower() == "true")
            )
        elif skill_type == SkillType.CHAIN:
            skill = Chain(
                name=selected_skill["name"],
                element=selected_skill["element"].upper(),
                damage=int(selected_skill["damage"]),
                radius=float(selected_skill["radius"]),
                duration=float(selected_skill["duration"]),
                pull=(selected_skill["pull"].strip().lower() == "true"),
                cooldown=float(selected_skill["cooldown"]),
                description=selected_skill["description"]
            )
        else:
            raise ValueError(
                f"Unknown skill type: {skill_type_str}")
        return skill

    def use_skill(self, index, target_x, target_y, enemies, now, player, effects=None):
        """Activates a skill, creates entities/effects, and adds visual effects"""
        if not 0 <= index < len(self.skills):
            return False

        skill = self.skills[index]  # Get the skill *definition*
        if not skill.is_off_cooldown(now):
            return False

        # --- Skill Activation ---
        skill.trigger_cooldown()  # Use the method in BaseSkill

        # --- Record Skill Usage for Data Collection ---
        if player and hasattr(player, 'game') and player.game and hasattr(player.game, 'current_wave_skill_usage'):
            player.game.current_wave_skill_usage[skill.name] = player.game.current_wave_skill_usage.get(
                skill.name, 0) + 1

        # --- Set Player Animation State ---
        action_state = 'cast'  # Default animation
        if skill.skill_type == SkillType.SLASH:
            action_state = 'sweep'

        # Ensure animation config exists before accessing
        anim_config = player.animation.config.get(
            action_state) if player.animation else None
        if anim_config:
            player.state = action_state
            player.animation.set_state(action_state, force_reset=True)
            animations = anim_config.get('animations', [])
            duration_per_frame = anim_config.get('duration', 0.1)
            player.attack_timer = len(animations) * duration_per_frame
        else:
            player.state = action_state  # Still set state even if no animation
            player.attack_timer = 0.5  # Default action duration

        # --- Create Skill Entities and Visual Effects ---
        if skill.skill_type == SkillType.PROJECTILE:
            # Calculate spawn position near player in direction of mouse
            dx = target_x - player.x
            dy = target_y - player.y
            dist = math.hypot(dx, dy)
            if dist == 0:
                dist = 1
            # Normalize direction and multiply by spawn distance
            spawn_distance = 30  # Distance from player to spawn projectile
            spawn_x = player.x + (dx / dist) * spawn_distance
            spawn_y = player.y + (dy / dist) * spawn_distance

            # Create the actual projectile entity at the calculated position
            projectile_entity = type(skill).activate(
                skill, spawn_x, spawn_y, target_x, target_y)
            projectile_entity.owner = player  # Set the owner reference

            # Add to sprite group
            self.projectiles.add(projectile_entity)

            # Add casting effect
            effect = VisualEffect(
                spawn_x, spawn_y, "explosion", skill.color, 10, 0.2)
            self.add_effect(effect)

        elif skill.skill_type == SkillType.SUMMON:
            if len(self._summons) >= self.__summon_limit:
                # Remove oldest summon
                oldest_summon = next(iter(self._summons))
                oldest_summon.kill()

            # Calculate spawn position near player in direction of mouse
            dx = target_x - player.x
            dy = target_y - player.y
            dist = math.hypot(dx, dy)
            if dist == 0:
                dist = 1
            # Normalize direction and multiply by spawn distance
            spawn_distance = 40  # Distance from player to spawn summon
            spawn_x = player.x + (dx / dist) * spawn_distance
            spawn_y = player.y + (dy / dist) * spawn_distance

            # Create the actual summon entity at the calculated position
            summon_entity = type(skill).activate(
                skill, spawn_x, spawn_y, C.ATTACK_RADIUS)
            summon_entity.owner = player  # Set the owner reference

            # Add to sprite group
            self._summons.add(summon_entity)

            # Add visual effect for summoning
            effect = VisualEffect(
                spawn_x, spawn_y, "explosion", skill.color, 20, 0.3)
            self.add_effect(effect)

        elif skill.skill_type == SkillType.HEAL:
            # Get summons for healing (if applicable)
            summons_to_heal = list(self._summons.sprites()) if hasattr(
                skill, 'heal_summons') and skill.heal_summons else None

            # Activate the heal skill with both player and summons
            Heal.activate(skill, player, summons_to_heal)

            # Add visual effect for healing
            effect = VisualEffect(
                player.x, player.y, "heal", skill.color, 30, 0.5)
            self.add_effect(effect)

            # Add effects for healed summons too
            if summons_to_heal:
                for summon in summons_to_heal:
                    if summon.alive and summon.health < summon.max_health:
                        effect = VisualEffect(
                            summon.x, summon.y, "heal", skill.color, 20, 0.3)
                        self.add_effect(effect)

        elif skill.skill_type == SkillType.AOE:
            # Ensure duration is not zero
            duration = max(0.1, skill.duration)
            effect = VisualEffect(
                target_x, target_y, "explosion", skill.color, skill.radius, duration)
            self.add_effect(effect)

            # Apply damage to enemies in radius
            AOE.activate(skill, target_x, target_y, enemies)

        elif skill.skill_type == SkillType.SLASH:
            # Calculate angle from player to target
            angle = math.atan2(target_y - player.y, target_x - player.x)

            # Define sweep parameters
            arc_width = math.pi / 3  # 60 degree sweep
            # This is a CLOCKWISE sweep - starting to the left of target angle
            # and ending to the right of target angle
            # Start 30 degrees to the "left" of target
            start_angle = angle - (arc_width / 2)
            sweep_angle = arc_width  # Sweep 60 degrees clockwise

            # Create visual effect with the correct start angle and sweep direction
            effect = VisualEffect(
                player.x,
                player.y,
                "slash",
                skill.color,
                skill.radius,
                0.3,
                start_angle=start_angle,
                sweep_angle=sweep_angle
            )
            self.add_effect(effect)

            # Apply damage to enemies in arc - hit detection must match the visual
            Slash.activate(skill, player.x, player.y,
                           target_x, target_y, enemies, start_angle, sweep_angle)

        elif skill.skill_type == SkillType.CHAIN:
            # Call the Chain's activate method to perform the chain logic
            chain_effects = Chain.activate(
                skill, player.x, player.y, target_x, target_y, enemies)
            # Add all effects returned by Chain.activate
            for effect in chain_effects:
                self.add_effect(effect)

        # Skill was successfully used
        return True

    def update(self, dt, enemies):
        """Update all active entities managed by the deck"""
        self._update_projectiles(dt, enemies)
        self._update_summons(dt, enemies)
        self._update_effects(dt)

    def _update_projectiles(self, dt, enemies):
        """Update all active projectiles"""
        # Use list comprehension to safely remove dead projectiles after update
        dead_projectiles = []
        for projectile in self.projectiles:
            result = projectile.update(dt, enemies)
            if result is not True:  # If it's not True, it might be an effect or False
                dead_projectiles.append(projectile)
                if result is not False:  # It's an effect
                    self.add_effect(result)

        # Remove dead projectiles
        for projectile in dead_projectiles:
            self.projectiles.remove(projectile)

    def _update_summons(self, dt, enemies):
        """Update all active summons"""
        # Use list comprehension to safely remove dead summons after update
        dead_summons = []
        for summon in self._summons:
            if not summon.update(dt, enemies):
                dead_summons.append(summon)

        # Remove dead summons
        for summon in dead_summons:
            self._summons.remove(summon)

    def _update_effects(self, dt):
        """Update all visual effects"""
        # Remove inactive effects
        self._effects = [
            effect for effect in self._effects if effect.update(dt)]

    def draw(self, surface):
        """Draw all active entities managed by the deck"""
        # Draw projectiles
        for projectile in self.projectiles:
            projectile.draw(surface)

        # Draw summons
        for summon in self._summons:
            summon.draw(surface)

        # Draw effects
        for effect in self._effects:
            effect.draw(surface)

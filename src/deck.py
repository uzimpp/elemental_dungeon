import csv
import math
import time
import pygame
from skill import SkillType, Projectile, Summon, Heal, AOE, Slash, Chain
from config import Config as C
from visual_effects import VisualEffect


class Deck:
    """Centralized manager for player skills, projectiles, and summons"""

    def __init__(self, owner):
        self.owner = owner
        self.skills = []
        
        # Replace lists with sprite groups
        self.projectiles = pygame.sprite.Group()
        self.summons = pygame.sprite.Group()
        self.summon_limit = 5

    @property
    def get_projectiles(self):
        return list(self.projectiles.sprites())

    @property
    def get_summons(self):
        return list(self.summons.sprites())

    def load_from_csv(self, filename):
        """Load skills from CSV file into this deck"""
        try:
            with open(filename, newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    skill_type_str = row["skill_type"].upper()
                    try:
                        skill_type = SkillType[skill_type_str]
                    except KeyError:
                        print(f"Unknown skill type: {skill_type_str}")
                        continue

                    # Create the appropriate skill based on type
                    if skill_type == SkillType.PROJECTILE:
                        skill = Projectile(
                            name=row["name"],
                            element=row["element"].upper(),
                            damage=int(row["damage"]),
                            speed=float(row["speed"]),
                            radius=float(row["radius"]),
                            duration=float(row["duration"]),
                            cooldown=float(row["cooldown"]),
                            description=row["description"]
                        )
                    elif skill_type == SkillType.SUMMON:
                        element = row["element"].upper()
                        if element == "SHADOW":
                            sprite_path = C.SHADOW_SUMMON_SPRITE_PATH
                            animation_config = C.SHADOW_SUMMON_ANIMATION_CONFIG
                        else:
                            raise ValueError(
                                f"Unsupported element for summon: {element}")

                        skill = Summon(
                            name=row["name"],
                            element=element,
                            damage=int(row["damage"]),
                            speed=float(row["speed"]),
                            radius=float(row["radius"]),
                            # Infinite duration - summons stay until killed
                            duration=float('inf'),
                            cooldown=float(row["cooldown"]),
                            description=row["description"],
                            sprite_path=sprite_path,
                            animation_config=animation_config,
                            attack_radius=C.ATTACK_RADIUS
                        )
                    elif skill_type == SkillType.HEAL:
                        # Parse the heal_summons parameter if it exists
                        heal_summons = True  # Default to True for backward compatibility
                        if "heal_summons" in row and row["heal_summons"].upper() == "FALSE":
                            heal_summons = False

                        skill = Heal(
                            name=row["name"],
                            element=row["element"].upper(),
                            heal_amount=int(row["heal_amount"]),
                            radius=float(row["radius"]),
                            duration=float(row["duration"]),
                            cooldown=float(row["cooldown"]),
                            description=row["description"],
                            heal_summons=heal_summons
                        )
                    elif skill_type == SkillType.AOE:
                        skill = AOE(
                            name=row["name"],
                            element=row["element"].upper(),
                            damage=int(row["damage"]),
                            radius=float(row["radius"]),
                            duration=float(row["duration"]),
                            cooldown=float(row["cooldown"]),
                            description=row["description"]
                        )
                    elif skill_type == SkillType.SLASH:
                        skill = Slash(
                            name=row["name"],
                            element=row["element"].upper(),
                            damage=int(row["damage"]),
                            radius=float(row["radius"]),
                            duration=float(row["duration"]),
                            cooldown=float(row["cooldown"]),
                            description=row["description"]
                        )
                    elif skill_type == SkillType.CHAIN:
                        skill = Chain(
                            name=row["name"],
                            element=row["element"].upper(),
                            damage=int(row["damage"]),
                            radius=float(row["radius"]),
                            duration=float(row["duration"]),
                            pull=(row["pull"].strip().lower() == "true"),
                            cooldown=float(row["cooldown"]),
                            description=row["description"]
                        )
                    else:
                        raise ValueError(
                            f"Unknown skill type: {skill_type_str}")
                    self.skills.append(skill)
        except FileNotFoundError:
            raise ValueError(f"Error: CSV '{filename}' not found.")
        except KeyError as e:
            raise ValueError(f"CSV parsing error: missing column {e}")

        return self.skills

    def use_skill(self, index, target_x, target_y, enemies, now):
        """Activates a skill, creates entities/effects, and adds visual effects"""
        if not 0 <= index < len(self.skills):
            print(
                f"[Deck] Error: Skill index {index} out of bounds (0-{len(self.skills)-1})")
            return False

        skill = self.skills[index]  # Get the skill *definition*
        if not skill.is_off_cooldown(now):
            print(f"[Deck] Skill '{skill.name}' is on cooldown.")
            return False

        # --- Skill Activation ---
        skill.trigger_cooldown()  # Use the method in BaseSkill
            
        # Set the owner reference on the skill for visual effects
        skill.owner = self.owner

        # --- Set Player Animation State ---
        action_state = 'cast'  # Default animation
        if skill.skill_type == SkillType.SLASH:
            action_state = 'sweep'

        # Ensure animation config exists before accessing
        anim_config = self.owner.animation.config.get(
            action_state) if self.owner.animation else None
        if anim_config:
            self.owner.state = action_state
            self.owner.animation.set_state(action_state, force_reset=True)
            animations = anim_config.get('animations', [])
            duration_per_frame = anim_config.get('duration', 0.1)
            self.owner.attack_timer = len(animations) * duration_per_frame
        else:
            print(
                f"Warning: Animation config not found for state '{action_state}'. Setting default timer.")
            self.owner.state = action_state  # Still set state even if no animation
            self.owner.attack_timer = 0.5  # Default action duration

        # --- Get Game Effects List ---
        # Safely get the effects list from the game instance via the owner (player)
        game_effects_list = None
        if hasattr(self.owner, 'game') and self.owner.game and hasattr(self.owner.game, 'effects'):
            game_effects_list = self.owner.game.effects
        else:
            print("[Deck] Warning: Cannot access game effects list from player.")

        # --- Create Skill Entities and Visual Effects ---
        if skill.skill_type == SkillType.PROJECTILE:
            # Calculate spawn position near player in direction of mouse
            dx = target_x - self.owner.x
            dy = target_y - self.owner.y
            dist = math.hypot(dx, dy)
            if dist == 0:
                dist = 1
            # Normalize direction and multiply by spawn distance
            spawn_distance = 30  # Distance from player to spawn projectile
            spawn_x = self.owner.x + (dx / dist) * spawn_distance
            spawn_y = self.owner.y + (dy / dist) * spawn_distance

            # Create the actual projectile entity at the calculated position
            projectile_entity = skill.create(
                skill, spawn_x, spawn_y, target_x, target_y)
            projectile_entity.owner = self.owner  # Set the owner reference

            # Add to sprite group
            self.projectiles.add(projectile_entity)

            # Add visual effect for casting at the spawn location
            if game_effects_list is not None:
                effect = VisualEffect(
                    spawn_x, spawn_y, "explosion", skill.color, 10, 0.2)
                game_effects_list.append(effect)

        elif skill.skill_type == SkillType.SUMMON:
            if len(self.summons) >= self.summon_limit:
                # Remove oldest summon
                oldest_summon = next(iter(self.summons))
                oldest_summon.kill()

            # Calculate spawn position near player in direction of mouse
            dx = target_x - self.owner.x
            dy = target_y - self.owner.y
            dist = math.hypot(dx, dy)
            if dist == 0:
                dist = 1
            # Normalize direction and multiply by spawn distance
            spawn_distance = 40  # Distance from player to spawn summon
            spawn_x = self.owner.x + (dx / dist) * spawn_distance
            spawn_y = self.owner.y + (dy / dist) * spawn_distance

            # Create the actual summon entity at the calculated position
            summon_entity = skill.create(
                skill, spawn_x, spawn_y, C.ATTACK_RADIUS)
            
            # Add to sprite group
            self.summons.add(summon_entity)

            # Add visual effect for summoning at the spawn location
            if game_effects_list is not None:
                effect = VisualEffect(
                    spawn_x, spawn_y, "explosion", skill.color, 20, 0.3)
                game_effects_list.append(effect)

        elif skill.skill_type == SkillType.HEAL:
            # Get summons for healing (if applicable)
            summons_to_heal = list(self.summons.sprites()) if hasattr(
                skill, 'heal_summons') and skill.heal_summons else None

            # Activate the heal skill with both player and summons
            Heal.activate(skill, self.owner, summons_to_heal)

            # Add visual effect for healing
            if game_effects_list is not None:
                effect = VisualEffect(
                    self.owner.x, self.owner.y, "heal", skill.color, 30, 0.5)
                game_effects_list.append(effect)

                # Add effects for healed summons too
                if summons_to_heal:
                    for summon in summons_to_heal:
                        if summon.alive and summon.health < summon.max_health:
                            effect = VisualEffect(
                                summon.x, summon.y, "heal", skill.color, 20, 0.3)
                            game_effects_list.append(effect)

        elif skill.skill_type == SkillType.AOE:
            # AOE primarily creates a visual effect and might apply damage immediately or over time
            if game_effects_list is not None:
                # Ensure duration is not zero
                # Minimum duration of 0.1 seconds
                duration = max(0.1, skill.duration)
                effect = VisualEffect(
                    target_x, target_y, "explosion", skill.color, skill.radius, duration)
                game_effects_list.append(effect)

            # Apply damage to enemies in radius
            AOE.activate(skill, target_x, target_y, enemies)
            
        elif skill.skill_type == SkillType.SLASH:
            # Slash creates a visual effect and applies damage in an arc
            if game_effects_list is not None:
                # Calculate angle from player to target
                angle = math.atan2(target_y - self.owner.y, target_x - self.owner.x)
                
                # Define sweep parameters
                arc_width = math.pi / 3  # 60 degree sweep
                # This is a CLOCKWISE sweep - starting to the left of target angle 
                # and ending to the right of target angle
                start_angle = angle - (arc_width / 2)  # Start 30 degrees to the "left" of target
                sweep_angle = arc_width  # Sweep 60 degrees clockwise
                
                # Create visual effect with the correct start angle and sweep direction
                effect = VisualEffect(
                    self.owner.x, 
                    self.owner.y, 
                    "slash", 
                    skill.color, 
                    skill.radius, 
                    0.3, 
                    start_angle=start_angle,
                    sweep_angle=sweep_angle
                )
                game_effects_list.append(effect)

            # Apply damage to enemies in arc - hit detection must match the visual
            # The start and sweep angles need to be passed to ensure consistency
            Slash.activate(skill, self.owner.x, self.owner.y,
                           target_x, target_y, enemies, start_angle, sweep_angle)
                           
        elif skill.skill_type == SkillType.CHAIN:
            # Call the Chain's activate method to perform the chain logic
            Chain.activate(skill, self.owner.x, self.owner.y, target_x, target_y, enemies)

        # Skill was successfully used
        return True

    def update(self, dt, enemies):
        """Update all active entities managed by the deck"""
        self._update_projectiles(dt, enemies)
        self._update_summons(dt, enemies)

    def _update_projectiles(self, dt, enemies):
        """Update all active projectiles"""
        # Use list comprehension to safely remove dead projectiles after update
        dead_projectiles = []
        for projectile in self.projectiles:
            if not projectile.update(dt, enemies):
                dead_projectiles.append(projectile)
        
        # Remove dead projectiles
        for projectile in dead_projectiles:
            self.projectiles.remove(projectile)

    def _update_summons(self, dt, enemies):
        """Update all active summons"""
        # Use list comprehension to safely remove dead summons after update
        dead_summons = []
        for summon in self.summons:
            if not summon.update(dt, enemies):
                dead_summons.append(summon)
        
        # Remove dead summons
        for summon in dead_summons:
            self.summons.remove(summon)

    def draw(self, surface):
        """Draw all active entities managed by the deck"""
        # Draw projectiles
        for projectile in self.projectiles:
            projectile.draw(surface)

        # Draw summons
        for summon in self.summons:
            summon.draw(surface)

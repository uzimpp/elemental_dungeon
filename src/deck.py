import csv
import math
import time
from skill import SkillType, ProjectileEntity, SummonEntity, Projectile, Summon, Heal, AOE, Slash, Chain
from config import (
    SHADOW_SUMMON_SPRITE_PATH,
    SHADOW_SUMMON_ANIMATION_CONFIG,
    ATTACK_RADIUS
)
from visual_effects import VisualEffect


class Deck:
    """Centralized manager for player skills, projectiles, and summons"""

    def __init__(self, owner):
        self.owner = owner
        self.skills = []
        self.active_projectiles = []
        self.active_summons = []
        self.summon_limit = 5

    @property
    def get_projectiles(self):
        return self.active_projectiles

    @property
    def get_summons(self):
        return self.active_summons

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
                            sprite_path = SHADOW_SUMMON_SPRITE_PATH
                            animation_config = SHADOW_SUMMON_ANIMATION_CONFIG
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
                            attack_radius=ATTACK_RADIUS
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
        print(
            f"[Deck] Using skill '{skill.name}' (Type: {skill.skill_type}) towards ({target_x}, {target_y})")

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
            print(
                f"[Deck] Set player state to '{action_state}' for {self.owner.attack_timer:.2f}s")
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

            self.active_projectiles.append(projectile_entity)
            print(
                f"[Deck] Created ProjectileEntity instance at ({spawn_x}, {spawn_y}).")

            # Add visual effect for casting at the spawn location
            if game_effects_list is not None:
                effect = VisualEffect(
                    spawn_x, spawn_y, "explosion", skill.color, 10, 0.2)
                game_effects_list.append(effect)
                print("[Deck] Added projectile cast visual effect.")

        elif skill.skill_type == SkillType.SUMMON:
            if len(self.active_summons) >= self.summon_limit:
                print(
                    f"[Deck] Summon limit ({self.summon_limit}) reached. Removing oldest.")
                self.active_summons.pop(0)  # Remove oldest summon

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
                skill, spawn_x, spawn_y, ATTACK_RADIUS)
            self.active_summons.append(summon_entity)
            print(
                f"[Deck] Created SummonEntity instance at ({spawn_x}, {spawn_y}) with sprite: {skill.sprite_path}")

            # Add visual effect for summoning at the spawn location
            if game_effects_list is not None:
                effect = VisualEffect(
                    spawn_x, spawn_y, "explosion", skill.color, 20, 0.3)
                game_effects_list.append(effect)
                print("[Deck] Added summon visual effect.")

        elif skill.skill_type == SkillType.HEAL:
            # Get summons for healing (if applicable)
            summons = self.active_summons if hasattr(
                skill, 'heal_summons') and skill.heal_summons else None

            # Activate the heal skill with both player and summons
            Heal.activate(skill, self.owner, summons)

            print(
                f"[Deck] Applied Heal skill to player and {len(self.active_summons) if summons else 0} summons.")

            # Add visual effect for healing
            if game_effects_list is not None:
                effect = VisualEffect(
                    self.owner.x, self.owner.y, "heal", skill.color, 30, 0.5)
                game_effects_list.append(effect)

                # Add effects for healed summons too
                if summons:
                    for summon in summons:
                        if summon.alive and summon.health < summon.max_health:
                            effect = VisualEffect(
                                summon.x, summon.y, "heal", skill.color, 20, 0.3)
                            game_effects_list.append(effect)

                print("[Deck] Added heal visual effects.")

        elif skill.skill_type == SkillType.AOE:
            # AOE primarily creates a visual effect and might apply damage immediately or over time
            print(f"[Deck] Activated AOE skill '{skill.name}'.")
            if game_effects_list is not None:
                # Ensure duration is not zero
                # Minimum duration of 0.1 seconds
                duration = max(0.1, skill.duration)
                effect = VisualEffect(
                    target_x, target_y, "explosion", skill.color, skill.radius, duration)
                game_effects_list.append(effect)
                print("[Deck] Added AOE visual effect.")

            # Apply damage to enemies in radius
            AOE.activate(skill, target_x, target_y, enemies)
        elif skill.skill_type == SkillType.SLASH:
            print(f"[Deck] Activated Slash skill '{skill.name}'.")
            # Slash creates a visual effect and applies damage in an arc
            if game_effects_list is not None:
                angle = math.atan2(target_y - self.owner.y,
                                   target_x - self.owner.x)
                effect = VisualEffect(
                    self.owner.x, self.owner.y, "slash", skill.color, skill.radius, 0.3, start_angle=angle)
                game_effects_list.append(effect)
                print("[Deck] Added Slash visual effect.")

            # Apply damage to enemies in arc
            Slash.activate(skill, self.owner.x, self.owner.y,
                           target_x, target_y, enemies)
        # --- Handle CHAIN etc. ---
        elif skill.skill_type == SkillType.CHAIN:
            print(
                f"[Deck] Activated Chain skill '{skill.name}' (Not fully implemented).")
            # Chain needs logic to find targets and create visual links/damage
            pass
        else:
            print(
                f"[Deck] Warning: Skill type {skill.skill_type} activation not fully implemented.")
        # Skill was successfully used (even if effect not fully implemented)
        return True

    def update(self, dt, enemies):
        """Update all active entities managed by the deck"""
        print(
            f"[Deck] update() called with {len(enemies)} enemies ({len([e for e in enemies if e.alive])} alive)")
        self._update_projectiles(dt, enemies)
        self._update_summons(dt, enemies)

    def _update_projectiles(self, dt, enemies):
        """Update all active projectiles"""
        print(
            f"[Deck] Updating {len(self.active_projectiles)} projectiles with {len(enemies)} enemies")
        if len(enemies) > 0:
            print(
                f"[Deck] First enemy at ({enemies[0].x:.1f}, {enemies[0].y:.1f}), alive={enemies[0].alive}, health={enemies[0].health}")

        # Process projectiles in reverse order for safe removal
        for i in range(len(self.active_projectiles) - 1, -1, -1):
            projectile = self.active_projectiles[i]
            # Only update if no collision occurred
            if projectile.update(dt, enemies):
                continue
            else:
                # Projectile expired or hit screen edge
                print(f"[Deck] Projectile {i} expired or hit something")
                self.active_projectiles.pop(i)

    def _update_summons(self, dt, enemies):
        """Update all active summons"""
        print(
            f"[Deck] Updating {len(self.active_summons)} summons with {len(enemies)} enemies")
        if len(enemies) > 0:
            print(
                f"[Deck] First enemy at ({enemies[0].x:.1f}, {enemies[0].y:.1f}), alive={enemies[0].alive}, health={enemies[0].health}")

        # Process summons in reverse order for safe removal
        for i in range(len(self.active_summons) - 1, -1, -1):
            summon = self.active_summons[i]
            print(
                f"[Deck] Updating summon {i+1} at ({summon.x:.1f}, {summon.y:.1f}), state: {summon.state}")
            result = summon.update(dt, enemies)
            print(f"[Deck] Summon update result: {result}")
            if not result:
                print(f"[Deck] Removing summon {i+1}")
                self.active_summons.pop(i)

    def draw(self, surface):
        """Draw all active entities managed by the deck"""
        print(f"[CRITICAL] Drawing {len(self.active_projectiles)} projectiles")

        # Draw projectiles
        for i, projectile in enumerate(self.active_projectiles):
            print(
                f"[CRITICAL] Drawing projectile {i} at ({projectile.x:.1f}, {projectile.y:.1f}), alive={projectile.alive}")
            projectile.draw(surface)

        # Draw summons
        for summon in self.active_summons:
            summon.draw(surface)

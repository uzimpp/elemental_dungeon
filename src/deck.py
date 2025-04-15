import csv
import math
import time
from skill import SkillType, ProjectileEntity, SummonEntity, Projectile, Summon, Heal, AOE, Slash, Chain
from config import (
    SHADOW_SUMMON_SPRITE_PATH,
    SHADOW_SUMMON_ANIMATION_CONFIG
)
from visual_effects import VisualEffect

class Deck:
    """Centralized manager for player skills, projectiles, and summons"""
    def __init__(self, owner):
        self.owner = owner  # Reference to the player
        self.skills = []    # Available skills
        self.active_projectiles = []
        self.active_summons = []
        self.summon_limit = 5
        
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
                            raise ValueError(f"Unsupported element for summon: {element}")
                            
                        skill = Summon(
                            name=row["name"],
                            element=element,
                            damage=int(row["damage"]),
                            speed=float(row["speed"]),
                            radius=float(row["radius"]),
                            duration=float('inf'),  # Infinite duration - summons stay until killed
                            cooldown=float(row["cooldown"]),
                            description=row["description"],
                            sprite_path=sprite_path,
                            animation_config=animation_config
                        )
                        print(f"[Deck] Created Summon skill: {skill.name} with sprite: {sprite_path}")
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
                        raise ValueError(f"Unknown skill type: {skill_type_str}")
                    self.skills.append(skill)
        except FileNotFoundError:
            raise ValueError(f"Error: CSV '{filename}' not found.")
        except KeyError as e:
            raise ValueError(f"CSV parsing error: missing column {e}")
            
        return self.skills
    
    def use_skill(self, index, target_x, target_y, enemies, now):
        """Activates a skill, creates entities/effects, and adds visual effects"""
        if not 0 <= index < len(self.skills):
            print(f"[Deck] Error: Skill index {index} out of bounds (0-{len(self.skills)-1})")
            return False

        skill = self.skills[index] # Get the skill *definition*

        if not skill.is_off_cooldown(now):
            print(f"[Deck] Skill '{skill.name}' is on cooldown.")
            return False

        # --- Skill Activation ---
        skill.trigger_cooldown() # Use the method in BaseSkill
        print(f"[Deck] Using skill '{skill.name}' (Type: {skill.skill_type}) towards ({target_x}, {target_y})")

        # --- Set Player Animation State ---
        action_state = 'cast' # Default animation
        if skill.skill_type == SkillType.SLASH:
             action_state = 'sweep'

        # Ensure animation config exists before accessing
        anim_config = self.owner.animation.config.get(action_state) if self.owner.animation else None
        if anim_config:
            self.owner.state = action_state
            self.owner.animation.set_state(action_state, force_reset=True)
            animations = anim_config.get('animations', [])
            duration_per_frame = anim_config.get('duration', 0.1)
            self.owner.attack_timer = len(animations) * duration_per_frame
            print(f"[Deck] Set player state to '{action_state}' for {self.owner.attack_timer:.2f}s")
        else:
            print(f"Warning: Animation config not found for state '{action_state}'. Setting default timer.")
            self.owner.state = action_state # Still set state even if no animation
            self.owner.attack_timer = 0.5 # Default action duration

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
            projectile_entity = ProjectileEntity(spawn_x, spawn_y, target_x, target_y, skill)
            self.active_projectiles.append(projectile_entity)
            print(f"[Deck] Created ProjectileEntity instance at ({spawn_x}, {spawn_y}).")
            
            # Add visual effect for casting at the spawn location
            if game_effects_list is not None:
                effect = VisualEffect(spawn_x, spawn_y, "explosion", skill.color, 10, 0.2)
                game_effects_list.append(effect)
                print("[Deck] Added projectile cast visual effect.")

        elif skill.skill_type == SkillType.SUMMON:
            if len(self.active_summons) >= self.summon_limit:
                print(f"[Deck] Summon limit ({self.summon_limit}) reached. Removing oldest.")
                self.active_summons.pop(0) # Remove oldest summon

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
            summon_entity = SummonEntity(spawn_x, spawn_y, skill)
            self.active_summons.append(summon_entity)
            print(f"[Deck] Created SummonEntity instance at ({spawn_x}, {spawn_y}) with sprite: {skill.sprite_path}")
            
            # Add visual effect for summoning at the spawn location
            if game_effects_list is not None:
                effect = VisualEffect(spawn_x, spawn_y, "explosion", skill.color, 20, 0.3)
                game_effects_list.append(effect)
                print("[Deck] Added summon visual effect.")

        elif skill.skill_type == SkillType.HEAL:
            # Get summons for healing (if applicable)
            summons = self.active_summons if hasattr(skill, 'heal_summons') and skill.heal_summons else None
            
            # Activate the heal skill with both player and summons
            Heal.activate(skill, self.owner, summons)
            
            print(f"[Deck] Applied Heal skill to player and {len(self.active_summons) if summons else 0} summons.")
            
            # Add visual effect for healing
            if game_effects_list is not None:
                effect = VisualEffect(self.owner.x, self.owner.y, "heal", skill.color, 30, 0.5)
                game_effects_list.append(effect)
                
                # Add effects for healed summons too
                if summons:
                    for summon in summons:
                        if summon.alive and summon.health < summon.max_health:
                            effect = VisualEffect(summon.x, summon.y, "heal", skill.color, 20, 0.3)
                            game_effects_list.append(effect)
                
                print("[Deck] Added heal visual effects.")

        elif skill.skill_type == SkillType.AOE:
            # AOE primarily creates a visual effect and might apply damage immediately or over time
            print(f"[Deck] Activated AOE skill '{skill.name}'.")
            if game_effects_list is not None:
                # Ensure duration is not zero
                duration = max(0.1, skill.duration)  # Minimum duration of 0.1 seconds
                effect = VisualEffect(target_x, target_y, "explosion", skill.color, skill.radius, duration)
                game_effects_list.append(effect)
                print("[Deck] Added AOE visual effect.")
            
            # Apply damage to enemies in radius
            AOE.activate(skill, target_x, target_y, enemies)

        elif skill.skill_type == SkillType.SLASH:
            print(f"[Deck] Activated Slash skill '{skill.name}'.")
            # Slash creates a visual effect and applies damage in an arc
            if game_effects_list is not None:
                 angle = math.atan2(target_y - self.owner.y, target_x - self.owner.x)
                 effect = VisualEffect(self.owner.x, self.owner.y, "slash", skill.color, skill.radius, 0.3, start_angle=angle)
                 game_effects_list.append(effect)
                 print("[Deck] Added Slash visual effect.")
            
            # Apply damage to enemies in arc
            Slash.activate(skill, self.owner.x, self.owner.y, target_x, target_y, enemies)

        # --- Handle CHAIN etc. ---
        elif skill.skill_type == SkillType.CHAIN:
             print(f"[Deck] Activated Chain skill '{skill.name}' (Not fully implemented).")
             # Chain needs logic to find targets and create visual links/damage
             pass

        else:
             print(f"[Deck] Warning: Skill type {skill.skill_type} activation not fully implemented.")


        return True # Skill was successfully used (even if effect not fully implemented)
    
    def update(self, dt, enemies):
        """Update all active entities managed by the deck"""
        print(f"[Deck] Updating {len(self.active_projectiles)} projectiles and {len(self.active_summons)} summons with {len(enemies)} enemies")
        
        # --- Update Projectiles ---
        for i in reversed(range(len(self.active_projectiles))):
            projectile = self.active_projectiles[i]
            if not projectile.update(dt, enemies): # Use ProjectileEntity's update
                self.active_projectiles.pop(i)
                continue

            # Check collisions
            for enemy in enemies:
                if not enemy.alive: continue
                dist = math.hypot(enemy.x - projectile.x, enemy.y - projectile.y)
                if dist < (enemy.radius + projectile.radius):
                    print(f"[Deck] Projectile hit enemy at ({enemy.x:.0f}, {enemy.y:.0f})")
                    enemy.take_damage(projectile.damage)
                    projectile.alive = False # Mark projectile for removal

                    # Create hit effect
                    game_effects_list = getattr(getattr(self.owner, 'game', None), 'effects', None)
                    if game_effects_list is not None:
                        effect = VisualEffect(projectile.x, projectile.y, "explosion", projectile.color, 15, 0.2)
                        game_effects_list.append(effect)

                    self.active_projectiles.pop(i) # Remove projectile immediately after hit
                    break # Move to next projectile

        # --- Update Summons ---
        for i in reversed(range(len(self.active_summons))):
            summon = self.active_summons[i]
            print(f"[Deck] Updating summon {i+1} at ({summon.x:.1f}, {summon.y:.1f}), state: {summon.state}")
            result = summon.update(dt, enemies)
            print(f"[Deck] Summon update result: {result}")
            if not result:
                print(f"[Deck] Removing summon {i+1}")
                self.active_summons.pop(i)


    def draw(self, surface):
        """Draw all active entities managed by the deck"""
        print(f"[Deck] Drawing {len(self.active_projectiles)} projectiles and {len(self.active_summons)} summons")
        
        # Draw projectiles
        for projectile in self.active_projectiles:
            projectile.draw(surface) # Use ProjectileEntity's draw
            
        # Draw summons
        for i, summon in enumerate(self.active_summons):
            print(f"[Deck] Drawing summon {i+1}/{len(self.active_summons)} at ({summon.x:.1f}, {summon.y:.1f})")
            summon.draw(surface) # Use SummonEntity's draw

    # Keep getters for compatibility if needed by other parts (like Player properties)
    def get_projectiles(self):
        return self.active_projectiles

    def get_summons(self):
        return self.active_summons

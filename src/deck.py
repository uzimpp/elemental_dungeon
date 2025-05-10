import time
import csv
import math
import json
import os
from skill import SkillType, Projectile, Summon, Heal, AOE, Slash, Chain
from visual_effects import VisualEffectManager
from config import Config
from resources import Resources


class Deck:
    """Manages a collection of skills for the player"""
    def __init__(self, owner):
        self.resources = Resources.get_instance()
        self.owner = owner
        self.skills = []
        self.active_summons = []
        self.active_projectiles = []
        self.summon_limit = 5  # Default limit of summons
        self.effect_manager = VisualEffectManager()

    @property
    def get_projectiles(self):
        return self.active_projectiles

    @property
    def get_summons(self):
        return self.active_summons

    def load_from_csv(self, csv_name=None):
        """Load skills from CSV using Resources"""
        # Use Resources to load the skills CSV
        csv_path = Config.SKILLS_PATH if csv_name is None else csv_name
        # Make sure the file exists
        if not os.path.exists(csv_path):
            print(f"[Deck] Error: Skills file not found: {csv_path}")
            return False
        # Load skill data from CSV
        skills_data = []
        try:
            with open(csv_path, mode='r', newline='', encoding='utf-8') as file:
                csv_reader = csv.DictReader(file)
                for row in csv_reader:
                    skills_data.append(row)
        except Exception as e:
            print(f"[Deck] Error loading CSV: {e}")
            return False
            
        if not skills_data:
            print("[Deck] Error: Could not load skills data")
            return False
            
        # Parse the skills data
        for row in skills_data:
            try:
                skill_type = row.get('Type', '').upper()
                if not skill_type:
                    continue
                # All skills need these parameters
                name = row.get('Name', 'Unknown Skill')
                element = row.get('Element', 'FIRE').upper()
                cooldown = float(row.get('Cooldown', 5.0))
                description = row.get('Description', '')
                if skill_type == 'PROJECTILE':
                    # Create projectile skill
                    skill = Projectile(
                        name=name,
                        element=element,
                        damage=float(row.get('Damage', 10.0)),
                        speed=float(row.get('Speed', 5.0)),
                        radius=float(row.get('Radius', 15.0)),
                        duration=float(row.get('Duration', 0.3)),
                        cooldown=cooldown,
                        description=description
                    )
                    self.skills.append(skill)
                elif skill_type == 'SUMMON':
                    # Create summon skill
                    skill = Summon(
                        name=name,
                        element=element,
                        damage=float(row.get('Damage', 5.0)),
                        speed=float(row.get('Speed', 3.0)),
                        radius=float(row.get('Radius', 20.0)),
                        duration=float(row.get('Duration', 30.0)),
                        cooldown=cooldown,
                        description=description,
                        sprite_path=row.get('SpritePath', Config.SHADOW_SUMMON_SPRITE_PATH),
                        animation_config=None,  # Animation class will use default config
                        attack_radius=float(row.get('AttackRadius', 50.0))
                    )
                    self.skills.append(skill)
                elif skill_type == 'HEAL':
                    # Create heal skill
                    skill = Heal(
                        name=name,
                        element=element,
                        heal_amount=float(row.get('HealAmount', 20.0)),
                        radius=float(row.get('Radius', 30.0)),
                        cooldown=cooldown,
                        description=description,
                        heal_summons=row.get('HealSummons', 'False').lower() == 'true'
                    )
                    self.skills.append(skill)
                elif skill_type == 'AOE':
                    # Create AOE skill
                    skill = AOE(
                        name=name,
                        element=element,
                        damage=float(row.get('Damage', 15.0)),
                        radius=float(row.get('Radius', 80.0)),
                        duration=float(row.get('Duration', 0.5)),
                        cooldown=cooldown,
                        description=description
                    )
                    self.skills.append(skill)
                elif skill_type == 'SLASH':
                    # Create slash skill
                    skill = Slash(
                        name=name,
                        element=element,
                        damage=float(row.get('Damage', 20.0)),
                        radius=float(row.get('Radius', 60.0)),
                        duration=float(row.get('Duration', 0.4)),
                        cooldown=cooldown,
                        description=description
                    )
                    self.skills.append(skill)
                elif skill_type == 'CHAIN':
                    # Create chain skill
                    skill = Chain(
                        name=name,
                        element=element,
                        damage=float(row.get('Damage', 12.0)),
                        radius=float(row.get('Radius', 150.0)),
                        duration=float(row.get('Duration', 0.6)),
                        cooldown=cooldown,
                        description=description,
                        chain_count=int(row.get('ChainCount', 3))
                    )
                    self.skills.append(skill)
                # Set owner for the skill
                skill.owner = self.owner
                print(f"[Deck] Loaded skill: {name} ({skill_type})")
            except Exception as e:
                print(f"[Deck] Error loading skill: {e}")
                continue
        print(f"[Deck] Successfully loaded {len(self.skills)} skills")
        return True

    def use_skill(self, skill_idx, target_x, target_y, enemies, now=None):
        """Use a skill by index"""
        if not self.skills or skill_idx < 0 or skill_idx >= len(self.skills):
            return False

        skill = self.skills[skill_idx]

        # Check cooldown
        if not skill.is_off_cooldown(now):
            print(f"[Deck] Skill {skill.name} is on cooldown")
            return False

        # Activate skill based on its type
        try:
            if skill.skill_type == SkillType.PROJECTILE:
                # Create and track projectile
                projectile = skill.activate(
                    self.owner.x, self.owner.y, target_x, target_y, enemies)
                projectile.owner = self.owner
                self.active_projectiles.append(projectile)
                
            elif skill.skill_type == SkillType.SUMMON:
                # Check summon limit
                if len(self.active_summons) >= self.summon_limit:
                    print(f"[Deck] Reached summon limit ({self.summon_limit})")
                    return False

                # Create and track summon
                summon = skill.activate(
                    self.owner.x, self.owner.y, target_x, target_y, enemies)
                summon.owner = self.owner
                self.active_summons.append(summon)

            elif skill.skill_type == SkillType.HEAL:
                # Heal the player and possibly summons
                skill.activate(self.owner, self.active_summons)

            elif skill.skill_type == SkillType.AOE:
                # Apply AOE damage
                skill.activate(target_x, target_y, enemies)

            elif skill.skill_type == SkillType.SLASH:
                # Apply slash attack
                skill.activate(self.owner.x, self.owner.y, target_x, target_y, enemies)
                
            elif skill.skill_type == SkillType.CHAIN:
                # Apply chain lightning
                skill.activate(self.owner.x, self.owner.y, target_x, target_y, enemies)
                
            # Start cooldown
            skill.trigger_cooldown()
            return True
            
        except Exception as e:
            print(f"[Deck] Error using skill: {e}")
            return False
            
    def update(self, dt, enemies):
        """Update all active summons and projectiles"""
        # Update summons
        for summon in self.active_summons[:]:
            still_active = summon.update(dt, enemies)
            if not still_active:
                self.active_summons.remove(summon)
                
        # Update projectiles
        for projectile in self.active_projectiles[:]:
            still_active = projectile.update(dt, enemies)
            if not still_active:
                self.active_projectiles.remove(projectile)
                
        self.effect_manager.update(dt)

    def draw(self, surface):
        """Draw all active summons and projectiles"""
        # Draw summons
        for summon in self.active_summons:
            summon.draw(surface)
            
        # Draw projectiles
        for projectile in self.active_projectiles:
            projectile.draw(surface)
            
        # Draw effects
        self.effect_manager.draw(surface)

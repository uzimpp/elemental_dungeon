import csv
import math
import time
import json
from skill import SkillType, Projectile, Summon, Heal, AOE, Slash, Chain
from visual_effects import VisualEffectManager
from resources import Resources


class Deck:
    """Manages a collection of skills and their active instances"""
    def __init__(self, player, summon_limit=3):
        self.player = player
        self.summon_limit = summon_limit
        self.active_projectiles = []
        self.active_summons = []
        self.skills = []
        self.effect_manager = VisualEffectManager()

    @property
    def get_projectiles(self):
        return self.active_projectiles

    @property
    def get_summons(self):
        return self.active_summons

    def load_from_csv(self, csv_path):
        """Load skills from a CSV file"""
        # First check if skills are already cached
        cached_skills = Resources.get_instance().load_file(csv_path)
        if cached_skills:
            self.skills = cached_skills
            return

        # If not cached, load from CSV
        with open(csv_path, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                skill = self._create_skill(row)
                if skill:
                    skill.set_effect_manager(self.effect_manager)
                    self.skills.append(skill)

        # Cache the loaded skills
        Resources.get_instance().cache_file(csv_path, self.skills)

    def _create_skill(self, row):
        """Create a skill instance from a CSV row"""
        try:
            # Common parameters
            name = row['name']
            element = row['element']
            cooldown = float(row['cooldown'])
            description = row['description']
            skill_type = SkillType[row['type'].upper()]

            # Type-specific parameters
            if skill_type == SkillType.PROJECTILE:
                return Projectile(
                    name, element,
                    damage=float(row['damage']),
                    speed=float(row['speed']),
                    radius=float(row['radius']),
                    duration=float(row['duration']),
                    cooldown=cooldown,
                    description=description
                )
            elif skill_type == SkillType.SUMMON:
                return Summon(
                    name, element,
                    damage=float(row['damage']),
                    speed=float(row['speed']),
                    radius=float(row['radius']),
                    duration=float(row['duration']),
                    cooldown=cooldown,
                    description=description,
                    sprite_path=row['sprite_path'],
                    animation_config=json.loads(row['animation_config']),
                    attack_radius=float(row['attack_radius'])
                )
            elif skill_type == SkillType.HEAL:
                return Heal(
                    name, element,
                    heal_amount=float(row['heal_amount']),
                    radius=float(row['radius']),
                    cooldown=cooldown,
                    description=description,
                    heal_summons=row.get('heal_summons', 'false').lower() == 'true'
                )
            elif skill_type == SkillType.AOE:
                return AOE(
                    name, element,
                    damage=float(row['damage']),
                    radius=float(row['radius']),
                    duration=float(row['duration']),
                    cooldown=cooldown,
                    description=description
                )
            elif skill_type == SkillType.SLASH:
                return Slash(
                    name, element,
                    damage=float(row['damage']),
                    radius=float(row['radius']),
                    duration=float(row['duration']),
                    cooldown=cooldown,
                    description=description
                )
            elif skill_type == SkillType.CHAIN:
                return Chain(
                    name, element,
                    damage=float(row['damage']),
                    radius=float(row['radius']),
                    duration=float(row['duration']),
                    cooldown=cooldown,
                    description=description,
                    chain_count=int(row.get('chain_count', 3))
                )
        except (KeyError, ValueError) as e:
            print(f"Error creating skill from row: {e}")
            return None

    def use_skill(self, skill_index, target_x, target_y, enemies):
        """Use a skill at the specified index"""
        if not 0 <= skill_index < len(self.skills):
            return False

        skill = self.skills[skill_index]
        if not skill.is_off_cooldown(time.time()):
            return False

        # Use the skill's activate method based on type
        if skill.skill_type == SkillType.PROJECTILE:
            projectile = skill.activate(self.player.x, self.player.y, target_x, target_y, enemies)
            self.active_projectiles.append(projectile)
        elif skill.skill_type == SkillType.SUMMON:
            if len(self.active_summons) >= self.summon_limit:
                self.active_summons.pop(0)
            summon = skill.activate(self.player.x, self.player.y, target_x, target_y, enemies)
            self.active_summons.append(summon)
        elif skill.skill_type == SkillType.HEAL:
            summons = self.active_summons if hasattr(skill, 'heal_summons') and skill.heal_summons else None
            skill.activate(self.player, summons)
        else:
            skill.activate(self.player.x, self.player.y, target_x, target_y, enemies)

        skill.trigger_cooldown()
        return True

    def update(self, dt, enemies):
        """Update all active entities managed by the deck"""
        self._update_projectiles(dt, enemies)
        self._update_summons(dt, enemies)
        self.effect_manager.update(dt)

    def _update_projectiles(self, dt, enemies):
        """Update all active projectiles"""
        for i, projectile in enumerate(self.active_projectiles):
            if not projectile.update(dt, enemies):
                self.active_projectiles.pop(i)

    def _update_summons(self, dt, enemies):
        """Update all active summons"""
        for i, summon in enumerate(self.active_summons):
            if not summon.update(dt, enemies):
                self.active_summons.pop(i)

    def draw(self, surface):
        """Draw all active entities and effects"""
        # Draw projectiles
        for projectile in self.active_projectiles:
            projectile.draw(surface)

        # Draw summons
        for summon in self.active_summons:
            summon.draw(surface)

        # Draw effects
        self.effect_manager.draw(surface)

# skill.py
import time
from enum import Enum, auto
import math
import pygame
from utils import draw_hp_bar
from config import (
    WIDTH, HEIGHT, FPS,
    WHITE, BLACK, RED, BLUE, PURPLE, GREEN,
    ELEMENT_COLORS, SHADOW_SUMMON_SPRITE_PATH, SHADOW_SUMMON_ANIMATION_CONFIG,
    ENEMY_SPRITE_PATH, ENEMY_ANIMATION_CONFIG
)
from animation import CharacterAnimation
import sys
import csv
from entity import Entity  # Import the Entity base class

class SkillType(Enum):
    PROJECTILE = auto()
    SUMMON = auto()
    HEAL = auto()
    AOE = auto()
    SLASH = auto()
    CHAIN = auto()

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
                            duration=float(row["duration"]),
                            cooldown=float(row["cooldown"]),
                            description=row["description"],
                            sprite_path=sprite_path,
                            animation_config=animation_config
                        )
                    elif skill_type == SkillType.HEAL:
                        skill = Heal(
                            name=row["name"],
                            element=row["element"].upper(),
                            heal_amount=int(row["heal_amount"]),
                            radius=float(row["radius"]),
                            duration=float(row["duration"]),
                            cooldown=float(row["cooldown"]),
                            description=row["description"]
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
                    
                    self.skills.append(skill)
                    
        except FileNotFoundError:
            print(f"Error: CSV '{filename}' not found.")
            return []
        except KeyError as e:
            print(f"CSV parsing error: missing column {e}")
            return []
            
        return self.skills
    
    def use_skill(self, index, target_x, target_y):
        """Attempt to use a skill at the target position"""
        if not 0 <= index < len(self.skills):
            return False
            
        skill = self.skills[index]
        if not skill.is_off_cooldown():
            return False
            
        # Put skill on cooldown
        skill.trigger_cooldown()
        
        # Set animation state on player with proper duration
        if skill.skill_type == SkillType.SLASH:
            self.owner.state = 'sweep'
            self.owner.animation.set_state('sweep', force_reset=True)
            animations_length = len(self.owner.animation.config['sweep']['animations'])
            duration = self.owner.animation.config['sweep']['duration'] * animations_length
            self.owner.attack_timer = duration
        else:
            self.owner.state = 'cast'
            self.owner.animation.set_state('cast', force_reset=True)
            animations_length = len(self.owner.animation.config['cast']['animations'])
            duration = self.owner.animation.config['cast']['duration'] * animations_length
            self.owner.attack_timer = duration
        
        # Handle skill activation based on type
        if skill.skill_type == SkillType.PROJECTILE:
            projectile = Projectile.create(
                skill,
                self.owner.x,
                self.owner.y,
                target_x,
                target_y
            )
            self.active_projectiles.append(projectile)
            
        elif skill.skill_type == SkillType.SUMMON:
            if len(self.active_summons) >= self.summon_limit:
                # Remove oldest summon
                self.active_summons.pop(0)
                
            summon = Summon.create(skill, target_x, target_y)
            self.active_summons.append(summon)
            
        elif skill.skill_type == SkillType.HEAL:
            Heal.activate(skill, self.owner)
            
        elif skill.skill_type == SkillType.AOE:
            # Add effects handling here
            pass
            
        elif skill.skill_type == SkillType.SLASH:
            # Add slash effects here
            pass
            
        elif skill.skill_type == SkillType.CHAIN:
            # Add chain effects here
            pass
            
        return True
    
    def update(self, dt, enemies):
        """Update all active projectiles and summons"""
        # Update projectiles
        for i in reversed(range(len(self.active_projectiles))):
            projectile = self.active_projectiles[i]
            if not Projectile.update(projectile, dt):
                # Check for collisions with enemies
                hit = False
                for enemy in enemies:
                    if Projectile.check_collision(projectile, enemy):
                        enemy.take_damage(projectile['damage'])
                        hit = True
                        break
                
                if hit or projectile['life_time'] >= projectile['max_life_time']:
                    self.active_projectiles.pop(i)
        
        # Update summons
        for i in reversed(range(len(self.active_summons))):
            summon = self.active_summons[i]
            if not Summon.update(summon, dt, enemies):
                self.active_summons.pop(i)
    
    def draw(self, surface):
        """Draw all active projectiles and summons"""
        print(f"Drawing {len(self.active_projectiles)} projectiles and {len(self.active_summons)} summons")
        for projectile in self.active_projectiles:
            Projectile.draw(projectile, surface)
            
        for summon in self.active_summons:
            Summon.draw(summon, surface)
    
    def get_projectiles(self):
        return self.active_projectiles
    
    def get_summons(self):
        return self.active_summons

class BaseSkill:
    """Base class for all skills"""
    def __init__(self, name, element, skill_type, cooldown, description):
        self.name = name
        self.element = element
        self.skill_type = skill_type
        self.cooldown = cooldown
        self.description = description
        self.last_use_time = 0
        self.color = self._get_color_from_element(element)
    
    def _get_color_from_element(self, element):
        if element in ELEMENT_COLORS:
            return ELEMENT_COLORS[element]['primary']
        return WHITE  # Default fallback
    
    def is_off_cooldown(self, current_time=None):
        if current_time is None:
            current_time = time.time()
        return (current_time - self.last_use_time) >= self.cooldown
    
    def trigger_cooldown(self):
        self.last_use_time = time.time()

class ProjectileEntity(Entity):
    def __init__(self, start_x, start_y, target_x, target_y, skill):
        super().__init__(start_x, start_y, 5, 1, skill.speed, skill.color)
        
        # Calculate direction vector
        dist = math.hypot(target_x - start_x, target_y - start_y)
        if dist == 0:
            dist = 1
        self.dx = (target_x - start_x) / dist
        self.dy = (target_y - start_y) / dist
        
        # Set speed in pixels per second
        self.speed = skill.speed * 60
        
        # Projectile attributes
        self.damage = skill.damage
        self.element = skill.element
        self.life_time = 0
        self.max_life_time = skill.duration
        
    def update(self, dt):
        # Update position
        self.x += self.dx * self.speed * dt
        self.y += self.dy * self.speed * dt
        self.life_time += dt
        
        # Check if out of bounds or expired
        if (self.x < 0 or self.x > WIDTH or
            self.y < 0 or self.y > HEIGHT or
            self.life_time >= self.max_life_time):
            self.alive = False
            
        return self.alive

class Projectile(BaseSkill):
    """Projectile skill with static methods for managing projectile instances"""
    def __init__(self, name, element, damage, speed, radius, duration, cooldown, description):
        super().__init__(name, element, SkillType.PROJECTILE, cooldown, description)
        self.damage = damage
        self.speed = speed
        self.radius = radius
        self.duration = duration
    
    @staticmethod
    def create(skill, start_x, start_y, target_x, target_y):
        """Create a projectile instance"""
        # Calculate direction vector
        dx = target_x - start_x
        dy = target_y - start_y
        dist = math.hypot(dx, dy)
        if dist == 0:
            dist = 1
        
        # Normalize and scale by speed
        dx = (dx / dist) * skill.speed * 60  # Convert to pixels per second
        dy = (dy / dist) * skill.speed * 60
        
        return {
            'x': start_x,
            'y': start_y,
            'dx': dx,
            'dy': dy,
            'radius': 5,  # Visual radius
            'damage': skill.damage,
            'color': skill.color,
            'life_time': 0,
            'max_life_time': skill.duration,
            'element': skill.element
        }
    
    @staticmethod
    def update(projectile, dt):
        """Update projectile position"""
        projectile['x'] += projectile['dx'] * dt
        projectile['y'] += projectile['dy'] * dt
        projectile['life_time'] += dt
        
        # Check if out of bounds
        if (projectile['x'] < 0 or projectile['x'] > WIDTH or
            projectile['y'] < 0 or projectile['y'] > HEIGHT):
            return False
        
        return True
    
    @staticmethod
    def draw(projectile, surface):
        """Draw projectile on screen"""
        pygame.draw.circle(
            surface,
            projectile['color'],
            (int(projectile['x']), int(projectile['y'])),
            projectile['radius']
        )
    
    @staticmethod
    def check_collision(projectile, enemy):
        """Check if projectile hits an enemy"""
        if not enemy.alive:
            return False
            
        dist = math.hypot(enemy.x - projectile['x'], enemy.y - projectile['y'])
        return dist < (enemy.radius + projectile['radius'])

class SummonEntity(Entity):
    """Entity class for summons that behaves like other game entities"""
    def __init__(self, x, y, skill):
        # Call parent Entity constructor
        super().__init__(
            x=x, 
            y=y,
            radius=12,
            max_health=50,  # Fixed starting health
            speed=skill.speed,
            color=skill.color
        )
        
        # Summon-specific properties
        self.damage = skill.damage
        self.element = skill.element
        self.start_time = time.time()
        self.max_life_time = skill.duration
        self.state = 'idle'
        
        # Set up animation
        self.animation = CharacterAnimation(
            sprite_sheet_path=skill.sprite_path,
            config=skill.animation_config,
            sprite_width=32,
            sprite_height=32
        )
    
    def update(self, dt, enemies):
        """Update summon behavior"""
        if not self.alive:
            return False
            
        # Check lifetime
        current_time = time.time()
        if current_time - self.start_time >= self.max_life_time:
            self.alive = False
            return False
            
        # Find closest enemy
        closest = None
        closest_dist = float('inf')
        
        for enemy in enemies:
            if enemy.alive:
                dist = math.hypot(enemy.x - self.x, enemy.y - self.y)
                if dist < closest_dist:
                    closest_dist = dist
                    closest = enemy
        
        # Update movement and state
        if closest and closest_dist > 0:
            self.dx = (closest.x - self.x) / closest_dist
            self.dy = (closest.y - self.y) / closest_dist
            
            # Set animation state based on distance
            if closest_dist < (self.radius + closest.radius):
                if self.state != 'sweep':
                    self.state = 'sweep'
                    self.animation.set_state('sweep', force_reset=True)
                closest.take_damage(self.damage * 0.1)
            else:
                if self.state != 'walk':
                    self.state = 'walk'
                    self.animation.set_state('walk')
                self.x += self.dx * self.speed * dt
                self.y += self.dy * self.speed * dt
        else:
            if self.state != 'idle':
                self.state = 'idle'
                self.animation.set_state('idle')
        
        # Update animation
        self.animation.update(dt, self.dx, self.dy)
        
        # Keep within screen bounds
        self.x = max(self.radius, min(WIDTH - self.radius, self.x))
        self.y = max(self.radius, min(HEIGHT - self.radius, self.y))
        
        return self.alive
    
    def take_damage(self, amount):
        """Override take_damage to handle animations"""
        if not self.alive:
            return
            
        super().take_damage(amount)  # Call parent method
        
        if self.health <= 0:
            if self.state != 'dying':
                self.state = 'dying'
                self.animation.set_state('dying', force_reset=True)
        else:
            # Play hurt animation if not in more important state
            if self.state not in ['dying', 'sweep']:
                self.state = 'hurt'
                self.animation.set_state('hurt', force_reset=True)
    
    def draw(self, surface):
        """Draw summon with sprite or fallback"""
        current_sprite = self.animation.get_current_sprite()
        
        if current_sprite:
            # Calculate drawing position
            draw_x = self.x - 16  # Half of sprite width
            draw_y = self.y - 16  # Half of sprite height
            surface.blit(current_sprite, (int(draw_x), int(draw_y)))
        else:
            # Fallback to circle
            pygame.draw.circle(
                surface, 
                self.color, 
                (int(self.x), int(self.y)), 
                self.radius
            )
        
        # Draw health bar
        bar_x = self.x - 25
        bar_y = self.y - self.radius - 10
        draw_hp_bar(
            surface, 
            bar_x, 
            bar_y, 
            self.health, 
            self.max_health, 
            GREEN
        )

class Summon(BaseSkill):
    """Summon skill that creates SummonEntity instances"""
    def __init__(self, name, element, damage, speed, radius, duration, cooldown, description, sprite_path, animation_config):
        super().__init__(name, element, SkillType.SUMMON, cooldown, description)
        self.damage = damage
        self.speed = speed
        self.radius = radius
        self.duration = duration
        self.sprite_path = sprite_path
        self.animation_config = animation_config
    
    @staticmethod
    def create(skill, x, y):
        """Create a SummonEntity instance"""
        return SummonEntity(x, y, skill)
    
    @staticmethod
    def update(summon, dt, enemies):
        """Update the summon (for compatibility with existing code)"""
        return summon.update(dt, enemies)
    
    @staticmethod
    def draw(summon, surface):
        """Draw the summon (for compatibility with existing code)"""
        summon.draw(surface)

class Heal(BaseSkill):
    """Heal skill implementation"""
    def __init__(self, name, element, heal_amount, radius, duration, cooldown, description):
        super().__init__(name, element, SkillType.HEAL, cooldown, description)
        self.heal_amount = heal_amount
        self.radius = radius
        self.duration = duration
    
    @staticmethod
    def activate(skill, target):
        """Apply healing to target"""
        target.heal(skill.heal_amount)
        # Visual effects could be added here

class AOE(BaseSkill):
    """Area of Effect skill implementation"""
    def __init__(self, name, element, damage, radius, duration, cooldown, description):
        super().__init__(name, element, SkillType.AOE, cooldown, description)
        self.damage = damage
        self.radius = radius
        self.duration = duration

class Slash(BaseSkill):
    """Slash attack skill implementation"""
    def __init__(self, name, element, damage, radius, duration, cooldown, description):
        super().__init__(name, element, SkillType.SLASH, cooldown, description)
        self.damage = damage
        self.radius = radius
        self.duration = duration

class Chain(BaseSkill):
    """Chain attack skill implementation"""
    def __init__(self, name, element, damage, radius, duration, pull, cooldown, description):
        super().__init__(name, element, SkillType.CHAIN, cooldown, description)
        self.damage = damage
        self.radius = radius
        self.duration = duration
        self.pull = pull

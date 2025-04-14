# wave_manager.py
import random
from enemy import MeleeEnemy, RangedEnemy, BossEnemy
from config import (
    WIDTH, HEIGHT, 
    ENEMY_BASE_HP, ENEMY_BASE_SPEED, 
    WAVE_MULTIPLIER, ENEMY_DAMAGE, ATTACK_COOLDOWN,
    RED, BLUE, PURPLE
)

class WaveManager:
    """Manages enemy wave generation and difficulty scaling"""
    
    def __init__(self):
        self.current_wave = 1
        self.boss_waves = [5, 10, 15, 20]  # Waves where bosses appear
    
    def spawn_wave(self, wave_number, enemies_list):
        """Spawn a new wave of enemies and add them to the provided list"""
        # Clear any existing enemies
        enemies_list.clear()
        
        # Check if this is a boss wave
        if wave_number in self.boss_waves:
            self._spawn_boss_wave(wave_number, enemies_list)
        else:
            self._spawn_regular_wave(wave_number, enemies_list)
        
        self.current_wave = wave_number
    
    def _spawn_regular_wave(self, wave_number, enemies_list):
        """Spawn a mix of melee and ranged enemies."""
        # Total number of enemies increases with wave number
        n_enemies = 5 + wave_number
        
        # As waves progress, increase the proportion of ranged enemies
        ranged_percent = min(50, 10 + wave_number * 3)  # Max 50% ranged
        n_ranged = int(n_enemies * ranged_percent / 100)
        n_melee = n_enemies - n_ranged
        
        # Spawn melee enemies
        for _ in range(n_melee):
            x = random.randint(50, WIDTH - 50)  # Keep enemies away from edges
            y = random.randint(50, HEIGHT - 50)
            e = MeleeEnemy(
                x, y, wave_number,
                radius=15,
                base_speed=ENEMY_BASE_SPEED,
                base_hp=ENEMY_BASE_HP,
                wave_multiplier=WAVE_MULTIPLIER,
                color=RED,
                damage=ENEMY_DAMAGE,
                attack_cooldown=ATTACK_COOLDOWN
            )
            enemies_list.append(e)
        
        # Spawn ranged enemies
        for _ in range(n_ranged):
            x = random.randint(50, WIDTH - 50)  # Keep enemies away from edges
            y = random.randint(50, HEIGHT - 50)
            e = RangedEnemy(
                x, y, wave_number,
                radius=15,
                base_speed=ENEMY_BASE_SPEED * 0.8,  # Slightly slower
                base_hp=ENEMY_BASE_HP * 0.8,        # Less HP
                wave_multiplier=WAVE_MULTIPLIER,
                color=BLUE,
                damage=ENEMY_DAMAGE * 0.7,          # Less damage
                attack_cooldown=ATTACK_COOLDOWN * 2,  # Longer cooldown
                projectile_speed=300,
                attack_range=250
            )
            enemies_list.append(e)
    
    def _spawn_boss_wave(self, wave_number, enemies_list):
        """Spawn a boss with some minions."""
        # Boss in the center
        boss = BossEnemy(
            WIDTH // 2, HEIGHT // 2,
            wave_number,
            radius=25,
            base_speed=ENEMY_BASE_SPEED * 0.7,
            base_hp=ENEMY_BASE_HP * 4,
            wave_multiplier=WAVE_MULTIPLIER,
            color=PURPLE,
            damage=ENEMY_DAMAGE * 2,
            attack_cooldown=ATTACK_COOLDOWN * 1.5
        )
        enemies_list.append(boss)
        
        # Some minions (fewer than a regular wave)
        n_minions = 3 + wave_number // 2
        
        for _ in range(n_minions):
            x = random.randint(50, WIDTH - 50)  # Keep enemies away from edges
            y = random.randint(50, HEIGHT - 50)
            
            # 50/50 chance of melee or ranged minion
            if random.random() < 0.5:
                e = MeleeEnemy(
                    x, y, wave_number,
                    radius=15,
                    base_speed=ENEMY_BASE_SPEED,
                    base_hp=ENEMY_BASE_HP,
                    wave_multiplier=WAVE_MULTIPLIER,
                    color=RED,
                    damage=ENEMY_DAMAGE,
                    attack_cooldown=ATTACK_COOLDOWN
                )
            else:
                e = RangedEnemy(
                    x, y, wave_number,
                    radius=15,
                    base_speed=ENEMY_BASE_SPEED * 0.8,
                    base_hp=ENEMY_BASE_HP * 0.8,
                    wave_multiplier=WAVE_MULTIPLIER,
                    color=BLUE,
                    damage=ENEMY_DAMAGE * 0.7,
                    attack_cooldown=ATTACK_COOLDOWN * 2,
                    projectile_speed=300,
                    attack_range=250
                )
            enemies_list.append(e)
    
    def get_difficulty_multiplier(self, wave_number):
        """Calculate difficulty multiplier based on wave number"""
        return 1.0 + (wave_number - 1) * WAVE_MULTIPLIER
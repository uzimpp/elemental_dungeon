# main.py
import pygame
import sys
import time
import csv
import random
from deck import Deck
from player import Player
from enemy import Enemy
from visual_effects import VisualEffect
from utils import resolve_overlap, draw_hp_bar, angle_diff
from game_state import *
from audio import Audio
from config import Config as C


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((C.WIDTH, C.HEIGHT))
        pygame.display.set_caption(C.GAME_NAME)
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Initialize audio system
        self.audio = Audio()
        self.audio.load_music()
        
        # Visual effects list
        self.effects = []
        
        # Game state tracking
        self.wave_number = 1
        self.skills_filename = C.SKILLS_FILENAME
        self.player_name = "Unknown"  # Default name
        
        # Sprite groups for collision detection
        self.enemy_group = pygame.sprite.Group()

        # Initialize state machine
        self.current_state = None
        self.states = {
            "MENU": MenuState(self),
            "NAME_ENTRY": PlayerNameState(self),
            "DECK_SELECTION": DeckSelectionState(self),
            "PLAYING": PlayingState(self),
            "PAUSED": PausedState(self),
            "GAME_OVER": GameOverState(self)
        }
        
        # Start with menu state and play menu music
        self.change_state("MENU")

    def initialize_player(self):
        """Initialize just the player without deck (first phase)"""
        # Player name is now set by the PlayerNameState

        # Create player first with no deck
        self.player = Player(
            self.player_name,
            C.WIDTH,
            C.HEIGHT,
            None,  # No deck yet
            C.PLAYER_RADIUS,
            C.PLAYER_MAX_HEALTH,
            C.PLAYER_SUMMON_LIMIT,
            C.PLAYER_COLOR,
            C.PLAYER_WALK_SPEED,
            C.PLAYER_SPRINT_SPEED,
            C.PLAYER_MAX_STAMINA,
            C.PLAYER_STAMINA_REGEN,
            C.PLAYER_SPRINT_DRAIN,
            C.PLAYER_DASH_COST,
            C.PLAYER_DASH_DISTANCE,
            C.PLAYER_STAMINA_COOLDOWN)

        # Set game reference
        self.player.game = self

        # Create deck without skills yet
        self.deck = Deck(self.player)
        
        # Set empty deck on player
        self.player.deck = self.deck
        
        # Set summon limit
        self.deck.summon_limit = C.PLAYER_SUMMON_LIMIT
        
        # Game tracking
        self.game_start_time = time.time()
        self.effects = []
    
    def finish_initialization(self):
        """Complete game initialization after deck is built (second phase)"""
        # Switch to game music when starting gameplay
        
        # Spawn first wave of enemies
        self.wave_number = 1
        self.spawn_wave()

    def change_state(self, new_state):
        """Change the current game state"""
        old_state = None
        if self.current_state:
            old_state = self.current_state.__class__.__name__
            self.current_state.exit()
            
        if new_state == "QUIT":
            self.audio.fade_out(500)
            self.running = False
            return
            
        self.current_state = self.states[new_state]
        
        # Handle music transitions based on state changes
        if old_state != self.current_state.__class__.__name__:
            # From any state to menu
            if new_state == "MENU":
                self.audio.fade_out(800)
                self.audio.fade_in("MENU", 1000)
            # From menu/pause to playing
            elif new_state == "PLAYING" and (old_state in ["MenuState", "PausedState"] or old_state is None):
                self.audio.fade_out(800)
                self.audio.fade_in("PLAYING", 1000)
        
        self.current_state.enter()

    def log_csv(self, wave):
        now_str = time.strftime("%Y-%m-%d %H:%M:%S")
        g_time = time.time() - self.game_start_time

        # Convert deck to string representation
        deck_str = "|".join([skill.name for skill in self.player.deck.skills])

        with open(C.LOG_FILENAME, "a", newline="") as f:
            w = csv.writer(f)
            # Write header if file is empty
            if f.tell() == 0:
                w.writerow([
                    "timestamp", "player_name", "wave_survived",
                    "game_duration", "final_hp", "deck_composition",
                    "skill1", "skill2", "skill3", "skill4"
                ])

            # Write data row
            w.writerow([
                now_str,                    # timestamp
                self.player_name,          # player_name
                wave,                      # wave_survived
                f"{g_time:.2f}",          # game_duration
                self.player.health,        # final_hp
                deck_str,                  # deck_composition
                self.player.deck.skills[0].name,  # skill1
                self.player.deck.skills[1].name,  # skill2
                self.player.deck.skills[2].name,  # skill3
                self.player.deck.skills[3].name,  # skill4
            ])

    def spawn_wave(self):
        # Clear enemy group and list
        self.enemy_group.empty()
        
        # spawn enemies based on wave number
        n_enemies = 5 + self.wave_number
        for _ in range(n_enemies):
            x = random.randint(20, C.WIDTH - 20)
            y = random.randint(20, C.HEIGHT - 20)
            e = Enemy(
                x,
                y,
                self.wave_number,
                C.ENEMY_RADIUS,
                C.ENEMY_BASE_SPEED,
                C.ENEMY_BASE_HP,
                C.WAVE_MULTIPLIER,
                C.RED,
                C.ENEMY_DAMAGE,
                C.ATTACK_COOLDOWN,
                C.ATTACK_RADIUS)
            
            # Add to sprite group
            self.enemy_group.add(e)
    
    @property
    def enemies(self):
        """Property to maintain backward compatibility"""
        return list(self.enemy_group.sprites())

    def run(self):
        while self.running:
            # Convert milliseconds to seconds for dt
            dt = self.clock.tick(C.FPS) / 1000.0
            
            # Get all events
            events = pygame.event.get()
            
            # Handle current state events
            next_state = self.current_state.handle_events(events)
            if next_state:
                self.change_state(next_state)
                continue  # Skip this frame to properly initialize new state

            # Update current state
            next_state = self.current_state.update(dt)
            if next_state:
                self.change_state(next_state)
                continue

            # Render current state
            self.current_state.render(self.screen)
            pygame.display.flip()

        pygame.quit()
        sys.exit()

    # These methods are used by the state classes
    def resolve_overlap(self, entity1, entity2):
        """Wrapper to call the utility function"""
        resolve_overlap(entity1, entity2)
        
    def check_collisions(self):
        """Use sprite collide for efficient collision detection"""
        # Check collisions between player projectiles and enemies
        for projectile in self.player.deck.projectiles:
            # Check for collision with enemies
            collided_enemies = pygame.sprite.spritecollide(
                projectile, 
                self.enemy_group, 
                False, 
                pygame.sprite.collide_circle
            )
            
            if collided_enemies:
                # Handle collision - projectile hits first enemy
                enemy = collided_enemies[0]
                enemy.take_damage(projectile.damage)
                projectile.explode(self.enemies)
                break  # Stop checking after first collision
        
        # Check collisions between player summons and enemies
        for summon in self.player.deck.summons:
            # Use distance-based collision for summon attacks
            # This is handled in the summon's update method
            pass
        
        # Check collisions between player and enemies
        collided_enemies = pygame.sprite.spritecollide(
            self.player, 
            self.enemy_group, 
            False, 
            pygame.sprite.collide_circle
        )
        
        for enemy in collided_enemies:
            # Push enemies away from player
            self.resolve_overlap(self.player, enemy)
        
    def draw_wave_info(self):
        ui_font = pygame.font.SysFont("Arial", 24)
        wave_text = ui_font.render(f"WAVE: {self.wave_number}", True, C.BLACK)
        self.screen.blit(wave_text, (10, 10))

    def draw_player_bars(self):
        ui_font = pygame.font.SysFont("Arial", 24)
        # HP Bar
        player_bar_x = 10
        player_bar_y = 50
        bar_width = 200
        bar_height = 20
        pygame.draw.rect(self.screen, C.UI_COLORS['hp_bar_bg'],
                         (player_bar_x, player_bar_y, bar_width, bar_height))
        hp_frac = self.player.health / self.player.max_health
        fill_width = int(bar_width * max(hp_frac, 0))
        pygame.draw.rect(self.screen, C.UI_COLORS['hp_bar_fill'],
                         (player_bar_x, player_bar_y, fill_width, bar_height))
        hp_text_str = f"{int(self.player.health)}/{self.player.max_health}"
        hp_text = ui_font.render(hp_text_str, True, C.UI_COLORS['hp_text'])
        self.screen.blit(
            hp_text, (player_bar_x + bar_width + 10, player_bar_y - 2))

        # Stamina Bar
        pygame.draw.rect(
            self.screen, C.UI_COLORS['stamina_bar_bg'], (10, 80, 200, 20))
        st_frac = self.player.stamina / self.player.max_stamina
        st_fill = int(200 * max(st_frac, 0))
        pygame.draw.rect(
            self.screen, C.UI_COLORS['stamina_bar_fill'], (10, 80, st_fill, 20))
        st_text_str = f"{int(self.player.stamina)}/{self.player.max_stamina}"
        st_text = ui_font.render(st_text_str, True, C.UI_COLORS['stamina_text'])
        self.screen.blit(st_text, (220, 78))

    def draw_skill_ui(self):
        skill_font = pygame.font.SysFont("Arial", 16)
        now = time.time()
        skill_start_y = C.HEIGHT - 100
        for i, skill in enumerate(self.player.deck.skills):
            box_x = 10 + i * 110
            box_y = skill_start_y
            box_width = 100
            box_height = 80
            pygame.draw.rect(self.screen, C.UI_COLORS['skill_box_bg'],
                             (box_x, box_y, box_width, box_height))
            name_text = skill_font.render(skill.name, True, C.WHITE)
            name_rect = name_text.get_rect(
                centerx=box_x + box_width // 2, top=box_y + 5)
            self.screen.blit(name_text, name_rect)
            self.draw_skill_cooldown(
                skill, box_x, box_y, box_width, box_height, now, skill_font)
            key_text = skill_font.render(f"[{i + 1}]", True, C.WHITE)
            key_rect = key_text.get_rect(
                bottom=box_y + box_height - 5, centerx=box_x + box_width // 2)
            self.screen.blit(key_text, key_rect)
            pygame.draw.rect(self.screen, skill.color,
                             (box_x, box_y, 5, box_height))

    def draw_skill_cooldown(self, skill, box_x, box_y, box_width, box_height, now, skill_font):
        if not skill.is_off_cooldown(now):
            cd_remaining = skill.cooldown - (now - skill.last_use_time)
            cd_height = int((cd_remaining / skill.cooldown) * box_height)
            pygame.draw.rect(self.screen, C.UI_COLORS['cooldown_overlay'],
                             (box_x, box_y + box_height - cd_height, box_width, cd_height))
            cd_text = skill_font.render(f"{cd_remaining:.1f}s", True, C.WHITE)
            cd_rect = cd_text.get_rect(
                center=(box_x + box_width // 2, box_y + box_height // 2))
            self.screen.blit(cd_text, cd_rect)


def main():
    game = Game()
    game.run()


if __name__ == "__main__":
    main()

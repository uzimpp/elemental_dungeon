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
from config import *


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Elemental Tower Defense")
        self.clock = pygame.time.Clock()
        self.running = True
        self.effects = []

        self.player_name = input("Enter player name: ") or "Unknown"

        # Create player first with no deck
        self.player = Player(
            self.player_name,
            WIDTH // 2,
            HEIGHT // 2,
            None,  # No deck yet
            PLAYER_RADIUS,
            PLAYER_MAX_HEALTH,
            PLAYER_SUMMON_LIMIT,
            PLAYER_COLOR,
            PLAYER_WALK_SPEED,
            PLAYER_SPRINT_SPEED,
            PLAYER_MAX_STAMINA,
            PLAYER_STAMINA_REGEN,
            PLAYER_SPRINT_DRAIN,
            PLAYER_DASH_COST,
            PLAYER_DASH_DISTANCE,
            PLAYER_STAMINA_COOLDOWN)
        
        # Set game reference
        self.player.game = self

        # Create and initialize deck
        deck = Deck(self.player)  # Create deck with player reference
        all_skills = deck.load_from_csv(SKILLS_FILENAME)
        chosen_skills = self.build_deck_interactively(all_skills)
        deck.skills = chosen_skills  # Set chosen skills
        deck.summon_limit = PLAYER_SUMMON_LIMIT
        
        # Set deck on player
        self.player.deck = deck

        self.wave_number = 1
        self.enemies = []
        self.spawn_wave()

        self.game_start_time = time.time()
        self.effects = []

    def log_csv(self, wave):
        now_str = time.strftime("%Y-%m-%d %H:%M:%S")
        g_time = time.time() - self.game_start_time

        # Convert deck to string representation
        deck_str = "|".join([skill.name for skill in self.player.deck.skills])

        with open(LOG_FILENAME, "a", newline="") as f:
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
        self.enemies.clear()
        # spawn 5 enemies each wave
        n_enemies = 5 + self.wave_number
        for _ in range(n_enemies):
            x = random.randint(20, WIDTH - 20)
            y = random.randint(20, HEIGHT - 20)
            e = Enemy(
                x,
                y,
                self.wave_number,
                15,
                ENEMY_BASE_SPEED,
                ENEMY_BASE_HP,
                WAVE_MULTIPLIER,
                RED,
                ENEMY_DAMAGE,
                ATTACK_COOLDOWN)
            self.enemies.append(e)

   

    def build_deck_interactively(self, skill_list):
        print("=== BUILD YOUR DECK (Pick 4) ===")
        for i, sk in enumerate(skill_list):
            print(f"{i + 1}. [{sk.element}] {sk.name} - {sk.description}")

        chosen = []
        picks_needed = 4
        while len(chosen) < picks_needed:
            c = input(f"Pick skill #{len(chosen) + 1} (1-{len(skill_list)}): ")
            if not c.isdigit():
                print("Invalid input. Enter a number.")
                continue
            idx = int(c) - 1
            if idx < 0 or idx >= len(skill_list):
                print("Out of range. Try again.")
                continue
            chosen_skill = skill_list[idx]
            chosen.append(chosen_skill)
            print(f"Added {chosen_skill.name}.")

        print("=== Final Deck ===")
        for s in chosen:
            print(f"- {s.name}")
        return chosen

    def run(self):
        while self.running:
            # Convert milliseconds to seconds for dt
            dt = self.clock.tick(FPS) / 1000.0
            self.handle_events()
            self.update(dt)
            self.draw()

            if self.player.health <= 0:
                print("Player died!")
                self.log_csv(self.wave_number)
                self.running = False

        pygame.quit()
        sys.exit()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            else:
                mouse_pos = pygame.mouse.get_pos()
                now = time.time()
                result = self.player.handle_event(
                    event, mouse_pos, self.enemies, now, self.effects)
                if result == 'exit':
                    self.log_csv(self.wave_number)
                    self.running = False

    def update(self, dt):
        # 1. Update enemy positions and attacks
        for e in self.enemies:
            e.update(self.player, dt)

        # 2. Handle player input (movement)
        self.player.handle_input(dt)

        # 3. Update deck
        print(f"[Game] Updating deck with {len(self.enemies)} enemies. First enemy at: {self.enemies[0].x:.1f}, {self.enemies[0].y:.1f} if available")
        self.player.deck.update(dt, self.enemies)
    
        # 4. Resolve collisions
        entities = [entity for entity in ([self.player] + 
                                          self.player.summons + 
                                          self.enemies) if entity.alive]
        for i in range(len(entities)):
            for j in range(i + 1, len(entities)):
                resolve_overlap(entities[i], entities[j])

        # 5. Clean up dead entities
        self.enemies = [e for e in self.enemies if e.alive]

        # 6. Wave logic
        if len(self.enemies) == 0:
            self.wave_number += 1
            self.spawn_wave()

        # 7. Update visual effects
        for eff in self.effects:
            eff.update(dt)
        self.effects = [ef for ef in self.effects if ef.active]

    def draw(self):
        self.screen.fill(WHITE)
        self.draw_wave_info()
        self.draw_player_bars()
        self.draw_skill_ui()
        self.draw_game_elements()
        pygame.display.flip()

    def draw_wave_info(self):
        ui_font = pygame.font.SysFont("Arial", 24)
        wave_text = ui_font.render(f"WAVE: {self.wave_number}", True, BLACK)
        self.screen.blit(wave_text, (10, 10))

    def draw_player_bars(self):
        ui_font = pygame.font.SysFont("Arial", 24)
        # HP Bar
        player_bar_x = 10
        player_bar_y = 50
        bar_width = 200
        bar_height = 20
        pygame.draw.rect(self.screen, UI_COLORS['hp_bar_bg'],
                         (player_bar_x, player_bar_y, bar_width, bar_height))
        hp_frac = self.player.health / self.player.max_health
        fill_width = int(bar_width * max(hp_frac, 0))
        pygame.draw.rect(self.screen, UI_COLORS['hp_bar_fill'],
                         (player_bar_x, player_bar_y, fill_width, bar_height))
        hp_text_str = f"{int(self.player.health)}/{self.player.max_health}"
        hp_text = ui_font.render(hp_text_str, True, UI_COLORS['hp_text'])
        self.screen.blit(hp_text, (player_bar_x + bar_width + 10, player_bar_y - 2))

        # Stamina Bar
        pygame.draw.rect(self.screen, UI_COLORS['stamina_bar_bg'], (10, 80, 200, 20))
        st_frac = self.player.stamina / self.player.max_stamina
        st_fill = int(200 * max(st_frac, 0))
        pygame.draw.rect(self.screen, UI_COLORS['stamina_bar_fill'], (10, 80, st_fill, 20))
        st_text_str = f"{int(self.player.stamina)}/{self.player.max_stamina}"
        st_text = ui_font.render(st_text_str, True, UI_COLORS['stamina_text'])
        self.screen.blit(st_text, (220, 78))

    def draw_skill_ui(self):
        skill_font = pygame.font.SysFont("Arial", 16)
        now = time.time()
        skill_start_y = HEIGHT - 100
        for i, skill in enumerate(self.player.deck.skills):
            box_x = 10 + i * 110
            box_y = skill_start_y
            box_width = 100
            box_height = 80
            pygame.draw.rect(self.screen, UI_COLORS['skill_box_bg'],
                             (box_x, box_y, box_width, box_height))
            name_text = skill_font.render(skill.name, True, WHITE)
            name_rect = name_text.get_rect(centerx=box_x + box_width // 2, top=box_y + 5)
            self.screen.blit(name_text, name_rect)
            self.draw_skill_cooldown(skill, box_x, box_y, box_width, box_height, now, skill_font)
            key_text = skill_font.render(f"[{i + 1}]", True, WHITE)
            key_rect = key_text.get_rect(bottom=box_y + box_height - 5, centerx=box_x + box_width // 2)
            self.screen.blit(key_text, key_rect)
            pygame.draw.rect(self.screen, skill.color, (box_x, box_y, 5, box_height))

    def draw_skill_cooldown(self, skill, box_x, box_y, box_width, box_height, now, skill_font):
        if not skill.is_off_cooldown(now):
            cd_remaining = skill.cooldown - (now - skill.last_use_time)
            cd_height = int((cd_remaining / skill.cooldown) * box_height)
            pygame.draw.rect(self.screen, UI_COLORS['cooldown_overlay'],
                             (box_x, box_y + box_height - cd_height, box_width, cd_height))
            cd_text = skill_font.render(f"{cd_remaining:.1f}s", True, WHITE)
            cd_rect = cd_text.get_rect(center=(box_x + box_width // 2, box_y + box_height // 2))
            self.screen.blit(cd_text, cd_rect)

    def draw_game_elements(self):
        # Draw all game objects in proper layers
        
        # 1. Draw entities (enemies, player)
        for enemy in self.enemies:
            enemy.draw(self.screen)
        
        # 2. Draw player
        self.player.draw(self.screen)
        
        # 3. Draw projectiles and summons via deck
        self.player.deck.draw(self.screen)
        
        # 4. Draw overhead effects (top layer)
        for effect in self.effects:
            effect.draw(self.screen)


def main():
    pygame.init()
    game = Game()
    game.run()


if __name__ == "__main__":
    main()

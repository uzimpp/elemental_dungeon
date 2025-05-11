import pygame
import time
from config import UI_COLORS, WHITE, BLACK

class UI:
    def __init__(self, screen, player):

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
        self.screen.blit(
            hp_text, (player_bar_x + bar_width + 10, player_bar_y - 2))

        # Stamina Bar
        pygame.draw.rect(
            self.screen, UI_COLORS['stamina_bar_bg'], (10, 80, 200, 20))
        st_frac = self.player.stamina / self.player.max_stamina
        st_fill = int(200 * max(st_frac, 0))
        pygame.draw.rect(
            self.screen, UI_COLORS['stamina_bar_fill'], (10, 80, st_fill, 20))
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
            name_rect = name_text.get_rect(
                centerx=box_x + box_width // 2, top=box_y + 5)
            self.screen.blit(name_text, name_rect)
            self.draw_skill_cooldown(
                skill, box_x, box_y, box_width, box_height, now, skill_font)
            key_text = skill_font.render(f"[{i + 1}]", True, WHITE)
            key_rect = key_text.get_rect(
                bottom=box_y + box_height - 5, centerx=box_x + box_width // 2)
            self.screen.blit(key_text, key_rect)
            pygame.draw.rect(self.screen, skill.color,
                             (box_x, box_y, 5, box_height))

    def draw_skill_cooldown(self, skill, box_x, box_y, box_width, box_height, now, skill_font):
        if not skill.is_off_cooldown(now):
            cd_remaining = skill.cooldown - (now - skill.last_use_time)
            cd_height = int((cd_remaining / skill.cooldown) * box_height)
            pygame.draw.rect(self.screen, UI_COLORS['cooldown_overlay'],
                             (box_x, box_y + box_height - cd_height, box_width, cd_height))
            cd_text = skill_font.render(f"{cd_remaining:.1f}s", True, WHITE)
            cd_rect = cd_text.get_rect(
                center=(box_x + box_width // 2, box_y + box_height // 2))
            self.screen.blit(cd_text, cd_rect)

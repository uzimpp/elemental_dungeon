"""
User interface module for Incantato.
Handles rendering of UI elements like health bars, skill icons, and wave information.
"""
import time
import pygame
from config import Config


class UI:
    """
    Utility class for rendering user interface elements.
    Contains static methods for drawing various UI components.
    """
    @staticmethod
    def draw_wave_info(screen, wave_number):
        """
        Draw the current wave number on the screen.
        
        Args:
            screen (pygame.Surface): The surface to draw on
            wave_number (int): Current wave number
        """
        ui_font = pygame.font.SysFont("Arial", 24)
        wave_text = ui_font.render(f"WAVE: {wave_number}", True, Config.BLACK)
        screen.blit(wave_text, (10, 10))

    @staticmethod
    def draw_player_bars(screen, player):
        """
        Draw player's health and stamina bars on the screen.
        
        Args:
            screen (pygame.Surface): The surface to draw on
            player (Player): The player object with health and stamina attributes
        """
        ui_font = pygame.font.SysFont("Arial", 24)
        # HP Bar
        player_bar_x = 10
        player_bar_y = 50
        bar_width = 200
        bar_height = 20
        pygame.draw.rect(screen, Config.UI_COLORS['hp_bar_bg'],
                         (player_bar_x, player_bar_y, bar_width, bar_height))
        hp_frac = player.health / player.max_health
        fill_width = int(bar_width * max(hp_frac, 0))
        pygame.draw.rect(screen, Config.UI_COLORS['hp_bar_fill'],
                         (player_bar_x, player_bar_y, fill_width, bar_height))
        hp_text_str = f"{int(player.health)}/{player.max_health}"
        hp_text = ui_font.render(hp_text_str, True, Config.UI_COLORS['hp_text'])
        screen.blit(
            hp_text, (player_bar_x + bar_width + 10, player_bar_y - 2))

        # Stamina Bar
        pygame.draw.rect(
            screen, Config.UI_COLORS['stamina_bar_bg'], (10, 80, 200, 20))
        st_frac = player.energy.get_stamina_percentage()
        st_fill = int(200 * max(st_frac, 0))
        pygame.draw.rect(
            screen, Config.UI_COLORS['stamina_bar_fill'], (10, 80, st_fill, 20))
        st_text_str = f"{int(player.energy.stamina)}/{player.energy.max_stamina}"
        st_text = ui_font.render(st_text_str, True, Config.UI_COLORS['stamina_text'])
        screen.blit(st_text, (220, 78))

    @staticmethod
    def draw_skill_ui(screen, player, height):
        """
        Draw skill icons and cooldown indicators.
        
        Args:
            screen (pygame.Surface): The surface to draw on
            player (Player): The player object with skill deck
            height (int): Screen height for positioning
        """
        skill_font = pygame.font.SysFont("Arial", 16)
        now = time.time()
        skill_start_y = height - 100
        for i, skill in enumerate(player.deck.skills):
            box_x = 10 + i * 110
            box_y = skill_start_y
            box_width = 100
            box_height = 80
            pygame.draw.rect(screen, Config.UI_COLORS['skill_box_bg'],
                             (box_x, box_y, box_width, box_height))
            name_text = skill_font.render(skill.name, True, Config.WHITE)
            name_rect = name_text.get_rect(
                centerx=box_x + box_width // 2, top=box_y + 5)
            screen.blit(name_text, name_rect)
            UI.draw_skill_cooldown(
                screen, skill, box_x, box_y, box_width, box_height, now, skill_font)
            key_text = skill_font.render(f"[{i + 1}]", True, Config.WHITE)
            key_rect = key_text.get_rect(
                bottom=box_y + box_height - 5, centerx=box_x + box_width // 2)
            screen.blit(key_text, key_rect)
            pygame.draw.rect(screen, skill.color,
                             (box_x, box_y, 5, box_height))

    @staticmethod
    def draw_skill_cooldown(screen, skill, box_x, box_y, box_width, box_height, now, skill_font):
        """
        Draw cooldown overlay for a skill.
        
        Args:
            screen (pygame.Surface): The surface to draw on
            skill (BaseSkill): The skill to check cooldown for
            box_x (int): X position of the skill box
            box_y (int): Y position of the skill box
            box_width (int): Width of the skill box
            box_height (int): Height of the skill box
            now (float): Current time for cooldown calculation
            skill_font (pygame.font.Font): Font for cooldown text
        """
        if not skill.is_off_cooldown(now):
            cd_remaining = skill.cooldown - (now - skill.last_use_time)
            cd_height = int((cd_remaining / skill.cooldown) * box_height)
            pygame.draw.rect(screen, Config.UI_COLORS['cooldown_overlay'],
                             (box_x, box_y + box_height - cd_height, box_width, cd_height))
            cd_text = skill_font.render(f"{cd_remaining:.1f}s", True, Config.WHITE)
            cd_rect = cd_text.get_rect(
                center=(box_x + box_width // 2, box_y + box_height // 2))
            screen.blit(cd_text, cd_rect)

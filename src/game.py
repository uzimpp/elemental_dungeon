# main.py
import pygame
import sys
import time
import random
from deck import Deck
from player import Player
from enemy import Enemy
from visual_effects import VisualEffect
from utils import resolve_overlap, draw_hp_bar, angle_diff
from game_state import MenuState, PlayerNameState, DeckSelectionState, PlayingState, PausedState, GameOverState
from config import *


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(GAME_NAME)
        self.effects = []
        self.wave_number = 1
        self.enemies = []
        
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
        
        # Start with menu state
        self.change_state("MENU")

    def initialize_player(self):
        """Initialize just the player without deck (first phase)"""
        self.player = Player(
            self.player_name,
            WIDTH,
            HEIGHT,
            None,  # No deck yet
            PLAYER_RADIUS,
            PLAYER_MAX_HEALTH,
            PLAYER_SUMMON_LIMIT,
            PLAYER_WALK_SPEED,
            PLAYER_SPRINT_SPEED,
            PLAYER_MAX_STAMINA,
            PLAYER_STAMINA_REGEN,
            PLAYER_SPRINT_DRAIN,
            PLAYER_DASH_COST,
            PLAYER_DASH_DISTANCE,
            PLAYER_STAMINA_COOLDOWN)

        # Set deck on player
        self.player.deck = Deck(self.player)
        # Set summon limit
        self.player.deck.summon_limit = PLAYER_SUMMON_LIMIT
        # Set game reference
        self.player.game = self
        # Game tracking
        self.game_start_time = time.time()
        self.effects = []

    def finish_initialization(self):
        """Complete game initialization after deck is built (second phase)"""
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
            return

        self.current_state = self.states[new_state]
        self.current_state.enter()

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
                ENEMY_RADIUS,
                ENEMY_BASE_SPEED,
                ENEMY_BASE_HP,
                WAVE_MULTIPLIER,
                RED,
                ENEMY_DAMAGE,
                ATTACK_COOLDOWN,
                ATTACK_RADIUS)
            self.enemies.append(e)

    def run(self):
        while self.running:
            # Convert milliseconds to seconds for dt
            now = pygame.time.get_ticks()
            dt = (now - self.last_time) / 1000.0
            self.last_time = now

            events = pygame.event.get()
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


def main():
    pygame.init()
    game = Game()
    game.run()


if __name__ == "__main__":
    main()

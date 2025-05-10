# main.py
import pygame
import sys
import time
import random
from deck import Deck
from player import Player
from enemy import Enemy
from game_state import MenuState, PlayerNameState, DeckSelectionState, PlayingState, PausedState, GameOverState
from config import *
from resources import Resources


class Game:
    def __init__(self):

        pygame.init()

        # Initialize Resources first
        self.resources = Resources.get_instance()
        print(f"Game base path: {self.resources.base_path}")
        print(f"Game assets path: {self.resources.asset_path}")
        print(f"Game data path: {self.resources.data_path}")
        
        # Initialize display
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(GAME_NAME)
        
        # Initialize game variables
        self.effects = []
        self.wave_number = 1
        self.enemies = []
        self.player = None
        self.deck = None
        self.current_state = None
        self.states = {}
        self.running = True
        self.last_time = pygame.time.get_ticks()
        
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
        
        # Preload common resources
        self._preload_resources()
        
        # Start with menu state
        self.change_state("MENU")
        
    def _preload_resources(self):
        """Preload commonly used resources"""
        # Preload sprite sheets
        self.resources.load_image("player", PLAYER_SPRITE_PATH)
        self.resources.load_image("enemy", ENEMY_SPRITE_PATH)
        self.resources.load_image("shadow_summon", SHADOW_SUMMON_SPRITE_PATH)
        
        # Preload skill data
        self.resources.load_csv("skills", SKILLS_PATH)
        
        # Preload sound effects if needed
        if pygame.mixer.get_init():
            # Load menu music
            if MENU_BGM_PATH:
                self.resources.load_sound("menu_bgm", MENU_BGM_PATH)
            # Load game music
            if GAME_BGM_PATH:
                self.resources.load_sound("game_bgm", GAME_BGM_PATH)

    def initialize(self):
        """Initialize the game"""
        # Create player
        self.player = Player(WIDTH // 2, HEIGHT // 2)
        
        # Create deck
        self.deck = Deck(self.player)
        self.deck.load_from_csv(SKILLS_PATH)
        
        # Initialize states
        self.states = {
            'menu': MenuState(self),
            'playing': PlayingState(self),
            'paused': PausedState(self),
            'game_over': GameOverState(self)
        }
        self.current_state = self.states['menu']

    def update(self, dt):
        """Update game state"""
        if self.current_state:
            self.current_state.update(dt)

    def draw(self, surface):
        """Draw game state"""
        if self.current_state:
            self.current_state.draw(surface)

    def change_state(self, state_name):
        """Change the current game state"""
        if state_name in self.states:
            if self.current_state:
                # Exit current state
                self.current_state.exit()
            self.current_state = self.states[state_name]
            self.current_state.enter()
            print(f"Changed game state to: {state_name}")

    def handle_event(self, event):
        """Handle game events"""
        if self.current_state:
            self.current_state.handle_event(event)

    def initialize_player(self):
        """Initialize just the player without deck (first phase)"""
        self.player = Player(
            self.player_name,
            WIDTH,
            HEIGHT,
            None,  # No deck yet
            PLAYER_RADIUS,
            PLAYER_MAX_HEALTH,
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
        # Set game reference
        self.player.game = self
        # Load deck from CSV
        self.player.deck.load_from_csv(SKILLS_PATH)
        # Set summon limit
        if hasattr(self.player.deck, 'summon_limit'):
            self.player.deck.summon_limit = PLAYER_SUMMON_LIMIT
        # Game tracking
        self.game_start_time = time.time()
        self.effects = []

    def finish_initialization(self):
        """Complete game initialization after deck is built (second phase)"""
        # Spawn first wave of enemies
        self.wave_number = 1
        self.spawn_wave()

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
            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False
                    break
                self.handle_event(event)
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


def main():
    game = Game()  # pygame.init() is called in Game.__init__
    game.run()


if __name__ == "__main__":
    main()

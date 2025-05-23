"""
Main entry point for Incantato game.

Handles game initialization, state management, event loop,
collision detection, and wave spawning.
"""
import random
import sys
import time

import pygame

from audio import Audio
from config import Config as C
from data_collector import DataCollector
from enemy import Enemy
from font import Font
from game_state import (DeckSelectionState, GameStateManager, MenuState,
                        NameEntryState, PlayingState, StatsDisplayState)
from player import Player
from utils import resolve_overlap


class Game:
    def __init__(self):
        """Initialize game state and assets."""
        pygame.init()
        Font().initialize(C.FONT_PATH, C.FONT_SIZES)
        self.screen = pygame.display.set_mode((C.WIDTH, C.HEIGHT))
        pygame.display.set_caption(C.GAME_NAME)
        self.clock = pygame.time.Clock()
        self.running = True
        self.audio = Audio()
        self.audio.load_music()

        # Game state tracking
        self.wave_number = 1
        self.player_name = None
        self.last_player_name = None

        # Sprite groups for collision detection
        self.enemy_group = pygame.sprite.Group()

        # Initialize player attribute to avoid AttributeError before initialization
        self.player = None
        self.game_start_time = None

        # Data collection attributes for per-wave logging
        self.wave_start_time = None
        self.current_wave_skill_usage = {}
        self.current_wave_spawned_enemies = 0

        # Initialize state manager and states
        self.state_manager = GameStateManager(self)
        self.state_manager.add_state("MENU", MenuState(self))
        self.state_manager.add_state("NAME_ENTRY", NameEntryState(self))
        self.state_manager.add_state(
            "DECK_SELECTION", DeckSelectionState(self))
        self.state_manager.add_state("PLAYING", PlayingState(self))
        self.state_manager.add_state("STATS_DISPLAY", StatsDisplayState(self))

        # Start with menu state and play menu music
        self.state_manager.set_state("MENU")
        # Initial music play moved to MenuState.enter()

        # Initialize DataCollector CSVs
        DataCollector.initialize_csvs()

    def initialize_player(self):
        """Initialize the player with an empty deck."""
        self.player = Player(self.player_name, game_instance=self)
        self.game_start_time = time.time()

    def reset_game(self):
        """Reset game state for retry."""
        # Reset wave number
        self.wave_number = 1
        # IMPORTANT: Get a new Play_ID for this new game session
        DataCollector.current_play_id = DataCollector._get_next_play_id()
        # Clear enemy group
        self.enemy_group.empty()

        # Clear any overlays
        self.state_manager.clear_overlay()

        # Reset player health and position if exists
        if hasattr(self, 'player') and self.player:
            self.player.health = self.player.max_health
            self.player.stamina = self.player.max_stamina
            self.player.pos.x = C.WIDTH // 2
            self.player.pos.y = C.HEIGHT // 2

            # Reset player skills cooldowns if they exist
            if hasattr(self.player, 'deck') and self.player.deck:
                for skill in self.player.deck.skills:
                    skill.last_use_time = 0

                # Clear any active projectiles/summons
                if hasattr(self.player.deck, 'projectiles'):
                    if hasattr(self.player.deck.projectiles, 'empty'):
                        self.player.deck.projectiles.empty()
                    elif hasattr(self.player.deck.projectiles, 'clear'):
                        self.player.deck.projectiles.clear()

                if hasattr(self.player.deck, 'summons'):
                    if hasattr(self.player.deck.summons, 'empty'):
                        self.player.deck.summons.empty()
                    elif hasattr(self.player.deck.summons, 'clear'):
                        self.player.deck.summons.clear()

            # Reset player state
            self.player.state = 'idle'
            if self.player.animation:
                self.player.animation.set_state('idle', force_reset=True)

    def prepare_game(self):
        """Setup game for playing after deck is created."""
        self.reset_game()
        self.spawn_wave()
        self.audio.fade_out(800)
        self.audio.fade_in("PLAYING", 1000)

    def spawn_wave(self):
        """Spawn a new wave of enemies after clearing the previous wave."""
        # Clear enemy group
        self.enemy_group.empty()

        # Reset per-wave data trackers
        self.wave_start_time = time.time()
        self.current_wave_skill_usage = {}
        # Note: current_wave_spawned_enemies will be set below

        # Clear player projectiles and summons to avoid overlapping entities
        if hasattr(self, 'player') and self.player and hasattr(self.player, 'deck'):
            # Use empty() for sprite groups instead of clear()
            if hasattr(self.player.deck, 'projectiles'):
                if hasattr(self.player.deck.projectiles, 'empty'):
                    self.player.deck.projectiles.empty()
                elif hasattr(self.player.deck.projectiles, 'clear'):
                    self.player.deck.projectiles.clear()

            if hasattr(self.player.deck, 'summons'):
                if hasattr(self.player.deck.summons, 'empty'):
                    self.player.deck.summons.empty()
                elif hasattr(self.player.deck.summons, 'clear'):
                    self.player.deck.summons.clear()

        # spawn enemies based on wave number
        n_enemies = 5 + self.wave_number
        # Track spawned enemies for logging
        self.current_wave_spawned_enemies = n_enemies
        for _ in range(n_enemies):
            # Ensure enemies don't spawn too close to the player
            spawn_too_close = True
            x, y = 0, 0
            player_pos = (C.WIDTH // 2, C.HEIGHT // 2)

            if hasattr(self, 'player') and self.player:
                player_pos = (self.player.pos.x, self.player.pos.y)

            while spawn_too_close:
                x = random.randint(20, C.WIDTH - 20)
                y = random.randint(20, C.HEIGHT - 20)

                # Calculate distance to player
                dx = x - player_pos[0]
                dy = y - player_pos[1]
                distance = (dx*dx + dy*dy) ** 0.5

                # Ensure minimum safe distance from player (150 pixels)
                if distance > 150:
                    spawn_too_close = False

            enemy = Enemy(
                x, y,
                self.wave_number,
                C.ENEMY_BASE_SPEED,
                C.ENEMY_BASE_HP
            )
            self.enemy_group.add(enemy)

    @property
    def enemies(self):
        """
        Property to maintain backward compatibility.

        Returns:
            list: All enemy sprites
        """
        return list(self.enemy_group.sprites())

    def check_collisions(self):
        """Use sprite collide for efficient collision detection."""
        # Player projectiles vs enemies
        for projectile in self.player.deck.projectiles:
            collided_enemies = pygame.sprite.spritecollide(
                projectile, self.enemy_group, False, pygame.sprite.collide_circle
            )
            if collided_enemies:
                enemy = collided_enemies[0]
                enemy.take_damage(projectile.damage)
                projectile.explode(self.enemies)
                break

        # Player summons vs enemies handled in the summon update

        # Player vs enemies (push back enemies)
        collided_enemies = pygame.sprite.spritecollide(
            self.player, self.enemy_group, False, pygame.sprite.collide_circle
        )
        for enemy in collided_enemies:
            resolve_overlap(self.player, enemy)

    def run(self):
        """
        Main game loop with pause support.

        Handles event processing, updates, and rendering until 
        the game is closed.
        """
        while self.running:
            dt = self.clock.tick(C.FPS) / 1000.0
            events = pygame.event.get()

            # GameStateManager.handle_events will now check for pygame.QUIT internally first
            state_manager_result = self.state_manager.handle_events(events)

            if state_manager_result == "QUIT":
                self.running = False
                # Loop will terminate as self.running is false

            if self.running:  # Only update and render if not quitting
                self.state_manager.update(dt)
                self.state_manager.render(self.screen)
                pygame.display.flip()

        pygame.quit()
        sys.exit()

    def show_stats_window(self):
        """
        Shows the stats visualization window.

        Pauses the game while the stats window is active.
        """
        # First pause the game
        self.state_manager.pause()

        try:
            # This is where you would create and run your Tkinter window
            print("Stats window would appear here (paused game)")
        except Exception as e:
            print(f"Error showing stats: {e}")
            # Make sure to resume the game if there's an error
            self.state_manager.resume()

    def pause_game(self):
        """Pause the game by pausing the state manager."""
        self.state_manager.pause()

    def resume_game(self):
        """Resume the game by resuming the state manager."""
        self.state_manager.resume()

    def toggle_pause(self):
        """Toggle between paused and unpaused states."""
        self.state_manager.toggle_pause()


def main():
    """
    Entry point for the game.

    Creates a Game instance and starts the main loop.
    """
    game = Game()
    game.run()


if __name__ == "__main__":
    main()

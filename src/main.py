# main.py
import pygame
import sys
import time
import random
from font import Font
from player import Player
from enemy import Enemy
from utils import resolve_overlap
from game_state import GameStateManager, MenuState, NameEntryState, DeckSelectionState, PlayingState
from audio import Audio
from config import Config as C


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
        self.skills_filename = C.SKILLS_FILENAME
        self.player_name = None
        self.last_player_name = None

        # Sprite groups for collision detection
        self.enemy_group = pygame.sprite.Group()

        # Initialize state manager and states
        self.state_manager = GameStateManager(self)
        self.state_manager.add_state("MENU", MenuState(self))
        self.state_manager.add_state("NAME_ENTRY", NameEntryState(self))
        self.state_manager.add_state(
            "DECK_SELECTION", DeckSelectionState(self))
        self.state_manager.add_state("PLAYING", PlayingState(self))

        # Start with menu state and play menu music
        self.state_manager.set_state("MENU")
        self.audio.play_music("MENU")

    def initialize_player(self):
        """Initialize the player with an empty deck"""
        self.player = Player(self.player_name)
        self.game_start_time = time.time()

    def reset_game(self):
        """Reset game state for retry"""
        # Reset wave number
        self.wave_number = 1

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
        """Setup game for playing after deck is created"""
        self.reset_game()
        self.spawn_wave()
        self.audio.fade_out(800)
        self.audio.fade_in("PLAYING", 1000)

    def spawn_wave(self):
        """Spawn a new wave of enemies after clearing the previous wave"""
        # Clear enemy group
        self.enemy_group.empty()

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
        """Property to maintain backward compatibility"""
        return list(self.enemy_group.sprites())

    def check_collisions(self):
        """Use sprite collide for efficient collision detection"""
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
        """Main game loop with pause support"""
        self.running = True
        while self.running:
            # Get delta time in seconds
            dt = self.clock.tick(C.FPS) / 1000.0

            # Get all events
            events = pygame.event.get()

            # Process all quit events
            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False
                    break

            if not self.running:
                break

            # Handle events through state manager (always processes events)
            self.state_manager.handle_events(events)

            # Update game state (handles pausing internally)
            self.state_manager.update(dt)

            # Render everything (always happens even when paused)
            self.state_manager.render(self.screen)

            # Update the display
            pygame.display.flip()

        pygame.quit()
        sys.exit()

    def show_stats_window(self):
        """Example method for showing a Tkinter stats window"""
        # First pause the game
        self.state_manager.pause()

        try:
            # This is where you would create and run your Tkinter window
            # For example:
            # import tkinter as tk
            # root = tk.Tk()
            # root.title("Game Stats")
            # ... set up your Tkinter window ...
            # root.mainloop()

            # For now, just print a message
            print("Stats window would appear here (paused game)")

            # You can either:
            # 1. Keep the game paused until the Tkinter window is closed
            # 2. Resume automatically and let the Tkinter window run alongside
            # For option 1, the Tkinter window would need to call game.state_manager.resume()
            # when it closes
        except Exception as e:
            print(f"Error showing stats: {e}")
            # Make sure to resume the game if there's an error
            self.state_manager.resume()

    def pause_game(self):
        """Pause the game"""
        self.state_manager.pause()

    def resume_game(self):
        """Resume the game"""
        self.state_manager.resume()

    def toggle_pause(self):
        """Toggle pause state"""
        self.state_manager.toggle_pause()


def main():
    game = Game()
    game.run()


if __name__ == "__main__":
    main()

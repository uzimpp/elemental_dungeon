# main.py
import pygame
import sys
import time
import csv
import random
import os
from deck import Deck
from player import Player
from enemy import Enemy
from visual_effects import VisualEffect
from utils import resolve_overlap, draw_hp_bar, angle_diff
from game_state import *
from audio import Audio
from config import Config as C
from data_collection import DataCollection


class Game:
    def __init__(self):
        """Initialize game state and assets."""
        pygame.init()
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
        """Initialize the player with an empty deck"""
        # Create player with empty deck
        self.player = Player(self.player_name)
        self.game_start_time = time.time()

    def initialize_selected_deck(self, selected_skills):
        """Assign selected skills to the player's deck"""
        # Create a new deck
        if self.player.deck is None:
            deck = Deck()
            deck.skills = selected_skills
            self.player.deck = deck
        self.finish_initialization()

    def finish_initialization(self):
        """Complete game initialization after deck is built"""
        # Spawn first wave of enemies
        self.wave_number = 1
        self.player_name = self.last_player_name
        self.spawn_wave()

    def retry_with_same_player(self):
        """Restart the game with the same player name"""
        # Set the player name from last used name
        self.player_name = self.last_player_name
        self.initialize_player()
        return "DECK_SELECTION"

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

    @property
    def player_name(self):
        """Get player name, returning 'Unknown' if None"""
        return self._player_name if self._player_name else "Unknown"
    
    @player_name.setter
    def player_name(self, name):
        """Set player name and update last_player_name if not None"""
        # Store the new name (even if None)
        self._player_name = name
        # Only update last_player_name if we have a non-None name
        if name is not None:
            self.last_player_name = name

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


def main():
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
